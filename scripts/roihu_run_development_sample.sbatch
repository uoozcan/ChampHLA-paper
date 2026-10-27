#!/bin/bash
#SBATCH --job-name=champhla_dev
#SBATCH --account=project_2008084
#SBATCH --partition=small
#SBATCH --time=24:00:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --output=/scratch/project_2008084/champhla_publication_remediation/development/logs/%x_%j.out
#SBATCH --error=/scratch/project_2008084/champhla_publication_remediation/development/logs/%x_%j.err

# One truth-free, restartable development-rerun sample. Usage:
#   sbatch roihu_run_development_sample.sbatch HG00096 wes
# Set PRUNE_ON_SUCCESS=1 only after a smoke run has passed. It removes exactly
# this sample's downloaded public input and Nextflow work directory after every
# result and provenance file has been hashed.
# PRUNE_ON_FAILURE=1 does the same after any failure, once the small task files
# and logs are copied to forensics/<job>/, so failed attempts cannot fill scratch.
# Before anything is staged, the project scratch headroom must cover
# CHAMPHLA_RESERVE_GIB (default 60 GiB WES, 25 GiB RNA-seq); otherwise the job
# exits 10, which the controller classifies as a storage deferral.
# While the sample runs, a watcher samples the headroom every CHAMPHLA_WATCH_SECONDS
# (default 30) into storage_watch_<job>.tsv. If it ever falls below
# CHAMPHLA_TAINT_GIB (default 2), or a task log reports a quota error, the run
# exits 11 and is never marked complete: HLA-HD exited 0 on truncated whole-BAM
# intermediates when the quota filled on 2026-10-15/16.
set -eo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: sbatch $0 <sample_id> <wes|rnaseq>" >&2
  exit 2
fi
sample_id=$1
modality=$2
if [[ ! ${sample_id} =~ ^((HG|NA)[0-9]+|NCI60_[A-Z0-9]+)$ || ! ${modality} =~ ^(wes|rnaseq)$ ]]; then
  echo "Unsafe sample or modality: ${sample_id} ${modality}" >&2
  exit 2
fi

ROOT=${CHAMPHLA_RUN_ROOT:-/scratch/project_2008084/champhla_publication_remediation}
PIPELINE=${CHAMPHLA_PIPELINE:-${ROOT}/releases/PanelHLA-3.5.0}
PAPER=${CHAMPHLA_PAPER:-${ROOT}/paper}
MANIFEST=${CHAMPHLA_DEV_MANIFEST:-${PAPER}/cohorts/development_rerun_manifest.tsv}
# Another roster (the frozen extension) runs in its own directory; the manager passes it.
RUN_ROOT=${CHAMPHLA_RUN_DIR:-${ROOT}/development}
SAMPLE_ROOT=${RUN_ROOT}/samples/${modality}/${sample_id}
INPUT_ROOT=${RUN_ROOT}/inputs/${modality}/${sample_id}
WORK_DIR=${RUN_ROOT}/work/${modality}_${sample_id}
RESULTS=${SAMPLE_ROOT}/results
PRUNE_ON_SUCCESS=${PRUNE_ON_SUCCESS:-0}
RELEASE_COMMIT=${CHAMPHLA_RELEASE_COMMIT:-66d949da90861da6cf60cf1d4bee2f094f2518bd}
REQUIRE_T1K_SUCCESS=${REQUIRE_T1K_SUCCESS:-0}
PRUNE_ON_FAILURE=${PRUNE_ON_FAILURE:-0}
if [[ ${modality} == wes ]]; then default_reserve=60; else default_reserve=25; fi
RESERVE_GIB=${CHAMPHLA_RESERVE_GIB:-${default_reserve}}
TAINT_GIB=${CHAMPHLA_TAINT_GIB:-2}
WATCH_SECONDS=${CHAMPHLA_WATCH_SECONDS:-30}
run_tag=${SLURM_JOB_ID:-$$}.${SLURM_RESTART_COUNT:-0}
WATCH_LOG=${SAMPLE_ROOT}/storage_watch_${run_tag}.tsv
PRESSURE=${SAMPLE_ROOT}/STORAGE_PRESSURE.${run_tag}
if [[ ${PRUNE_ON_FAILURE} != 0 && ${PRUNE_ON_FAILURE} != 1 ]]; then
  echo "PRUNE_ON_FAILURE must be 0 or 1" >&2
  exit 8
