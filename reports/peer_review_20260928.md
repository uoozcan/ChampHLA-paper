# Peer review — *PanelHLA: an auditable benchmark and plurality baseline for short-read HLA class-I genotyping*

**Review date:** 2026-09-28
**Materials reviewed:** `manuscripts/benchmark/manuscript.md` and `manuscripts/benchmark/supplementary.md` (both Sep 25); Figures 1–5 (PNG/PDF/SVG/TIFF); the generating artifacts under `artifacts/development_corrected/`, `artifacts/development_characterisation/`, `artifacts/development_limits/`; `src/champhla_confirmation/statistics.py` and `evaluation.py`; `README.md`, `THIRD_PARTY_NOTICES.md`, `AUTHOR_FIELDS_TO_COMPLETE.md`, `CITATIONS_TO_VERIFY.md`, `manuscripts/claim_audit.tsv`, `reports/peer_review_remediation_matrix.tsv`.
**Repository state:** branch `panelhla-rename-and-statistical-corrections`, HEAD `306ae81`.
**Recommendation:** **Major revision.**

Where an issue already appears on the authors' own remediation matrix I have marked it `[tracked: ACT-…]`. Issues without that marker are, as far as I can tell, new.

---

## 1. Summary assessment

This is an unusually candid manuscript. The authors discovered two upstream defects — a parser that converted a singleton allele report into a homozygous genotype, and a truth builder that picked one allele out of an ambiguous laboratory-typing string — corrected both, and accepted the consequence, which was that the evaluable cohort fell from 390 WES and 321 RNA-seq loci to 158 and 125, and that the headline result became negative. The paper now says plainly that equal-weight plurality does not beat the assay-best caller, that the primary rule was selected post hoc, that no external validation exists, and that raw-read-to-call reproducibility is outside the verified boundary. That discipline is rare and should survive revision intact.

The problem is that the manuscript has been edited so hard toward caution that it now under-reports its own evidence. Three analyses that are already computed and sitting in the repository — pairwise caller error correlation, the detectability/minimum-attainable-*p* table, and the nested-CV best-single-tool comparator — are absent from the main text. Those three are, respectively, the mechanistic explanation for the negative result, the honest statement of what this design could ever have detected, and the single comparison that most supports the authors' thesis. Adding them would make the paper both more informative and more defensible, without adding a claim.

There is also one genuine internal inconsistency in the statistics that must be resolved before this can be published in any venue (MAJ-08): the Bonferroni-adjusted bootstrap intervals and the Holm-adjusted sign-flip tests are computed over the same comparator families and reach opposite conclusions for at least two comparators, and Figure 2 renders the contradiction visibly.

**On venue.** The authors have not yet chosen one, so this review is venue-neutral, but the framing question is worth stating: as a conventional research article the paper is weak, because the method it proposes does not outperform a single existing caller and the evaluable cohort is 158/125 loci. As a Resource or data-descriptor — where the contribution is the audited benchmark, the fail-closed release gate, the singleton-abstention convention and the ambiguity-respecting truth parser — it is viable and the negative comparison is acceptable, even valuable. The current title already commits to the resource framing ("an auditable benchmark and plurality baseline"). I would encourage the authors to commit to it fully, which mainly means promoting the audit machinery into the Results and retiring any residual presentation of PanelHLA-Consensus as a method being proposed for use.

**Strengths worth preserving in revision**

- The fixed-denominator convention (missing or non-callable predictions score incorrect) with callability reported separately. This is the right choice and many HLA benchmarks get it wrong.
- Singleton abstention, with duplication allowed only where a caller-native format declares homozygosity (Methods, lines 156–171).
- Truth ambiguity respected rather than collapsed, with the source checksum-pinned (lines 115–131).
- Explicit separation of `primary` / `descriptive_comparator` / `exploratory_fitted` scopes, applied consistently across Table 1, S2, S3 and Figure 2.
- The fail-closed extension readiness gate, and the willingness to report that it is closed (lines 241–251).
- Quarantining rather than deleting the invalid WGS material.

---

## 2. Major concerns

### 2.1 Statistical rigour

---

**MAJ-08 — The Bonferroni-adjusted intervals and the Holm-adjusted tests contradict each other.**

*Location:* Methods lines 197–212; Results lines 263–266; Table 1 note line 270; supplementary S3 lines 69–107 (rows `RNA-seq | BestSingleTool_nestedCV` and `WES | Two-thirds consensus`); Figure 2 and its legend (lines 416–421). Implementation: `src/champhla_confirmation/evaluation.py:352–374`.

*Problem.* The simultaneous intervals are built by passing `alpha = 0.05 / family_size` to the subject-cluster percentile bootstrap, where `family_size` is the count of comparators in that modality — the *same* 13 (WES) and 12 (RNA-seq) families over which Holm is applied. Bonferroni is uniformly more conservative than Holm. It should therefore be impossible for a Bonferroni-adjusted interval to exclude zero while the Holm-adjusted test fails to reject. Two comparators do exactly that:

| Assay | Comparator | Bonferroni 95% CI (points) | Holm *p* | Marked significant? |
|---|---|---|---|---|
| RNA-seq | `BestSingleTool_nestedCV` | **+0.78 to +18.85** | 0.141 | no |
| WES | Two-thirds consensus | **+0.58 to +10.69** | 0.3125 | no |

Several further rows report intervals with an endpoint at exactly `0.00` (`ChampionChallenger` RNA-seq `0.00 to 3.88`; `MVFlooredCC` RNA-seq `−6.84 to 0.00`; `MVFlooredCC` and `MetaConsensus` WES `0.00 to 0.00`), which is a second symptom of the same cause — the bootstrap's support in the far tail is discrete and very coarse.

*Why it matters.* The paper's central methodological claim is a negative one: that the data "do not support 'matches,' 'equivalent' or 'non-inferior'" (line 266). That claim is carried entirely by these intervals. If the intervals disagree with the exact tests computed on the same data, a referee cannot take either at face value, and the post-hoc non-inferiority column in S3 — which is decided from the same lower bound (`evaluation.py:374`) — inherits the problem. Figure 2 makes the contradiction visible to any reader: two grey (non-significant) markers sit with their whole interval on one side of the zero line.

*Suggested fix.* Diagnose, then state the resolution explicitly in Methods. The most likely explanation is that the percentile cluster bootstrap is anti-conservative in the extreme tail here — with 64 WES and 53 RNA-seq clusters, a Bonferroni-adjusted two-sided interval sits at the 0.19th and 99.81st percentiles, which with so few clusters is driven by a handful of distinct resample configurations — while the sign-flip test is exact but coarsely discrete. Concretely:

1. Replace the percentile interval with BCa, or with a subject-level *t*-interval on the paired per-subject difference, and check whether the contradiction resolves.
2. If it does not, report both and say which governs. My recommendation, consistent with how the authors resolved the earlier CI-versus-Holm disagreement, is that the exact test governs and the interval is descriptive; say so in one sentence in Methods and repeat it in the Figure 2 legend.
3. Add a sentence to the Figure 2 legend explaining why an interval may exclude zero without the test rejecting, so the visual contradiction is pre-empted rather than left for the reader to find.

---

**MAJ-09 — The design's detection limits are computed but not reported, and they are the most important thing the paper can say.**

*Location:* supplementary S3 lines 109–111 (the current one-sentence treatment); S7 lines 236–241. Artifact: `artifacts/development_limits/detectability.tsv`.

*Problem.* S3 currently says "Seventeen of the 25 comparisons had too few discordant subjects for any two-sided test to attain unadjusted *p* < 0.05." That is true but understated, and the artifact that backs it contains far more. `detectability.tsv` carries per-comparator `min_attainable_p`, `significance_reachable_uncorrected` and `significance_reachable_holm_worst_case`. It shows that for the three comparisons a reader actually cares about, no possible outcome could have reached significance:

