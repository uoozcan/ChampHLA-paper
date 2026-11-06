from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
PROMPT = ROOT / "FINAL_PUBLICATION_REVIEW_PROMPT.md"
pytestmark = pytest.mark.skipif(
    not PROMPT.is_file(), reason="internal prompts are held back from the public snapshot"
)


def test_final_review_requires_collector_chain_and_fitted_refits():
    text = PROMPT.read_text(encoding="utf-8")
    for required in (
        "schema-v2 collector bundle",
        "selected_input_manifest.tsv",
        "sample_run_provenance.tsv",
        "t1k_parser_provenance.tsv",
        "normalized_caller_calls.tsv",
        "rejected aggregate-only input",
        "MVFlooredCC and MetaConsensus",
        "historical frozen-secondary table",
    ):
        assert required in text


def test_final_review_remains_cluster_independent_and_refutational():
    text = PROMPT.read_text(encoding="utf-8")
    assert "No cluster dependency" in text
    assert "cold referee read" in text
    assert "refute your own findings" in text.lower()
    assert "reports/final_closure_audit_<YYYYMMDD>.tsv" in text
