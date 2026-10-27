#!/bin/bash
# Local verification gate.
#
# Every step is fail-closed. The two audit steps previously ended in "|| true"
# under `set -e`, so a failing claim audit could not fail this script, which
# defeated the point of running it. The script also never regenerated the
# artifacts the manuscript cites, so none of them was reproducible from a
# checked-in entry point.
#
# Set BOOTSTRAP to a small value for a quick developer run; a release run must
# use the default 100000.
#
# Set ALLOW_PENDING_AUTHOR_INPUT=1 to let the run pass while the manuscript still
# carries unresolved TO CONFIRM fields. This keeps continuous integration a
# meaningful signal about code health. The submission gate must run WITHOUT it:
# an unresolved placeholder is a submission blocker.
#
# Set RELEASE=1 for the run that backs a reproducibility claim. It refuses to
# pass when regeneration was skipped, when the bootstrap is below the release
# value, or when author placeholders are being waved through -- the three ways
# this script could otherwise exit 0 having verified very little.
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "${ROOT}"
export PYTHONPATH="${ROOT}/src"

PYTHON=${PYTHON:-python3}
BOOTSTRAP=${BOOTSTRAP:-100000}
AUDIT_FLAGS=()
if [[ "${ALLOW_PENDING_AUTHOR_INPUT:-0}" == "1" ]]; then
  AUDIT_FLAGS+=(--allow-pending-author-input)
fi
JOINED=artifacts/consensus_eval_wes_rna/joined_wes_rna.tsv

# Release artifacts are written only by a full-precision run. A reduced
# bootstrap is for speed, and must not quietly replace published confidence
# intervals with wider ones, so it writes to a scratch directory instead.
RELEASE_BOOTSTRAP=100000
if [[ "${BOOTSTRAP}" == "${RELEASE_BOOTSTRAP}" ]]; then
  H2H_OUT=artifacts/head_to_head
  EVAL_OUT=artifacts/consensus_eval_wes_rna
else
  H2H_OUT=$(mktemp -d)/head_to_head
  EVAL_OUT=$(mktemp -d)/consensus_eval_wes_rna
  echo "NOTE: BOOTSTRAP=${BOOTSTRAP} is below the release value of ${RELEASE_BOOTSTRAP}."
  echo "      Regenerated outputs go to a scratch directory; the committed"
  echo "      artifacts are left untouched and are what the audits below read."
fi

echo "== test suite =="
"${PYTHON}" -m pytest -q

echo "== regenerate registry tables =="
"${PYTHON}" -m champhla_recovery.cli render-manuscript-tables \
  --registry result_registry.tsv \
  --root "${ROOT}" \
  --output manuscripts/shared/generated_results.md

# The truth-joined table carries truth_allele columns and is therefore not
# tracked (see .gitignore). Where it is absent -- a fresh clone, or CI -- the
# steps that consume it cannot run. They are skipped loudly rather than
# silently, and the audits below still run against the committed artifacts.
if [[ -f "${JOINED}" ]]; then
  echo "== regenerate consensus head-to-head (bootstrap=${BOOTSTRAP}) =="
  "${PYTHON}" scripts/consensus_head_to_head.py "${JOINED}" "${H2H_OUT}" "${BOOTSTRAP}"

  echo "== regenerate confirmation decision, WES+RNA scope =="
  "${PYTHON}" -c "from champhla_confirmation.cli import evaluate_confirmation_main as m; raise SystemExit(m())" \
    --joined "${JOINED}" \
    --output-dir "${EVAL_OUT}" \
    --allow-partial \
    --bootstrap "${BOOTSTRAP}"
else
  echo "== SKIPPED: regeneration from the truth-joined table =="
  echo "   ${JOINED} is absent, so the statistical artifacts were NOT regenerated."
  echo "   They are audited as committed. Rebuild it with join_truth_once and"
  echo "   re-run this gate before declaring a release reproducible."
  # Without this, the whole point of the gate leaks away on any machine that
  # lacks the joined table -- a fresh clone, and CI. The audits below then
  # compare the committed artifacts against themselves and the script exits 0,
  # which reads as "reproduced" when nothing was reproduced. RELEASE=1 makes
  # that state fail, so a release claim cannot be made from a run that skipped.
  if [[ "${RELEASE:-0}" == "1" ]]; then
    echo "   RELEASE=1: refusing to pass a run that regenerated nothing." >&2
    exit 3
  fi
