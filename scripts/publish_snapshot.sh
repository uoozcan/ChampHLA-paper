#!/bin/bash
# Build the scanned GitHub snapshot of this repository and, with --push, publish it to
# github.com/uoozcan/ChampHLA-paper. This is the only route from this repository to GitHub.
#
#   scripts/publish_snapshot.sh            # build and scan only; prints the snapshot commit
#   scripts/publish_snapshot.sh --push     # also push public-snapshot to public/main
#
# Why a snapshot: the development history (commits 482cabf and e7986f1, 2026-09-29) held
# FIMM per-sample genotype tables, so no history branch may ever reach GitHub. Each
# snapshot is one commit holding the tree of the current HEAD minus the held-back paths;
# its parent is the previous snapshot, never a development commit. The pre-push hook
# refuses anything else.
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"
PUSH=0
[[ ${1:-} == --push ]] && PUSH=1

if [[ -n $(git status --porcelain --untracked-files=no) ]]; then
  echo "commit or stash tracked changes first; the snapshot is built from HEAD" >&2
  exit 2
fi
SRC=$(git rev-parse HEAD)

# FIMM/VenEx-only paths, held back until the cohort governance fields are confirmed
# (AUTHOR_FIELDS_TO_COMPLETE.md). Mixed files such as result_registry.tsv and the
# manuscript sources keep the aggregate values the paper reports.
HOLD_BACK=(
  artifacts/fimm
  artifacts/fimm_consensus
  artifacts/venex
  'figures/supplementary_figure_s6_fimm_concordance.*'
  'figures/supplementary_figure_s7_fimm_bb72.*'
  'figures/supplementary_figure_s8_venex_diagnostics.*'
  # Quotes the VenEx pseudonym exposed in the 2026-10-08 incident.
  reports/pre_submission_review_20261008.tsv
)

IDX=$(mktemp)
trap 'rm -f "${IDX}"' EXIT
GIT_INDEX_FILE=${IDX} git read-tree HEAD
GIT_INDEX_FILE=${IDX} git rm -r -q --cached --ignore-unmatch -- "${HOLD_BACK[@]}"
TREE=$(GIT_INDEX_FILE=${IDX} git write-tree)

# Fail closed on anything that looks like controlled data. The synthetic FIMM test
# fixtures (FIMM-001, REAL-001, ...) are the only allowed matches.
ALLOW=(':!tests/fixtures/fimm' ':!tests/test_fimm.py' ':!scripts/publish_snapshot.sh')
fail=0
bad_paths=$(git ls-tree -r --name-only "${TREE}" \
  | grep -iE '(^|/)fimm_results/|\.xlsx?$|(^|/)runtime_data/|crosswalk|pseudo_id' \
  | grep -vE '^tests/fixtures/fimm/' || true)
if [[ -n ${bad_paths} ]]; then
  echo "BLOCKED: forbidden paths in snapshot tree:" >&2
  echo "${bad_paths}" >&2
  fail=1
fi
for pattern in 'FIMM-[A-Za-z]{0,6}[_-]?[0-9]{2,}' 'VX_[0-9]+_[0-9]+' '\bFHRB[0-9]' \
               '\bFH[0-9]{4,}' 'specimen_id.donor_id'; do
  hits=$(git grep -I -l -E "${pattern}" "${TREE}" -- . "${ALLOW[@]}" || true)
  if [[ -n ${hits} ]]; then
    echo "BLOCKED: pattern '${pattern}' found in:" >&2
    echo "${hits}" | sed "s/^${TREE}://" >&2
    fail=1
  fi
done
if (( fail )); then
  exit 3
fi

PREV=$(git rev-parse -q --verify refs/heads/public-snapshot || true)
if [[ -n ${PREV} && $(git rev-parse "${PREV}^{tree}") == "${TREE}" ]]; then
  echo "snapshot unchanged: ${PREV}"
  COMMIT=${PREV}
else
  MSG=$(printf 'ChampHLA paper snapshot of %s\n\nSource commit: %s\nHeld back: %s\n' \
    "${SRC:0:7}" "${SRC}" "${HOLD_BACK[*]}")
  if [[ -n ${PREV} ]]; then
    COMMIT=$(git commit-tree "${TREE}" -p "${PREV}" -m "${MSG}")
  else
    COMMIT=$(git commit-tree "${TREE}" -m "${MSG}")
  fi
  git update-ref refs/heads/public-snapshot "${COMMIT}" ${PREV:+"${PREV}"}
  echo "snapshot ${COMMIT} built from ${SRC}"
fi

if (( PUSH )); then
  git push public refs/heads/public-snapshot:refs/heads/main
fi
