#!/bin/bash
#SBATCH --job-name=champhla_ctl
#SBATCH --account=project_2008084
#SBATCH --partition=small
#SBATCH --time=24:00:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --output=/scratch/project_2008084/champhla_publication_remediation/development/logs/%x_%j.out
#SBATCH --error=/scratch/project_2008084/champhla_publication_remediation/development/logs/%x_%j.err

# Storage-gated controller for the v3.5.0 development rerun. Usage:
#   sbatch roihu_development_controller.sbatch [extra control arguments]
# Each pass of `manage_development_batches.py control` re-derives every sample's
# state from artifacts, ledgers and Slurm, so this job holds no state of its own
# and can be cancelled and resubmitted at any time. It stops (and never retries)
# when a failed sample needs an author's failure class (exit 3), when the quota
# headroom cannot be read or too many jobs hit the storage gate (exit 4), when
# another controller is already running (exit 5), on any unexpected error, or
# when the roster is done (exit 10). Before its time limit it hands over to a
# successor queued with afterany on this job, so two controllers never overlap.
set -eo pipefail

ROOT=${CHAMPHLA_RUN_ROOT:-/scratch/project_2008084/champhla_publication_remediation}
PAPER=${CHAMPHLA_PAPER:-${ROOT}/paper}
PIPELINE=${CHAMPHLA_PIPELINE:-${ROOT}/releases/PanelHLA-3.5.0}
# Another roster runs in its own directory with its own manager options, for example
#   CHAMPHLA_RUN_DIR=${ROOT}/extension CHAMPHLA_MANAGER_ARGS='--manifest <tsv> --job-name
#   champhla_ext --amendment <signed amendment>', set in the environment of the submission.
RUN_ROOT=${CHAMPHLA_RUN_DIR:-${ROOT}/development}
read -r -a MANAGER_ARGS <<< "${CHAMPHLA_MANAGER_ARGS:-}"
POLL_SECONDS=${CHAMPHLA_POLL_SECONDS:-600}
HANDOVER_SECONDS=${CHAMPHLA_HANDOVER_SECONDS:-79200}
SELF=${PAPER}/scripts/roihu_development_controller.sbatch
STATUS=${RUN_ROOT}/CONTROLLER_STOPPED
CHAIN=${RUN_ROOT}/controller_chain.tsv

# shellcheck disable=SC1090
source "${PIPELINE}/bin/roihu_env.sh"
set -u
mkdir -p "${RUN_ROOT}/logs"

stop() {
  printf '%s\tjob=%s\texit=%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    "${SLURM_JOB_ID:-none}" "$1" "$2" > "${STATUS}"
  echo "Controller stopped: $2" >&2
}

others=$(squeue -h -u "${USER}" -n champhla_ctl -t RUNNING -o '%i' | grep -vx "${SLURM_JOB_ID:-none}" || true)
if [[ -n ${others} ]]; then
  stop 5 "another controller is already running: ${others//$'\n'/ }"
  exit 5
fi
rm -f -- "${STATUS}"

while true; do
  printf '== pass %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  set +e
  python3 "${PAPER}/scripts/manage_development_batches.py" --run-root "${RUN_ROOT}" \
    ${MANAGER_ARGS[@]+"${MANAGER_ARGS[@]}"} control --execute "$@"
  pass_exit=$?
  set -e
  case ${pass_exit} in
    0) reason="" ;;
    3) reason="a failed sample needs an author failure class (see controller_status.tsv)" ;;
    4) reason="scratch headroom unreadable or repeated storage-gate deferrals; nothing was submitted" ;;
    10) reason="every roster entry is complete or terminally classified" ;;
    *) reason="unexpected controller error (exit ${pass_exit})" ;;
  esac
  if [[ ${pass_exit} -ne 0 ]]; then
    stop "${pass_exit}" "${reason}"
    [[ ${pass_exit} -eq 10 ]] && exit 0
    exit "${pass_exit}"
  fi
  if [[ ${SECONDS} -ge ${HANDOVER_SECONDS} ]]; then
    if ! successor=$(sbatch --parsable --dependency="afterany:${SLURM_JOB_ID}" "${SELF}" "$@"); then
      stop 6 "could not queue a successor controller; resubmit this script by hand"
      exit 6
    fi
    printf '%s\t%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "${SLURM_JOB_ID}" "${successor}" \
      >> "${CHAIN}"
    echo "Handed over to controller ${successor}"
    exit 0
  fi
  sleep "${POLL_SECONDS}"
done