fi

if [[ "${RELEASE:-0}" == "1" && "${BOOTSTRAP}" != "${RELEASE_BOOTSTRAP}" ]]; then
  echo "RELEASE=1 requires BOOTSTRAP=${RELEASE_BOOTSTRAP}; got ${BOOTSTRAP}." >&2
  echo "A reduced bootstrap writes to a scratch directory, so the committed" >&2
  echo "intervals would be audited rather than the ones just computed." >&2
  exit 3
fi

if [[ "${RELEASE:-0}" == "1" && "${ALLOW_PENDING_AUTHOR_INPUT:-0}" == "1" ]]; then
  echo "RELEASE=1 and ALLOW_PENDING_AUTHOR_INPUT=1 are contradictory:" >&2
  echo "unresolved placeholders are a submission blocker." >&2
  exit 3
fi

echo "== audit benchmark manuscript =="
"${PYTHON}" -m champhla_recovery.cli audit-manuscript-claims \
  --manuscript manuscripts/benchmark/manuscript.md \
  --registry result_registry.tsv \
  --claims manuscripts/claim_audit.tsv \
  --root "${ROOT}" \
  --output artifacts/benchmark_manuscript_audit.json "${AUDIT_FLAGS[@]}"

echo "== audit benchmark supplementary =="
"${PYTHON}" -m champhla_recovery.cli audit-manuscript-claims \
  --manuscript manuscripts/benchmark/supplementary.md \
  --registry result_registry.tsv \
  --claims manuscripts/claim_audit.tsv \
  --root "${ROOT}" \
  --output artifacts/benchmark_supplementary_audit.json "${AUDIT_FLAGS[@]}"

echo "== audit generated registry fragment =="
# This fragment is manuscript-facing but was never audited, so the generator was
# free to emit numbers the audit bans -- and it did.
"${PYTHON}" -m champhla_recovery.cli audit-manuscript-claims \
  --manuscript manuscripts/shared/generated_results.md \
  --registry result_registry.tsv \
  --claims manuscripts/claim_audit.tsv \
  --root "${ROOT}" \
  --output artifacts/generated_results_audit.json "${AUDIT_FLAGS[@]}"

echo "== validate the release freeze manifest =="
# The repository's central provenance claim is that artifacts/release_freeze.json
# attests a specific tree ("Freeze manifests record POSIX-relative paths and a
# content hash", manuscripts/benchmark/manuscript.md). Nothing checked it, so the
# claim was unfalsifiable by the project's own gate -- and it is currently false.
#
# This reports on every run and fails only under RELEASE=1, deliberately. A stale
# freeze is a release blocker, not a code-health problem: hard-failing every run
# would block CI and every developer run until the manifest is regenerated, which
# must happen LAST, after all other edits. RELEASE=1 is where a reproducibility
# claim is made, and that is where a stale manifest must stop the run.
#
# "unfrozen" is the check that matters most: files that would be released but are
# absent from the manifest. Note that validate_freeze in champhla_confirmation
# cannot do this job -- it reads inputs/project_files, which a release manifest
# does not carry, so it would walk zero entries and report success.
set +e
"${PYTHON}" -m champhla_recovery.cli validate-release-freeze   --project-root "${ROOT}"   --manifest artifacts/release_freeze.json
FREEZE_STATUS=$?
set -e
if [[ "${FREEZE_STATUS}" != "0" ]]; then
  echo "   The freeze manifest does not describe this tree."
  echo "   Regenerate it with freeze-release-bundle as the final release step."
  if [[ "${RELEASE:-0}" == "1" ]]; then
    echo "   RELEASE=1: refusing to pass with a freeze manifest that does not validate." >&2
    exit 4
  fi
fi

echo "== all verification steps passed =="
