# Revision following the six PDF comments — 27 October 2026

This pass builds on the existing uncommitted v6 follow-up in the active worktree. It changes presentation and explanatory wording, without adding extension or NCI-60 results. The local review version is v7; the delivered Drive v6 and the author's copy were not changed.

## Responses to the PDF comments

| Comment | Resolution |
| --- | --- |
| 1. Title | **Benchmarking consensus HLA class I genotyping from exome and RNA sequencing with ChampHLA**. The title states the method, assay scope and benchmark purpose without implying superiority. |
| 2. Jargon, IMRAD and earlier Methods | Main text now follows Introduction, Methods, Results and Discussion. Internal status words were replaced with descriptions of the study procedures. Methods were compared with earlier benchmark drafts from Git history (`e80a38f`, `00f6e5e`, `e77a8d9`); useful explanations were adapted only where they describe the present analysis. Superseded results were not restored. |
| 3. Provisional paragraphs | Unconfirmed author metadata and declarations were removed from reader copies and preserved verbatim in `AUTHOR_FIELDS_TO_COMPLETE.md`. Required submission elements remain unresolved; no unknown declaration was inferred. |
| 4. Protocol history | The main Protocol history section was removed. Its relevant interpretation is explained in Supplementary S14; Supplementary S11 provides practical application guidance. The main Methods retain a concise explanation of the retrospective design and sensitivity analyses. |
| 5. Equations and pseudocode | Four editable Word equations describe the vote, tie resolution, callability and concordance. Algorithm 1 describes normalization, valid complete allele-pair voting, abstention and lexicographic tie resolution. These describe the implemented equal-weight plurality method. |
| 6. Figures and tables | All 13 figures and 43 tables were reviewed. Six figures received presentation changes; seven were retained. Wide tables use landscape pages, larger text and repeated headers. Adjacent Word tables remain distinct. Statistical displays and numerical table content are unchanged. |

## Figure audit

| Figure | Action and interpretation retained |
| --- | --- |
| 1 | Clarified input and reference labels; removed project-status jargon and the misleading implication of independent truth. Study-flow counts unchanged. |
| 2 | Emphasized the consensus row, wrapped the long comparator label and clarified count columns. Denominators, confidence intervals and axes unchanged. |
| 3 | Shortened policy labels and removed redundant fitted labels. Governing tests, multiplicity correction and descriptive intervals unchanged. |
| 4 | Retained the error-dependence heatmap and its interpretation limits. |
| S1 | Retained the call-state display, including the distinction between absent and unsuccessful calls. |
| S2 | Retained the trade-off display and coincident RNA-seq markers; no artificial jitter added. |
| S3 | Retained support profiles, small-group suppression and descriptive uncertainty. |
| S4 | Clarified P-compatible mapping terminology; did not recast compatibility as exact equivalence. |
| S5 | Clarified the selected default caller and eligibility conditions; zero-margin behavior remains explicit. |
| S6 | Clarified the two eligibility rules. Shared-caller and dependence limitations remain. |
| S7 | Retained the linked serogroup comparison and its denominator and uncertainty definitions. |
| S8 | Retained availability and dissent diagnostics; unavailable estimates were not invented. |
| S9 | Retained aggregate changes between stored and rerun outputs, classified without reference genotypes. |

All figure source-artifact hashes and statistical contracts match the baseline. Figures 4, S1, S2, S3, S7, S8 and S9 have byte-identical PNGs. Regenerated figure formats remain available in `figures/`.

## Scientific preservation and readability

- The multiset of 175 `[RESULT:]` citations is unchanged.
- All 43 tables retain their numerical data. Internal registry/decision identifiers omitted from reader tables remain in source metadata or the underlying artifacts.
- Result-registry SHA-256 remains `6fd741d6e4427ef84268cd6b114df098ac982370262ba448e0bd185ca0be9f2a`.
- The extension implementation, its protected resource configuration and initial rosters remain unchanged. No Slurm jobs were inspected or controlled.
- The principal result still states that the vote could not be distinguished from the strongest single caller. Retrospective, exploratory and external-validation limitations remain explicit.
- Main narrative: 4,011 words excluding Methods, tables and provenance tags; abstract: 180 words; title: 13 words. There are 57 references, renumbered by first appearance after the section reordering, and six main display items.

## Validation and deliverables

- Full scientific regeneration completed with 100,000 bootstrap iterations and 2,000 power iterations: 545 tests passed, 3 skipped; lint passed. Gate status: `author_input_required`; scientific failures: zero.
- After that run, three proofreading corrections changed a supplementary figure cross-reference, an article and a table caption. Both drafts were rebuilt, claim audits refreshed, preservation checks repeated, and the full tests/lint passed again (545 passed, 3 skipped).
- Final layout corrections kept a list introduction with its list and a table introduction with its table. Both drafts were rebuilt again; the final manuscript, rendering, figure and claim suites passed: 146 passed in 50.86s. Final source/DOCX parity and scientific-preservation checks passed.
- Presentation tests were updated for the user-requested section order, labels and separate author checklist. Numerical and inference assertions were retained. Regressions cover native equation/code parity, separate landscape tables and wrapped bullets.
- The final PDF has 79 pages and no detected text-boundary overflow. The final changed pages were visually inspected; all other page images match the previously reviewed copy exactly.
- Word SHA-256: `4b50c2907cdb380f2c212cf1efbdddf112c1d43efb53adf62434308a9f2785a4`.
- PDF SHA-256: `a8ce00c86e1b149b99a49290067353679b9ea24e5ec4048089541dd539c7d93c`.
- Evidence: `D:/panelhla_work/v7_imrad_20261027/full_gate_final.log`, `post_proof_tests.log`, `final_manuscript_tests.log`, `build_review_delivery.log`, `qa_complete/comparison.json`. The earlier preliminary run was deliberately stopped for layout corrections; the final full run completed successfully.
- Machine-readable preservation evidence: `reports/manuscript_v7_preservation_20261027.json`.


The combined Word document contains a one-page change summary, main text and supplement. All pages were visually reviewed, including native equations, algorithm indentation, 13 figures and 43 tables. The PDF is a review export; author declarations, governance and release metadata still require completion before submission.

No project commit, push, Drive upload, release or remote analysis was performed in this revision. The existing project HEAD is `77bb6f7`. Earlier uncommitted follow-up work and root prompt files were preserved.