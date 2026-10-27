# Equal-weight caller consensus is a strong default for short-read HLA class-I typing: a benchmark of six callers across exome and transcriptome sequencing

## Authors

Umut Onur Özcan^1^, Nemo Ikonen^TO CONFIRM^, Philipp Sergeev^TO CONFIRM^,
Ella Sinervuori^TO CONFIRM^, Khalid Saeed^TO CONFIRM^,
Ziaurrehman Tanoli^TO CONFIRM^, Markus Vähä-Koskela^TO CONFIRM^

TO CONFIRM — author order. The list above follows the order used in earlier
internal records and has not been agreed for submission.

**Affiliations.** TO CONFIRM — one numbered affiliation per author, with
department, institution, city and country.

**ORCIDs.** TO CONFIRM — one iD per author.

**Corresponding author.** TO CONFIRM — name, institutional address and email.

## Keywords

HLA typing; consensus methods; ensemble benchmarking; immunogenomics;
reproducible workflows; exome sequencing; RNA sequencing

## Abstract

Short-read HLA typing depends on both the sequencing assay and the choice of
computational caller, and no single caller is best across assays. We built
PanelHLA, a reproducible workflow that executes modality-appropriate HLA
callers, harmonises their outputs to canonical two-field allele pairs, and
records the evidence behind every integration decision. Using it we benchmarked
six callers — five on exomes and four on transcriptomes, overlapping in three —
on 1000 Genomes exome and transcriptome data against reference-quality
laboratory typing, scoring exact unordered two-field HLA-A, HLA-B and HLA-C
calls at fixed denominators that count missing calls as incorrect.

Unweighted plurality over a modality-appropriate caller panel matched the best
individual caller in each assay without requiring prior knowledge of which
caller that would be. It significantly outperformed three of the five exome
callers and one of the four transcriptome callers, and was not significantly
worse than any of them. Eight fitted integration policies were also built on this
vote and evaluated against it; none separated from it in either assay, and they
are reported in a companion paper rather than here. The reason they had so
little room is a ceiling we measure directly: where the vote errs, no caller in
the panel is correct at 15 of 25 WES and 13 of 15 RNA-seq loci, leaving 10 and 2
loci recoverable by any method that selects among caller outputs. We also find
that the vote supplies the confidence scale its callers lack: unanimous calls
are correct 98.2% (WES) and 97.8% (RNA-seq) of the time against 50.0% at a bare
plurality, so a user can route a small minority of loci to review rather than
treating all calls alike. We further show that a
harmonisation defect, in which a caller's undetermined second allele is
duplicated into a false homozygous genotype, propagates preferentially into
consensus calls, and we report it as a diagnosis of the apparent fragility of
consensus in whole-genome data — a lane whose inputs are invalid, from which no
accuracy claim is made here. PanelHLA is released as an open, auditable benchmarking and
integration framework under the MIT licence; the callers it invokes carry their own
terms, several of which restrict commercial use. Results reported here are
development evidence pending frozen unseen-subject confirmation.

## Introduction

HLA class-I genotype is a prerequisite for work in several clinical and research
settings: drug hypersensitivity risk (Chung *et al.*, 2004; Mallal *et al.*,
2008), donor matching in haematopoietic transplantation (Petersdorf *et al.*,
2007), susceptibility across autoimmune and infectious disease (Matzaraki
*et al.*, 2017), and neoantigen prediction in cancer immunotherapy (Schumacher
and Schreiber, 2015).

Typing it from short reads is difficult because of extreme polymorphism
(Trowsdale and Knight, 2013; Robinson *et al.*, 2020), reference bias,
multimapping, assay-specific coverage, and heterogeneous caller outputs
(Mishima *et al.*, 2019). Individual tools adopt different reference resources
and inference strategies, so their errors and their missingness differ
(Kiyotani *et al.*, 2017), and, as the results below show, their relative
ranking is not stable across sequencing assays. A practitioner who must type
HLA from a given assay therefore faces a selection problem before an accuracy
problem: which caller should be trusted here?

Combining callers is the natural response, and combination rules of increasing
sophistication carry an intuitive appeal that this paper puts to test: whether
any of them improves on a plain equal-weight vote, measured against that vote
rather than against the weakest available alternative. It matters, because a
complex integration policy carries costs a simple vote does not: parameters
that must be fitted, a training cohort that must be representative — a cost
measured directly here when a trained scorer is transferred to a second
resource — and a failure mode that is opaque to the user.

This paper asks three questions. Does combining callers protect against
choosing the wrong one? Where does caller disagreement leave room for
selection? And do more complex selection methods provide reproducible benefit
beyond a transparent vote? We answer them with one workflow, one endpoint, and
one set of denominators, reporting both the methods that worked and the ones
that did not.

## Methods

### Data and reference typing

Development data are 1000 Genomes phase 3 exome alignments (WES; 1000 Genomes
Project Consortium, 2015) and Geuvadis transcriptome samples (RNA-seq;
Lappalainen *et al.*, 2013), with reference-quality laboratory HLA typing from
the 2014 1000 Genomes HLA panel (Gourraud *et al.*, 2014). The reporting denominator is
all development subjects: 390 WES loci from 130 subjects and 321 RNA-seq loci
from 107 subjects, covering HLA-A, HLA-B and HLA-C.

Only loci whose laboratory truth resolves uniquely to a two-field pair enter the
denominator; no representative allele is chosen from a cross-two-field
ambiguity, which sequence-based typing can leave unresolved (Adams *et al.*,
2005). The current 1000 Genomes analysis is development evidence.
Subject-unseen 2014 laboratory-typed 1000G samples are reserved for
same-resource confirmation and are not described as an independent cohort. HPRC
phased assemblies (Liao *et al.*, 2023; Hickey *et al.*, 2024) define the
independent whole-genome validation arm. NCI-60 (Reinhold *et al.*, 2019) and
E-MTAB-197 (Montgomery *et al.*, 2010) are secondary transfer or independent-library analyses and are not
pooled into the primary family.

