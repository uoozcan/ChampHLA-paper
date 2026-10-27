# ChampHLA Scientific Reports rewrite change log

**Date:** 19 October 2026  
**Worktree:** `champhla_scirep_rewrite_wt`  
**Branch:** `scientific-reports-rewrite`  
**Canonical source HEAD:** `2b9929ad3776a85ba6efe3477e6effd6cfb0f808`  
**Status:** editorially complete submission candidate; not ready for submission

## Scope and provenance

This rewrite was made in a new isolated worktree from the current canonical HEAD. The canonical working copy and the existing `manuscript-rewrite` worktree were not edited. No commit, merge, push, external upload, new analysis, result recomputation, truth join, sealed-holdout inspection or patient-level FIMM/VenEx inspection was performed.

The canonical manuscript and `result_registry.tsv` controlled scientific state and numerical claims. The earlier rewritten manuscript, RW-001–RW-032 review and change log were used only as editorial and narrative resources. The repository copy of the v3 manuscript was used for document-level reconciliation. Where sources differed scientifically, the current canonical repository prevailed.

## Manuscript changes

- Replaced the BMC-formatted title with the 13-word provisional title, “ChampHLA: a fail-closed benchmark of plurality voting across short-read HLA class I callers”.
- Replaced the structured abstract with a 179-word unstructured abstract without citations, headings or performance estimates.
- Limited keywords to six.
- Reordered the paper as Introduction, Results, Discussion and Methods.
- Removed the internal “Headline results / changes since v2” memo from the submission manuscript.
- Rebuilt the Introduction around the biological problem, caller disagreement, prior consensus approaches, the evaluation gap and the study question.
- Reordered Results to follow the scientific argument: endpoint retention; vote-versus-caller inference and detectability; ambiguity scoring; apparent shared errors and oracle headroom; corrected-reference adjudication; operational call states and ties; cross-assay consistency; exploratory FIMM/VenEx agreement.
- Opened the Discussion with interpretation, consolidated repeated cautions and grouped limitations by study design, reference typing, sample representation, caller/deployment provenance, statistical power and cohort governance.
- Folded the standalone Conclusions into the closing Discussion paragraph.
- Kept Introduction + Results + Discussion at 4,398 words after excluding tables and provenance-only result tags, within the journal's recommended 4,500-word main-text limit.
- Retained six main display items: four figures and two editable tables.
- Moved ethics and consent wording into Methods and retained conspicuous author-only stop conditions.
- Split Data availability and Code availability.
- Replaced BMC-only headings and labels, including Background, Declarations, Conclusions, Additional files, Consent for publication and Availability of data and materials.
- Kept the AI-assistance disclosure and author responsibility statement.
- Preserved Oxford English and rewrote prose for a natural scientific voice without concealing AI assistance.
- Kept FIMM and VenEx explicitly exploratory; no accuracy, clinical-utility or external-validation claim was introduced.
- Reordered numbered references by first citation after the section and narrative changes. Supplementary citations were updated to the same numbering; the Abi-Rached paper is now reference 31.

## Integrity-preserving changes

- Preserved all 111 original `[RESULT:…]` tags across the manuscript and Supplementary Information.
- Preserved the generated main-text block and all 30 generated supplementary blocks.
- Introduced no new registered result and changed no registry value, estimate, denominator, interval, test result or analysis artifact.
- Retained the interpretation of the Abi-Rached asterisks and kept the corrected-reference analysis explicitly post hoc and non-independent.
- Retained the frozen-primary outcome, prior-truth-exposure disclosure, call-state accounting, tie handling and detectability limits.
- Kept the abstract free of numerical performance claims while `abstract_numeric_performance_allowed=false`.

## Supplementary Information

- Updated reference numbers and availability-section terminology to match the main manuscript.
- Retained detailed protocol archaeology, diagnostic reruns, run identifiers and hashes, extended call-state results and the protocol-change history in the Supplementary Information.
- Retained 35 editable tables and five supplementary figures, ordered S1–S5 in the Word rendering.

## Reusable prompt and editorial package

