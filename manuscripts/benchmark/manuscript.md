# An auditable plurality vote for HLA class I genotyping from exome and RNA sequencing: a development benchmark

**Running title:** Consensus HLA genotyping benchmark

## Abstract

HLA class I typing from short reads depends on the caller, assay and reference database; voting is proposed when the best caller is unknown. We evaluated ChampHLA-Consensus, an equal-weight plurality vote over five exome and four RNA-seq callers, made primary after a fitted rule failed to outperform it on these data. In 1000 Genomes and Geuvadis subjects with one recorded 2014 reference genotype, the vote agreed with it at 143/153 exome loci (63 subjects) and 113/118 RNA-seq loci (51 subjects), one locus above the strongest caller in each assay. They differed at three exome loci and one RNA-seq locus, too few to compare. After multiplicity correction the vote exceeded HLA-HD and T1K in exome data and T1K in RNA-seq; a deployment defect affected one RNA-seq caller. All 15 vote errors, at 10 loci, fell where a re-typing of the same exomes reports the 2014 type as incorrect; laboratory typing, checked post hoc and only there, gives the vote's type at nine. With corrected values there, HLA-HD scored 118/118 and the vote 117/118 in RNA-seq. Retained loci came mainly from two populations. These development results establish neither equivalence nor clinical validity; testing on unseen subjects is incomplete.

## Keywords

HLA typing; consensus genotyping; benchmarking; immunogenomics; whole-exome sequencing; RNA sequencing

## Introduction

The human leukocyte antigen (HLA) genes of the major histocompatibility complex (MHC) on chromosome 6p21.3 form one of the most polymorphic regions of the human genome [1].
The classical class I genes studied here, HLA-A, HLA-B and HLA-C, present intracellular peptides to CD8-positive cytotoxic T cells.
These genes are the main route by which adaptive immunity surveys cells for infection, malignant transformation and, after transplantation, non-self antigens.

HLA typing errors have consequences.
In unrelated-donor haematopoietic cell transplantation, a single allele mismatch at HLA-A, -B, -C or -DRB1 is associated with higher mortality [2]. Matching lowers the risks of graft failure and graft-versus-host disease [3].
HLA-B\*57:01 predicts abacavir hypersensitivity [4], and HLA-B\*15:02 is associated with carbamazepine-induced Stevens–Johnson syndrome in Han Chinese patients [5].
HLA genotype determines which tumour neoantigens can be presented, so typing errors propagate into vaccine and T-cell receptor therapy design [6]. The region also carries many of the strongest known associations with autoimmune disease [7].

Typing these genes from short whole-exome sequencing (WES), whole-genome sequencing (WGS) or RNA sequencing (RNA-seq) reads is difficult.
The genes are highly diverse. We used release 3.65.0 of the IPD-IMGT/HLA database (Immuno Polymorphism Database–ImMunoGeneTics HLA) [8]. It contains 45,421 HLA allele designations in the allele list (46,652 entries when MICA, MICB, TAP1, TAP2 and HFE are included).
Homologous loci make it difficult to assign short reads uniquely.
RNA-seq samples expressed rather than genomic copies, so a weakly expressed allele can be missed. Expression estimation is itself sensitive to polymorphism-aware mapping [9].

The callers evaluated here use different evidence.
OptiType chooses the allele pair that best explains read support by integer linear programming [10]; HLA-HD scores alignments against an allele dictionary [11]. arcasHLA uses transcript abundance in RNA-seq [12], POLYSOLVER adds population allele frequencies as a prior [13] (run here with the frequency prior off), and T1K uses expectation maximization over allele abundance [14].
SpecHLA combines alignment with local assembly and phasing [15].
Callers that share mapping assumptions may make correlated errors, limiting what a vote can correct. We measured that dependence directly.
Running several callers requires different dependencies, databases and inputs: FASTQ reads or alignments in BAM or its compressed form, CRAM. Their allele formats also differ.
Outside a few public resources such as the 1000 Genomes Project [16, 17], sequencing data with reference HLA typing are rare, so accuracy on a new cohort usually cannot be measured.
ChampHLA runs the callers for each assay in one Nextflow workflow [18], converts their outputs to a common two-field representation and applies a declared consensus rule (Methods).

Benchmarks show that caller rankings depend on the assay, gene and dataset [19] and reveal typing-tool-specific errors [20]. The best caller for a new dataset is therefore unknown.
Several studies have evaluated consensus.
Larjo *et al.* [21] found that ensemble prediction could improve accuracy. Combining the three best tools outperformed any single tool on The Cancer Genome Atlas data [22], although the labels there came from agreement among the evaluated tools.
Lee *et al.* [23] proposed accepting a consensus type when at least six of eight tools agreed and otherwise retyping by PCR sequence-based typing.
Claeys *et al.* [19] applied a majority vote, with ties broken toward the best tool, to 1000 Genomes exome and Geuvadis RNA-seq data.
Their four-tool WES class I vote, with the tool set selected against the same reference typing, reached 99.0% against 98.0% for OptiType alone, with little gain in RNA-seq.
Among workflows, consHLA combines HLA-HD results across germline and tumour sequencing of one patient [24], and nf-hlamajority implements majority class I typing from DNA in Nextflow [25].
SweHLA combined computational typings and compared allele frequencies with 252 laboratory-typed Swedes to build a population resource [26].

Evaluation choices have received less attention. Two choices can inflate a vote's apparent performance.
The first completes every single reported allele into a homozygous pair, although for some callers a missing second allele marks a failed call.
The second selects one allele from an ambiguous laboratory-typing string, which turns an unresolved reference typing into an exact label.
We completed a single allele only where the caller's output format declared homozygosity. We excluded ambiguous reference typing from the exact endpoint and scored it separately.

We asked how ChampHLA-Consensus, a deterministic equal-weight genotype vote, performs within one assay and a named caller panel when failed calls, reference ambiguity and unavailable provenance remain visible.
We deliberately made the vote without fitted parameters primary. An earlier internal plan named a fitted rule as primary and required it to outperform; it did not, and we then made the vote primary.
With a single labelled development resource, apparent gains of fitted policies cannot be separated from fitting to that resource. We retained them only as exploratory comparators (Supplementary S13).
A rule without fitted parameters can instead be stated completely, audited from each vote to the reported genotype and applied unchanged to new data.
We ran the evaluated callers through ChampHLA. A separate cohort with no overlapping subjects has been specified for a later confirmatory test; its analysis plan is not yet publicly deposited, and no result is reported here.

## Methods

### Study design and data

This is a method-developer evaluation: we wrote the workflow, parsers, primary rule and fitted comparators. We ran callers on 1000 Genomes WES and Geuvadis RNA-seq data [16, 27] with the ChampHLA workflow in October 2026. The October caller run was made after results from archived outputs of these callers were known. This retrospective benchmark evaluates the caller outputs produced by that run. The prediction tables contain no reference genotypes; reference typing is used only for evaluation.
A *subject* is one individual in these public collections of consented population-genomics donors; the development set contains no clinical samples.
A *locus* is one subject–gene pair within one assay.
The workflow version, input files, software images and outputs are recorded with file checksums so that the analysis can be reproduced (Supplementary S10).
Archived outputs are used only in supplementary comparisons and exploratory analyses (Supplementary S10 and S12). Their executables, container images and launch parameters were not preserved.
The reproducible analysis covers allele normalization, reference-genotype selection, prediction scoring, statistical comparisons, and preparation of tables and figures.
We call these data the *development set* because we selected the primary reporting rule after inspecting their results. Development performance is post hoc, not prospective validation.

The analysed sample list contained 130 WES subjects (390 subject–gene loci) and 106 RNA-seq subjects (318 loci), 105 of whom also occurred in the WES roster. The analysed subjects are a convenience roster inherited from an earlier development analysis. The rule that selected them could not be reconstructed, so we cannot exclude selection related to outcome. Eighteen subjects in each assay had no record in the 2014 table. Capture kit, read length, sequencing depth and original preprocessing metadata were unavailable.
We analysed the assays separately; they are not independent replications.
Exact-reference filtering left 63 WES subjects and 51 RNA-seq subjects, 50 present in both sets. Subjects were the clusters used for inference. By the public 1000 Genomes pedigree file, no retained subjects were first-, second- or third-degree relatives, and clustering by family identifier (46 WES and 40 RNA-seq clusters) changed no sign-flip verdict (post hoc; Supplementary S3).
[RESULT:DEV_RELATED_PAIRS_WES]
[RESULT:DEV_RELATED_PAIRS_RNASEQ]
[RESULT:DEV_FAMILY_CLUSTERED_WES_VERDICTS_CHANGED]
[RESULT:DEV_FAMILY_CLUSTERED_RNASEQ_VERDICTS_CHANGED]

We checked sample identity without using reference genotypes.
Every input had to appear in the official 1000 Genomes and Geuvadis assay manifest, and all study inputs appeared in it.
For the 105 subjects in both assays, we compared WES and RNA-seq consensus genotypes at every gene called in both: 101 subjects shared all six alleles and four shared five.
We added this check after the development results were known and first applied it to archived outputs.
The archived NA07000 RNA-seq input shared one of six alleles with the subject's WES input and was absent from the manifest. We withheld it as a provenance failure; the analysed sample list excludes it. The subject's WES input was in the manifest and was retained.
In the archived outputs, the withheld RNA-seq input's two exact-endpoint loci were both consensus errors, and including them gave 113/120 (Supplementary S7, analysis-choice summary).
[RESULT:DEV_IDENTITY_NOT_IN_ASSAY_MANIFEST]
[RESULT:DEV_IDENTITY_SHARED_6_OF_6]
[RESULT:DEV_IDENTITY_SHARED_5_OF_6]
[RESULT:DEV_IDENTITY_SHARED_1_OF_6]
[RESULT:DEV_IDENTITY_WITH_WITHHELD_RNASEQ_SIMPLEPLURALITYLEX]

One exploratory application lies outside the primary analysis and supports no accuracy, external-validation or abstract claim (Supplementary S9).
The NCI-60 cancer cell lines have published sequence-based class I typing [28]. This application is being processed with ChampHLA, the development panels and a parser that retains only unambiguous reference genotypes (Supplementary S9).

### The ChampHLA workflow