| Assay | Comparator | Discordant subjects | Min attainable *p* | Reachable under Holm? |
|---|---|---|---|---|
| WES | POLYSOLVER | 3 | 0.25 | **no** |
| WES | OptiType | 3 | 0.25 | **no** |
| WES | `BestSingleTool_nestedCV` | 3 | 0.25 | **no** |
| RNA-seq | OptiType | 3 | 0.25 | **no** |
| WES | Two-thirds consensus | 6 | 0.03125 | **no** (reachable uncorrected only) |

*Why it matters.* This converts "we did not find a difference" into "this design was structurally incapable of finding one for these comparators" — a categorically stronger and more useful statement, and precisely the distinction the authors are trying to draw throughout the paper. It also pre-empts the obvious referee objection that non-significance is being quietly leaned on.

*Suggested fix.* Promote `detectability.tsv` to a numbered supplementary table (suggest S3b), and add one sentence to the Results at line 266 and one to the Limitations at lines 386–388: *"For the comparisons against POLYSOLVER, OptiType and nested-CV best-single-tool selection, the number of discordant subjects was such that no outcome could have produced a Holm-adjusted p below 0.05; non-significance for these comparators reflects the design, not the data."*

---

**MAJ-10 — The Holm families include degenerate comparators and mix pre-specified with exploratory ones.**

*Location:* Methods lines 205–207; supplementary S3 lines 73–75. Implementation: `statistics.py:167–181`, `evaluation.py:250–252`.

*Problem.* `holm_adjust` takes the family size from the number of rows passed to it, and the families passed are "every comparator in the modality." Three of those rows are degenerate on this cohort — WES `MVFlooredCC` and `MetaConsensus`, and RNA-seq `TwoThirdsGuardedCC` — each with 0 wins, 0 losses, a delta of exactly 0.00 and an interval of `0.00 to 0.00`. They are identical to the primary rule at every locus and can never reject. Including them inflates the Holm multiplier for every comparator that can. This is the same class of error as the self-comparison rows removed from the families earlier in September, recurring in a different form.

Separately, the families mix three logically distinct groups: five/four individual callers, two transparent vote thresholds, and six exploratory fitted policies. Correcting the scientifically primary caller comparisons for multiplicity against a set of exploratory policies the authors themselves decline to interpret is difficult to justify.

*Why it matters.* Family definition is the most contestable free parameter in a multiple-comparison analysis, and this one is currently defined by an implementation detail rather than by a stated principle.

*In fairness, I checked the consequence and it is limited.* Re-running Holm within plausible alternative families — callers only (m = 5 WES, m = 4 RNA-seq), vote thresholds only (m = 2), exploratory only — flips **no** significance verdict. WES HLA-HD, SpecHLA and T1K remain significant; RNA-seq arcasHLA, HLA-HD and T1K remain significant; WES two-thirds remains non-significant at *p* = 0.0625 in a two-member family. So this is a transparency and justification fix, not a correctness failure, and the revision should present it that way.

*Suggested fix.* (a) Exclude comparators with zero discordant subjects from the family, documenting the rule as the authors already documented `panels.REFERENCE_ALIASES`; (b) define families by scope — `descriptive_comparator` and `exploratory_fitted` corrected separately — and state the principle in Methods; (c) report, in one sentence, that no verdict changes under the alternative family definitions. Point (c) is worth more to the reader than either (a) or (b).

---

**MAJ-11 — Resampling parameters are not reported, and the interval method is not appropriate to the cluster count.**

*Location:* Methods lines 197–208; Table 1 note line 270; supplementary S2 lines 33–35, S3 lines 74–75.

*Problem.* The manuscript never states the number of bootstrap resamples or any seed. From the code these are `B = 100,000` with seeds 20260831 (`cluster_bootstrap_ci`), 20260925 (`cluster_bootstrap_ratio_ci`) and 20260921 (`NONINFERIORITY_SEED`), and 1,000,000 sign-flip iterations with seed 20260926 and `exact_max = 20`. The manuscript reports the sign-flip iteration count and the exact/Monte Carlo threshold but not the seed, and reports nothing at all for the bootstrap. Given that `README.md:96` documents a `BOOTSTRAP=2000` developer mode, a reader has no way to know which figure generated the published intervals.

Relatedly, the number of clusters is small (64 WES subjects, 53 RNA-seq subjects, each contributing one to three loci) and is never stated in the statistics paragraph where it matters.

*Why it matters.* Percentile intervals at Bonferroni-adjusted levels require both a large `B` and enough clusters for the tail to be meaningful; neither quantity is currently visible to the reader, and the cluster count is the binding constraint. This is also the mechanism most likely responsible for MAJ-08.

*Suggested fix.* In Methods, state: the number of subjects entering each bootstrap; `B = 100,000`; the seeds; that intervals are percentile intervals on a locus-weighted ratio estimator with a random denominator; and the sign-flip seed. Replace the percentile method with BCa or a subject-level *t*-interval, or justify the percentile choice explicitly at this cluster count.

---

**MAJ-16 — The interval estimand and the test estimand differ, and the difference is not stated.**

*Location:* Methods lines 197–205.

*Problem.* The intervals are locus-weighted (`statistics.py:101–139` resamples subjects and forms a ratio with a random denominator), while the tests operate on subject-aggregated differences (`statistics.py:184–188`), which weights subjects equally regardless of how many loci each contributes. The manuscript states the first ("the reported estimand remains locus weighted", line 200) and not the second, so a reader will reasonably assume both address the same quantity.

*Why it matters.* With subjects contributing between one and three loci, the two weightings are not equivalent, and the discrepancy is a candidate contributing explanation for MAJ-08.

*Suggested fix.* Add one sentence: *"Intervals estimate a locus-weighted concordance difference; the paired tests are computed on subject-aggregated locus differences and therefore weight subjects equally. The two estimands coincide only when subjects contribute equal numbers of evaluable loci."* Consider reporting a subject-weighted interval as a sensitivity analysis.

---

### 2.2 Benchmarking and validation

---

**MAJ-05 — Pairwise caller error correlation is computed and never reported; it is the missing explanation for the whole result.**

*Location:* Discussion lines 340–368 (where it belongs); Results section at lines 313–326. Artifact: `artifacts/development_characterisation/caller_error_correlation.tsv`.

*Problem.* The repository contains a complete pairwise error-correlation table that appears nowhere in the manuscript or supplement. It shows that panel callers fail together:

| Assay | Caller pair | φ (error correlation) | Both wrong |
|---|---|---|---|
| RNA-seq | HLA-HD / T1K | 0.87 | 24 |
| RNA-seq | arcasHLA / HLA-HD | 0.85 | 22 |
| RNA-seq | arcasHLA / T1K | 0.82 | 24 |
| WES | OptiType / POLYSOLVER | 0.77 | 9 |
| WES | HLA-HD / T1K | 0.62 | 31 |

*Why it matters.* An equal-weight vote extracts information only to the extent that its members err independently. These φ values say they largely do not, which is *the* reason plurality cannot beat the assay-best caller, and the reason the oracle headroom is only four (WES) and three (RNA-seq) recoverable errors against seven and eight that no caller solves (S7, lines 225–228). At present the paper reports the symptom (limited headroom) without the diagnosis, and the Discussion's statement that "selecting among the same outputs cannot fix loci where every caller is wrong" (lines 364–365) is left as an assertion when the authors hold the evidence for it.

*Suggested fix.* Add the table as a supplementary table (suggest S7b) and a short Results paragraph, then rewrite the Discussion paragraph at lines 364–368 around it. Suggested framing: *"Panel callers erred in a strongly correlated manner (φ = 0.62–0.87 for the RNA-seq pairs; 0.32–0.77 for WES), so the panel supplies less independent evidence than its size suggests. This bounds what any output-level integration can achieve and explains the small oracle headroom reported above: the gains available to a vote are limited less by the voting rule than by the shared failure modes of the callers being voted over."* This single addition converts the paper's negative result from a disappointment into a finding.

---

