## What changed since the 12 October version (v3)

This page is not part of the manuscript. It summarises the changes between
`ChampHLA_Manuscript_v3.docx` (12 October) and this version, which was generated on
26 October 2026 from the manuscript sources. Old values are taken from v3. New values come
from the current manuscript and its results registry.

### The evidence changed: every development caller was re-run

- **What was re-run:** the 236-run development roster (130 WES and 106 RNA-seq subjects),
  with the pinned ChampHLA workflow release 3.5.0, on the CSC Roihu cluster in October 2026.
- **What it replaced:** the stored outputs of the unarchived April–May run. They are kept
  only as a labelled cell-by-cell comparison (Supplementary S10) and for the restored
  analyses (S12).
- **What each run records:** its release commit, scheduler job, container digests and
  checksummed inputs and results.
- **The rerun's results were approved by the author before the prose was revised.** The
  approval is recorded in `decisions/20261025_rerun_registry_delta_approved_corrected.json`.

### Headline results

- **The vote is unchanged:** WES 143/153 (93.5%) and RNA-seq 113/118 (95.8%).
- **The strongest single callers changed:**
  - WES: OptiType, at 142/153. In v3 it was POLYSOLVER, tied with the vote; POLYSOLVER now
    scores 138/153.
  - RNA-seq: HLA-HD and OptiType tied at 112/118. In v3 it was HLA-HD at 110/118.
- **Margin over the best single caller:** the vote is now one locus above it in each assay.
  The differences are not significant, so neither equivalence nor superiority is claimed.
- **No fitted policy beats the vote.** The refitted nested-CV best-caller policy reached
  142/153 in WES and 111/118 in RNA-seq.

### New problems found, and reported as they are

- **arcasHLA.** The release 3.5.0 module reads the paired-end Geuvadis RNA-seq libraries as
  single-end, and its container holds arcasHLA 0.2.0. Its rerun concordance is 58/118. The
  defect is described in the Limitations. The author chose to report it as is, with no
  amended rerun (`decisions/20261025_arcashla_report_as_is.json`).
- **Why the WES calls changed.** A new truth-free Supplementary Table S10.3 characterises
  the changed caller calls:
  - OptiType changed least.
  - Most changes replace one allele of a pair.
  - The changed T1K call states follow the release 3.5.0 parser rules.

### Material brought back from earlier versions

All drafts were compared; the comparison is in `reports/manuscript_salvage_ledger_20261026.md`.
- **Supplementary S9 is complete again**, with every number taken from the existing
  registry:
  - FIMM import rules, valid-caller composition, specimen and donor cross-assay agreement,
    and within-panel dissent;
  - BB7.2 serogroup agreement, always with its 16-of-53 donor linkage;
  - VenEx WES diagnostics;
  - Supplementary Figures S6–S8.
- **NCI-60** is disclosed again as a legacy analysis (S9.6), without numbers. Its estimates
  will return only after it is re-run on release 3.5.0 under the current rules.
- **New Supplementary S13 "Background and design rationale"**, rewritten from earlier
  drafts:
  - class I/II biology and 8/8 or 10/10 transplant matching;
  - why callers disagree;
  - caller choice as a selection problem;
  - why harmonisation and database vintage matter;
  - why "no significant difference" is not equivalence;
  - workflow reproducibility and the outlook.
- **Not brought back:** trimodal analyses, WGS accuracy, superiority claims, silver truth,
  and FIMM LOH, HED or survival.

### Corrections

- **Methods** now state that the release 3.5.0 rerun supplies the primary inputs; the
  earlier text still described the April–May stored outputs.
- **Software section** now names release 3.5.0 instead of 3.4.1.
- **First-use explanations** were added for SHA-256 and the CSC software modules.

### What comes next

- The frozen confirmatory extension (89 WES and 99 RNA-seq unseen subjects) will run once
  the signed, amended pre-registration has been deposited on Zenodo.
- The final version will then carry the title "ChampHLA: a fail-closed, pre-registered
  benchmark of plurality voting across short-read HLA class I callers" and a numeric
  abstract.