ChampHLA runs each caller in an assay's panel (Table 1) as an independent Nextflow process [18], in a container except for SpecHLA, which ran from a native installation in this study (Supplementary S10). It parses outputs into unordered two-field genotypes and combines callers at each sample and gene (Figure 1A).
For DNA BAM or CRAM input, reads in the chromosome 6 MHC window and on HLA-allele and alternate-haplotype contigs are first realigned to chromosome 6 with BWA-MEM [29], so that every caller sees both haplotypes (Supplementary S11.1).
Under `-profile paper`, the consensus step implements ChampHLA-Consensus. A workflow test requires the same rule output on archived calls at all 708 development loci (Supplementary S11.2). The default calibrated weighting was not evaluated.
We computed all development results by applying the paper-repository rule to normalized caller tables from the ChampHLA runs.

**Table 1. HLA callers evaluated in the WES and RNA-seq benchmark.**

| Caller | Evidence and inference | WES panel | RNA-seq panel | Earliest consistent IPD-IMGT/HLA release (lower bound) | Version and settings in the study runs |
|---|---|:---:|:---:|---|---|
| HLA-HD | Alignment scored against an allele dictionary | Yes | Yes | 3.15.0 | 1.4.0; `-c 0.95` |
| OptiType | Integer linear programming over allele-pair read support | Yes | Yes | 3.13.1 | Not recorded; DNA mode for WES, RNA mode for RNA-seq |
| POLYSOLVER | Alignment likelihood with population allele frequencies (run here with the frequency prior off) | Yes | No | 3.11.0 | v4; population Unknown |
| SpecHLA | Alignment, local assembly and haplotype phasing | Yes | No | 3.38.0 and 3.51.0 components | 1.0.7, native installation; exon reads only (`-u 1`) |
| T1K | Allele abundance by expectation maximization | Yes | Yes | 3.63.0 | v1.0.9-r251; genomic index (`hla_dna.fa`) in both assays |
| arcasHLA | Allele reconstruction from transcript abundance | No | Yes | 3.40.0 (bundled report, not preserved) | Not recorded; `--min_count 75` |

Image digests, database sources and input routes for each caller and assay are in Supplementary Table S10.4.
The fifth column gives the earliest IPD-IMGT/HLA release consistent with each caller's bundled database, a content-derived lower bound (Supplementary S6) that is not necessarily the release used to build the caller.
For example, the POLYSOLVER publication reports IMGT/HLA 3.10, whereas 3.11.0 is the lower bound for the preserved allele list [13].
The arcasHLA value comes from a bundled version report that was not preserved.
The reference typing was interpreted against IMGT/HLA 2.26.0 [17].

### Reference HLA typing and denominator construction

We obtained reference genotypes from the International Genome Sample Resource (IGSR) copy of the 2014 1000 Genomes HLA diversity table [17]. A SHA-256 file checksum verifies that the reference file is identical to the version used for this analysis (Data availability).

This table is laboratory typing, not error-free truth.
Class I loci were typed by locus-specific polymerase chain reaction (PCR) and Sanger sequencing of exons 2 and 3 and interpreted against IMGT/HLA 2.26.0 (July 2009); allele ambiguities were retained, and confirmatory typing was performed for 12 samples [17]. The source also states that several HapMap and CEPH samples had been typed previously and that those types were otherwise included; it does not mark which records these are, and most retained loci come from those collections.
Such typing cannot separate alleles that differ only outside exons 2 and 3, and a 2009 release cannot name alleles described later.
Independent typings of the same samples do not always agree: of 263 1000 Genomes samples typed in more than one study, 221 (84%) had concordant typings [30].
When 992 of the typed individuals were retyped from exome data, read inspection and new laboratory typing of 21 individuals led the authors to retain 105 results that disagreed with the published types [31].
Agreement with this reference therefore combines caller error with reference error, and the exact endpoint measures agreement with the reference rather than accuracy against the true genotype.

We used that in silico re-typing by Abi-Rached *et al.* [31], obtained from IGSR with a verified checksum, to adjudicate consensus errors.
In it, an asterisk marks a result that disagreed with the previously published type and that its authors kept after verification [31].
Thuesen *et al.* later used these corrections to update the 2014 types in an exome benchmark [32], and Buchkovich *et al.* replaced 38 discordant and two low-resolution Geuvadis allele calls after targeted typing of 34 samples [33].
Because the re-typing derives from the same exome data, and T1K and SpecHLA were evaluated against it in their original publications [14, 15], it can adjudicate a discordance but never replaces the reference.
Its parsing rule, adjudication classes and a sensitivity analysis restricted to loci where both typings agree were recorded on 9 October 2026, before the second typing was compared with predictions or the reference but after the pattern of caller agreement at discordant loci had been seen.
That rule treats an asterisked value as unavailable, so comparing predictions with these corrected values (Results) is post hoc.

Exact scoring requires an exact reference genotype, but the source includes allele-ambiguity strings and duplicate subject records.
We retained a locus for exact scoring only when its reference genotype could be resolved without ambiguity.
We parsed every source row for each subject and gene, excluding a locus from the exact endpoint if any row was ambiguous, invalid or conflicting. A resolved duplicate could not conceal an ambiguous one.
No first-listed or frequency-preferred allele was ever selected.
The audit excluded 237/390 requested WES loci and 200/318 RNA-seq loci, leaving 153 WES loci from 63 subjects and 118 RNA-seq loci from 51 subjects.
We generated and checksummed predictions for all 708 requested loci before any reference genotype was selected (Figure 1C).

To retain information from ambiguous typing, secondary analyses represented the reference as every valid unordered two-field candidate pair. Where a subject–gene pair had more than one reference row, we took the union of their candidates; taking their intersection instead lowered the vote by one locus in each assay (post hoc; Supplementary S1). A prediction was compatible if it matched any allowed pair, making 335 WES and 263 RNA-seq loci evaluable.
Further sensitivities mapped each two-field designation to every compatible official IPD-IMGT/HLA 3.65.0 G group and P group. They test compatibility under a two-field mapping and do not infer exact P- or G-group calls.
Supplementary S1 describes the exclusions by gene, source population, reference-typing state and candidate-pair count.
Populations use the 1000 Genomes codes, among them CEU (Utah residents with Northern and Western European ancestry) and YRI (Yoruba in Ibadan, Nigeria); the others are defined in Supplementary S1.

### Callers and assay-specific panels

We used a separate intended-use panel for each assay (Table 1): HLA-HD, OptiType, POLYSOLVER, SpecHLA and T1K for WES; arcasHLA, HLA-HD, OptiType and T1K for RNA-seq.
The assay-specific panels were chosen from the callers available in the original deployment; the same panels were used throughout the comparisons.
They reflect the callers deployed in that run rather than an exhaustive modern benchmark.
Only the caller–assay combinations in Table 1 contribute to the benchmark comparisons. Supplementary S6 documents archived outputs outside these panels.

This benchmark is not independent of the callers' own development.
Five of the six panel callers were evaluated in their original publications against reference typings of 1000 Genomes samples, using exome or Geuvadis RNA-seq data from the collections used here [10, 12, 13, 14, 15].
They are OptiType, whose β parameter was chosen by cross-validation on 253 1000 Genomes exome runs, POLYSOLVER, arcasHLA, T1K and SpecHLA.
We could not find in an open-access source which data were used to evaluate HLA-HD [11].
The development subjects may include samples used to develop or evaluate these callers; we could not check this subject by subject. Such overlap can inflate absolute concordance for callers and votes built from them.

We recorded the inputs supplied to each caller.
WES inputs are GRCh38DH exome alignments (the GRCh38 reference with decoy and HLA allele sequences). The workflow realigns reads on HLA-allele and alternate-haplotype contigs to primary chromosome 6 before DNA callers run. RNA-seq inputs are GRCh37 Geuvadis alignments.
Each sample's input checksums, container digests, workflow files and results are recorded (Supplementary S10).
In both assays, every T1K task used the index built from genomic sequences, not the coding-sequence index built beside it (Table 1; Supplementary S10).
All RNA-seq inputs were paired-end with a median read length of 75 bp; WES inputs had a median read length of 100 bp (Supplementary Table S10.5).
[RESULT:DEV_INPUT_RNASEQ_READ_LENGTH]
[RESULT:DEV_INPUT_WES_READ_LENGTH]
[RESULT:DEV_DEPLOYMENT_WES_T1K_DNA_INDEX_RUNS]
[RESULT:DEV_DEPLOYMENT_RNASEQ_T1K_DNA_INDEX_RUNS]
Normalization checks allele syntax and reduces identifiers to two numeric fields. The collector records whether an allele is a current IPD-IMGT/HLA 3.65.0 designation, a group designation, or deleted or renamed. It does not rename calls, with one exception: a SpecHLA C\*15:05:08 became C\*15:152 at one WES cell, which did not affect the vote. Results are syntax-normalized, not database-harmonized.
Native search databases differ in vintage (Table 1; Supplementary S6), so algorithm, database and deployment effects remain inseparable. For the archived outputs, not even the route by which reads reached each caller was recorded.

### Allele normalization and call states

HLA alleles are named by gene and colon-separated fields, as in HLA-A\*02:01:01 [34]. The first field gives the allele group, often corresponding to a serological antigen; the first two fields identify the protein sequence, which is the two-field resolution used here. Later fields record synonymous and non-coding differences. A suffix marks altered expression; N marks a null allele, which is not expressed. Exons 2 and 3 encode the peptide-binding groove of class I molecules. A P group collects alleles with the same protein sequence there, and a G group alleles with the same nucleotide sequence over those exons [34].
In this paper a *locus* is one subject–gene pair in one assay, not a genomic position, and a *homozygous reference locus* is one whose reference typing gives the same two-field allele twice. Unless a genome build is named, *reference* means the HLA typing table. *Archived outputs* are the caller outputs of the original deployment; the *ChampHLA runs* (study runs) are the caller runs of 13–25 October 2026 that the results score.

We assigned every output row a call state before counting votes because callers report incomplete or uncertain results differently.
Alleles required a valid HLA gene and at least two numeric fields. We rejected gene mismatches, malformed alleles and unresolved slash-delimited ambiguities, retaining higher fields and suffix tokens as metadata.
N, L, S and Q expression suffixes and P/G group terminology follow HLA nomenclature [34]; C and A were retained as opaque suffix metadata rather than interpreted by this analysis.
The primary endpoint used the first two numeric fields, and diploid pairs were sorted before comparison.