**MAJ-04 — The most policy-relevant comparator is absent from the main table and the entire Results narrative.**

*Location:* Table 1 (lines 268–289); Results lines 253–294; contradicted by `README.md:38–40`.

*Problem.* `BestSingleTool_nestedCV` appears only in supplementary S2 and S3. It is missing from Table 1, from Figure 1, and from every sentence of the Results. Yet it is the comparator that answers the question a practitioner actually asks — *should I run five callers and vote, or just pick the best one?* — and on RNA-seq it is the paper's strongest supportive result: consensus +8.80 points, 13 wins to 2 losses, with a Bonferroni interval of +0.78 to +18.85. `README.md:40` states "None is omitted from the main comparison," which the manuscript contradicts.

*Why it matters.* Omitting a comparator that favours your method is unusual, but it leaves the paper without an answer to its central practical question, and a referee who finds the comparator in the supplement will wonder why it was moved there. The honest treatment is to report it in Table 1 together with the reason it cannot be leaned on (it is fitted, and its Holm-adjusted *p* is 0.141 — see MAJ-08, which this row also exemplifies).

*Suggested fix.* Add `BestSingleTool_nestedCV` to Table 1 and to Figure 1 with its `exploratory fitted` scope label, and add a Results paragraph after line 294. Suggested text: *"Against nested-CV selection of the single best caller, PanelHLA-Consensus was 1.27 points higher in WES (145/158 versus 147/158) and 8.80 points higher in RNA-seq (103/125 versus 114/125, 13 subject-level wins to 2). Neither difference reached Holm-adjusted significance within its comparator family, and nested-CV selection is a fitted development analysis; the comparison indicates that a vote need not be inferior to caller selection, not that it is superior to it."* Also correct `README.md:40`.

---

**MAJ-06 — The comparator panel omits every methodologically distinct caller class, which limits what the benchmark resource can serve.**

*Location:* Methods lines 133–139; Limitations lines 378–382; Discussion line 360. `[tracked: ACT-MAJ-007, blocked_external]`

