#!/bin/bash
# Fail-closed Roihu readiness audit for development reruns and smoke tests.
# This script reads no reference typing or outcomes.
set -eo pipefail

ROOT=${CHAMPHLA_RUN_ROOT:-/scratch/project_2008084/champhla_publication_remediation}
PIPELINE=${CHAMPHLA_PIPELINE:-${ROOT}/releases/PanelHLA-3.5.0}
PAPER=${CHAMPHLA_PAPER:-${ROOT}/paper}
MANIFEST=${CHAMPHLA_DEV_MANIFEST:-${PAPER}/cohorts/development_rerun_manifest.tsv}
MANIFEST_META=${CHAMPHLA_DEV_MANIFEST_META:-${PAPER}/cohorts/development_rerun_manifest.json}
RELEASE_META=${CHAMPHLA_RELEASE_META:-${PAPER}/scripts/PanelHLA-3.5.0.json}
RELEASE_ARCHIVE=${CHAMPHLA_RELEASE_ARCHIVE:-${ROOT}/PanelHLA-3.5.0.tar.gz}
REPORT=${1:-${ROOT}/development/readiness_audit.txt}

# shellcheck disable=SC1090
source "${PIPELINE}/bin/roihu_env.sh"
set -u
mkdir -p "$(dirname "${REPORT}")"

exec > >(tee "${REPORT}") 2>&1
printf 'ChampHLA development rerun readiness audit\n'
date --iso-8601=seconds

cd "${ROOT}"
sha256sum -c SHA256SUMS
test -s "${PIPELINE}/main.nf"
test -s "${PIPELINE}/bin/parse_t1k_results.py"
grep -q '^version: "3.5.0"$' "${PIPELINE}/CITATION.cff"
grep -q "num_diff_alleles" "${PIPELINE}/bin/parse_t1k_results.py"
grep -q "T1K_FASTQ|T1K_LONGREADS" "${PIPELINE}/conf/hpc_binds.config"
command -v bwa >/dev/null

python3 - "${RELEASE_META}" "${RELEASE_ARCHIVE}" <<'PY'
import hashlib, json, sys
meta_path, archive_path = sys.argv[1:]
with open(meta_path, encoding='utf-8') as handle:
    meta = json.load(handle)
if meta['tag'] != 'v3.5.0':
    raise SystemExit(f"wrong release tag: {meta['tag']}")
if meta['commit'] != '66d949da90861da6cf60cf1d4bee2f094f2518bd':
    raise SystemExit(f"wrong release commit: {meta['commit']}")
h = hashlib.sha256()
with open(archive_path, 'rb') as handle:
    for chunk in iter(lambda: handle.read(1024 * 1024), b''):
        h.update(chunk)
if h.hexdigest() != meta['archive_sha256']:
    raise SystemExit('release archive SHA-256 mismatch')
print(f"release archive OK: {meta['commit']} {h.hexdigest()}")
PY

python3 - "${MANIFEST}" "${MANIFEST_META}" <<'PY'
import csv, hashlib, json, sys
tsv, meta = sys.argv[1:]
with open(meta, encoding='utf-8') as handle:
    metadata = json.load(handle)
with open(tsv, 'rb') as handle:
    observed = hashlib.sha256(handle.read()).hexdigest()
if observed != metadata['tsv_sha256']:
    raise SystemExit('development manifest SHA-256 mismatch')
with open(tsv, newline='', encoding='utf-8') as handle:
    rows = list(csv.DictReader(handle, delimiter='\t'))
counts = {modality: sum(row['modality'] == modality for row in rows)
          for modality in ('wes', 'rnaseq')}
if counts != {'wes': 130, 'rnaseq': 106}:
    raise SystemExit(f'roster count mismatch: {counts}')
if len({(row['sample_id'], row['modality']) for row in rows}) != len(rows):
    raise SystemExit('duplicate sample/modality row')
print(f"truth-free manifest OK: {counts}")
PY

python_version=$(python3 --version 2>&1)
printf '%s\n' "${python_version}"
if [[ ${python_version} != "Python 3.11.15" ]]; then
  echo "Expected Python 3.11.15, found ${python_version}" >&2
  exit 8
fi
samtools --version | head -n 1
nextflow -version
apptainer --version

test -s /scratch/project_2008084/hla_references/genomes/GRCh38_full_analysis_set_plus_decoy_hla.fa
test -s /scratch/project_2008084/hla_references/genomes/GRCh38_full_analysis_set_plus_decoy_hla.fa.fai
test -s /scratch/project_2008084/hla_references/genomes/hla_rescue_GRCh38_chr6/chr6.fa
test -d /scratch/project_2008084/hla_references/t1k_hlaidx
test -s /scratch/project_2008084/hla_references/t1k_hlaidx/_dna_seq.fa
test -s /projappl/project_2008084/SpecHLAx/script/whole/SpecHLA.sh
git -C /projappl/project_2008084/SpecHLAx rev-parse HEAD

for image in arcashla.sif hlahd.sif optitype.sif polysolver.sif t1k.sif; do
  test -s "/scratch/project_2008084/hla_references/singularity_cache/containers/${image}"
  sha256sum "/scratch/project_2008084/hla_references/singularity_cache/containers/${image}"
done

available_kb=$(df --output=avail /scratch | tail -n 1 | tr -d ' ')
if [[ ${available_kb} -lt 52428800 ]]; then
  echo "Less than 50 GiB available on /scratch" >&2
  exit 9
fi
df -h /scratch
squeue --me
printf 'READINESS_PASS\n'
