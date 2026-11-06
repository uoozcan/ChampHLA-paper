# Manuscript run wording revision — 27 October 2026

The manuscript now presents ChampHLA directly as the workflow evaluated in this study. The abstract says: “We ran all HLA callers using the ChampHLA workflow.” The main narrative uses runs rather than reruns, removes the earlier design and naming story, and omits repeated software-release comparisons. Reference 57 uses the ChampHLA name. The exact evaluated tag and commit remain in Code availability for reproducibility; the software has not been relabelled as a different release.

Supplementary prose uses the same run terminology. The interpretation limits of archived comparisons and diagnostic runs remain explicit. Generated tables, figure data, technical identifiers, immutable records and source paths were preserved.

## Verification

- 148 manuscript, reference, figure and document tests passed. After final proofreading, 57 document and journal-format tests passed again. Both review drafts match their Markdown sources.
- The registry SHA-256 remains `6fd741d6e4427ef84268cd6b114df098ac982370262ba448e0bd185ca0be9f2a`.
- All 175 result citations, every generated block and all numerical table cells are unchanged. Claim audits have zero blocking failures. Statistical results and uncertainty statements were preserved.
- Main narrative: 3,928 words excluding Methods, tables and provenance tags; abstract: 180 words.
- All three Word copies were updated. The combined review has 13 figures and 43 tables. The 79-page Word PDF export was checked visually; unchanged pages were matched against previously reviewed pages, and every changed page was inspected. No text-boundary overflow was detected.
- The full scientific regeneration gate was not repeated for this wording-only change. Existing scientific outputs were preserved.

## Delivery and state

Updated sources: `manuscripts/benchmark/manuscript.md` and `manuscripts/benchmark/supplementary.md`. Updated Word copies are in the same directory. The combined review also exists at `D:/panelhla_work/run_wording_20261027/ChampHLA_manuscript_review_20261027.docx`.

These are local, uncommitted edits. No push, upload, job control, parser change or scientific rerun was performed. Release hold-backs and the vault were left unchanged, as instructed. The prior approved remote snapshot remains the published repository state.

Detailed preservation, claim audits and layout evidence are under `D:/panelhla_work/run_wording_20261027/`.
