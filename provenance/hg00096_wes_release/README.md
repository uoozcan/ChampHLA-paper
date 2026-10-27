# HG00096 whole-exome runs of workflow releases 3.3.0 and 3.4.0

HG00096 is a development subject; no extension subject was touched. Both runs used
the 1000 Genomes whole-exome CRAM
`HG00096.alt_bwamem_GRCh38DH.20150826.GBR.exome.cram` (MD5
`5f2adb4635fb23a5ea2763cd58eee4dd`, checked in each job), `-profile
roihu,singularity,paper`, `--run_modality wes`, `--spechla_exon_only 1`, on CSC
Roihu. Files are stored byte-exact (`.gitattributes`: `-text`); the aggregated
calls carry the CRLF line endings the workflow writes.

| File prefix | Workflow | Slurm job | Notes |
|---|---|---|---|
| `v3.3.0_job2121882_` | release 3.3.0, tag `v3.3.0`, commit `360a449`, archive SHA-256 `589d3f94af91940677229178458e680af0a495e2b898f318c8d95c3255089603` | 2121882 | 3 h 44 min wall |
| `v3.4.0_job2128858_` | tree `15f45cfaca83f6c1532a55ee26f6e1b0a1c267a8` (commit `200ab99`); release 3.4.0 (tag `v3.4.0`, commit `2a72a4b`) adds only version strings and the changelog | 2128858 | 16 min 48 s wall; `hla_rescue.tsv` is the new per-sample rescue record |

Release 3.3.0 read only `chr6:28-34 Mb`. These GRCh38DH alignments place many
reads from non-reference HLA alleles on `HLA-*` and `chr6_*_alt` contigs instead,
and on this CRAM the selection that 3.4.0 adds finds 7,703,805 records on those
contigs against 1,422,354 in the window. A diagnostic run (Slurm job 2128100) realigned the
window, contig and unplaced reads to primary chr6 and gave the same 15 caller-gene
calls as the 3.4.0 run. `scripts/compare_hg00096_rerun.py` scores both runs against
the stored development calls with the paper's normalizer.
