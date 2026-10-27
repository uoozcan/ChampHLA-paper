from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "scripts/audit_development_rerun_readiness.sh"


def test_readiness_audit_is_truth_free_and_checks_release_inputs_and_capacity():
    text = AUDIT.read_text(encoding="utf-8")
    lowered = text.lower()

    for required in (
        "sha256sum -c SHA256SUMS",
        "3.5.0",
        "66d949da90861da6cf60cf1d4bee2f094f2518bd",
        "num_diff_alleles",
        "Python 3.11.15",
        "tsv_sha256",
        "{'wes': 130, 'rnaseq': 106}",
        "GRCh38_full_analysis_set_plus_decoy_hla.fa",
        "t1k_hlaidx",
        "SpecHLA.sh",
        "Less than 50 GiB",
        "READINESS_PASS",
    ):
        assert required in text

    assert "reference_typing" not in lowered
    assert "ground_truth" not in lowered