### Callers and intended-use panels

PanelHLA is a Nextflow DSL2 workflow (Di Tommaso *et al.*, 2017) that integrates
eight HLA callers: OptiType (Szolek *et al.*, 2014), arcasHLA (Orenbuch *et al.*,
2019), HLA-HD (Kawaguchi *et al.*, 2017), T1K (Song *et al.*, 2023), POLYSOLVER
(Shukla *et al.*, 2015), Kourami (Lee and Kingsford, 2018), seq2HLA (Boegel
*et al.*, 2012) and SpecHLA (Wang *et al.*, 2023).

Voting uses a curated intended-use panel per assay rather than all eight,
because a caller run outside the assay it was designed for contributes noise
rather than information. Five callers vote on WES (HLA-HD, OptiType, POLYSOLVER,
SpecHLA, T1K) and four on RNA-seq (arcasHLA, HLA-HD, OptiType, T1K) — six
distinct callers across the two assays, overlapping in three. Kourami votes only
on whole-genome data and therefore does not enter the results reported here.
Supplementary S3 reports the cost of abandoning panel curation entirely.

### Caller reference databases

Callers are evaluated as deployed, each with the IPD-IMGT/HLA release (Robinson
*et al.*, 2020) it bundles, rather than rebuilt against a single release. Those
releases differ substantially:

| Caller | IPD-IMGT/HLA release | Determined from |
|---|---|---|
| POLYSOLVER | 3.11.0 | database content, filtered to complete sequences |
| OptiType | 3.13.1 | database content |
| HLA-HD | 3.15.0 | `dictionary/allele.list` |
| Kourami | 3.24.0 | `db/VERSION.txt`, content agrees |
| arcasHLA | 3.40.0 | `dat/IMGTHLA/version_report.txt` |
| SpecHLA | 3.38.0 + 3.51.0 | internally heterogeneous across its own components |
| T1K | 3.63.0 | deployment declaration, content agrees |

The panel therefore spans **52 releases**, from 3.11.0 to 3.63.0. This is a
property of the comparison, not an oversight: it reflects how these tools are
actually distributed and used. It also means some caller disagreement is a
database-vintage artefact rather than an inference difference, and that an
allele absent from an older bundled database cannot be called by that caller at
all. We return to this in the Limitations.

Releases were determined by matching each database's two-field type set against
pinned per-release allele lists, taking the earliest release containing every
type. Two bundled filenames are misleading and were resolved by content:
HLA-HD's `HLA_gene.split.3.32.0.txt` is a gene and exon table carrying no allele
designations rather than the allele database, and POLYSOLVER's
`a_complete.3100.new.eb.fasta` is 3.11.0, not 3.10.0.

The full resolution record, which reproduces the table above from each caller's
bundled database together with the coverage evidence behind each assignment, is
`provenance/external_evidence/db_release_resolution.json`. It covers the six
callers that ship a database whose release can be determined from content.
arcasHLA is the exception: it declares its release directly in
`dat/IMGTHLA/version_report.txt`, which is the source for 3.40.0.

### Harmonisation

Caller outputs are harmonised into canonical unordered HLA-A, HLA-B and HLA-C
allele pairs at two-field resolution. Each intended-use caller contributes at
most one callable pair per locus, and missing calls remain explicit rather than
being imputed. Harmonisation is not a neutral preprocessing step; a defect in
this layer is analysed in the Results.

### Primary method

`PanelHLA-Consensus` is unweighted plurality over the intended-use caller panel.
Every callable caller casts one equal vote for its exact canonical unordered
two-field pair, the pair with the most votes is emitted, ties break
alphabetically, and the rule always emits a call. It uses no confidence score,
reliability weight, calibration, truth label, gene-specific parameter or
modality-specific parameter, so it has nothing to fit and nothing to overfit.

The rule is a **plurality**, not a majority: it does not require more than half
of the votes. It must not be confused with `SimpleStrictMajority` (more than
half) or `SimpleTwoThirdsConsensus` (at least two thirds, abstaining), which are
separate rules evaluated here as comparators. Its internal identifier is
`SimplePluralityLex`, and earlier internal reports of this work called the same
rule "MajorityVote".

### Comparators

Every individual intended-use caller is reported, together with
`BestSingleTool_nestedCV` (fold-wise best-caller selection),
`SimpleTwoThirdsConsensus`, `ChampionChallenger`, `TwoThirdsGuardedCC`,
`MVFlooredCC` and `MetaConsensus`. No comparator is omitted from the main
comparison. `TwoThirdsGuardedCC` preserves every two-thirds consensus call,
invokes the frozen Champion–Challenger policy below that threshold, and falls
back to deterministic plurality where the raw policy is unavailable; the
truth-derived homozygosity amendment is excluded from it. It is reported as an
ablation, not as a candidate method.

Because the plurality rule is also emitted under its historical name, that
duplicate row is excluded from the comparator family, so no method is compared
against itself and each Holm family counts only distinct comparators.

### Endpoint and denominators

The primary endpoint is exact unordered two-field correctness at the fixed
eligible-locus denominator. A missing call or an explicit `no_consensus`
abstention counts as incorrect. Because the denominator is fixed, a comparator
that emits no row at an eligible locus is scored incorrect there rather than
dropped, so every method is evaluated over identical loci; coverage is reported
beside each comparison. Coverage is complete for every WES comparator, and the
three RNA-seq callers other than arcasHLA are absent at 6 of 321 loci. For
abstaining rules, callability and accuracy among called loci are reported next
to the primary endpoint, because a fixed denominator otherwise understates them.

