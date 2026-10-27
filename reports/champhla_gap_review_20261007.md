# ChampHLA gap review: what the earlier drafts had that the master does not

**Date:** 2026-10-07  
**Master:** `manuscripts/benchmark/manuscript.md` + `supplementary.md`, branch `champhla-name-restore`  
**Earlier drafts compared:**
- `Downloads/ChampHLA_Manuscript_Draft_V1 (17).docx` (supervisor document, Sep 7)
- `Downloads/ChatGPT_Bioinformatics_ChampHLA_Manuscript_V5x_reviewfix.docx` (working line, Aug 27; = `manuscripts/source_original/`)
- `.../ChampHLA_algorithms_suppfigs_20260825/deliverables/..._algorithms_suppfigs_20260825.docx` (adds the algorithm schematics)

**Starting classification:** `reports/champhla_to_panelhla_transfer_matrix_20260930.md`.
That ledger worked from a PDF-to-Markdown conversion of Draft V1 and marked about 20 figures
and tables "caption-to-image mapping is unstable; no direct transfer". Those items were **never
assessed on content**. They are assessed here from the clean `.docx` captions.

**Not yet compared:** the current Drive copy of `ChampHLA_manuscript_draft_v1`, in case it was
edited after Sep 7 (awaiting download), and anything that exists only on Roihu (access blocked
on the CSC side since 2026-10-06).

## Restore categories

| Code | Meaning |
|---|---|
| **Text** | Can return as prose, a schematic or a descriptive table without new results. Wording must stay inside the current evidence (no clinical-utility, external-validation or WGS-accuracy claims). |
| **Supp** | Can return in the supplement as method description or exploratory material. |
| **Recompute** | Can return after recomputing statistics from stored caller tables on the current 153 WES / 120 RNA-seq loci. No caller is re-run. Each number needs a registry row first. |
| **Blocked** | Possible in principle, but the needed source files are only on Roihu (or must be confirmed there). |
| **No** | Cannot return as evidence: invalid WGS inputs, RNA results computed before 2026-08-31 (wrong-locus reads), the 390/321 ambiguous-truth denominators, or a non-independent "truth". |
| **Present** | Already in the master in current form. |

## A. Introduction, methods and discussion text

| # | Earlier item | Master now | Code | What it takes / why |
|---|---|---|---|---|
| A1 | Introduction: clinical motivation (AML, transplantation, neoantigen work, HLA-linked drug hypersensitivity), class-I biology, caller landscape. Draft V1 ≈1,360 words | Introduction 738 words | **Text** | Restore the condensed material in Umut's wording; keep the current aim paragraph. |
| A2 | §2.1 ChampHLA pipeline architecture (BAM/CRAM/FASTQ routing, per-modality modules, harmonisation, outputs) + Figure 1 workflow schematic | One sentence ("run with the ChampHLA Nextflow workflow") | **Text** | Describe the software that produced the calls; redraw Figure 1 as a schematic without numbers. Keep the existing statement that this repository verifies steps from the stored tables onward. |
| A3 | Algorithm schematics: Figure 2 "Majority voting baseline", Figure 3 "Champion–Challenger routed consensus", and S4.2 formal pseudocode | Prose only | **Text / Supp** | Figure 2 redrawn as the main-text schematic of ChampHLA-Consensus (plurality, alphabetical tie-break). Figure 3 and the pseudocode go to S7 as comparator definitions. |
| A4 | §2.2 full Champion–Challenger description (≈650 words) and §2.3 weight/guardrail definition | S7 "limited definitions" | **Supp** | Expand S7 with the full method text, as a comparator, not the method. |
| A5 | Conclusion (≈320 words) and S1 Recommendations | Conclusions 145 words, no recommendations | **Text** | Rewrite recommendations on current findings (assay-matched panel; plurality matches the best caller without knowing which; report ambiguity). |
| A6 | S2 Limitations / future directions, S6 "ChampHLA v2 roadmap" | Limitations section present | **Present / Text** | The roadmap can return as a short future-work paragraph. |
| A7 | Software usage: HPC guide, local guide, scenario walkthroughs, output schema (V5x S3, S7–S9, ≈1,000 words) | Excluded as "software documentation" | **Supp** | Reasonable for a software paper. Commands and schema must first be checked against the current pipeline release (`uoozcan/panelhla`). |
| A8 | Acknowledgements, funding, data availability | Present (provisional) | **Present** | No change. |

