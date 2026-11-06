"""Round 5 descriptions (decisions/20261106_roihu_descriptions_round5.json) on synthetic data."""
from __future__ import annotations

import importlib.util
import random
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def random_dna(length: int, seed: int) -> str:
    rng = random.Random(seed)
    return "".join(rng.choice("ACGT") for _ in range(length))


def test_exon_sequences_use_inclusive_t1k_bounds_and_check_splice_signals():
    module = load("roihu_input_read_depth")
    exon1, exon2, exon3 = "ATGGCC", "CCCCAAAATTTT", "GGGGCCCC"
    sequence = exon1 + "GTAAAG" + exon2 + "GTCCAG" + exon3 + "GTAA"
    s2 = len(exon1) + 6
    s3 = s2 + len(exon2) + 6
    header = (f"HLA-A*01:01 3 0 {len(exon1) - 1} {s2} {s2 + len(exon2) - 1} "
              f"{s3} {s3 + len(exon3) - 1}")
    assert module.exon_sequences(header, sequence) == {2: exon2, 3: exon3}
    with pytest.raises(ValueError, match="splice"):
        module.exon_sequences(header.replace(f" {s2} ", f" {s2 + 1} "), sequence)


def test_place_finds_the_exon_on_either_strand_with_mismatches():
    module = load("roihu_input_read_depth")
    genome = random_dna(5000, 1)
    exon = genome[1200:1470]
    mutated = exon[:100] + ("A" if exon[100] != "A" else "C") + exon[101:]
    assert module.place(mutated, genome)[:2] == (1200, "+")
    assert module.place(mutated, genome)[2] == pytest.approx(269 / 270)
    flipped = (genome[:1200] + random_dna(270, 3) + genome[1470:3000]
               + module.reverse_complement(exon) + genome[3270:])
    start, strand, identity = module.place(exon, flipped)
    assert (start, strand, identity) == (3000, "-", 1.0)


def test_fetch_reads_a_wrapped_fasta_through_its_index(tmp_path):
    module = load("roihu_input_read_depth")
    sequence = random_dna(250, 2)
    fasta = tmp_path / "g.fa"
    body = "\n".join(sequence[i:i + 60] for i in range(0, 250, 60))
    fasta.write_bytes(f">6 test\n{body}\n".encode("ascii"))
    Path(f"{fasta}.fai").write_bytes(b"6\t250\t8\t60\t61\n")
    assert module.fetch(fasta, "6", 55, 130) == sequence[55:130]


def test_build_is_read_from_the_header_chromosome_6_length():
    module = load("roihu_input_read_depth")
    header = "@HD\tVN:1.4\n@SQ\tSN:chr6\tLN:171115067\n"
    assert module.build_from_header(header) == ("GRCh37", "chr6")
    assert module.build_from_header("@SQ\tSN:6\tLN:170805979") == ("GRCh38", "6")
    with pytest.raises(ValueError):
        module.build_from_header("@SQ\tSN:chr6\tLN:1")


def test_reads_summary_skips_secondary_unmapped_and_reports_layout():
    module = load("roihu_input_read_depth")
    lines = ["r1\t99\tchr6\t1\t60\t75M\t=\t1\t0\t*\t*",
             "r1\t147\tchr6\t1\t60\t70M5S\t=\t1\t0\t*\t*",
             "r2\t355\tchr6\t1\t0\t75M\t=\t1\t0\t*\t*",       # secondary
             "r3\t4\tchr6\t1\t0\t*\t*\t0\t0\t*\t*",            # unmapped
             "r4\t2147\tchr6\t1\t0\t30H45M\t=\t1\t0\t*\t*"]     # supplementary
    assert module.summarise_reads(lines) == ("paired", 75, 2)
    assert module.summarise_reads(["s\t0\tchr6\t1\t60\t50M\t*\t0\t0\t*\t*"]) == ("single", 50, 1)
    assert module.mean_depth(["chr6\t1\t3", "chr6\t2\t5", "chr6\t3\t0"]) == pytest.approx(8 / 3)


TRACE_HEADER = ("task_id\thash\tnative_id\tname\tstatus\texit\tsubmit\tstart\tcomplete\t"
                "duration\trealtime\tcpus\tmemory\t%cpu\t%mem\trss\tvmem\tpeak_rss\t"
                "peak_vmem\trchar\twchar\n")


