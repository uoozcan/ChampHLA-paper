import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

_spec = importlib.util.spec_from_file_location(
    "plurality_support_calibration", ROOT / "scripts" / "plurality_support_calibration.py")
calib = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = calib
_spec.loader.exec_module(calib)


HEADER = ("cohort\tsubject\tmodality\tgene\tmethod\tallele1\tallele2\ttop_support"
          "\tcallable_tools\ttie_at_top\ttruth_allele1\ttruth_allele2\n")


def _row(subject, gene, method, a1, a2, support, callable_tools, tie, t1, t2):
    return (f"dev\t{subject}\twes\t{gene}\t{method}\t{a1}\t{a2}\t{support}"
            f"\t{callable_tools}\t{tie}\t{t1}\t{t2}\n")


def _joined(tmp_path: Path, rows: str) -> Path:
    path = tmp_path / "joined.tsv"
    path.write_text(HEADER + rows, encoding="utf-8")
    return path


def test_majority_vote_duplicate_does_not_double_the_counts(tmp_path: Path):
    """The same rule is emitted twice, under its current and historical names.

    Counting both would double every locus in the calibration table.
    """
    rows = (_row("S1", "A", "SimplePluralityLex", "A*01:01", "A*02:01", 5, 5, "0",
                 "A*01:01", "A*02:01")
            + _row("S1", "A", "MajorityVote", "A*01:01", "A*02:01", 5, 5, "0",
                   "A*01:01", "A*02:01"))
    result = calib.calibration(calib._plurality_rows(_joined(tmp_path, rows)))
    assert len(result) == 1
    assert result[0]["loci"] == 1


def test_accuracy_is_order_insensitive(tmp_path: Path):
    """A genotype is an unordered pair; reversing it is the same call."""
    rows = _row("S1", "A", "SimplePluralityLex", "A*02:01", "A*01:01", 5, 5, "0",
                "A*01:01", "A*02:01")
    result = calib.calibration(calib._plurality_rows(_joined(tmp_path, rows)))
    assert result[0]["correct"] == 1


def test_partial_panel_loci_are_reported_separately(tmp_path: Path):
    """4-of-5 support is not the same situation as 4-of-4 with one caller absent.

    Folding them together would report a full-panel majority and a
    reduced-panel unanimity under one label.
    """
    rows = (_row("S1", "A", "SimplePluralityLex", "A*01:01", "A*02:01", 4, 5, "0",
                 "A*01:01", "A*02:01")
            + _row("S2", "A", "SimplePluralityLex", "A*01:01", "A*02:01", 4, 4, "0",
                   "A*01:01", "A*02:01"))
    result = calib.calibration(calib._plurality_rows(_joined(tmp_path, rows)))
    labels = {row["support_label"]: row["full_panel"] for row in result}
    assert labels == {"4/5": 1, "4/4": 0}


def test_tie_audit_counts_only_tied_loci(tmp_path: Path):
    rows = (_row("S1", "A", "SimplePluralityLex", "A*01:01", "A*02:01", 2, 5, "1",
                 "A*03:01", "A*11:01")
            + _row("S2", "A", "SimplePluralityLex", "A*01:01", "A*02:01", 2, 5, "1",
                   "A*01:01", "A*02:01")
            + _row("S3", "A", "SimplePluralityLex", "A*01:01", "A*02:01", 5, 5, "0",
                   "A*01:01", "A*02:01"))
    result = calib.ties(calib._plurality_rows(_joined(tmp_path, rows)))
    assert result == [{"modality": "wes", "tied_loci": 2, "tie_break_correct": 1,
                       "tie_break_accuracy": 0.5}]


def test_rows_without_truth_are_excluded(tmp_path: Path):
    """A locus with no reference typing cannot be scored either way."""
    rows = (_row("S1", "A", "SimplePluralityLex", "A*01:01", "A*02:01", 5, 5, "0", "", "")
            + _row("S2", "A", "SimplePluralityLex", "A*01:01", "A*02:01", 5, 5, "0",
                   "A*01:01", "A*02:01"))
    result = calib.calibration(calib._plurality_rows(_joined(tmp_path, rows)))
    assert sum(row["loci"] for row in result) == 1


def test_committed_artifact_matches_the_manuscript(tmp_path: Path):
    """The numbers the supplement prints must be the ones in the artifact."""
    import csv
    path = ROOT / "artifacts" / "plurality_characterisation" / "support_calibration.tsv"
    if not path.is_file():
        return
    with path.open(newline="", encoding="utf-8") as handle:
        rows = {(r["modality"], r["support_label"]): r
                for r in csv.DictReader(handle, delimiter="\t")}
    assert rows[("wes", "5/5")]["correct"] == "219"
    assert rows[("wes", "2/5")]["accuracy"].startswith("0.5")
    assert rows[("rnaseq", "4/4")]["correct"] == "267"
