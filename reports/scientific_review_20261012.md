# ChampHLA scientific review, 2026-10-12 (v3 manuscript)

Produced by `SCIENTIFIC_REVIEW_PROMPT.md`. Read-only review; nothing in the manuscript,
registry, artifacts, decisions or code was changed. Finding IDs are `SR-###`. The work list
is `reports/scientific_review_20261012.tsv`.

## 1. What was reviewed

| Item | Value |
|---|---|
| Text reviewed | Google Drive `ChampHLA_Manuscript_v3.docx`, file ID `1T9Gc-tXFc4eAV6FD7bco8d3Ra63DiDYa` |
| Drive state | 3,423,697 bytes; created 2026-10-12T00:56:35Z; modified 2026-10-12T00:56:13Z (unchanged since upload) |
| Local copy used for extraction | `D:\panelhla_work\drive_v3\ChampHLA_Manuscript_v3.docx`, same size, MD5 `d02f7c4b70176383fd6f1f71f34b2004` (the MD5 recorded at upload) |
| Paper repository | branch `submission-remediation`, HEAD `ca708067`, `git fsck` clean; working tree had one pre-existing modification (`reports/champhla_gap_review_20261007.md`) and the untracked prompt file |
| Document against markdown | Every paragraph and table cell of the document traces to `manuscript.md`, `supplementary.md` or the preface source; no source block is missing from the document. Seven builder banner lines are extra. All 12 embedded images are byte-identical to `figures/*.png`. **One divergence the comparison could not see because it ignored punctuation: allele asterisks are lost in the document (SR-015).** |
| Workflow repository | `D:\panelhla_work\panelhla-repo`, tags `v3.3.0`, `v3.4.0`, `v3.4.1`; read with `git show` only |

**What was run.** Independent recomputation from
`artifacts/development_corrected/per_locus_results.tsv` with my own scripts
(`D:\panelhla_work\tmp\scientific_review_20261012\recompute1-4.py`, no project module
imported): every method's concordance, paired subject differences, exact sign-flip
p-values, Holm adjustment, Bonferroni CR1 intervals, caller-error phi with 2×2 counts,
oracle headroom, an independent re-implementation of the vote, error anatomy per caller,
and phi on the loci where the two reference typings agree.

**Who read what.** Four independent readers with clean contexts were used, as the approved
plan stated, because this session had already read the main text: a cold referee read of
the document alone (`phase1_cold_read.md`), a reference and quoted-fact check
(`reference_check.md`, 51 references, 66 verdicted statements), a literature and
caller-accuracy search (`literature_check.md`), and a refutation pass on the eleven most
serious draft findings (`refute/refutation.md`). All four files are in the scratch directory.

**What was not run.** The verification gate (`run_local_verification.sh`) was not run, so
whether the committed artifacts are stale relative to HEAD was not re-tested. Nothing was
run on Roihu. No patient-level file was opened. Nothing was written to Drive.

## 2. Referee summary

**The paper's claim.** On 63 exome and 51 RNA-seq subjects with unambiguous 2014 reference
typing, an untrained equal-weight plurality vote over five or four HLA class I callers
agrees with the reference about as often as the best single caller, no fitted policy does
better, and the lasting contribution is the way the evaluation was done.

**Assessment.** The downstream analysis is careful and every number I recomputed matched.
The problem is upstream of the arithmetic. The paper explains its null by correlated caller
errors, but its own unreported sensitivity analysis shows those correlations vanish on loci
where the reference is credible; what the correlations measure is callers jointly
disagreeing with a reference that the source of the second typing had already corrected.
The paper calls that correction mark "undocumented"; it is documented in the same article.
Once that is put right the story changes, and for the better: on credible-reference loci
the vote is 142/143 and 112/112, caller errors are nearly independent, and the vote removes
almost all of them. Separately, the individual-caller rows describe one unrecorded
deployment: T1K scores far below every published figure and is wrong at every homozygous
locus, the workflow's T1K parser ignores the quality field T1K's authors say to filter on,
and the one re-run subject did not reproduce four stored calls, all in the three weakest
callers. The study is small by choice, not by necessity: 130 of 1,267 typed individuals
were run and the paper does not say how they were picked.

