# arcasHLA in the v3.5.0 development rerun: deployment diagnosis

Date: 2026-10-25. Scope: the 106 RNA-seq samples of the v3.5.0 development rerun.

This diagnosis is **truth-free**. It uses only the rerun's own task logs, its result files
and the historical stored caller calls. No reference typing, and no score derived from one,
was read to produce it. The reference-scored arcasHLA results appear only through
`result_registry.tsv` (for example `DEV_CORRECTED_RNASEQ_CALLER_ARCASHLA`). They were not
used to choose, change or rerun anything described here.

## Why it was examined

The cell-by-cell comparison of stored and rerun calls (Supplementary Table S10.2, generated
from `provenance/development_rerun_v350/truth_free_collection/stored_vs_rerun_cells.tsv`)
showed an unusual change rate for arcasHLA:

- arcasHLA changed at 176 of 318 RNA-seq caller–gene cells;
- HLA-HD changed at 7, OptiType at 0 and T1K at 6.

Discovery path, recorded honestly: the diagnosis began after the author had reviewed the
first registry delta, in which arcasHLA's reference-scored result had fallen, and chose
"accept, and diagnose arcasHLA". The evidence below is truth-free. Nothing in the analysis
or the workflow was changed in response to it.

## Findings

1. **Single-end extraction of paired-end libraries.** `modules/arcashla.nf` at tag `v3.5.0`
   (line 41) calls `arcasHLA extract` without `--paired`.
   - The Geuvadis libraries are paired-end, but all 106 extract logs report
     `Read type: single-end`.
   - `kallisto pseudo` then runs with `--single` and fragment-length parameters estimated
     from single reads, for example `-l 74.84 -s 1.78` for HG00097.
   - arcasHLA therefore genotyped every sample without pair information.
2. **Release and reference.** The container (`arcashla.sif`, SHA-256 `60c42737…6c05c`)
   holds arcasHLA 0.2.0, built from master `47469f58` with IPD-IMGT/HLA 3.40.0.
   - The release is read from the container, because the task's `versions.yml` does not
     report it (decisions/20261025_rerun_arcashla_release_from_container.json).
   - 0.2.0 reports homozygotes as one allele, so the signed singleton policy applies.
3. **Runtime patch.** Before genotyping, the module copies the container's `align.py` and
   replaces `counts[eq]` with `counts.get(eq, 0)`, to avoid a `KeyError`.
   - The patched code therefore differs from the released 0.2.0 code.
   - This is recorded here; it was not assessed separately.
4. **Rare-allele designations.** Among the 636 allele calls, counted the same way in each:

   | Calls | Second field ≥100 | Distinct alleles |
   |---|---:|---:|
   | Rerun arcasHLA | 177 (27.8%) | 166 |
   | Stored arcasHLA | 11 (1.7%) | 99 |
   | Rerun OptiType | 0 | 88 |
   | Rerun HLA-HD | 1 | 95 |

   The pattern is consistent with genotyping from under-informative single reads. It is
   not a property of the RNA-seq inputs, because the other callers on the same inputs
   did not change.

## What this does and does not support

- The rerun's arcasHLA results describe **this deployment** (single-end extraction,
  arcasHLA 0.2.0 and the runtime patch), not arcasHLA as a method.
- The manuscript reports them as produced (Limitations; Supplementary S10), with no change
  to the module.
- Fixing the module (`--paired`) and rerunning arcasHLA would be a new workflow release and
  a protocol change. It needs a signed amendment before any run, and the result would be
  reported as a sensitivity analysis rather than as a replacement chosen after seeing
  scores.
- That decision belongs to the author and is open.

## Sources

- Roihu task logs, read-only:
  `/scratch/project_2008084/champhla_publication_remediation/development/samples/rnaseq/<sample>/results/<sample>/arcashla/<sample>/{<sample>.extract.log,<sample>.genotype.log}`.
  Summary scripts: `arcas_diag1.sh` and `arcas_diag2.sh`. The local outputs are kept off the
  repository because they contain sample identifiers.
- Pipeline repository `uoozcan/PanelHLA`, tag `v3.5.0`, file `modules/arcashla.nf`.
