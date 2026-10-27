from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_release_boundary_refits_instead_of_retaining_historical_rows():
    development = (ROOT / "src" / "champhla_confirmation" / "development.py").read_text(
        encoding="utf-8"
    )
    reproduction = (ROOT / "scripts" / "reproduce_development_benchmark.py").read_text(
        encoding="utf-8"
    )
    assert 'retained_frozen: set[str] = set()' in development
    assert "refit_secondary_fitted_methods(" in reproduction
    assert "development_secondary_fitted_predictions.tsv" in reproduction
