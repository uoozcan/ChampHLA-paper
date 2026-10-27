"""Synthetic, aggregate-only tests for Supplementary Figure S9."""
from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "generate_figures", ROOT / "scripts/generate_figures.py"
)
assert SPEC and SPEC.loader
FIGURES = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FIGURES)


def _rows() -> list[dict[str, str]]:
    rows = []
    for modality in FIGURES.ASSAYS:
        for caller in FIGURES.FROZEN_PANELS[modality]:
            for index, change in enumerate(FIGURES.RERUN_CHANGE_ORDER):
                rows.extend({
                    "subject": f"PRIVATE-{copy}",
                    "modality": modality,
                    "caller": caller,
                    "gene": "A",
                    "difference_class": change,
                } for copy in range(index + 1))
    return rows


def test_s6_is_deterministic_and_contains_only_aggregate_metadata(tmp_path: Path):
    first_spec, first_hashes = FIGURES.supplementary_figure9(_rows(), tmp_path / "first")
    second_spec, second_hashes = FIGURES.supplementary_figure9(_rows(), tmp_path / "second")
    assert first_hashes == second_hashes
    assert first_spec == second_spec
    assert first_spec["aggregate_only"] is True
    assert "PRIVATE" not in str(first_spec)
    assert list(first_hashes) == ["pdf", "svg", "png", "tiff"]
    for suffix in first_hashes:
        assert (tmp_path / "first" / f"supplementary_figure_s9_rerun_cell_changes.{suffix}").is_file()


def test_s6_rejects_unknown_change_classes(tmp_path: Path):
    rows = _rows()
    rows[0]["difference_class"] = "unexpected"
    try:
        FIGURES.supplementary_figure9(rows, tmp_path)
    except ValueError as exc:
        assert "unknown stored-to-rerun change classes" in str(exc)
    else:
        raise AssertionError("unknown change class was accepted")


def test_s6_panels_are_the_frozen_assay_panels():
    from champhla_confirmation.panels import PANELS
    assert FIGURES.FROZEN_PANELS == {modality: PANELS[modality] for modality in FIGURES.ASSAYS}
    assert "ArcasHLA" not in FIGURES.FROZEN_PANELS["wes"]
