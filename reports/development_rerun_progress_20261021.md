# ChampHLA v3.5.0 development-rerun progress

**Date:** 21 October 2026  
**Evidence class:** truth-free operational quality control only  
**Manuscript use:** prohibited

## Latest successfully observed aggregate state

| Assay | Signed roster | Checksum-valid | Remaining |
|---|---:|---:|---:|
| WES | 130 | 130 | 0 |
| RNA-seq | 106 | 36 | 70 |
| **Total** | **236** | **166** | **70** |

At that observation, one controller job, one development job and one RNA input-prefetch
job were still active, and the controller's normal-finish marker was absent. A later
read-only refresh was attempted on 21 October 2026 but the Roihu host was not resolvable
from the local environment, so the counts above are not asserted to be newer than the
last successful observation.

No caller calls, public reference typing, joined truth, performance estimate, method
ranking or subject-level result was inspected. These counts describe file integrity and
completion only. They must not appear in the manuscript or be interpreted as interim
accuracy evidence.

## Provenance checks

| Object | Local canonical SHA-256 | Remote state at last successful observation |
|---|---|---|
| `scripts/manage_development_batches.py` | `cd5e6ac676a1b1937e051de3f22d6162cfaf7ddb457cfccb4719b0e8d0aec7e9` | matched |
| `cohorts/development_rerun_manifest.tsv` | `506405a006a2cabc80f8584fa21368d868d56a6164ccd60e017d36173bcbfd85` | matched |
| `scripts/collect_development_rerun.py` | `e6f34c1894c22d2843f51af66ad36c2e0434da1fe19014ccf702ba740648493a` | did not match; remote copy must not be used |

The collector must therefore be run locally from the current source after the complete
remote result tree and truth-free provenance have been exported. The older remote
collector is not an admissible collection program.

## Full-roster stop gate

Collection and analysis remain prohibited until all conditions are simultaneously true:

- validator summary is exactly `checked=236`, `complete_valid=236`,
  `incomplete_or_invalid=0`;
- no `champhla_ctl`, `champhla_dev` or `champhla_prefetch` job remains;
- the controller records a normal finish;
- execution-manager and roster hashes match the canonical values above; and
- `scripts/validate_development_rerun_gate.py` emits a `PASS` gate record.

The gate record is then required by `scripts/activate_development_rerun.py`. Failure of
any check leaves the historical development inputs and all manuscript claims unchanged.
