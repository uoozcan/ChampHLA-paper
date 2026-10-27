# Confirmatory extension: dry run of the analysis chain (2026-10-09)

**Purpose.** Show, before the pre-registration is signed, that the extension driver
(`scripts/run_extension.py`) is the development method. The driver was run end to end on
the **development** subjects, which are not the extension roster, and had to reproduce
the development results.

## What ran

| Stage | Input / setting |
|---|---|
| `prepare` | Raw caller strings in the workflow's `aggregated_calls.tsv` format: the parity fixture exported to the workflow repository (`tests/fixtures/paper_parity/caller_calls.tsv`, SHA-256 `2ef071e7…`). Roster: the 236 development subject-assays. Normalization with IPD-IMGT/HLA 3.65.0 membership and the native-declaration singleton rule. |
| `predict` | The development gate's own `build_development_predictions`; identity check; freeze of predictions and code. |
| `unblind` | Dry-run mode, which needs a non-frozen roster and a scratch work directory, so the readiness gate is not consulted. The truth is built with the extension's cohort label and joined once, then evaluated with the locked protocol's inference: 100,000 bootstrap iterations, bootstrap seed 20260925, sign-flip seed 20260926. |

Work directory: `D:/panelhla_work/extension_dry_run/run` (scratch; not part of the repository).

## Result: identical to the development results

| Assay | Method | Development | Dry run |
|---|---|---|---|
| WES | ChampHLA-Consensus | 143/153 | 143/153 |
| WES | POLYSOLVER / OptiType / SpecHLA / HLA-HD / T1K | 143 / 140 / 123 / 126 / 113 | identical |
| WES | strict majority / two-thirds | 140 / 136 | identical |
| RNA-seq | ChampHLA-Consensus | 113/118 | 113/118 |
| RNA-seq | HLA-HD / arcasHLA / OptiType / T1K | 110 / 109 / 109 / 91 | identical |
| RNA-seq | strict majority / two-thirds | 111 / 111 | identical |

Every caller and every simple rule matches in both assays.

## What this establishes

- The extension analysis is the development method, executed by the same functions.
- IPD-IMGT/HLA 3.65.0 release-membership validation, which the locked protocol requires
  for the extension and which the development set did not apply, changes no
  development result.
- Missing caller outputs are explicit `no_caller_output` rows in the extension (18 such
  caller-loci here, 3,222 rows against the development table's 3,204), and they stay in
  the fixed denominator as before.

## Code changes made to get here

- `evaluate(..., signflip_seed=...)` lets the extension use the protocol's separate
  sign-flip seed. When unset, behaviour is unchanged.
- `prepare_development_truth(..., cohort=...)` labels the truth rows with the
  extension's cohort. Its default is unchanged. The dry run found that a hard-coded
  label made the truth join fail on every locus.
