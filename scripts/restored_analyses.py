"""Analyses restored from the ChampHLA drafts, recomputed on the current loci.

Gap review items (reports/champhla_gap_review_20261007.md):
  B1  truth-free discordance taxonomy, with consensus concordance per class
  B2  exploratory caller calibration (Brier score, expected calibration error)
  B3  cross-assay agreement for subjects with both WES and RNA-seq endpoint loci
  B4  per-gene caller concordance

Every analysis reads the frozen joined development table, so the loci are the
exact-endpoint loci of the paper (WES 153, RNA-seq 120) and no caller is re-run.
B2 additionally reads the recovered caller table that the development inputs
were normalized from; its SHA-256 must match the value recorded in
data/development/input_manifest.json.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from champhla_confirmation.statistics import exact_binomial_ci  # noqa: E402
JOINED = ROOT / "runtime_data" / "joined_development.tsv"
INPUT_MANIFEST = ROOT / "data" / "development" / "input_manifest.json"
OUT = ROOT / "artifacts" / "restored_analyses"
PLURALITY = "SimplePluralityLex"
PANELS = {
    "wes": ("HLA-HD", "OptiType", "POLYSOLVER", "SpecHLA", "T1K"),
    "rnaseq": ("ArcasHLA", "HLA-HD", "OptiType", "T1K"),
}
ASSAYS = ("wes", "rnaseq")
GENES = ("A", "B", "C")
ECE_BINS = 5


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if n == 0:
        return float("nan"), float("nan")
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return max(0.0, centre - half), min(1.0, centre + half)


def gene_of(value: str) -> str:
    return value.replace("HLA-", "")


def pct(k: int, n: int) -> str:
    return f"{100 * k / n:.1f}" if n else ""


def load_loci() -> dict[tuple[str, str, str], dict]:
    """(assay, subject, gene) -> truth, plurality call and panel caller calls."""
    loci: dict[tuple[str, str, str], dict] = defaultdict(lambda: {"callers": {}})
    for row in read_tsv(JOINED):
        key = (row["modality"], row["subject"], gene_of(row["gene"]))
        locus = loci[key]
        locus["truth"] = tuple(sorted((row["truth_allele1"], row["truth_allele2"])))
        method = row["method"]
        callable_ = row["call_status"] == "callable" and row["allele1"] and row["allele2"]
        pair = tuple(sorted((row["allele1"], row["allele2"]))) if callable_ else None
        if method == PLURALITY:
            locus["plurality"] = pair
            locus["tie"] = row.get("tie_at_top") == "1"
        elif method.startswith("Caller:"):
            caller = method[len("Caller:"):]
            if caller in PANELS[row["modality"]]:
                locus["callers"][caller] = pair
    missing = [key for key, locus in loci.items() if "plurality" not in locus]
    if missing:
        raise SystemExit(f"plurality call missing at {len(missing)} loci")
    return dict(loci)


# B1 ---------------------------------------------------------------------------
TAXONOMY = ("no_evidence", "single_caller", "unanimous", "one_allele_conflict",
            "two_allele_conflict")


def classify(locus: dict) -> str:
    calls = [pair for pair in locus["callers"].values() if pair]
    if not calls:
        return "no_evidence"
    if len(calls) == 1:
        return "single_caller"
    if len(set(calls)) == 1:
        return "unanimous"
    reported = set(locus["plurality"])
    dissent = [pair for pair in calls if pair != locus["plurality"]]
    # A dissenting genotype that shares no allele with the reported genotype is
    # a two-allele conflict; otherwise every dissent differs at one allele.
    if any(not (set(pair) & reported) for pair in dissent):
        return "two_allele_conflict"
    return "one_allele_conflict"


def discordance(loci: dict) -> list[dict]:
    rows = []
    for assay in ASSAYS:
        keys = [key for key in loci if key[0] == assay]
        for category in TAXONOMY:
            members = [key for key in keys if classify(loci[key]) == category]
            correct = sum(loci[key]["plurality"] == loci[key]["truth"] for key in members)
            lo, hi = exact_binomial_ci(correct, len(members)) if members else (0.0, 0.0)
            rows.append({
                "assay": assay, "category": category, "loci": len(members),
                "assay_loci": len(keys), "share_percent": pct(len(members), len(keys)),
                "consensus_correct": correct,
                "consensus_concordance_percent": pct(correct, len(members)),
                "ci_low_percent": "" if not members else f"{100 * lo:.1f}",
                "ci_high_percent": "" if not members else f"{100 * hi:.1f}",
                "interval_method": "clopper_pearson_exact",
                "tied_loci": sum(loci[key]["tie"] for key in members),
            })
    return rows


# B3 ---------------------------------------------------------------------------
def pooled_vote(calls: list[tuple[str, str]]) -> tuple[str, str] | None:
    counts: dict[tuple[str, str], int] = defaultdict(int)
    for pair in calls:
        counts[pair] += 1
    if not counts:
        return None
    return sorted(counts, key=lambda pair: (-counts[pair], pair))[0]


def cross_assay(loci: dict) -> tuple[list[dict], dict]:
    shared = sorted({(subject, gene) for _, subject, gene in loci
                     if ("wes", subject, gene) in loci and ("rnaseq", subject, gene) in loci})
    subjects = {s for s, _ in shared}
    strata = defaultdict(lambda: {"loci": 0, "wes_correct": 0, "rna_correct": 0,
                                  "pooled_correct": 0})
    for subject, gene in shared:
        wes, rna = loci[("wes", subject, gene)], loci[("rnaseq", subject, gene)]
        truth = wes["truth"]
        if truth != rna["truth"]:
            raise SystemExit(f"truth differs across assays at {subject} {gene}")
        agree = wes["plurality"] is not None and wes["plurality"] == rna["plurality"]
        pooled = pooled_vote([p for p in wes["callers"].values() if p]
                             + [p for p in rna["callers"].values() if p])
        for stratum in ("all", "assays_agree" if agree else "assays_disagree", f"gene_{gene}"):
            cell = strata[stratum]
            cell["loci"] += 1
            cell["wes_correct"] += wes["plurality"] == truth
            cell["rna_correct"] += rna["plurality"] == truth
            cell["pooled_correct"] += pooled == truth
    rows = []
    for stratum in ("all", "assays_agree", "assays_disagree", "gene_A", "gene_B", "gene_C"):
        cell = strata[stratum]
        n = cell["loci"]
        rows.append({
            "stratum": stratum, "loci": n,
            "wes_consensus_correct": cell["wes_correct"],
            "rnaseq_consensus_correct": cell["rna_correct"],
            "pooled_vote_correct": cell["pooled_correct"],
            "wes_percent": pct(cell["wes_correct"], n),
            "rnaseq_percent": pct(cell["rna_correct"], n),
            "pooled_percent": pct(cell["pooled_correct"], n),
        })
    return rows, {"shared_loci": len(shared), "shared_subjects": len(subjects)}


# B4 ---------------------------------------------------------------------------
def per_gene(loci: dict) -> list[dict]:
    rows = []
    for assay in ASSAYS:
        for method in (*PANELS[assay], "ChampHLA-Consensus"):
            for gene in (*GENES, "all"):
                keys = [key for key in loci if key[0] == assay
                        and (gene == "all" or key[2] == gene)]
                if method == "ChampHLA-Consensus":
                    correct = sum(loci[k]["plurality"] == loci[k]["truth"] for k in keys)
                    called = sum(loci[k]["plurality"] is not None for k in keys)
                else:
                    correct = sum(loci[k]["callers"].get(method) == loci[k]["truth"] for k in keys)
                    called = sum(loci[k]["callers"].get(method) is not None for k in keys)
                lo, hi = wilson(correct, len(keys))
                rows.append({
                    "assay": assay, "method": method, "gene": gene, "loci": len(keys),
                    "called": called, "correct": correct,
                    "concordance_percent": pct(correct, len(keys)),
                    "wilson_low_percent": f"{100 * lo:.1f}",
                    "wilson_high_percent": f"{100 * hi:.1f}",
                })
    return rows


# B2 ---------------------------------------------------------------------------
def calibration(loci: dict, source: Path) -> list[dict]:
    probabilities: dict[tuple[str, str, str, str], float] = {}
    for row in read_tsv(source):
        assay = row["modality"]
        if assay not in PANELS or row["tool"] not in PANELS[assay]:
            continue
        value = row.get("cv_calibrated_probability", "")
        if value in ("", "NA", "nan"):
            continue
        probabilities[(assay, row["sample"], gene_of(row["gene"]), row["tool"])] = float(value)
    rows = []
    for assay in ASSAYS:
        for caller in PANELS[assay]:
            scored = []
            for key, locus in loci.items():
                if key[0] != assay or locus["callers"].get(caller) is None:
                    continue
                p = probabilities.get((assay, key[1], key[2], caller))
                if p is not None:
                    scored.append((p, int(locus["callers"][caller] == locus["truth"])))
            callable_loci = sum(1 for key, locus in loci.items()
                                if key[0] == assay and locus["callers"].get(caller) is not None)
            if not scored:
                rows.append({"assay": assay, "caller": caller, "callable_loci": callable_loci,
                             "scored_loci": 0, "mean_probability": "", "observed_concordance": "",
                             "brier": "", "ece": "", "note": "no calibrated probability"})
                continue
            brier = sum((p - y) ** 2 for p, y in scored) / len(scored)
            bins: dict[int, list[tuple[float, int]]] = defaultdict(list)
            for p, y in scored:
                bins[min(ECE_BINS - 1, int(max(0.0, min(1.0, p)) * ECE_BINS))].append((p, y))
            ece = sum(abs(sum(p for p, _ in v) / len(v) - sum(y for _, y in v) / len(v)) * len(v)
                      for v in bins.values()) / len(scored)
            rows.append({
                "assay": assay, "caller": caller, "callable_loci": callable_loci,
                "scored_loci": len(scored),
                "mean_probability": f"{sum(p for p, _ in scored) / len(scored):.3f}",
                "observed_concordance": f"{sum(y for _, y in scored) / len(scored):.3f}",
                "brier": f"{brier:.3f}", "ece": f"{ece:.3f}",
                "note": (
                    "" if len(scored) == callable_loci
                    else f"{callable_loci - len(scored)} callable loci lacked a preserved "
                         "calibrated probability"
                ),
            })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--caller-source", type=Path,
        help=("recovered harmonized_population_enriched.tsv; when omitted, "
              "the checksum-pinned historical calibration artifact is retained"),
    )
    args = parser.parse_args()
    expected = json.loads(INPUT_MANIFEST.read_text(encoding="utf-8"))["source_sha256"]["caller_rows"]
    observed = None
    if args.caller_source is not None:
        observed = sha256(args.caller_source)
        if observed != expected:
            raise SystemExit(
                f"caller source checksum {observed} does not match manifest {expected}"
            )

    loci = load_loci()
    outputs = {
        "discordance_taxonomy.tsv": discordance(loci),
        "per_gene_caller_concordance.tsv": per_gene(loci),
    }
    cross_rows, cross_meta = cross_assay(loci)
    outputs["cross_assay_agreement.tsv"] = cross_rows
    if args.caller_source is not None:
        outputs["caller_calibration.tsv"] = calibration(loci, args.caller_source)
    elif not (OUT / "caller_calibration.tsv").is_file():
        raise SystemExit(
            "caller calibration source was omitted and no preserved calibration artifact exists"
        )
    else:
        # Preserve every historical estimate, but make an already implicit
        # scored-versus-callable exclusion explicit in the artifact metadata.
        calibration_rows = read_tsv(OUT / "caller_calibration.tsv")
        for row in calibration_rows:
            missing = int(row["callable_loci"]) - int(row["scored_loci"])
            row["note"] = (
                f"{missing} callable loci lacked a preserved calibrated probability"
                if missing else row.get("note", "")
            )
        outputs["caller_calibration.tsv"] = calibration_rows

    for name, rows in outputs.items():
        write_tsv(OUT / name, rows, list(rows[0]))
    output_names = [*outputs]
    if "caller_calibration.tsv" not in output_names:
        output_names.append("caller_calibration.tsv")
    manifest = {
        "schema_version": "champhla-restored-analyses-1",
        "gap_review": "reports/champhla_gap_review_20261007.md",
        "inputs": {
            "joined_development": {
                "path": JOINED.relative_to(ROOT).as_posix(),
                "sha256": sha256(JOINED),
            },
            "caller_source": {
                "identifier": "recovered harmonized_population_enriched.tsv",
                "sha256": expected,
                "supplied_for_this_run": args.caller_source is not None,
            },
        },
        "calibration_refresh": (
            "recomputed_from_checksum_verified_source"
            if args.caller_source is not None
            else "preserved_checksum_pinned_historical_estimates_with_denominator_note"
        ),
        "loci": {assay: sum(1 for key in loci if key[0] == assay) for assay in ASSAYS},
        "cross_assay": cross_meta,
        "exploratory": ["caller_calibration.tsv"],
        "outputs": {name: sha256(OUT / name) for name in output_names},
    }
    (OUT / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({"loci": manifest["loci"], **cross_meta}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
