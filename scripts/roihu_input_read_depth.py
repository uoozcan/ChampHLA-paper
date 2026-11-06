#!/usr/bin/env python3
"""Round 5, item R2: read layout, read length and exon depth of the development inputs.

decisions/20261106_roihu_descriptions_round5.json. Runs on Roihu, which streams each
public input alignment over HTTPS; nothing is stored but the summaries.

1. ``exons``: locate exons 2 and 3 of HLA-A, -B and -C on chromosome 6 of each build.
   The exon boundaries come from the T1K index header of the first allele of each gene
   (0-based, inclusive ends; checked against the AG/GT splice signals), and each exon is
   placed on the genome by its best ungapped seed diagonal on either strand.
2. ``inputs``: for every development input, the build is read from the length of
   chromosome 6 in the file's own header (never from the manifest), then the reads over
   those six exons give the layout, the median read length and the mean depth
   (``samtools depth -a`` defaults: unmapped, secondary, QC-fail and duplicate reads
   excluded). Reads realigned from HLA-allele or alternate contigs are not counted, because
   the depth is over the primary chromosome 6 coordinates of each build.

Development subjects only; no reference typing is read.
"""
from __future__ import annotations

import argparse
import csv
import statistics
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

GENES = ("A", "B", "C")
EXONS = (2, 3)
SEARCH_WINDOW = (28_000_000, 34_000_000)  # contains the class I genes in GRCh37 and GRCh38
CHR6_LENGTH = {170_805_979: "GRCh38", 171_115_067: "GRCh37"}
SEED = 24
COMPLEMENT = str.maketrans("ACGTN", "TGCAN")


def reverse_complement(sequence: str) -> str:
    return sequence.translate(COMPLEMENT)[::-1]


def read_fasta(path: Path, wanted) -> dict[str, tuple[str, str]]:
    """First record per gene among headers accepted by ``wanted``: {gene: (header, seq)}."""
    records: dict[str, tuple[str, str]] = {}
    header, chunks = None, []

    def flush():
        if header is not None:
            gene = wanted(header)
            if gene and gene not in records:
                records[gene] = (header, "".join(chunks).upper())

    with path.open(encoding="ascii") as handle:
        for line in handle:
            line = line.rstrip("\n")
            if line.startswith(">"):
                flush()
                header, chunks = line[1:], []
            elif header is not None:
                chunks.append(line)
    flush()
    return records


def t1k_gene(header: str) -> str | None:
    name = header.split()[0]
    for gene in GENES:
        if name.startswith(f"HLA-{gene}*"):
            return gene
    return None


def exon_sequences(header: str, sequence: str) -> dict[int, str]:
    """Exons 2 and 3 from a T1K header 'NAME n s1 e1 s2 e2 ...' (0-based, inclusive ends)."""
    fields = [int(value) for value in header.split()[1:]]
    count, bounds = fields[0], fields[1:]
    if len(bounds) != 2 * count:
        raise ValueError(f"malformed T1K exon header: {header}")
    exons = {}
    for number in EXONS:
        start, end = bounds[2 * (number - 1)], bounds[2 * (number - 1) + 1]
        if sequence[start - 2:start] != "AG" or sequence[end + 1:end + 3] != "GT":
            raise ValueError(f"exon {number} of {header.split()[0]} lacks AG/GT splice signals")
        exons[number] = sequence[start:end + 1]
    return exons


