#!/bin/bash
#SBATCH --job-name=champhla_dev_array
#SBATCH --account=project_2008084
#SBATCH --partition=small
#SBATCH --time=24:00:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --output=/scratch/project_2008084/champhla_publication_remediation/development/logs/champhla_dev_array_%A_%a.out
#SBATCH --error=/scratch/project_2008084/champhla_publication_remediation/development/logs/champhla_dev_array_%A_%a.err

# Stable one-row-per-task launcher for the frozen development manifest. The
# submission command supplies --array=0-(manifest_rows-1)%5. Completed samples
# are checksum/provenance validated and skipped; all others use the established
# single-sample runner under the same allocation.
set -euo pipefail

ROOT=/scratch/project_2008084/champhla_publication_remediation
MANIFEST=${CHAMPHLA_DEV_MANIFEST:-${ROOT}/paper/cohorts/development_rerun_manifest.tsv}
MANAGER=${ROOT}/paper/scripts/manage_development_batches.py
RUNNER=${ROOT}/paper/scripts/roihu_run_development_sample.sbatch
RUN_ROOT=${ROOT}/development
RELEASE_COMMIT=${CHAMPHLA_RELEASE_COMMIT:-66d949da90861da6cf60cf1d4bee2f094f2518bd}

if [[ -z ${SLURM_ARRAY_TASK_ID:-} ]]; then
  echo "This launcher must be submitted as a Slurm array." >&2
  exit 2
fi

mapfile -t row < <(python3 - "${MANIFEST}" "${SLURM_ARRAY_TASK_ID}" <<'PY'
import csv
import sys

path, task = sys.argv[1], int(sys.argv[2])
with open(path, newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle, delimiter="\t"))
if not 0 <= task < len(rows):
    raise SystemExit(f"array task {task} is outside manifest rows 0..{len(rows)-1}")
row = rows[task]
print(row["sample_id"])
print(row["modality"])
print(row["batch_id"])
PY
)

if [[ ${#row[@]} -ne 3 ]]; then
  echo "Could not decode manifest row for task ${SLURM_ARRAY_TASK_ID}." >&2
  exit 3
fi
sample_id=${row[0]}
modality=${row[1]}
batch_id=${row[2]}

if python3 - "${MANAGER}" "${MANIFEST}" "${RUN_ROOT}" \
    "${RELEASE_COMMIT}" "${sample_id}" "${modality}" <<'PY'
import importlib.util
import sys
from pathlib import Path

manager_path, manifest, run_root, release, sample, modality = sys.argv[1:]
spec = importlib.util.spec_from_file_location("development_manager", manager_path)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)
rows = module.read_manifest(Path(manifest))
matches = [row for row in rows if row["sample_id"] == sample and row["modality"] == modality]
if len(matches) != 1:
    raise SystemExit(2)
errors = module.validate_sample(Path(run_root), matches[0], release)
if errors:
    print("RUN_REQUIRED\t" + sample + "\t" + modality + "\t" + "; ".join(errors))
    raise SystemExit(1)
print("SKIP_COMPLETE\t" + sample + "\t" + modality)
PY
then
  exit 0
else
  status=$?
  if [[ ${status} -ne 1 ]]; then
    echo "Pre-run validation failed for ${sample_id} ${modality}." >&2
    exit "${status}"
  fi
fi

echo "START\t${batch_id}\t${sample_id}\t${modality}\tarray=${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
export PRUNE_ON_SUCCESS=1
export CHAMPHLA_RELEASE_COMMIT=${RELEASE_COMMIT}
exec bash "${RUNNER}" "${sample_id}" "${modality}"
