"""Best-single-caller refit on recovered folds (decisions/20261009_nestedcv_refit.json)."""
from __future__ import annotations

import csv
import json
from pathlib import Path

from champhla_confirmation.development import combine_predictions, refit_best_single_caller

ROOT = Path(__file__).resolve().parents[1]


def _write(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def _scenario(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Two folds of two WES subjects each. OptiType is right on fold 0 and wrong on
    fold 1; POLYSOLVER is the reverse. A selector that peeked at the held-out fold
    would pick the caller that is right there; a correct one picks the other."""
    calls, truth, secondary = [], [], []
    for fold, subjects in (("0", ("S1", "S2")), ("1", ("S3", "S4"))):
        for subject in subjects:
            truth.append({"cohort": "c", "subject": subject, "modality": "wes", "gene": "A",
                          "truth_allele1": "A*01:01", "truth_allele2": "A*02:01",
                          "truth_status": "resolved"})
            secondary.append({"subject": subject, "modality": "wes", "gene": "A",
                              "method": "BestSingleTool_nestedCV", "outer_fold": fold})
            for caller in ("HLA-HD", "OptiType", "POLYSOLVER", "SpecHLA", "T1K"):
                right = (caller == "OptiType") == (fold == "0") and caller in (
                    "OptiType", "POLYSOLVER")
                calls.append({"cohort": "c", "subject": subject, "superpopulation": "X",
                              "modality": "wes", "gene": "A", "caller": caller,
                              "allele1": "A*01:01", "allele2": "A*02:01" if right else "A*03:01",
                              "call_status": "callable"})
    paths = tmp_path / "calls.tsv", tmp_path / "truth.tsv", tmp_path / "secondary.tsv"
    for path, rows in zip(paths, (calls, truth, secondary)):
        _write(path, rows)
    return paths


def test_each_fold_is_fitted_on_the_other_folds_only(tmp_path: Path):
    calls, truth, secondary = _scenario(tmp_path)
    manifest = refit_best_single_caller(str(calls), str(truth), str(secondary),
                                        str(tmp_path / "fitted.tsv"), str(tmp_path / "m.json"))
    picks = {fold: record["caller"] for fold, record in manifest["picks"]["wes"].items()}
    assert picks == {"0": "POLYSOLVER", "1": "OptiType"}
    assert manifest["truth_values_used_for_prediction"] == "training_folds_only"
    with (tmp_path / "fitted.tsv").open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    assert {r["decision_reason"] for r in rows if r["outer_fold"] == "0"} == {
        "nestedcv_refit_pick:POLYSOLVER"}
    assert all(r["analysis_scope"] == "exploratory_fitted" for r in rows)


def test_stages_cannot_both_predict_the_same_locus(tmp_path: Path):
    row = {"subject": "S1", "modality": "wes", "gene": "A", "method": "M"}
    _write(tmp_path / "a.tsv", [row])
    _write(tmp_path / "b.tsv", [row])
    try:
        combine_predictions([str(tmp_path / "a.tsv"), str(tmp_path / "b.tsv")],
                            str(tmp_path / "c.tsv"))
    except ValueError as exc:
        assert "duplicate" in str(exc)
    else:
        raise AssertionError("duplicate method/locus rows were accepted")


def test_decision_is_signed_and_frozen_score_is_reported():
    decision = json.loads((ROOT / "decisions" / "20261009_nestedcv_refit.json")
                          .read_text(encoding="utf-8"))
    assert decision["status"] == "SIGNED"
    with (ROOT / "artifacts" / "development_corrected" / "frozen_nestedcv_legacy.tsv").open(
            encoding="utf-8") as handle:
        assert {r["modality"] for r in csv.DictReader(handle, delimiter="\t")} == {"wes", "rnaseq"}
