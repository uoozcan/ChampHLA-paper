#!/bin/bash
#SBATCH --job-name=champhla_prefetch
#SBATCH --account=project_2008084
#SBATCH --partition=small
#SBATCH --time=72:00:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --output=/scratch/project_2008084/champhla_publication_remediation/development/logs/%x_%j.out
#SBATCH --error=/scratch/project_2008084/champhla_publication_remediation/development/logs/%x_%j.err

# Download the next CHAMPHLA_PREFETCH_AHEAD (default 1) pending RNA-seq inputs while
# the exclusive RNA-seq job runs, so each runner finds its BAM already staged. The
# source serves ~1.6 MB/s, which made the download a third to half of every RNA job.
# The runner skips a download only when the final file exists and still checks it
# (MD5, or gzip -t for the Geuvadis BAMs), so a prefetched file is re-verified.
# This job writes <file>.prefetch, verifies it, and moves it into place with mv -n:
# it never touches the runner's .partial and never replaces a file already present.
# It reads the controller's status table, submits nothing, and stops when no
# RNA-seq sample is pending.
set -eo pipefail

ROOT=${CHAMPHLA_RUN_ROOT:-/scratch/project_2008084/champhla_publication_remediation}
PAPER=${CHAMPHLA_PAPER:-${ROOT}/paper}
MANIFEST=${CHAMPHLA_DEV_MANIFEST:-${PAPER}/cohorts/development_rerun_manifest.tsv}
RUN_ROOT=${ROOT}/development
STATUS=${RUN_ROOT}/controller_status.tsv
AHEAD=${CHAMPHLA_PREFETCH_AHEAD:-1}
POLL_SECONDS=${CHAMPHLA_POLL_SECONDS:-300}
MIN_FREE_GIB=${CHAMPHLA_PREFETCH_MIN_FREE_GIB:-50}
set -u

fetch() {
  local url=$1 target=$2 md5=$3 sample_root=$4
  [[ -s ${target} ]] && return 0
  rm -f -- "${target}.prefetch"
  if ! curl --fail --location --silent --show-error --retry 5 --retry-all-errors \
      --output "${target}.prefetch" "${url}"; then
    rm -f -- "${target}.prefetch"; return 1
  fi
  if [[ -n ${md5} ]]; then
    printf '%s  %s\n' "${md5}" "${target}.prefetch" | md5sum --check --status || {
      rm -f -- "${target}.prefetch"; return 1; }
  elif [[ ${target} == *.bam ]]; then
    gzip -t -- "${target}.prefetch" || { rm -f -- "${target}.prefetch"; return 1; }
  fi
  # A sample that finished meanwhile has pruned its input; do not leave a copy behind.
  if [[ ! -f ${sample_root}/SAMPLE_COMPLETE ]]; then
    mv -n -- "${target}.prefetch" "${target}"
  fi
  rm -f -- "${target}.prefetch"
}

while true; do
  # Pending RNA-seq rows in the controller's own order; the active one is the runner's.
  mapfile -t next < <(awk -F'\t' '$2=="rnaseq" && ($3=="never_submitted" || $3=="failed_retryable") {print $1}' \
    "${STATUS}" | head -n "${AHEAD}")
  if [[ ${#next[@]} -eq 0 ]]; then
    echo "no pending RNA-seq samples; prefetch done $(date -u +%FT%TZ)"
    exit 0
  fi
  for sample in "${next[@]}"; do
    free=$(python3 "${PAPER}/scripts/manage_development_batches.py" free-gib 2>/dev/null) || free=0
    if [[ ! ${free} =~ ^[0-9]+$ || ${free} -lt ${MIN_FREE_GIB} ]]; then
      echo "$(date -u +%FT%TZ) holding: ${free:-unknown} GiB free < ${MIN_FREE_GIB}"
      break
    fi
    # '|' rather than tab: empty MD5 fields must not collapse into each other.
    IFS='|' read -r input_format input_url index_url input_md5 index_md5 < <(
      awk -F'\t' -v s="${sample}" 'NR==1{for(i=1;i<=NF;i++) c[$i]=i; next}
        $c["sample_id"]==s && $c["modality"]=="rnaseq" {
          print $c["input_format"] "|" $c["input_url"] "|" $c["index_url"] "|" \
                $c["source_input_md5"] "|" $c["source_index_md5"] }' "${MANIFEST}")
    [[ ${input_format} == BAM ]] || { echo "skip ${sample}: format ${input_format}"; continue; }
    dir=${RUN_ROOT}/inputs/rnaseq/${sample}
    mkdir -p "${dir}"
    input=${dir}/${sample}.bam
    if [[ -s ${input} && -s ${input}.bai ]]; then continue; fi
    echo "$(date -u +%FT%TZ) prefetch ${sample}"
    sample_root=${RUN_ROOT}/samples/rnaseq/${sample}
    if fetch "${input_url}" "${input}" "${input_md5}" "${sample_root}" \
        && fetch "${index_url}" "${input}.bai" "${index_md5}" "${sample_root}"; then
      echo "$(date -u +%FT%TZ) staged ${sample} $(du -sh "${dir}" | cut -f1)"
    else
      echo "$(date -u +%FT%TZ) prefetch failed for ${sample}; the runner will download it itself"
    fi
  done
  sleep "${POLL_SECONDS}"
done