### Statistical inference

Predictions are produced without truth-bearing columns and checksummed before
truth is joined once. Inference clusters by subject throughout. Paired
comparisons use exact subject-cluster sign-flip tests, and Holm correction
(Holm, 1979) is applied within each modality's comparator family.

Two kinds of bootstrap interval appear in this paper and they are not
interchangeable. Per-comparator intervals are subject-cluster bootstrap
intervals over 100,000 resamples, seeded per modality and comparator, at a
two-sided five per cent error rate; these are the intervals reported in Table 1
and Supplementary S1, and they are not corrected for multiplicity. Where such
an interval excludes zero but the Holm-adjusted test does not reach
significance, the Holm-adjusted test governs the claim. The non-inferiority
assessment instead uses family-simultaneous bounds: the same subject-cluster
bootstrap evaluated at alpha divided by the number of comparators in that
modality's family, so that the bounds hold simultaneously across the family.
Only these are described as simultaneous, and they are used nowhere else.

### Whole-genome scope

No whole-genome accuracy claim is made. The legacy WGS extraction omitted HLA
alternate-contig mappings and mates falling outside the chromosome-6 interval,
and all legacy WGS rows carry `validity=invalid` in `result_registry.tsv`. WGS
appears here only as a diagnostic analysis of how a harmonisation defect
propagates into a consensus.

### Pre-registration amendments

Both the choice of primary method and the choice of reporting denominator were
made after development scores were visible. Neither is presented as
prespecified: both are disclosed as amendments in
`decisions/20260908_consensus_primary_amendment.json`, with the superseded
record retained alongside. The 276/231 subject-separated subset used in earlier
internal reports is retained as a sensitivity analysis only. Superseded and
historical analyses, including the withdrawn whole-genome headline, are listed in
Supplementary S6.

## Results

### The best individual caller is assay-dependent

No caller led both assays. On WES the strongest individual callers were
OptiType (360 of 390 loci) and POLYSOLVER (357), with T1K at 324, SpecHLA at 306
and HLA-HD at 305. On RNA-seq the ordering changed: HLA-HD reached 297 of 321 loci,
OptiType 296, arcasHLA 295 and T1K 277, and the WES advantage of OptiType did
not carry over. A user committed in advance to any single caller therefore
accepts a substantial and assay-specific risk of having chosen the wrong one.
Per-gene rates for every caller are given in Supplementary S5.

A procedure that selects the best caller within training folds
(`BestSingleTool_nestedCV`) reached 360 of 390 WES loci and 291 of 321 RNA-seq
loci, confirming that the selection problem is not solved simply by measuring
tool performance on a training split.

### Consensus matches the assay-best caller without selecting it

`PanelHLA-Consensus` was correct at 365 of 390 WES loci
[RESULT:DEV_WES_CONSENSUS] and 306 of 321 RNA-seq loci
[RESULT:DEV_RNA_CONSENSUS] (Figure 1).

Against the individual callers it separated cleanly into two regimes. It
significantly outperformed three of the five WES callers — HLA-HD (+60 loci, 63
wins against 3 losses, Holm-adjusted p = 4.3e-12), SpecHLA (+59, 60 against 1,
p = 8.7e-13) and T1K (+41, 47 against 6, p = 1.9e-7) — and one of the four
RNA-seq callers, T1K (+29, 30 against 1, p = 1.4e-5). Against the strongest
caller in each assay it was statistically indistinguishable: OptiType on WES (+5
loci, 8 wins against 3 losses, Holm-adjusted p = 1.0) and POLYSOLVER on WES (+8,
11 against 3, p = 0.17). On RNA-seq its leads over arcasHLA (+11), OptiType
(+10) and HLA-HD (+9) did not survive Holm correction (p = 0.091, 0.22 and
0.75), though it lost no locus at all to OptiType or HLA-HD. It was not
significantly worse than any individual caller in either assay. The complete
comparator table, with coverage and confidence intervals, is Supplementary S1.

Consensus did significantly outperform fold-wise best-tool selection on RNA-seq
(+15 loci, 15 wins against 0 losses, Holm-adjusted p = 0.02) and matched it on
WES (+5, p = 1.0).

The claim this supports is therefore one of protection rather than ceiling:
equal-weight voting delivers approximately the accuracy of the best caller for
an assay while requiring no prior knowledge of which caller that is, and it
removes the tail risk of committing to a caller that is weak in the assay at
hand. Its 5-locus margin over the best WES caller is not significant, so it
should not be read as exceeding that caller's accuracy.

### How much of the panel agrees is itself a confidence scale

The callers expose no common confidence score, so a consensus over them appears
to inherit none. It does not: the number of panel members backing the emitted
pair is a scale the vote produces for free, and it is strongly calibrated
(Figure 5). At loci where the whole panel is callable and unanimous, the vote is
correct at 219 of 223 WES loci (98.2%) and 267 of 273 RNA-seq loci (97.8%). One
dissenter costs little on WES — 109 of 116, 94.0%. Below that the rate falls
steeply: 31 of 37 at three-of-five (83.8%), and 6 of 12 at a bare two-of-five
plurality, which is indistinguishable from a coin toss.

The practical consequence is that a user need not treat every call alike. Calls
carrying unanimous or all-but-one support are 339 of 390 WES loci (86.9%) and
302 of 321 RNA-seq loci (94.1%), and are correct at 96.8% and 96.0%. The
remaining 51 WES and 19 RNA-seq loci are correct at 72.5% and 84.2%, so routing
that minority to review or to orthogonal typing concentrates nearly all of the
residual error into one locus in eight on WES and one in seventeen on RNA-seq.
The
RNA-seq curve is not monotone — two-of-four scores 9 of 11 against 23 of 29 at
three-of-four — but both rest on fewer than thirty loci, and the difference is
well within what those counts support.

