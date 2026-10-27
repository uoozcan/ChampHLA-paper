# ChampHLA v3.5.0 development-rerun progress

**Date:** 22 October 2026  
**Evidence class:** truth-free operational quality control only  
**Manuscript use:** prohibited

## Aggregate state

| Assay | Signed roster | Checksum-valid | Incomplete or invalid |
|---|---:|---:|---:|
| WES | 130 | 130 | 0 |
| RNA-seq | 106 | 58 | 48 |
| **Total** | **236** | **188** | **48** |

Since the 21 October record, 22 additional RNA-seq sample runs have become
checksum-valid. This is an operational completion count, not a scientific result.
No caller output, reference typing, joined truth, performance estimate, ranking or
subject-level result was inspected.

At the observation, one `champhla_ctl`, one `champhla_dev` and one
`champhla_prefetch` job remained. The controller normal-finish marker was absent.
The signed full-roster gate therefore remains closed.

## Source-provenance checks

| Object | Local canonical SHA-256 | Remote SHA-256 | Status |
|---|---|---|---|
| `scripts/manage_development_batches.py` | `cd5e6ac676a1b1937e051de3f22d6162cfaf7ddb457cfccb4719b0e8d0aec7e9` | `cd5e6ac676a1b1937e051de3f22d6162cfaf7ddb457cfccb4719b0e8d0aec7e9` | Match |
| `cohorts/development_rerun_manifest.tsv` | `506405a006a2cabc80f8584fa21368d868d56a6164ccd60e017d36173bcbfd85` | `506405a006a2cabc80f8584fa21368d868d56a6164ccd60e017d36173bcbfd85` | Match |
| `scripts/collect_development_rerun.py` | `e6f34c1894c22d2843f51af66ad36c2e0434da1fe19014ccf702ba740648493a` | `3f9b97abba3f9ec3258f4d0449a0579aa88e4e0e50f53167aeb765646cf676e9` | Mismatch; remote collector prohibited |

The complete result tree must eventually be exported without staged alignment inputs,
workflow work directories or sealed resources. Collection must then use the current
local canonical collector, not the stale remote copy.

## Consequence for the manuscript package

The manuscript, `result_registry.tsv`, performance tables and figures remain frozen.
WES-only or 188/236 interim analysis is prohibited. Evaluation may begin only after:

- `checked=236`, `complete_valid=236`, `incomplete_or_invalid=0`;
- no controller, development or prefetch job remains;
- the controller records a normal finish; and
- `validate_development_rerun_gate.py` emits `PASS`.

Until then, the correct update is this external operational memo only.
