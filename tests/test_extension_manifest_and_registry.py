"""The frozen-extension input manifest and the EXT_* registry rows (no truth involved)."""
from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _module(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def test_committed_extension_manifest_is_the_frozen_roster_and_disjoint(tmp_path):
    builder = _module("build_extension_manifest")
    committed = ROOT / "cohorts/extension_v350_manifest.tsv"
    regenerated = tmp_path / "manifest.tsv"
    assert builder.main(["--output-tsv", str(regenerated),
                         "--output-json", str(tmp_path / "manifest.json")]) == 0
    assert regenerated.read_bytes() == committed.read_bytes()
    rows = _rows(committed)
    assert {m: sum(r["modality"] == m for r in rows) for m in ("wes", "rnaseq")} == {
        "wes": 89, "rnaseq": 99}
    assert all(row["batch_id"].startswith("ext-") for row in rows)
    development = {(r["sample_id"], r["modality"]) for r in
                   _rows(ROOT / "cohorts/development_rerun_manifest.tsv")}
    assert not {r["sample_id"] for r in rows} & {key[0] for key in development}
    metadata = json.loads((ROOT / "cohorts/extension_v350_manifest.json").read_text("utf-8"))
    assert metadata["source_files"]["cohorts/frozen_initial_rosters.tsv"] == builder.FROZEN_ROSTER_SHA256


def test_extension_manifest_refuses_a_changed_roster(tmp_path):
    builder = _module("build_extension_manifest")
    changed = tmp_path / "roster.tsv"
    changed.write_bytes((ROOT / "cohorts/frozen_initial_rosters.tsv").read_bytes() + b"\n")
    with pytest.raises(SystemExit, match="differs from the pre-registration pin"):
        builder.main(["--roster", str(changed), "--output-tsv", str(tmp_path / "m.tsv"),
                      "--output-json", str(tmp_path / "m.json")])


def _write(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t",
                                lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _performance(modality, method, correct="80", loci="90"):
    return {"modality": modality, "method": method, "analysis_scope": "primary",
            "subjects": "40", "loci": loci, "rows_present": loci, "callable": loci,
            "genotypes_correct": correct, "genotype_accuracy": str(int(correct) / int(loci)),
            "genotype_ci_lo": "0.8", "genotype_ci_hi": "0.95",
            "interval_method": "subject_cluster_percentile_bootstrap", "boundary_intervals": ""}


def _paired(modality, comparator):
    return {"modality": modality, "comparator": comparator, "clusters": "40", "loci": "90",
            "delta_points": "1.1", "simultaneous_ci_lo_points": "-2",
            "simultaneous_ci_hi_points": "4", "inference_method": "signflip",
            "signflip_p_value": "0.5", "signflip_holm_adjusted_p": "1",
            "holm_adjusted_p": "1", "inference_family": "confirmatory", "family_size": "7"}


def test_extension_rows_are_absent_until_evaluated_and_never_external(tmp_path, monkeypatch):
    registry = _module("generate_result_registry")
    monkeypatch.setattr(registry, "EXTENSION", tmp_path / "extension")
    rows: list[dict[str, str]] = []
    registry.append_extension_rows(rows)
    assert rows == []

    _write(tmp_path / "extension/method_performance.tsv", [
        _performance("wes", "SimplePluralityLex"), _performance("rnaseq", "SimplePluralityLex"),
        _performance("wes", "Caller:OptiType"),
    ])
    with pytest.raises(SystemExit, match="incomplete extension evaluation"):
        registry.append_extension_rows([])
    _write(tmp_path / "extension/secondary_method_results.tsv",
           [_paired("wes", "Caller:OptiType"), _paired("rnaseq", "Caller:HLA-HD")])
    (tmp_path / "extension/unblinding_manifest.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(registry, "ROOT", tmp_path)
    registry.append_extension_rows(rows)
    by_id = {row["result_id"]: row for row in rows}
    assert set(by_id) == {"EXT_WES_SIMPLEPLURALITYLEX", "EXT_RNASEQ_SIMPLEPLURALITYLEX",
                          "EXT_WES_CALLER_OPTITYPE", "EXT_PAIRED_WES_CALLER_OPTITYPE",
                          "EXT_PAIRED_RNASEQ_CALLER_HLA_HD"}
    assert all(row["analysis_status"] != "external_confirmation" for row in rows)
    assert all("not independent external validation" in row["claim_boundary"] for row in rows)
    # Every frozen RNA-seq row missed its locked minimum, so RNA-seq is descriptive.
    assert by_id["EXT_RNASEQ_SIMPLEPLURALITYLEX"]["analysis_status"] == "preregistered_descriptive"
    assert by_id["EXT_RNASEQ_SIMPLEPLURALITYLEX"]["abstract_allowed"] == "0"
    assert by_id["EXT_WES_CALLER_OPTITYPE"]["analysis_status"] == "descriptive_comparator"


def test_wes_eligibility_follows_the_frozen_roster():
    registry = _module("generate_result_registry")
    eligible = registry.extension_confirmation_modalities()
    assert "rnaseq" not in eligible