Ties are the boundary case of the same phenomenon and are rare: the frozen
alphabetical tie-break was invoked at 9 loci across both assays and was correct
at 2 of them (0 of 5 on WES, 2 of 4 on RNA-seq). The rule is arbitrary by
construction and resolves too few loci to matter for the reported totals, but a
tie is better read as an abstention signal than as a call.

Both tables are generated by `scripts/plurality_support_calibration.py` into
`artifacts/plurality_characterisation/`; Supplementary S7 gives the full
breakdown, including the reduced-panel loci excluded from Figure 5.

### Consensus against every caller and simple rule

Against the abstaining two-thirds rule, consensus gained 37 WES loci (37 wins,
0 losses, Holm-adjusted p = 3.7e-8) [RESULT:DEV_TT_WES_BASE] and 10 RNA-seq
loci (10 wins, 0 losses, p = 0.035) [RESULT:DEV_TT_RNA_BASE], because the
two-thirds rule abstains at low-agreement loci that count against it at a fixed
denominator. The advantage of the two-thirds rule is conditional accuracy among
called loci, and its callability and called-only accuracy are reported beside
the primary endpoint (Figure 4). The full comparator picture is Figure 2.

**Table 1. Consensus against each caller and simple rule.** Correct calls at the
fixed eligible-locus denominator of 390 WES and 321 RNA-seq loci, with
Holm-adjusted p values from exact subject-cluster sign-flip tests against the
vote. Correction is applied over every comparison conducted in this cohort --
twelve on WES and eleven on RNA-seq -- not over the subset printed here, because
multiplicity is a property of the analyses performed rather than of the ones
reported. A dash marks a caller outside that assay's intended-use panel.

| Comparator | WES | RNA-seq |
|---|---|---|
| PanelHLA-Consensus | 365 / 390 | 306 / 321 |
| Caller: OptiType | 360 (p = 1.0) | 296 (p = 0.22) |
| Caller: POLYSOLVER | 357 (p = 0.17) | — |
| Caller: T1K | 324 (p = 1.9e-7) | 277 (p = 1.4e-5) |
| Caller: SpecHLA | 306 (p = 8.7e-13) | — |
| Caller: HLA-HD | 305 (p = 4.3e-12) | 297 (p = 0.75) |
| Caller: arcasHLA | — | 295 (p = 0.091) |
| SimpleTwoThirdsConsensus | 328 (p = 3.7e-8) | 296 (p = 0.035) |
| BestSingleTool_nestedCV | 360 (p = 1.0) | 291 (p = 0.02) |

No caller exceeds the vote in either assay. The three RNA-seq callers that lack
a row at six loci are scored incorrect there by the fixed-denominator
convention, which accounts for part of the OptiType and HLA-HD gaps;
Supplementary S1b reports those comparisons again restricted to loci where the
whole panel emits a call.

### Fitted integration policies are reported separately

Eight integration policies of increasing sophistication were built on top of
this vote and evaluated against it on the same loci: a reliability-weighted
consensus, a Champion-Challenger routing policy and three variants of it
including an algorithm-family diversity gate, a regularised candidate-level
scorer, an evidence-gated override and a transformer reranker. None of them
separated from the vote in either assay. They are reported in full in a
companion paper, because they are a different kind of object from the callers
and simple rules compared here -- each carries parameters, a training cohort or
a learned scorer -- and because the question they raise needs a larger cohort
than this one to settle.

Two things about them belong here rather than there, because deferring the
methods must not defer what they say about the vote. First, three of them are
numerically ahead of the vote on WES by four and five loci, none significantly.
Second, and more important, the two-percentage-point non-inferiority margin
**fails** against those three: the simultaneous lower bound on the difference
reaches -3.08 points for Champion-Challenger and its two-thirds-guarded
variant and -3.33 for the family-gated variant, so consensus cannot be
declared non-inferior to them at this cohort size. Resampling puts the
cohort that would settle the question at roughly 500 subjects, and the resource
can supply them. The scope decision is recorded in
`decisions/20260921_integration_scope_split.json`, and the multiplicity family
above is unchanged by it.

### Negative method ablations

Two extensions were taken to prespecified kill criteria and stopped. RefFormer,
a transformer candidate reranker over pinned IPD-IMGT/HLA sequence
representations, failed its candidate-reranker gate [RESULT:REFFORMER_GATE]: it
did not exceed the strongest baseline in any assay, and the IMGT-aware model did
not outperform its own no-IMGT ablation. EvidenceGatedCC, which used independent
read-level 31-mer evidence to override the vote only under strong evidence,
failed its development gate [RESULT:EGCC_GATE], rescuing none of the 23 WES and
none of the 9 RNA-seq consensus errors it targeted. Those two counts are taken
on the subject-separated development subset the gate was run against (276 WES
and 231 RNA-seq loci, Supplementary S6), not on the reporting denominator used
elsewhere in this paper, where the vote errs at 25 and 15 loci. Candidate expansion raised
the theoretical oracle, but the evidence scorer could not identify the correct
candidate reliably.

These are informative rather than merely negative, for a reason the next section
makes measurable.

### There is very little left for caller-output-only integration to win

Any method that chooses among the calls its panel emitted is bounded by those
calls: where every caller is wrong, no selection policy can be right. Comparing
the vote against an oracle that takes any caller's correct answer therefore
measures the ceiling, and the ceiling is low.

