# Cover letter

**To:** Editorial Board, *Scientific Reports*  
**Re:** “ChampHLA: a fail-closed benchmark of plurality voting across short-read HLA class I callers”

Dear Editors,

Please consider our manuscript, “ChampHLA: a fail-closed benchmark of plurality voting across short-read HLA class I callers,” for publication as an Article in *Scientific Reports*.

Short-read HLA genotyping tools can disagree across assays and genes, yet the apparent performance of a consensus depends strongly on how failed calls, single-allele outputs and ambiguous reference typing are scored. We evaluate ChampHLA-Consensus, an equal-weight plurality rule without fitted parameters, on public 1000 Genomes whole-exome and Geuvadis RNA-sequencing data. The study contributes a fail-closed, artifact-traceable benchmark in which no-calls remain in the denominator, reference ambiguity is kept visible and every result can be traced to the underlying caller outputs and registered analysis artifacts.

On the historical development data, the plurality rule could not be distinguished from the strongest single caller in either assay, and fitted policies did not improve on it. A published re-typing supports the plurality call at most apparent consensus errors, although that interpretation is explicitly post hoc and not independent of the exome data. We therefore present ChampHLA-Consensus as an auditable development baseline, not as evidence of equivalence, external validation or clinical performance.

We believe the work fits *Scientific Reports* because it emphasizes technical validity, reproducibility and transparent evaluation of a widely relevant genomics problem. The manuscript includes the analysis code, result registry, tests, provenance records and reusable Nextflow workflow needed to inspect and reproduce the post-normalization analysis boundary.

**AUTHOR INPUT REQUIRED BEFORE SUBMISSION:** confirm the corresponding author's affiliation, postal address and email; confirm that all authors approve submission and the author order; insert the final repository release identifiers and DOIs; resolve the ethics/governance fields for the retained exploratory FIMM and VenEx analyses; and confirm funding and competing interests.

The manuscript is not under consideration elsewhere, and all authors will confirm accountability for the work before submission. Large-language-model assistance used in code review and manuscript editing is disclosed in the Methods; the authors take responsibility for every claim and reported result.

Suggested reviewers: **AUTHOR INPUT REQUIRED**  
Reviewers to exclude: **AUTHOR INPUT REQUIRED, or state “none”**  
Prior discussion with a *Scientific Reports* Editorial Board Member: **AUTHOR INPUT REQUIRED, or state “none”**

Sincerely,

**AUTHOR INPUT REQUIRED**  
Corresponding author on behalf of all authors