Each requested caller cell has exactly one state: complete, partial, missing, ambiguous, invalid, failed or absent.
*Absent* means the collected table has no row for that sample, gene and caller, distinct from an executed caller returning a missing or failed result. Empty strings, `-`, `.`, `NA` and `NOTTYPED` are recognized centrally as placeholders.
A caller is *callable* at a locus when its row is complete and reports an unordered two-field genotype. Missing, partial and invalid rows do not vote.

A row with one resolved allele and no second, a *singleton call*, is partial and abstains unless the caller's own output format declares homozygosity.
HLA-HD writes a hyphen for the second allele of a homozygous call and "Not typed" for a failed call [35]. arcasHLA releases before 0.4.0 report homozygotes as a single allele [36].
These rows are completed into homozygous pairs.
The arcasHLA container used here holds arcasHLA 0.2.0, which reports homozygotes this way. Supplementary S10 documents the limitations of archived outputs.
The T1K parser records `num_diff_alleles` and quality fields distinguishing native homozygotes from missing alleles. It ignores alleles with non-positive quality and does not promote secondary alleles into the genotype. We complete T1K's declared homozygotes; other single-allele rows abstain.
At exact-endpoint loci, 27 of 30 single-allele WES rows and 30 of 34 RNA-seq rows lay at homozygous reference genotypes. Exceptions were three T1K WES rows (one declaration, two partial) and four arcasHLA RNA-seq declarations.
We finalized this handling after inspecting development results and report abstain-all singleton scoring alongside it (Supplementary S2).
[RESULT:DEV_SINGLE_ALLELE_WES_REFERENCE_HOMOZYGOUS]
[RESULT:DEV_SINGLE_ALLELE_RNASEQ_REFERENCE_HOMOZYGOUS]

### Primary and secondary consensus rules

At each locus, every callable intended-use caller casts one vote for its unordered two-field genotype, and ChampHLA-Consensus reports the genotype with the most votes (Figure 1B).
The rule is a plurality, not a majority: the selected genotype need not receive more than half of the votes.
Ties go to the first-sorting pair when sorted allele names are compared as character strings (A\*02:101 precedes A\*02:11).
If no caller is callable, the method abstains.
The rule uses no reference genotypes, allele frequencies or fitted weights.

Let *x* denote one subject–gene locus within an assay, *C*ₓ the callers with a complete two-field genotype at that locus, and *G*₍c,x₎ the unordered genotype reported by caller *c*. For each candidate genotype *g*, the vote count is

$$
V_x(g) = \sum_{c \in C_x}{\mathbf{1}[G_{c,x}=g]}
$$

Here, the indicator is one when the caller reports g and zero otherwise. The reported genotype is the alphabetically first genotype among those with the largest vote count:

$$
\hat{G}_x = \operatorname{lexmin}\{g:V_x(g)=\max_{h \in \mathcal{G}_x}{V_x(h)}\}
$$

The candidate set contains the genotypes reported by the callable callers. Alleles within each pair are sorted before voting. If no caller has a complete genotype, the method returns no call. Alphabetic ordering is a deterministic tie-break; it does not use allele frequencies or biological evidence.

**Algorithm 1. Equal-weight consensus for one subject–gene locus.**

```text
Input: caller outputs for one locus and its assay-specific panel
votes = empty genotype-to-count map
for each caller in the panel:
    normalize the reported allele pair to two fields
    if the pair is complete and valid:
        sort the two alleles to form an unordered genotype
        add one vote to that genotype
if votes is empty:
    return NO CALL
largest_count = the largest count in votes
winners = all genotypes with count equal to largest_count
report the alphabetically first genotype in winners
```

The normalization step applies the caller-specific homozygote rules described above; it does not complete an otherwise partial call.


Two descriptive rules use the same votes. Strict majority requires more than half of callable votes for the leading pair; two-thirds consensus requires at least two thirds.
Each caller was also evaluated on its own.
Six fitted policies were exploratory: the best single caller chosen by nested cross-validation (CV), four champion–challenger variants and an L2-regularized logistic meta-consensus (Supplementary S7.1).
Their development scores cannot establish generalization, because construction or selection and evaluation share the development resource.

### Endpoints and statistical analysis

The primary endpoint was exact unordered diploid concordance at two-field resolution. Both predicted alleles had to match both reference alleles to the first two fields, in either order; matching one allele earned no credit.
The denominator is fixed, so an absent or non-callable prediction counts as incorrect and a method cannot improve its score by declining difficult loci.
We reported callability separately and always alongside called-only concordance, computed over loci with a complete diploid prediction.

For *N* loci with eligible reference genotypes, callability and exact genotype concordance are

$$
\operatorname{Callability} = \frac{1}{N}\sum_{x=1}^{N}{\mathbf{1}[\hat{G}_x \ne \varnothing]}
$$

$$
\operatorname{Concordance} = \frac{1}{N}\sum_{x=1}^{N}{\mathbf{1}[\hat{G}_x = G_x^{\ast}]}
$$

An asterisk denotes the reference genotype. A no-call contributes zero to concordance and remains in the denominator. Called-only concordance uses only loci with a complete prediction and is reported as a secondary descriptive measure.

Allele concordance counted the multiset intersection between predicted and reference alleles over twice the genotype denominator.

We described concordance, allele concordance, callability and called-only concordance with subject-cluster percentile bootstrap intervals from 100,000 subject resamples, base seed 20260831 and a deterministic SHA-256-derived seed per method.
Each resample drew subjects with replacement and kept every evaluable locus, with both alleles, of each drawn subject, so the estimates weight loci rather than subjects equally.
Estimates of 0% or 100%, where a percentile bootstrap collapses to a point, use the exact Clopper–Pearson interval [37].
Stratified results use exact Clopper–Pearson intervals, as stated with each table.

For each comparator, the paired effect is ChampHLA-Consensus minus the comparator, in percentage points.
We determined significance with an exact two-sided subject sign-flip test of the locus-weighted difference. We enumerated all sign assignments for at most 20 subjects with nonzero aggregates, otherwise using 1,000,000 seeded assignments and a plus-one correction.
We applied Holm correction [38] separately within each assay's descriptive-comparator and exploratory fitted-policy families. Zero-discordance comparisons were displayed but excluded from multiplicity. The families were fixed on 28 September 2026, after development results had been seen, and *p* values are conditional on the post hoc choice of the vote as the reference arm.
A comparison is called significant when its sign-flip Holm-adjusted *p*<0.05.
Because the test is discrete, a comparison in which few subjects differ cannot reach *p*<0.05 at any effect size (Supplementary S3).

Intervals for the paired differences are descriptive.
They use a CR1 (finite-cluster-corrected cluster-robust) subject-clustered standard error, a Student *t* reference distribution with `G−1` degrees of freedom and Bonferroni adjustment over the same family.
Cluster-robust inference is unreliable with few clusters [39]. Only discordant subjects contribute to a paired contrast, so intervals may be too narrow when few subjects differ.Results stratified by vote support are descriptive proportions, not probability calibration, and no external validation test was performed.

### Retrospective design and sensitivity analyses

The primary reporting rule and several analysis choices were selected after examining development results. The comparisons are therefore retrospective and exploratory, even though reference genotypes were excluded when generating the predictions used for evaluation. These procedures do not make the development results confirmatory. Supplementary S14 explains how changes to reference handling, missing calls and inference affect interpretation.

The confirmatory extension uses a separate cohort with no overlapping subjects and an analysis plan written before predictions are compared with reference genotypes. The plan is not yet publicly deposited. Processing is paused with about 20 samples complete, and no comparison with reference genotypes has been made. The separate NCI-60 application is described in Supplementary S9.

### Software and reproducibility

We computed results using Python 3.11.15, NumPy 1.26.4, SciPy 1.14.1 and Matplotlib 3.9.2 [40, 41, 42]. The software environment of the archived caller run was not recorded.
We ran the workflow on the Roihu cluster of CSC – IT Center for Science (CSC) with Nextflow 25.10.2 [18], Apptainer (formerly Singularity) [43], SAMtools 1.21 [44] and BWA 0.7.19 [29].
Its caller images are specified by SHA-256 in `configs/caller_resources_v2.json`. Under Singularity or Apptainer, the workflow stops before any task runs if an image present on disk differs from the checksum in the workflow repository's image list. The check does not cover Docker or the natively installed SpecHLA code used in this study (Supplementary S10).
Inputs, reference genotypes, predictions and outputs carry SHA-256 identities. Prediction generation rejects any input table containing reference-genotype columns, keeping prediction and evaluation data separate.
Figures read tab-separated value (TSV) artifacts. Supplementary analyses are accompanied by their documentation.
WGS outputs from the original caller run failed input-validity checks (Limitations); they are quarantined, and no quantitative WGS performance is reported.



### Ethics and data reuse

The primary benchmark uses public 1000 Genomes and Geuvadis sequencing data and published HLA typing. No new participants were recruited and no new samples were collected. The development subjects were consented population-genomics donors rather than clinical patients.


## Results

### Exact reference genotypes were available for a selected subset of loci

Only 153/390 requested WES loci and 118/318 requested RNA-seq loci had a unique two-field genotype after resolving the checksum-verified reference typing without selecting an allele from an ambiguous result.
The remaining WES loci were ambiguous (182), invalid (one) or absent from the source (54); for RNA-seq the corresponding counts were 145, one and 54.
The retained WES set contained 50 HLA-A, 52 HLA-B and 51 HLA-C loci, and the RNA-seq set 38, 40 and 40.
Checking every duplicate source record removed ten assay-loci accepted earlier because a resolved duplicate had concealed an ambiguous one.
The earlier 390- and 321-locus denominators, which selected representatives from ambiguous typing strings, are therefore invalid for an exact two-field endpoint.

Retention depended strongly on population.
After pooling genes, 84.7% of CEU (CEPH) and 92.8% of YRI WES source-present loci were retained, compared with 3.9% of FIN, 3.9% of GBR and 8.3% of PUR loci.
The exact endpoint therefore represents a selected subset of the data (Figure 1D; Supplementary S1).

### The vote could not be distinguished from the strongest caller in small comparisons