The vote is wrong at 25 of 390 WES loci and 15 of 321 RNA-seq loci. At 15 of
those 25 and 13 of those 15, **no panel caller produced the correct genotype
either**, so the recoverable headroom is 10 WES loci (2.6 percentage points) and
2 RNA-seq loci (0.6 points). Every locus the vote gets right is one some caller
got right, so this is a partition rather than an approximation; the check is
asserted in the generating script and would fail loudly otherwise.

This is the quantity that explains the rest of the paper. It bounds what any of
the eight integration methods could have contributed before any of them was
built, it is why their measured differences from the vote are one to five loci,
and it is why the two evidence-based extensions failed: EvidenceGatedCC and
RefFormer both attacked errors that are mostly not recoverable from caller
output at all. A method with a genuinely independent evidence source is not
bounded this way, which is the one direction the present results leave open.

The ceiling is also a diagnostic another group can compute for its own panel
before investing in integration, from nothing more than per-caller calls and
reference typing: `scripts/integration_headroom_and_power.py` writes it to
`artifacts/integration_limits/headroom.tsv`.

### Harmonisation is not neutral, and whether it harms depends on the assay

Whole-genome results are reported as a diagnostic only. The historical WGS
extraction omitted HLA alternate-contig mappings and mates falling outside the
chromosome-6 interval, so no WGS accuracy estimate from it is admissible, and
all legacy WGS results are flagged invalid in the result registry. A repaired
mate-aware full-CRAM pipeline has been run on two subjects, where automated
freeze, parser and native-source checks passed on all 30 expected caller-locus
records; named human adjudication of those records is still outstanding, and
the production gate requires ten reviewed records per caller before any
whole-genome expansion is authorised
(`artifacts/wgs_pilot_review/REVIEW_STATUS.md`). This establishes that the
workflow runs, not that it performs.

The diagnostic finding is nonetheless informative about consensus itself. When
a caller cannot determine a second allele it emits a placeholder, and
harmonisation replaced that placeholder with a copy of the first allele,
converting a partial call into a confident homozygous genotype.

Whether that is an error turns out to depend on the assay. On WES and RNA-seq a
placeholder second allele signals genuine homozygosity: the reference typing at
affected loci is homozygous in 92.1% and
97.0% of cases against a baseline near
13%, so duplicating the first allele is correct
93.4% and
97.8% of the time. Re-deriving the vote
under a pre-registered rule that abstains instead *reduces* accuracy, by 1 WES and
3 RNA-seq loci, while the individual callers carrying the behaviour lose around
thirty each. In whole-genome data the same rule is harmful rather than helpful,
because the invalid legacy extraction caused genuine allele dropout: there the
reference typing at affected loci is heterozygous 80.4% of the time and the
manufactured genotype correct only 17.0%.

The effect is caller-specific rather than universal, which is itself informative.
Across the development cohort reported here it affected HLA-HD, T1K and arcasHLA;
OptiType emits no placeholder at all, and SpecHLA emits 75 of them on RNA-seq yet
manufactured no homozygous genotype from any, because its outputs were handled
correctly. A second and largely disjoint mechanism compounds the first: SpecHLA
and POLYSOLVER sometimes report two distinct high-resolution alleles that collapse
to the same two-field group. Taken together the two mechanisms make 4.1% of WES
and 7.4% of RNA-seq panel-member calls falsely homozygous. Figure 3 summarises the
mechanism and these rates; Supplementary S4 gives the per-caller counts and
explains why an earlier internal report of this defect quoted a higher WES figure,
which was measured on a larger cohort than the one reported here.

This matters for integration methods generally. A vote aggregates its panel, so it
concentrates rather than dilutes a defect carried by several panel members — on
RNA-seq, three of the four. The correct handling is to treat an undetermined
second allele as a partial call, either abstaining
from the vote at that locus or voting only for the allele actually determined.
Because the defect is present in all three assays, correcting it requires
re-running all of them, and we therefore report it as a defect diagnosis rather
than applying a correction to the results above.

A residual WGS problem is not explained by this defect: OptiType emits no
placeholders and no same-group collapses, yet its WGS accuracy remains far
below its WES accuracy, while class II appears to perform better than class I on
the same inputs. Something class-I-specific in the WGS path remains unresolved.
Both observations derive from the invalid legacy inputs and are stated as a
direction only; no value is cited for either, and neither can be resolved
without the corrected whole-genome lane (Supplementary S4e).

## Discussion

Across two assays and eight integration methods, the strongest reproducible
finding is a negative one: we could not build a caller-output-only method that
separates from an unweighted vote. This is not evidence that integration is
worthless — the vote significantly outperforms three of the five WES callers,
one of the four RNA-seq callers, and fold-wise tool selection on RNA-seq — but
it bounds what integration buys. The value of consensus here is protection
against caller choice, not a higher ceiling.

The bound is worth stating precisely, because "not significant" and "no
difference" are different claims and this study supports different ones for
different methods. `MVFlooredCC` reproduces the vote's call at every locus, so
the two are the same method on this data. The three Champion–Challenger variants
differ from the vote at between two and seven subjects, which is too few for the
test to resolve at any effect size on RNA-seq and too few to survive
multiplicity correction on WES. MetaConsensus, which is one locus behind in
each assay, is the one comparator whose difference could not have reached
significance in either assay at any effect size (Supplementary S8).
Resampling puts the cohort that would settle the WES question at roughly 500
subjects; the resource can supply them, and that is the study these results
argue for.

