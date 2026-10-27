"""Evidence table for incomplete ledgered development runs (read-only except the output TSV)."""

import csv
from collections import Counter
import importlib.util
from pathlib import Path

R = Path("/scratch/project_2008084/champhla_publication_remediation")
D = R / "development"
L = D / "logs"
spec = importlib.util.spec_from_file_location(
    "m", R / "paper/scripts/manage_development_batches.py"
)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
manifest = {
    (r["sample_id"], r["modality"]): r
    for r in m.read_manifest(R / "paper/cohorts/development_rerun_manifest.tsv")
}
attempts = m.attempts_by_key(
    m.read_rows(D / "submission_ledger.tsv"), m.read_rows(D / "retry_ledger.tsv")
)
out, review = [], []
for key, history in sorted(attempts.items()):
    if not m.validate_sample(D, manifest[key], m.DEFAULT_RELEASE_COMMIT):
        continue
    job = history[-1][1]
    state, code = m.job_outcome(job)
    if "_" in job:
        array, task = job.split("_")
        logs = [
            L / f"champhla_dev_array_{array}_{task}.err",
            L / f"champhla_dev_array_{array}_{task}.out",
        ]
    else:
        logs = [L / f"champhla_dev_{job}.err", L / f"champhla_dev_{job}.out"]
    sample_logs = [
        D / "samples" / key[1] / key[0] / n for n in ("nextflow.stdout.log", "nextflow.stderr.log")
    ]
    texts = {p: p.read_text(errors="replace") for p in logs + sample_logs if p.exists()}
    quota = [p.name for p, t in texts.items() if "Disk quota exceeded" in t or "Errno 122" in t]
    curl23 = any("curl: (23)" in t for t in texts.values())
    err = logs[0]
    empty = err.exists() and err.stat().st_size == 0
    if quota:
        evidence = "'Disk quota exceeded' in " + ",".join(quota)
    elif curl23:
        evidence = "curl (23) failure writing the download"
    elif empty and code.startswith("23:"):
        evidence = "exit 23 (curl write error) with a 0-byte stderr log"
    elif empty and code.startswith(("1:", "120:")):
        evidence = "0-byte stderr log, consistent with the quota being full when it was written"
    else:
        review.append((key, job, state, code))
        continue
    note = (
        f"job {job} {state} exit {code}; {evidence}; project_2008084 scratch quota exhausted "
        "2026-10-15 01:04-09:46 UTC+3. Classified by Claude Code on author instruction 2026-10-16."
    )
    out.append({"sample_id": key[0], "modality": key[1], "failure_class": "storage", "note": note})
path = D / "classification_20261016_storage.tsv"
with path.open("w", newline="", encoding="utf-8") as h:
    w = csv.DictWriter(
        h,
        fieldnames=["sample_id", "modality", "failure_class", "note"],
        delimiter="\t",
        lineterminator="\n",
    )
    w.writeheader()
    w.writerows(out)
print(
    f"incomplete_ledgered={len(out) + len(review)} storage_evidence={len(out)} needs_review={len(review)} -> {path}"
)
for item in review:
    print("REVIEW", *item)

print(Counter(r["note"].split("; ")[1].split(" in ")[0] for r in out))
