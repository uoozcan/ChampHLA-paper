# Cover letter

**To:** Editorial Board, *Scientific Reports*  
**Re:** “Benchmarking consensus HLA class I genotyping from exome and RNA sequencing with ChampHLA”

Dear Editors,

Please consider our manuscript, “Benchmarking consensus HLA class I genotyping from exome and RNA sequencing with ChampHLA,” for publication as an Article in *Scientific Reports*.

Short-read HLA genotyping tools can disagree across assays and genes, yet the apparent performance of a consensus depends strongly on how failed calls, single-allele outputs and ambiguous reference typing are scored. We evaluate ChampHLA-Consensus, an equal-weight plurality rule without fitted parameters, on public 1000 Genomes whole-exome and Geuvadis RNA-sequencing data. The evaluation counts failed calls in the denominator, scores ambiguous reference typing separately and traces reported results to caller outputs and analysis artifacts.

In the retrospective development benchmark, the plurality rule could not be distinguished from the strongest single caller in either assay, and fitted policies did not improve on it. A published re-typing supports the plurality call at most apparent consensus errors, although that interpretation is explicitly post hoc and not independent of the exome data. We therefore present ChampHLA-Consensus as an auditable development baseline, not as evidence of equivalence, external validation or clinical performance.

We believe the work fits *Scientific Reports* because it emphasizes technical validity, reproducibility and transparent evaluation of a widely relevant genomics problem. The accompanying repositories contain analysis code, result records, tests, provenance and a reusable Nextflow workflow. The post-normalization analysis is reproducible from public inputs; final release identifiers and archival DOIs remain to be inserted after the authors approve release.

**AUTHOR INPUT REQUIRED BEFORE SUBMISSION:** confirm the corresponding author's affiliation, postal address and email; confirm that all authors approve submission and the author order; insert the final repository release identifiers and DOIs; resolve the ethics/governance fields for the retained exploratory FIMM and VenEx analyses; and confirm funding and competing interests.

**AUTHOR INPUT REQUIRED:** confirm that the manuscript is not under consideration elsewhere, that all authors approve submission and accept accountability, and that the proposed language-model disclosure in the author checklist is complete and correctly placed. These declarations must be confirmed before this draft is sent.

Suggested reviewers: **AUTHOR INPUT REQUIRED**  
Reviewers to exclude: **AUTHOR INPUT REQUIRED, or state “none”**  
Prior discussion with a *Scientific Reports* Editorial Board Member: **AUTHOR INPUT REQUIRED, or state “none”**

Sincerely,

**AUTHOR INPUT REQUIRED**  
Corresponding author on behalf of all authors