We think the mechanism is saturation. Where the panel agrees it is usually
right — at loci where at least two thirds of it concurs, the call is correct
96.8% of the time on WES and 96.1% on RNA-seq (Supplementary S3) — and a vote
captures that for free. Where callers disagree, the correct genotype is
frequently absent from every caller's output: at 15 of the 25 WES and 13 of the
15 RNA-seq loci the vote misses, no panel caller had it either, so no policy
operating on caller outputs could have recovered those; that is what the
EvidenceGatedCC and RefFormer gates measured, and both failed for the same
reason. Methods with more
parameters had more opportunity to overfit the development cohort without a
corresponding source of new information, which is consistent with
MetaConsensus regressing on transfer to NCI-60.

The practical recommendation follows directly. For WES and RNA-seq class-I
typing, run a modality-appropriate panel and take an equal-weight vote; prefer
an abstaining threshold only if conditional accuracy matters more than
coverage, and expect to pay for it in callability. Reserve complex integration
for settings where a genuinely independent evidence source is available, not
merely a richer function of the same caller outputs.

The harmonisation diagnosis carries a transferable lesson for anyone building
consensus over heterogeneous callers: harmonisation is not a neutral
preprocessing step. A vote aggregates its panel, so it concentrates rather than
dilutes a behaviour carried by several panel members — on RNA-seq, three of the
four. Whether that concentration helps or harms depends on whether the
imputation is right, and that is a property of the input rather than of the
rule. On WES and RNA-seq it was usually right, and abstaining instead costs the
vote 1 and 3 loci against roughly thirty for each affected caller. In the
whole-genome lane the same rule was harmful, because a placeholder there marked
a dropped allele rather than a homozygote; that contrast is a diagnosis drawn
from invalid inputs, not a performance comparison. What generalises is the
requirement rather than the direction: a harmonisation layer deserves the same
scrutiny as the integration rule.

The study is restricted to class-I, exact two-field typing, and has not been
validated for clinical or diagnostic application.
Class II, long reads, clinical safety, FIMM LOH, HED, and survival analyses are
outside the main manuscript.

## Limitations

All results here are development evidence on a single resource and are not
external confirmation; primary-method and denominator choices were made after
development scores were visible and are disclosed as pre-registration
amendments. The pre-registered confirmation gate accordingly does not retain a
confirmed headline: its external prerequisites — an independent cohort and the
locked minimum subject counts — are not met, and the evaluation therefore
reports discovery status. The RNA-seq arm is furthest short: 107 subjects
against a locked minimum of 130, and only 99 unexposed subjects with eligible
laboratory typing remain in the resource, so that arm cannot reach its
confirmatory target at all. What the gate does establish on this cohort is that
no tested comparator significantly exceeds the vote in either assay, and that
the vote harms no individual gene.

That first clause is weaker than it sounds and should not be read as a finding
of equivalence. A criterion phrased as the absence of a significant exceedance
passes automatically wherever the comparison is underpowered, and most of the
integration comparisons here are underpowered by construction rather than by
accident: seven of the ten could not have returned a significant result at any
effect size (Supplementary S8). Equivalence is claimed only where it is
measured — `MVFlooredCC` is identical to the vote locus by locus — and nowhere
else.

The comparison is restricted to HLA-A, HLA-B and HLA-C at exact two-field
resolution, so conclusions do not transfer to class II or to higher-field typing
without re-evaluation. No WGS accuracy claim is made, and the residual class-I
WGS deficit is unexplained. Because integration methods were evaluated on caller
outputs from one panel per assay, we cannot exclude that a different panel
composition would change the ranking.

Callers were evaluated as deployed, each carrying its own bundled IPD-IMGT/HLA
release, and those releases span 52 releases from 3.11.0 to 3.63.0. This
reflects how the tools are actually distributed, but it confounds the comparison
in a specific way: part of what we measure as caller disagreement is a
difference in database vintage rather than in inference, and a caller whose
bundled database predates an allele cannot call that allele at all. The effect
is not symmetric across callers, so the individual-caller ranking reported here
should be read as a ranking of deployed tools rather than of algorithms.
Rebuilding every caller against one release would isolate the algorithmic
comparison, and would be a different study.

A further consequence of the fixed denominator is that comparators differ in
coverage; three RNA-seq callers are absent at 6 of 321 loci and are scored
incorrect there. This is the convention that keeps all methods on one
denominator, but it slightly penalises callers that decline to emit a row rather
than emitting a wrong one.

## Figures

Generated by `scripts/generate_figures.py` from the frozen analysis artifacts;
no value in any figure is transcribed by hand. Source files are in `figures/` as
vector PDF with embedded TrueType fonts, and as 600 dpi PNG and LZW-compressed
TIFF. Titles are carried by these captions rather than set inside the artwork.

**Figure 1. Consensus tracks the assay-best caller without selecting it.**
Correct two-field calls at the fixed eligible-locus denominator, for every
intended-use caller and for the vote, in each assay. Counts are printed beside
each bar. The best individual caller differs between assays — OptiType on WES,
HLA-HD on RNA-seq — while the vote is at or above the best caller in both
without being told which one it is.

**Figure 2. The vote against every comparator evaluated in this cohort.**
Paired advantage of the vote over each comparator, in percentage points, with
subject-cluster bootstrap intervals. Red points and asterisks mark comparators
the vote beats with Holm-adjusted significance within that modality's family; no
comparator lies significantly to the left of zero in either assay. Intervals are
uncorrected for multiplicity while the tests are corrected, so an interval may
exclude zero where the corrected test does not reach significance — this happens
for POLYSOLVER on WES and for arcasHLA, OptiType and HLA-HD on RNA-seq, and the
corrected test governs the claim in each case. Italic labels are the fitted
integration policies reported in the companion paper; they are shown here
because the multiplicity correction is computed over every comparison conducted,
including theirs.

