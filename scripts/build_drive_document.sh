#!/bin/bash
# Build the shareable combined document: the paper, then the supplement as an
# appendix, with all nine figures and all thirty-seven tables. One is the
# non-scientific CHAMPHLA-to-PanelHLA historical-material disposition table.
#
# This is NOT the tracked review draft. scripts/build_review_draft.sh builds that,
# and tests/test_submission_docx.py parity-locks it to the markdown. This output is
# a separate file at a separate path, so the two never collide.
#
# Needs the "documents" extra: python -m pip install -e ".[documents]"
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "${ROOT}"
export PYTHONPATH="${ROOT}/src"

PYTHON=${PYTHON:-python3}
GENERATED=${GENERATED:-$(date +%Y-%m-%d)}
MANUSCRIPT=manuscripts/benchmark/manuscript.md
SUPPLEMENT=manuscripts/benchmark/supplementary.md
OUTPUT=manuscripts/benchmark/ChampHLA_manuscript_COMBINED_DRIVE.docx

"${PYTHON}" -m champhla_recovery.cli build-drive-docx \
  --manuscript "${MANUSCRIPT}" \
  --supplementary "${SUPPLEMENT}" \
  --output "${OUTPUT}" \
  --figures figures \
  --title "ChampHLA manuscript" \
  --note "REVIEW DRAFT - NOT FOR SUBMISSION. Generated ${GENERATED} from ${MANUSCRIPT} and ${SUPPLEMENT}." \
  --note "Author declarations and submission details await confirmation; see AUTHOR_FIELDS_TO_COMPLETE.md." \
  --note "FIMM governance and secure source-provenance fields remain submission blockers; see COAUTHOR_REVIEW_CHECKLIST.md." \
  --note "Scientific results are retrospective development evidence; no external validation is claimed." \
  --note "Inline provenance citations are stripped from this rendering; they remain in the markdown source."