ChampHLA-Consensus called every retained locus (153/153 WES, 118/118 RNA-seq).
Its exact genotype concordance was 143/153 (93.5%; subject-clustered 95% confidence interval [CI] 89.7–96.8%) for WES and 113/118 (95.8%; 92.1–99.1%) for RNA-seq. Allele concordance was 296/306 (96.7%; 94.9–98.4%) and 231/236 (97.9%; 96.1–99.6%), respectively (Figure 2; Table 2).
[RESULT:DEV_CORRECTED_WES_SIMPLEPLURALITYLEX]
[RESULT:DEV_CORRECTED_RNASEQ_SIMPLEPLURALITYLEX]

The strongest single caller in each assay scored slightly lower.
OptiType was the strongest WES caller, with 142/153 correct genotypes, a paired difference of 0.65 points (Bonferroni-adjusted cluster-*t* 95% CI −3.44 to 4.74; sign-flip Holm *p*=1). In archived outputs from an earlier, unrecorded deployment, POLYSOLVER had led WES callers at 143/153; in this run, which adds the read rescue, it scored 138/153 (post hoc; Supplementary S10).
In RNA-seq HLA-HD and OptiType tied as the strongest callers with 112/118 each, one locus below the vote (0.85 points; −1.47 to 3.16; sign-flip Holm *p*=1 for both).
These intervals permit benefit or harm and do not establish equivalence or non-inferiority (Figure 3).
[RESULT:DEV_CORRECTED_WES_CALLER_OPTITYPE]
[RESULT:DEV_ARCHIVED_WES_CALLER_POLYSOLVER]
[RESULT:DEV_CORRECTED_WES_CALLER_POLYSOLVER]
[RESULT:DEV_CORRECTED_RNASEQ_CALLER_HLA_HD]
[RESULT:DEV_CORRECTED_RNASEQ_CALLER_OPTITYPE]
[RESULT:DEV_PAIRED_WES_CALLER_OPTITYPE]
[RESULT:DEV_PAIRED_RNASEQ_CALLER_HLA_HD]
[RESULT:DEV_PAIRED_RNASEQ_CALLER_OPTITYPE]

Neither exact sign-flip comparison could have detected a difference.
Only two WES subjects differed in correctness between ChampHLA-Consensus and OptiType, and only one RNA-seq subject differed between the vote and either strongest caller. The exact sign-flip test therefore could not reach *p*<0.05 at any effect size.
In these comparison families, a significant difference with no losses would have required at least nine WES subjects (5.88 points) or eight RNA-seq subjects (6.78 points) to favour one method (Supplementary S3).[RESULT:DEV_DETECTABILITY_WES_CALLER_OPTITYPE]
[RESULT:DEV_DETECTABILITY_RNASEQ_CALLER_HLA_HD]
[RESULT:DEV_DETECTABILITY_RNASEQ_CALLER_OPTITYPE]

In the ChampHLA runs, every panel caller returned a row for every retained locus.
Supplementary S10 compares these calls with archived outputs and documents differences in caller availability.
[RESULT:DEV_MUTUALLY_AVAILABLE_RNASEQ_HLA_HD]

<!-- BEGIN GENERATED MAIN TABLE -->
**Table 2. Primary and descriptive comparator performance.**

| Assay | Method | Scope | Callable | Exact-reference correct | Loci where both typings agree, correct | P group agrees with the 2014 type | Fixed-denominator concordance, % (95% CI) | Called-only concordance, % (95% CI) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| WES | ChampHLA-Consensus | primary | 153/153 | 143/153 | 143/143 | 148/153 | 93.5 (89.7–96.8) | 93.5 (89.7–96.8) |
| WES | Strict majority | descriptive comparator | 150/153 | 141/153 | 141/143 | 145/153 | 92.2 (88.2–95.9) | 94.0 (90.3–97.3) |
| WES | Two-thirds consensus | descriptive comparator | 144/153 | 136/153 | 136/143 | 139/153 | 88.9 (84.0–93.4) | 94.4 (90.8–97.8) |
| WES | POLYSOLVER | individual caller | 153/153 | 138/153 | 137/143 | 143/153 | 90.2 (85.5–94.6) | 90.2 (85.5–94.6) |
| WES | OptiType | individual caller | 153/153 | 142/153 | 141/143 | 146/153 | 92.8 (88.5–96.7) | 92.8 (88.5–96.7) |
| WES | SpecHLA | individual caller | 153/153 | 134/153 | 131/143 | 136/153 | 87.6 (82.3–92.6) | 87.6 (82.3–92.6) |
| WES | T1K | individual caller | 150/153 | 125/153 | 124/143 | 131/153 | 81.7 (75.6–87.5) | 83.3 (77.7–88.7) |
| WES | HLA-HD | individual caller | 153/153 | 131/153 | 131/143 | 135/153 | 85.6 (79.0–91.6) | 85.6 (79.0–91.6) |
| WES | Best single caller (nested CV) | exploratory fitted; nested CV | 153/153 | 142/153 | 141/143 | 146/153 | 92.8 (88.4–96.7) | 92.8 (88.4–96.7) |
| RNA-seq | ChampHLA-Consensus | primary | 118/118 | 113/118 | 112/112 | 114/118 | 95.8 (92.1–99.1) | 95.8 (92.1–99.1) |
| RNA-seq | Strict majority | descriptive comparator | 110/118 | 106/118 | 106/112 | 107/118 | 89.8 (84.2–94.9) | 96.4 (92.7–99.1) |
| RNA-seq | OptiType | individual caller | 118/118 | 112/118 | 111/112 | 113/118 | 94.9 (91.0–98.3) | 94.9 (91.0–98.3) |
| RNA-seq | T1K | individual caller | 118/118 | 101/118 | 100/112 | 102/118 | 85.6 (79.0–91.7) | 85.6 (79.0–91.7) |
| RNA-seq | HLA-HD | individual caller | 118/118 | 112/118 | 112/112 | 114/118 | 94.9 (91.0–98.3) | 94.9 (91.0–98.3) |
| RNA-seq | arcasHLA | individual caller | 118/118 | 58/118 | 58/112 | 80/118 | 49.2 (40.9–57.1) | 49.2 (40.9–57.1) |
| RNA-seq | Best single caller (nested CV) | exploratory fitted; nested CV | 118/118 | 111/118 | 111/112 | 113/118 | 94.1 (89.9–97.6) | 94.1 (89.9–97.6) |

Concordance uses the fixed denominator; intervals are 95% subject-cluster
percentile bootstrap intervals, or exact Clopper–Pearson intervals for estimates
of 0% or 100%. In the four-caller RNA-seq panel, strict majority and
two-thirds consensus are mathematically identical and therefore appear once.
The arcasHLA row reflects a defective workflow deployment rather than the caller (Limitations).
The both-typings column scores the 2014 type only at loci where the second
typing equals it. This removes all 15 vote errors by construction,
so it is not an accuracy estimate against corrected values.
The P-group column is post hoc: the 2014 typing read exons 2 and 3, so it counts a call
that equals the 2014 type or shares its P groups under a two-field mapping.
<!-- END GENERATED MAIN TABLE -->

### Fitted rules did not exceed the vote, and thresholds trade callability for precision

After Holm correction within the descriptive comparison family, ChampHLA-Consensus had greater concordance than HLA-HD and T1K in WES, and than T1K and arcasHLA in RNA-seq; the arcasHLA comparison (58/118) reflects a defective deployment rather than the caller (Limitations).
Its WES advantage over SpecHLA, 5.88 points (Bonferroni-adjusted cluster-*t* 95% CI −0.91 to 12.67), did not survive correction (sign-flip Holm *p*=0.133).
In WES, stricter vote thresholds reduced callability and fixed-denominator concordance (Table 2; Supplementary Figure S2). In RNA-seq the reduction came from the arcasHLA row: without that caller, a strict majority called all 118 loci and scored 113/118 (post hoc; Supplementary S7).
[RESULT:DEV_LEAVE_ONE_OUT_RNASEQ_ARCASHLA_STRICT]
[RESULT:DEV_PAIRED_WES_CALLER_HLA_HD]
[RESULT:DEV_PAIRED_WES_CALLER_T1K]
[RESULT:DEV_PAIRED_WES_CALLER_SPECHLA]
[RESULT:DEV_PAIRED_RNASEQ_CALLER_ARCASHLA]
[RESULT:DEV_PAIRED_RNASEQ_CALLER_T1K]

The exploratory nested-CV best-caller policy was refitted on the recovered subject folds under the current rules. It scored 142/153 in WES (0.65 points below the vote; −3.25 to 4.56) and 111/118 in RNA-seq (1.69 points below; −1.02 to 4.41; sign-flip Holm *p*=1 and 0.5).
Archived exploratory predictions fitted under different reference labels and call states had scored 99/118 and appeared significantly worse; they are excluded from this comparison (Supplementary S7).
Under the adopted single-allele rule no retained fitted policy exceeded the vote; under abstain-all scoring one scored one locus above it in RNA-seq (113/118 vs 112/118; *p*=1). Their weights came from archived outputs and one policy reproduced the vote at every locus, so this does not test whether a properly fitted rule could help. All share the development resource and lack validation on unseen subjects (Supplementary S2 and S7).
[RESULT:DEV_SINGLETON_ABSTAIN_RNASEQ_METACONSENSUS]
[RESULT:DEV_SINGLETON_ABSTAIN_RNASEQ_SIMPLEPLURALITYLEX]
[RESULT:DEV_SINGLETON_ABSTAIN_PAIRED_RNASEQ_METACONSENSUS]
[RESULT:DEV_CORRECTED_WES_BESTSINGLETOOL_NESTEDCV]
[RESULT:DEV_CORRECTED_RNASEQ_BESTSINGLETOOL_NESTEDCV]
[RESULT:DEV_PAIRED_WES_BESTSINGLETOOL_NESTEDCV]
[RESULT:DEV_PAIRED_RNASEQ_BESTSINGLETOOL_NESTEDCV]
[RESULT:DEV_FROZEN_NESTEDCV_LEGACY_RNASEQ]

### Scoring ambiguous typing left the comparison with the strongest caller unchanged, but rankings depended on which loci were scored