- Added `SCIENTIFIC_REPORTS_MANUSCRIPT_REWRITE_PROMPT.md`, including source precedence, journal constraints, scientific and statistical safeguards, HLA-specific checks, privacy boundaries, author/ethics stop conditions, staged rewriting and verification, rerun handling, required deliverables and acceptance criteria.
- Added the Scientific Reports review memo, cover-letter draft, author-input register and submission checklist.
- The review memo reconciles RW-001–RW-032 and records the venue-specific findings SRP-001–SRP-010.
- The cover letter uses placeholders for corresponding-author details, suggested reviewers and exclusions; no identity or opinion was invented.

## Document-build changes

- Rebuilt the tracked manuscript and supplementary review DOCX files from their Markdown sources so repository parity checks remain valid.
- Built the package manuscript with four figures, two editable tables, Word heading styles, a contents field and page numbering.
- Built the package Supplementary Information with five figures, 35 editable tables, Word heading styles, a contents field and page numbering.
- Built a separate cover-letter DOCX with visible author-input placeholders.
- Stripped internal `[RESULT:…]` tags from Word output while retaining them in the controlled Markdown sources.
- Added a visible “SUBMISSION CANDIDATE — DO NOT SUBMIT” notice to the manuscript and supplementary DOCX files.

Package DOCX SHA-256 values:

| File | SHA-256 |
|---|---|
| `ChampHLA_Scientific_Reports_Manuscript.docx` | `f6877ccd12929d7900ad9737d219ca6e2918636cdc1eeb500be7d4f238e18216` |
| `ChampHLA_Scientific_Reports_Supplementary.docx` | `6500e65c8847527bce89e5bd918cc4e4a948596f34629d4d93b20543b305aa6b` |
| `ChampHLA_Scientific_Reports_Cover_Letter.docx` | `69b0e82612a0dc35b2819f12f9b82c5ed2d851b01882035d5fa410f782981385` |

## Test and tooling maintenance

The following non-scientific maintenance was required to run the repository in its declared Python 3.8 environment:

- replaced `Path.is_relative_to()` with a `relative_to()`/`ValueError` compatibility branch;
- replaced Python 3.10-only runtime type expressions in one test with `typing.Optional`/`typing.List`;
- replaced `str.removeprefix()` in one test with an equivalent prefix check;
- replaced the unsupported `Path.write_text(..., newline=...)` test helper with `Path.open(..., newline=...)`.

Wording and document tests were updated only where the protected fact was unchanged:

- the table-rendering test now accepts the Results-first Scientific Reports order of the two main tables;
- the contents anchor changed from Background to Introduction, with a supplementary S1 anchor for a separate supplement;
- the Abi-Rached citation test identifies the reference by author rather than the obsolete number 34;
- the frozen-primary test normalises whitespace while preserving the exact conclusion that it did not outperform the vote.

## Verification record

| Check | Outcome |
|---|---|
| Scientific Reports rewrite guard | PASS: 111 result tags, one main generated block and 30 supplementary generated blocks preserved |
| Main manuscript claim audit | PASS with author-input allowance; only declared author/ethics placeholders prevent submission readiness |
| Supplementary claim audit | PASS with author-input allowance; retained FIMM governance field remains blocking |
| Venue tests | PASS: title, abstract, keywords, section order, word limit, display count, availability sections and reference order |
| Focused manuscript/document tests | 72 passed |
| Full repository suite | 475 passed, 3 skipped |
| Tracked review-DOCX parity | PASS for text and figure order |
| Package Word inspection | PASS for heading hierarchy, contents placement, figure order, editable table counts, page fields, italic statistical symbols and absence of leaked result tags |

## Unresolved submission blockers

The package must not be submitted until all items below are resolved by the appropriate authors or by the pending validated rerun:

1. v3.5.x rerun and any resulting registry/manuscript refresh;
2. final author names, order, affiliations, ORCIDs and corresponding-author details;
3. CRediT roles and final author approval;
4. FIMM/VenEx ethics, consent, governance and lawful-basis wording;
5. funding statement and grant identifiers;
6. competing-interests confirmation;
7. release tag, commit and archival DOI;
8. unavailable historical container identifiers or an explicit author-approved limitation statement;
9. suggested reviewers, exclusions and any prior editorial contact.

Editing cannot guarantee publication or acceptance. The completed deliverable is a rigorously rewritten and tested Scientific Reports submission candidate with all known author-only and data-dependent blockers made explicit.
