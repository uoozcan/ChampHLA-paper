import csv
import json

from champhla_confirmation.protocol import validate_benchmark_resource_protocol


def _write_tsv(path, fields, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def test_protocol_fails_closed_on_exposure_overlap(tmp_path):
    protocol = tmp_path / "protocol.json"
    protocol.write_text(json.dumps({
        "modalities": ["wes", "rnaseq"], "wgs_accuracy_allowed": False,
        "extension_rosters": {"wes_subjects": 1, "rnaseq_subjects": 1},
    }), encoding="utf-8")
    roster = tmp_path / "roster.tsv"
    _write_tsv(roster, ["subject", "modality"], [
        {"subject": "S1", "modality": "wes"},
        {"subject": "S2", "modality": "rnaseq"},
        {"subject": "S3", "modality": "wgs"},
    ])
    exposure = tmp_path / "exposure.tsv"
    _write_tsv(exposure, ["canonical_subject", "exposure_role"], [
        {"canonical_subject": "S2", "exposure_role": "development_exposed"},
    ])
    result = validate_benchmark_resource_protocol(str(protocol), str(roster), str(exposure))
    assert not result["valid"]
    assert result["development_extension_overlap"] == ["S2"]
    assert result["wgs_rows_selected"] == 0