We next scored ambiguous reference typing instead of excluding it.
Set-valued scoring admitted 335 WES and 263 RNA-seq loci with parseable reference typing.
ChampHLA-Consensus was compatible with 321/335 WES candidate sets (95.8%; subject-clustered 95% CI 93.7–97.6%) and 257/263 RNA-seq candidate sets (97.7%; 95.8–99.2%).
Mapping two-field designations to all compatible official IPD-IMGT/HLA 3.65.0 groups gave 324/333 (97.3%; 95.5–98.8%) for WES and 256/261 (98.1%; 96.2–99.6%) for RNA-seq under both the G- and P-group mappings, with two reference loci per assay unresolved for each endpoint.
These compatibility analyses are more permissive than the exact primary endpoint and do not replace it (Supplementary Figure S4).
[RESULT:DEV_AMBIGUITY_COMPATIBLE_TWO_FIELD_WES_SIMPLEPLURALITYLEX]
[RESULT:DEV_AMBIGUITY_COMPATIBLE_TWO_FIELD_RNASEQ_SIMPLEPLURALITYLEX]
[RESULT:DEV_G_COMPATIBLE_UNDER_TWO_FIELD_MAPPING_IPD_3_65_WES_SIMPLEPLURALITYLEX]
[RESULT:DEV_G_COMPATIBLE_UNDER_TWO_FIELD_MAPPING_IPD_3_65_RNASEQ_SIMPLEPLURALITYLEX]
[RESULT:DEV_P_GROUP_COMPATIBLE_UNDER_TWO_FIELD_MAPPING_IPD_3_65_WES_SIMPLEPLURALITYLEX]
[RESULT:DEV_P_GROUP_COMPATIBLE_UNDER_TWO_FIELD_MAPPING_IPD_3_65_RNASEQ_SIMPLEPLURALITYLEX]

Exact-reference filtering changed which loci were scored.
Of the retained loci, 125/153 WES and 105/118 RNA-seq came from the CEU (CEPH) and YRI HapMap samples, against 15/182 and 14/145 of the excluded loci that could be scored for compatibility (Supplementary S1).
On excluded loci ChampHLA-Consensus was compatible with 178/182 WES and 144/145 RNA-seq candidate sets. OptiType led individual callers in both assays (176/182 and 143/145), ahead of POLYSOLVER in WES (168/182) and HLA-HD in RNA-seq (142/145).
Exact-endpoint rankings therefore describe the retained, predominantly CEU and YRI loci. Compatibility on excluded loci is lenient because any of several candidate genotypes counts, but not trivially so: predicting the most common genotype among the other subjects, without reads, was compatible with 4/182 WES and 3/145 RNA-seq candidate sets (post hoc; Supplementary S1).
[RESULT:DEV_TRUTH_SELECTION_PROFILE_WES_RESOLVED_CEU_YRI]
[RESULT:DEV_TRUTH_SELECTION_PROFILE_RNASEQ_RESOLVED_CEU_YRI]
[RESULT:DEV_TRUTH_SELECTION_PROFILE_WES_AMBIGUOUS_CEU_YRI]
[RESULT:DEV_TRUTH_SELECTION_PROFILE_RNASEQ_AMBIGUOUS_CEU_YRI]
[RESULT:DEV_TRUTH_SELECTION_WES_AMBIGUOUS_SIMPLEPLURALITYLEX]
[RESULT:DEV_TRUTH_SELECTION_RNASEQ_AMBIGUOUS_SIMPLEPLURALITYLEX]
[RESULT:DEV_TRUTH_SELECTION_WES_AMBIGUOUS_CALLER_OPTITYPE]
[RESULT:DEV_TRUTH_SELECTION_WES_AMBIGUOUS_CALLER_POLYSOLVER]
[RESULT:DEV_TRUTH_SELECTION_RNASEQ_AMBIGUOUS_CALLER_OPTITYPE]
[RESULT:DEV_TRUTH_SELECTION_RNASEQ_AMBIGUOUS_CALLER_HLA_HD]
[RESULT:DEV_NAIVE_WES_MOST_COMMON_GENOTYPE_EXCLUDED]
[RESULT:DEV_NAIVE_RNASEQ_MOST_COMMON_GENOTYPE_EXCLUDED]

No consensus error was attributable to nomenclature alone.
All 15 ChampHLA-Consensus error loci (10 WES and 5 RNA-seq) were callable discordances. Every reference and predicted allele at those loci was a current IPD-IMGT/HLA 3.65.0 designation.
[RESULT:DEV_NOMENCLATURE_WES_CONSENSUS_ERRORS_CURRENT]
[RESULT:DEV_NOMENCLATURE_RNASEQ_CONSENSUS_ERRORS_CURRENT]

### Shared caller errors were mostly disagreements with the 2014 reference

A vote can correct one caller's error only when the other callers err differently.
Pairwise caller-error φ, the phi coefficient between two callers' per-locus error indicators, ranged from 0.28 to 0.59 in WES and from 0.11 to 0.82 in RNA-seq.
Dependence remained after restricting analysis to mutually callable loci: the corresponding ranges were 0.24–0.59 and 0.11–0.82.
HLA-HD and OptiType had the strongest RNA-seq association (φ=0.82 on the fixed denominator), resting on five joint errors against 0.31 expected if independent (Supplementary S7). Intervals were wide, and the arcasHLA–OptiType and arcasHLA–T1K intervals included zero (Figure 4; Supplementary S7).
[RESULT:DEV_ERROR_PHI_WES_RANGE_ALL]
[RESULT:DEV_ERROR_PHI_RNASEQ_RANGE_ALL]
[RESULT:DEV_ERROR_PHI_WES_RANGE_MUTUALLY_CALLABLE]
[RESULT:DEV_ERROR_PHI_RNASEQ_RANGE_MUTUALLY_CALLABLE]
[RESULT:DEV_ERROR_PHI_RNASEQ_HLA_HD_OPTITYPE]
[RESULT:DEV_ERROR_PHI_RNASEQ_ARCASHLA_OPTITYPE]
[RESULT:DEV_ERROR_PHI_RNASEQ_ARCASHLA_T1K]
[RESULT:DEV_ERROR_COUNTS_RNASEQ_FIXED_DENOMINATOR_HLA_HD_OPTITYPE]

The same dependence bounds what any rule that selects among these outputs could achieve.
Of the vote's 10 WES and 5 RNA-seq errors, an oracle choosing any evaluated caller output could have corrected six WES errors and no RNA-seq error. No panel caller solved four WES and five RNA-seq errors.
A selector restricted to existing outputs therefore had ceilings of 149/153 (97.4%) for WES and 113/118 (95.8%) for RNA-seq; this is an oracle bound, not achievable performance.
[RESULT:DEV_HEADROOM_WES_ORACLE]
[RESULT:DEV_HEADROOM_RNASEQ_ORACLE]
[RESULT:DEV_HEADROOM_WES_RECOVERABLE]
[RESULT:DEV_HEADROOM_RNASEQ_RECOVERABLE]
[RESULT:DEV_HEADROOM_WES_UNREACHABLE]
[RESULT:DEV_HEADROOM_RNASEQ_UNREACHABLE]

All 15 vote errors fall at 10 distinct loci where a published re-typing of the same exomes reports the 2014 type as incorrect.
Under the recorded parsing rule, which treats asterisked values as unavailable, the second typing was unavailable at all 15 consensus errors.
Wherever it was available it agreed with the reference (143/143 WES and 112/112 RNA-seq loci), as the rule entails.
Read post hoc with the asterisk removed, the second typing equals the consensus call at all 15 error loci (10 WES, 5 RNA-seq). Only one other exact-endpoint locus carries an asterisk: an RNA-seq HLA-C locus where the vote matches the 2014 type rather than the corrected value.
At each of the 15, the source reports the 2014 type as incorrect. It records confirmation by targeted sequencing for some allele corrections and by inspection of exome reads for the others [31].
The five RNA-seq errors are the same subject–gene loci as five of the WES errors, with the same consensus genotype, although the two assays use different reads and partly different callers (Supplementary S7).
[RESULT:DEV_ADJUDICATION_WES_UNAVAILABLE]
[RESULT:DEV_ADJUDICATION_RNASEQ_UNAVAILABLE]
[RESULT:DEV_REFERENCE_TYPINGS_AGREE_WES]
[RESULT:DEV_REFERENCE_TYPINGS_AGREE_RNASEQ]
[RESULT:DEV_ADJUDICATION_POSTHOC_WES_FLAGGED_EQUALS_CONSENSUS]
[RESULT:DEV_ADJUDICATION_POSTHOC_RNASEQ_FLAGGED_EQUALS_CONSENSUS]
[RESULT:DEV_ADJUDICATION_POSTHOC_WES_FLAGGED_DISCORDANT]
[RESULT:DEV_ADJUDICATION_POSTHOC_RNASEQ_FLAGGED_DISCORDANT]

Where the two typings agree, the vote and the strongest caller were almost always correct.
On these loci ChampHLA-Consensus was correct at all 143 WES and all 112 RNA-seq loci. OptiType was correct at 141/143 WES and 111/112 RNA-seq loci, and HLA-HD at all 112 RNA-seq loci.
WES caller errors were nearly uncorrelated on this subset (φ −0.08 to 0.31). The vote was correct at all 12 of HLA-HD's errors, all 12 of SpecHLA's and all 19 of T1K's.
In RNA-seq, HLA-HD made no error on this subset, and OptiType's single error was not shared with HLA-HD or T1K.
Laboratory typing not derived from these exomes agrees at the flagged loci: 454 sequencing of exons 2 and 3 [45] gives the vote's type at nine of the ten, and targeted typing [33] gives it at all five RNA-seq loci. The tenth differs only outside exons 2 and 3. At five loci the 2014 type and the vote differ in protein (different P groups); at the other five they are P- and G-compatible under a two-field mapping. We made these checks post hoc and only at loci already flagged, so they cannot show that loci without a flag are correct (Supplementary S7). With corrected values substituted at flagged loci, the vote scored 153/153 in WES, and HLA-HD scored 118/118 and the vote 117/118 in RNA-seq (post hoc and not independent; Supplementary S7). On the subset where the two typings agree, the strongest caller makes almost no errors; shared caller errors do not explain the vote's result.
This exploratory interpretation was made after the data had been seen and rests on few errors. The second typing derives from the same exomes, so the analysis does not estimate independence (Supplementary S7).
[RESULT:DEV_FLAGGED_LOCI_ERLICH_GIVES_VOTE]
[RESULT:DEV_FLAGGED_LOCI_TRUSIGHT_GIVES_VOTE]
[RESULT:DEV_FLAGGED_LOCI_P_GROUP_DIFFERS]
[RESULT:DEV_REFERENCE_SUBSTITUTION_WES_SIMPLEPLURALITYLEX]
[RESULT:DEV_REFERENCE_SUBSTITUTION_RNASEQ_SIMPLEPLURALITYLEX]
[RESULT:DEV_REFERENCE_SUBSTITUTION_RNASEQ_CALLER_HLA_HD]
[RESULT:DEV_REFERENCE_AGREEMENT_WES_SIMPLEPLURALITYLEX]
[RESULT:DEV_REFERENCE_AGREEMENT_RNASEQ_SIMPLEPLURALITYLEX]
[RESULT:DEV_REFERENCE_AGREEMENT_WES_CALLER_OPTITYPE]
[RESULT:DEV_REFERENCE_AGREEMENT_RNASEQ_CALLER_OPTITYPE]
[RESULT:DEV_REFERENCE_AGREEMENT_RNASEQ_CALLER_HLA_HD]
[RESULT:DEV_REFERENCE_AGREEMENT_PHI_WES_RANGE]
[RESULT:DEV_REFERENCE_AGREEMENT_PHI_RNASEQ_HLA_HD_OPTITYPE]
[RESULT:DEV_REFERENCE_AGREEMENT_WES_VOTE_CORRECTS_HLA_HD]
[RESULT:DEV_REFERENCE_AGREEMENT_WES_VOTE_CORRECTS_SPECHLA]
[RESULT:DEV_REFERENCE_AGREEMENT_WES_VOTE_CORRECTS_T1K]

