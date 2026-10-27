from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAIRED = ROOT / "artifacts" / "development_characterisation" / "ambiguity_paired_results.tsv"
REGISTRY = ROOT / "result_registry.tsv"


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _slug(value: str) -> str:
    import re
    return re.sub(r"[^A-Z0-9]+", "_", value.upper()).strip("_")


def test_set_valued_paired_results_have_one_row_per_comparator_and_modality():
    rows = _rows(PAIRED)
    keys = [(row["modality"], row["comparator"]) for row in rows]
    assert rows and len(keys) == len(set(keys))
    assert {row["modality"] for row in rows} == {"wes", "rnaseq"}
    assert all(row["comparator"] != "SimplePluralityLex" for row in rows)
    assert {row["endpoint"] for row in rows} == {"set_valued_two_field_compatibility"}


def test_set_valued_deltas_and_holm_families_recompute_from_counts():
    rows = _rows(PAIRED)
    for row in rows:
        loci = int(row["loci"])
        expected = 100 * (
            int(row["consensus_compatible"]) - int(row["comparator_compatible"])
        ) / loci
        assert abs(float(row["delta_points"]) - expected) < 1e-12
        family = [
            item for item in rows
            if item["modality"] == row["modality"]
            and item["inference_family"] == row["inference_family"]
        ]
        active = [item for item in family if int(item["wins"]) or int(item["losses"])]
        assert int(row["family_size"]) == len(active)
        assert int(row["multiplicity_included"]) == int(row in active)
        raw = float(row["signflip_p_value"])
        adjusted = float(row["signflip_holm_adjusted_p"])
        assert 0 <= raw <= adjusted <= 1


def test_set_valued_signflip_assignment_policy_is_auditable_through_25_subjects():
    for row in _rows(PAIRED):
        discordant = int(row["discordant_subjects"])
        expected_assignments = 2 ** discordant if discordant <= 25 else 1_000_000
        expected_method = (
            "exact_enumeration" if discordant <= 25 else "monte_carlo_plus_one"
        )
        assert int(row["signflip_assignments"]) == expected_assignments
        assert row["signflip_method"] == expected_method
        assert int(row["signflip_seed"]) >= 0


def test_every_set_valued_paired_result_is_registry_backed():
    registry = {row["result_id"]: row for row in _rows(REGISTRY)}
    for row in _rows(PAIRED):
        result_id = (
            f"DEV_AMBIGUITY_PAIRED_{row['modality'].upper()}_"
            f"{_slug(row['comparator'])}"
        )
        registered = registry[result_id]
        assert registered["artifact_path"].endswith("ambiguity_paired_results.tsv")
        assert registered["raw_p"] == row["signflip_p_value"]
        assert registered["adjusted_p"] == row["signflip_holm_adjusted_p"]
        assert registered["endpoint"] == (
            "paired_set_valued_compatibility_difference_percentage_points"
        )