fi
if [[ ! ${RESERVE_GIB} =~ ^[0-9]+$ || ! ${TAINT_GIB} =~ ^[0-9]+$ || ! ${WATCH_SECONDS} =~ ^[1-9][0-9]*$ ]]; then
  echo "CHAMPHLA_RESERVE_GIB, CHAMPHLA_TAINT_GIB and CHAMPHLA_WATCH_SECONDS must be whole numbers" >&2
  exit 2
fi

export NXF_OPTS='-Xms256m -Xmx4g'
# Source the release-owned bootstrap so Nextflow, samtools and the bwa required by
# RESCUE_HLA_READS are the exact tested Roihu modules.
# shellcheck disable=SC1090
source "${PIPELINE}/bin/roihu_env.sh"
set -u
mkdir -p "${RUN_ROOT}/logs" "${SAMPLE_ROOT}" "${INPUT_ROOT}" "${RUN_ROOT}/work"

mapfile -t fields < <(python3 - "${MANIFEST}" "${sample_id}" "${modality}" <<'PY'
import csv, sys
path, sample, modality = sys.argv[1:]
with open(path, newline='', encoding='utf-8') as handle:
    matches = [row for row in csv.DictReader(handle, delimiter='\t')
               if row['sample_id'] == sample and row['modality'] == modality]
if len(matches) != 1:
    raise SystemExit(f"expected one manifest row, found {len(matches)}")
row = matches[0]
for key in ('input_format', 'expected_genome_build', 'input_url', 'index_url',
            'source_input_md5', 'source_index_md5', 'source_record', 'batch_id'):
    print(row[key])
# FASTQ rosters (NCI-60) may subsample RNA-seq pairs; "-" means no subsampling.
print(row.get('subsample_pairs', '') or '-')
print(row.get('subsample_seed', '') or '-')
PY
)
if [[ ${#fields[@]} -ne 10 ]]; then
  echo "Could not decode the frozen manifest row" >&2
  exit 3
fi
input_format=${fields[0]}
expected_build=${fields[1]}
input_url=${fields[2]}
index_url=${fields[3]}
source_input_md5=${fields[4]}
source_index_md5=${fields[5]}
source_record=${fields[6]}
batch_id=${fields[7]}
subsample_pairs=${fields[8]#-}
subsample_seed=${fields[9]#-}

case "${input_format}" in
  CRAM) extension=cram; index_extension=crai; sheet_column=cram_path ;;
  BAM)  extension=bam;  index_extension=bai;  sheet_column=bam_path ;;
  FASTQ) sheet_column=fastq ;;
  *) echo "Unsupported input format ${input_format}" >&2; exit 3 ;;
esac
if [[ ${input_format} == FASTQ ]]; then
  # Paired FASTQ (decisions/20261026_nci60_v350_regeneration.json): input_url is
  # mate 1 and index_url mate 2.
  input_path=${INPUT_ROOT}/${sample_id}_1.fastq.gz
  index_path=${INPUT_ROOT}/${sample_id}_2.fastq.gz
else
  input_path=${INPUT_ROOT}/${sample_id}.${extension}
  index_path=${input_path}.${index_extension}
fi

# The watcher keeps its verdict on node-local disk first: a full project quota may
# refuse even the marker on scratch, which is copied over once the run has ended.
watch_mark=$(mktemp "${TMPDIR:-/tmp}/champhla_pressure.XXXXXX")
watcher_pid=
storage_watcher() {
  set +e
  local misses=0 free usage now
  while true; do
    now=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    free=$(python3 "${PAPER}/scripts/manage_development_batches.py" free-gib 2>/dev/null)
    usage=$(du -sk -- "${WORK_DIR}" "${INPUT_ROOT}" 2>/dev/null | awk '{s += $1} END {printf "%.1f", s / 1048576}')
    printf '%s\t%s\t%s\n' "${now}" "${free:-unknown}" "${usage}" >> "${WATCH_LOG}" 2>/dev/null
    if [[ ${free} =~ ^-?[0-9]+$ ]]; then
      misses=0
      if (( free < TAINT_GIB )); then
        printf '%s\tfree_gib=%s\tbelow %s GiB\n' "${now}" "${free}" "${TAINT_GIB}" >> "${watch_mark}"
      fi
    else
      misses=$((misses + 1))
      if (( misses >= 4 )); then
        printf '%s\theadroom unreadable %s times in a row\n' "${now}" "${misses}" >> "${watch_mark}"
      fi
    fi
    sleep "${WATCH_SECONDS}"
  done
}
stop_watcher() {
  if [[ -n ${watcher_pid} ]]; then
    kill "${watcher_pid}" 2>/dev/null || true
    wait "${watcher_pid}" 2>/dev/null || true
    watcher_pid=
  fi
}
storage_tainted() {
  [[ -s ${watch_mark} ]] || grep -rqsE --include=.command.err --include=.command.log \
    --include=.command.out 'Disk quota exceeded|No space left on device' -- "${WORK_DIR}"
}
record_taint() {
  {
    cat -- "${watch_mark}" 2>/dev/null
    printf 'task logs or watcher report project quota exhaustion during job %s\n' "${run_tag}"
  } >> "${PRESSURE}" || touch "${PRESSURE}" || true
}

prune_after_failure() {
  local status=$?
  stop_watcher
  if [[ ${status} -ne 0 && ${status} -ne 10 && ${status} -ne 11 ]] && storage_tainted; then
    echo "Project quota was exhausted during this run; exit ${status} reported as 11" >&2
    record_taint
    status=11
  fi
  rm -f -- "${watch_mark}"
  if [[ ${status} -eq 0 || ${PRUNE_ON_FAILURE} != 1 || -f ${SAMPLE_ROOT}/SAMPLE_COMPLETE ]]; then
    exit "${status}"
  fi
  local forensics=${SAMPLE_ROOT}/forensics/${SLURM_JOB_ID:-unknown_job}
  mkdir -p "${forensics}"
  local keep_work=0
  if [[ -d ${WORK_DIR} ]]; then
    if ! (cd "${WORK_DIR}" && find . -type f \( -name '.command.*' -o -name '.exitcode' \) \
      -size -10M -print0 | tar --force-local --null -czf "${forensics}/task_files.tar.gz" -T -); then
      # Never delete the only copy of the task diagnostics.
      keep_work=1
      printf 'forensic archive failed; work directory kept: %s\n' "${WORK_DIR}" \
        > "${forensics}/FORENSICS_FAILED"
    fi
  fi
  for log in "${SAMPLE_ROOT}/nextflow.stdout.log" "${SAMPLE_ROOT}/nextflow.stderr.log" \
    "${SAMPLE_ROOT}/nxf_launch/.nextflow.log"; do
    if [[ -f ${log} ]]; then cp -p -- "${log}" "${forensics}/" || true; fi
  done
  if [[ -d ${RESULTS} ]]; then mv -- "${RESULTS}" "${forensics}/results_failed_attempt" || true; fi
  printf '%s\n' "${status}" > "${forensics}/runner.exit"
  if [[ ${keep_work} -eq 0 ]]; then rm -rf -- "${WORK_DIR:?}"; fi
  rm -f -- "${input_path}" "${index_path}" "${input_path}.partial" "${index_path}.partial"
  rm -f -- "${INPUT_ROOT}/${sample_id}"_[12].fastq.gz "${INPUT_ROOT}/${sample_id}"_[12].sub.fastq.gz
  printf 'work and downloaded input pruned after failure (exit %s); forensics in %s\n' \
    "${status}" "${forensics}" > "${SAMPLE_ROOT}/PRUNED_AFTER_FAILURE"
  exit "${status}"
}
trap prune_after_failure EXIT

# Storage gate: fail closed before staging when the headroom is unknown or short.
free_gib=$(python3 "${PAPER}/scripts/manage_development_batches.py" free-gib) || free_gib=
if [[ ! ${free_gib} =~ ^[0-9]+$ || ${free_gib} -lt ${RESERVE_GIB} ]]; then
  echo "Storage gate: ${free_gib:-unknown} GiB free, ${RESERVE_GIB} GiB required; nothing staged" >&2
  exit 10
fi
storage_watcher &
watcher_pid=$!

# A retry must not inherit caller outputs published by an earlier failed attempt.
if [[ -d ${RESULTS} && ! -f ${SAMPLE_ROOT}/SAMPLE_COMPLETE ]]; then
  stale=${SAMPLE_ROOT}/stale_attempts/$(date -u +%Y%m%dT%H%M%SZ)
  mkdir -p "${stale}"
  mv -- "${RESULTS}" "${stale}/results"
fi

download_one() {
  local url=$1 target=$2 expected_md5=$3
  if [[ ! -s ${target} ]]; then
    # Never resume a .partial left by an earlier job: after a NODE_FAIL requeue on
    # 2026-10-16 the dead node's partial failed its MD5 on resume. curl's own
    # --retry still resumes within this one invocation.
    rm -f -- "${target}.partial"
    curl --fail --location --retry 5 --retry-all-errors --continue-at - \
      --output "${target}.partial" "${url}"
    mv "${target}.partial" "${target}"
  fi
  if [[ -n ${expected_md5} ]]; then
    printf '%s  %s\n' "${expected_md5}" "${target}" | md5sum --check --status
  elif [[ ${target} == *.bam || ${target} == *.fastq.gz ]]; then
    # Rows without a source MD5 (the Geuvadis RNA-seq BAMs): verify every BGZF
    # block's CRC, which samtools quickcheck (header and EOF only) does not.
    gzip -t -- "${target}"
  fi
}

download_one "${input_url}" "${input_path}" "${source_input_md5}"
download_one "${index_url}" "${index_path}" "${source_index_md5}"
if [[ ${input_format} == FASTQ ]]; then
  printf 'FASTQ input: no alignment header\n' > "${SAMPLE_ROOT}/input_header.sam"
  sha256sum "${input_path}" "${index_path}" > "${SAMPLE_ROOT}/source_fastq_sha256.txt"
  if [[ -n ${subsample_pairs} ]]; then
    if [[ ! ${subsample_pairs} =~ ^[1-9][0-9]*$ || ! ${subsample_seed} =~ ^[0-9]+$ ]]; then
      echo "Invalid subsampling parameters: ${subsample_pairs} ${subsample_seed}" >&2
      exit 3
    fi
    module load seqtk/1.4
    if ! command -v seqtk >/dev/null; then
      echo "seqtk/1.4 is not available on this node; nothing subsampled" >&2
      exit 3
    fi
    # The same seed on both mates keeps the pairs together (seqtk sample -s).
    for mate in 1 2; do
      source_fastq=${INPUT_ROOT}/${sample_id}_${mate}.fastq.gz
      seqtk sample -s"${subsample_seed}" "${source_fastq}" "${subsample_pairs}" \
        | gzip > "${INPUT_ROOT}/${sample_id}_${mate}.sub.fastq.gz"
      gzip -t -- "${INPUT_ROOT}/${sample_id}_${mate}.sub.fastq.gz"
      rm -f -- "${source_fastq}"
    done
    input_path=${INPUT_ROOT}/${sample_id}_1.sub.fastq.gz
    index_path=${INPUT_ROOT}/${sample_id}_2.sub.fastq.gz
    printf 'seqtk sample -s%s <mate> %s\n' "${subsample_seed}" "${subsample_pairs}" \
      > "${SAMPLE_ROOT}/subsampling.txt"
  fi
  detected_build=none
else
samtools quickcheck -v "${input_path}"
samtools view -H "${input_path}" > "${SAMPLE_ROOT}/input_header.sam"

detected_build=$(python3 - "${SAMPLE_ROOT}/input_header.sam" <<'PY'
import re, sys
lengths = {}
for line in open(sys.argv[1], encoding='utf-8'):
    if not line.startswith('@SQ\t'):
        continue
    fields = dict(field.split(':', 1) for field in line.rstrip().split('\t')[1:] if ':' in field)
    if fields.get('SN') in {'1', 'chr1'}:
        lengths[fields['SN']] = fields.get('LN')
if '248956422' in lengths.values():
    print('GRCh38')
elif '249250621' in lengths.values():
    print('GRCh37')
else:
    print('unknown')
PY
)
fi
case "${expected_build}:${detected_build}" in
  GRCh38DH:GRCh38|GRCh38:GRCh38|GRCh37:GRCh37|none:none) ;;
  *) echo "Assembly mismatch: expected ${expected_build}, detected ${detected_build}" >&2; exit 4 ;;