### Call states, singletons, ties and vote support

In the ChampHLA runs, every panel caller had a row at every exact-endpoint locus; two T1K WES rows were partial and one was missing (Supplementary S5).
The singleton rows of HLA-HD (16 WES, 14 RNA-seq) and arcasHLA (9 RNA-seq), and T1K's declared homozygotes (12 WES, 11 RNA-seq), were completed as caller-declared homozygotes.
Of the 64 single-allele rows at exact-endpoint loci, 57 lay at homozygous reference loci. The other seven—four arcasHLA RNA-seq declarations, one T1K WES declaration and the two partial T1K WES rows—lay at heterozygous reference loci (Supplementary Figure S1).

No exact-endpoint locus was tied, so the tie-break did not affect either result (143/153 and 113/118 with ties sent to the last-sorting pair). Three of the 708 requested loci were tied (two WES, one RNA-seq), and on the set-valued endpoint the tie direction moves the vote by one locus in each assay.
Concordance did not rise steadily with vote support, the number of callers supporting the reported genotype out of the number callable (Supplementary Figure S3).
Full-panel unanimity was concordant at 103/104 WES 5/5 loci (99.0%) and 51/53 RNA-seq 4/4 loci (96.2%): unanimous calls were usually, but not always, correct. Among RNA-seq strata with at least five loci, support was nonmonotonic. These are descriptive proportions, not held-out calibration.
Abstaining below a support of four would have called 141/153 WES loci with 134 correct, and below three, 110/118 RNA-seq loci with 106 correct; every threshold is in Supplementary S5 (post hoc). A post hoc allele-level vote gave the genotype vote's call at every exact-endpoint locus.
Results by gene, rare allele, population and zygosity are descriptive, with small strata outside CEU and YRI (Supplementary S4). Disagreement classes, cross-assay agreement and per-gene concordance are in Supplementary S12.
[RESULT:DEV_ABSTENTION_WES_SUPPORT_4]
[RESULT:DEV_ABSTENTION_RNASEQ_SUPPORT_3]
[RESULT:DEV_ALLELE_LEVEL_VOTE_WES]
[RESULT:DEV_ALLELE_LEVEL_VOTE_RNASEQ]
[RESULT:DEV_TIEBREAK_WES_TIED_LOCI]
[RESULT:DEV_TIEBREAK_RNASEQ_TIED_LOCI]
[RESULT:DEV_TIEBREAK_WES_LAST_PAIR]
[RESULT:DEV_TIEBREAK_RNASEQ_LAST_PAIR]

### Exploratory cohorts show that agreement is not accuracy

The NCI-60 cell-line application is being processed with the evaluated workflow under a previously specified analysis plan and is not reported here (Supplementary S9).

## Discussion

The equal-weight plurality vote does not require choosing a caller in advance. Within these named panels, it could not be distinguished from each assay's strongest caller.
Under the single-allele rule adopted after results, the vote was one locus above OptiType in WES and one above both HLA-HD and OptiType in RNA-seq. Every reported genotype can be traced to its supporting votes.
No fitted policy did better. The refitted nested-CV best-caller policy fell one locus short in WES and two in RNA-seq without a significant difference (Supplementary S7). These data do not test whether a rule fitted to better labels could help.
The comparisons were small, and we made the vote primary after seeing the results. They establish neither equivalence nor superiority.
[RESULT:DEV_PAIRED_WES_CALLER_OPTITYPE]
[RESULT:DEV_PAIRED_RNASEQ_CALLER_HLA_HD]
[RESULT:DEV_PAIRED_RNASEQ_CALLER_OPTITYPE]

Reference-typing error may contribute to the vote's small gain, but these data do not show why the gain is small.
Across all exact loci, caller errors were correlated and few loci had a correct caller that the vote missed (small oracle headroom), a pattern that would ordinarily point to errors shared by the callers.
Most loci behind that pattern had already been corrected from the 2014 reference to the callers' genotype by a published re-typing [31].
Where the two typings agreed, caller errors were nearly uncorrelated and the vote was correct at every locus, including every locus where a caller erred. The strongest caller also made almost no errors.
A vote cannot exceed a caller at a ceiling set by the reference, and an uncorrected reference can make agreement among callers look like shared error.
This account is exploratory. Laboratory typing supports it at the flagged loci, but those loci were checked because they were flagged; testing it elsewhere would need independent typing of unflagged loci.

How the benchmark was scored mattered as much as the voting rule.
Treating every single allele as homozygous conflates missingness with biological evidence. Reading caller-native declarations changed the scores of HLA-HD, arcasHLA, T1K and the RNA-seq vote; we report both scorings (Supplementary S2).
Credible HLA benchmarks should record call states and abstentions, parse every reference record and report exact and set-valued endpoints together. Recording caller inputs and execution details also matters: after the low arcasHLA score, these records let us trace it to a deployment defect.

Earlier studies also combined HLA callers by voting.
Claeys *et al.* [19] evaluated a majority vote on the same public 1000 Genomes and Geuvadis data, keeping failed predictions in an allele-level denominator. Lee *et al.* [23] combined callers within an assay and restricted genotype-level analysis to loci with one resolved reference genotype.
This evaluation adds fixed-denominator scoring of caller-native call states and a locus-level record that traces every reported number to its source.
Claeys *et al.* reported allele-level accuracy; our primary endpoint is unordered-genotype concordance, so the values are not directly comparable. In both studies the vote's gain over the best single caller was small.
Our panel covers only a few related algorithmic families. ChampHLA-Consensus therefore provides a baseline and a framework for checking results, rather than a comprehensive comparison of HLA callers.

For research use, these results do not justify running a multi-caller panel solely to improve concordance when a suitable assay-specific caller has already been validated.
The plurality baseline is useful when caller choice is uncertain and users want an auditable rule without fitted parameters.
These results do not extend to clinical HLA typing, including donor–recipient matching or pharmacogenomic screening, which requires accredited laboratory methods and regulatory-grade validation.
Users of the workflow should run it with `-profile paper`, which applies the evaluated rule rather than the unevaluated calibrated default. With RNA-seq BAM input this profile runs the arcasHLA module with the defect described under Limitations.
They should treat a single reported allele as homozygous only where the caller's format declares it, review loci supported by only one caller, and report exact and ambiguity-compatible concordance together.

The specified rule has not yet been tested on unseen subjects. Processing of a separate extension cohort began with the same workflow version and is paused; its analysis plan will be publicly deposited before predictions are compared with reference typing. A comparison of the vote with the strongest caller will remain underpowered: a significant result with no losses needs at least nine discordant WES or eight discordant RNA-seq subjects, against two and one here (Supplementary S3).
The NCI-60 cell-line application is being processed under a documented exploratory protocol.
Evaluating graph and pangenome callers, harmonized databases, class II genes HLA-DRB1 and HLA-DQB1, three-field reference typing, re-extracted WGS inputs and long-read modes would widen the study. Larger cohorts would allow population-stratified analysis and help separate algorithm from deployment effects.

### Limitations

**Design.** This is a retrospective development study without independent external validation.
We set or changed the primary rule, multiplicity scheme, primary paired test and single-allele handling after seeing development results (Methods; Supplementary S14). Every development result is therefore exploratory.
A subject-disjoint extension cohort of 89 WES and 99 RNA-seq subjects has been specified, and no comparison with its reference genotypes has been made; the analysis is not complete and is not reported here.
WES and RNA-seq subjects overlap, and the filtered sets are small. The same five subject–gene loci account for all RNA-seq vote errors and five WES errors, so cross-assay agreement is not independent replication.

**Reference typing.** The reference is the fallible 2014 exon 2–3 table interpreted against a 2009 allele release, and only HLA-A, HLA-B and HLA-C were evaluated, at two-field resolution.
Several callers were developed or evaluated against typings of these same samples (Methods). Neither the primary comparison nor the comparison on loci where both typings agree is independent of every caller, and absolute concordance may be optimistic.
Exclusion of ambiguous typing was strongly population-dependent.
Retention reflects how each contributing laboratory encoded ambiguity as well as typing resolution or quality, so it must not be read as a population accuracy estimate.

**Samples, callers and provenance.** Both assays were generated from lymphoblastoid cell lines, whose high HLA expression and cell-state composition limit transfer of the RNA-seq result to primary or tumour tissue.
The caller panel reflects the original deployment and used different database vintages and reference builds.
We recorded each sample's container digests; equivalent records are unavailable for the archived outputs used in supplementary comparisons. Caller differences still combine algorithm, deployment and reference-resource effects; rankings describe deployed tools rather than algorithms (Supplementary S13).
The workflow has a deployment defect: its arcasHLA module extracts paired-end Geuvadis reads as single-end, which may contribute to the result. The arcasHLA 0.2.0 container, with a runtime patch to its alignment script, then genotypes them without pair information.
In a comparison that did not use reference genotypes, arcasHLA calls from this study differed from archived calls at 176 of 318 RNA-seq caller–gene cells and included many rarely observed allele designations (Supplementary Table S10.2). Exact concordance was 58/118; we diagnosed the deployment only after seeing that score.
We report the result as the specified deployment produced it and did not change the module, so the arcasHLA estimate describes that deployment rather than the caller.
[RESULT:DEV_CORRECTED_RNASEQ_CALLER_ARCASHLA]
WGS outputs from the original caller run failed input-validity checks involving HLA alternate contigs and read extraction, and all quantitative WGS results were removed.

