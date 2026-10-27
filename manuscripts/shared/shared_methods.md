# Shared verified methods

> **Internal reference, not a submission file.** These definitions are now
> written out in full in the Methods section of
> `manuscripts/benchmark/manuscript.md`, which no longer delegates to this file.
> A referee receives the manuscript, not this document. Keep the two in step:
> where they differ, the manuscript governs.


ChampHLA harmonises caller outputs into canonical unordered HLA-A, HLA-B, and
HLA-C allele pairs at two-field resolution. Each intended-use caller contributes
at most one callable pair per locus. Missing calls remain explicit.

## Primary method

`ChampHLA-Consensus` is unweighted plurality over the intended-use caller panel:
every callable caller casts one equal vote for its exact canonical unordered
two-field pair, the pair with the most votes is emitted, ties break
alphabetically, and the rule always emits a call. It uses no confidence,
reliability weight, calibration, truth label, gene-specific parameter, or
modality-specific parameter.

The rule is a **plurality**, not a majority: it does not require more than half
of the votes. Earlier internal reports called it "MajorityVote"; the internal
identifier is `SimplePluralityLex`. It must not be confused with
`SimpleStrictMajority` (more than half) or `SimpleTwoThirdsConsensus` (at least
two thirds, abstaining), which are separate rules evaluated as comparators.

Intended-use panels are fixed per modality: WES uses HLA-HD, OptiType,
POLYSOLVER, SpecHLA and T1K; RNA-seq uses ArcasHLA, HLA-HD, OptiType and T1K;
WGS uses HLA-HD, Kourami, OptiType, SpecHLA and T1K.

## Comparators

Every individual intended-use caller, `BestSingleTool_nestedCV`,
`SimpleTwoThirdsConsensus`, `ChampionChallenger`, `TwoThirdsGuardedCC`,
`MVFlooredCC` and `MetaConsensus` are reported as comparators. No comparator is
omitted from the main comparison.

`TwoThirdsGuardedCC` preserves every two-thirds consensus call, invokes the
frozen Champion–Challenger policy below that threshold, and falls back to
deterministic plurality when the raw policy is unavailable. The truth-derived
homozygosity amendment is excluded. It is reported as an ablation.

## Endpoint and inference

The primary endpoint is exact unordered two-field correctness at the fixed
eligible-locus denominator. Only loci whose laboratory truth resolves uniquely
to a two-field pair enter that denominator; no representative allele is chosen
from a cross-two-field ambiguity. A missing call or `no_consensus` is incorrect.
A comparator that does not cover a locus scores zero at that locus, so all
methods share one denominator. Callability and accuracy among called loci are
reported next to the primary endpoint for abstaining rules.

The reporting denominator is all development subjects: 390 WES loci, 321
RNA-seq loci, 411 WGS loci. The 276/231/275 subject-separated subset is a
sensitivity analysis only. This choice is recorded, with its discovery path
disclosed, in `decisions/20260908_consensus_primary_amendment.json`.

All predictions are produced without truth-bearing columns and checksummed
before truth is joined once. Statistical inference clusters by subject, uses
exact paired sign-flip tests and subject bootstrap intervals, and applies Holm
correction within each modality's comparator family. WGS, WES, and RNA-seq have
separate input, reference, caller-panel, and QC records.

## WGS scope

No WGS accuracy claim is made. The legacy WGS extraction omitted HLA
alternate-contig mappings and mates outside the chromosome-6 interval, and all
legacy WGS rows carry `validity=invalid` in `result_registry.tsv`. WGS appears
only as a diagnostic analysis of how harmonisation defects propagate into
consensus.