def trace_line(name, status, realtime, cpu, peak):
    return f"1\th\t1\t{name}\t{status}\t0\t-\t-\t-\t-\t{realtime}\t1\t1 GB\t{cpu}\t0\t0\t0\t{peak}\t0\t0\t0\n"


def test_trace_costs_sum_cpu_hours_take_peak_memory_and_count_failures(tmp_path):
    module = load("summarise_round5_records")
    trace = tmp_path / "trace.txt"
    trace.write_bytes((TRACE_HEADER
                       + trace_line("HLAHD_BAM (s1)", "FAILED", "-", "-", "-")
                       + trace_line("HLAHD_BAM (s1)", "COMPLETED", "1h 30m", "200.0%", "3.5 GB")
                       + trace_line("OPTITYPE (s1)", "CACHED", "36s", "100.0%", "512 MB")
                       + trace_line("RESCUE_HLA_READS (s1)", "COMPLETED", "500ms", "50.0%", "0")
                       ).encode())
    costs = module.trace_costs(trace)
    assert costs["HLA-HD"] == {"cpu_hours": pytest.approx(3.0), "peak_gib": 3.5, "failed": 1}
    assert costs["OptiType"]["cpu_hours"] == pytest.approx(0.01)
    assert costs["OptiType"]["peak_gib"] == pytest.approx(0.5)
    assert costs["shared steps"]["failed"] == 0
    assert module.duration_hours("1d 2h 3m 4.5s") == pytest.approx(26 + 3 / 60 + 4.5 / 3600)


def test_representative_subject_is_first_sorted_with_both_assays():
    module = load("summarise_round5_records")
    manifest = [{"sample_id": "HG00102", "modality": "wes"},
                {"sample_id": "HG00100", "modality": "rnaseq"},
                {"sample_id": "HG00101", "modality": "wes"},
                {"sample_id": "HG00101", "modality": "rnaseq"},
                {"sample_id": "HG00102", "modality": "rnaseq"}]
    assert module.representative_subject(manifest) == "HG00101"


def test_r2_summary_reports_median_and_range_by_assay():
    module = load("summarise_round5_records")
    inputs = [{"modality": "wes", "subject": s, "detected_build": "GRCh38", "layout": "paired",
               "median_read_length": str(n), "exon_reads": "1", "mean_exon_depth": str(d)}
              for s, n, d in (("a", 76, 10.0), ("b", 100, 30.5), ("c", 76, 20.25))]
    (row,) = module.r2_summary(inputs)
    assert (row["inputs"], row["layouts"], row["detected_builds"]) == (3, "paired 3", "GRCh38 3")
    assert (row["read_length_median"], row["read_length_min"], row["read_length_max"]) == ("76", "76", "100")
    assert (row["exon_depth_median"], row["exon_depth_min"], row["exon_depth_max"]) == ("20.2", "10.0", "30.5")


def test_representative_sample_copies_match_the_recorded_run_hashes():
    module = load("summarise_round5_records")
    copied = module.read_tsv(module.REPRESENTATIVE / "manifest.tsv")
    recorded = {(r["modality"], r["subject"]): r for r in module.read_tsv(module.PROVENANCE)}
    assert {(r["modality"], r["file"]) for r in copied} == {
        (m, f) for m in ("wes", "rnaseq") for f in module.REPRESENTATIVE_FILES}
    for row in copied:
        path = module.REPRESENTATIVE / row["modality"] / row["subject"] / row["file"]
        assert module.sha256(path) == row["sha256"]
        assert recorded[(row["modality"], row["subject"])][row["provenance_column"]] == row["sha256"]


def test_version_parsing_marks_usage_text_and_blank_as_not_recorded(tmp_path):
    module = load("summarise_round5_records")
    for caller, text in (("OptiType", '"OPTITYPE":\n    optitype: usage: OptiType [-h]\n'),
                         ("arcasHLA", '"ARCASHLA_BAM":\n    arcashla: \n'),
                         ("HLA-HD", '"HLAHD_BAM":\n    hlahd: HLA-HD version 1.4.0\n    samtools: 1.9\n')):
        folder = tmp_path / "s1" / "results" / "s1" / module.CALLER_DIR[caller]
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "versions.yml").write_text(text, encoding="utf-8")
    run = tmp_path / "s1"
    assert module.caller_version(run, "s1", "OptiType") == "not recorded"
    assert module.caller_version(run, "s1", "arcasHLA") == "not recorded"
    assert module.caller_version(run, "s1", "HLA-HD") == "1.4.0"
