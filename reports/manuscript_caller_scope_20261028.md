# Manuscript caller scope correction — 28 October 2026

HLA*LA and HISAT-genotype supplied no benchmark predictions. Their mentions were background examples and explicit exclusions, not evidence that they had been run. Those mentions and their bibliography entries were removed to keep the paper focused on the evaluated methods.

## Scope corrections

- The main text and Table 1 now describe only the evaluated callers. WES uses HLA-HD, OptiType, POLYSOLVER, SpecHLA and T1K; RNA-seq uses arcasHLA, HLA-HD, OptiType and T1K. These panels were checked against the actual normalized caller input table, using caller names only and without calculating new performance results.
- Kourami and seq2HLA were removed from the main introduction and Table 1. They remain in supplementary archived and operational diagnostic records where they were actually used, with an explicit statement that neither contributes to the WES/RNA-seq benchmark comparisons. Their recorded diagnostic measurements were preserved.
- The family-restricted exploratory policy description names only the families' evaluated members, without changing its implementation or decision record. Supplementary usage guidance no longer presents all wrapped workflow modules as benchmark comparators.
- The background mapping sentence was shortened to a general explanation of ambiguous short-read assignment. The removed graph-caller reference is no longer used to support a claim about the evaluated pipeline.
- Four unused tool references were removed; the remaining 53 entries were renumbered consistently throughout the main text and supplement. Every retained bibliographic entry is otherwise verbatim. The old-to-new citation map is in the local preservation evidence.
- Abstract and introductory wording now say evaluated callers, rather than all HLA callers.

## Verification

- All 148 focused manuscript, reference, figure and Word rendering tests passed. A rendering test that required HLA*LA in the real manuscript now tests the same escaped-name case using sample text, preserving the regression check without prescribing manuscript content.
- All 175 result citations and all generated blocks are unchanged. Numerical results are unchanged; only the two non-evaluated caller rows were removed from the descriptive main table.
- Registry SHA-256: `6fd741d6e4427ef84268cd6b114df098ac982370262ba448e0bd185ca0be9f2a`.
- Both manuscript claim audits have zero blocking failures. Author-input requirements remain as previously recorded.
- Main narrative is 3,880 words excluding Methods, tables and provenance tags; abstract is 181 words.
- Both review Word files match their Markdown sources. The combined Word copy contains 13 figures and 43 tables. Its 79-page Word PDF export has no detected boundary overflow; 50 body pages match the previously reviewed copy, and all 29 changed pages were visually inspected. HLA*LA and HISAT-genotype are absent from the reader copy.
- The full scientific regeneration gate was not repeated for this editorial correction. No scientific implementation, parser, prediction, registry, immutable record or figure data was changed.

## Deliverables and state

The edited sources and all three Word copies are under `manuscripts/benchmark/`. The combined review is also saved at `D:/panelhla_work/caller_scope_20261028/ChampHLA_manuscript_review_20261028.docx`. Preservation, citation mapping, claim audits and layout evidence are in the same local working directory.

These changes build on the existing uncommitted wording revision of 27 October; that work was preserved. This correction is local and uncommitted. No push, upload, cluster action or release-policy change was made. The vault remains for Claude to update, as the author instructed.