esac

samplesheet=${SAMPLE_ROOT}/${sample_id}.${modality}.samplesheet.csv
if [[ ${input_format} == FASTQ ]]; then
  printf 'sample_id,fastq_1,fastq_2\n%s,%s,%s\n' "${sample_id}" "${input_path}" "${index_path}" \
    > "${samplesheet}"
else
  printf 'sample_id,%s\n%s,%s\n' "${sheet_column}" "${sample_id}" "${input_path}" > "${samplesheet}"
fi
{
  nextflow -version
  samtools --version
  apptainer --version
  module list
} > "${SAMPLE_ROOT}/environment.txt" 2>&1

sha256sum "${MANIFEST}" "${input_path}" "${index_path}" "${samplesheet}" \
  "${SAMPLE_ROOT}/input_header.sam" > "${SAMPLE_ROOT}/input_sha256.txt"
find /scratch/project_2008084/hla_references/singularity_cache/containers -maxdepth 1 \
  -type f -name '*.sif' -print0 | sort -z | xargs -0 sha256sum \
  > "${SAMPLE_ROOT}/container_sha256.txt"
git -C /projappl/project_2008084/SpecHLAx rev-parse HEAD \
  > "${SAMPLE_ROOT}/spechla_git_commit.txt" 2>/dev/null \
  || printf 'not_a_git_checkout\n' > "${SAMPLE_ROOT}/spechla_git_commit.txt"
