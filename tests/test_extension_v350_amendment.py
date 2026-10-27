import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AMENDMENT = ROOT / "decisions/20261013_extension_v350_preregistration_amendment.json"


def test_v350_amendment_is_exact_and_fail_closed_in_either_state():
    """Unsigned, everything is closed. Signed (signature_rule: committed alone), the
    analysis commit and code digest are pinned, staging is permitted, and the truth join
    stays closed until the separate Zenodo publication record exists."""
    import re

    record = json.loads(AMENDMENT.read_text(encoding="utf-8"))
    release = record["release_pin"]
    assert release["tag"] == "v3.5.0"
    assert release["commit"] == "66d949da90861da6cf60cf1d4bee2f094f2518bd"
    assert release["archive_sha256"] == "22d9ed3bd808aec7364fbe869ad048c561be38bd02479dff530fe13fee4da7ed"
    gates = record["gates"]
    if not record["authorization"]["signed"]:
        assert release["analysis_commit"] is None
        assert not any(gates.values())
        assert "forbidden" in record["status"]
        return
    assert record["status"].startswith("SIGNED")
    assert re.fullmatch(r"[0-9a-f]{40}", release["analysis_commit"])
    assert re.fullmatch(r"[0-9a-f]{64}", release["analysis_code_sha256"])
    assert gates["author_signed"] and gates["analysis_commit_pinned"]
    assert gates["extension_stage_or_submit_permitted"]
    assert gates["truth_join_permitted"] is False
    assert record["zenodo"]["reserved_doi"] == "10.5281/zenodo.23251288"
    assert record["zenodo"]["publication_record"].startswith("decisions/")


def test_t1k_correction_and_unchanged_rules_are_complete():
    record = json.loads(AMENDMENT.read_text(encoding="utf-8"))
    t1k = record["t1k_correction"]
    assert "nine-column" in t1k["schema"] and "legacy eight-column" in t1k["schema"]
    assert "<=0" in t1k["quality"]
    assert "homozygosity" in t1k["count_one"]
    assert "never homozygous" in t1k["count_two"]
    assert "never promote" in t1k["secondary_alleles"]
    unchanged = " ".join(record["unchanged_commitments"])
    for phrase in ("plurality", "89-WES/99-RNA", "exact two-field", "one-time truth join", "regardless of direction"):
        assert phrase in unchanged