**Statistics.** Single-allele handling changes individual callers' scores (Supplementary S2).
Lexicographic tie-breaking is deterministic but not biologically informed, and it needs prospective replacement or review routing.
Support strata were not externally calibrated. Rare alleles, homozygotes and most population strata were too few to analyse.
ChampHLA-Consensus is an auditable development baseline. With a single recorded reference genotype, fixed denominators, explicit call states and documented caller runs, it could not be distinguished from the best single caller in WES or RNA-seq. It provides neither a new inference algorithm nor a clinical typing system. Its value is operational: users need not choose a caller in advance, and every reported genotype remains traceable to the calls that support it. Between the archived outputs and the study runs, single callers moved by up to 51 loci and the leading exome caller changed, while the vote stayed at 143/153 and 113/118 (post hoc). A later test on unseen subjects, under a plan to be deposited first, will examine the specified rule; claims of equivalence, generalization or clinical use require independent laboratory typing beyond it.
[RESULT:DEV_RUN_STABILITY_WES_CHAMPHLA_CONSENSUS]
[RESULT:DEV_RUN_STABILITY_RNASEQ_CHAMPHLA_CONSENSUS]
[RESULT:DEV_RUN_STABILITY_RNASEQ_LARGEST_CALLER_CHANGE]
[RESULT:DEV_RUN_STABILITY_WES_LEADING_CALLER]

## Data availability

The primary input data are public. The WES data are the 1000 Genomes Project GRCh38DH exome alignments distributed by the International Genome Sample Resource [46]. The RNA-seq data are from the Geuvadis project (ENA study PRJEB3366 [47]; ArrayExpress E-GEUV-1 [48]). `cohorts/official_1000g_assay_manifest.tsv` lists each subject–assay input, its URL and the source checksum where available. The reference typing is the 2014 1000 Genomes HLA table [49] (SHA-256 `0455d0302ac12a29ab87091cab5e3e557416f6301e89fb122eef8d49cd5644ec`). The second typing used for adjudication [31] is the IGSR file `20181129_HLA_types_full_1000_Genomes_Project_panel.txt` (https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/data_collections/HLA_types/; SHA-256 `570b5cc5523273826a5695452f18b77f8742e568e1e35a34aed5d2a313472e8e`). The IPD-IMGT/HLA 3.65.0 allele, deleted-allele, P-group and G-group files [8] come unchanged from tag `v3.65.0-alpha` of the ANHIG/IMGTHLA repository, with checksums in `resources/ipd_imgt_hla/3.65.0/SHA256SUMS`. The relatedness check reads the IGSR pedigree file `20130606_g1k.ped` (https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/technical/working/20130606_sample_info/; SHA-256 `38687335d053056d799891a37c42b1ac24a5a2a1eb5fccaf34db58188bccfff7`). The paths in this section refer to the paper repository [50], which is not yet public and will be released at a fixed tag. `cohorts/development_rerun_manifest.tsv` lists the 236 analysed subject–assay inputs. `artifacts/development_corrected/per_locus_results.tsv` gives every method's call, reference genotype and agreement at each exact-endpoint locus. `scripts/run_local_verification.sh` regenerates these results from the normalized caller tables and the public reference table; it does not rerun callers from reads. Because the logistic meta-consensus refit varies between runs (Supplementary S7.1), a run can stop at the registry-delta author gate; in that case, restore the tracked files and rerun. The caller outputs used in this study, without reference genotypes, their per-sample provenance and the comparison with archived outputs are in `provenance/development_rerun_v350/truth_free_collection/`. The public inputs of the planned extension are listed in `cohorts/extension_v350_manifest.tsv`, and those of the NCI-60 application in `cohorts/nci60_v350_manifest.tsv`, with the ENA file reports and the published NCI-60 typing in `resources/nci60/`.

Public human data remain subject to source-project terms.

## Code availability

The paper repository is intended for archival release on GitHub [50] under the MIT licence; it is currently private. The reproducible analysis starts from normalized caller outputs that contain no reference genotypes and covers checksum-verified reference acquisition, reference selection, code, tests, artifacts, figure formats, manuscript sources and a release manifest. The raw-read-to-caller workflow is maintained separately on GitHub [51], also currently private. The evaluated workflow is identified by tag `v3.5.0` and commit `66d949d`. It implements the rule under `-profile paper`, verifies caller images against specified SHA-256 checksums under Singularity or Apptainer, rescues HLA-allele and alternate-contig reads and parses T1K quality and homozygosity fields. Callers retain their own licences, and some distributions restrict commercial use; see `THIRD_PARTY_NOTICES.md`.



## References

1. Trowsdale J, Knight JC. Major Histocompatibility Complex Genomics and Human Disease. Annu Rev Genomics Hum Genet. 2013;14:301–323. doi:10.1146/annurev-genom-091212-153455.

2. Lee SJ, Klein J, Haagenson M, Baxter-Lowe LA, Confer DL, Eapen M, et al. High-resolution donor-recipient HLA matching contributes to the success of unrelated donor marrow transplantation. Blood. 2007;110:4576–4583. doi:10.1182/blood-2007-06-097386.

3. Petersdorf EW. Risk assessment in haematopoietic stem cell transplantation: Histocompatibility. Best Pract Res Clin Haematol. 2007;20:155–170. doi:10.1016/j.beha.2006.09.001.

4. Mallal S, Phillips E, Carosi G, Molina JM, Workman C, Tomažič J, et al. HLA-B\*5701 Screening for Hypersensitivity to Abacavir. N Engl J Med. 2008;358:568–579. doi:10.1056/NEJMoa0706135.

5. Chung WH, Hung SI, Hong HS, Hsih MS, Yang LC, Ho HC, et al. A marker for Stevens–Johnson syndrome. Nature. 2004;428:486. doi:10.1038/428486a.

6. Schumacher TN, Schreiber RD. Neoantigens in cancer immunotherapy. Science. 2015;348:69–74. doi:10.1126/science.aaa4971.

7. Matzaraki V, Kumar V, Wijmenga C, Zhernakova A. The MHC locus and genetic susceptibility to autoimmune and infectious diseases. Genome Biol. 2017;18:76. doi:10.1186/s13059-017-1207-1.

8. Robinson J, Barker DJ, Georgiou X, Cooper MA, Flicek P, Marsh SGE. IPD-IMGT/HLA Database. Nucleic Acids Res. 2020;48:D948–D955. doi:10.1093/nar/gkz950.

9. Aguiar VRC, César J, Delaneau O, Dermitzakis ET, Meyer D. Expression estimation and eQTL mapping for HLA genes with a personalized pipeline. PLoS Genet. 2019;15:e1008091. doi:10.1371/journal.pgen.1008091.

10. Szolek A, Schubert B, Mohr C, Sturm M, Feldhahn M, Kohlbacher O. OptiType: precision HLA typing from next-generation sequencing data. Bioinformatics. 2014;30:3310–3316. doi:10.1093/bioinformatics/btu548.

11. Kawaguchi S, Higasa K, Shimizu M, Yamada R, Matsuda F. HLA-HD: An accurate HLA typing algorithm for next-generation sequencing data. Hum Mutat. 2017;38:788–797. doi:10.1002/humu.23230.

12. Orenbuch R, Filip I, Comito D, Shaman J, Pe’er I, Rabadan R. arcasHLA: high-resolution HLA typing from RNAseq. Bioinformatics. 2020;36:33–40. doi:10.1093/bioinformatics/btz474.

13. Shukla SA, Rooney MS, Rajasagi M, Tiao G, Dixon PM, Lawrence MS, et al. Comprehensive analysis of cancer-associated somatic mutations in class I HLA genes. Nat Biotechnol. 2015;33:1152–1158. doi:10.1038/nbt.3344.

14. Song L, Bai G, Liu XS, Li B, Li H. Efficient and accurate KIR and HLA genotyping with massively parallel sequencing data. Genome Res. 2023;33:923–931. doi:10.1101/gr.277585.122.

15. Wang S, Wang M, Chen L, Pan G, Wang Y, Li SC. SpecHLA enables full-resolution HLA typing from sequencing data. Cell Rep Methods. 2023;3:100589. doi:10.1016/j.crmeth.2023.100589.

16. 1000 Genomes Project Consortium. A global reference for human genetic variation. Nature. 2015;526:68–74. doi:10.1038/nature15393.

17. Gourraud PA, Khankhanian P, Cereb N, Yang SY, Feolo M, Maiers M, et al. HLA Diversity in the 1000 Genomes Dataset. PLoS One. 2014;9:e97282. doi:10.1371/journal.pone.0097282.

18. Di Tommaso P, Chatzou M, Floden EW, Barja PP, Palumbo E, Notredame C. Nextflow enables reproducible computational workflows. Nat Biotechnol. 2017;35:316–319. doi:10.1038/nbt.3820.

19. Claeys A, Merseburger P, Staut J, Marchal K, Van den Eynden J. Benchmark of tools for in silico prediction of MHC class I and class II genotypes from NGS data. BMC Genomics. 2023;24:247. doi:10.1186/s12864-023-09351-z.

20. Kiyotani K, Mai TH, Nakamura Y. Comparison of exome-based HLA class I genotyping tools: identification of platform-specific genotyping errors. J Hum Genet. 2017;62:397–405. doi:10.1038/jhg.2016.141.

21. Larjo A, Eveleigh R, Kilpeläinen E, Kwan T, Pastinen T, Koskela S, et al. Accuracy of Programs for the Determination of Human Leukocyte Antigen Alleles from Next-Generation Sequencing Data. Front Immunol. 2017;8:1815. doi:10.3389/fimmu.2017.01815.

22. Li X, Zhou C, Chen K, Huang B, Liu Q, Ye H. Benchmarking HLA genotyping and clarifying HLA impact on survival in tumor immunotherapy. Mol Oncol. 2021;15:1764–1782. doi:10.1002/1878-0261.12895.

