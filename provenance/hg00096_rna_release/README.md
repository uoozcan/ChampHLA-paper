# HG00096 RNA-seq BAM run of workflow release 3.4.0

HG00096 is a development subject; no extension subject was touched. The run used
the input format the confirmatory extension stages for RNA-seq: the Geuvadis
GRCh37 BAM `HG00096.1.M_111124_6.bam` (E-GEUV-1 processed data; SHA-256
`61c411cfbcb93aacdc19f3fa70afab1cd4ce02dbffac38c07a4545b00bfd3fdc`, MD5
`df6fd5c6732197d7a9f6247c883be0bb`, computed in the job because the source lists
no checksum). Release 3.4.0 (tag `v3.4.0`, commit `2a72a4b`, archive SHA-256
`e206179f3e36d05025178376a795401a812202c022aeb565f49d4d42f50c9b0a`),
`-profile roihu,singularity,paper`, `--seq_type rna --run_modality rnaseq`, CSC
Roihu Slurm job 2129989 (24 min wall, 7.6 CPU-hours). The September 2026 RNA
re-run in `provenance/hg00096_rerun` used paired FASTQ instead.

Files are stored byte-exact (`.gitattributes`: `-text`). `scripts/compare_hg00096_rerun.py`
scores the calls against the stored development calls with the paper's normalizer.
