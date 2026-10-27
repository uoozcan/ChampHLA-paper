"""SR-012: fitted comparators are reproducible from v3.5.0-shaped inputs."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from champhla_confirmation.fitted import (
    META_METHOD,
    MV_FLOOR_METHOD,
    learn_mv_floor_routing,
    refit_fitted_methods,
    score_meta,
)


CALLERS = ("HLA-HD", "OptiType", "POLYSOLVER", "SpecHLA", "T1K")
PAIR_ONE = ("A*01:01", "A*02:01")
PAIR_TWO = ("A*03:01", "A*24:02")


def _row(subject: str, caller: str, pair: tuple[str, str]) -> dict[str, str]:
    return {
        "cohort": "synthetic",
        "subject": subject,
        "superpopulation": "TEST",
        "modality": "wes",
        "gene": "A",
        "caller": caller,
        "allele1": pair[0],
        "allele2": pair[1],
        "call_status": "callable",
    }


def _fixture(tmp_path: Path):
    calls = []
    truth = {}
    folds = {}
    for index in range(6):
        subject = f"S{index}"
        folds[(subject, "wes")] = str(index % 3)
        target = PAIR_ONE if index % 2 == 0 else PAIR_TWO
        truth[("synthetic", subject, "wes", "A")] = target
        for caller_index, caller in enumerate(CALLERS):
            pair = target if caller_index < 3 else (PAIR_TWO if target == PAIR_ONE else PAIR_ONE)
            calls.append(_row(subject, caller, pair))
    policy = {
        "schema_version": "truth-free-raw-cc-policy-1",
        "policies": {
            "wes": {
                "champions": {"A": "OptiType"},
                "min_challenger_support_fraction": 0.35,
                "min_challenger_margin": 0.0,
                "min_supporting_tools": 1,
            }
        },
        "weights": {"wes": {caller: {"A": 1.0} for caller in CALLERS}},
    }
    policy_path = tmp_path / "policy.json"
    policy_path.write_text(json.dumps(policy), encoding="utf-8")
    return calls, truth, folds, policy_path


def test_refit_emits_both_methods_from_v350_schema(tmp_path: Path):
    calls, truth, folds, policy = _fixture(tmp_path)
    rows, manifest = refit_fitted_methods(
        calls, truth, folds, str(policy), inner_folds=2, mv_min_loci=1
    )
    assert {row["method"] for row in rows} == {MV_FLOOR_METHOD, META_METHOD}
    assert len(rows) == 12
    assert all(row["analysis_scope"] == "exploratory_fitted" for row in rows)
    assert not any("truth" in field.lower() for row in rows for field in row)
    assert manifest["truth_values_used_for_prediction"] == "training_folds_only"
    assert manifest["held_out_truth_columns_in_prediction_input"] is False


def test_held_subject_truth_does_not_change_its_predictions(tmp_path: Path):
    calls, truth, folds, policy = _fixture(tmp_path)
    first, _ = refit_fitted_methods(
        calls, truth, folds, str(policy), inner_folds=2, mv_min_loci=1
    )
    changed = dict(truth)
    changed[("synthetic", "S0", "wes", "A")] = PAIR_TWO
    second, _ = refit_fitted_methods(
        calls, changed, folds, str(policy), inner_folds=2, mv_min_loci=1
    )
    def project(rows):
        return [
            (row["method"], row["allele1"], row["allele2"], row["decision_reason"])
            for row in rows if row["subject"] == "S0"
        ]
    assert project(first) == project(second)


def test_mv_floor_requires_all_three_training_gates():
    vote, cc, truth = [], [], {}
    for index in range(20):
        subject = f"S{index:02d}"
        key = ("synthetic", subject, "wes", "A")
        truth[key] = PAIR_ONE
        common = {
            "cohort": "synthetic", "subject": subject, "modality": "wes", "gene": "A",
            "top_support": "2", "callable_tools": "4", "call_status": "callable",
        }
        vote.append({**common, "allele1": PAIR_TWO[0], "allele2": PAIR_TWO[1]})
        cc.append({**common, "allele1": PAIR_ONE[0], "allele2": PAIR_ONE[1]})
    routing = learn_mv_floor_routing(vote, cc, truth)
    assert routing["split"]["route"] == "cc"
    assert learn_mv_floor_routing(vote[:19], cc[:19], truth)["split"]["route"] == "mv"


def test_runtime_meta_scoring_rejects_truth_bearing_rows():
    with pytest.raises(ValueError, match="truth-bearing"):
        score_meta([{
            **_row("S0", "OptiType", PAIR_ONE),
            "truth_allele1": PAIR_ONE[0],
        }], {
            "context": {}, "feature_schema": {}, "candidate_model": {}, "model_sha256": "x",
        }, "0")