## B. Extra analyses

| # | Earlier item | Master now | Code | What it takes / why |
|---|---|---|---|---|
| B1 | Discordance taxonomy (§2.5, §3.3, Table 3/4, Fig S5, Fig S14) | Absent (call states and error dependence cover related ground) | **Recompute** | Tags exist locally: `D:\RoihuWork\pihla-publish\analysis\1000g_realdata\benchmark_{wes,rna}_truthbacked\run\tables\discordance_tags.tsv`. Restrict to the retained loci; drop WGS. |
| B2 | Confidence calibration and benchmark-derived weights (§2.3, §3.4, Fig 7, Fig S2) | Absent | **Recompute (exploratory)** | Originally fitted on old denominators including WGS. Brier/ECE can be recomputed for WES and RNA-seq on current loci; reported as exploratory, not as part of the method. |
| B3 | Cross-modality robustness, bimodal WES+RNA (§3.6, Fig 8) | Absent | **Recompute** | 51 subjects are in both current sets. The trimodal part is **No** (WGS). |
| B4 | Per-gene caller accuracy (Fig S1) and per-locus complexity covariates (Fig 6) | 68-word subgroup paragraph | **Recompute** | A WES/RNA-seq per-gene figure from existing tables. |
| B5 | Two- vs three-field resolution (Fig S3, Fig S17) | Ambiguity-compatible and G-group analyses present | **Present / No** | The 2014 truth is two-field, so a three-field 1000G endpoint is not possible. |
| B6 | Computational performance (§2.8, §3.1, Fig 4: RAM and runtime per caller) | S10 single-sample test runs only | **Blocked** | The local `results/pipeline_info/execution_trace.txt` is empty (header only). Needs the original Nextflow traces from Roihu. |
| B7 | MV-floor routing diagnostics, CC-vs-vote, sweep surface, selective reporting, warning layer, novelty screen (§3.9, Tables 7–11, Figs 10–11, S6, S12, S19–S22) | S7 definitions only | **No** (as results) | Driven by WGS. On WES and RNA-seq, CC ties the plurality vote, so there is no result to show. |
| B8 | RNA read-evidence layer (§2.13, Table S4, Fig S18) | Absent | **No** | Evaluated on a truth-selected, error-enriched subset. |
| B9 | Voter independence and family gates (§2.12, Table S3, Fig S11) | Current Figure 4 (caller-error dependence) | **Present / No** | Fig S11 is superseded by Figure 4. Table S3 gates are fitted policies. |

## C. Validation arms

| # | Earlier item | Master now | Code | What it takes / why |
|---|---|---|---|---|
| C1 | NCI-60 (Fig S13) | S9.6 exploratory application | **Present** | |
| C2 | GIAB Ashkenazi trio (3 subjects) and IHWG reference cells (4 subjects) | Excluded | **Blocked** | Truth tables are local (`giab_trio_benchmark/`, `ihwg_benchmark/`); caller outputs are on Roihu only. Very small n, so descriptive only, re-scored with the plurality rule. |
| C3 | GeT-RM reference panel | Never run | **No** | Excellent three-field truth for 108 lines, but only 2 have usable short reads (`getrm_benchmark/PHASE0_STATUS.md`, 2026-06-28). |
| C4 | HPRC pangenome Locityper/Immuannot "silver truth" (§2.9, §3.10, Fig 12, Table S2) | Excluded | **No** as validation | Not independent biological truth. It could at most be "agreement with an orthogonal method", and only if call-level provenance is recovered from Roihu. |
| C5 | FIMM HLA-A2 flow cytometry (BB7.2) | S9.4 corrected analysis | **Present** | |
| C6 | FIMM cross-modality concordance | S9.3 identity-linked analysis | **Present** | The fingerprint-paired version was withdrawn as circular. |
| C7 | FIMM LOH, allele dropout, HED and survival (Figs S8–S10) | Excluded | **No** | Non-informative imbalance input; underpowered post hoc clinical endpoints. |