**Predicted decision at BMC Bioinformatics: major revision.** The journal asks for
soundness, and soundness is recoverable here: the fixes to the interpretation are local,
and the experiment can be re-run with a pinned workflow on public data. An independent cold
reader given only the document reached the same decision ("major revision, at the boundary
of reject") and the same three priorities. If the paper is submitted as it stands, a
referee who opens the Abi-Rached supplement or knows T1K will find the two FATAL items
quickly.

**The three changes that matter most, in order.**

1. **Put the reference right and follow it through.** State what the asterisk means, report
   the correlations and headroom on loci where the typings agree (already computed, already
   promised in a signed decision), withdraw the correlated-error explanation, and present
   the reference-corrected results beside the headline. Local work only.
2. **Re-run the callers with the pinned workflow.** Fix T1K parsing first, then run release
   3.4.x on the development subjects and the frozen extension roster. This replaces an
   unrecorded run with a reproducible one, settles whether the weak callers are weak, and
   supplies the confirmation a referee will ask for. Needs the cluster and two signatures.
3. **Narrow the claims to what survives.** A negative result with an evaluation protocol;
   novelty stated accurately against Lee et al. and Claeys et al.; exploratory patient
   cohorts cut back.

## 3. Strengths to preserve

- The fixed denominator reported beside callability and called-only concordance.
- Subject-level clustering, the exact sign-flip test, and the plain statement of what the
  design could not detect. Few papers in this field say this.
- The table listing every consensus error with both typings, and the released per-locus
  results table. These made this review possible.
- The population-retention analysis and the statement that the strongest caller differs on
  excluded loci.
- The tie-reversal and single-allele sensitivity analyses, and the oracle bound.
- The dated protocol history, and the refusal to claim non-inferiority, external validity
  or clinical use.
- Structure, abstract length, keywords, declarations and the AI-use statement already meet
  the current BMC Bioinformatics guidelines (section 11).

## 4. Findings by severity

Referee codes: R1 HLA immunogeneticist, R2 biostatistician, R3 reproducibility and software
reviewer, R4 handling editor. Dimensions A–L are those of the review prompt. Line numbers
are in `manuscripts/benchmark/manuscript.md` (MS) and `supplementary.md` (SUPP).

### 4.1 FATAL (2)

### SR-001 — The correlated-error explanation is contradicted by the project's own unreported analysis
FATAL · F, H · R2 · CONFIRMED
Where the reader meets it: Abstract, "correlated caller errors limit what any vote over these callers can add"; Conclusions, "because caller errors were strongly correlated".
Source: MS 54–55, 59–61, 684–695, 825–829, 930–931; Figure 4; SUPP 518–550.
Evidence: `artifacts/development_characterisation/reference_agreement_error_phi.tsv`, reproduced independently (`recompute4.py`; again by the refuter). WES pairwise error phi is 0.16 to 0.77 on all 153 loci and −0.04 to 0.20 on the 143 loci where the two typings agree. OptiType with POLYSOLVER falls from 0.77 (9 loci both wrong) to −0.01 (0 both wrong). For the three callers with enough errors to estimate anything (HLA-HD 17, SpecHLA 22, T1K 30 on agreeing loci) the pairwise values are −0.04, 0.02 and −0.03. In RNA-seq the three remaining sizeable values (0.86, 0.34, 0.27) are each produced by the same three loci of NA19130, where HLA-HD, OptiType and T1K have no stored row; arcasHLA with T1K is 0.20 from two loci. On agreeing loci the vote corrects 16 of HLA-HD's 17 WES errors, 22 of SpecHLA's 22 (with one loss) and 29 of T1K's 30. The decision `decisions/20261009_reference_adjudication.json` (reporting commitment 1) promises "per-method concordance, oracle, phi ... whatever its direction"; the phi result has no registry row and appears nowhere in the manuscript.
Why a referee objects: "Your stated mechanism is an artefact of the reference. Where the reference is credible your callers err independently and your vote fixes nearly all of it. You computed this and left it out."
Fix: Report the agreeing-loci phi table and headroom in S7 with one Results sentence, as the signed decision requires. Remove the causal wording from the Abstract, Discussion and Conclusions. Replace it with what the data show: on all loci, joint "errors" are mostly joint disagreement with a reference corrected elsewhere (SR-002); on agreeing loci the vote and the best caller are both at ceiling (142/143 each in WES), so the small gain is a ceiling effect. Attach the caveat that the agreeing subset is conditioned on a further exome-based caller. Delete "Further gains require callers that fail differently". Redraw or annotate Figure 4.
Fix type: new analysis from stored tables (already computed) plus rewording
Effort: M
Prior review: PSR-054 closure contested

### SR-002 — The second typing's asterisk is documented; the manuscript says it is not, and the "agreement" result is true by construction
FATAL · B, J · R1 · CONFIRMED
Where the reader meets it: Results, "they carry an asterisk that the source does not document"; "the asterisk's meaning is undocumented".
Source: MS 266–268, 717–729; SUPP 563–570; `decisions/20261009_reference_adjudication_posthoc.json`.
Evidence: Abi-Rached et al. 2018 (doi:10.1371/journal.pone.0206512). S1 Table legend: "In some cases (marked by asterisks), the PolyPheMe typing was validated through manual verifications (see Methods)". S1 Table workbook footnote: "*: corrected match (see methods)". S3 Fig tabulates the 109 validated cases with the existing result each replaced, including every allele at this paper's error loci (A 02:07 for 02:01; A 66:03 for 66:02; B 27:05 for 27:03; B 39:24 for 39:03; C 02:10 for 02:02; C 07:01 for 07:02). The IGSR README and the S2 Table legend, which are what the decision record says was checked, do not mention it. Verified twice independently (`reference_check.md` section 3; `refute/refutation.md` claim 2), including that the IGSR file's asterisks match S1 Table at 109 of 110 cells and that all 64 exact-endpoint subjects are among the 992 individuals of S1 Table. Two consequences. (a) "Wherever it was available it agreed with the reference (143/143 WES and 112/112 RNA-seq loci)" is true by construction: the signed rule classes an asterisked value as unavailable, and the asterisk marks a retained disagreement with the 2014 typing. (b) MS 266–268, "targeted resequencing confirmed the new typing for 105 results", misstates the source: all cases were confirmed by manual read inspection, with NGS retyping of 21 individuals.
Why a referee objects: "The paper's most consequential interpretive sentence rests on a symbol it calls undocumented, and the documentation is in the cited article's supplement."
Fix: Replace both "undocumented" statements with the documented meaning, citing the S1 Table legend and S3 Fig. State the result plainly: at 14 of 15 consensus errors the source reports that the 2014 typing was wrong and its corrected typing equals the consensus call; give the strength of each correction as S3 Fig records it (targeted NGS for C 07:01 and for one case each of A 02:07 and C 02:10; manual inspection otherwise). Say that the 143/143 and 112/112 agreement follows from the parsing rule. Correct MS 266–268 to "manual inspection of the reads, with NGS retyping of 21 individuals". Record a superseding decision; the signed rule and its results stay as they are. Note that the second typing is exome-derived and that T1K and SpecHLA were evaluated against it (SR-017).
Fix type: rewording, plus a new decision record
Effort: S
Prior review: PSR-054 closure contested

### 4.2 MAJOR (6)

### SR-003 — The headline measures agreement with a reference the field has already corrected, and the corrected picture is not carried into the conclusions
MAJOR · B, H · R1 · CONFIRMED
Where the reader meets it: Conclusions, "ChampHLA-Consensus achieved 93.5% exact two-field concordance on 153 WES loci and 95.8% on 118 RNA-seq loci."
Source: MS 536–539, 624–626, 717–729, 940–941; SUPP 572–626, 1321–1345.
Evidence: (a) All 5 RNA-seq consensus errors are at the same subject and gene as a WES error with the identical consensus genotype (`recompute2.py`); the 15 errors are 10 distinct loci. The text never says so; it is visible only by reading the adjudication table rows or by arithmetic on S12.2. (b) On loci where the typings agree the vote is 142/143 and 112/112 (MS 720–721), but the Conclusions quote only 93.5% and 95.8%. (c) Corrected references for these samples are published and not cited: Thuesen et al. 2022 (doi:10.3389/fimmu.2022.987655) corrected the 2014 typing with the second typing on 829 exomes; Buchkovich et al. 2017 (doi:10.1186/s13073-017-0473-6) re-typed discordant Geuvadis samples in the laboratory and published a corrected truth that the arcasHLA paper then used (`literature_check.md` Q1, Q4). (d) Five of the 15 errors are C*02:02 against C*02:10, which exon 2–3 typing cannot separate; the manuscript's "G-equivalent" column flags them, but that flag is lenient (SR-021). (e) The Results commitment to state the G-equivalence counts is unmet (decision reporting commitment 0).
Why a referee objects: "You report as error what the literature, and your own supplement, show to be reference error, and you rediscover post hoc what two cited-adjacent papers published years ago."
Fix: State in Results that the five RNA-seq errors replicate WES errors, on different data and partly different callers. Give 142/143 and 112/112 beside the headline wherever the headline appears, including the Conclusions. Cite Thuesen and Buchkovich and say what they found. Add a reference-corrected sensitivity for every method in the main table. Whether the corrected endpoint becomes co-primary is an analysis-rule decision for the author (group 3).
Fix type: rewording plus new analysis from stored tables; endpoint status needs a signed decision
Effort: M
Prior review: PSR-054 closure contested

### SR-004 — T1K's results reflect the wrapper and the scoring rule, not only the caller
MAJOR · D, E · R1 · CONFIRMED (facts) / PLAUSIBLE (cause of the two-allele errors)
Where the reader meets it: Table 2, "T1K ... 113/153 ... 73.9"; Results, "ChampHLA-Consensus had greater concordance than HLA-HD, SpecHLA and T1K in WES, and than T1K in RNA-seq."
Source: MS 364–368, 576, 583, 593–595, 656–662; SUPP 229–259; workflow `bin/parse_t1k_results.py` at `v3.4.1`.
Evidence: The parser reads `allele_1` and `allele_2` and never reads `num_diff_alleles` or either quality column; no T1K quality filter exists anywhere in the release. The T1K README says "We recommend to ignore alleles with quality less or equal to 0". T1K is correct at 0 of 18 WES and 0 of 15 RNA-seq homozygous-reference loci (other callers 16–18 of 18 and 14–15 of 15): 21 single-allele rows that abstain by rule, and 11 two-allele calls of which 10 are the reference allele plus another (for example A*02:1061, A*02:816, C*05:176, B*07:359). In all 21 single-allele rows the single allele equals the reference allele; completing them gives 124/153 (81.0%) and 101/118 (85.6%) (`refute/check_t1k.py`). The T1K authors themselves read a single allele as homozygous. Published T1K accuracy is 96.1% for WES class I and about 99.3% for RNA-seq (doi:10.1101/gr.277585.122, allele level). The quality values of the development run are not stored, so whether the filter would remove the extra alleles cannot be checked locally.
Why a referee objects: "A caller that is never right at a homozygous locus is telling you about your parser. Two of your four significant comparisons are against this caller."
Fix: Add a T1K-completed row to the single-allele sensitivity table (local). State in Methods that the wrapper does not apply T1K's quality recommendation and what that may cost. Fix the parser in the workflow to honour quality and `num_diff_alleles`, then re-run (with SR-005). Until re-run, word the T1K comparisons as comparisons with this deployment of T1K.
Fix type: new analysis from stored tables; workflow fix; needs cluster to settle
Effort: M
Prior review: new

### SR-005 — The caller run cannot be reproduced, and the one re-run failed exactly where the weak callers are
MAJOR · D, I · R3 · CONFIRMED
Where the reader meets it: Methods, "The stored development calls do not show the read-loss pattern: POLYSOLVER, the caller it affects most, was the most concordant WES caller"; Conclusions, "an audited, artifact-traceable benchmark of six short-read HLA class I callers".
Source: MS 172–189, 927–928; SUPP 1106–1122; `artifacts/development_characterisation/hg00096_wes_release_comparison.tsv`; `provenance/hg00096_wes_release/`.
Evidence: For HG00096, release 3.4.0 made all five WES callers unanimous at all three genes. The four stored calls it did not reproduce are HLA-HD at HLA-B (stored B*44:26), HLA-HD at HLA-C (C*07:141 with C*16:21), SpecHLA at HLA-C (homozygous C*16:01) and T1K at HLA-B (B*07:359): all in the three lowest-scoring callers, none in POLYSOLVER or OptiType. Neither the main text nor S10 names them. Three of the four are rare-allele substitutions, which read loss does not explain. The manuscript's argument covers POLYSOLVER only; a truth-free check over all 390 requested WES loci does support the absence of haplotype loss for all five callers (`refute/check_readloss.py`), but the paper does not show it. Separately, the revision named as the one that produced the calls (7 April 2026) has a T1K parser that reads the wrong columns for T1K's format; the stored T1K rows match the parser as changed on 18 April (commit `304abfc`), so MS 173–174 cannot be right as written for T1K. Published context: HLA-HD's 82.4% is in line with Lee et al. 2021 (81.4% on the same data and metric), so HLA-HD is not shown to be artificially weak; SpecHLA's 80.4% is well below its published 98.4% with the run mode unrecorded.
Why a referee objects: "This is not a benchmark of six callers. It is an audit of one table of outputs whose provenance you cannot state, and your only reproduction attempt disagrees with it at a quarter of the calls."
Fix: Name the four non-reproduced calls and say they are unexplained. Add the truth-free haplotype-loss check for all callers. Correct or qualify the "7 April" statement. Re-run the development subjects from reads with the pinned release and report a cell-by-cell comparison with the stored calls; decide by signed record which run is primary. Until then, title and Conclusions should describe an evaluation of stored outputs, not a benchmark of callers.
Fix type: rewording now; needs cluster to resolve
Effort: L
Prior review: PSR-018 closure contested

### SR-006 — The cohort is small by choice, its selection is not described, and the confirmation is unrun
MAJOR · C · R2 · CONFIRMED
Where the reader meets it: Methods, "The requested inputs contained 130 WES subjects (390 subject-gene loci) and 106 RNA-seq subjects (318 loci)".
Source: MS 200–206, 474–476, 890–892; SUPP 10–20, 51–94; `cohorts/`.
Evidence: The 2014 table types 1,267 individuals; `cohorts/official_1000g_assay_manifest.tsv` lists 2,692 WES and 462 RNA-seq inputs. No sentence in the manuscript, decisions, README or `cohorts/` says how 130 and 106 were chosen. Eighteen requested subjects, the same in both assays, have no entry in the reference table (54 absent loci per assay; the absence is disclosed, the reason is not). Claeys et al. scored about 1,010 exomes and 372 RNA-seq samples per gene from the same resource (verified, `reference_check.md`). After filtering, the headline comparisons differ in two subjects and one. The extension roster (89 WES, 99 RNA-seq) is frozen and its pre-registration has a reserved DOI but no signature (`decisions/20261009_extension_confirmatory_preregistration.json`, `signed: null`). The subject ledger also records an earlier sealed hold-out of 38 of these subjects (`cohorts/subject_exposure_summary.json`); the manuscript treats all as development and does not mention it (not checked further).
Why a referee objects: "The data to answer your question ten times over are public, and your workflow exists. Why this subset, and why should I accept 'planned' for the confirmation?"
Fix: State the selection rule and why untyped subjects were requested. Run the confirmatory extension before submission. Consider scoring all typed subjects in the re-run of SR-005.
Fix type: rewording; needs cluster; needs author signature
Effort: L
Prior review: new

### SR-007 — The RNA-seq comparison with the strongest caller is one subject with no stored rows
MAJOR · F, G · R2 · CONFIRMED
Where the reader meets it: Discussion, "ChampHLA-Consensus tied POLYSOLVER on the WES total and was three loci above HLA-HD in RNA-seq".
Source: MS 545–549, 553–556, 584, 656–657, 690–691, 801–802; SUPP 441–453, 541.
Evidence: At NA19130 HLA-A, -B and -C, HLA-HD, OptiType and T1K have no row in the stored table; the vote there is arcasHLA alone and is correct. The vote and HLA-HD differ in correctness at exactly those three loci; on the 115 loci with an HLA-HD row both are correct at 110 (`recompute2.py`). The same three loci supply 3 of the 8 joint errors behind the HLA-HD–OptiType phi of 0.94. The manuscript gives the pieces in four places and never joins them. Supplementary Figure S1's legend says the stored table cannot separate a run failure from a missing output, so these "caller errors" may be missing data. A second subject, HG00174, has the same pattern outside the exact endpoint.
Why a referee objects: "Your only RNA-seq difference from the best caller is a file that was not there."
Fix: Say it in Results and remove "three loci above HLA-HD" or qualify it. Add paired comparisons on mutually available loci beside the fixed denominator. State whether the three callers were run on NA19130. Scoring an absent row as incorrect is the declared rule and can stay; whether an input with three of four callers absent should be withheld is a rule question for the author.
Fix type: rewording plus new analysis from stored tables
Effort: S
Prior review: new

### SR-008 — The novelty statement is overstated and the nearest prior work is missing
MAJOR · A · R4 · CONFIRMED
Where the reader meets it: Discussion, "What differs here is the evaluation: ambiguous reference typing is excluded rather than resolved ... missing calls stay in a fixed denominator".
Source: MS 124–144, 831–844.
Evidence: Lee et al. 2021 (doi:10.3389/fimmu.2021.688183) scored only loci with a single reference type, at genotype level, on 1000 Genomes exomes ("The number of cases obtained the HLA genotype as one type was 234 for HLA-A, 308 for HLA-B, and 309 for HLA-C. Using this data, we calculated the availability and accuracy"). Claeys et al. 2023 (doi:10.1186/s12864-023-09351-z) define accuracy as correctly predicted alleles over twice the number of samples, so a failed call counts against accuracy. Two of the five listed differences are therefore anticipated; the declared call states, the performance-free tie-break and the artifact trail are not. The non-comparability with Claeys is mainly allele-level against genotype-level scoring, which the manuscript does not say. Not cited: Thuesen 2022 and Buchkovich 2017 (SR-003); nf-hlamajority (Ryan et al., doi:10.1158/1557-3265.sabcs24-p2-06-26), a Nextflow implementation of the Claeys vote and the closest software competitor; SweHLA (Nordin 2020, doi:10.1038/s41431-019-0559-2). Li et al. [26] is cited as ensemble evidence although its truth was the tools' own consensus. The Lee and Claeys quotations were retrieved through a page-fetch tool; re-check them against the PDFs before quoting.
Why a referee objects: "The contribution you claim is the evaluation, and half of what you list as different is in papers you cite."
Fix: Rewrite the novelty paragraph to claim only the three things that are new, credit Lee and Claeys for the other two, state the allele-level against genotype-level difference, add the missing citations, and add the caveat on Li et al.
Fix type: rewording
Effort: S
Prior review: PSR-015 closure contested

### 4.3 MINOR (15)

### SR-009 — "Did not change this picture" is asserted without a test on the set-valued endpoint
MINOR · F · R2 · CONFIRMED
Where the reader meets it: Abstract, "Scoring ambiguous reference typing as sets of allowed genotypes did not change this picture."
Source: MS 51–52, 607–618; SUPP 113–171.
Evidence: No paired comparison exists on this endpoint in the text, supplement or registry. Summing the truth-selection table gives the vote 320/335 against OptiType 315 and POLYSOLVER 314 (WES), and 256/263 against OptiType 249 and HLA-HD 247 (RNA-seq). Computed by the refuter with the repository's own functions (`refute/check_claim9_detail.py`): WES against POLYSOLVER, 9 wins and 3 losses in 8 subjects, raw sign-flip p = 0.070, Holm 0.141; against OptiType p = 0.125; RNA-seq against OptiType p = 0.25, against HLA-HD p = 0.125. Six of the RNA-seq wins against each caller come from NA19130 and HG00174, the two subjects with absent rows.
Why a referee objects: "The endpoint with twice the loci is the one you did not test."
Fix: Report these paired tests in S3 with registry rows, and say that the best caller on this endpoint is OptiType in both assays.
Fix type: new analysis from stored tables
Effort: S
Prior review: new

### SR-010 — The arcasHLA single-allele rule cites the wrong version boundary and depends on an unrecorded version
MINOR · E, J · R1 · CONFIRMED
Where the reader meets it: Methods, "arcasHLA releases before 0.5 report a homozygous genotype as a single allele".
Source: MS 360–364.
Evidence: arcasHLA `scripts/genotype.py` returns a single allele at v0.2.0 to v0.3.0 and a pair from v0.4.0 (27 January 2022); v0.4.0 and v0.5.0 are identical there (`reference_check.md`, problem 3). The caller run did not record executable versions (MS 334), so which convention applied is inferred, not known. The empirical support (all 14 arcasHLA single-allele rows at homozygous-reference loci) is the same support T1K has and is denied (SR-004).
Fix: Say "releases before 0.4.0"; state that the version was not recorded and that the rule is supported by the observed zygosity; cite the HLA-HD demo PDF for the hyphen convention (reference 33 does not contain it).
Fix type: rewording
Effort: S
Prior review: new

### SR-011 — The supplement still states the superseded single-allele rule
MINOR · E, G · R4 · CONFIRMED
Where the reader meets it: S7.1, "a single reported allele is not completed into a homozygous genotype"; S8, "A signed superseding decision adopts singleton abstention".
Source: SUPP 713–715, 772–773; MS 356–365; SUPP 434–435.
Evidence: The Methods and the S5 table (HLA-HD 153 callable, 0 partial) follow the 8 October rule; S7.1 and S8 contradict it. The call-state lists also differ: Methods has "complete, partial, missing, ambiguous, invalid or failed"; the S5 table and Figure S1 have "absent", which the Methods list lacks.
Fix: Bring S7.1 and S8 into line with the Methods; add "absent" to the Methods list and define it.
Fix type: rewording
Effort: S
Prior review: PSR-005 closure contested

### SR-012 — "No fitted policy scored above the vote" is not true on every table, and two sensitivity rows were not recomputed
MINOR · G · R2 · CONFIRMED
Where the reader meets it: Abstract, "No fitted policy, including best-caller selection by nested cross-validation, scored above the vote."
Source: MS 52–53, 745–747, 807–808; SUPP 141–171, 229–259.
Evidence: On excluded loci three champion–challenger variants are compatible at 178/182 against the vote's 177/182 (SUPP 144–151). In the single-allele sensitivity table the vote is 110/118 with 117/118 callable, while the vote-stratum-gated policy is 113/118 with 118/118 callable and the logistic meta-consensus 112/118 (SUPP 239–241); both rows are identical to the primary table. A policy defined to "return plurality" cannot be callable where plurality is not, so those rows are frozen predictions, not a recomputation under the sensitivity scoring.
Fix: Qualify the sentence to the exact endpoint. Either recompute the two fitted rows under the sensitivity scoring or mark them as frozen.
Fix type: rewording plus new analysis from stored tables
Effort: S
Prior review: new

### SR-013 — A stale number in S1
MINOR · G · R2 · CONFIRMED
Where the reader meets it: S1, "The corresponding RNA-seq rates were 84.7%, 90.2%, 3.9% and 7.4% for CEU, YRI, FIN and GBR."
Source: SUPP 108–109 against SUPP 53–69.
Evidence: The S1 table gives RNA-seq CEPH resolved 23 + 19 + 17 = 59 of 69 = 85.5%. 84.7% is 61/72, the value before NA07000 was withheld (and the WES value). The sentence carries no `[RESULT:]` tag, which is why the audit did not catch it.
Fix: Correct to 85.5% from a registry row and tag it.
Fix type: rewording
Effort: S
Prior review: new

### SR-014 — The Methods account of the HG00096 re-run conflates three runs
MINOR · G, I · R3 · CONFIRMED
Where the reader meets it: Methods, "development subject HG00096 was re-run in September 2026 ... Workflow release 3.4.0 ... matched 11 of 15 stored WES calls".
Source: MS 181–186; SUPP 1108–1122; preface.
Evidence: S10 reports a September run (12 of 12 RNA-seq, 4 of 12 WES), release 3.3.0 (5 of 15) and release 3.4.0 (11 of 15 and 11 of 12). The main text gives only the last, reads as if 3.4.0 ran in September, and gives a different RNA-seq figure from the September run without saying why. Three identifiers are given for where the rule is implemented (preface 3.3.0; Availability 3.4.0; S11.2 commit `71f037d`).
Fix: One sentence per run with its date and denominator; say why the WES denominator is 12 in one run and 15 in the others; state how the three identifiers relate.
Fix type: rewording
Effort: S
Prior review: new

### SR-015 — Allele names lose their asterisk in the Word document
MINOR · G, K · R4 · CONFIRMED
Where the reader meets it: Supplementary S7 adjudication table, "C03:04+C03:04"; Supplementary Figure S6 legend, "Primary A02 confusion matrices".
Source: v3 document; SUPP 575–589, 1053–1056; `src/champhla_recovery/drive_document.py`.
Evidence: 44 table cells in the v3 document carry an allele with no asterisk, and the S6 legend reads "A02" and "A02/A68/A*69". The markdown is correct (`C*03:04+C*03:04`); the renderer treats paired unescaped asterisks as emphasis. The Phase 0 comparison ignored punctuation and so did not see it.
Fix: Escape asterisks in generated tables or make the renderer leave allele patterns alone; add a test that no rendered cell matches an allele without its asterisk.
Fix type: rewording (renderer and test)
Effort: S
Prior review: PSR-036 regressed

### SR-016 — Statements attributed to sources that the sources do not quite support
MINOR · J · R4 · CONFIRMED
Where the reader meets it: Background, "release 3.65.0 ... lists 46,652 named alleles"; Methods, "With few discordant subjects this cluster-t test is anti-conservative [36]".
Source: MS 73–74, 85–86, 92, 103–104, 124, 266–268, 352–353, 361, 431; reference list.
Evidence (`reference_check.md`; 51 references all exist, all 40 DOIs resolve; 48 of 66 statements supported): (1) 46,652 is the all-gene total including 1,231 non-HLA alleles (HLA alleles 45,421), and reference 8 does not contain the number. (2) Cameron and Miller address few clusters, not few discordant subjects; the application to this design is the authors' reasoning. (3) "Platform-specific errors [24]": in the source "platform" is the typing tool. (4) Reference 32 does not define suffixes S, C or A. (5) Reference 33 does not contain the HLA-HD hyphen statement; the demo PDF does. (6) "The most polymorphic region" where the source says "one of the most". (7) Chung et al. report Stevens–Johnson syndrome, not the wider category. (8) arcasHLA selects among alleles; it does not "reconstruct" them. (9) Gourraud et al. did perform confirmatory typing for 12 samples. (10) Reference 29 omits an author before "et al."; Clopper–Pearson, samtools, bwa, Apptainer and the GRCh38 realignment paper are used without a reference; the T1K placeholder statement has none. (11) The POLYSOLVER paper states IMGT v3.10; Table 1 gives 3.11.0 as the earliest consistent release, which deserves a clause.
Fix: Reword each to what its source says and add the missing references. `tests/test_reference_facts.py` enforces citation order, so add references in order of first citation.
Fix type: rewording
Effort: M
Prior review: new

### SR-017 — The circularity limitation names the wrong typing, and three limitations are missing
MINOR · B, H · R1 · CONFIRMED
Where the reader meets it: Limitations, "most panel callers were evaluated, and OptiType partly tuned, on 1000 Genomes samples typed with it".
Source: MS 314–323, 885–887.
Evidence: Only arcasHLA used the 2014 table as its truth. T1K and SpecHLA used the 2018 in silico file, the same file this paper uses to adjudicate; POLYSOLVER cites Erlich et al. 2011; OptiType does not cite Gourraud et al. (`reference_check.md`, problem 4). The Methods wording is accurate; the Limitations wording is not. Missing limitations: both assays are lymphoblastoid cell lines with high HLA expression, so RNA-seq results do not transfer to primary or tumour tissue; the RNA-seq and WES errors are the same loci, so the assays are not two observations; retention reflects which laboratory reported ambiguity strings (HLA-A retention is 100% for CEPH and 0% for FIN, GBR, TSI and PUR), not typing quality.
Fix: Correct the Limitations sentence; say in the adjudication paragraph that T1K and SpecHLA were evaluated against the second typing; add the three limitations.
Fix type: rewording
Effort: S
Prior review: PSR-056 closure contested

### SR-018 — Figure and legend defects
MINOR · G · R4 · CONFIRMED
Where the reader meets it: Figure 4 legend, "The mutually callable analysis reduces correlation induced by shared no-calls."
Source: MS 1180–1185; `scripts/generate_figures.py:1125`; SUPP 1016–1073.
Evidence: In Figure 4 the mutually callable phi is higher than the fixed-denominator phi in 9 of 16 pairs and lower in one. Supplementary Figure S8 prints "(fitted on the development set)" while S7.1 says the weights were fitted on the superseded sets. From the cold read of the images: Figure 3 panel A has ticks without labels; Figures 2 and 3 show neither subject counts nor interval type; S2 and S3 have overlapping labels; S4 uses a different axis range in every facet; S5 legends overprint data and text; S6 clips points at 100%; S1 has legend entries with no bars.
Fix: Correct the two statements; tidy the supplementary figures in the generator.
Fix type: rewording (figure code)
Effort: M
Prior review: PSR-041 closure contested

### SR-019 — The protocol history lacks a ledger of effects and two plain statements
MINOR · F · R2 · CONFIRMED
Where the reader meets it: Methods, "A protocol frozen on 31 August 2026, before truth was joined, named a two-thirds-guarded champion–challenger rule as the primary method ... and required the primary method to outperform its comparators."
Source: MS 438–476; Figure 1C legend; SUPP 728–731.
Evidence: See the ledger in section 6. Every change from 24 September onward that moved the RNA-seq headline moved it upward (110/120 to 113/118). Each is disclosed, but the effects are scattered across Methods, Discussion, S2 and the preface. Two things are not said plainly: that the frozen primary method did not outperform its comparators (on the current endpoint it is 142/153 against the vote's 143/153, and tied in RNA-seq), and that truth had already been joined to these caller outputs in the earlier analysis that fitted the champions and weights (S7.1), so "before truth was joined" and Figure 1C describe the confirmation protocol's join, not the analysts' first sight of truth.
Fix: Add a one-table ledger (date, change, effect on headline and verdicts) to the supplement; add the two sentences; describe the safeguards as procedural.
Fix type: rewording
Effort: S
Prior review: PSR-007 closure contested

### SR-020 — Exome caller rank follows database age exactly, and a bounded representability check is possible
MINOR · D · R1 · CONFIRMED (observation) / OPINION (weight)
Where the reader meets it: Methods, "native truth representability and the fraction of errors caused by database vintage remain unknown".
Source: MS 325–336, 624–628; SUPP 501–514; Table 1.
Evidence: WES concordance order (POLYSOLVER, OptiType, HLA-HD, SpecHLA, T1K) is the order of bundled database release (3.11.0, 3.13.1, 3.15.0, 3.38.0/3.51.0, 3.63.0). In T1K's own WES errors, 14 of 19 involve an allele whose second field is 100 or more; in HLA-HD's, 4 of 17 (`recompute3.py`). The repository holds verified native allele lists for the current deployment (`resources/caller_native/`), so membership of each reference allele in each caller's list can be tabulated even though the April databases are gone.
Fix: Mention the ordering; add the bounded representability table with its caveat.
Fix type: new analysis from stored tables
Effort: M
Prior review: new

### SR-021 — The "G-equivalent" flag is lenient; the C*02:02 and C*02:10 pair shares a P group, not a G group
MINOR · B · R1 · CONFIRMED
Where the reader meets it: Supplementary S7 adjudication table, column "G-equivalent to reference: yes".
Source: SUPP 569–590; `resources/ipd_imgt_hla/3.65.0/wmda/hla_nom_g.txt`.
Evidence: In the pinned release C*02:02:02:01 is in C*02:02:02G and C*02:10:01 in C*02:10:01G; the flag fires because some allele under each two-field name sits in the other's group (`refute/refutation.md`, claim 3). They do share P group C*02:02P. On the manuscript's lenient mapping, exact-endpoint concordance would be 147/153 and 114/118 for the vote (`recompute3.py`), with caller ranks unchanged.
Fix: Rename the column and endpoint to what they test ("G-compatible under a two-field mapping"), add P-group equivalence, and consider reporting every caller on it.
Fix type: rewording plus new analysis from stored tables
Effort: S
Prior review: new

### SR-022 — The exploratory patient cohorts cost more than they add
MINOR · H · R4 · OPINION
Where the reader meets it: Results, "exact-pair agreement between bulk RNA-seq and WES was 62/70 (88.6%; Wilson 95% CI 79.0–94.1%)".
Source: MS 771–792, 860–863, 913–923; SUPP 795–1005.
Evidence: No truth exists, so nothing here bears on the paper's question. The FIMM WES panel includes arcasHLA on WES, a combination the benchmark excludes, and the main text never names the FIMM callers. An 88.6% agreement for the germline genotype of one specimen is a warning sign that goes undiscussed (post-transplant chimerism and HLA loss in AML are not mentioned). These sections carry the paper's only patient-data governance risk and its submission-blocking text. `decisions/` records the author's choice to keep them.
Fix: Reduce to one paragraph and one supplementary section, or remove. The author's decision.
Fix type: rewording
Effort: S
Prior review: new

### SR-023 — Small consistency and cross-reference defects
MINOR · G · R4 · CONFIRMED (except where marked)
Where the reader meets it: Methods, "for the 106 subjects with calls in both assays".
Source: MS 201–217; SUPP 523, 1171, 1396–1404, 833, 851–855.
Evidence: (1) 106 subjects in both assays is the count before NA07000 was withheld and 105 after; the text does not say which is which, and "97 subjects shared all six" leaves eight unexplained (7 shared five, 1 shared four; `identity_check.tsv`). (2) Methods cites Supplementary S1 for 113/120 and for ambiguity width; S1 gives neither. (3) S11 refers to "Data and software availability"; the section is "Availability of data and materials". (4) The supplement restarts reference numbering. (5) Bootstrap replicates are 100,000 in Methods and 10,000 in S7; support strata use exact intervals in S5 and Wilson in S12.1 for the same loci. (6) Identical count vectors get slightly different intervals (Table 2, SpecHLA 73.9–86.5 against 73.9–86.4). (7) S12.4 scores 109 HLA-HD RNA-seq loci against 115 callable, unexplained (not checked). (8) S9.2 gives 7,179 locus rows; the panel table sums to 4,416 (not checked). (9) Table 2 lists strict majority and two-thirds separately for RNA-seq although they are identical for a four-caller panel.
Fix: Correct each in place.
Fix type: rewording
Effort: S
Prior review: new

### 4.4 EDITORIAL (4)

### SR-024 — "Within the uncertainty of" appears twice without its caveat
EDITORIAL · H · R2 · OPINION
Source: MS 59–60, 929–930.
Evidence: The refutation pass showed that every element of the concern (anti-conservative intervals, undetectable comparison, in-sample best caller, no equivalence) is already stated elsewhere in the manuscript, and that the bias runs in the harmless direction. What remains is that the phrase carries no information when nothing could be detected, and it stands alone in the Abstract's Conclusions and in the Conclusions.
Fix: Replace with the count ("differed from the best caller at two loci, one each way") or repeat the caveat.
Fix type: rewording · Effort: S · Prior review: new

### SR-025 — The Conclusions open with the caller benchmark
EDITORIAL · A · R4 · OPINION
Source: MS 927–928, 843–844, title.
Evidence: The manuscript does name its contribution, twice and consistently (MS 63–64, 945–947). But the first sentence of the Conclusions leads with "benchmark of six ... callers", which the Discussion disclaims and which is not the question the Background poses.
Fix: Lead the Conclusions with the evaluation; reconsider "auditable benchmark" in the title in light of SR-005.
Fix type: rewording · Effort: S · Prior review: new

### SR-026 — Monte Carlo is used where exact enumeration is cheap
EDITORIAL · F · R2 · CONFIRMED
Source: MS 420–423; SUPP 276–279, 349–352.
Evidence: The largest set has 23 nonzero subjects; 2^23 assignments enumerate in seconds. The reported T1K WES p of 1.00e-06 is the Monte Carlo floor; the exact value is 2.4e-07. No verdict changes.
Fix: Enumerate up to at least 25 subjects, or leave and say so.
Fix type: rewording · Effort: S · Prior review: new

### SR-027 — A Results abstract with no numbers
EDITORIAL · J · R4 · OPINION
Source: MS 43–57; `decisions/publication_route.json` (`abstract_numeric_performance_allowed: false`).
Evidence: BMC asks the Results section of the abstract for "the main findings". The abstract gives denominators but no concordance, while the Conclusions give both. An editor may ask for them. The recorded decision is defensible while the numbers are in flux; revisit it once SR-001 to SR-003 settle the headline.
Fix: Author's decision. · Fix type: rewording · Effort: S · Prior review: new

## 5. The case for rejection

The strongest honest case: the paper reports agreement with a 2014 reference at loci the
field corrected in 2017 and 2018, explains its null by a correlation that its own
supplement-grade analysis dissolves, and calls the correction mark undocumented when the
cited article documents it. The outputs it scores come from a run that cannot be
re-executed and that the authors' one reproduction attempt contradicted in exactly the
callers the vote is said to beat. The sample is a tenth of what is publicly available,
chosen by an unstated rule, and the pre-specified confirmation has not been run. What
remains is that the study could not tell the vote from the best caller, which is not a
result.

| Point | Reply readiness | Findings |
|---|---|---|
| The mechanism claimed is contradicted by the authors' own analysis | Ready once fixed: the corrected story is stronger than the original | SR-001 |
| "Undocumented" asterisk is documented; agreement is circular | Ready once fixed | SR-002 |
| Headline is agreement with a disputed reference | Needs work: corrected-reference results exist but endpoint status must be decided | SR-003, SR-021 |
| Callers were mis-deployed (T1K certainly) | No defence without a re-run | SR-004, SR-005 |
| Cannot be reproduced from reads | No defence without a re-run | SR-005 |
| Too small, selection unexplained, confirmation unrun | No defence without running the extension | SR-006 |
| RNA-seq difference is a missing file | Ready: reword and add mutually-available comparison | SR-007 |
| Not novel: Lee and Claeys did this | Ready: three of five claimed differences survive | SR-008 |
| Post hoc analysis plan | Ready: disclosure is already a strength; add the ledger | SR-019 |

## 6. Protocol-change ledger

Effects are from the decision records and artifacts named; values on superseded
denominators were not re-derived here and are not quoted.

| Date | Change | Effect on headline and verdicts | Disclosed at | Adequate? |
|---|---|---|---|---|
| 31 Aug | Protocol frozen: two-thirds-guarded champion–challenger primary; must outperform | On the current endpoint that method is 142/153 and 113/118 against the vote's 143/153 and 113/118 | MS 443–446 | Partly: the outcome is not stated plainly (SR-019) |
| 8 Sep (signed 18 Sep) | Plurality made primary; Holm within assay; WGS excluded | Primary method changed after accuracy was inspected | MS 447–450 | Yes |
| 18 Sep | Pre-registered abstention test | Lowered concordance; not adopted (`decisions/20260918_harmonisation_correction_result.json`) | MS 451–453 | Yes |
| 24 Sep | Abstain-all adopted as implemented; post hoc 2-point margin | RNA-seq vote 110/118 under this scoring on the current loci (SUPP 241) | MS 453–455; S2 | Yes |
| 28 Sep | Fail-closed truth parser; freeze before truth; cluster-t primary; separate Holm families | Denominators became 153 and 120 loci; family sensitivity shows the same four significant comparisons | MS 456–460; S3 | Yes |
| 8 Oct | Caller-declared homozygotes completed | RNA-seq vote 110 to 113; HLA-HD RNA-seq 97 to 110; arcasHLA 95 to 109; HLA-HD WES 110 to 126; strongest RNA-seq caller changes from OptiType to HLA-HD (`decisions/20261008_singleton_native_homozygosity.json`) | MS 462–464, 815–819; S2 | Yes, though the size of the effect is only in S2 and the preface |
| 8 Oct | NA07000 RNA-seq input withheld | 113/120 becomes 113/118; both removed loci were consensus errors | MS 208–217 | Yes |
| 9 Oct | Nested-CV comparator refitted | RNA-seq 99/118 to 106/118; significant becomes Holm p = 0.188 | MS 595–601; S7 | Yes |
| 9 Oct | Sign-flip test decides significance | Same four significant comparisons | MS 469–472 | Yes |
| 9 Oct | Second-typing adjudication (signed) and post hoc asterisk reading | No primary number changes | MS 717–729; S7 | No: phi on agreeing loci unreported (SR-001); asterisk called undocumented (SR-002) |

Direction: every change from 24 September onward that moved the RNA-seq headline raised it.
None was hidden.

## 7. Number cross-check

About 150 values were recomputed from the per-locus table and compared with Table 2, S2, S3,
S5, S7 and the text: every concordance and callability count, every wins and losses pair,
every raw and Holm sign-flip p-value, the Bonferroni CR1 intervals, all 16 phi values with
their 2×2 counts and both ranges and medians, the oracle headroom, the tie loci and the
support profiles. **All matched.** The independent vote re-implementation matched the
stored vote at 271 of 271 loci. The cold reader separately reconciled Table 2 against
Figures 2 and 3, the detectability thresholds, and the gene and population totals.

| Mismatch or unexplained difference | Where | Finding |
|---|---|---|
| RNA-seq CEU retention 84.7% against 59/69 = 85.5% | SUPP 109 | SR-013 |
| Two fitted-policy rows in the single-allele sensitivity table are not recomputed | SUPP 239–241 | SR-012 |
| "No fitted policy scored above the vote" against 178/182 and 177/182 | MS 52; SUPP 144–151 | SR-012 |
| HG00096: main text against S10 | MS 181–186; SUPP 1108–1122 | SR-014 |
| Allele asterisks absent in 44 document table cells | v3 document | SR-015 |
| 46,652 alleles is the all-gene total | MS 92 | SR-016 |
| Identical vectors, different interval bounds | MS 575, 577, 585 | SR-023 |
| 109 scored against 115 callable loci | SUPP 1404 | SR-023 (not checked) |
| 7,179 locus rows against a table summing to 4,416 | SUPP 833, 851–855 | SR-023 (not checked) |

## 8. Author-side blockers

No values are proposed. Status as of 12 October.

| Field or action | Blocks | Waits on |
|---|---|---|
| Author names, order, affiliations, ORCIDs, corresponding-author details | Title page | Co-authors |
| Authors' contributions by initials | Declarations | Co-authors |
| Funding and the funder's role | Declarations | Tanoli |
| Competing interests, confirmed by every author | Declarations | Co-authors |
| Acknowledgements, including whether CSC may be named | Declarations | Co-authors |
| Public-data ethics determination | Ethics statement | Host institution |
| FIMM and VenEx ethics committee and reference, FHRB identifier, collection period, demographics, consent basis, secure manifest checksum | Ethics statement; submission of S9 at all | FIMM data custodian |
| Approval of the AI-use and consent-for-publication wording | Methods; Declarations | Co-authors |
| Paper repository release tag, final commit and DOI | Availability statement; references 42 and 43 return 404 today | Umut, after the GitHub purge is confirmed |
| Workflow repository made public, with DOI | Availability statement; the parity-test link in S11.2 | GitHub Support purge |
| Signature on the confirmatory pre-registration | Running the extension (SR-006) | Umut |

Process text that must go before submission regardless of the values: "Submission remains
blocked pending ..." in the Limitations (MS 920–923) and S9.1, and the PROVISIONAL banners.

## 9. Reconciliation with the 8 October review

The earlier report and its TSV were opened only after the findings above were fixed.

**Findings here that contest an earlier closure**

| This review | Earlier finding | Why the closure is contested |
|---|---|---|
| SR-001, SR-002, SR-003 | PSR-054 (closed) | The adjudication was added, but phi on agreeing loci was computed and not reported, the asterisk was called undocumented, and the causal wording stayed |
| SR-005 | PSR-018, PSR-059 (closed) | The four non-reproduced HG00096 calls are unnamed and unexplained; the "7 April" revision cannot have produced the T1K rows |
| SR-008 | PSR-015 (closed) | Citations were corrected, but the novelty paragraph still claims two things Lee and Claeys already did |
| SR-011 | PSR-005 (closed) | The rule was changed in the Methods; S7.1 and S8 still state the old one |
| SR-015 | PSR-036 (closed) | Regressed: the Drive renderer drops unescaped asterisks |
| SR-017 | PSR-056 (closed) | The Limitations sentence attributes all callers' evaluation to the 2014 table |
| SR-018 | PSR-041 (closed) | Figure S8 still says "fitted on the development set" |
| SR-019 | PSR-007 (closed) | History disclosed; outcome of the frozen test and prior truth exposure not stated plainly |

**New in this review:** SR-004, SR-006, SR-007, SR-009, SR-010, SR-012, SR-013, SR-014,
SR-016, SR-020, SR-021, SR-022, SR-023, SR-024 to SR-027.

**Earlier closures checked and found to hold:** PSR-004 (NCI-60 citation), PSR-008 and
PSR-009 (nested-CV refit and family sensitivity), PSR-010 (cluster-t labelled descriptive),
PSR-011 (structured abstract), PSR-012 (tie sensitivity reported), PSR-013 (detectability
stated), PSR-014 (NCI-60 estimates withdrawn), PSR-017 (margin gate documented), PSR-027
(phi intervals and counts), PSR-030 (selection by the audit), PSR-031, PSR-037 (per-locus
table released), PSR-053 (reference typing described), PSR-055 (NA07000), PSR-058
(tie-break specified). The remaining closed findings were not individually re-tested.

**Still open, unchanged:** PSR-001, PSR-002, PSR-003, PSR-006, PSR-020, PSR-022, PSR-023,
PSR-034, PSR-051. All wait on co-authors, the GitHub purge or a release (section 8).

**Where I differ from the earlier review.** It rated the reference-error question MAJOR and
closed it on the addition of the adjudication. I rate what was left behind FATAL, because
the unreported result reverses the paper's stated mechanism and the "undocumented"
statement is false.

## 10. What referees will ask for

| Request | Feasibility | If absent | One-sentence reply |
|---|---|---|---|
| Re-run all callers from reads with a pinned release | Needs cluster; release 3.4.1 is deployed; about 17 minutes per exome on the one measured sample | Likely fatal for the "benchmark" framing | "All calls were regenerated with release X; Supplementary Table Y compares them cell by cell with the earlier outputs." |
| Run the confirmatory extension | Needs cluster and the pre-registration signature | A referee will not accept "planned" | "The pre-registered extension was run unchanged; results are reported whatever their direction." |
| More subjects, or all typed subjects | Needs cluster; storage is the constraint | Defensible if the selection rule is stated | "Subjects were drawn by rule R; scoring all typed subjects is outside the registered protocol." |
| Corrected-reference or P/G-group primary endpoint | From stored tables now | Raises SR-003 at review | "Reference-corrected and group-level results are reported beside the exact endpoint for every method." |
| Independent typing as truth (Buchkovich corrected Geuvadis truth; HPRC assemblies) | Needs new public data; overlap with these subjects unknown | Defensible as a limitation | "No orthogonal typing covers these subjects; the published corrections that do are used for adjudication." |
| T1K with its quality filter; SpecHLA mode stated | Workflow fix, then cluster | Raises SR-004 at review | "T1K calls now honour the authors' quality recommendation." |
| Allele-level vote, minimum-support variants, leave-one-caller-out | From stored tables now | Defensible | "Supplementary Table Z gives these variants; none changes the conclusion." |
| Class II, WGS, long reads | Needs new runs | Defensible as stated scope | "Out of scope; the workflow routes exist but are not evaluated." |
| Reconciliation with Claeys on shared samples | Needs their per-sample calls | Defensible | "Their accuracy is allele-level with group mapping; ours is genotype-level and exact, which accounts for the gap." |
| Remove the patient cohorts | Rewording | Removes the only governance risk | "Removed; they did not bear on the question." |

## 11. BMC Bioinformatics compliance checklist

Checked against the Research article guidelines fetched on 12 October 2026
(`link.springer.com/journal/12859/submission-guidelines/research-article`).

| Requirement | State | Gap |
|---|---|---|
| Title page: title, authors, affiliations, corresponding author | Not met | Author-side (section 8) |
| Abstract of at most 350 words with Background, Results, Conclusions | Met | 303 words; see SR-027 on numbers |
| Three to ten keywords | Met | Seven |
| Background, Methods, Results, Discussion, Conclusions | Met | — |
| List of abbreviations | Met | — |
| Declarations with all seven headings | Present | Six of seven hold provisional or missing author input |
| Ethics approval and consent to participate | Not met | Author-side; patient cohorts blocked |
| Consent for publication | Provisional | Wording awaits approval |
| Availability of data and materials | Partly met | Accessions and per-locus table present; both repository links return 404; no DOI |
| LLM use documented in the Methods | Met, provisional | Awaits co-author approval |
| Vancouver numbered references; web links in the list | Met | Housekeeping in SR-016; one inline URL in S11.2 |
| Figures, tables, additional files | Met | Additional file 1 described; rendering defect SR-015 |
| Length | No stated limit | 7,323 main-text words |

## 12. What could not be checked, and why

- Whether T1K's quality filter would remove the extra alleles: the development run's
  `*_genotype.tsv` files are not stored locally (SR-004).
- Which SpecHLA mode and which arcasHLA version ran in the development run: not recorded.
- Whether HLA-HD, OptiType and T1K were run on NA19130 and HG00174 at all (SR-007).
- The HLA-HD paper's evaluation data: the publisher returned 403 to automated access; a
  manual check in a browser is worth one try.
- Whether the earlier sealed hold-out of 38 subjects was formally opened (SR-006).
- Staleness of committed artifacts against HEAD: the verification gate was not run.
- The FIMM and VenEx aggregates against their sources: patient-level data were not opened.
- The Lee et al. and Claeys et al. quotations were retrieved through a page-fetch tool;
  re-read the PDFs before quoting them.

## 13. Appendix: findings considered and dropped or reduced

| Draft finding | Outcome | Reason |
|---|---|---|
| "Within the uncertainty of" rests on unreliable intervals (drafted MAJOR) | Reduced to SR-024, EDITORIAL | Every element is already stated in the manuscript; an anti-conservative interval is too narrow, so the bias makes the stated conclusion more true, not less |
| The paper does not commit to one contribution (drafted MAJOR) | Reduced to SR-025, EDITORIAL | It names its contribution twice in the same words; the residue is the order of one paragraph |
| The vote's lead is larger on the set-valued endpoint (drafted MAJOR) | Reduced to SR-009, MINOR | The paired test, once computed, is not significant, and the RNA-seq lead is mostly two subjects with absent rows |
| HLA-HD is artificially weak on exomes | Dropped | Lee et al. 2021 report 81.4% on the same data and metric; only the HG00096 observation remains (SR-005) |
| NA19130 is treated inconsistently with NA07000 | Dropped | NA07000 failed a stated identity rule that NA19130 passes |
| "5 of 15 errors are G-group equivalent" | Corrected to SR-021 | The common alleles share a P group, not a G group; the manuscript's flag is lenient |
| The reference table has 1,277 typed samples | Corrected | 1,277 rows, 1,267 individuals |
| The stored calls show haplotype loss in the weak callers | Dropped | A truth-free check finds almost no homozygous calls at heterozygous loci for any caller |
