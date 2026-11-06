# Manuscript FATAL and MAJOR fixes — 5 November 2026

## MAJOR findings (JP-005 to JP-018): first pass

Text fixes that add no new registered result are applied on top of the FATAL fixes below. Local and uncommitted. The sources from just before this pass are in `C:/Users/uonur/AppData/Local/Temp/claude/D--projects-project-2008084-champhla-scirep-rerun-wt/5db22489-3ecf-43cc-8b3f-ce938d4411ba/scratchpad/pre_major/`.

| Finding | Applied | Not applied, and why |
|---|---|---|
| JP-005 reference | Nothing | Moving past "may reflect" breaches `decisions/20261009_reference_adjudication.json` without a signed amendment. The per-locus table needs registry rows |
| JP-006 arcasHLA | Text and Table 2 note say defective deployment; `-profile paper` warning; "may contribute" and the runtime patch disclosed | Leave-one-caller-out table and the M:370 threshold wording need registry rows. Figures 2-3 are hash-pinned. A `--paired` run needs a signed amendment |
| JP-007 abstract | Nothing | Headline claim and the publication-route flag are the author's |
| JP-008 fitted rules | Heading, the fitted-policy paragraph with abstain-all result and existing tags, Discussion sentence | The abstract sentence goes with JP-007 |
| JP-009 roster | Methods sentence | Nothing |
| JP-010 extension | Discussion sentence on power | The estimand belongs in the plan the author signs and deposits |
| JP-011 developer | Methods sentence | Title is the author's. Tools-considered table needs reasons from the author. Ledger row needs registry approval |
| JP-012 deployment | Frequency prior off stated | Version and digest columns, T1K reference and positive controls need Roihu |
| JP-013 reference label | "single recorded reference genotype"; HapMap and CEPH sentence | P-group column needs registry rows. Asking the 2014 authors is the author's |
| JP-014 value claim | Nothing | The "insurance" wording changes what the paper says the method is for, and its numbers need registry rows |
| JP-015 history | Two restored sentences; "adopted after results" in Discussion | More ledger rows need registry approval. Telling co-authors is the author's |
| JP-016 statistics | S:359, S:427, S:1823, M:481, tie-flag claims, the renamed SpecHLA cell | Nothing |
| JP-017 patient cohorts | Nothing | Reverses a signed decision |
| JP-018 S11.2 | Commands replaced with the study's own; rename and route warnings stated | Test case with expected output and a clean-machine run |

**Please check these four.**
- JP-015's two restored sentences reverse part of the 27 October wording revision, which removed the earlier design story on purpose.
- JP-016 adds one number with no registry row: Holm *p*=0.047 for RNA-seq strict majority if the duplicate row is removed. It corrects a false "changes no significance verdict", and the text labels it as our calculation.
- JP-016's disclosure of the renamed SpecHLA cell: the review left whether that discovery was truth-contaminated to the author. It was found by reading code and then the call table.
- JP-013's HapMap and CEPH sentence rests on one review agent's reading of the source, which has not been checked by a person.

**S11.2 test.** Both new commands exit 0 in a Nextflow stub run on the `v3.5.0` archive with Nextflow 23.10.0 (the study used 25.10.2), using the `stub` execution profile and empty placeholder inputs. No caller ran. WES resolves the five-caller panel with `RESCUE_HLA_READS` and `SPECHLA_BAM`; RNA-seq resolves the four-caller panel with `ARCASHLA_BAM`. The first WES attempt failed only because the test pointed both reference options at one placeholder file. Under `-profile roihu,singularity,paper`, `nextflow config` resolves SpecHLA to no container.

**Checks after this pass.** Full test suite 547 passed, 1 failed (the pre-existing wording test), 3 skipped; lint passed; claim audits show zero blocking failures in both documents. The registry is unchanged from the signed `00ce7f01...`, so the 5 November approval still holds. All three Word copies are rebuilt and both review drafts pass parity; layout was not inspected visually. Full verification was not repeated after this pass.

## JP-017 patient cohorts: removed and signed

The author signed `decisions/20261105_patient_cohorts_removed.json` in the Claude Code session of 5 November ("Sign removal"), reversing two signed decisions. No patient data was opened, and `artifacts/fimm`, `artifacts/fimm_consensus`, `artifacts/venex` and `data/fimm` are untouched.

The author approved the registry in the same session ("I approve it"), recorded in `decisions/20261105_rerun_registry_delta_approved_cohorts_removed.json`.

- `result_registry.tsv` went from 709 to 610 rows, SHA-256 `c02f0dfcfa8ea75743dd264d270f59fd9717727baf1a0ec1d312bb3787cc93f1`. The diff is 99 removed rows, all FIMM or VENEX, and the hash and count fields of `PROTOCOL_CHANGE_LEDGER_20261013`. The 25 stop reasons are unchanged.
- Main text, S9.1-S9.5, Figures S6-S8 and references 28, 29 and 40 are gone. NCI-60 is now S9. Former Figure S9 is S6, with its files renamed. Later references are renumbered, leaving 51 entries.
- One disclosure stays in the S8 table and one row in the ledger. `configs/fimm_submission_gate.json` no longer feeds the claim audit, and its six FIMM items no longer appear.
- Code: the registry, figure and verification scripts no longer read the controlled aggregate paths. The import code and its synthetic tests stay.
- Tests: counts and figure names updated. Five tests that pinned FIMM registry rows and text were removed from `tests/test_exploratory_integration.py`, and one new test checks the cohorts are out. Copies from before are in the scratchpad `pre_removal` folder.
- Other checks: claim audits show zero blocking failures and no pending author-input items from FIMM. Word copies are rebuilt with 10 figures and 42 tables, and both review drafts pass parity. Layout was not inspected visually. Author fields and the co-author checklist dropped their FIMM items.

**Snapshot-shaped verification:** run once on a temporary copy of this working tree with the held-back paths deleted, unopened. Exit 0, gate accepted, claim audits 0 scientific failures, and the registry byte-identical at `c02f0dfc...`. This clears the snapshot failure in the tree shape tested; `scripts/publish_snapshot.sh` itself was not run, because it builds from committed HEAD. Run on that copy, the suite had five further failures from held-back files (three needing the controlled aggregates, two needing an internal prompt); those tests now skip when the files are absent. The skips were checked in the checkout, where the files are present, and not re-run on the snapshot shape.