**Figure 3. A harmonisation defect manufactured homozygous genotypes.**
Left: when a caller could not determine a second allele, harmonisation replaced
the placeholder with a copy of the first, converting a partial call into a
confident homozygous genotype, which is correct only where the subject is truly
homozygous. Right: the share of calls made falsely homozygous among the callers
that actually vote in each assay, counting both mechanisms — a duplicated
placeholder and two high-resolution alleles collapsing to one two-field group.
Whole-genome data is excluded because its inputs are invalid, so no
whole-genome rate appears in either panel; how often the duplication was in fact
correct on each assay is reported in Supplementary S4c, with per-caller counts
in S4.

**Figure 4. Abstaining buys conditional accuracy and pays in coverage.**
Accuracy among called loci against callability, for the abstaining two-thirds
rule and for the always-calling vote, in both assays. The two-thirds rule is
more accurate where it commits, but at a fixed denominator the loci it declines
count against it.

**Figure 5. The panel's own agreement is a calibrated confidence scale.**
Accuracy of the emitted call against the number of panel callers backing it, at
loci where every panel member was callable (223 + 116 + 37 + 12 + 2 = 390 WES;
273 + 29 + 11 + 2 = 315 RNA-seq). Counts are printed beside each point, because
the low-support categories rest on very few loci; the dotted line marks chance
between two competing pairs. Loci where part of the panel was not callable are
excluded here and reported in Supplementary S7. Generated from
`artifacts/plurality_characterisation/support_calibration.tsv`.

## Data and software availability

**Data.** All primary data are public. Exome data are the 1000 Genomes phase 3
exome alignments remapped to GRCh38DH (1000 Genomes Project Consortium, 2015);
whole-genome data, used for diagnosis only, are the 30x high-coverage
resequencing of the expanded cohort (Byrska-Bishop *et al.*, 2022);
transcriptome data are Geuvadis (Lappalainen *et al.*, 2013). All were accessed
through the European Nucleotide Archive. Per-sample source URLs and checksums
are recorded in `cohorts/official_1000g_assay_manifest.tsv`. Reference HLA typing is the
published 2014 1000 Genomes HLA panel (Gourraud *et al.*, 2014). NCI-60
expression data are from CellMiner (Reinhold *et al.*, 2019). HPRC assemblies,
used to define the independent validation arm, are from the Human Pangenome
Reference Consortium (Liao *et al.*, 2023). No new sequence data were generated.

**Software.** PanelHLA is a Nextflow DSL2 workflow, released under the MIT
licence. The analysis, audit and freeze code accompanying this manuscript is
dependency-free Python and is covered by an automated test suite and a
verification gate (`scripts/run_local_verification.sh`). Run with `RELEASE=1`,
the gate regenerates the statistical artifacts this manuscript cites and then
audits every claim against them, and it refuses to pass if regeneration was
skipped or run below the release bootstrap. Run without it — the routine
development and continuous-integration path — it audits the committed artifacts
for internal consistency, which is a weaker guarantee and is reported as such:
the truth-joined table carries reference-typing columns and so is not
version-controlled, and regeneration is skipped wherever it is absent.

PanelHLA redistributes no HLA caller: each is obtained and executed separately, as a
container pulled at run time or as a local checkout, and remains under its own
licence. Because the callers run as separate processes rather than being linked, a
copyleft licence on a caller does not extend to PanelHLA. Several callers do
restrict commercial use, so an assembled panel is in practice for research use even
though the workflow itself is permissively licensed. Per-caller terms are recorded
in `THIRD_PARTY_NOTICES.md`.

**Reproduction bundle.** The release bundle contains the workflow, the analysis
package, compact fixtures, cohort and fold assignments, the frozen per-caller
predictions, the truth-join manifest, per-file checksums, the statistical
outputs, and the scripts that generate every figure and table in this paper and
its supplement. Figures are regenerated from the statistical artifacts by
`scripts/generate_figures.py`; no value in any figure is transcribed by hand.

**Provenance.** Predictions are checksummed before truth is joined, and truth is
joined exactly once. Freeze manifests record POSIX-relative paths and a content
hash that excludes build time and absolute root, so the same source tree yields
the same content identity on any platform.

The work is split across two repositories, both under the MIT licence. The
PanelHLA workflow — the Nextflow pipeline that runs the callers — is at
`https://github.com/uoozcan/panelhla`. The analysis, audit and freeze code
accompanying this manuscript is a separate repository,
`https://github.com/uoozcan/PanelHLA-paper`; every path cited in this paper
(`scripts/`, `artifacts/`, `decisions/`, `provenance/`, `cohorts/`,
`result_registry.tsv`) resolves inside that second repository, not the first.

TO CONFIRM — the tagged release and commit for each repository, to be fixed at
submission so that every path and value cited here resolves to one immutable
state.

TO CONFIRM — the archived release DOI and the container image digests for each
caller. Both are assigned at the tagged release and are deliberately left
unresolved here rather than stated speculatively.

## Author contributions

TO CONFIRM — CRediT roles per author (conceptualisation, methodology, software,
validation, formal analysis, investigation, data curation, writing, supervision,
funding acquisition).

## Ethics

This study analyses only publicly available, consented human genomic data: the
1000 Genomes Project exome and whole-genome collections (1000 Genomes Project
Consortium, 2015; Byrska-Bishop *et al.*, 2022), the Geuvadis transcriptome
collection (Lappalainen *et al.*, 2013), and published reference HLA typing for those same
samples. No new human samples were collected and no identifiable participant
data were accessed.

TO CONFIRM — whether the host institution requires an ethics statement or
approval number for secondary analysis of these public resources, and if so,
which.

## Funding

TO CONFIRM — funders and grant numbers for each supported author.

## Competing interests

TO CONFIRM — declare any competing interests, or state that the authors declare
none.

## Acknowledgements

TO CONFIRM — computational resources (CSC, the Finnish IT Center for Science),
and any contributors not meeting authorship criteria.

