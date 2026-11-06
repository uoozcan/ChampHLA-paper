# MetaConsensus run-to-run variation — 5 November 2026

One full verification run stopped at the author gate with differences in `artifacts/development_sensitivity_abstain/`. This records what was tested and found. The fitting code and results did not change for it. The only manuscript change is the signed S7.1 correction below.

## Result

Only logistic meta-consensus moves. It is an exploratory fitted comparator.

| Inputs | Refits | Refits with a changed call | Loci that moved | Exact-endpoint scores across refits |
|---|---|---|---|---|
| Primary | 17 | 1 | HG00641 HLA-A, WES, outside the exact endpoint | WES 140 in all 17; RNA-seq 113 in all 17 |
| Abstain-all | 26 | 3 | NA19119 HLA-A, WES, outside (2 refits); NA11830 HLA-B, WES, exact endpoint (1 refit) | WES 143 in 25 and **142 in 1**; RNA-seq 113 in all 26 |

MV-floor scores did not move in any of these refits, and nested-CV output was identical across the probe runs. The vote and the single callers use no fitted model.

- The main-text abstain-all statement (113/118 against 112/118) did not move in 26 refits.
- The abstain-all WES meta-consensus score did move once, so S7.1's "No reported result changed" is true of the 26 October run but not in general.
- HG00641 HLA-A is the same locus recorded on 26 October.

## Mechanism

- Fitted coefficients differ between refits on identical inputs. Among six instrumented parallel runs, comparisons with the same penalty were bit-identical in 19 of 100 primary fold pairs and 13 of 95 abstain fold pairs. The largest differences were 3.5e-3 and 3.0e-2.
- In one abstain run the selected L2 penalty changed in one WES fold (0.1 against 10.0).
- The fit runs a fixed 1,200 optimizer steps, so small numerical differences appear to be amplified rather than damped.

**What is not established:** the origin of the first numerical difference. The 26 October record suggests memory alignment, and that remains unconfirmed.

## What was tested and ruled out

Each prediction was written down before its run.

| Test | Prediction | Outcome |
|---|---|---|
| OpenBLAS threads set to 1, six parallel runs | All identical | **Failed.** One primary run still differed. Threading is not the whole cause |
| Candidates with a top-two gap under 1e-6 | The moved loci are near machine-precision ties | **Failed.** No locus has a gap under 1e-6. The moved loci have gaps of 0.02 to 0.11, so "two candidate pairs were nearly tied" in S7.1 overstates it |
| Hash-order randomness | Not run | Iteration in the fitting code is sorted, so this was set aside by reading the code |

Solo runs did not drift (3 of 3 identical), and five of the six observed differences across this and the earlier test came under parallel load, although that is too few to show load is required. A full pipeline run on its own has also drifted before (26 October).

## Limits

These are 43 refits on one Windows machine. They show what can move, not everything that could. Rarer changes are possible, including at RNA-seq. `src/champhla_confirmation/fitted.py` lies inside the extension-analysis digest pinned by the signed amendment, so a code fix needs a new signed amendment, and it would change exploratory results.

## Signed

`decisions/20261105_metaconsensus_variation.json` holds the corrected S7.1 wording. The author signed it in the Claude Code session of 5 November ("Sign the correction"), and it is applied in S7.1 and the README. Scripts and outputs are in the session scratchpad; per-run outputs are in the git-ignored `runtime_data/drift_probe/`.