**Full verification:** run twice on temporary copies, with tests skipped because they ran separately.
- The run alone passed: exit 0, gate accepted, claim audits 0 scientific failures, and the registry, every table and figure, and both manuscript sources byte-identical. The audit files and `artifacts/publication_readiness_gate.json` were refreshed from it. The gate file now reads `technically_ready`, meaning scientific checks only; the audit still warns that author contributions, author list, competing interests and funding are missing.
- **The earlier run, alongside the snapshot run, stopped at the author gate.** Its registry had a different hash (`6d4777a2...`), with differences in `artifacts/development_sensitivity_abstain/confirmation_decision.json`, `method_performance.tsv` and `secondary_method_results.tsv`. The differing files were not kept, so what moved is unknown. This is not the pattern in `decisions/20261026_metaconsensus_floating_point_drift.json`, which describes four compatibility tables. This was later tracked down and is recorded in `reports/metaconsensus_drift_20261105.md`: only logistic meta-consensus moves, the main-text result did not move in 26 refits, but S7.1's claim that no reported result changes needs correcting.

## MINOR and EDITORIAL findings (JP-019 to JP-040): first pass, 6 November

Applied at the author's instruction ("Yes, start it"). This pass changes only text that adds no new number, each checked against the code, artifacts or registry. No registry row, figure or signed record changed.