sha256sum "${PIPELINE}/main.nf" "${PIPELINE}/nextflow.config" \
  "${PIPELINE}/conf/roihu_params.yaml" > "${SAMPLE_ROOT}/workflow_files_sha256.txt"

{
  printf 'sample_id\tmodality\tbatch_id\tinput_url\tindex_url\tsource_input_md5\t'
  printf 'source_index_md5\tsource_record\texpected_build\tdetected_build\n'
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "${sample_id}" "${modality}" "${batch_id}" "${input_url}" "${index_url}" \
    "${source_input_md5}" "${source_index_md5}" "${source_record}" \
    "${expected_build}" "${detected_build}"
} > "${SAMPLE_ROOT}/input_provenance.tsv"

if [[ ${input_format} == FASTQ && ${modality} == wes ]]; then
  sequence_args=(--input_type fastq --seq_type dna --run_modality wes \
    --reference_build hg38 --spechla_exon_only 1)
elif [[ ${input_format} == FASTQ ]]; then
  sequence_args=(--input_type fastq --seq_type rna --run_modality rnaseq \
    --reference_build hg19 --optitype_seq_type rna)
elif [[ ${modality} == wes ]]; then
  sequence_args=(--input_type cram --seq_type dna --run_modality wes \
    --reference_build hg38 --spechla_exon_only 1)
