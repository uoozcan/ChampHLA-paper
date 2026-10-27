# ChampHLA v6 gate stop — 26 October 2026

## Status

The sentence pass and author-approved S5 correction are saved. The focused manuscript suite passed: 85 tests. The full gate completed scientific regeneration but stopped at the test stage: **6 failed, 536 passed, 3 skipped**. Lint and final readiness generation were not reached. The previous readiness file is stale and is not evidence for v6.

Registry SHA-256 remains `6fd741d6e4427ef84268cd6b114df098ac982370262ba448e0bd185ca0be9f2a`. Both result-tag multisets and all generated manuscript blocks still match the v5 baseline. No test, analysis code, registry row or scientific artifact was manually edited. The gate regenerated artifacts in place.

At the initial stop, no v6 file was uploaded and no v6 manuscript commit was made. The existing combined document in the repository is still the pre-v6 file; only a v6 preview was built in scratch.

## Required stop

`CODEX_V6_SENTENCE_EDIT_PROMPT.md`, Step 3: “Any other failure: stop and report.” Hard rule 5 also requires test-pinned sentences to be kept rather than changing tests. The broader wording pins below were missed in the initial focused-test review.

## Proposed repair for author approval

Restore these six sentences verbatim from v5. Leave the tests untouched and put the attempted editorial revisions in the ledger as proposals. Main text would remain below its v5 length: **4,226 → 4008 words**. Rebuild the review drafts, run the focused suite plus these three test modules, then rerun the full gate. The author approved this repair; all six restorations are now applied. Verification rerun and final delivery are pending.

### 1. M53.1 — manuscripts/benchmark/manuscript.md:53

Failed assertion: `tests/test_reference_facts.py::test_stated_allele_count_matches_the_pinned_release`.

Restore: The genes are extraordinarily diverse: release 3.65.0 of the IPD-IMGT/HLA database (Immuno Polymorphism Database–ImMunoGeneTics HLA) [8], used here, contains 45,421 HLA allele designations in the pinned allele list (46,652 entries when MICA, MICB, TAP1, TAP2 and HFE are included).

Attempted editorial revision (preserve as a ledger proposal): The genes are highly diverse. The pinned allele list from IPD-IMGT/HLA release 3.65.0 (Immuno Polymorphism Database–ImMunoGeneTics HLA) [8] contains 45,421 HLA allele designations (46,652 entries including MICA, MICB, TAP1, TAP2 and HFE).

### 2. M65.1 — manuscripts/benchmark/manuscript.md:65

Failed assertion: `tests/test_reference_facts.py::test_sr016_factual_corrections_and_primary_citations_are_present`.

Restore: Benchmarks show that caller rankings depend on the assay, the gene and the dataset [23] and reveal typing-tool-specific errors [24], so the best caller for a new dataset cannot be known in advance.

Attempted editorial revision (preserve as a ledger proposal): Benchmarks show that caller rankings depend on assay, gene and dataset [23] and reveal caller-specific errors [24]. The best caller for a new dataset therefore cannot be known in advance.

### 3. M370.1 — manuscripts/benchmark/manuscript.md:370

Failed assertion: `tests/test_sr023_consistency.py::test_identity_counts_distinguish_pre_and_post_withholding`.

Restore: The signed rerun roster contained 130 WES subjects (390 subject–gene loci) and 106 RNA-seq subjects (318 loci), 105 of whom also occurred in the WES roster; capture kit, read length, sequencing depth and original preprocessing metadata were not available.

Attempted editorial revision (preserve as a ledger proposal): The signed rerun roster contained 130 WES subjects (390 subject–gene loci) and 106 RNA-seq subjects (318 loci), 105 also in the WES roster. Capture kit, read length, sequencing depth and original preprocessing metadata were unavailable.

### 4. M750.1 — manuscripts/benchmark/manuscript.md:750

Failed assertion: `tests/test_figures_publication_ready.py::test_adjusted_interval_significance_is_coherent_with_holm`.

Restore: Significance follows the governing sign-flip test, not the bars: in RNA-seq the strict-majority and two-thirds consensus bars exclude zero, but their sign-flip Holm-adjusted *p* values are not below 0.05, so they are grey (Supplementary S3).

Attempted editorial revision (preserve as a ledger proposal): The sign-flip test governs significance. RNA-seq strict-majority and two-thirds consensus intervals exclude zero, but their sign-flip Holm-adjusted *p* values are not below 0.05; both are grey (Supplementary S3).

### 5. S1883.1 — manuscripts/benchmark/supplementary.md:1883

Failed assertion: `tests/test_sr023_consistency.py::test_s12_uses_exact_intervals_and_explains_calibration_denominator`.

Restore: The table reports scored loci over callable loci; six of 115 callable HLA-HD RNA-seq loci lacked a preserved calibrated probability and were excluded from calibration scoring.

Attempted editorial revision (preserve as a ledger proposal): The table reports scored over callable loci. Six of 115 callable HLA-HD RNA-seq loci lacked preserved calibrated probabilities and were excluded from calibration scoring.

### 6. S1145.1 — manuscripts/benchmark/supplementary.md:1145

Failed assertion: `tests/test_sr023_consistency.py::test_fimm_locus_row_units_are_explicit`.

Restore: Of 2,642 source rows, 2,610 were imported, and 7,179 caller-level locus rows (one per specimen, assay, caller and gene) remained after replicate collapse.

Attempted editorial revision (preserve as a ledger proposal): Of 2,642 source rows, 2,610 were imported. After replicate collapse, 7,179 caller-level locus rows remained, one per specimen, assay, caller and gene.

## Remaining delivery work

Shorten the changes preface: the preview currently spans two pages. Build the final combined v6 after the passing gate; inspect the preface and all pages, verify inline figures and stripped markup, upload a new stored DOCX, verify its remote MD5 and make the one authorized local manuscript commit. The six pre-existing scientific wording questions in the sentence ledger remain for the author.

Scratch evidence: `D:/panelhla_work/v6_sentence_edit_20261026/` contains the downloaded v5, exact paragraph/table comparison, original source snapshots, edit-preservation audit, focused-test and gate logs, the repair proposal and rendered previews.

## Repair verified

The author-approved six-sentence restoration passed the expanded focused suite (145 tests) and the full gate (542 passed, 3 skipped; scientific failures=0; expected author_input_required). The registry and tags are unchanged. This report is retained as an unstaged working record; the committed sentence ledger contains the repair and final verification history.