*Problem.* The panel is five WES and four RNA-seq callers drawn from two algorithmic families (alignment/dictionary scoring and abundance/EM, plus OptiType's integer programming). Graph and pangenome approaches — HLA\*LA, HISAT-genotype — and assembly-based Kourami are absent, as is seq2HLA. The manuscript states this honestly in three places and makes no claim about them, which is correct conduct. But it interacts with MAJ-05: the callers that *are* present are exactly the ones most likely to share failure modes, and a panel drawn from one or two algorithmic families is the worst case for an ensemble.

*Why it matters.* For a paper positioned as a benchmark resource, the value to the community scales with comparator coverage. As it stands the resource covers a historical deployment rather than the current tool landscape, which limits its shelf life.

*Suggested fix.* I accept that execution is blocked on container availability and CSC access, and I am not asking for new callers as a condition of acceptance. I am asking for two things that are not blocked: (a) connect the panel's narrow algorithmic coverage to the error-correlation result from MAJ-05 explicitly in the Discussion — *"the panel spans two algorithmic families, which is the condition under which correlated error is most expected"*; (b) state in the Limitations what a reader should and should not use this resource for, in one sentence.

---

**MAJ-07 — No computational cost is reported for a method whose entire cost is that it runs five callers.**

*Location:* absent; belongs in Methods (after line 154) and Discussion.

*Problem.* PanelHLA-Consensus requires executing the whole panel. The paper reports no runtime, CPU-hours, memory footprint or storage for any caller or for the ensemble.

*Why it matters.* The paper's own results show no concordance gain over POLYSOLVER (WES) or OptiType (RNA-seq). A reader deciding whether to adopt the approach therefore needs the cost side of a trade-off whose benefit side is measured at zero. Benchmark and resource venues generally require this.

*Suggested fix.* Report per-caller and total wall-clock and CPU-hours for a representative sample on stated hardware, even approximately and even if recovered from historical scheduler logs rather than re-measured. If historical execution metadata is genuinely unrecoverable — which would be consistent with the missing container digests — say so explicitly in the Limitations rather than omitting the topic.

---

### 2.3 Scientific validity and methodology

---

**MAJ-01 — No ambiguity-tolerant scoring is attempted, discarding 60% of the requested loci.**

*Location:* Methods lines 115–131; Results lines 232–239; supplementary S1 lines 7–28. `[partially tracked: ACT-MAJ-002]`

*Problem.* A locus is retained only when the reference ambiguity string collapses to exactly one unordered two-field genotype. This excludes 232/390 WES and 196/321 RNA-seq loci. The authors describe the consequence accurately and restrict inference to uniquely resolved loci. But the standard alternative in HLA benchmarking — scoring a call as correct when it is a member of the reference ambiguity set, or scoring at P-group or G-group resolution, where most 2014-era sequence-based-typing ambiguity resolves — is not attempted, and `ACT-MAJ-002` records that a set-valued truth builder already exists in the codebase.

*Why it matters.* This is the largest single determinant of the paper's statistical power, and therefore the root cause of MAJ-09. Recovering even half the excluded loci would materially change which comparisons are detectable. It is also the first thing a referee with HLA typing experience will ask, because ambiguity-set scoring is routine practice rather than a novel proposal, and because two-field exact matching against a 2014 reference is known to be harsh.

*Suggested fix.* Run the set-valued truth builder and report, as a clearly labelled sensitivity analysis on all 390 and 321 requested loci: (a) concordance under ambiguity-set membership; (b) concordance at G-group resolution. Keep the exact two-field analysis as primary — that choice is defensible and should not change — but the sensitivity analysis tells the reader whether the exclusion is load-bearing for the conclusions. If the two analyses agree in ranking, that is a substantial strengthening of the paper at no cost to its caution. Add one line to S1 with the count of loci recoverable under each relaxation.

---

**MAJ-03 — Exclusion bias is asserted as a limitation but never tested, though the data to test it are in hand.**

*Location:* Methods lines 129–131; Limitations lines 373–375. `[partially tracked: ACT-MIN-016]`

*Problem.* The manuscript twice states that extensive exclusion "could be non-random" and "may select easier or older alleles," and stops there. The selection manifest records every excluded subject-modality-gene key (S1, line 26), so the comparison is available.

*Why it matters.* An unexamined 60% exclusion is the kind of thing that sinks a benchmark paper in review, because the reviewer cannot tell whether the retained set is representative or is the easy subset. A short empirical check converts a vulnerability into a documented property of the resource — and if the retained set *is* biased toward common alleles, saying so precisely is far better than the current vague hedge.

*Suggested fix.* Add a supplementary table comparing retained versus excluded loci on: gene (A/B/C), source population, and truth-allele frequency within the 1000 Genomes table. Then replace the hedge at lines 373–375 with the measured result. If the retained set is enriched for common alleles, state the enrichment factor, exactly as the harmonisation-correction analysis did for placeholder homozygosity.

---

**MAJ-02 — Database heterogeneity is acknowledged but its effect on the error count is never quantified.**

*Location:* Methods lines 141–154; supplementary S6 lines 199–217; Limitations lines 378–382.

*Problem.* The manuscript states clearly that caller resources span IPD-IMGT/HLA 3.11.0 to 3.63.0, that normalisation was syntactic two-field reduction without release-membership verification, and that no representability-adjusted claim is made. All correct. But the reference is the 2014 table while caller databases run to 3.63.0, and IPD-IMGT/HLA renames a two-field allele to three fields once subtypes appear. A call of `A*32:55` scored against a truth of `A*32:55:01` — or the reverse — is a nomenclature artefact counted as a genotyping error.

*Why it matters.* There are only 11 errors per assay. If even two or three are nomenclature artefacts, the ranking of consensus against POLYSOLVER (a one-locus gap) and against OptiType (a zero-locus gap) is not robust to a purely clerical effect. The paper's headline comparisons turn on differences of this magnitude.

*Suggested fix.* The tooling exists (`champhla_confirmation.imgt_release`, and `resolve_caller_database_release`). For each of the 22 errors, check whether the predicted and truth two-field designations are linked by a rename or split across releases between the 2014 table and the caller's own database vintage, and report the count. Compare at two fields throughout — comparing full designations is the known trap here. If the count is zero, that is a strong sentence for the Results. If it is not zero, it belongs in the Limitations with the affected comparisons named.

---

### 2.4 Reproducibility and completeness of methods

---

**MAJ-12 — Six exploratory policies are tabulated by code identifier and never defined.**

*Location:* Methods lines 184–187 (the only mention); supplementary S2 lines 37–67, S3 lines 79–107, S7 lines 230–235; Figure 2.

*Problem.* `BestSingleTool_nestedCV`, `ChampionChallenger`, `FamilyGatedCC`, `MVFlooredCC`, `MetaConsensus` and `TwoThirdsGuardedCC` appear as raw internal identifiers in two supplementary tables and one figure. The only description in the manuscript is the single sentence at lines 184–186 naming them. Nothing states what any of them computes. `MVFlooredCC` is reported as scoring 117/125 on RNA-seq — the highest value anywhere in the paper — with no indication of what it does.

*Why it matters.* A reader cannot judge whether an exploratory policy is a plausible method or an artefact of fitting, and therefore cannot calibrate how much to discount it. This also affects MAJ-10: if the reader cannot tell what is in the Holm family, they cannot assess whether the family is reasonable. Presenting internal camelCase identifiers in a published table is additionally a presentation problem (see MIN-14).

*Suggested fix.* Add a supplementary subsection (suggest S7a) with two to three sentences per policy: what it computes, what was fitted on development data, and why it is therefore exploratory. Give each a plain-language display name for the tables and figures, keeping the code identifier in a parenthetical so the artifacts remain traceable. Recommended treatment of the champion–challenger family in particular: state that it was the project's original primary method and was demoted to an ablation by the September amendment — that history explains the family's presence and is currently invisible to the reader.

---

### 2.5 Novelty, positioning and clarity

---

**MAJ-13 — The paper never tells the reader what to do.**

*Location:* Discussion lines 340–368; Conclusions lines 396–405.

*Problem.* The Discussion establishes that plurality is transparent, traceable and not better than the assay-best caller, and stops. It does not say whether a reader should run the panel and vote, run POLYSOLVER on WES and OptiType on RNA-seq, or do something else. The Conclusions describe the contribution as "a fail-closed, artifact-traceable evaluation" without operational guidance.

*Why it matters.* A resource paper earns citations by being useful. Given the results as they stand, there is a genuinely defensible recommendation available — and making it would sharpen rather than weaken the paper.

*Suggested fix.* Add a short closing Discussion paragraph making the recommendation explicit. Suggested substance, which follows from the authors' own numbers: on a single assay with a known-good caller, the evidence here does not support running a panel to vote; the value of the vote is that it does not require knowing in advance which caller is best for the assay at hand, which matters when assay, capture or population differs from the benchmarked setting. Pair that with the error-correlation result from MAJ-05: a vote over callers with correlated errors buys robustness, not accuracy.

---

**MAJ-14 — The Introduction never says why HLA typing matters, and never states an aim.**

*Location:* Introduction lines 56–86.

*Problem.* The Introduction opens on polymorphism and short-read difficulty, moves to tool differences, then to benchmarks and prior ensembles, then to the two integrity findings. It never states the clinical or biological motivation — transplant donor matching, drug hypersensitivity risk, disease susceptibility, neoantigen prediction — and it never states the study's aim in a dedicated sentence. `CITATIONS_TO_VERIFY.md` records that exactly this paragraph, with citations (Chung 2004; Mallal 2008; Petersdorf 2007; Matzaraki 2017; Schumacher and Schreiber 2015), existed before the 2026-09-24 remediation and was cut.

*Why it matters.* Every general bioinformatics venue expects an Introduction to establish stakes before methodology. A reader outside immunogenomics currently has no reason to care by the end of paragraph one, and the absence reads as an oversight rather than as restraint.

*Suggested fix.* Restore a two-to-three sentence opening paragraph with those citations, then add an explicit aim sentence at the end of the Introduction, after line 78: *"Here we ask whether an equal-weight plurality vote over a fixed panel of heterogeneous callers improves two-field genotype concordance relative to the individual callers in the panel, under a fixed-denominator evaluation with auditable truth selection."* Note that restoring motivation does not restore any claim — the cut appears to have been collateral damage from removing the unsupported "a large literature assumes…" sentence, and only the latter needed to go.

---

### 2.6 Data presentation

---

**MAJ-15 — Pooling reduced support fractions puts single-voter loci in the "unanimous" stratum.**

*Location:* Results lines 304–311; supplementary S5 lines 173–192; Figure 5 and legend lines 432–436.

*Problem.* Support strata are keyed on the reduced fraction, and the `support_profiles` column shows what that merges. In RNA-seq the "1/1" stratum (reported as unanimous, 104/108, 96.3%) pools **12 loci at which exactly one caller was callable** with 96 loci at genuine 4/4 unanimity. In WES the "1/1" stratum pools 8 loci at 3/3 with 88 at 5/5. Figure 5 plots all of these at 100% support on the x-axis.

*Why it matters.* A locus decided by a single caller is the *weakest* evidential state the pipeline can produce, and it is being displayed as the strongest. For RNA-seq that is 12 of 125 loci — nearly 10% of the assay — and it inflates the apparent concordance of the high-support stratum, which is the stratum a reader would use to decide whether high support is trustworthy. The authors are careful to say these strata are not calibrated probabilities; the problem is not the calibration caveat, it is that the stratum definition conflates two different things.

*Suggested fix.* Stop reducing the fractions. Report support as *k* of *n* callable callers with *n* retained, and either facet Figure 5 by *n* or encode *n* as point size with a legend. At minimum, split the single-voter loci into their own stratum and report it separately — the authors already do exactly this for the 0/0 no-evidence locus (Figure 5 annotation, legend line 435), so the precedent and the display convention are established.

**Related, and worth stating as a finding rather than a defect:** support is markedly non-monotonic and the text does not say so. WES runs 40% → 100% (3/3), 60% → 57.1% (4/7), 67% → 100% (2/2), 75% → 100% (7/7), 80% → 88.4% (38/43), 100% → 96.9% (93/96). Given that the paper's thesis is that vote support is *not* calibrated confidence, non-monotonicity is direct evidence for that thesis and should be stated in the Results at line 308 and reflected in the Figure 5 legend.

---

## 3. Minor concerns

### Clarity and scientific writing

**MIN-01 — Abstract length and structure.** Lines 19–52; approximately 330 words. Many venues cap abstracts at 250 and several require structured headings. Tighten by cutting the methodological hedging in lines 44–48, which is repeated verbatim in the Results and Discussion.

**MIN-02 — "Five WES callers and four RNA-seq callers" overstates the panel.** Line 32. Only **six distinct** callers exist; HLA-HD, OptiType and T1K are in both panels. A reader scanning the abstract will count nine. Rewrite: *"…recovered outputs from six callers deployed across two assay-specific panels (five for WES, four for RNA-seq)."*

**MIN-03 — Title should name the loci.** Line 1. "HLA class-I" implies A, B, C, E, F and G; only the three classical loci were evaluated. Rewrite: *"…for short-read classical HLA class I (HLA-A, -B, -C) genotyping."*

**MIN-04 — Ambiguous count in the singleton paragraph.** Lines 299–300: "three HLA-HD, OptiType and T1K rows were absent" reads as three rows in total. S5 shows three rows absent *for each* of the three callers. Rewrite: *"…three rows were absent for each of HLA-HD, OptiType and T1K."*

**MIN-05 — Duplicated word.** Supplementary S8, lines 252–253: "No WGS concordance, ranking, concordance or denominator is reproduced." Delete the second "concordance"; the intended third term was probably "accuracy" or "denominator."

**MIN-06 — Terminology drift.** The primary method is referred to as "PanelHLA-Consensus," "equal-weight plurality," "plurality," "the primary method" and "the vote," sometimes within one paragraph (e.g. lines 340–347). Fix a single display name — PanelHLA-Consensus — and use "equal-weight plurality" only where the *rule* rather than the *method* is meant. Similarly, standardise on "concordance" throughout and reserve "accuracy" for where it is formally meant; the manuscript is mostly consistent here but `README.md` and the artifact field names are not.

**MIN-07 — Undefined jargon on first use.** "Fixed-denominator" (line 39) and "called-only" (line 194) carry the whole evaluation design and are used before being defined. Define both at first use in the Abstract, in one clause each.

**MIN-08 — "Recovered" is load-bearing and never defined.** Used at lines 29, 32, 92, 137, 141, 158 and throughout S6 to mean, apparently, "produced by a historical workflow that cannot now be re-executed." Define it once in Methods at line 92 and then use it consistently.

**MIN-09 — Repetition of the non-equivalence caveat.** The point that non-significance is not equivalence appears at lines 44–46, 253 (heading), 265–266, 291–294, 421 and S3 lines 109–111. Two placements — Results and the Figure 2 legend — suffice. The current density makes the paper read defensively and costs space that MAJ-05 and MAJ-09 need.

**MIN-10 — Declarative section headings.** Results headings are full sentences asserting conclusions ("Truth-source audit materially changed the evaluable cohort", line 232). This is acceptable at some venues and disallowed at others. Flagging for the authors to check against the chosen venue's style; no change needed yet.

### Citations and references

**MIN-11 — Geuvadis is never cited.** Referenced as a primary data source at lines 33, 93, 106 and 460 with no citation anywhere. Add Lappalainen *et al.* (2013), *Nature* 501:506–511, at line 93.

**MIN-12 — Orphan reference.** `1000 Genomes Project Consortium (2015)` appears in the reference list (lines 478–479) and is cited nowhere in the text. Either cite it at line 93 alongside Geuvadis or remove it. `CITATIONS_TO_VERIFY.md` §3 flags a broader version of this problem; the current reference list is clean apart from this one entry, so the earlier eight-uncited-references issue appears to have been resolved by the remediation cut.

**MIN-13 — Nomenclature standard not cited.** Two-field resolution, expression suffixes (N, L, S, Q, C, A) and P/G groups are defined at lines 158–165 with no citation. Add Marsh *et al.* (2010), *Tissue Antigens* 75:291–455. The substance of the definition is correct, including the frequently-muddled point that P and G are group designators rather than expression suffixes — that distinction is worth keeping exactly as written.

**MIN-14 — arcasHLA citation year.** Line 511: cited as (2019) with *Bioinformatics* 36, 33–40, which is the 2020 issue. Use 2020 for consistency with the volume, or add the 2019 advance-access date.

**MIN-15 — No citations for the software stack.** Python 3.11 is named at line 216; numpy, the container runtime and the historical Nextflow workflow are not cited or versioned in the manuscript. Add a short software paragraph with versions.

### Figures and tables

**MIN-16 — Figure 1: numeric labels collide with the error bars.** In every row the "147/158"-style label overlaps the upper whisker (most visible for POLYSOLVER, HLA-HD and the RNA-seq T1K row). Offset the labels, or right-align them in a dedicated column at the axis edge.

**MIN-17 — Figure 1 and Table 1 do not contain the same methods.** Figure 1 shows the primary method and individual callers; Table 1 adds strict majority and two-thirds consensus. Neither the legend (lines 409–414) nor the table caption states the selection rule. Add one clause to the Figure 1 legend, and — per MAJ-04 — add `BestSingleTool_nestedCV` to both.

**MIN-18 — Figure 2: comparator ordering differs between panels.** WES and RNA-seq are each sorted by effect size, so the same comparator sits at different heights. Use a common ordering (or sort both by the WES effect) so the panels can be read across.

**MIN-19 — Figure 2 carries its caption inside the image.** Two lines of caption text are rendered in the PNG/PDF and repeated in the manuscript legend. Several venues reject in-figure captions and most will duplicate them awkwardly in typesetting. Move the text out of the figure.

**MIN-20 — Figure 3 legend wording.** "Singleton-derived caller outputs" (line 423) describes the historical defect rather than what is plotted, which is rows reporting one resolved allele. Retitle: *"Caller rows reporting a single resolved allele."*

**MIN-21 — S4 reports 100% strata with n = 2.** Lines 145–148: four population strata (FIN, GBR, PUR on WES; FIN, GBR on RNA-seq) report 100% on two loci with intervals of 15.8–100.0%. The text correctly warns against reading these (lines 333–335), but presenting them as point estimates invites exactly the misreading. Suppress the percentage for strata below a stated size and show counts only.

**MIN-22 — Stratum label is opaque.** `minimum_within_benchmark_truth_allele_count` (S4, lines 117–119, and the table rows) is a long internal field name used as a display label. Rename for display — "rarer truth allele: within-benchmark count" — and keep the field name in the artifact.

### Reproducibility and repository hygiene

**MIN-23 — Superseded artifact directories sit in the active tree.** `artifacts/head_to_head/consensus_head_to_head.tsv` still contains the 390/321 analysis (consensus 365/390, 306/321), as do `artifacts/consensus_eval/` and `artifacts/consensus_eval_wes_rna/`. `artifacts/README.md` explains that these are provenance-only, which is adequate but is the only signal. A reader who opens the file directly finds numbers that contradict the manuscript with nothing in the file saying so. Move them under `provenance/`, consistent with the handling of `provenance/quarantined_figures/`, or add a `SUPERSEDED.md` inside each directory.

**MIN-24 — Two repository names for one artifact.** The paper repository is given as `PanelHLA-paper` (line 441) and the pipeline as `panelhla` (line 445), while `README.md` and the memory record refer to `uoozcan/PanelHLA`. Confirm the final names and make all three consistent before the archival tag is cut.

**MIN-25 — Assay acquisition metadata is missing.** Capture kit, read length, sequencing depth and preprocessing are not reported for either assay. `[tracked: ACT-MIN-013, blocked_external]` — I accept this is blocked on recovering historical metadata, but the manuscript should state what is unavailable rather than being silent, since coverage depth is a first-order determinant of HLA calling accuracy and a reader will assume it was simply not reported.

**MIN-26 — Thirteen author/archive fields remain unfilled.** `[tracked: ACT-MIN-001]` Noted only for completeness; the manuscript cannot be submitted until `AUTHOR_FIELDS_TO_COMPLETE.md` is resolved. The consolidated-block approach is good practice and should be retained.

---

## 4. Paragraph-by-paragraph pass

### Title and front matter (lines 1–17)

- **Line 1.** See MIN-03 — name the three loci.
- **Lines 5–12.** Seven `TO CONFIRM` superscripts and a nine-item author-input block (MIN-26). The block is well-constructed; keep it, and keep it out of the submitted version.
- **Lines 14–17.** Keywords are reasonable. Consider adding "consensus genotyping" and "benchmark reproducibility," and consider dropping "immunogenomics" if the venue limits keyword count, since it is the least specific.

### Abstract (lines 19–52)

- **Lines 21–25.** "Combining callers may reduce dependence on selecting one tool, but the benefit can be overstated when incomplete outputs are converted into genotypes, ambiguous reference typing is collapsed arbitrarily, or non-significance is interpreted as equivalence." Strong sentence, and the right opening. Keep.
- **Lines 26–28.** "Selection of plurality for primary reporting followed inspection of development evidence and is therefore post hoc." Correct and admirable, but placed in the abstract's setup where it stops the reader before any result has been given. Move it to the results portion of the abstract, next to the numbers it qualifies.
- **Lines 28–30.** "The verified development-analysis boundary begins with recovered truth-free caller tables; the historical upstream workflow is an external dependency." This is repository-internal phrasing that a reader meeting the paper for the first time cannot parse. Rewrite: *"Reproducibility is verified from normalized caller outputs onward; the historical read-alignment and caller-execution workflow could not be re-run and is treated as an external dependency."*
- **Line 32.** See MIN-02 — six distinct callers.
- **Lines 36–39.** The reduction from 390/321 to 158/125 is the most consequential sentence in the abstract and is currently delivered in the passive voice as a procedural note ("This source audit reduced…"). Give it its own sentence with the consequence attached: *"Requiring unique two-field resolution of the reference ambiguity strings reduced the evaluable set from 390 to 158 WES loci (64 subjects) and from 321 to 125 RNA-seq loci (53 subjects); all inference is therefore restricted to uniquely resolved loci."*
- **Lines 41–48.** Results are accurately stated. Add the `BestSingleTool_nestedCV` comparison here per MAJ-04 — it is more informative than the `MVFlooredCC` mention at lines 47–48, which names an undefined policy (MAJ-12) in an abstract.
- **Lines 48–50.** "Of 11 plurality errors in each assay, any evaluated caller recovered four in WES and three in RNA-seq." The phrase "any evaluated caller recovered" is ambiguous between "some caller recovered" and "every caller recovered." Rewrite: *"…at four of the 11 WES errors and three of the 11 RNA-seq errors, at least one panel caller produced the reference genotype."*
- **Lines 50–52.** Good closing sentence. Keep verbatim.

### Introduction (lines 54–86)

- **Lines 56–68.** See MAJ-14 — no motivation precedes this. The algorithmic survey itself is accurate, well-cited and efficiently written; the one-clause-per-tool construction works. Keep.
- **Lines 70–78.** The positioning against Lee *et al.* (2021) and consHLA is the right comparison set and is fairly characterised. Two improvements: (a) say what is *inadequate* about the prior work for the present question rather than only what it did, since as written a reader may conclude the question is already answered; (b) the closing question at lines 75–78 is posed as "how does a deterministic equal-weight genotype vote behave," which is too open to be an aim — see MAJ-14 for a concrete aim sentence.
- **Lines 80–86.** The two integrity findings. This paragraph is doing important work and is buried at the end of the Introduction in compressed form. Consider expanding by one sentence each to state the *direction* of each defect's effect (both inflate apparent sample size, and singleton-to-homozygote conversion additionally inflates apparent consensus), which is what makes them worth a reader's attention.

### Methods — Study design and reproducibility boundary (lines 90–113)

- **Lines 92–98.** Clear and correctly scoped. Keep.
- **Lines 100–103.** "It uses no truth labels during prediction, but its development performance is post hoc and cannot estimate prospective generalization." Precise. Keep.
- **Lines 103–108.** The locked extension is described before the reader knows why an extension is needed. Move this to the end of the Methods, or to the Discussion's future-work paragraph — it currently interrupts the design description with a description of an analysis that produced no results.
- **Lines 110–113.** "106 subjects occurred in both requested assay sets." Good. But the corresponding figure for the *filtered* sets (52) appears only in the next subsection at line 128 and in S1; state both here, since this is where the reader is thinking about independence. Also state here the subject counts that enter the bootstrap (64 and 53) per MAJ-11.

### Methods — Reference HLA typing and denominator construction (lines 115–131)

- **Lines 117–122.** Checksum pinning with a stated failure mode. Exemplary; keep verbatim.
- **Lines 123–128.** The ambiguity rule is stated precisely and the "No first-listed or frequency-preferred allele was selected" sentence is exactly the right disclaimer. Keep. Add the ambiguity-tolerant sensitivity analysis per MAJ-01, and a forward reference to it here.
- **Lines 128–131.** See MAJ-03 — test the exclusion rather than hedging about it.

### Methods — Callers and assay-specific panels (lines 133–154)

- **Lines 135–139.** Accurate. The sentence "The panel reflects historical assay deployment rather than an exhaustive modern benchmark" is good and should be echoed in the Limitations (it currently is, at lines 378–379).
- **Lines 141–147.** "The development results are therefore syntax-normalized, not database-harmonized." Exactly the right admission. See MAJ-02 — quantify the consequence for the 22 errors.
- **Lines 147–154.** The content-derived release audit is a genuine methodological contribution buried in a Methods paragraph. Two points: (a) the 3.11.0–3.63.0 span across a panel is itself a finding about the field and deserves a sentence in the Discussion; (b) note that these releases were derived from database *content*, not from filenames, since filename-based provenance was demonstrably wrong for two of these callers — that is a transferable methodological caution and a reader would benefit from the one sentence it takes.
- **Line 152.** "These are caller resources, not the later normalization release." Correct but cryptic on first read. Rewrite: *"These releases describe the allele databases each caller searched, not the release against which the calls were subsequently normalized."*

### Methods — Allele normalization and call states (lines 156–171)

- **Lines 158–165.** Technically precise; the P/G-versus-expression-suffix distinction is correct and worth keeping (MIN-13 asks only for the citation).
- **Lines 163–165.** Extension requirements are described in a paragraph otherwise about development normalisation, and in the present tense while everything around it is past tense. Separate the two, or move extension normalisation into the extension paragraph.
- **Lines 167–171.** The six call states and the centralised placeholder list are exactly what this section should contain. Keep. One addition: state what fraction of rows landed in each state, or forward-reference S5, so the reader knows the states are not merely hypothetical.

### Methods — Primary and secondary consensus rules (lines 173–187)

- **Lines 175–179.** The rule is stated unambiguously — top vote-getter, always calls, lexicographic tie-break, flagged. Note that "selects the genotype with the most votes" correctly describes a *plurality* and never requires a majority; the manuscript is consistent on this throughout, which earlier drafts were not. Keep.
- **Lines 181–183.** Strict majority and two-thirds are defined adequately.
- **Lines 184–187.** See MAJ-12 — six policies named and never defined. This is also the sentence where "Previously fitted" appears without explaining when or on what, leaving the reader unable to judge the leakage risk that the following sentence asserts.

### Methods — Endpoints and statistical analysis (lines 189–212)

- **Lines 191–195.** Endpoint definitions are clear. "Allele concordance counted the multiset intersection between predicted and truth alleles over twice the genotype denominator" is exact; keep.
- **Lines 197–201.** See MAJ-11 (missing `B`, seeds, cluster counts) and MAJ-16 (estimand mismatch).
- **Lines 202–205.** The exact/Monte Carlo policy is well specified. Add the seed. Also state the symmetry assumption that sign-flipping requires — one clause suffices: *"The sign-flip null assumes the subject-level difference distribution is symmetric about zero under exchangeability of the two methods within subject."*
- **Lines 205–208.** See MAJ-10 — justify the family composition.
- **Lines 208–210.** "A post hoc two-percentage-point non-inferiority calculation is exploratory sensitivity analysis and is not used to claim equivalence." Correct, and the honesty about the margin being post hoc is the right call. But the margin's *provenance* is still unstated — why two points rather than one or five? Add one clause, even if the answer is that it was chosen as a round number after the fact.
- **Lines 210–212.** Good. Keep.

### Methods — Software and audit trail (lines 214–228)

- **Lines 216–221.** See MIN-15 — versions. "Prediction generation rejects truth-bearing columns" is an excellent detail; consider naming the check so a reader can find it.
- **Lines 223–228.** The fail-closed gate and the admission that it is currently closed. This is the paper's strongest reproducibility content and it is the last paragraph of the Methods, where it will be skimmed. Consider promoting the gate to the Results as a short subsection — it is a *result* about the state of the field's provenance practices, not merely a procedure.

### Results (lines 230–336)

- **Lines 232–239.** The cohort collapse. Well handled. "The prior 390/321 denominators and associated concordance estimates are invalid for an exact two-field endpoint" is the correct and courageous sentence; keep it. Add the retained-versus-excluded comparison per MAJ-03.
- **Lines 241–251.** The locked extension. A Results section reporting that an analysis was not run is unusual, and here it is justified — the audit itself produced findings (rosters confirmed, zero overlap, ten caller resources incomplete). Sharpen the opening so a reader understands immediately that this subsection reports an audit rather than a performance estimate.
- **Lines 253–258.** Primary numbers, clearly given. Keep.
- **Lines 260–266.** See MAJ-08 — the interval-versus-test contradiction is at its most consequential here, since these are the two comparisons the whole paper turns on. The sentence "The data therefore do not support 'matches,' 'equivalent' or 'non-inferior'" is right, but it should rest on MAJ-09's detectability statement rather than on the intervals alone.
- **Table 1 (lines 268–289).** Values reconcile exactly with `artifacts/development_corrected/`. Add `BestSingleTool_nestedCV` (MAJ-04). Consider adding a `Δ vs consensus` column so the reader does not have to subtract, and state in the caption that intervals here are unadjusted while Figure 2's are Bonferroni-adjusted — the difference is currently discoverable only by comparing legends.
- **Lines 291–294.** Accurate against S3. "These are within-resource paired comparisons, not evidence of global superiority" is well put; keep.
- **Lines 296–302.** Singleton abstention. See MIN-04. The sentence "These rows no longer contribute fabricated homozygous votes" is doing real work and deserves the consequence attached: how many *votes* changed, and did any locus's consensus call change as a result? The authors have the paired locus audit and this is the direct measurement of the defect's impact on results.
- **Lines 304–311.** See MAJ-15 (pooling) and the non-monotonicity note. The tie reporting (one WES, four RNA-seq, lexicographic winner correct in one and two respectively) is honest and appropriately placed.
- **Lines 313–320.** Oracle headroom, correctly framed as a bound. This is where MAJ-05's error-correlation result should be introduced, since headroom is its consequence.
- **Lines 322–326.** Exploratory policies. "Those RNA-seq values exceed the primary method descriptively, but the policies share the development resource and lack unseen validation" is the correct treatment. See MAJ-12 — the reader still does not know what these policies are.
- **Lines 328–336.** Stratified results, appropriately labelled descriptive. See MIN-21 and MIN-22.

### Discussion (lines 338–368)

- **Lines 340–347.** The restraint is right. But "competitive within these named historical panels" is vague where the paper elsewhere is precise; say *"within 0.63 points of the best WES caller and equal to the best RNA-seq caller by total"* and let the reader judge "competitive."
- **Lines 349–354.** The remediation-as-result paragraph is the strongest in the Discussion. Keep. Consider strengthening the closing sentence into a recommendation for the field: these three conventions — explicit call states, abstention on incomplete output, and a truth parser that respects ambiguity — should be preconditions for any HLA benchmark, which is a genuinely transferable contribution.
- **Lines 356–362.** Prior-work positioning is accurate but thin on *why* the difference in integration unit matters. One sentence would fix it.
- **Lines 364–368.** See MAJ-05 — this paragraph asserts the headroom conclusion the error-correlation table would demonstrate. See MAJ-13 — the future-work list is good but is not a recommendation to a present-day reader.

### Limitations (lines 370–394)

This section is thorough and honest, and I would not ask for much to be added — it is closer to an exemplar than to a problem.

- **Lines 372–376.** Good. Add the measured result of MAJ-03 in place of "may select easier or older alleles."
- **Lines 378–382.** Good. "Differences combine algorithm, deployment and reference-resource effects" is an important admission that is easy to miss at the end of a paragraph; consider promoting it to its own sentence.
- **Lines 384–388.** Good. Add compute cost per MAJ-07 if it cannot be recovered.
- **Lines 390–394.** The WGS withdrawal. Correctly handled.

### Conclusions (lines 396–405)

Accurate and appropriately scoped. See MAJ-13 — add the operational recommendation. The final sentence ("The transferable contribution is a fail-closed, artifact-traceable evaluation that keeps missing calls, truth ambiguity, fitted analyses and unavailable provenance visible") is the best single summary of the paper's contribution and should arguably appear in the abstract as well.

### Figure legends (lines 407–436)

Generally strong; the axis-truncation disclosures (lines 413–414, 429–430) and the common-scale statements are better practice than most published figures. Specific issues at MIN-17 through MIN-20, and the Figure 2 reconciliation sentence requested in MAJ-08.

### Data and software availability (lines 438–452)

- **Lines 440–448.** Clear and appropriately scoped; the distinction between the verified paper repository and the external pipeline repository is exactly right. See MIN-24 on naming.
- **Lines 446–448.** "Callers retain their own licences and some caller distributions restrict commercial use" is consistent with `THIRD_PARTY_NOTICES.md`, which correctly separates the MIT licence of the authors' own code from the caller licences and marks four callers as unverified. Good. Consider stating in the manuscript that four caller licences could not be verified from the deployment, since a reader assembling the pipeline needs to know.

### Supplementary S1–S9

- **S1 (lines 7–28).** Cohort table reconciles. Add the recoverable-loci counts from MAJ-01.
- **S2 (lines 30–67).** All values reconcile with `artifacts/development_corrected/method_performance.tsv`. See MIN-14 on display names.
- **S3 (lines 69–111).** All values reconcile with `secondary_method_results.tsv`. See MAJ-08, MAJ-09, MAJ-10. The header says intervals are "Bonferroni-adjusted percentile subject-cluster bootstrap intervals" while the underlying artifact columns are `simultaneous_ci_lo_points`/`simultaneous_ci_hi_points`; use one term in both places.
- **S4 (lines 113–152).** See MIN-21, MIN-22. The disclaimer at lines 115–119 is good, particularly the note that population labels are source codes rather than continental superpopulations.
- **S5 (lines 154–197).** Missingness table reconciles. See MAJ-15 for the support table.
- **S6 (lines 199–217).** The provenance table is one of the most useful things in the supplement. The closing paragraph on representability is appropriately restrained. Add the release-span observation from MAJ-02.
- **S7 (lines 219–241).** Oracle headroom reconciles with `development_limits/headroom.tsv`. See MAJ-12 for policy definitions and MAJ-09 for promoting the detectability table. The power-projection caveat at lines 236–241 — that simulation uses a normal approximation while observed tests are exact — is an honest and easily-omitted disclosure; keep it.
- **S8 (lines 243–254).** See MIN-05 for the duplicated word (lines 252–253).
- **S9 (lines 256–277).** The reproducibility contract is well specified. Add `B` and the seeds (MAJ-11) so that "reduced resampling" has a stated reference value.

---

## 5. Rewrite guidance: scientific tone and precision

The prose is already formal and largely free of promotional language — the September remediation clearly worked. The remaining issues are of a different kind: the manuscript is over-hedged in places where it has evidence, and imprecise in places where it is trying to be careful. Five patterns account for most of it.

**1. Hedging that should be a measurement.** The manuscript repeatedly states that something *may* be true when the data to settle it are in the repository. "Because exclusions are extensive and could be non-random, inference is limited to uniquely resolved loci" (lines 129–131) and "Extensive truth-ambiguity exclusion may select easier or older alleles" (lines 374–375) are the clearest cases. A hedge reads as caution to the author and as an unexamined weakness to a referee. Replace each with the measured result plus a bounded interpretation — *"Retained loci were enriched for alleles with within-benchmark counts of five or more (X% versus Y%), so concordance on this set is expected to exceed concordance on the excluded set"* — and where a measurement genuinely cannot be made, say why in the same sentence.

**2. Repository vocabulary in the manuscript.** "Verified development-analysis boundary" (line 29), "recovered truth-free caller tables" (line 29), "the release gate remains closed" (line 227), `minimum_within_benchmark_truth_allele_count` (S4) and the six camelCase policy identifiers are internal names. They are precise for someone who knows the codebase and opaque otherwise. For each, give a plain-language phrase on first use and keep the internal identifier in a parenthetical so the artifacts stay traceable — the manuscript already does this well for PanelHLA-Consensus (`SimplePluralityLex`) in `README.md:36` and should extend the pattern.

**3. Passive constructions that hide the consequential step.** "This source audit reduced the requested 390 WES and 321 RNA-seq subject-gene loci to 158 loci" (lines 36–38) and "Historical execution did not preserve executable versions or container digests" (lines 147–148) both bury decisions that a reader needs to register. Use the active voice with the agent named where the agent is the authors, and state the consequence in the same sentence rather than the next one.

**4. Caveats repeated in place of being placed once and well.** The non-equivalence caveat appears six times (MIN-09); the post-hoc-selection caveat appears at lines 26–28, 100–102, 342–343 and 387. Repetition past the second instance reads as anxiety rather than rigour, and it displaces content the paper needs. Choose the two locations where a reader could be misled — the Results sentence and the relevant figure legend — and delete the rest.

**5. Vague comparatives where the paper has exact numbers.** "Competitive within these named historical panels" (lines 341–342), "Lower-support strata were small and imprecise" (lines 307–308), "Population strata other than CEU and YRI were very small, sometimes two loci" (lines 333–334). This manuscript's whole character is exactness; these sentences break it. Give the number: "within 0.63 points of the best WES caller", "strata of two to eleven loci", "five of the seven population strata contained fewer than 16 loci".

**One thing not to change.** The manuscript's willingness to state negative and self-critical results plainly — that the primary rule was selected post hoc, that POLYSOLVER was ahead, that the extension gate is closed, that the repository cannot reproduce caller execution — is its main asset and the reason I would support publication after revision. Nothing in this review asks for any of it to be softened. The recommended additions (MAJ-04, MAJ-05, MAJ-09) all *increase* what the paper reports about its own limits; they simply do so with evidence rather than with hedging.

---

## 6. Issue summary

| ID | Severity | Location | One-line fix |
|---|---|---|---|
| MAJ-01 | Major | Methods 115–131; S1 | Run ambiguity-set and G-group sensitivity analyses on all 390/321 loci |
| MAJ-02 | Major | Methods 141–154; S6 | Count how many of the 22 errors are cross-release nomenclature artefacts |
| MAJ-03 | Major | Methods 129–131; Lim. 373–375 | Compare retained vs excluded loci by gene, population, allele frequency |
| MAJ-04 | Major | Table 1; Results 253–294 | Add `BestSingleTool_nestedCV` to Table 1, Figure 1 and the narrative |
| MAJ-05 | Major | Discussion 364–368 | Report the existing caller error-correlation table; use it to explain the result |
| MAJ-06 | Major | Methods 133–139; Lim. 378–382 | Link narrow algorithmic coverage to correlated error; state resource scope |
| MAJ-07 | Major | absent | Report compute cost, or state that historical execution metadata is unrecoverable |
| MAJ-08 | Major | S3; Figure 2; `evaluation.py:352–374` | Reconcile Bonferroni intervals with Holm tests; state which governs |
| MAJ-09 | Major | S3 109–111 | Promote `detectability.tsv`: these comparisons could never have been significant |
| MAJ-10 | Major | Methods 205–207 | Drop zero-discordance comparators; define families by scope; report no verdict flips |
| MAJ-11 | Major | Methods 197–208 | Report `B`, seeds, cluster counts; replace far-tail percentile intervals |
| MAJ-12 | Major | Methods 184–187; S2/S3/S7 | Define all six exploratory fitted policies in a supplementary subsection |
| MAJ-13 | Major | Discussion; Conclusions | State what a reader should actually do |
| MAJ-14 | Major | Introduction 56–86 | Restore clinical motivation; add an explicit aim sentence |
| MAJ-15 | Major | Results 304–311; S5; Figure 5 | Stop pooling reduced support fractions; report non-monotonicity as a finding |
| MAJ-16 | Major | Methods 197–205 | State that intervals are locus-weighted and tests are subject-weighted |
| MIN-01 | Minor | Abstract 19–52 | Trim to the venue's word limit; cut duplicated hedging |
| MIN-02 | Minor | Abstract 32 | Six distinct callers, not five plus four |
| MIN-03 | Minor | Title 1 | Name HLA-A, -B, -C explicitly |
| MIN-04 | Minor | Results 299–300 | Clarify "three rows for each of" |
| MIN-05 | Minor | S8 252–253 | Delete duplicated "concordance" |
| MIN-06 | Minor | throughout | Fix one display name for the primary method |
| MIN-07 | Minor | Abstract 39; Methods 194 | Define "fixed-denominator" and "called-only" at first use |
| MIN-08 | Minor | Methods 92 | Define "recovered" once |
| MIN-09 | Minor | six locations | Keep the non-equivalence caveat twice, not six times |
| MIN-10 | Minor | Results headings | Check declarative headings against venue style |
| MIN-11 | Minor | Methods 93 | Cite Geuvadis (Lappalainen 2013) |
| MIN-12 | Minor | References 478–479 | Cite or remove the orphan 1000 Genomes reference |
| MIN-13 | Minor | Methods 158–165 | Cite Marsh 2010 for nomenclature |
| MIN-14 | Minor | References 511 | arcasHLA year should match volume 36 (2020) |
| MIN-15 | Minor | Methods 216 | Add software versions and citations |
| MIN-16 | Minor | Figure 1 | Labels collide with error bars |
| MIN-17 | Minor | Figure 1 legend | State which methods the figure shows |
| MIN-18 | Minor | Figure 2 | Use a common comparator ordering across panels |
| MIN-19 | Minor | Figure 2 | Move the in-image caption out of the figure |
| MIN-20 | Minor | Figure 3 legend 423 | Retitle to describe what is plotted |
| MIN-21 | Minor | S4 145–148 | Suppress percentages for strata below a stated size |
| MIN-22 | Minor | S4 117–119 | Give the allele-count stratum a display label |
| MIN-23 | Minor | `artifacts/` | Move superseded 390/321 directories under `provenance/` |
| MIN-24 | Minor | Data availability 441–445 | Reconcile the three repository names |
| MIN-25 | Minor | Methods | State that assay acquisition metadata is unrecoverable |
| MIN-26 | Minor | front matter | Resolve the 13 author/archive fields |

---

## 7. Note on what was checked and found sound

So that the authors do not spend revision effort re-verifying these:

- **Arithmetic and internal consistency.** Table 1, S2, S3, S4, S5, the support tables and the oracle headroom table all reconcile exactly with `artifacts/development_corrected/` and `artifacts/development_characterisation/`. Support strata sum to 158 and 125 with 147 and 114 correct. Callable plus partial equals rows for every caller in S5. The single uncalled RNA-seq locus reconciles with the 0/0 undefined-support row. The Holm family sizes stated in Methods (13 WES, 12 RNA-seq) match the S3 row counts.
- **The sign-flip test is genuinely two-sided.** `statistics.py:46–60` tests `|total| >= observed` over the full enumeration, and every exact *p*-value in the artifacts is of the form 2/2^k as that implies. No change needed; I raise only the unstated symmetry assumption (Methods 202–205).
- **Figure formats.** All five figures exist as PDF, SVG, 600-dpi PNG and TIFF, matching the claim at lines 218–219.
- **References.** Volume, page and year details check out for all sixteen listed works except arcasHLA (MIN-14). Bowen-James *et al.* (2025) I could not verify independently.
- **Licence consistency.** `THIRD_PARTY_NOTICES.md` and the manuscript's licence statement agree, and the four unverified caller licences are marked as unverified rather than guessed.
- **Nomenclature.** The P/G-group versus expression-suffix distinction (Methods 160–163) is correct, as is the expression-suffix list (N, L, S, Q, C, A).

---

*Reviewer's closing note.* The cohort collapse from 390/321 to 158/125 will look, to an editor, like the paper got weaker. It got more truthful, and the manuscript should make that argument explicitly rather than leaving the editor to infer it — the September remediation is the reason the numbers in this paper can be believed, and that is worth a sentence in the cover letter as well as the two it already gets in the Discussion.
