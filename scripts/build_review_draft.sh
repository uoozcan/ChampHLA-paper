#!/bin/bash
# Rebuild the co-author review DOCX from the benchmark manuscript.
#
# This exists because the draft is tracked AND parity-checked:
# tests/test_submission_docx.py::test_committed_review_draft_matches_the_manuscript
# compares the committed .docx against manuscripts/benchmark/manuscript.md and fails
# on any divergence. So every prose edit to the manuscript must be followed by a
# rebuild, or the suite goes red.
#
# The notice lines below are part of the artifact, not decoration: the parity test
# also asserts that the rendering says "NOT FOR SUBMISSION" and that no [RESULT:...]
# provenance tag leaked into it. They previously existed only inside the committed
# binary, so a faithful rebuild meant reading them out of word/document.xml. They are
# recorded here instead.
#
# Keep the generation date current when the draft is recirculated.
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "${ROOT}"
export PYTHONPATH="${ROOT}/src"

PYTHON=${PYTHON:-python3}
GENERATED=${GENERATED:-$(date +%Y-%m-%d)}
MANUSCRIPT=manuscripts/benchmark/manuscript.md
OUTPUT=manuscripts/benchmark/ChampHLA_manuscript_REVIEW_DRAFT.docx
SUPPLEMENT=manuscripts/benchmark/supplementary.md
SUPPLEMENT_OUTPUT=manuscripts/benchmark/ChampHLA_supplementary_REVIEW_DRAFT.docx

"${PYTHON}" -m champhla_recovery.cli build-review-docx \
  --manuscript "${MANUSCRIPT}" \
  --output "${OUTPUT}" \
  --figures figures \
  --note "REVIEW DRAFT - NOT FOR SUBMISSION. Generated ${GENERATED} from ${MANUSCRIPT}." \
  --note "Author declarations and submission details await confirmation; see AUTHOR_FIELDS_TO_COMPLETE.md." \
  --note "Scientific results are retrospective development evidence; no external validation is claimed." \
  --note "Inline provenance citations are stripped from this rendering; they remain in the markdown source."

"${PYTHON}" -m champhla_recovery.cli build-review-docx \
  --manuscript "${SUPPLEMENT}" \
  --output "${SUPPLEMENT_OUTPUT}" \
  --figures figures \
  --title "ChampHLA supplementary material" \
  --note "REVIEW DRAFT - NOT FOR SUBMISSION. Generated ${GENERATED} from ${SUPPLEMENT}." \
  --note "Author declarations and submission details await confirmation; see AUTHOR_FIELDS_TO_COMPLETE.md." \
  --note "Scientific results are retrospective development evidence; no external validation is claimed." \
  --note "Inline provenance citations are stripped from this rendering; they remain in the markdown source."