## References

Adams, S.D. *et al.* (2005). Ambiguous allele combinations in HLA Class I and II
sequence-based typing: when precise nucleotide sequencing leads to imprecise
allele identification. *Journal of Translational Medicine*, 3, 30.

Aguiar, V.R.C. *et al.* (2019). Expression estimation and eQTL mapping for HLA
genes with a personalized pipeline. *PLoS Genetics*, 15, e1008091.

Boegel, S. *et al.* (2012). HLA typing from RNA-seq sequence reads. *Genome
Medicine*, 4, 102.

1000 Genomes Project Consortium (2015). A global reference for human genetic
variation. *Nature*, 526, 68-74.

Byrska-Bishop, M. *et al.* (2022). High-coverage whole-genome sequencing of the
expanded 1000 Genomes Project cohort including 602 trios. *Cell*, 185,
3426-3440.e19.

Chin, C.S. *et al.* (2020). A diploid assembly-based benchmark for variants in
the major histocompatibility complex. *Nature Communications*, 11, 4794.

Chung, W.H. *et al.* (2004). Medical genetics: a marker for Stevens-Johnson
syndrome. *Nature*, 428, 486.

Di Tommaso, P. *et al.* (2017). Nextflow enables reproducible computational
workflows. *Nature Biotechnology*, 35, 316-319.

Gourraud, P.A. *et al.* (2014). HLA diversity in the 1000 genomes dataset. *PLoS
ONE*, 9, e97282.

Hickey, G. *et al.* (2024). Pangenome graph construction from genome alignments
with Minigraph-Cactus. *Nature Biotechnology*, 42, 663-673.

Holm, S. (1979). A simple sequentially rejective multiple test procedure.
*Scandinavian Journal of Statistics*, 6, 65-70.

Hurley, C.K. *et al.* (2020). Common, intermediate and well-documented HLA
alleles in world populations: CIWD version 3.0.0. *HLA*, 95, 516-531.

Kawaguchi, S. *et al.* (2017). HLA-HD: an accurate HLA typing algorithm for
next-generation sequencing data. *Human Mutation*, 38, 788-797.

Kiyotani, K., Mai, T.H. & Nakamura, Y. (2017). Comparison of exome-based HLA
class I genotyping tools: identification of platform-specific genotyping errors.
*Journal of Human Genetics*, 62, 397-405.

Lee, H. & Kingsford, C. (2018). Kourami: graph-guided assembly for novel human
leukocyte antigen allele discovery. *Genome Biology*, 19, 16.

Lappalainen, T. *et al.* (2013). Transcriptome and genome sequencing uncovers
functional variation in humans. *Nature*, 501, 506-511.

Liao, W.W. *et al.* (2023). A draft human pangenome reference. *Nature*, 617,
312-324.

Llamas, B. *et al.* (2019). A strategy for building and using a human reference
pangenome. *F1000Research*, 8, 1751.

Mallal, S. *et al.* (2008). HLA-B*5701 screening for hypersensitivity to
abacavir. *New England Journal of Medicine*, 358, 568-579.

Matzaraki, V. *et al.* (2017). The MHC locus and genetic susceptibility to
autoimmune and infectious diseases. *Genome Biology*, 18, 76.

Mishima, H. *et al.* (2019). A practical guide for the evaluation of
next-generation sequencing-based HLA typing. *Human Immunology*, 80, 891-898.

Orenbuch, R. *et al.* (2019). arcasHLA: high-resolution HLA typing from RNAseq.
*Bioinformatics*, 36, 33-40.

Parham, P. & Brodsky, F.M. (1981). Partial purification and some properties of
BB7.2, a cytotoxic monoclonal antibody with specificity for HLA-A2 and a variant
of HLA-A28. *Human Immunology*, 3, 277-299.

Petersdorf, E.W. *et al.* (2007). Major histocompatibility complex variation and
outcomes in hematopoietic cell transplantation. *Immunological Reviews*, 214,
229-244.

Prodanov, T. *et al.* (2025). Locityper enables targeted genotyping of complex
polymorphic genes. *Nature Genetics*, 57, 2901-2908.

Reinhold, W.C. *et al.* (2019). RNA sequencing of the NCI-60: integration into
CellMiner and CellMiner CDB. *Cancer Research*, 79, 3514-3524.

Montgomery, S.B. *et al.* (2010). Transcriptome genetics using second generation
sequencing in a Caucasian population. *Nature*, 464, 773-777.

Robinson, J. *et al.* (2020). IPD-IMGT/HLA database. *Nucleic Acids Research*,
48, D948-D955.

Schumacher, T.N. & Schreiber, R.D. (2015). Neoantigens in cancer immunotherapy.
*Science*, 348, 69-74.

Shukla, S.A. *et al.* (2015). Comprehensive analysis of cancer-associated
somatic mutations in class I HLA genes. *Nature Biotechnology*, 33, 1152-1158.

Song, L. *et al.* (2023). Efficient and accurate KIR and HLA genotyping with
massively parallel sequencing data. *Genome Research*, 33, 923-931.

Szolek, A. *et al.* (2014). OptiType: precision HLA typing from next-generation
sequencing data. *Bioinformatics*, 30, 3310-3316.

Trowsdale, J. & Knight, J.C. (2013). Major histocompatibility complex genomics
and human disease. *Annual Review of Genomics and Human Genetics*, 14, 301-323.

Wang, S. *et al.* (2023). SpecHLA enables full-resolution HLA typing from
sequencing data. *Cell Reports Methods*, 3, 100589.

Zhou, Y. *et al.* (2024). Full-resolution HLA and KIR gene annotations for human
genome assemblies. *Genome Research*, 34, 1931-1941.