23. Lee M, Seo JH, Song S, Song IH, Kim SY, Kim YA, et al. A New Human Leukocyte Antigen Typing Algorithm Combined With Currently Available Genotyping Tools Based on Next-Generation Sequencing Data and Guidelines to Select the Most Likely Human Leukocyte Antigen Genotype. Front Immunol. 2021;12:688183. doi:10.3389/fimmu.2021.688183.

24. Bowen-James R, Wu W, Wong-Erasmus M, Quinn JMW, Mayoh C, Cowley MJ. consHLA: a next generation sequencing consensus-based HLA typing workflow. BMC Bioinformatics. 2025;26:215. doi:10.1186/s12859-025-06223-z.

25. Ryan KM, O’Connor D, Digby B, Barkley LR, Ó Broin P. Abstract P2-06-26: nf-hlamajority: a Nextflow pipeline for consensus MHC class I typing and its application to neoantigen identification in breast cancer stromal cells. Clin Cancer Res. 2025;31 Suppl 12:P2-06-26. doi:10.1158/1557-3265.SABCS24-P2-06-26.

26. Nordin J, Ameur A, Lindblad-Toh K, Gyllensten U, Meadows JRS. SweHLA: the high confidence HLA typing bio-resource drawn from 1000 Swedish genomes. Eur J Hum Genet. 2020;28:627–635. doi:10.1038/s41431-019-0559-2.

27. Lappalainen T, Sammeth M, Friedländer MR, ‘t Hoen PAC, Monlong J, Rivas MA, et al. Transcriptome and genome sequencing uncovers functional variation in humans. Nature. 2013;501:506–511. doi:10.1038/nature12531.

28. Adams S, Robbins FM, Chen D, Wagage D, Holbeck SL, Morse HC, et al. HLA class I and II genotype of the NCI-60 cell lines. J Transl Med. 2005;3:11. doi:10.1186/1479-5876-3-11.

29. Li H. Aligning sequence reads, clone sequences and assembly contigs with BWA-MEM. arXiv. 2013;1303.3997. doi:10.48550/arXiv.1303.3997.

30. Bauer DC, Zadoorian A, Wilson LOW, Melbourne Genomics Health Alliance, Thorne NP. Evaluation of computational programs to predict HLA genotypes from genomic sequencing data. Brief Bioinform. 2018;19:179–187. doi:10.1093/bib/bbw097.

31. Abi-Rached L, Gouret P, Yeh JH, Di Cristofaro J, Pontarotti P, Picard C, et al. Immune diversity sheds light on missing variation in worldwide genetic diversity panels. PLoS One. 2018;13:e0206512. doi:10.1371/journal.pone.0206512.

32. Thuesen NH, Klausen MS, Gopalakrishnan S, Trolle T, Renaud G. Benchmarking freely available HLA typing algorithms across varying genes, coverages and typing resolutions. Front Immunol. 2022;13:987655. doi:10.3389/fimmu.2022.987655.

33. Buchkovich ML, Brown CC, Robasky K, Chai S, Westfall S, Vincent BG, et al. HLAProfiler utilizes k-mer profiles to improve HLA calling accuracy for rare and common alleles in RNA-seq data. Genome Med. 2017;9:86. doi:10.1186/s13073-017-0473-6.

34. Marsh SGE, Albert ED, Bodmer WF, Bontrop RE, Dupont B, Erlich HA, et al. Nomenclature for factors of the HLA system, 2010. Tissue Antigens. 2010;75:291–455. doi:10.1111/j.1399-0039.2010.01466.x.

35. HLA-HD demo manual, version 1.7.0. Kyoto University. https://w3.genome.med.kyoto-u.ac.jp/HLA-HD/demo/hlahd-demo.v1.pdf. Accessed 13 Oct 2026.

36. arcasHLA, release v0.2.0 (source code). GitHub. https://github.com/RabadanLab/arcasHLA/tree/v0.2.0. Accessed 10 Oct 2026.

37. Clopper CJ, Pearson ES. The use of confidence or fiducial limits illustrated in the case of the binomial. Biometrika. 1934;26:404–413. doi:10.2307/2331986.

38. Holm S. A simple sequentially rejective multiple test procedure. Scand J Stat. 1979;6:65–70. doi:10.2307/4615733.

39. Cameron AC, Miller DL. A Practitioner’s Guide to Cluster-Robust Inference. J Hum Resour. 2015;50:317–372. doi:10.3368/jhr.50.2.317.

40. Harris CR, Millman KJ, van der Walt SJ, Gommers R, Virtanen P, Cournapeau D, et al. Array programming with NumPy. Nature. 2020;585:357–362. doi:10.1038/s41586-020-2649-2.

41. Virtanen P, Gommers R, Oliphant TE, Haberland M, Reddy T, Cournapeau D, et al. SciPy 1.0: fundamental algorithms for scientific computing in Python. Nat Methods. 2020;17:261–272. doi:10.1038/s41592-019-0686-2.

42. Hunter JD. Matplotlib: A 2D Graphics Environment. Comput Sci Eng. 2007;9:90–95. doi:10.1109/MCSE.2007.55.

43. Kurtzer GM, Sochat V, Bauer MW. Singularity: Scientific containers for mobility of compute. PLoS One. 2017;12:e0177459. doi:10.1371/journal.pone.0177459.

44. Li H, Handsaker B, Wysoker A, Fennell T, Ruan J, Homer N, et al. The Sequence Alignment/Map format and SAMtools. Bioinformatics. 2009;25:2078–2079. doi:10.1093/bioinformatics/btp352.

45. Erlich RL, Jia X, Anderson S, Banks E, Gao X, Carrington M, et al. Next-generation sequencing for HLA typing of class I loci. BMC Genomics. 2011;12:42. doi:10.1186/1471-2164-12-42.

46. International Genome Sample Resource. 1000 Genomes Project data collection. https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/data_collections/1000_genomes_project/. Accessed 10 Oct 2026.

47. European Nucleotide Archive. Study PRJEB3366 (Geuvadis RNA sequencing). https://www.ebi.ac.uk/ena/browser/view/PRJEB3366. Accessed 10 Oct 2026.

48. ArrayExpress. E-GEUV-1: RNA-sequencing of 465 lymphoblastoid cell lines from the 1000 Genomes. https://www.ebi.ac.uk/biostudies/arrayexpress/studies/E-GEUV-1. Accessed 10 Oct 2026.

49. International Genome Sample Resource. 1000 Genomes HLA diversity genotypes (20140702_hla_diversity.txt). https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/technical/working/20140725_hla_genotypes/20140702_hla_diversity.txt. Accessed 10 Oct 2026.

50. ChampHLA paper repository. GitHub. https://github.com/uoozcan/ChampHLA-paper.

51. ChampHLA Nextflow workflow. GitHub. https://github.com/uoozcan/ChampHLA.

## Figure legends

**Figure 1. ChampHLA workflow, consensus rule, study design and cohort flow.**
(A) The workflow routes FASTQ, BAM or CRAM input to the assay's caller panel (Table 1), parses and normalizes outputs to two-field genotypes, then applies consensus. Callers run in containers, except SpecHLA, which ran from a native installation in this study.
(B) Example ChampHLA-Consensus vote at a WES locus: each callable caller casts one vote; callers without calls do not vote. The most-voted unordered genotype is reported, with exact ties going to the alphabetically first genotype.
The alleles shown are an example, not data.
(C) Caller processing and normalization are completed before comparison with separately parsed reference typing. Caller output cannot influence reference resolution.
(D) Requested assay–gene loci partitioned into resolved, ambiguous, invalid and source-absent reference states.
Source absence is a state of the reference record, not a caller no-call.
Counts are generated from the truth-flow artifact.

**Figure 2. Fixed-denominator exact genotype concordance and callability.**
Exact unordered two-field genotype concordance and callability of each method in WES (A) and RNA-seq (B), over the same fixed denominator.
Bars are 95% subject-cluster percentile bootstrap intervals, or exact Clopper–Pearson intervals for estimates of 0% or 100%, and the adjacent columns give correct/N and callable/N.
Blue denotes ChampHLA-Consensus, the orange triangle the exploratory fitted nested-CV best-caller policy, and grey circles individual callers. Threshold rules and the other five exploratory fitted policies are not shown (Table 2; Supplementary S7).
Methods follow a fixed role-based order rather than observed performance.
Both percentage axes are truncated below 100% to show the observed range and never extend above 100%.
† Defective deployment: paired-end reads processed as single-end (Limitations).

**Figure 3. Paired differences from ChampHLA-Consensus.**
Each point is ChampHLA-Consensus minus one comparator, in percentage points, so positive values favour the vote.
Bars are descriptive Bonferroni-adjusted cluster-*t* intervals over the same family used for Holm testing.
Circles denote descriptive comparators and triangles exploratory fitted policies.
Magenta with an asterisk marks an exact subject sign-flip Holm-adjusted *p*<0.05; grey is nonsignificant.
Significance follows the governing sign-flip test. In RNA-seq the strict-majority and two-thirds consensus intervals exclude zero, but their sign-flip Holm-adjusted *p* values are not below 0.05; both are grey (Supplementary S3).
The right-hand columns give locus wins/losses and sign-flip Holm-adjusted *p* values.
† Defective deployment: paired-end reads processed as single-end (Limitations).
Comparisons with zero discordance are displayed at 0 with interval 0 to 0, wins/losses 0/0 and *p*=1.
Cluster-*t* Holm-adjusted *p* values are in Supplementary S3.
Non-significance is not equivalence.

**Figure 4. Pairwise caller-error dependence.**
Error φ between each pair of callers in WES (A) and RNA-seq (B), on one 0–1 colour scale and annotated to two decimals.
Both triangles use exact-endpoint loci. Above the diagonal, φ uses the fixed denominator; below it, φ uses mutually callable loci, excluding any locus where either caller made no call.
Most joint errors occur where second typing disagrees with the reference. Where the typings agree, dependence largely disappears (Supplementary S7).
The matrices are descriptive and do not identify a causal error mechanism.

## Supplementary information

Supplementary methods, results, tables and figures are supplied as a separate document. They cover the cohort and reference-source audit, complete method performance, paired comparisons, stratified results, call states and ties, caller-resource provenance, oracle headroom and fitted policies, excluded earlier analyses, the status of the NCI-60 application, the reproducibility details, workflow execution, disagreement classes, and background and design rationale.