else
  sequence_args=(--input_type bam --seq_type rna --run_modality rnaseq \
    --reference_build hg19 --optitype_seq_type rna)
fi
command=(nextflow run "${PIPELINE}/main.nf" -resume -ansi-log false
  -name "champhla_dev_${modality}_${sample_id}_${SLURM_JOB_ID}"
  -w "${WORK_DIR}"
  -params-file "${PIPELINE}/conf/roihu_params.yaml"
  --input_samplesheet "${samplesheet}"
  --outdir "${RESULTS}"
  --slurm_account project_2008084
  --use_local_spechla true
  --spechla_path /projappl/project_2008084/SpecHLAx
  --singularity_cache_dir /scratch/project_2008084/hla_references/singularity_cache/containers
  --require_full_panel true
  --release_commit "${RELEASE_COMMIT}"
  "${sequence_args[@]}"
  -profile roihu,singularity,paper)
printf '%q ' "${command[@]}" > "${SAMPLE_ROOT}/nextflow_command.sh"
printf '\n' >> "${SAMPLE_ROOT}/nextflow_command.sh"

launch_root=${SAMPLE_ROOT}/nxf_launch
mkdir -p "${launch_root}"
cd "${launch_root}"
set +e
"${command[@]}" > "${SAMPLE_ROOT}/nextflow.stdout.log" 2> "${SAMPLE_ROOT}/nextflow.stderr.log"
nextflow_exit=$?
set -e
printf '%s\n' "${nextflow_exit}" > "${SAMPLE_ROOT}/nextflow.exit"
if [[ ${nextflow_exit} -ne 0 ]]; then
  echo "Nextflow failed for ${sample_id} ${modality}: exit ${nextflow_exit}" >&2
  exit "${nextflow_exit}"
fi

trace=${RESULTS}/pipeline_info/execution_trace.txt
panel=${RESULTS}/pipeline_info/panel_provenance.json
if [[ ! -s ${trace} || ! -s ${panel} ]]; then
  echo "Required pipeline provenance is missing" >&2
  exit 5
fi

if [[ ${modality} == wes ]]; then
  callers=(hlahd optitype polysolver spechla t1k)
else
  callers=(arcashla hlahd optitype t1k)