| Finding | Applied in the main text |
|---|---|
| JP-020 | Methods: the families were fixed on 28 September 2026 after results, and *p* values are conditional on the post hoc choice of the vote as reference arm |
| JP-021 | Results: the arcasHLA–T1K φ interval also includes zero (registry row `DEV_ERROR_PHI_RNASEQ_ARCASHLA_T1K`, −0.08 to 0.30). Discussion: where the typings agree, the vote is correct at every locus, rather than "almost all" caller errors |
| JP-023 | Methods: duplicate reference rows are combined as the union of candidates, as `src/champhla_recovery/truth.py` does |
| JP-028 | Methods: the workflow test checks the rule output on archived calls |
| JP-029 | Methods: read rescue applies to DNA BAM or CRAM input |
| JP-030 | Introduction: Lee, Claeys and SweHLA wording as proposed; "common" dropped |
| JP-032 | Discussion: what this evaluation adds, without the tie-break and repeat-run claims |
| JP-035 | Data availability: second-typing file, URL and SHA-256; IPD-IMGT/HLA 3.65.0 source and checksum file; the analysed roster `cohorts/development_rerun_manifest.tsv` |
| JP-037 | Discussion gets a "Limitations" heading, so the "(Limitations)" pointers resolve (no Conclusions heading, which `tests/test_scientific_reports_manuscript.py` bans for this journal's format); Methods says WGS outputs came from the original caller run, as S8 records |
| JP-040 | Figure 2 legend: Clopper–Pearson at 0% or 100%; threshold rules and five fitted policies not shown |
| S7.1 follow-on | Data availability no longer cites the "near-tie"; it points to the meta-consensus variation |

JP-025 needed no change: Methods already says the capture kit, read length, depth and preprocessing metadata were unavailable. JP-034 is moot, because S9.4 went with the patient cohorts.

**Not applied: new numbers, which need a signed post hoc amendment, values stated in advance and registry rows:** JP-019 (non-inferiority, power table, exact intervals), JP-021 (joint and expected error counts, no median), JP-022 (naive baselines), JP-023 (count under intersection; G above P explained), JP-024 (pedigree check), JP-027 (S12 on study-run calls), JP-029 (POLYSOLVER led WES in archived outputs, if not already a registry row), JP-033 (HG00096 rows against historical inputs), JP-036 (allele-level vote, abstention trade-off), JP-040 (clipped S2 bar, S3 and S6 legends, which need figure rebuilds).

**Not applied: the author's call:** abstract wording in JP-023 and JP-032, because the abstract is signed; JP-031 cover letter, after the title and JP-014 framing; JP-037 Declarations and an LLM statement; JP-038 hold-back list and what stays as provenance; JP-039 nomenclature rewrite, a judgement call across the whole text; JP-035 referee route to decisions files.

**Needs Roihu:** JP-025 read length and depth; JP-029 read-class check of the rescue.

**Checks:** Full test suite 542 passed, 1 failed (the pre-existing wording test), 3 skipped. Word copies rebuilt, both review drafts pass parity, 42 tables. Claim audits show zero blocking failures, and the audit files are refreshed. Lint passes on `src`, `scripts` and `tests`. Registry unchanged at `c02f0dfc...`. Supplementary text unchanged in this pass.

**Round 3 amendment drafted, unsigned.** `decisions/20261106_posthoc_round3_amendment.json` fixes each new-number item before any script exists: three truth-free corrections (HG00096 rows, S12.1-S12.2 on study-run calls, figure presentation) and eight post hoc items, each with the panel's numbers as expected values. Not included, with reasons: exact intervals in Table 2, score intervals for paired contrasts, the JP-014 baselines, abstract wording and the Roihu items. Nothing has been computed.

## Round 3 amendment: signed and applied except B5, 6 November

The author signed `decisions/20261106_posthoc_round3_amendment.json` as drafted ("Sign as drafted"). Each script was tested on synthetic data and run once.

| Item | Result against the stated expectation |
|---|---|
| A1 HG00096 rows | Matched: 12/12, 11/15 and 11/12, now equal to the S10 text; the other three rows unchanged |
| A2, B6 S12 | Matched: arcasHLA 17/38, 27/40, 14/40 (58/118), HLA-HD leads RNA-seq HLA-B, RNA-seq unanimity 51/53. Archived values kept in `provenance/development_rerun_v350/historical_artifacts/restored_analyses/`. **Deviation:** S12.4 calibration stays archived, because the study-run calls have no calibrated probabilities |
| A3 figures | S2 bars unclipped and S6 panel letters added; only those two figures changed. S3: no mismatch found between legend and figure, so unchanged |
| B1 | Non-inferiority text and the power table removed; the Discussion now uses the exact detectability rule; S8 row added. `power_curve.tsv` is still computed but not reported |
| B2 error counts | Matched: HLA-HD–OptiType RNA-seq 5 joint errors (0.31 expected), 1 and 1 single; 3 of 6 RNA-seq subset φ undefined. Medians removed |
| B3 naive baselines | Matched all stated values (most common genotype 8/153, 11/118 exact; 4/182, 3/145 excluded; two alleles 3/153, 3/118 exact). Values without an expectation are reported as computed |
| B4 | Matched: intersection 320/335 and 256/263; vote ties OptiType at 143/145 on RNA-seq excluded loci; all 9 + 7 + 3 G-over-P loci carry a null call |
| B7 | Matched: archived POLYSOLVER 143/153, the highest archived caller |
| B8 | Abstention matched all four values. **Allele-level vote differs:** 143/153 WES against the panel's 142 (its rule was not recorded); 113/118 RNA-seq matched. Under the signed rule it equals the genotype vote at every exact locus |
| B5 pedigree | Matched. Downloaded with the author's permission ("Yes, download it"): `20130606_g1k.ped`, 155,869 bytes, SHA-256 `38687335...`. All retained subjects are in it; no first-, second- or third-degree pairs; family clusters 46 WES and 40 RNA-seq; none of 20 sign-flip verdicts changed. Methods sentence, S3 paragraph, Data availability and README fetch lines added |

Code fixes that changed no definition or value: the B2 script first wrote empty WGS rows; `restored_analyses.py` read a checksum field that only the archived manifest has, and failed before writing anything. Both were fixed and the scripts rerun.

Registry: 695 rows, SHA-256 `d2702af18ebba4552d31e590e5f2d2e480c7cbb108b3d080414866ca8671bf32`. Against the approved `c02f0dfc...`: 86 added, 1 removed, 88 changed, none of them primary, comparator or fitted-policy rows; the 25 gate reasons are those approved on 5 November. The author approved it in the Claude Code session of 6 November ("I approve it"), recorded in `decisions/20261106_rerun_registry_delta_approved_round3.json`; the gate now accepts this registry with that record and no other.

**Full verification after round 3 (6 November):** one solo run on a temporary copy of this working tree, with the three public files fetched and checksum-verified. Exit 0, gate accepted the round 3 record, publication gate `technically_ready` with zero scientific failures, and the registry byte-identical at `d2702af1...`; the meta-consensus variation did not appear. Every table, figure and manuscript source matched the checkout. Four files differed as expected and were copied in from the run: `characterisation_manifest.json`, which now lists the round 3 artifacts, and the three `result_registry_delta` files, which now describe this registry. The two review drafts differ only in the notice lines that run writes. Full suite afterwards: 547 passed, 1 failed (the old wording test), 3 skipped. Ledger has 16 changes. Claim audits zero failures; Word copies rebuilt with 45 tables, both review drafts pass parity; lint clean. Tests: four pinned counts updated (tables 45, ledger 16, S12 reconciles with the current performance table); the full suite otherwise has only the old wording failure.

## Remaining findings: second pass, 6 November

Applied at the author's instruction ("could you make a plan and continue to fix those issues too?"). No registry row, artifact, figure or signed record changed. The sources from just before this pass are in `C:/Users/uonur/AppData/Local/Temp/claude/D--projects-project-2008084-champhla-scirep-rerun-wt/5db22489-3ecf-43cc-8b3f-ce938d4411ba/scratchpad/pre_jp039/`.

| Item | Applied |
|---|---|
| Old wording test | `test_reader_facing_text_does_not_invent_historical_task_state` now pins the 27–28 October wording ("In the ChampHLA runs, every panel caller returned a row"; "In the study runs no panel caller row is absent."). The sentences say the same as before |
| JP-039 nomenclature | Methods opens "Allele normalization and call states" with a paragraph defining fields, two-field resolution, null alleles, exons 2–3, P and G groups [34], and this paper's *locus*, *homozygous reference locus*, *reference*, *archived outputs* and *ChampHLA runs* |
| JP-039 terms | Main text: *truth* becomes *reference genotype* or *reference typing* in reader prose (7 places), and *stored* or *historical* becomes *archived* (5 places). Supplement: 24 prose phrases become *archived* or *study run*, including the S12.4 sentence below. File paths, generated tables and the ledger keep their wording; the ledger feeds registry hashes |
| JP-039 sentences | Rewritten from J4's list: Discussion opening (#1), oracle headroom (#5, now defined in place), deployment-defect discovery (#15, now consistent with Limitations), resampling (#13), NA07000 referents (#14), read route (#12), asterisk comparison (#4). The signed JP-005 sentences (#6, #7) are unchanged |
| JP-023 heading | The Results heading "Scoring ambiguous typing kept the conclusions" becomes "…left the comparison with the strongest caller unchanged…". `ambiguity_paired_results.tsv` gives Holm *p* = 0.5 for the vote against OptiType (WES) and against HLA-HD and OptiType (RNA-seq), while more comparisons with weaker callers become significant |
| S12.4 sentence | It said the other S12 tables came from the historical joined table, which round 3 made false. It now says S12.1 to S12.3 use the study-run calls |
| JP-031 cover letter | Rewritten with the sample sizes, the post hoc primary, "all 15", the extension status, the arcasHLA defect and the unevaluated default rule. The FIMM item is gone; author-input blocks stay |
| Author checklist | `AUTHOR_FIELDS_TO_COMPLETE.md` drops its patient-cohort governance items, which the 5 November removal made moot. Its provisional LLM statement now names ChatGPT and Codex as well as Claude, matching the record (JP-038) |
| Stale venue | `tests/test_reference_facts.py` docstring named BMC Bioinformatics |

The JP-023 and JP-032 abstract items need no change: the signed A-plus abstract no longer contains either sentence.

**Drafted for the author, not applied:** `reports/author_decisions_20261106.md` covers the JP-014 framing, the title, Declarations and the LLM statement, referee access, the hold-back list, round 4 and the co-author update. `decisions/20261106_posthoc_round4_amendment.json` is unsigned and fixes the figure corrections (Figure 1A text, arcasHLA marking in Figures 2–3, Figure S6 labels), the JP-014 rows and the Roihu items before any script exists. `reports/coauthor_update_20261106.md` is a draft message and has not been sent.

**Found while drafting the hold-back list:** four tracked provenance files each hold the 99 FIMM and VenEx aggregate rows that the current registry dropped (`historical_result_registry_pre_v350.tsv` and `result_registry_delta.tsv`, in `provenance/development_rerun_v350/` and in its 25 October superseded copy). The registry gate reads the first of them, so holding it back is not a list edit. The options are in section 6 of the decision pack.

**Checks:** full test suite 548 passed, 0 failed, 3 skipped, the first run with no failure since the 27 October wording revision. Two tests changed beyond the old wording test: one pins the reworded S13 resource-use phrase, and one docstring names the right journal. Claim audits show zero blocking failures and no pending author-input items in either document, and the audit files are refreshed. Word copies are rebuilt: 45 tables, 10 figures; both review drafts pass parity. Lint is clean on `src`, `scripts` and `tests`. Registry unchanged at `d2702af1...`, so the round 3 approval still holds. Main-text words under the 4,500 limit: 4,393 before this pass and 4,424 after; the nomenclature paragraph is in Methods, which the limit does not count. Full verification was not repeated, because only prose, tests and author files changed. Nothing is committed.

### Framing and title chosen, 6 November

The author chose in the Claude Code session of 6 November, from the options in `reports/author_decisions_20261106.md`:

- **Title: T3** ("T3: auditable plurality vote"). "An auditable plurality vote for HLA class I genotyping from exome and RNA sequencing: a development benchmark" (16 words) replaces the earlier title in the manuscript, the supplement's opening line, the cover letter and the Word-copy title test. The 27 October change reports keep the old title as history.
- **JP-014 framing: option C** ("C: keep, add stability"). The "operational" sentence stays. The run-stability sentence is not added yet: its numbers need registry rows, item C1 of the round 4 draft.

The round 4 draft was split. `decisions/20261106_posthoc_round4_amendment.json` now holds only the local items: figure corrections A1–A3, and C1 with its expected values and the exact sentence. `decisions/20261106_roihu_descriptions_round5.json` holds the Roihu items R1–R5. Both are unsigned, and nothing in either has been computed.

**Checks:** full test suite 548 passed, 0 failed, 3 skipped. Claim audits show zero blocking failures. Word copies are rebuilt with 45 tables and 10 figures, and both review drafts pass parity. Registry unchanged at `d2702af1...`. Nothing is committed.

## Round 4 amendment: signed and applied, 6 November

The author signed `decisions/20261106_posthoc_round4_amendment.json` as drafted ("Sign as drafted"). The C1 script was tested on synthetic data and run once.

| Item | Result against the stated expectation |
|---|---|
| A1 Figure 1A | Footer now says each caller runs in a container except SpecHLA, which ran natively. Only Figure 1 changed |
| A2 arcasHLA | Marked "arcasHLA†" in Figures 2 and 3, with the dagger note in both legends. No plotted value changed |
| A3 labels | Figure S6 and Table S10.2 share one set of reader labels; the S6 legend says "present only in the study run". No count changed |
| C1 run stability | **All matched:** vote 143/153 WES and 113/118 RNA-seq in both runs; the largest change was arcasHLA, 51 loci (109 to 58); the leading WES caller went from POLYSOLVER (143/153) to OptiType (142/153); vote calls changed at 2 of 153 WES and 0 of 118 RNA-seq loci. Before writing the archived scores, the script confirmed that its study-run scores reproduce `per_locus_results.tsv` at every locus |

The sentence the record fixed is in Limitations, with four result tags, and uses the expected values unchanged. `scripts/score_run_stability_posthoc.py` writes `run_stability_posthoc.tsv` and `run_stability_summary_posthoc.tsv`. The verification pipeline runs it after S12 on study-run inputs. `tests/test_posthoc_round4.py` holds two synthetic tests. The ledger has a seventeenth change, `posthoc_round4`.

Only Figures 1, 2, 3 and S6 were rewritten when the figures were regenerated.

**Registry:** 712 rows, SHA-256 `a4d970ecba73f5483f2a1899c1b75d7ce35681595f61927b5c0ff96afae5bd10`. Against the approved `d2702af1...`: 17 rows added (`DEV_RUN_STABILITY_*`), none removed, one changed (the ledger row, 16 to 17 changes). No primary, comparator or fitted-policy row changed. The 25 gate reasons are the ones already approved. `decisions/20261106_rerun_registry_delta_approved_round4.json` was drafted unsigned. The gate refused this registry with it and with the round 3 record, and accepted a signed scratch copy. The author then approved the registry in the Claude Code session of 6 November ("I approve it"), and the record now reads SIGNED.

**Full verification after round 4 (6 November):** one run on a temporary copy of this working tree, with the three public files fetched and checksum-verified.
- **Result:** exit 0. The gate accepted the round 4 record, and the publication gate reads `technically_ready` with zero scientific failures.
- **Matched the checkout:** the registry (byte-identical at `a4d970ec...`), every table and figure, and both manuscript sources.
- **Copied back from the run, with LF line endings:** `characterisation_manifest.json`, which now lists the two run-stability artifacts, and the three `result_registry_delta` files.
- **Expected differences:** the two review drafts differ only in the notice lines that run writes.
- **Afterwards:** the full suite passed, 550 with 0 failed and 3 skipped.

**Checks:**
- Full test suite: 550 passed, 0 failed, 3 skipped. The ledger count test was updated to 17.
- Claim audits: zero blocking failures in both documents.
- Word copies: rebuilt with 45 tables and 10 figures, and both review drafts pass parity.
- Lint: clean on `src`, `scripts` and `tests`.
- Main text: 4,458 counted words, under the 4,500 limit.

Nothing is committed.

## Public snapshot scope and round 5: signed and run, 6 November

The author set the co-author update aside and chose the recommended options ("we can continue with best options, and with p2"). Two records were then signed as drafted ("Sign as drafted"): `decisions/20261106_public_snapshot_scope.json` and the round 5 record. Before signing, the round 5 record gained one fixed rule: R5 copies the first subject in sorted manifest order that has both assays.

**S1, hold-back list.** `scripts/publish_snapshot.sh` holds back the 16 internal records listed in the decision pack, and the snapshot build now refuses any provenance file that names a withheld cohort. `decisions/` stays in the snapshot.

**S2, P2.** `scripts/withhold_cohort_rows.py` was tested on synthetic data and run once. The four unfiltered files moved unchanged to `provenance/cohort_rows_withheld_20261106/`, which the snapshot holds back. Filtered copies replaced them, and `provenance/cohort_rows_withheld_20261106.json` records each file's rows and SHA-256 before and after. The activation reports still pin `a5747655...`, which is now checkable against the private originals.

| Expected (signed) | Computed |
|---|---|
| Each archived registry 631 to 532 rows | 631 to 532, both copies |
| Superseded delta 631 to 532 | 631 to 532 |
| Current delta 813 to 714 | 813 to 714, and 714 after regeneration |
| Gate: old rows 532, new rows 712; 34 unchanged, 496 changed, 182 added, 2 removed | Same |
| The 25 gate reasons unchanged | Same 25 |
| In the registry, only `DEV_ARCHIVED_WES_CALLER_POLYSOLVER` and the ledger row change | Same; registry SHA-256 `894e1c10...` |

The author approved that registry ("I approve it"): `decisions/20261106_rerun_registry_delta_approved_snapshot_scope.json`. The ledger gained `cohort_rows_withheld`.

**S3, R1 referee access.** Recorded. The Data availability and cover-letter sentences wait for the deposit link.

**Round 5.** The CSC certificate downloaded on 6 November was installed in WSL; the expired copy was kept as `id_ed25519-cert.pub.expired_20261103`. The per-sample results had been archived to Allas on 25 October and deleted from scratch. One Slurm job read the 58.6 GB archive back, matched its recorded SHA-256 `c344844f...`, and extracted only the small per-sample records. All 2,596 recorded file hashes matched (236 runs by 11 files). The workflow's `main.nf`, `nextflow.config` and site parameter file at commit `66d949d` match the hashes every run recorded, so module code was read at that commit.

| Item | Expected (signed) | Computed |
|---|---|---|
| R1 deployment | POLYSOLVER race Unknown, includeFreq 0; SpecHLA `-u 1`; arcasHLA database 3.40.0 | The first two confirmed in code and command lines. The arcasHLA database version is not in the run records, so Table 1 keeps its existing source. **New:** every T1K task in both assays used the genomic index `hla_dna.fa`, not the coding-sequence `_rna_seq.fa` beside it. OptiType and arcasHLA versions were not recorded by the runs |
| R2 inputs | RNA-seq paired-end, about 75 bp | **Matched:** all 106 RNA-seq inputs are GRCh37 and paired-end, median read length 75 bp (75–76). The 130 WES inputs are GRCh38; 128 are paired and 2 carry some unpaired reads; median read length 100 bp (68–101). Median of the per-input mean depth over the six exons: RNA-seq 3,926.7 (222.4–12,113.5), WES 20.4 (3.8–79.3), on primary chromosome 6 only |
| R3 rescue classes | No expected value | **Not computable as signed.** The rescue tables hold counts only (contigs present, records selected, pairs realigned, records out), and the realigned BAMs were pruned. Totals are reported; classifying reads would mean rerunning the rescue and needs its own record. The record says 129 WES subjects; the runs number 130 |
| R4 cost | No expected value | Per caller and assay in Table S10.6. Largest per-run CPU use: RNA-seq HLA-HD, median 2.40 CPU hours (0.14–12.21), peak 10.7 GiB. One failed task attempt across all final launches, an RNA-seq HLA-HD task that was retried |
| R5 manifest | One subject's files, hash-checked | HG00096, 12 files (6 per assay), all matching |

The R1 table was generated twice. The second pass only added SpecHLA's recorded version (1.0.7) beside the git commit of its native installation; every other cell and file was byte-identical.

The R2 job was submitted four times; none before the last produced a result:
- Job 2916575 failed while loading the samtools module.
- Job 2916604 was cancelled after one input because a serial run would have taken about six hours.
- Job 2916686 was resubmitted with the old serial script by mistake and cancelled after one input.
- Job 2916730 ran with eight parallel inputs.

The logs of the first three are kept beside the result on Roihu.

**Where the text went.** Table 1 gained a column for the version and settings in the study runs, and POLYSOLVER's row carries "(run here with the frequency prior off)". Image digests, database sources and input routes are in the new Supplementary Table S10.4 rather than Table 1, which keeps Table 1 readable. Methods gained two sentences, on the T1K index and on the read layout and length. Supplementary S10 gained Tables S10.4 to S10.6 with their notes, and S11.1 gained the rescue counts. The Methods additions are outside the counted word limit.

**Registry:** 745 rows, SHA-256 `143a1e16...`. Against the approved `894e1c10...`:
- 33 rows added: the T1K index rows, the input rows, the rescue rows and the `DEV_RUN_COST_*` rows.
- One row changed: the ledger row, now at 19 changes; the ledger gained `roihu_descriptions_round5`.
- Gate summary: 532 old rows, 745 new; 34 unchanged, 496 changed, 215 added, 2 removed; the same 25 reasons.

The author approved this registry ("I approve it"): `decisions/20261106_rerun_registry_delta_approved_round5.json`.

**Snapshot-shaped verification of P2**, run before round 5 on a temporary copy with every held-back path deleted:
- **Result:** exit 0. The gate accepted the snapshot-scope approval, and the registry was byte-identical at `894e1c10...`.
- **Tests:** three failed on that shape. Two read `AUTHOR_FIELDS_TO_COMPLETE.md`, which the snapshot now holds back; they now check it only where it exists. The third counted the supplement lines that name the cohorts, and it now expects the signed withholding row too.

**Checks after round 5:**
- Full suite: 564 passed, 0 failed, 3 skipped. Three test pins changed: the Word copy has 48 tables, Table 1 has 6 columns, and the ledger has 19 changes.
- Claim audits: zero blocking failures in both documents.
- Both review drafts pass parity.
- Lint: clean.

**Final snapshot-shaped verification after round 5** ran on a temporary copy with all 28 held-back paths deleted:
- **Result:** exit 0. The gate accepted the round 5 approval, and the publication gate reads `technically_ready` with zero scientific failures.
- **Registry:** byte-identical at `143a1e16...`.
- **Tests on the snapshot shape:** 559 passed, 0 failed, 8 skipped.
- **Copied back with LF endings:** `characterisation_manifest.json`, which now lists the six round 5 artifacts, and the two claim-audit JSONs, which were stale.
- **Expected differences:** the review drafts differ only in their notice lines.

Nothing is committed or pushed, and no snapshot is built.

The T1K index finding is truth-free (task logs), and it is reported as a fact, not as a defect. Whether it affected the RNA-seq T1K calls has not been examined, and judging that is the author's decision.

## Run on another machine and the snapshot build, 6 November

At the author's request ("A run on another machine, then building the snapshot"). The tree the snapshot would publish from `c5a60df` was built with the script's own hold-back list and no ref updated: tree `baddd874...`, 848 files. It was copied to Roihu with nothing held back added. Work files are in `/scratch/project_2008084/champhla_snapshot_check_20261106` and `D:/panelhla_work/snapshot_check_20261106`.

**Environment.** `scripts/setup_roihu_test_env.sh` built the pinned environment: Python 3.11.15, NumPy 1.26.4, SciPy 1.14.1, Matplotlib 3.9.2. All three public 1000 Genomes files matched their pinned SHA-256. The run used release mode (`RELEASE=1`: full resampling, tests not skipped, exact Python), which cannot run on the Windows machine.

**Result: every reported number reproduces, but the registry is not byte-identical.** Both release runs stopped at the registry-delta author gate, as designed:

| Run | Registry SHA-256 | What differs from the approved `143a1e16...` |
|---|---|---|
| Job 2922240 | `585648f7...` | 185 rows. One exploratory meta-consensus prediction moved (WES, HLA-A, second allele A*23:17 versus A*23:01): the case in `decisions/20261026_metaconsensus_floating_point_drift.json`. Its hash reaches 171 rows. 14 rows also differ in `sensitivity_adjusted_p` |
| Job 2922316, one repeat as that record prescribes | `2fac3e5d...` | 50 rows. Combined predictions are back at the approved `09a64e67...`. The 14 `sensitivity_adjusted_p` values still differ, and the other 36 rows differ only in the hashes of the two files that hold them |

The 14 values differ in the 16th or 17th significant digit, for example 0.004011279957868068 against 0.004011279957868069. Both runs gave the same values, so this is a deterministic Linux against Windows difference, not the meta-consensus variation. No count, estimate, interval, call or rounded value changed. The README tells a reader whose run stops at the gate to rerun when only meta-consensus rows differ. A reader on Linux will see these 14 rows on every run, so that advice does not fit them. Whether to record this and change the README is the author's decision. Nothing was changed.

The release freeze and the in-gate tests did not run, because the gate stops first. The test suite was run on a third untouched copy: 557 passed, 9 skipped, 1 failed. The failure, `test_sample_usage_reads_work_and_input_trees`, passed when rerun alone. It reads files' allocated size, so Roihu's Lustre scratch is the likely cause. The failure was not investigated further.

**Snapshot build.** `scripts/publish_snapshot.sh` failed closed at the first attempt. The cohort-label check added in S1 flagged `provenance/cohort_rows_withheld_20261106.json`. Signed S2 makes that file the public manifest whose rule names the withheld cohorts. It holds only counts and hashes, and `decisions/` already names the cohorts. The check now exempts exactly that file. Against the tested tree, the old check flags only that file and the new one flags nothing. No snapshot was built at that attempt, and `public-snapshot` stayed at `787aa7c`.

## Meta-consensus variation: S7.1 corrected and signed

The author signed `decisions/20261105_metaconsensus_variation.json` in the Claude Code session of 5 November ("Sign the correction"). The 26 October record is kept unedited.

- S7.1: the two sentences on the 26 October run are replaced by the signed wording, which gives the 17 and 26 refit tallies, the one refit that lowered the abstain-all WES meta-consensus score from 143/153 to 142/153, and drops "nearly tied".
- README: the registry-gate note cites the new record, says the variation can reach the primary and abstain-all artifacts, and keeps its advice to restore and rerun.
- No code changed. `src/champhla_confirmation/fitted.py` stays inside the pinned extension digest, and the registry is unchanged at `c02f0dfc...`, so the cohort-removal approval still holds.
- Full test suite 542 passed, 1 failed (the pre-existing wording test), 3 skipped. Word copies are rebuilt, and both review drafts pass parity. Claim audits show zero blocking failures, and the two audit files are refreshed. Lint passes on `src`, `scripts` and `tests`. A whole-tree `ruff check .` also flags 25 issues in `ablations/refformer`, which is unchanged since September. Full verification was not repeated, because only prose changed.

## JP-007 abstract: A-plus chosen and applied

The author chose option A-plus and allowed counts in the Claude Code session of 5 November ("A-plus; allow counts"), recorded in `decisions/20261105_abstract_counts_allowed.json`. `decisions/publication_route.json` now sets `abstract_numeric_performance_allowed` to true. All three options remain in `reports/abstract_options_20261105.md`.

After applying: full test suite 552 passed, 1 failed (the pre-existing wording test), 3 skipped; lint passed; claim audits show zero blocking failures, and the two audit files are refreshed. The registry is unchanged at `1b47f479...`. Word copies are rebuilt; layout was not inspected visually. Full verification was not repeated.

At the author's instruction, Results now states the abstract's corrected-value result, with existing result tags: the vote 153/153 in WES, HLA-HD 118/118 and the vote 117/118 in RNA-seq, post hoc and not independent.

## JP-005 amendment: signed and applied

`decisions/20261105_reference_attribution_amendment.json` holds the rule and the exact wording. The author signed it in the Claude Code session of 5 November ("Sign; not contaminated"), and that judgement is recorded in the same words. The wording is applied in Results, Discussion and S7. Erlich 2011 is now reference 48, and former references 48 to 53 are 49 to 54. The abstract is unchanged and still carries its earlier sentence on re-typing (JP-007).

After applying: full test suite 552 passed, 1 failed (the pre-existing wording test), 3 skipped; lint passed; claim audits show zero blocking failures, and the two audit files are refreshed. The registry is unchanged at `1b47f479...`, so the round 2 approval still holds. Word copies are rebuilt; layout was not inspected visually. Full verification was not repeated, because only prose and the reference numbers changed.

- It discloses that the main text already went past the signed "may reflect" limit in three places, and replaces those sentences.
- It changes no score and no registry row.
- Erlich Additional File 7 and Buchkovich Table S6 were re-read directly on 5 November, filtered to the 10 subjects. Erlich gives the vote's type at 9 of 10, and at NA19129 HLA-C the 2014 type; TruSight gives the vote's type at all 5 RNA-seq loci. This settles the check on the published-typing values listed under round 2 below. It does not replace a person reading the sources before submission.
- The contamination judgement is left blank for the author.

## MAJOR findings: registry round 2, built and signed

The author approved both records in the Claude Code session of 5 November ("I approve both"), and they now read SIGNED. They supersede the earlier approval of `00ce7f01...`.

**Full verification after signing:** run on a temporary copy of this working tree, with tests skipped because they ran separately. Exit 0, gate accepted the new approval, claim audits 0 scientific failures. The regenerated registry, every table and figure, and `manuscript.md` and `supplementary.md` were byte-identical to this checkout. The first attempt failed because the test script did not copy the new `resources/reference_adjudication/` folder; it was fixed and rerun. That failed attempt also showed the four compatibility tables differing, the known intermittent drift, so a future run can still stop at the gate as the README describes.

Three tracked outputs were stale here and were refreshed from the verified run, with LF line endings: `artifacts/benchmark_manuscript_audit.json`, `artifacts/benchmark_supplementary_audit.json` and `artifacts/development_characterisation/characterisation_manifest.json`. The manifest differed because it hashes the directory and now lists the new post hoc artifacts, which also explains the unexplained difference recorded under "Built and signed" below. The Word drafts differ only because that run builds them with different notice lines; the tracked copies were built by `scripts/build_review_draft.sh` and pass parity.

Before signing:

- `result_registry.tsv` went from 657 to 709 rows, SHA-256 `1b47f47955f1da58931bb4263d94112beb46ae6ae048c27af33845ab9435b36b`. The diff is 52 added rows (27 P group, 22 leave-one-out, 3 flagged-locus) and the hash and count fields of `PROTOCOL_CHANGE_LEDGER_20261013`. The 25 stop reasons are unchanged.
- To sign: `decisions/20261105_rerun_registry_delta_approved_round2.json` and `decisions/20261105_posthoc_round2_amendment.json`.
- Added: leave-one-caller-out table in S7 (JP-006) with the M:370 threshold sentence; published-typing table at the ten flagged loci in S7 (JP-005); P-group column in Table 2 (JP-013); ledger rows for the rerun's caller effects and the arcasHLA decision, with five earlier sizes labelled historical (JP-015).
- Values were written down before each script ran, and all 18 matched on the single run. The empty WGS rows were then removed from the leave-one-out output, with no count affected.
- To undo: the state before this round is in `C:/Users/uonur/AppData/Local/Temp/claude/D--projects-project-2008084-champhla-scirep-rerun-wt/5db22489-3ecf-43cc-8b3f-ce938d4411ba/scratchpad/pre_round2/`. The three new scripts, their three artifacts and the curated resource are new files.

**Checks after this round.** Full test suite 552 passed, 1 failed (the pre-existing wording test), 3 skipped; lint passed; claim audits show zero blocking failures in both documents. The gate refuses this registry with the unsigned record and with the earlier signed record. All three Word copies are rebuilt, with 46 tables, and both review drafts pass parity. Layout was not inspected visually, and Table 2 now has nine columns, so check how it fits. Full verification was not repeated.

**Not done in this round.**
- No main-text wording moves past "may reflect" (JP-005). The S7 table reports what the sources say and attributes nothing.
- The published-typing values were transcribed from the review's evidence file, which a second agent checked. They were not re-read from the source files, so a person should check them before submission.
- The 2011 454 study is cited by DOI in S7, because a numbered reference has to enter through the main text and renumbers the list. Add it when the JP-005 wording is settled.
- No ledger row for panel choice (JP-011), because no decision record of that choice was found. It needs the author's account.
- Figures 2-3 are still unmarked for arcasHLA, because they are hash-pinned.

---

# FATAL fixes (JP-001 to JP-004)

Applied at the author's instruction ("Yes, FATAL fixes first") on top of the uncommitted wording revisions of 27 and 28 October. The findings are in `D:/panelhla_work/reviews/journal_panel_20261103/journal_panel_review.md`. These changes are local and uncommitted. The Google Doc was not changed, and nothing was pushed or deposited.

## What changed

**JP-001, status.** The abstract and M:55, 272, 533, 539 and 560, plus S:1788, no longer say "pre-registered", "under way" or "is running" about the extension. They now say the plan is not yet publicly deposited, processing is paused with about 20 samples complete, and no comparison with reference genotypes has been made. The "about 20" and "paused" come from the author's statement of 2 November. **Check them again on the day of submission.**

**JP-002, Table 2.** The column is now "Loci where both typings agree, correct", changed in `scripts/generate_manuscript_tables.py` and its test. The table note says the filter removes all 15 vote errors by construction, with the count computed from the artifacts. M:443 names the other asterisked locus, and M:543 uses the new name. No count changed.

**JP-003, history.**
- S:1785 now discloses that truth-derived singleton-sensitivity rows prompted the inspection that found the collector defect, and gives the effect of the fix: RNA-seq vote 112 to 113, HLA-HD 98 to 112, arcasHLA 55 to 58, margin over OptiType 0 to +1 locus. The text follows the discovery path in the signed record `decisions/20261025_rerun_native_homozygote_collection.json`.
- M:128, M:441, S:196, S:790, S:1173 and S:1775 are corrected as the finding proposed.

**JP-004, availability.**
- M:92, the Figure 1A legend and S13.6 now say SpecHLA ran natively.
- M:278 and M:570 name what the image check covers.
- M:564 and M:570 say the repositories are private and that the verification script starts from the normalized caller tables, and M:564 explains what to do if a run stops at the registry gate.
- `README.md` carries the same note about the registry gate.

## Built and signed on 5 November

The ledger row, the S:873 wording and the S7 substitution table are in the working tree. The author approved both records in the Claude Code session of 5 November ("I approve both"), and they now read SIGNED.

**Full verification after signing:** run on a temporary copy of this working tree, with tests skipped because they ran separately. Exit 0, gate accepted the new approval, claim audits 0 scientific failures. The regenerated `result_registry.tsv`, every table and figure, and `manuscript.md` and `supplementary.md` were byte-identical to this checkout. Seven files differed in the copy:
- The two review Word drafts, which that run builds with different notice lines.
- `artifacts/benchmark_manuscript_audit.json` and `artifacts/benchmark_supplementary_audit.json`. The copies in this checkout are still the committed versions and do not describe the edited text; the next real run refreshes them.
- `cohorts/extension_v350_manifest.json` and `reports/manuscript_v7_changes_20261027.md`, which match HEAD here apart from CRLF line endings in this checkout. Neither was opened beyond hashing.
- `artifacts/development_characterisation/characterisation_manifest.json`, which matches HEAD here. Why the copy's version differed was not established before the copy was removed. Line endings from the Windows run are the likely cause, but that is unconfirmed.

Before signing:

- `result_registry.tsv` went from 630 to 657 rows, SHA-256 `00ce7f014925a004519f1f2c490992cb9ecf7fe4c5c25078a79233f5fbf4df2a`. The diff against the signed registry is 27 added `DEV_REFERENCE_SUBSTITUTION_*` rows and the hash and count fields of `PROTOCOL_CHANGE_LEDGER_20261013`. No other row changed, and the 25 stop reasons are the same as those already approved.
- Records: `decisions/20261105_rerun_registry_delta_approved_post_fixes.json` and `decisions/20261105_reference_presentation_amendment.json`. Any later registry change voids the signature.
- The gate's filename pattern in `scripts/reproduce_development_benchmark.py` was widened from `20261025_rerun_registry_delta_approved*.json` to `*_rerun_registry_delta_approved*.json`, so a record dated today can match. A record must still be signed and pin this exact registry and reason list.
- To undo: the registry, ledger, delta reports and manuscript sources from before this step are in `C:/Users/uonur/AppData/Local/Temp/claude/D--projects-project-2008084-champhla-scirep-rerun-wt/5db22489-3ecf-43cc-8b3f-ce938d4411ba/scratchpad/pre_registry_build/`.

The substitution table was run once. Before the repository script ran, the eleven review values were written down as the expected result, and all eleven matched. The script reads only development artifacts.

## Not applied: needs the author

| Item | Finding | Why it waits | What is ready |
|---|---|---|---|
| Whether the main text states the HLA-HD result under substitution | JP-002 | Bears on the headline claim | S7 states it; the main text does not |
| Figure 1A in-figure text ("process and container") | JP-004 | Figures are hash-pinned in `artifacts/release_freeze.json`. The legend now carries the correction | One-line change in `scripts/generate_figures.py` |
| `configs/caller_resources_v2.json` line 3, "blocked_pending_...", which M:278 sends readers to | JP-004 | The file's hash is pinned by the signed extension amendment | Nothing changed |
| Public deposit of the plan, referee access to both repositories at fixed tags | JP-001, JP-004 | Author actions | Nothing changed |
| Google Doc update | all | Outward-facing copy read by co-authors | The rebuilt `ChampHLA_manuscript_COMBINED_DRIVE.docx` is ready |

## Verification

**After the registry build:** full test suite 547 passed, 1 failed, 3 skipped, with the same pre-existing failure described below. Claim audits show zero blocking failures in both documents. The gate refuses the registry with the unsigned record, and with the old signed record, and accepts a scratch copy marked signed. The combined Word copy has 44 tables. The figures are unchanged. The lines below describe the earlier text-only step.

- Focused tests: 206 passed, 1 failed, across the 19 test files that read the manuscript sources. The failure, `test_mutually_available_comparison.py::test_reader_facing_text_does_not_invent_historical_task_state`, predates these fixes: it pins "In the v3.5.0 rerun every panel caller returned a row", which the 27 October wording revision replaced. It is left for the author, because the wording choice is theirs.
- Two tests were changed. `test_rerun_table_slots.py` pins the new column name. `test_correction_reported_as_robustness.py` pinned the S:790 sentence that JP-003 corrects, and now pins the corrected sentence; its checks on method scope are unchanged.
- Claim audits: zero blocking failures in both documents, with output written outside the repository. All 175 result tags are present.
- `result_registry.tsv` SHA-256 is unchanged: `6fd741d6e4427ef84268cd6b114df098ac982370262ba448e0bd185ca0be9f2a`. No artifact or figure changed.
- Only the Table 2 block was regenerated. All three Word copies were rebuilt, and both review drafts pass the parity check. The Word layout was not inspected visually.
- The full scientific regeneration gate was not repeated on these edits. They change prose, one table label and its note.

## New blocker found: the verification script fails on the public snapshot's contents

JP-004 left open whether `scripts/run_local_verification.sh` runs on the snapshot. It was tested once, in a temporary worktree at HEAD with the `scripts/publish_snapshot.sh` held-back paths deleted, unopened.

**It does not run.** It exits 1 at registry generation with `FileNotFoundError` on `artifacts/fimm_consensus/cohort_flow.tsv` (`scripts/generate_result_registry.py:137`), after about 30 minutes. Stages after the registry, including the tests and claim audits, did not run in that tree.

So M:564 is true of the full development tree but not of what a reader would receive from the current snapshot. Either the registry and figure steps must tolerate the held-back paths, or the patient cohorts leave the paper (the review recommends removing them, but that is the author's decision), or M:564 must say so. **Resolve this before any release.**