def fetch(fasta: Path, contig: str, start: int, end: int) -> str:
    """Bases start..end (0-based, end exclusive) of one contig, read through its .fai."""
    for line in Path(f"{fasta}.fai").read_text(encoding="ascii").splitlines():
        name, length, offset, bases, width = line.split("\t")[:5]
        if name == contig:
            length, offset, bases, width = int(length), int(offset), int(bases), int(width)
            break
    else:
        raise KeyError(f"{contig} not in {fasta}.fai")
    end = min(end, length)
    first = offset + (start // bases) * width + start % bases
    last = offset + (end // bases) * width + end % bases
    with fasta.open("rb") as handle:
        handle.seek(first)
        raw = handle.read(last - first)
    return raw.decode("ascii").replace("\n", "").replace("\r", "").upper()


def seed_index(genome: str) -> dict[str, list[int]]:
    index: dict[str, list[int]] = {}
    for position in range(len(genome) - SEED + 1):
        index.setdefault(genome[position:position + SEED], []).append(position)
    return index


def place(exon: str, genome: str, index: dict[str, list[int]] | None = None
          ) -> tuple[int, str, float]:
    """Best ungapped placement: (0-based start in genome, strand, identity)."""
    index = seed_index(genome) if index is None else index
    best = None
    for strand, query in (("+", exon), ("-", reverse_complement(exon))):
        votes: dict[int, int] = {}
        for offset in range(len(query) - SEED + 1):
            for hit in index.get(query[offset:offset + SEED], ()):
                votes[hit - offset] = votes.get(hit - offset, 0) + 1
        for diagonal, count in votes.items():
            key = (count, -diagonal)
            if best is None or key > best[0]:
                best = (key, diagonal, strand, query)
    if best is None:
        raise ValueError("exon has no seed match in the window")
    _, diagonal, strand, query = best
    target = genome[diagonal:diagonal + len(query)]
    identity = sum(a == b for a, b in zip(query, target)) / len(query)
    return diagonal, strand, identity


def derive_exons(t1k_dna: Path, genomes: dict[str, tuple[Path, str]]) -> list[dict]:
    rows = []
    records = read_fasta(t1k_dna, t1k_gene)
    for build in sorted(genomes):
        fasta, contig = genomes[build]
        window = fetch(fasta, contig, *SEARCH_WINDOW)
        index = seed_index(window)
        for gene in GENES:
            header, sequence = records[gene]
            for number, exon in exon_sequences(header, sequence).items():
                start, strand, identity = place(exon, window, index)
                begin = SEARCH_WINDOW[0] + start
                rows.append({
                    "build": build, "gene": f"HLA-{gene}", "exon": number,
                    "contig": contig, "start_1based": begin + 1,
                    "end_1based": begin + len(exon), "strand": strand,
                    "length": len(exon), "identity": f"{identity:.4f}",
                    "source_allele": header.split()[0],
                })
    return rows


def build_from_header(header: str) -> tuple[str, str]:
    """(build, chromosome 6 name) from the @SQ length of chromosome 6."""
    for line in header.splitlines():
        if not line.startswith("@SQ"):
            continue
        tags = dict(field.split(":", 1) for field in line.split("\t")[1:] if ":" in field)
        if tags.get("SN") in {"chr6", "6"}:
            build = CHR6_LENGTH.get(int(tags["LN"]))
            if build is None:
                raise ValueError(f"unknown chromosome 6 length {tags['LN']}")
            return build, tags["SN"]
    raise ValueError("no chromosome 6 in the header")


def query_length(cigar: str) -> int:
    total, number = 0, ""
    for character in cigar:
        if character.isdigit():
            number += character
        else:
            if character in "MIS=X":
                total += int(number)
            number = ""
    return total


def summarise_reads(sam_lines: list[str]) -> tuple[str, int, int]:
    """(layout, median read length, reads) from primary mapped records."""
    lengths, paired = [], 0
    for line in sam_lines:
        fields = line.split("\t")
        flag = int(fields[1])
        if flag & 0x904 or fields[5] == "*":
            continue
        lengths.append(query_length(fields[5]))
        paired += bool(flag & 0x1)
    if not lengths:
        return "no_reads", 0, 0
    layout = "paired" if paired == len(lengths) else "single" if paired == 0 else "mixed"
    return layout, int(statistics.median(lengths)), len(lengths)


def mean_depth(depth_lines: list[str]) -> float:
    values = [int(line.split("\t")[2]) for line in depth_lines if line.strip()]
    return sum(values) / len(values) if values else 0.0


def samtools(arguments: list[str]) -> list[str]:
    result = subprocess.run(["samtools", *arguments], check=True, capture_output=True,
                            text=True)
    return result.stdout.splitlines()


def measure_input(row: dict[str, str], exons: list[dict], reference: str, workdir: Path) -> dict:
    url = row["input_url"]
    source = f"{url}##idx##{row['index_url']}" if row["index_url"] else url
    ref = ["--reference", reference] if url.endswith(".cram") else []
    header = "\n".join(samtools(["view", "-H", *ref, source]))
    build, contig = build_from_header(header)
    chosen = [e for e in exons if e["build"] == build]
    if len(chosen) != len(GENES) * len(EXONS):
        raise ValueError(f"no exon coordinates for {build}")
    bed = workdir / f"{row['modality']}_{row['sample_id']}_exons.bed"
    bed.write_text("".join(f"{contig}\t{e['start_1based'] - 1}\t{e['end_1based']}\n"
                           for e in chosen), encoding="ascii")
    # One indexed remote fetch of the six exons into a small local BAM.
    local = workdir / f"{row['modality']}_{row['sample_id']}_exons.bam"
    regions = [f"{contig}:{e['start_1based']}-{e['end_1based']}" for e in chosen]
    samtools(["view", "-b", "-M", *ref, "-o", str(local), source, *regions])
    samtools(["index", str(local)])
    layout, read_length, count = summarise_reads(samtools(["view", str(local)]))
    depth = samtools(["depth", "-a", "-b", str(bed), str(local)])
    for path in (local, Path(f"{local}.bai"), bed):
        path.unlink()
    return {"subject": row["sample_id"], "modality": row["modality"], "detected_build": build,
            "layout": layout, "median_read_length": read_length, "exon_reads": count,
            "mean_exon_depth": f"{mean_depth(depth):.2f}"}


def write_tsv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t",
                                lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    one = sub.add_parser("exons")
    one.add_argument("--t1k-dna", type=Path, required=True)
    one.add_argument("--grch37", type=Path, required=True, help="FASTA; contig 6 or chr6")
    one.add_argument("--grch38", type=Path, required=True)
    one.add_argument("--output", type=Path, required=True)
    two = sub.add_parser("inputs")
    two.add_argument("--manifest", type=Path, required=True)
    two.add_argument("--exons", type=Path, required=True)
    two.add_argument("--reference", required=True, help="GRCh38DH FASTA for CRAM decoding")
    two.add_argument("--output", type=Path, required=True)
    two.add_argument("--workers", type=int, default=8)
    args = parser.parse_args(argv)
    if args.command == "exons":
        genomes = {}
        for build, fasta in (("GRCh37", args.grch37), ("GRCh38", args.grch38)):
            names = {line.split("\t")[0] for line in
                     Path(f"{fasta}.fai").read_text(encoding="ascii").splitlines()}
            genomes[build] = (fasta, "chr6" if "chr6" in names else "6")
        write_tsv(args.output, derive_exons(args.t1k_dna, genomes))
        return 0
    exons = list(csv.DictReader(args.exons.open(encoding="utf-8"), delimiter="\t"))
    for row in exons:
        row["start_1based"], row["end_1based"] = int(row["start_1based"]), int(row["end_1based"])
    with args.manifest.open(encoding="utf-8") as handle:
        manifest = sorted(csv.DictReader(handle, delimiter="\t"),
                          key=lambda r: (r["modality"], r["sample_id"]))
    workdir = args.output.parent
    # Network-bound, so threads; results keep the sorted manifest order.
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(lambda row: measure_input(row, exons, args.reference, workdir),
                             manifest))
    write_tsv(args.output, rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