fi
status_file=${SAMPLE_ROOT}/caller_dispositions.tsv
printf 'caller\toutput_file_count\ttrace_statuses\tdisposition\n' > "${status_file}"
for caller in "${callers[@]}"; do
  output_dir=${RESULTS}/${sample_id}/${caller}
  output_count=0
  if [[ -d ${output_dir} ]]; then
    output_count=$(find "${output_dir}" -type f -size +0c | wc -l)
  fi
  trace_statuses=$(awk -F '\t' -v caller="${caller}" -v sample="${sample_id}" '
    NR == 1 {for (i=1;i<=NF;i++) {if ($i=="name") n=i; if ($i=="status") s=i; if ($i=="exit") e=i}; next}
    tolower($n) ~ caller && $n ~ sample {print $s ":exit=" $e}
  ' "${trace}" | sort -u | paste -sd, -)
  if [[ ${output_count} -gt 0 ]]; then
    disposition=outputs_present
  elif [[ ${input_format} == FASTQ && ${caller} == polysolver && -z ${trace_statuses} ]]; then
    # The pinned release skips BAM-only callers for FASTQ input (and logs the skip);
    # the NCI-60 decision makes that a declared non-call at every locus.
    disposition=declared_non_call_fastq_input
  elif [[ -n ${trace_statuses} ]]; then
    disposition=explicit_non_call_or_failed_task
  else
    disposition=missing_without_trace
  fi
  printf '%s\t%s\t%s\t%s\n' "${caller}" "${output_count}" \
    "${trace_statuses:-not_observed}" "${disposition}" >> "${status_file}"
done

t1k_reports=0
if [[ -d ${RESULTS}/${sample_id}/t1k ]]; then
  t1k_reports=$(find "${RESULTS}/${sample_id}/t1k" -type f -name '*.parser.json' | wc -l)
fi
t1k_outputs=$(awk -F '\t' '$1=="t1k" {print $2}' "${status_file}")
if [[ ${t1k_outputs} -gt 0 && ${t1k_reports} -ne 1 ]]; then
  echo "T1K produced output but exactly one parser audit was not preserved" >&2
  exit 6
fi
if [[ ${REQUIRE_T1K_SUCCESS} == 1 ]]; then
  if [[ ${t1k_outputs} -eq 0 || ${t1k_reports} -ne 1 ]]; then
    echo "T1K smoke acceptance requires caller output and exactly one parser audit" >&2
    exit 9
  fi
  python3 - "${RESULTS}/${sample_id}/t1k" <<'PY'
import json, pathlib, sys
reports = list(pathlib.Path(sys.argv[1]).rglob('*.parser.json'))
if len(reports) != 1:
    raise SystemExit('expected exactly one T1K parser report')
report = json.loads(reports[0].read_text(encoding='utf-8'))
if report.get('status') != 'valid' or report.get('counts', {}).get('invalid') != 0:
    raise SystemExit('T1K parser report is not valid')
if report.get('schema_counts', {}).get('current_9', 0) <= 0:
    raise SystemExit('T1K smoke did not exercise the current nine-column schema')
PY
elif [[ ${REQUIRE_T1K_SUCCESS} != 0 ]]; then
  echo "REQUIRE_T1K_SUCCESS must be 0 or 1" >&2
  exit 9
fi
if grep -q $'\tmissing_without_trace$' "${status_file}"; then
  echo "At least one panel caller is absent without a trace disposition" >&2
  exit 7
fi

# Storage taint: a run during which the quota filled is not evidence, whatever the
# callers' exit codes say.
stop_watcher
if storage_tainted; then
  echo "Project quota was exhausted during this run; results are not marked complete" >&2
  record_taint
  exit 11
fi

find "${RESULTS}" -type f -print0 | sort -z | xargs -0 sha256sum \
  > "${SAMPLE_ROOT}/result_files_sha256.txt"
sha256sum "${status_file}" "${SAMPLE_ROOT}/result_files_sha256.txt" \
  > "${SAMPLE_ROOT}/completion_sha256.txt"
touch "${SAMPLE_ROOT}/SAMPLE_COMPLETE"

if [[ ${PRUNE_ON_SUCCESS} == 1 ]]; then
  test -f "${SAMPLE_ROOT}/SAMPLE_COMPLETE"
  rm -rf -- "${WORK_DIR}"
  rm -f -- "${input_path}" "${index_path}"
  printf 'work and downloaded public input pruned after checksummed completion\n' \
    > "${SAMPLE_ROOT}/PRUNED_AFTER_COMPLETION"
elif [[ ${PRUNE_ON_SUCCESS} != 0 ]]; then
  echo "PRUNE_ON_SUCCESS must be 0 or 1" >&2
  exit 8
fi