## D. Figures and tables, old number to fate

| Old | Content | Fate |
|---|---|---|
| Fig 1 | Workflow and governance | A2 |
| Fig 2, Fig 3 | Plurality and CC schematics | A3 |
| Fig 4 | Compute resources | B6 |
| Fig 5 | Accuracy across methods | Replaced by current Figures 2 and 3 |
| Fig 6 | Per-locus accuracy and covariates | B4 |
| Fig 7 | Calibration | B2 |
| Fig 8 | Cross-modality robustness | B3 |
| Fig 9 | External arms | C2 |
| Figs 10–11 | Routing diagnostics | B7 |
| Fig 12 | Pangenome | C4 |
| Table 1 | Callers, modalities, evidence types, versions | **D1 (new): Text.** A main-text caller table without the old accuracy column |
| Table 2 | Cohort design | Present (S1) |
| Table 3 | Discordance | B1 |
| Table 4 | Strict WGS | No |
| Table 5 | External arms | C2 |
| Table 6 | FIMM flow | C5 |
| Tables 7–11 | Routing, buckets, selective reporting, RNA sensitivity | B7 / B8 |
| S1 | Per-gene caller accuracy | B4 |
| S2 | Calibration heatmap | B2 |
| S3, S17 | Resolution | B5 |
| S4 | Abstention trade-off | Present (current S2) |
| S5, S14 | Discordance | B1 |
| S6, S12, S19–S22 | CC and routing | B7 |
| S7 | Legacy FIMM concordance | C6 |
| S8–S10 | Dropout, LOH, survival | C7 |
| S11 | Algorithm-family agreement | Present (current Figure 4) |
| S13 | NCI-60 | C1 |
| S15 | FIMM BB7.2 | C5 |
| S16 | Base reliability | Present (Table 1 / S6) |
| S18 | RNA selective accuracy | B8 |

## Summary

| Code | Items |
|---|---|
| Text / Supp (no new results) | A1, A2, A3, A4, A5, A6, A7, D1 |
| Recompute (stored tables, no caller re-run) | B1, B2, B3, B4 |
| Blocked on Roihu | B6, C2 |
| No | B7, B8, C3, C4, C7, plus all WGS accuracy |
| Already present | A8, B5, B9, C1, C5, C6 |

## Decisions (to be filled in by Umut)

| # | Restore? | Notes |
|---|---|---|
| A1 | Yes (Umut, 2026-10-07) | Done, commit 1dc6600 |
| A2 | Yes (Umut, 2026-10-07) | Done, commit 95d7113 |
| A3 | Yes (Umut, 2026-10-07) | Done, commit 95d7113, 9f280f9 |
| A4 | Yes (Umut, 2026-10-07) | Done, commit 9f280f9 |
| A5 | Yes (Umut, 2026-10-07) | Done, commit a6487dc |
| A6 | Yes (Umut, 2026-10-07) | Done, commit a6487dc |
| A7 | Yes (Umut, 2026-10-07) | Done, commit 9f280f9 |
| D1 | Yes (Umut, 2026-10-07) | Done, commit 95d7113 |
| B1 | Yes (Umut, 2026-10-07) | Done, commit 4130229 |
| B2 | Yes (Umut, 2026-10-07) | Done, commit 4130229 |
| B3 | Yes (Umut, 2026-10-07) | Done, commit 4130229 |
| B4 | Yes (Umut, 2026-10-07) | Done, commit 4130229 |
| B6 | | when Roihu is back |
| C2 | | when Roihu is back |
