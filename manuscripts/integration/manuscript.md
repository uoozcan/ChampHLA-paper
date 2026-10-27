# Fitted integration policies do not improve on an equal-weight caller vote in short-read HLA class-I typing

## Status

**Draft in preparation.** This is the companion to the benchmark manuscript
(`manuscripts/benchmark/manuscript.md`), which compares ChampHLA-Consensus against
individual callers and simple rules. The scope split is recorded in
`decisions/20260921_integration_scope_split.json` and is **pending author sign-off**;
until that record is signed and this draft is written out in full, the benchmark
manuscript's deferral statement is a promise rather than a citation, and the two
should be submitted or revised together.

Nothing here is new analysis. Every method below was built, run and frozen before
the split, and all of it remains in `artifacts/head_to_head/consensus_head_to_head.tsv`,
`artifacts/integration_limits/`, `configs/comparator_manifest.json` and
`result_registry.tsv`. The benchmark manuscript's Supplementary S1 still reports the
complete head-to-head, including every method listed here, so the split removes no
evidence from the reader.

## What this paper covers

Eight policies fitted on top of the equal-weight vote:

| Method | Kind |
|---|---|
| WeightedConsensus | reliability-weighted vote |
| ChampionChallenger | per-gene champion with a challenger override |
| TwoThirdsGuardedCC | CC below a two-thirds consensus threshold |
| MVFlooredCC | CC restricted to training-supported vote strata |
| FamilyGatedCC | CC with an algorithm-family diversity requirement |
| MetaConsensus | L2-regularised candidate-level scorer |
| EvidenceGatedCC | read-level 31-mer evidence override |
| RefFormer | transformer candidate reranker |

The line against the benchmark paper is that each of these carries parameters, a
training cohort, or a learned scorer. The callers and simple rules reported there
carry none.

## The three findings this paper has to carry

**1. None of them separated from the vote.** Differences run from zero to five loci
in either direction, and `MVFlooredCC` reproduces the vote's call at every locus in
both assays — an identical method, not a close one.

**2. Most of the comparisons could not have detected a difference.** The exact
sign-flip test enumerates 2^k sign assignments over the k subjects with a non-zero
net difference, so its smallest attainable two-sided p is 2^(1−k). Seven of the ten
method-by-assay comparisons could not have returned p < 0.05 at any effect size.
Reporting "not significant" without this is uninformative. Source:
`artifacts/integration_limits/detectability.tsv`.

**3. Non-inferiority fails on WES, and that is the reason for the next study.**
Against the two-percentage-point margin, the simultaneous lower bound
on the difference reaches −3.08 points for ChampionChallenger and TwoThirdsGuardedCC
and −3.33 for FamilyGatedCC. Consensus cannot be declared non-inferior to them at
this cohort size. Resampling puts the cohort that would settle it at roughly 500
subjects (`artifacts/integration_limits/power_curve.tsv`), and 373 unexposed
truth-eligible WES subjects remain in the resource. The RNA-seq arm cannot be
settled this way at all: three of the methods have a net difference of exactly zero
there, and its unexposed pool is capped at 99 against a locked minimum of 130.

## Material to be moved here from the benchmark supplement

- **S2**, the per-method ablation table with intended improvement, outcome and decision.
- **S2a**, the algorithm-family diversity gate measurement, including the four reverted
  overrides and the pre-registration at `decisions/20260918_family_gate_measurement.json`.
- **The integration rows of S8**, minimum detectable effect and the power curves.

The ceiling analysis stays in the benchmark paper. It is computed from caller outputs
alone, it bounds what any of these policies could have achieved before any was built,
and it is the reason this paper's answer is negative.

## To do before this is submittable

- Sign `decisions/20260921_integration_scope_split.json`, or abandon the split and
  return this material to the benchmark manuscript.
- Move S2, S2a and the S8 integration rows here rather than duplicating them.
- Write Methods, Discussion and References; the benchmark manuscript's Methods
  covers the shared cohort, endpoint and inference and should be cited rather than
  restated.
- Resolve the same author front matter that blocks the benchmark paper.
