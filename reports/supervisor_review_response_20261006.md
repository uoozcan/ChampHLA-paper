# Response to review comments — PanelHLA combined document

Reviewer: Ziaurrehman Tanoli. Comments dated 2026-10-05 on the Google Drive copy
(`AML_project/PanelHLA_Manuscript_v1x.docx`). Response prepared 2026-10-06.

All 17 comments are addressed below. Every change was made in the markdown
source (`manuscripts/benchmark/manuscript.md`), which is what the DOCX is
generated from, so the rebuilt document carries them all.

**Please note:** the Drive copy you commented on was generated from an earlier
build and then edited in Google Docs. Those Google Docs edits have been merged
back into the source, so nothing you or anyone else typed there has been lost.
The Drive copy also predates the NCI-60 exploratory section, which appears in
the rebuilt document.

---

## Comment-by-comment

| # | Comment | Response |
|---|---|---|
| 0 | "Rewrite it in better way, it reads a bit confusing." (Abstract, nested-CV and φ sentences) | Rewritten in plain language. It now says directly that selecting the single best caller did **not** improve on the plurality vote, and explains that φ measures correlation between caller errors, which is what bounds the benefit of voting. All values unchanged. |
| 1 | "I suggest to not mention it in the abstract, you can mention it in conclusion sections." | Moved. The sentence "PanelHLA is an auditable research benchmark … not a novel inference algorithm, clinical typing system or external validation" now opens the final paragraph of **Conclusions** and is gone from the Abstract. |
| 2 | "?" (disease-association research) | Expanded: "disease-association research — in which HLA alleles are tested for statistical association with susceptibility to autoimmune and infectious disease". |
| 3 | "Put the references at the end of tool's subsentence" | Done. Each caller now carries its own citation: OptiType (Szolek 2014), HLA-HD (Kawaguchi 2017), arcasHLA (Orenbuch 2019), POLYSOLVER (Shukla 2015), T1K (Song 2023), SpecHLA (Wang 2023). |
| 4 | "describe, how!" (graph-based caller class) | Described: they align reads to a graph in which known alleles are alternative paths, rather than to one linear reference, so reads from strongly divergent alleles can still be placed correctly. |
| 5 | "?" (result tables) | Disambiguated to "the result tables produced by that earlier analysis", and said what the defect was — a single allele was selected from an ambiguous typing string instead of the ambiguity being treated as unresolved. |
| 6 | "confusing." (cannot be re-executed from this repository) | Rewritten: the caller outputs were produced by an earlier run and kept as files; that workflow is not part of this repository, so the benchmark starts from the stored outputs rather than from raw reads. |
| 7 | "what is version-2?" | Defined on first use: a second, separately pre-registered protocol that locks a subject-disjoint public-data extension before any truth labels are joined, so its evaluation is prospective with respect to the rule reported here. **Please confirm this description matches your intent.** |
| 8 | "Always define the abbreviations before their first use." | IGSR expanded to International Genome Sample Resource. A full first-use audit was run over both documents and five further abbreviations were expanded: nested-CV, CR1, TSV, AML, MDS, HED. |
| 9 | "what is SHA-256?" | Glossed in place: "a cryptographic digest of the file contents, which changes if any byte of the file changes". The checksum value itself is kept — removing it would weaken the auditability the paper argues for. |
| 10 | "what is subject here?" | A definition paragraph was added before first substantive use: a *subject* is one individual in the public 1000 Genomes and Geuvadis collections, and a *locus* is one subject–gene pair within one assay. |
| 11 | "patient samples?" | No — and the text now says so explicitly: these are consented population-genomics donors, not patients, and no clinical samples are involved. |
| 12 | "??" (no comparative claim is made about them) | Explained: no outputs from those callers survive in the recovered data, so they could not be scored, and no claim is made about them in either direction. |
| 13 | "what is this?" (diploid concordance) | Defined: a locus counts as concordant only when both predicted alleles match both reference alleles to the first two fields, in either order, with no credit for matching one allele of the pair. |
| 14 | "rewrite in better way. External readers do not know what is CSC bio-apps." | Rewritten for an external reader: "caller containers taken from the curated bioinformatics software collection of the national computing centre used for this work (CSC — IT Center for Science, Finland; collection `bio-apps`, release v202603)". **Please confirm CSC may be named here and in Acknowledgements.** |
| 15 | "??" (Prediction generation rejects truth-bearing columns) | Explained as an enforced code behaviour: the step that produces caller predictions refuses to run if any input table carries a reference-genotype column, so truth cannot reach a prediction. This is the truth firewall. |
| 16 | "For google doc place all figures and tables directly in text after the paragraphs" | Done for the main text: each of Figures 1–4 now sits immediately after the paragraph that first cites it, and the separate "Figure legends" section is gone from the Drive version. Tables already appeared in place. See the note below about the supplement. |

---

## Three points that need your decision

1. **The supplement was deliberately left with collected figure legends.**
   Only Supplementary Figures S5–S7 are cited from inside the supplement;
   S1–S4 are cited from the main text. Inlining the supplement therefore moved
   S5–S7 up and stranded S1–S4 after them, so the supplementary figures no
   longer read in numeric order. Say the word and I will inline them too.

2. **Figure legends remain collected in the manuscript source.** Most journals
   require legends in their own section at submission, so the inlining is a
   property of the shareable Drive rendering, not of the manuscript we would
   submit. Both come from the same source file.

3. **One wording change from the Drive copy was not adopted.** The Drive copy
   read "The current PanelHLA-Consensus version is developed using Python
   3.11.15 …". That has been kept as "release environment", because those
   pinned versions describe the stack in which the reported results were
   regenerated, not the machine development happens on. The sentence now says
   so explicitly.

## Still outstanding, and not resolvable from the repository

Unchanged by this round, and listed in `AUTHOR_FIELDS_TO_COMPLETE.md`: author
ORCIDs, corresponding-author addresses, CRediT roles, the ethics determination
for the public-data analysis, funding and competing-interest confirmations, the
release tag and archival DOI, and the FIMM cohort governance identifiers.
