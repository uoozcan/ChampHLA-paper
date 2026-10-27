# HG00096 re-run with the September 2026 workflow deployment

`aggregated_calls.tsv` from two single-sample runs on CSC Roihu (`/scratch/project_2008084/panelhla_e2e`), copied 2026-10-09:

- `wes_aggregated_calls.tsv` (SHA-256 `0ee94ae8…`), from job `panelhla_wes_1411113`.
  - Workflow `pihla-publish_v2/main.nf`, revision `91f035f6f0`, 2026-09-19.
  - **Input:** an HLA-region pre-extract of the exome (`HG00096.wes_hla`), not the whole exome BAM.
  - SpecHLA output is not in this table.
- `rna_aggregated_calls.tsv` (SHA-256 `0c7f0078…`), from job `panelhla_rnaseq_1411214`.
  - Workflow `pihla-publish_v3/main.nf`, revision `91f035f6f0`, 2026-09-19.
  - **Input:** the Geuvadis BAM.

HG00096 is a public 1000 Genomes / Geuvadis sample. These files contain caller calls only and no reference typing. `scripts/compare_hg00096_rerun.py` compares them with the stored development calls.
