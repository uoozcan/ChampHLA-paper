# Current Roihu single-sample workflow smoke provenance

This directory preserves evidence from two successful HG00096 workflow smoke
runs performed on Roihu in September 2026:

- a DNA caller route using a WGS-derived mate-aware HLA BAM; and
- an RNA-seq caller route using paired-end FASTQ.

The files are operational provenance only. They are not historical
development-cohort resource measurements, WES runtime evidence, monetary cost
estimates, cohort scaling estimates, or accuracy results. The RNA workflow
source checkout was dirty because `modules/seq2hla.nf` differed from its Git
commit; the archived module and its hash therefore define the executed source.

`raw/SHA256SUMS` was generated on Roihu before transfer. The generator verifies
every transferred file against that manifest and writes
`artifacts/compute_smoke_benchmark.tsv` plus its manifest. Both Nextflow and
Slurm measurements are retained because they measure resources differently.
