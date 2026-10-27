# ChampHLA v6 sentence review — 26 October 2026

Review baseline: `ec8b777`; v5 manuscript sources agree with Drive v5 after excluding the expected rendering preface and header notes. All 425 body paragraphs and 43 tables matched. Drive v5 and the author’s copy both returned no comments.

Reviewed 849 sentence/prose-fragment units and 68 headings; changed 246 units. Each original sentence is represented, including unchanged OK decisions. Caption labels and list fragments are included as extra review units. Main text, using the Scientific Reports test’s word function: **4,226 → 4,008 words**.

Issue counts (a row can have several codes): AI 12, CLAR 33, FLOW 1, GRAM 16, HEDGE 3, JARG 10, LEN 157, LOGIC 12, NOM 10, PASS 51, REP 87, TERM 10.

## Items needing Umut’s decision

1. Corrected-reference equality: main Results and Discussion say the vote equals the strongest caller, although the adjacent WES counts differ. The original claims remain unchanged (M255.1, M309.1).
2. Panel scope: “graph, pangenome and assembly approaches were not evaluated” appears broader than the listed SpecHLA assembly method. The sentence remains unchanged (M321.1).
3. Historical source revision: Code availability assigns stored outputs to 7 April, while S10 says the whole historical run cannot be assigned to that tree. The sentence remains unchanged (M586.5).
4. Fitted caller attribution: S3 names POLYSOLVER, while S7 names OptiType for every WES fold. The original sentence remains unchanged; no caller was reselected (S404.1).
5. FIMM eligibility: S9.3 calls one view “more informative”, while the registry requires coequal exploratory definitions. The original sentence remains unchanged (S1230.1).
6. Detectability unit: S13 attributes the sign-flip limit to discordant loci rather than subjects. The original scientific unit remains unchanged (S1978.1).

The author-approved S5 tie correction is complete: stale prose now agrees with the existing zero-tie registry values and generated table. This changed no registered result, estimate, number or claim boundary. No other flagged scientific inconsistency was silently resolved.

## Author-approved pinned-wording repair

The author approved resuming after the gate stop. Six sentences (M53.1, M65.1, M370.1, M750.1, S1883.1 and S1145.1) are restored verbatim from v5, with tests unchanged. Each row retains its proposed editorial alternative in the note. Current totals: 849 prose/fragment units and 68 headings reviewed; 244 prose units and two headings changed. Main text: **4,226 → 4,008 words**.

## Coverage and safeguards

Original line numbers below refer to v5 at HEAD. Main-text order is Abstract, Introduction, Results, Discussion, Methods, Data availability, Code availability and figure legends, followed by supplementary prose. Fixed author fields, references, generated blocks, table cells and code blocks are excluded from editorial changes. Long numerical specifications and deliberate limitations may remain unchanged where splitting would obscure their scope.

All result tags, generated blocks, tables, code blocks and inline code tokens match the baseline. The numeric-token check passed for every edited sentence. British spelling and Oxford -ize forms are retained. Pending extension and NCI-60 sentences and all placeholders remain unchanged.

## Verification

Review drafts rebuilt with text/figure parity. The initial focused suite passed (85 tests). The first full gate stopped at six literal wording assertions (6 failed, 536 passed, 3 skipped); the author approved restoring those six original sentences and retaining the alternatives in their ledger notes. Tests and scientific code were unchanged. The expanded focused suite then passed: **145 passed**.

The full gate rerun completed: **542 passed, 3 skipped**; lint passed. Final line: `publication gate: author_input_required; scientific failures=0`. The expected FIMM author-input block remains. Result-tag multisets are identical: main 90, supplement 85. The result registry is byte-identical to HEAD, SHA-256 `6fd741d6e4427ef84268cd6b114df098ac982370262ba448e0bd185ca0be9f2a`. Generated manuscript blocks, table source lines, fenced/inline code, fixed author/reference sections and every edited sentence's numeric tokens were checked against v5. Only the two manuscript claim-audit artifacts changed, in source hashes and prose word counts.

The combined Word preview has a one-page preface followed by the main title, 13 inline figures and 43 tables, with no visible HTML comments, result tags or stray carets. Visual inspection covered every page; the PDF geometry check found no text outside the page and no replacement glyphs. Four tiny empty paragraphs separate adjacent Word tables so each table repeats its own header. All 43 raw table XML blocks are byte-identical to the CLI build; no table cells or source tables changed. This is an output-only layout repair.

Final combined DOCX: 82 visually checked pages; main title starts on page 2. The final file is byte-identical to the checked Word preview. Final Word-output tests: **49 passed**. Local and remote MD5: `fd180bccbac7be3ee1f0451fe0e35394`; size: 3597385 bytes. Uploaded as a NEW stored DOCX in AML_project, file id `1b0iPQG0DxGPGPYlf-dPmWwhUsT8cHBZz`. The target-name collision check was empty immediately before upload; earlier versions and the author copy were untouched. Roihu staging copy was deleted after successful verification. Connected Drive metadata readback confirmed stored Word MIME type, size and parent folder.

Drive: https://docs.google.com/document/d/1b0iPQG0DxGPGPYlf-dPmWwhUsT8cHBZz/edit?usp=drivesdk&ouid=101732235537539952688&rtpof=true&sd=true

## Sentence ledger


### Main — Abstract

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| M33.H | 33 | ## Abstract | OK | OK — unchanged |  |
| M35.1 | 35 | Short-read HLA genotyping depends on the caller, the sequencing assay and the reference database, and combining callers by voting is attractive when the best caller for a dataset cannot be known in advance. | LEN, REP | Short-read HLA genotyping depends on the caller, sequencing assay and reference database. Voting combines callers when the best caller for a dataset is unknown. |  |
| M35.2 | 35 | How such votes are evaluated, however, can inflate their apparent performance. | CLAR, REP | Evaluation choices can inflate a vote's apparent performance. |  |
| M35.3 | 35 | We evaluated ChampHLA-Consensus, an equal-weight plurality vote without fitted parameters, on 1000 Genomes whole-exome and Geuvadis RNA sequencing data at HLA-A, -B and -C, after re-running every caller with one pinned workflow release. | LEN | We evaluated ChampHLA-Consensus, an equal-weight plurality vote without fitted parameters, at HLA-A, -B and -C in 1000 Genomes whole-exome and Geuvadis RNA sequencing data. We re-ran every caller with one pinned workflow release. |  |
| M35.4 | 35 | A fail-closed endpoint excluded ambiguous, invalid or conflicting reference typing and counted no-calls as errors. | PASS | We excluded ambiguous, invalid or conflicting reference typing from a fail-closed endpoint and counted no-calls as errors. |  |
| M35.5 | 35 | In both assays the vote could not be distinguished from the strongest single caller, although so few subjects differed that only large effects were detectable. | OK | OK — unchanged |  |
| M35.6 | 35 | No fitted or threshold rule improved on it, and scoring ambiguous typing did not change the conclusions. | CLAR | No fitted or threshold rule improved on the vote, and scoring ambiguous typing did not change the conclusions. |  |
| M35.7 | 35 | Most errors that the callers shared coincided with loci at which a published re-typing had corrected the reference, a post hoc reading that is not independent of the exome data. | LEN, CLAR | Most shared caller errors coincided with loci where a published re-typing had corrected the reference. This post hoc interpretation is not independent of the exome data. |  |
| M35.8 | 35 | Exact-endpoint retention depended on population. | OK | OK — unchanged |  |
| M35.9 | 35 | ChampHLA-Consensus is therefore an auditable development baseline rather than evidence of equivalence or clinical validity; a pre-registered test on unseen subjects is under way. | OK | OK — unchanged | Pending-study sentence retained verbatim under the task freeze. |

### Main — Introduction

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| M41.H | 41 | ## Introduction | OK | OK — unchanged |  |
| M43.1 | 43 | The human leukocyte antigen (HLA) genes of the major histocompatibility complex (MHC) on chromosome 6p21.3 form one of the most polymorphic regions of the human genome [1]. | OK | OK — unchanged |  |
| M44.1 | 44 | The classical class I genes HLA-A, HLA-B and HLA-C, the subject of this study, present intracellular peptides to CD8-positive cytotoxic T cells. | REP | The classical class I genes studied here, HLA-A, HLA-B and HLA-C, present intracellular peptides to CD8-positive cytotoxic T cells. |  |
| M45.1 | 45 | They are the main route by which adaptive immunity surveys cells for infection, malignant transformation and, after transplantation, non-self antigens. | CLAR | These genes are the main route by which adaptive immunity surveys cells for infection, malignant transformation and, after transplantation, non-self antigens. |  |
| M47.1 | 47 | Errors in typing these genes have consequences. | CLAR | HLA typing errors have consequences. |  |
| M48.1 | 48 | In unrelated-donor haematopoietic cell transplantation, a single allele mismatch at HLA-A, -B, -C or -DRB1 is associated with higher mortality [2], and matching lowers the risks of graft failure and graft-versus-host disease [3]. | LEN | In unrelated-donor haematopoietic cell transplantation, a single allele mismatch at HLA-A, -B, -C or -DRB1 is associated with higher mortality [2]. Matching lowers the risks of graft failure and graft-versus-host disease [3]. |  |
| M49.1 | 49 | HLA-B\*57:01 predicts abacavir hypersensitivity [4], and HLA-B\*15:02 is associated with carbamazepine-induced Stevens–Johnson syndrome in Han Chinese patients [5]. | OK | OK — unchanged |  |
| M50.1 | 50 | The HLA genotype also determines which tumour neoantigens can be presented, so a typing error propagates into vaccine and T-cell receptor therapy design [6], and the region carries many of the strongest known associations with autoimmune disease [7]. | LEN | HLA genotype determines which tumour neoantigens can be presented, so typing errors propagate into vaccine and T-cell receptor therapy design [6]. The region also carries many of the strongest known associations with autoimmune disease [7]. |  |
| M52.1 | 52 | Typing these genes from short whole-exome sequencing (WES), whole-genome sequencing (WGS) or RNA sequencing (RNA-seq) reads is difficult. | OK | OK — unchanged |  |
| M53.1 | 53 | The genes are extraordinarily diverse: release 3.65.0 of the IPD-IMGT/HLA database (Immuno Polymorphism Database–ImMunoGeneTics HLA) [8], used here, contains 45,421 HLA allele designations in the pinned allele list (46,652 entries when MICA, MICB, TAP1, TAP2 and HFE are included). | AI, LEN | OK — unchanged | TEST PINNED: restored v5 verbatim with author approval on 26 October 2026; test unchanged. tests/test_reference_facts.py::test_stated_allele_count_matches_the_pinned_release. Proposed editorial alternative for author review: The genes are highly diverse. The pinned allele list from IPD-IMGT/HLA release 3.65.0 (Immuno Polymorphism Database–ImMunoGeneTics HLA) [8] contains 45,421 HLA allele designations (46,652 entries including MICA, MICB, TAP1, TAP2 and HFE). |
| M54.1 | 54 | Homologous loci make reads map to more than one place, and alignment to a single linear reference loses or misplaces reads from strongly divergent alleles before any caller sees them [9]. | OK | OK — unchanged |  |
| M55.1 | 55 | RNA-seq samples expressed rather than genomic copies, so a weakly expressed allele can be missed, and expression estimation is itself sensitive to polymorphism-aware mapping [10]. | LEN | RNA-seq samples expressed rather than genomic copies, so a weakly expressed allele can be missed. Expression estimation is itself sensitive to polymorphism-aware mapping [10]. |  |
| M57.1 | 57 | HLA callers draw on materially different evidence. | AI, REP | HLA callers use different evidence. |  |
| M58.1 | 58 | OptiType chooses the allele pair that best explains the reads by integer linear programming over read support [11] and HLA-HD by scoring alignments against an allele dictionary [12]; arcasHLA works from transcript abundance in RNA-seq [13], POLYSOLVER adds population allele frequencies as a prior [14], and T1K uses expectation maximization over allele abundance [15]. | LEN, GRAM | OptiType chooses the allele pair that best explains read support by integer linear programming [11]; HLA-HD scores alignments against an allele dictionary [12]. arcasHLA uses transcript abundance in RNA-seq [13], POLYSOLVER adds population allele frequencies as a prior [14], and T1K uses expectation maximization over allele abundance [15]. |  |
| M59.1 | 59 | Others combine alignment with local assembly and phasing (SpecHLA [16]), assemble alleles by graph-guided alignment (Kourami [17]), type class I alleles directly from RNA-seq (seq2HLA [18]) or align reads to graphs of known alleles (HLA\*LA and HISAT-genotype [9, 19]). | LEN, CLAR | SpecHLA combines alignment with local assembly and phasing [16], and Kourami assembles alleles by graph-guided alignment [17]. seq2HLA types class I alleles directly from RNA-seq [18]; HLA\*LA and HISAT-genotype align reads to graphs of known alleles [9, 19]. |  |
| M60.1 | 60 | Callers that share mapping assumptions may make correlated errors, which limits what a vote can correct; this study measures that dependence directly. | LEN | Callers that share mapping assumptions may make correlated errors, limiting what a vote can correct. We measured that dependence directly. |  |
| M61.1 | 61 | Running several callers is also operationally demanding, because they need different dependencies, databases and inputs (FASTQ reads, or alignments in BAM or its compressed form, CRAM) and report alleles in different formats. | LEN, REP | Running several callers requires different dependencies, databases and inputs: FASTQ reads or alignments in BAM or its compressed form, CRAM. Their allele formats also differ. |  |
| M62.1 | 62 | Outside a few public resources such as the 1000 Genomes Project [20, 21], sequencing data with reference HLA typing are rare, so accuracy on a new cohort usually cannot be measured. | OK | OK — unchanged |  |
| M63.1 | 63 | ChampHLA runs the callers for each assay in one Nextflow workflow [22], converts their outputs to a common two-field representation and applies a declared consensus rule (Methods). | OK | OK — unchanged |  |
| M65.1 | 65 | Benchmarks show that caller rankings depend on the assay, the gene and the dataset [23] and reveal typing-tool-specific errors [24], so the best caller for a new dataset cannot be known in advance. | LEN, TERM | OK — unchanged | TEST PINNED: restored v5 verbatim with author approval on 26 October 2026; test unchanged. tests/test_reference_facts.py::test_sr016_factual_corrections_and_primary_citations_are_present. Proposed editorial alternative for author review: Benchmarks show that caller rankings depend on assay, gene and dataset [23] and reveal caller-specific errors [24]. The best caller for a new dataset therefore cannot be known in advance. |
| M66.1 | 66 | Consensus is therefore attractive, but it is not new. | AI, FLOW | Several studies have evaluated consensus. |  |
| M67.1 | 67 | Larjo *et al.* [25] found that ensemble prediction could improve accuracy, and combining the three best tools outperformed any single tool on The Cancer Genome Atlas data [26], although there the labels came from agreement among the evaluated tools. | LEN, CLAR | Larjo *et al.* [25] found that ensemble prediction could improve accuracy. Combining the three best tools outperformed any single tool on The Cancer Genome Atlas data [26], although the labels there came from agreement among the evaluated tools. |  |
| M68.1 | 68 | Lee *et al.* [27] accepted a 1000 Genomes genotype when at least six of eight tools agreed. | OK | OK — unchanged |  |
| M69.1 | 69 | Claeys *et al.* [23] applied a majority vote, with ties broken toward the best tool, to 1000 Genomes exome and Geuvadis RNA-seq data. | OK | OK — unchanged |  |
| M70.1 | 70 | Their four-tool WES class I vote reached 99.0% against 98.0% for OptiType alone, with little gain in RNA-seq. | OK | OK — unchanged |  |
| M71.1 | 71 | Among workflows, consHLA combines HLA-HD results across germline and tumour sequencing of one patient [28], and nf-hlamajority implements majority class I typing from DNA in Nextflow [29]. | OK | OK — unchanged |  |
| M72.1 | 72 | SweHLA combined computational typings with targeted validation to build a population resource [30]. | OK | OK — unchanged |  |
| M74.1 | 74 | Much less attention has been paid to how a vote is evaluated, and two common choices make a vote look better than it is. | PASS, LEN | Evaluation choices have received less attention. Two common choices can inflate a vote's apparent performance. |  |
| M75.1 | 75 | The first completes every single reported allele into a homozygous pair, although for some callers a missing second allele marks a failed call. | OK | OK — unchanged |  |
| M76.1 | 76 | The second selects one allele from an ambiguous laboratory-typing string, which turns unresolved truth into an exact label. | OK | OK — unchanged |  |
| M77.1 | 77 | An earlier analysis of these data made both choices. | OK | OK — unchanged |  |
| M78.1 | 78 | This study completes a single allele only where the caller's own output format declares homozygosity, excludes ambiguous reference typing from the exact endpoint and scores it separately, and retains the earlier values only as provenance. | PASS, LEN, GRAM | We completed a single allele only where the caller's output format declared homozygosity. We excluded ambiguous reference typing from the exact endpoint, scored it separately and retained earlier values only as provenance. |  |
| M80.1 | 80 | We therefore asked a narrower question than earlier ensembles: within one assay and a named panel of callers, how does a deterministic equal-weight genotype vote, ChampHLA-Consensus, perform when failed calls, reference ambiguity and unavailable provenance are kept visible? | LEN, REP | We asked how ChampHLA-Consensus, a deterministic equal-weight genotype vote, performs within one assay and a named caller panel when failed calls, reference ambiguity and unavailable provenance remain visible. |  |
| M81.1 | 81 | We made the untrained vote the primary method deliberately. | TERM | We deliberately made the vote without fitted parameters primary. |  |
| M82.1 | 82 | An earlier version of this work used a champion–challenger design, in which a benchmark-selected caller supplies each gene's default call and a weighted ensemble may override it; the project keeps the name ChampHLA from that design. | LEN | An earlier version used a champion–challenger design: a benchmark-selected caller supplies each gene's default call, which a weighted ensemble may override. The project retains the name ChampHLA from that design. |  |
| M83.1 | 83 | With a single labelled development resource, the apparent gains of such fitted policies cannot be separated from fitting to that resource, so they are retained only as exploratory comparators (design rationale in Supplementary S13). | LEN, PASS | With a single labelled development resource, apparent gains of fitted policies cannot be separated from fitting to that resource. We retained them only as exploratory comparators (Supplementary S13). |  |
| M84.1 | 84 | A rule without fitted parameters can instead be stated completely, audited from each vote to the reported genotype and applied unchanged to new data. | OK | OK — unchanged |  |
| M85.1 | 85 | Every caller was re-run for this evaluation with one pinned release of the workflow, and a subject-disjoint extension roster, frozen with a signed analysis plan, is reserved for a confirmatory test. | OK | OK — unchanged |  |

### Main — Results

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| M87.H | 87 | ## Results | OK | OK — unchanged |  |

### Main — The exact endpoint retained a selected subset of loci

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| M89.H | 89 | ### The exact endpoint retained a selected subset of loci | OK | OK — unchanged |  |
| M91.1 | 91 | Only 153/390 requested WES loci and 118/318 requested RNA-seq loci had a unique two-field genotype after fail-closed parsing of the checksum-pinned source. | OK | OK — unchanged |  |
| M92.1 | 92 | The remaining WES loci were ambiguous (182), invalid (one) or absent from the source (54); for RNA-seq the corresponding counts were 145, one and 54. | OK | OK — unchanged |  |
| M93.1 | 93 | The retained WES set contained 50 HLA-A, 52 HLA-B and 51 HLA-C loci, and the RNA-seq set 38, 40 and 40. | OK | OK — unchanged |  |
| M94.1 | 94 | Reading every duplicate source record removed ten assay-loci that the earlier analysis had accepted, because a resolved duplicate had concealed an ambiguous one. | NOM, REP | Checking every duplicate source record removed ten assay-loci accepted earlier because a resolved duplicate had concealed an ambiguous one. |  |
| M95.1 | 95 | The earlier 390- and 321-locus denominators, which selected representatives from ambiguous typing strings, are therefore invalid for an exact two-field endpoint. | OK | OK — unchanged |  |
| M97.1 | 97 | Retention depended strongly on population. | OK | OK — unchanged |  |
| M98.1 | 98 | After pooling genes, 84.7% of CEU (CEPH) and 92.8% of YRI WES source-present loci were retained, compared with 3.9% of FIN, 3.9% of GBR and 8.3% of PUR loci. | OK | OK — unchanged |  |
| M99.1 | 99 | The exact endpoint is therefore demonstrably a selected subset of the data (Figure 1D; Supplementary S1). | AI, REP | The exact endpoint therefore represents a selected subset of the data (Figure 1D; Supplementary S1). |  |

### Main — The vote matched the strongest single caller, but the comparisons were small

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| M101.H | 101 | ### The vote matched the strongest single caller, but the comparisons were small | LOGIC, HEDGE | ### The vote could not be distinguished from the strongest caller in small comparisons | Restore the stated negative claim boundary; the v5 heading used “matched”, although non-significance does not establish equivalence. No result changed. |
| M103.1 | 103 | ChampHLA-Consensus called every retained locus (153/153 WES, 118/118 RNA-seq). | OK | OK — unchanged |  |
| M104.1 | 104 | Its exact genotype concordance was 143/153 (93.5%; subject-clustered 95% confidence interval [CI] 89.7–96.8%) for WES and 113/118 (95.8%; 92.1–99.1%) for RNA-seq, and its allele concordance was 296/306 (96.7%; 94.9–98.4%) and 231/236 (97.9%; 96.1–99.6%), respectively (Figure 2; Table 2). | LEN | Its exact genotype concordance was 143/153 (93.5%; subject-clustered 95% confidence interval [CI] 89.7–96.8%) for WES and 113/118 (95.8%; 92.1–99.1%) for RNA-seq. Allele concordance was 296/306 (96.7%; 94.9–98.4%) and 231/236 (97.9%; 96.1–99.6%), respectively (Figure 2; Table 2). |  |
| M108.1 | 108 | The strongest single caller in each assay scored slightly lower. | OK | OK — unchanged |  |
| M109.1 | 109 | In WES it was OptiType, with 142/153 correct genotypes, a paired difference of 0.65 points (Bonferroni-adjusted cluster-*t* 95% CI −3.44 to 4.74; sign-flip Holm *p*=1). | CLAR | OptiType was the strongest WES caller, with 142/153 correct genotypes, a paired difference of 0.65 points (Bonferroni-adjusted cluster-*t* 95% CI −3.44 to 4.74; sign-flip Holm *p*=1). |  |
| M110.1 | 110 | In RNA-seq HLA-HD and OptiType tied as the strongest callers with 112/118 each, one locus below the vote (0.85 points; −1.47 to 3.16; sign-flip Holm *p*=1 for both). | OK | OK — unchanged |  |
| M111.1 | 111 | These intervals permit benefit or harm and do not establish equivalence or non-inferiority (Figure 3). | OK | OK — unchanged |  |
| M119.1 | 119 | Neither comparison could have detected a difference. | CLAR, LOGIC | Neither exact sign-flip comparison could have detected a difference. | Specify the governing test, as Supplementary S3 requires; do not generalize the detectability limit to all valid analyses. |
| M120.1 | 120 | Only two WES subjects differed in correctness between ChampHLA-Consensus and OptiType, and only one RNA-seq subject between it and either of the strongest RNA-seq callers, so no exact test could reach *p*<0.05 at any effect size. | LEN, CLAR, LOGIC | Only two WES subjects differed in correctness between ChampHLA-Consensus and OptiType, and only one RNA-seq subject differed between the vote and either strongest caller. The exact sign-flip test therefore could not reach *p*<0.05 at any effect size. | Retain the observed subject counts and narrow “no exact test” to the declared exact sign-flip test; no number or inference changed. |
| M121.1 | 121 | In these comparison families, a significant difference with no losses would have required at least nine WES subjects (5.88 points) or eight RNA-seq subjects (6.78 points) to favour one method (Supplementary S3). | OK | OK — unchanged |  |
| M122.1 | 122 | A two-point non-inferiority margin was not met in WES (lower adjusted limit −3.44 points), and the RNA-seq lower limit (−1.47 points) rests on a single discordant subject. | OK | OK — unchanged |  |
| M127.1 | 127 | In the v3.5.0 rerun every panel caller returned a row for every retained locus. | OK | OK — unchanged |  |
| M128.1 | 128 | The stored historical outputs had lacked three callers' rows for one RNA-seq subject, a gap that had decided the earlier comparison with HLA-HD; stored and rerun calls are compared caller by caller in Supplementary S10. | LEN, PASS | The stored historical outputs lacked three callers' rows for one RNA-seq subject, a gap that decided the earlier comparison with HLA-HD. Supplementary S10 compares stored and rerun calls for each caller. |  |

### Main — No threshold or fitted rule improved on the vote

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| M159.H | 159 | ### No threshold or fitted rule improved on the vote | OK | OK — unchanged |  |
| M161.1 | 161 | After Holm correction within the descriptive comparison family, ChampHLA-Consensus had greater concordance than HLA-HD and T1K in WES, and than arcasHLA and T1K in RNA-seq. | OK | OK — unchanged |  |
| M162.1 | 162 | Its WES advantage over SpecHLA, 5.88 points (Bonferroni-adjusted cluster-*t* 95% CI −0.91 to 12.67), did not survive correction (sign-flip Holm *p*=0.133). | OK | OK — unchanged |  |
| M163.1 | 163 | Stricter vote thresholds reduced both callability and fixed-denominator concordance (Table 2; Supplementary Figure S2). | OK | OK — unchanged |  |
| M170.1 | 170 | In the exploratory fitted family, the nested-CV best-caller policy, refitted on the recovered subject folds under the current rules, scored 142/153 in WES (0.65 points below the vote; −3.25 to 4.56) and 111/118 in RNA-seq (1.69 points below; −1.02 to 4.41; sign-flip Holm *p*=1 and 0.5). | LEN | The exploratory nested-CV best-caller policy was refitted on the recovered subject folds under the current rules. It scored 142/153 in WES (0.65 points below the vote; −3.25 to 4.56) and 111/118 in RNA-seq (1.69 points below; −1.02 to 4.41; sign-flip Holm *p*=1 and 0.5). |  |
| M171.1 | 171 | Frozen predictions of the same policy from the earlier analysis, fitted under superseded labels and call states, had scored 99/118 and appeared significantly worse; they were replaced (Supplementary S7). | PASS, LEN | We replaced the earlier frozen predictions, fitted under superseded labels and call states, which had scored 99/118 and appeared significantly worse (Supplementary S7). |  |
| M172.1 | 172 | No fitted policy exceeded the primary method in either assay, and all of them share the development resource and lack validation on unseen subjects (Supplementary S2 and S7). | LEN | No fitted policy exceeded the primary method in either assay. All share the development resource and lack validation on unseen subjects (Supplementary S2 and S7). |  |

### Main — Scoring ambiguous typing kept the conclusions, but rankings depended on which loci were scored

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| M179.H | 179 | ### Scoring ambiguous typing kept the conclusions, but rankings depended on which loci were scored | OK | OK — unchanged |  |
| M181.1 | 181 | We next scored ambiguous reference typing instead of excluding it. | OK | OK — unchanged |  |
| M182.1 | 182 | Set-valued scoring made 335 WES and 263 RNA-seq loci with parseable source truth evaluable. | JARG | Set-valued scoring admitted 335 WES and 263 RNA-seq loci with parseable reference typing. |  |
| M183.1 | 183 | ChampHLA-Consensus was compatible with 321/335 WES candidate sets (95.8%; subject-clustered 95% CI 93.7–97.6%) and 257/263 RNA-seq candidate sets (97.7%; 95.8–99.2%). | OK | OK — unchanged |  |
| M184.1 | 184 | Mapping two-field designations to all compatible official IPD-IMGT/HLA 3.65.0 groups gave 324/333 (97.3%; 95.5–98.8%) for WES and 256/261 (98.1%; 96.2–99.6%) for RNA-seq under both the G- and P-group mappings, with two reference loci per assay unresolved for each endpoint. | OK | OK — unchanged |  |
| M185.1 | 185 | These compatibility analyses are more permissive than the exact primary endpoint and do not replace it (Supplementary Figure S4). | OK | OK — unchanged |  |
| M193.1 | 193 | The exact endpoint did, however, change which loci were scored. | AI, CLAR | Exact-reference filtering changed which loci were scored. |  |
| M194.1 | 194 | Of the retained loci, 125/153 WES and 105/118 RNA-seq came from the CEU (CEPH) and YRI HapMap samples, against 15/182 and 14/145 of the excluded loci that could be scored for compatibility (Supplementary S1). | OK | OK — unchanged |  |
| M195.1 | 195 | On those excluded loci ChampHLA-Consensus was compatible with 178/182 WES and 144/145 RNA-seq candidate sets, and OptiType was the strongest individual caller in both assays (176/182 and 143/145), ahead of POLYSOLVER in WES (168/182) and HLA-HD in RNA-seq (142/145). | LEN | On excluded loci ChampHLA-Consensus was compatible with 178/182 WES and 144/145 RNA-seq candidate sets. OptiType led individual callers in both assays (176/182 and 143/145), ahead of POLYSOLVER in WES (168/182) and HLA-HD in RNA-seq (142/145). |  |
| M196.1 | 196 | Exact-endpoint caller rankings therefore describe the retained, predominantly CEU and YRI loci, and compatibility on the excluded loci is lenient because any of several candidate genotypes counts. | LEN | Exact-endpoint rankings therefore describe the retained, predominantly CEU and YRI loci. Compatibility on excluded loci is lenient because any of several candidate genotypes counts. |  |
| M208.1 | 208 | No consensus error was attributable to nomenclature alone. | OK | OK — unchanged |  |
| M209.1 | 209 | All 15 ChampHLA-Consensus error loci (10 WES and 5 RNA-seq) were callable discordances, and every reference and predicted allele at them was a current IPD-IMGT/HLA 3.65.0 designation. | LEN, CLAR | All 15 ChampHLA-Consensus error loci (10 WES and 5 RNA-seq) were callable discordances. Every reference and predicted allele at those loci was a current IPD-IMGT/HLA 3.65.0 designation. |  |

### Main — Shared caller errors were mostly disagreements with the 2014 reference

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| M213.H | 213 | ### Shared caller errors were mostly disagreements with the 2014 reference | OK | OK — unchanged |  |
| M215.1 | 215 | A vote can correct one caller's error only when the other callers err differently. | OK | OK — unchanged |  |
| M216.1 | 216 | Pairwise caller-error φ, the phi coefficient between two callers' per-locus error indicators, ranged from 0.28 to 0.59 in WES (median 0.41) and from 0.11 to 0.82 in RNA-seq (median 0.34). | OK | OK — unchanged |  |
| M217.1 | 217 | Restriction to mutually callable loci did not remove the dependence: the corresponding ranges were 0.24–0.59 and 0.11–0.82. | NOM | Dependence remained after restricting analysis to mutually callable loci: the corresponding ranges were 0.24–0.59 and 0.11–0.82. |  |
| M218.1 | 218 | The strongest RNA-seq association was between HLA-HD and OptiType (φ=0.82 on the fixed denominator); intervals were wide, and for arcasHLA and OptiType the interval included zero (Figure 4; Supplementary S7). | LEN, CLAR | HLA-HD and OptiType had the strongest RNA-seq association (φ=0.82 on the fixed denominator). Intervals were wide, and the arcasHLA–OptiType interval included zero (Figure 4; Supplementary S7). |  |
| M226.1 | 226 | The same dependence bounds what any rule that selects among these outputs could achieve. | OK | OK — unchanged |  |
| M227.1 | 227 | Of the vote's 10 WES and 5 RNA-seq errors, an oracle allowed to choose any evaluated caller output could have corrected six WES errors and no RNA-seq error; four WES and five RNA-seq errors were not solved by any panel caller. | LEN | Of the vote's 10 WES and 5 RNA-seq errors, an oracle choosing any evaluated caller output could have corrected six WES errors and no RNA-seq error. No panel caller solved four WES and five RNA-seq errors. |  |
| M228.1 | 228 | A selector restricted to existing outputs therefore had ceilings of 149/153 (97.4%) for WES and 113/118 (95.8%) for RNA-seq; this is an oracle bound, not achievable performance. | OK | OK — unchanged |  |
| M236.1 | 236 | A published re-typing of the same exomes explains most of this apparent shared error. | OK | OK — unchanged |  |
| M237.1 | 237 | Under the pre-specified parsing rule, which treats asterisked values as unavailable, the second typing was unavailable at all 15 consensus errors. | OK | OK — unchanged |  |
| M238.1 | 238 | Wherever it was available it agreed with the reference (143/143 WES and 112/112 RNA-seq loci), as the rule entails. | OK | OK — unchanged |  |
| M239.1 | 239 | Read post hoc with the asterisk removed, the second typing equals the consensus call at all 15 of these error loci (10 WES, 5 RNA-seq), and only one other exact-endpoint locus carries an asterisk. | LEN, REP | Read post hoc with the asterisk removed, the second typing equals the consensus call at all 15 error loci (10 WES, 5 RNA-seq). Only one other exact-endpoint locus carries an asterisk. |  |
| M240.1 | 240 | At each of the 15, the source reports the 2014 type as incorrect; it records confirmation by targeted sequencing for some of these allele corrections and by inspection of the exome reads for the others [31]. | LEN | At each of the 15, the source reports the 2014 type as incorrect. It records confirmation by targeted sequencing for some allele corrections and by inspection of exome reads for the others [31]. |  |
| M241.1 | 241 | The five RNA-seq errors are the same subject–gene loci as five of the WES errors, with the same consensus genotype, although the two assays use different reads and partly different callers (Supplementary S7). | OK | OK — unchanged |  |
| M251.1 | 251 | Where the two typings agree, the vote and the strongest caller were almost always correct. | OK | OK — unchanged |  |
| M252.1 | 252 | On these loci ChampHLA-Consensus was correct at all 143 WES and all 112 RNA-seq loci; OptiType was correct at 141/143 WES and 111/112 RNA-seq loci and HLA-HD at all 112 RNA-seq loci. | LEN | On these loci ChampHLA-Consensus was correct at all 143 WES and all 112 RNA-seq loci. OptiType was correct at 141/143 WES and 111/112 RNA-seq loci, and HLA-HD at all 112 RNA-seq loci. |  |
| M253.1 | 253 | WES caller errors were nearly uncorrelated on this subset (φ −0.08 to 0.31, median 0.02), and the vote was correct at all 12 of HLA-HD's errors, all 12 of SpecHLA's and all 19 of T1K's. | LEN | WES caller errors were nearly uncorrelated on this subset (φ −0.08 to 0.31, median 0.02). The vote was correct at all 12 of HLA-HD's errors, all 12 of SpecHLA's and all 19 of T1K's. |  |
| M254.1 | 254 | In RNA-seq, HLA-HD made no error on this subset, and OptiType's single error was not shared with HLA-HD or T1K. | OK | OK — unchanged |  |
| M255.1 | 255 | Most consensus errors therefore probably reflect error in the 2014 reference typing rather than in the callers, and on this subset the vote equals the strongest caller because that caller makes almost no errors, not because errors are shared. | LOGIC, LEN | OK — unchanged | AUTHOR DECISION 1: “equals the strongest caller” is not literal for WES on this subset: the adjacent registered counts differ. Preserve pending author review; proposed wording: “the strongest caller makes almost no errors on this subset”. Keep “probably” and the exploratory interpretation. |
| M256.1 | 256 | This reading is exploratory: it was made after the data had been seen, rests on few errors, and uses a second typing derived from the same exomes, so it does not estimate independence (Supplementary S7). | LEN, CLAR | This exploratory interpretation was made after the data had been seen and rests on few errors. The second typing derives from the same exomes, so the analysis does not estimate independence (Supplementary S7). |  |

### Main — Call states, singletons, ties and vote support

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| M268.H | 268 | ### Call states, singletons, ties and vote support | OK | OK — unchanged |  |
| M270.1 | 270 | In the rerun every panel caller had a row at every exact-endpoint locus; two T1K WES rows were partial and one was missing (Supplementary S5). | OK | OK — unchanged |  |
| M271.1 | 271 | The singleton rows of HLA-HD (16 WES, 14 RNA-seq) and arcasHLA (9 RNA-seq), and T1K's declared homozygotes (12 WES, 11 RNA-seq), were completed as caller-declared homozygotes. | OK | OK — unchanged |  |
| M272.1 | 272 | Of the 64 single-allele rows at exact-endpoint loci, 57 lay at homozygous reference loci; the other seven, four arcasHLA RNA-seq declarations, one T1K WES declaration and the two partial T1K WES rows, lay at heterozygous reference loci (Supplementary Figure S1). | LEN | Of the 64 single-allele rows at exact-endpoint loci, 57 lay at homozygous reference loci. The other seven—four arcasHLA RNA-seq declarations, one T1K WES declaration and the two partial T1K WES rows—lay at heterozygous reference loci (Supplementary Figure S1). |  |
| M274.1 | 274 | No locus was tied in either assay, so the tie-break did not affect either result (143/153 and 113/118 with ties sent to the last-sorting pair). | OK | OK — unchanged |  |
| M275.1 | 275 | Concordance did not rise steadily with vote support, the number of callers supporting the reported genotype out of the number callable (Supplementary Figure S3). | OK | OK — unchanged |  |
| M276.1 | 276 | Full-panel unanimity was concordant at 103/104 WES 5/5 loci (99.0%) and 51/53 RNA-seq 4/4 loci (96.2%), so unanimous calls were usually, but not always, correct; among RNA-seq strata with at least five loci support was nonmonotonic, and these are descriptive proportions, not held-out calibration. | LEN | Full-panel unanimity was concordant at 103/104 WES 5/5 loci (99.0%) and 51/53 RNA-seq 4/4 loci (96.2%): unanimous calls were usually, but not always, correct. Among RNA-seq strata with at least five loci, support was nonmonotonic. These are descriptive proportions, not held-out calibration. |  |
| M277.1 | 277 | Results by gene, rare allele, population and zygosity are descriptive, with small strata outside CEU and YRI (Supplementary S4); analyses restored from earlier drafts describe the historical stored outputs and are reported as provenance (Supplementary S12). | LEN, REP | Results by gene, rare allele, population and zygosity are descriptive, with small strata outside CEU and YRI (Supplementary S4). Restored analyses describe historical stored outputs and are reported as provenance (Supplementary S12). |  |

### Main — Exploratory cohorts show that agreement is not accuracy

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| M283.H | 283 | ### Exploratory cohorts show that agreement is not accuracy | OK | OK — unchanged |  |
| M285.1 | 285 | Two aggregate-only exploratory patient cohorts illustrate this (Supplementary S9). | CLAR | Two aggregate-only exploratory patient cohorts illustrate the distinction between agreement and accuracy (Supplementary S9). |  |
| M286.1 | 286 | In FIMM, exact-pair agreement between bulk RNA-seq and WES was 62/70 (88.6%; Wilson 95% CI 79.0–94.1%) [32] when both assays had at least two valid callers, but every assay pair shared callers, and the caller-disjoint sensitivity analysis had no evaluable pairs. | LEN | In FIMM, bulk RNA-seq–WES exact-pair agreement was 62/70 (88.6%; Wilson 95% CI 79.0–94.1%) [32] when both assays had at least two valid callers. Every assay pair shared callers; the caller-disjoint sensitivity analysis had no evaluable pairs. |  |
| M287.1 | 287 | In VenEx WES, dissent from the inclusive plurality ranged from 0/230 for HLA-HD to 26/231 for SpecHLA, while POLYSOLVER had no mutually callable loci. | OK | OK — unchanged |  |
| M288.1 | 288 | These estimates are neither comparisons with independent truth nor evidence of clinical utility. | OK | OK — unchanged |  |
| M289.1 | 289 | An earlier NCI-60 cell-line analysis is being regenerated with the evaluated workflow release under a signed protocol and is not reported here (Supplementary S9.6). | OK | OK — unchanged | Pending-study sentence retained verbatim under the task freeze. |

### Main — Discussion

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| M296.H | 296 | ## Discussion | OK | OK — unchanged |  |
| M298.1 | 298 | Within these named panels, an equal-weight plurality vote could not be distinguished from the strongest caller of each assay, without anyone having to choose that caller in advance. | REP | Within these named panels, the equal-weight plurality vote could not be distinguished from each assay's strongest caller, without choosing that caller in advance. |  |
| M299.1 | 299 | It was one locus above OptiType in WES and one above both HLA-HD and OptiType in RNA-seq, and every genotype it reported can be traced to the votes behind it. | LEN, CLAR | The vote was one locus above OptiType in WES and one above both HLA-HD and OptiType in RNA-seq. Every reported genotype can be traced to its supporting votes. |  |
| M300.1 | 300 | No fitted policy did better, and the refitted nested-CV best-caller policy fell one locus short in WES and two in RNA-seq without a significant difference (Supplementary S7), so these data give no reason to prefer a trained rule. | LEN | No fitted policy did better. The refitted nested-CV best-caller policy fell one locus short in WES and two in RNA-seq without a significant difference (Supplementary S7). These data give no reason to prefer a trained rule. |  |
| M301.1 | 301 | The comparisons were small, though, and the vote was made primary after the results had been seen, so they establish neither equivalence nor superiority. | PASS, LEN | The comparisons were small, and we made the vote primary after seeing the results. They establish neither equivalence nor superiority. |  |
| M306.1 | 306 | The more informative question is why the vote gained so little, and the answer appears to lie in the reference rather than in the callers. | AI, REP, HEDGE | The vote's small gain appears to reflect the reference typing rather than the callers. | Retain “appears” because the reference-error interpretation is exploratory, not an independently established cause. |
| M307.1 | 307 | On all exact loci, correlated caller errors and small oracle headroom would ordinarily point to errors shared by the callers. | OK | OK — unchanged |  |
| M308.1 | 308 | Yet most of the loci behind that pattern were ones at which a published re-typing had already corrected the 2014 reference to the callers' genotype [31]. | REP | Most loci behind that pattern had already been corrected from the 2014 reference to the callers' genotype by a published re-typing [31]. |  |
| M309.1 | 309 | Where the two typings agreed, caller errors were nearly uncorrelated and the vote corrected almost all of them; it equalled the strongest caller because that caller made almost no errors. | LOGIC, LEN | OK — unchanged | AUTHOR DECISION 1: “equalled the strongest caller” repeats the non-literal WES equality in M255.1. Leave the claim unchanged; propose replacing the equality clause with “the strongest caller made almost no errors”. |
| M310.1 | 310 | A vote cannot improve on a caller that is already at the ceiling the reference allows, and a benchmark scored against an uncorrected reference can mistake agreement among callers for shared error. | LEN, REP | A vote cannot improve on a caller at the ceiling allowed by the reference. An uncorrected reference can make agreement among callers look like shared error. |  |
| M311.1 | 311 | This account is exploratory and should be tested against orthogonal laboratory typing. | OK | OK — unchanged |  |
| M313.1 | 313 | How the benchmark was scored mattered as much as the voting rule. | OK | OK — unchanged |  |
| M314.1 | 314 | Treating every single reported allele as homozygous conflates missingness with biological evidence; reading each caller's own declaration instead changed the scores of HLA-HD, arcasHLA, T1K and the RNA-seq vote, so both scorings are reported (Supplementary S2). | LEN, PASS | Treating every single allele as homozygous conflates missingness with biological evidence. Reading caller-native declarations changed the scores of HLA-HD, arcasHLA, T1K and the RNA-seq vote; we report both scorings (Supplementary S2). |  |
| M315.1 | 315 | Explicit call states, abstention, a reference parser that respects every source record, and exact and set-valued endpoints reported together are, in our view, prerequisites for credible HLA benchmarking; so is re-running the callers from recorded inputs, which here exposed a defective caller deployment that stored outputs would have hidden. | LEN, NOM, REP | Credible HLA benchmarks should record call states and abstentions, parse every reference record and report exact and set-valued endpoints together. Re-running callers from recorded inputs also matters: here it exposed a deployment defect that stored outputs would have hidden. |  |
| M317.1 | 317 | This is not the first vote across HLA callers. | AI | Earlier studies also combined HLA callers by voting. |  |
| M318.1 | 318 | Claeys *et al.* [23] evaluated a majority vote on the same public 1000 Genomes and Geuvadis data and had already kept failed predictions in an allele-level denominator; Lee *et al.* [27] combined distinct callers within one assay and had already restricted their genotype-level analysis to loci with one resolved reference genotype. | LEN, REP | Claeys *et al.* [23] evaluated a majority vote on the same public 1000 Genomes and Geuvadis data, keeping failed predictions in an allele-level denominator. Lee *et al.* [27] combined callers within an assay and restricted genotype-level analysis to loci with one resolved reference genotype. |  |
| M319.1 | 319 | What this evaluation adds is narrower: explicit caller-native call states, a deterministic tie-break that uses no performance information, a pinned and re-executable caller run, and an artifact registry that links every reported number to its source. | JARG, REP | This evaluation adds caller-native call states, a tie-break independent of performance, a pinned caller run that can be repeated, and traceability from every reported number to its source. |  |
| M320.1 | 320 | Claeys *et al.* reported allele-level accuracy, whereas our primary endpoint is unordered-genotype concordance, so their higher accuracies are not directly comparable; in both studies the vote's gain over the best single caller was small. | LEN, REP | Claeys *et al.* reported allele-level accuracy; our primary endpoint is unordered-genotype concordance, so the values are not directly comparable. In both studies the vote's gain over the best single caller was small. |  |
| M321.1 | 321 | Our panel spans only a few related algorithmic families, and graph, pangenome and assembly approaches were not evaluated, so ChampHLA-Consensus is a baseline and an audit framework, not a comprehensive comparison of HLA callers. | LOGIC | OK — unchanged | AUTHOR DECISION 2: “graph, pangenome and assembly approaches were not evaluated” may overstate panel exclusions: the Introduction describes SpecHLA as using local assembly. Leave unchanged; author should specify which additional callers or approaches were excluded. |
| M323.1 | 323 | For research use, these results do not justify running a multi-caller panel solely to improve concordance when a suitable assay-specific caller has already been validated. | OK | OK — unchanged |  |
| M324.1 | 324 | The plurality baseline is useful when the choice of caller is uncertain and an auditable rule without fitted parameters is wanted. | PASS, REP | The plurality baseline is useful when caller choice is uncertain and users want an auditable rule without fitted parameters. |  |
| M325.1 | 325 | They do not extend to clinical HLA typing, such as donor–recipient matching or pharmacogenomic screening, which requires accredited laboratory methods and regulatory-grade validation. | CLAR | These results do not extend to clinical HLA typing, including donor–recipient matching or pharmacogenomic screening, which requires accredited laboratory methods and regulatory-grade validation. |  |
| M326.1 | 326 | Users of the workflow should run it with `-profile paper`, which applies the evaluated rule rather than the unevaluated calibrated default. | OK | OK — unchanged |  |
| M327.1 | 327 | They should treat a single reported allele as homozygous only where the caller's format declares it, review tied loci and loci supported by only one caller, and report exact and ambiguity-compatible concordance together. | OK | OK — unchanged |  |
| M329.1 | 329 | The locked rule is now being tested on unseen subjects: the frozen extension roster is being processed with the same workflow release under a signed analysis plan whose public deposit precedes the one-time join with its reference typing. | OK | OK — unchanged | Pending-study sentence retained verbatim under the task freeze. |
| M330.1 | 330 | The NCI-60 cell-line application is being regenerated under a signed exploratory protocol. | OK | OK — unchanged | Pending-study sentence retained verbatim under the task freeze. |
| M331.1 | 331 | Graph and pangenome callers, harmonized databases, the class II genes HLA-DRB1 and HLA-DQB1, three-field reference typing, re-extracted WGS inputs, long-read modes and cohorts large enough for population-stratified analysis would separate algorithm from deployment effects and widen the evaluation. | LEN | Evaluating graph and pangenome callers, harmonized databases, class II genes HLA-DRB1 and HLA-DQB1, three-field reference typing, re-extracted WGS inputs and long-read modes would widen the study. Larger cohorts would allow population-stratified analysis and help separate algorithm from deployment effects. |  |
| M333.1 | 333 | **Design.** | OK | OK — unchanged |  |
| M333.2 | 333 | This is a retrospective development study without independent external validation. | OK | OK — unchanged |  |
| M334.1 | 334 | The primary rule, the multiplicity scheme, the primary paired test and single-allele handling were all set or changed after development results had been seen (Methods, Protocol history), so every development result is exploratory. | PASS, LEN | We set or changed the primary rule, multiplicity scheme, primary paired test and single-allele handling after seeing development results (Methods, Protocol history). Every development result is therefore exploratory. |  |
| M335.1 | 335 | A subject-disjoint extension roster of 89 WES and 99 RNA-seq subjects was frozen before any truth join; its pre-specified confirmatory analysis is running and is not reported here. | OK | OK — unchanged | Pending-study sentence retained verbatim under the task freeze. |
| M336.1 | 336 | WES and RNA-seq subjects overlap and the filtered sets are small; the same five subject–gene loci account for all RNA-seq vote errors and five WES errors, so agreement across assays is not independent replication. | LEN | WES and RNA-seq subjects overlap, and the filtered sets are small. The same five subject–gene loci account for all RNA-seq vote errors and five WES errors, so cross-assay agreement is not independent replication. |  |
| M338.1 | 338 | **Reference typing.** | OK | OK — unchanged |  |
| M338.2 | 338 | The reference is the fallible 2014 exon 2–3 table interpreted against a 2009 allele release, and only HLA-A, HLA-B and HLA-C were evaluated, at two-field resolution. | OK | OK — unchanged |  |
| M339.1 | 339 | Several callers were developed or evaluated against typings of these same samples (Methods), so neither the primary nor the corrected-reference comparison is independent of every caller, and absolute concordance may be optimistic. | LEN | Several callers were developed or evaluated against typings of these same samples (Methods). Neither the primary nor the corrected-reference comparison is independent of every caller, and absolute concordance may be optimistic. |  |
| M340.1 | 340 | Exclusion of ambiguous typing was strongly population-dependent. | OK | OK — unchanged |  |
| M341.1 | 341 | Retention reflects how each contributing laboratory encoded ambiguity as well as typing resolution or quality, so it must not be read as a population accuracy estimate. | OK | OK — unchanged |  |
| M343.1 | 343 | **Samples, callers and provenance.** | OK | OK — unchanged |  |
| M343.2 | 343 | Both assays were generated from lymphoblastoid cell lines, whose high HLA expression and cell-state composition limit transfer of the RNA-seq result to primary or tumour tissue. | OK | OK — unchanged |  |
| M344.1 | 344 | The caller panel reflects the original deployment and used different database vintages and reference builds. | OK | OK — unchanged |  |
| M345.1 | 345 | For the historical stored outputs the executables, native search databases and container digests were not recorded; the v3.5.0 rerun pins the workflow release and records each sample's container digests, but differences between callers still combine algorithm, deployment and reference-resource effects, so the caller ranking describes deployed tools rather than algorithms (Supplementary S13). | LEN | Historical executables, native search databases and container digests were not recorded. The v3.5.0 rerun pins the workflow release and records each sample's container digests. Caller differences still combine algorithm, deployment and reference-resource effects; rankings describe deployed tools rather than algorithms (Supplementary S13). |  |
| M346.1 | 346 | The rerun also exposed a deployment defect carried by the pinned release: its arcasHLA module extracts reads from the paired-end Geuvadis libraries as single-end, and the arcasHLA 0.2.0 container then genotypes them without pair information. | LEN, REP | The rerun exposed a defect in the pinned release: its arcasHLA module extracts paired-end Geuvadis reads as single-end. The arcasHLA 0.2.0 container then genotypes them without pair information. |  |
| M347.1 | 347 | A truth-free comparison shows that the rerun arcasHLA calls differed from the stored ones at 176 of 318 RNA-seq caller–gene cells and included many rarely observed allele designations (Supplementary Table S10.2); its exact concordance was 58/118, and the deployment was diagnosed only after that score had been seen. | LEN, PASS | In a truth-free comparison, rerun arcasHLA calls differed from stored calls at 176 of 318 RNA-seq caller–gene cells and included many rarely observed allele designations (Supplementary Table S10.2). Exact concordance was 58/118; we diagnosed the deployment only after seeing that score. |  |
| M348.1 | 348 | We report the result as the pinned deployment produced it and did not change the module, so the arcasHLA estimate describes that deployment rather than the caller. | OK | OK — unchanged |  |
| M350.1 | 350 | WGS outputs from the original caller run failed input-validity checks involving HLA alternate contigs and read extraction, and all quantitative WGS results were removed. | OK | OK — unchanged |  |
| M352.1 | 352 | **Statistics.** | OK | OK — unchanged |  |
| M352.2 | 352 | Single-allele handling changes individual callers' scores (Supplementary S2). | OK | OK — unchanged |  |
| M353.1 | 353 | Lexicographic tie-breaking is deterministic but not biologically informed, and it needs prospective replacement or review routing. | OK | OK — unchanged |  |
| M354.1 | 354 | Support strata were not externally calibrated; rare alleles, homozygotes and most population strata were too few to analyse; and the post hoc non-inferiority and power analyses are sensitivity analyses only. | LEN | Support strata were not externally calibrated. Rare alleles, homozygotes and most population strata were too few to analyse. The post hoc non-inferiority and power analyses are sensitivities only. |  |
| M356.1 | 356 | Taken together, ChampHLA-Consensus is an auditable development baseline rather than a new inference algorithm or clinical typing system: with fail-closed reference typing, fixed denominators, explicit call states and a re-executed caller run, it could not be distinguished from the best single caller in WES or RNA-seq. | AI, LEN | ChampHLA-Consensus is an auditable development baseline. With fail-closed reference typing, fixed denominators, explicit call states and a re-executed caller run, it could not be distinguished from the best single caller in WES or RNA-seq. It provides neither a new inference algorithm nor a clinical typing system. |  |
| M356.2 | 356 | Its value is operational: users need not choose a caller in advance, and every reported genotype remains traceable to the calls that support it. | OK | OK — unchanged |  |
| M356.3 | 356 | The pre-registered extension will test the locked rule on unseen subjects; claims of equivalence, generalization or clinical use require independent laboratory typing beyond it. | OK | OK — unchanged |  |

### Main — Methods

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| M358.H | 358 | ## Methods | OK | OK — unchanged |  |

### Main — Study design and data

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| M360.H | 360 | ### Study design and data | OK | OK — unchanged |  |
| M362.1 | 362 | This retrospective benchmark ran the callers on 1000 Genomes WES and Geuvadis RNA-seq data [20, 33] with release 3.5.0 of the ChampHLA workflow in October 2026, and its primary inputs are the normalized, truth-free output tables of that run. | LEN, PASS | We ran callers on 1000 Genomes WES and Geuvadis RNA-seq data [20, 33] with ChampHLA workflow release 3.5.0 in October 2026. This retrospective benchmark uses the run's normalized, truth-free output tables as its primary inputs. |  |
| M363.1 | 363 | A *subject* is one individual in these public collections of consented population-genomics donors; the development set contains no clinical samples. | OK | OK — unchanged |  |
| M364.1 | 364 | A *locus* is one subject–gene pair within one assay. | OK | OK — unchanged |  |
| M365.1 | 365 | Each run records the workflow release commit, its scheduler job and checksummed manifests of its inputs, container images, workflow files and results (Supplementary S10). | OK | OK — unchanged |  |
| M366.1 | 366 | An earlier caller run of April and May 2026, made with an unarchived pre-release deployment whose executables, container images and launch parameters were not preserved, supplied the historical stored outputs; they enter only the stored-to-rerun comparison (Supplementary S10) and the restored analyses (Supplementary S12). | LEN | Historical stored outputs came from an April and May 2026 caller run with an unarchived pre-release deployment. Its executables, container images and launch parameters were not preserved. Those outputs enter only the stored-to-rerun comparison (Supplementary S10) and restored analyses (Supplementary S12). |  |
| M367.1 | 367 | The paper repository verifies every later step: normalization, truth selection, joining, statistics, tables, figures and manuscript generation. | OK | OK — unchanged |  |
| M368.1 | 368 | We call these data the *development set*, because the primary reporting rule was selected after results on them had been inspected; its development performance is post hoc and is not a prospective validation. | PASS, LEN | We call these data the *development set* because we selected the primary reporting rule after inspecting their results. Development performance is post hoc, not prospective validation. |  |
| M370.1 | 370 | The signed rerun roster contained 130 WES subjects (390 subject–gene loci) and 106 RNA-seq subjects (318 loci), 105 of whom also occurred in the WES roster; capture kit, read length, sequencing depth and original preprocessing metadata were not available. | LEN, REP | OK — unchanged | TEST PINNED: restored v5 verbatim with author approval on 26 October 2026; test unchanged. tests/test_sr023_consistency.py::test_identity_counts_distinguish_pre_and_post_withholding. Proposed editorial alternative for author review: The signed rerun roster contained 130 WES subjects (390 subject–gene loci) and 106 RNA-seq subjects (318 loci), 105 also in the WES roster. Capture kit, read length, sequencing depth and original preprocessing metadata were unavailable. |
| M371.1 | 371 | The two assays are analysed separately and are not independent replications. | PASS, GRAM | We analysed the assays separately; they are not independent replications. |  |
| M372.1 | 372 | After exact-truth filtering, the analyses contained 63 WES subjects and 51 RNA-seq subjects, 50 of whom occurred in both sets; these subjects are also the clusters used for inference. | LEN, GRAM | Exact-truth filtering left 63 WES subjects and 51 RNA-seq subjects, 50 present in both sets. Subjects were the clusters used for inference. |  |
| M374.1 | 374 | Sample identity was checked without reference to truth. | PASS | We checked sample identity without reference to truth. |  |
| M375.1 | 375 | Every input had to appear in the official 1000 Genomes and Geuvadis assay manifest, and no rerun input was absent from it. | OK | OK — unchanged |  |
| M376.1 | 376 | For the 105 subjects present in both assays, the WES and RNA-seq consensus genotypes were then compared at every gene called in both: 101 subjects shared all six alleles and four shared five. | PASS, REP | For the 105 subjects in both assays, we compared WES and RNA-seq consensus genotypes at every gene called in both: 101 subjects shared all six alleles and four shared five. |  |
| M377.1 | 377 | This check was added after the development results were known, and it was first applied to the historical stored outputs. | PASS, REP | We added this check after the development results were known and first applied it to historical stored outputs. |  |
| M378.1 | 378 | There the NA07000 RNA-seq input shared one of six alleles with its WES input and was absent from the manifest, so it was withheld as a provenance failure and the signed rerun roster excludes it; its WES input, which is in the manifest, was retained. | LEN, PASS | The stored NA07000 RNA-seq input shared one of six alleles with its WES input and was absent from the manifest. We withheld it as a provenance failure; the signed rerun roster excludes it. Its WES input was in the manifest and retained. |  |
| M379.1 | 379 | In the stored outputs that input's two exact-endpoint RNA-seq loci were both consensus errors, and including them gave 113/120 (Supplementary S7, protocol-change ledger). | OK | OK — unchanged |  |
| M386.1 | 386 | Three exploratory applications lie outside the primary analysis and support no accuracy, external-validation or abstract claim (Supplementary S9). | OK | OK — unchanged |  |
| M387.1 | 387 | The FIMM AML/MDS and VenEx WES cohorts contribute aggregate cross-assay agreement and within-panel dissent only. | OK | OK — unchanged |  |
| M388.1 | 388 | In a flow-linked FIMM subset, BB7.2 antibody status gives serogroup-level agreement; BB7.2 was characterized as an HLA-A2 reagent [34], and single-antigen beads show specificity for HLA-A\*02 and A\*69 with cross-reactivity at high concentration [35]. | OK | OK — unchanged |  |
| M389.1 | 389 | The NCI-60 cancer cell lines have published sequence-based class I typing [36]; an earlier NCI-60 analysis is withdrawn because its estimates cannot be traced to registered results, and the application is being regenerated with release 3.5.0, the development panels and a fail-closed parser of that typing (Supplementary S9.6). | OK | OK — unchanged | Pending-study sentence retained verbatim under the task freeze. |

### Main — The ChampHLA workflow

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| M391.H | 391 | ### The ChampHLA workflow | OK | OK — unchanged |  |
| M393.1 | 393 | ChampHLA is a Nextflow workflow [22] that runs each caller of the assay's panel (Table 1) as an independent containerized process, parses every output into unordered two-field genotypes and combines the callers at each sample and gene (Figure 1A). | LEN | ChampHLA runs each caller in an assay's panel (Table 1) as an independent containerized Nextflow process [22]. It parses outputs into unordered two-field genotypes and combines callers at each sample and gene (Figure 1A). |  |
| M394.1 | 394 | For BAM or CRAM input, reads in the chromosome 6 MHC window and on HLA-allele and alternate-haplotype contigs are first realigned to chromosome 6 with BWA-MEM [37], so that every caller sees both haplotypes (Supplementary S11.1). | OK | OK — unchanged |  |
| M395.1 | 395 | Under `-profile paper` the consensus step implements ChampHLA-Consensus, and a test in the workflow repository requires it to reproduce the ChampHLA-Consensus call at all 708 development loci (Supplementary S11.2); the workflow's default calibrated weighting was not evaluated. | LEN, REP | Under `-profile paper`, the consensus step implements ChampHLA-Consensus. A workflow test requires the same call at all 708 development loci (Supplementary S11.2). The default calibrated weighting was not evaluated. |  |
| M396.1 | 396 | All development results in this paper were computed by applying the rule in the paper repository to the normalized caller tables of the release 3.5.0 run. | PASS, REP | We computed all development results by applying the paper-repository rule to normalized caller tables from the release 3.5.0 run. |  |
| M411.1 | 411 | The last column gives the earliest IPD-IMGT/HLA release consistent with each caller's bundled database, a content-derived lower bound (Supplementary S6) that is not necessarily the release used to build the caller. | OK | OK — unchanged |  |
| M412.1 | 412 | For example, the POLYSOLVER publication reports IMGT/HLA 3.10, whereas 3.11.0 is the lower bound for the preserved allele list [14]. | OK | OK — unchanged |  |
| M413.1 | 413 | The arcasHLA value comes from a bundled version report that was not preserved. | OK | OK — unchanged |  |
| M414.1 | 414 | The reference typing was interpreted against IMGT/HLA 2.26.0 [21]. | OK | OK — unchanged |  |
| M415.1 | 415 | Kourami and seq2HLA are wrapped by the workflow but lie outside the evaluated panels, and their incomplete historical outputs are not scored. | OK | OK — unchanged |  |

### Main — Reference HLA typing and denominator construction

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| M417.H | 417 | ### Reference HLA typing and denominator construction | OK | OK — unchanged |  |
| M419.1 | 419 | Reference genotypes were taken from the International Genome Sample Resource (IGSR) copy of the 2014 1000 Genomes HLA diversity table [21], pinned to its SHA-256 checksum, a cryptographic fingerprint that changes if any byte of the file changes (Data availability); a mismatch stops regeneration. | PASS, LEN | We obtained reference genotypes from the International Genome Sample Resource (IGSR) copy of the 2014 1000 Genomes HLA diversity table [21]. Its SHA-256 checksum is pinned: any byte change alters this cryptographic fingerprint and stops regeneration (Data availability). |  |
| M421.1 | 421 | This table is laboratory typing, not error-free truth. | OK | OK — unchanged |  |
| M422.1 | 422 | Class I loci were typed by locus-specific polymerase chain reaction (PCR) and Sanger sequencing of exons 2 and 3 and interpreted against IMGT/HLA 2.26.0 (July 2009); allele ambiguities were retained, and confirmatory typing was performed for 12 samples [21]. | OK | OK — unchanged |  |
| M423.1 | 423 | Such typing cannot separate alleles that differ only outside exons 2 and 3, and a 2009 release cannot name alleles described later. | OK | OK — unchanged |  |
| M424.1 | 424 | Independent typings of the same samples do not always agree: of 263 1000 Genomes samples typed in more than one study, 221 (84%) had concordant typings [38]. | OK | OK — unchanged |  |
| M425.1 | 425 | When 992 of the typed individuals were retyped from exome data, read inspection and new laboratory typing of 21 individuals led the authors to retain 105 results that disagreed with the published types [31]. | OK | OK — unchanged |  |
| M426.1 | 426 | Agreement with this reference therefore combines caller error with reference error, and the exact endpoint measures agreement with the reference rather than accuracy against the true genotype. | OK | OK — unchanged |  |
| M428.1 | 428 | We used that in silico re-typing by Abi-Rached *et al.* [31], obtained from IGSR with a pinned checksum, to adjudicate consensus errors. | OK | OK — unchanged |  |
| M429.1 | 429 | In it, an asterisk marks a result that disagreed with the previously published type and that its authors kept after verification [31]. | OK | OK — unchanged |  |
| M430.1 | 430 | Thuesen *et al.* later used these corrections to update the 2014 types in an exome benchmark [39], and Buchkovich *et al.* replaced 38 discordant and two low-resolution Geuvadis allele calls after targeted typing of 34 samples [40]. | OK | OK — unchanged |  |
| M431.1 | 431 | Because the re-typing derives from the same exome data, and T1K and SpecHLA were evaluated against it in their original publications [15, 16], it can adjudicate a discordance but never replaces the reference. | OK | OK — unchanged |  |
| M432.1 | 432 | Its parsing rule, adjudication classes and a sensitivity analysis restricted to loci where both typings agree were fixed in a signed decision before any comparison was made. | OK | OK — unchanged |  |
| M433.1 | 433 | That rule treats an asterisked value as unavailable, so the comparison with the corrected values (Results) is post hoc. | OK | OK — unchanged |  |
| M435.1 | 435 | Exact scoring requires an exact reference genotype, but the source includes allele-ambiguity strings and duplicate subject records. | OK | OK — unchanged |  |
| M436.1 | 436 | We therefore built the denominator fail-closed. | OK | OK — unchanged |  |
| M437.1 | 437 | Every source row for a subject and gene was parsed, and the locus was excluded from the exact endpoint if any row was ambiguous, invalid or conflicting, so that a resolved duplicate could not conceal an ambiguous one. | PASS, LEN | We parsed every source row for each subject and gene, excluding a locus from the exact endpoint if any row was ambiguous, invalid or conflicting. A resolved duplicate could not conceal an ambiguous one. |  |
| M438.1 | 438 | No first-listed or frequency-preferred allele was ever selected. | OK | OK — unchanged |  |
| M439.1 | 439 | The audit excluded 237/390 requested WES loci and 200/318 RNA-seq loci, leaving 153 WES loci from 63 subjects and 118 RNA-seq loci from 51 subjects. | OK | OK — unchanged |  |
| M440.1 | 440 | Predictions for all 708 requested loci were generated and checksummed before any truth was selected (Figure 1C). | PASS | We generated and checksummed predictions for all 708 requested loci before selecting any truth (Figure 1C). |  |
| M442.1 | 442 | Because exclusion discards information, secondary analyses scored the ambiguous typing instead, representing the reference as every valid unordered two-field candidate pair; a prediction was compatible when it matched any allowed pair, which made 335 WES and 263 RNA-seq loci evaluable. | LEN | To retain information from ambiguous typing, secondary analyses represented the reference as every valid unordered two-field candidate pair. A prediction was compatible if it matched any allowed pair, making 335 WES and 263 RNA-seq loci evaluable. |  |
| M443.1 | 443 | Further sensitivity analyses mapped each two-field designation to every compatible official IPD-IMGT/HLA 3.65.0 G group and P group; they test compatibility under a two-field mapping and do not infer exact P- or G-group calls. | LEN | Further sensitivities mapped each two-field designation to every compatible official IPD-IMGT/HLA 3.65.0 G group and P group. They test compatibility under a two-field mapping and do not infer exact P- or G-group calls. |  |
| M444.1 | 444 | Supplementary S1 describes the exclusions by gene, source population, source-truth state and candidate-pair count. | OK | OK — unchanged |  |
| M445.1 | 445 | Populations use the 1000 Genomes codes, among them CEU (Utah residents with Northern and Western European ancestry) and YRI (Yoruba in Ibadan, Nigeria); the others are defined in Supplementary S1. | OK | OK — unchanged |  |

### Main — Callers and assay-specific panels

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| M447.H | 447 | ### Callers and assay-specific panels | OK | OK — unchanged |  |
| M449.1 | 449 | Each assay was analysed with its own panel of intended-use callers (Table 1): HLA-HD, OptiType, POLYSOLVER, SpecHLA and T1K for WES, and arcasHLA, HLA-HD, OptiType and T1K for RNA-seq. | PASS | We used a separate intended-use panel for each assay (Table 1): HLA-HD, OptiType, POLYSOLVER, SpecHLA and T1K for WES; arcasHLA, HLA-HD, OptiType and T1K for RNA-seq. |  |
| M450.1 | 450 | The panels are declared in the analysis code (`src/champhla_confirmation/panels.py`) and have not changed since the paper repository's first commit on 1 September 2026, after the caller run. | OK | OK — unchanged |  |
| M451.1 | 451 | They reflect the callers deployed in that run rather than an exhaustive modern benchmark. | OK | OK — unchanged |  |
| M452.1 | 452 | HLA\*LA and HISAT-genotype were not run [9, 19], and the historical outputs of Kourami and seq2HLA [17, 18], like those of off-panel caller–assay combinations, are partly incomplete and are not scored (Supplementary S6). | OK | OK — unchanged |  |
| M454.1 | 454 | This benchmark is not independent of the callers' own development. | OK | OK — unchanged |  |
| M455.1 | 455 | Five of the six panel callers were evaluated in their original publications against reference typings of 1000 Genomes samples, using exome or Geuvadis RNA-seq data from the collections used here [11, 13–16]. | OK | OK — unchanged |  |
| M456.1 | 456 | They are OptiType, whose β parameter was chosen by cross-validation on 253 1000 Genomes exome runs, POLYSOLVER, arcasHLA, T1K and SpecHLA. | OK | OK — unchanged |  |
| M457.1 | 457 | We could not find in an open-access source which data were used to evaluate HLA-HD [12]. | OK | OK — unchanged |  |
| M458.1 | 458 | The development subjects may therefore include samples on which these callers were developed or evaluated, which could not be checked subject by subject and can inflate absolute concordance for the callers and for any consensus built from them. | LEN, PASS | The development subjects may include samples used to develop or evaluate these callers; we could not check this subject by subject. Such overlap can inflate absolute concordance for callers and votes built from them. |  |
| M460.1 | 460 | The rerun records what each caller received. | OK | OK — unchanged |  |
| M461.1 | 461 | WES inputs are the GRCh38DH exome alignments (the GRCh38 human reference with decoy and HLA allele sequences), and release 3.5.0 realigns reads placed on HLA-allele and alternate-haplotype contigs to primary chromosome 6 before any DNA caller runs; RNA-seq inputs are the GRCh37 Geuvadis alignments. | LEN | WES inputs are GRCh38DH exome alignments (the GRCh38 reference with decoy and HLA allele sequences). Release 3.5.0 realigns reads on HLA-allele and alternate-haplotype contigs to primary chromosome 6 before DNA callers run. RNA-seq inputs are GRCh37 Geuvadis alignments. |  |
| M462.1 | 462 | Each sample's input checksums, container digests, workflow files and results are recorded (Supplementary S10). | OK | OK — unchanged |  |
| M463.1 | 463 | Normalization checks allele syntax and reduces identifiers to two numeric fields; the collector also records whether each allele is a current IPD-IMGT/HLA 3.65.0 designation, a group designation, or deleted or renamed, but no call is rewritten to another name, so the results are syntax-normalized, not database-harmonized. | LEN | Normalization checks allele syntax and reduces identifiers to two numeric fields. The collector records whether an allele is a current IPD-IMGT/HLA 3.65.0 designation, a group designation, or deleted or renamed. It never renames calls: results are syntax-normalized, not database-harmonized. |  |
| M464.1 | 464 | The callers' native search databases differ in vintage (Table 1; Supplementary S6), so algorithm, database and deployment effects still cannot be separated; for the historical stored outputs even the read route was not recorded. | LEN | Native search databases differ in vintage (Table 1; Supplementary S6), so algorithm, database and deployment effects remain inseparable. Even the read route was unrecorded for historical stored outputs. |  |

### Main — Allele normalization and call states

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| M466.H | 466 | ### Allele normalization and call states | OK | OK — unchanged |  |
| M468.1 | 468 | Every output row was assigned an explicit call state before any vote was counted, because callers report incomplete or uncertain results in different ways. | PASS, REP | We assigned every output row a call state before counting votes because callers report incomplete or uncertain results differently. |  |
| M469.1 | 469 | Alleles required a valid HLA gene and at least two numeric fields; gene mismatches, malformed alleles and unresolved slash-delimited ambiguities were rejected, and higher fields and suffix tokens were retained as metadata. | PASS, LEN | Alleles required a valid HLA gene and at least two numeric fields. We rejected gene mismatches, malformed alleles and unresolved slash-delimited ambiguities, retaining higher fields and suffix tokens as metadata. |  |
| M470.1 | 470 | N, L, S and Q expression suffixes and P/G group terminology follow HLA nomenclature [41]; C and A were retained as opaque suffix metadata rather than interpreted by this analysis. | OK | OK — unchanged |  |
| M471.1 | 471 | The primary endpoint used the first two numeric fields, and diploid pairs were sorted before comparison. | OK | OK — unchanged |  |
| M473.1 | 473 | Each requested caller cell has exactly one state: complete, partial, missing, ambiguous, invalid, failed or absent. | OK | OK — unchanged |  |
| M474.1 | 474 | *Absent* means that the collected caller table has no row for that sample, gene and caller, which is distinct from an executed caller returning a missing or failed result; placeholders such as empty strings, `-`, `.`, `NA` and `NOTTYPED` are recognized centrally. | LEN | *Absent* means the collected table has no row for that sample, gene and caller, distinct from an executed caller returning a missing or failed result. Empty strings, `-`, `.`, `NA` and `NOTTYPED` are recognized centrally as placeholders. |  |
| M475.1 | 475 | A caller is *callable* at a locus when its row is complete, that is, when it reports an unordered two-field genotype; missing, partial and invalid rows do not vote. | LEN, REP | A caller is *callable* at a locus when its row is complete and reports an unordered two-field genotype. Missing, partial and invalid rows do not vote. |  |
| M477.1 | 477 | A row with one resolved allele and no second, a *singleton call*, is partial and abstains unless the caller's own output format declares homozygosity. | OK | OK — unchanged |  |
| M478.1 | 478 | Two panel callers do so: HLA-HD writes a hyphen in place of the second allele for a homozygous call and "Not typed" for a failed one [42], and arcasHLA releases before 0.4.0 report a homozygous genotype as a single allele [43]. | LEN, CLAR | HLA-HD writes a hyphen for the second allele of a homozygous call and "Not typed" for a failed call [42]. arcasHLA releases before 0.4.0 report homozygotes as a single allele [43]. |  |
| M479.1 | 479 | These rows are completed into homozygous pairs. | OK | OK — unchanged |  |
| M480.1 | 480 | The historical arcasHLA executable was not preserved, so for the stored outputs this convention rested on their output representation; the v3.5.0 rerun container holds arcasHLA 0.2.0, a release that reports homozygotes this way. | LEN | The historical arcasHLA executable was not preserved, so the stored-output convention rested on its representation. The v3.5.0 rerun container holds arcasHLA 0.2.0, which reports homozygotes this way. |  |
| M481.1 | 481 | The rerun T1K parser records the `num_diff_alleles` and quality fields that distinguish a native homozygote from a missing allele, so T1K's declared homozygotes are completed too and its other single-allele rows abstain. | LEN, PASS | The rerun T1K parser records `num_diff_alleles` and quality fields distinguishing native homozygotes from missing alleles. We complete T1K's declared homozygotes; other single-allele rows abstain. |  |
| M482.1 | 482 | At exact-endpoint loci, 27 of 30 single-allele rows in WES and 30 of 34 in RNA-seq lay at a homozygous reference genotype; the exceptions were three T1K WES rows (one declaration, two partial) and four arcasHLA RNA-seq declarations. | LEN | At exact-endpoint loci, 27 of 30 single-allele WES rows and 30 of 34 RNA-seq rows lay at homozygous reference genotypes. Exceptions were three T1K WES rows (one declaration, two partial) and four arcasHLA RNA-seq declarations. |  |
| M483.1 | 483 | This handling was finalized after the development results had been inspected, so scoring in which every singleton abstains is reported alongside (Supplementary S2). | PASS, REP | We finalized this handling after inspecting development results and report abstain-all singleton scoring alongside it (Supplementary S2). |  |

### Main — Primary and secondary consensus rules

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| M487.H | 487 | ### Primary and secondary consensus rules | OK | OK — unchanged |  |
| M489.1 | 489 | At each locus, every callable intended-use caller casts one vote for its unordered two-field genotype, and ChampHLA-Consensus reports the genotype with the most votes (Figure 1B). | OK | OK — unchanged |  |
| M490.1 | 490 | The rule is a plurality, not a majority: the selected genotype need not receive more than half of the votes. | OK | OK — unchanged |  |
| M491.1 | 491 | Equal maxima are resolved by choosing the pair that sorts first when its two allele names, each pair sorted, are compared as character strings (so A\*02:101 precedes A\*02:11), and tied loci are flagged. | LEN, PASS, REP | Ties go to the first-sorting pair when sorted allele names are compared as character strings (A\*02:101 precedes A\*02:11). We flag tied loci. |  |
| M492.1 | 492 | If no caller is callable, the method abstains. | OK | OK — unchanged |  |
| M493.1 | 493 | The rule uses no truth labels, allele frequencies or fitted weights. | OK | OK — unchanged |  |
| M495.1 | 495 | Two descriptive rules use the same votes: strict majority reports the leading pair only when it has more than half of the callable votes, and two-thirds consensus requires at least two thirds. | LEN | Two descriptive rules use the same votes. Strict majority requires more than half of callable votes for the leading pair; two-thirds consensus requires at least two thirds. |  |
| M496.1 | 496 | Each caller was also evaluated on its own. | OK | OK — unchanged |  |
| M497.1 | 497 | Six fitted policies were exploratory: the best single caller chosen by nested cross-validation (CV), four champion–challenger variants and an L2-regularized logistic meta-consensus (Supplementary S7.1). | OK | OK — unchanged |  |
| M498.1 | 498 | Their development scores cannot establish generalization, because construction or selection and evaluation share the development resource. | OK | OK — unchanged |  |

### Main — Endpoints and statistical analysis

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| M500.H | 500 | ### Endpoints and statistical analysis | OK | OK — unchanged |  |
| M502.1 | 502 | The primary endpoint was exact unordered diploid concordance at two-field resolution: a locus counted as concordant only when both predicted alleles matched both reference alleles to the first two fields, in either order, with no credit for matching one allele. | LEN | The primary endpoint was exact unordered diploid concordance at two-field resolution. Both predicted alleles had to match both reference alleles to the first two fields, in either order; matching one allele earned no credit. |  |
| M503.1 | 503 | The denominator is fixed, so an absent or non-callable prediction counts as incorrect and a method cannot improve its score by declining difficult loci. | OK | OK — unchanged |  |
| M504.1 | 504 | Callability was reported separately, and called-only concordance, computed over loci with a complete diploid prediction, is always reported with it. | PASS, REP | We reported callability separately and always alongside called-only concordance, computed over loci with a complete diploid prediction. |  |
| M505.1 | 505 | Allele concordance counted the multiset intersection between predicted and reference alleles over twice the genotype denominator. | OK | OK — unchanged |  |
| M507.1 | 507 | Concordance, allele concordance, callability and called-only concordance are described by subject-cluster percentile bootstrap intervals from 100,000 subject resamples, with base seed 20260831 and a deterministic SHA-256-derived seed for each method. | PASS, GRAM, REP | We described concordance, allele concordance, callability and called-only concordance with subject-cluster percentile bootstrap intervals from 100,000 subject resamples, base seed 20260831 and a deterministic SHA-256-derived seed per method. |  |
| M508.1 | 508 | Each resample keeps every evaluable locus and both alleles of each sampled subject, so the estimand remains locus-weighted. | GRAM, REP | Each resample retained every evaluable locus and both alleles of each sampled subject, keeping the estimand locus-weighted. |  |
| M509.1 | 509 | Estimates of 0% or 100%, where a percentile bootstrap collapses to a point, use the exact Clopper–Pearson interval [44]. | OK | OK — unchanged |  |
| M510.1 | 510 | Stratified results use exact Clopper–Pearson intervals, and the exploratory Institute for Molecular Medicine Finland (FIMM) and VenEx results use Wilson intervals [32], as stated with each table. | OK | OK — unchanged |  |
| M512.1 | 512 | For each comparator, the paired effect is ChampHLA-Consensus minus the comparator, in percentage points. | OK | OK — unchanged |  |
| M513.1 | 513 | Significance was decided by an exact two-sided subject sign-flip test of the locus-weighted difference, enumerating all sign assignments when at most 20 subjects had nonzero aggregates and otherwise using 1,000,000 seeded assignments with a plus-one correction. | PASS, LEN | We determined significance with an exact two-sided subject sign-flip test of the locus-weighted difference. We enumerated all sign assignments for at most 20 subjects with nonzero aggregates, otherwise using 1,000,000 seeded assignments and a plus-one correction. |  |
| M514.1 | 514 | Holm correction [45] was applied separately within each assay's descriptive-comparator family and its exploratory fitted-policy family; comparisons with zero discordance were displayed but excluded from multiplicity. | PASS, LEN | We applied Holm correction [45] separately within each assay's descriptive-comparator and exploratory fitted-policy families. Zero-discordance comparisons were displayed but excluded from multiplicity. |  |
| M515.1 | 515 | A comparison is called significant when its sign-flip Holm-adjusted *p*<0.05. | OK | OK — unchanged |  |
| M516.1 | 516 | Because the test is discrete, a comparison in which few subjects differ cannot reach *p*<0.05 at any effect size (Supplementary S3). | OK | OK — unchanged |  |
| M518.1 | 518 | Intervals for the paired differences are descriptive. | OK | OK — unchanged |  |
| M519.1 | 519 | They use a CR1 (finite-cluster-corrected cluster-robust) subject-clustered standard error, a Student *t* reference distribution with `G−1` degrees of freedom and Bonferroni adjustment over the same family. | OK | OK — unchanged |  |
| M520.1 | 520 | Cluster-robust inference is unreliable with few clusters [46], and only discordant subjects contribute to a paired contrast, so these intervals may be too narrow when few subjects differ. | LEN | Cluster-robust inference is unreliable with few clusters [46]. Only discordant subjects contribute to a paired contrast, so intervals may be too narrow when few subjects differ. |  |
| M521.1 | 521 | A post hoc two-percentage-point non-inferiority calculation is an exploratory sensitivity analysis and is not used to claim equivalence. | OK | OK — unchanged |  |
| M522.1 | 522 | Results stratified by vote support are descriptive proportions, not probability calibration, and no external validation test was performed. | OK | OK — unchanged |  |

### Main — Protocol history

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| M524.H | 524 | ### Protocol history | OK | OK — unchanged |  |
| M526.1 | 526 | The analysis plan changed after development results had been seen. | OK | OK — unchanged |  |
| M527.1 | 527 | Each change is recorded in a dated decision file in the paper repository, and Supplementary S7 tabulates the direction and size of every change. | OK | OK — unchanged |  |
| M529.1 | 529 | A protocol frozen on 31 August 2026, before the confirmation protocol's truth-join step, named a two-thirds-guarded champion–challenger rule as the primary method, corrected for multiplicity across WGS, WES and RNA-seq together, and required the primary method to outperform its comparators. | OK | OK — unchanged |  |
| M530.1 | 530 | This was not the analysts' first sight of truth: an earlier analysis had already joined truth to these caller outputs to fit the champions and weights. | OK | OK — unchanged |  |
| M531.1 | 531 | On the current endpoint the frozen primary did not outperform: it scored 141/153 against the vote's 143/153 in WES (Holm *p*=1.0) and tied the vote at 113/118 in RNA-seq. | OK | OK — unchanged |  |
| M533.1 | 533 | The equal-weight plurality vote was then made primary, with multiplicity corrected within each assay and invalid WGS excluded (8 September; signed 18 September). | OK | OK — unchanged |  |
| M534.1 | 534 | Single-allele handling was revised three times, ending with caller-declared homozygotes completed (18 September to 8 October). | OK | OK — unchanged |  |
| M535.1 | 535 | After a structured review, the reference parser was made fail-closed and predictions were frozen before any truth was selected (28 September). | OK | OK — unchanged |  |
| M536.1 | 536 | Finally, the RNA-seq input that failed the identity check was withheld, the nested-CV comparator was refitted, and the exact sign-flip test replaced the cluster-*t* test as the test that decides significance (8–9 October); the set of significant comparisons did not change. | LEN, PASS | We then withheld the RNA-seq input that failed identity checks, refitted the nested-CV comparator and made the exact sign-flip test govern significance instead of the cluster-*t* test (8–9 October). The significant comparisons did not change. |  |
| M537.1 | 537 | The evidence then moved to a full rerun (13–25 October): a corrected T1K parser was released as workflow release 3.5.0, every development caller was re-run with it, the collector was corrected to complete caller-declared homozygotes before activation, and the author approved the resulting registry before any prose was revised. | LEN | The full rerun followed (13–25 October). A corrected T1K parser was released in workflow release 3.5.0, and every development caller was re-run with it. The collector was corrected to complete caller-declared homozygotes before activation; the author approved the resulting registry before prose revision. |  |
| M538.1 | 538 | The arcasHLA deployment defect found afterwards was reported as it stands rather than corrected. | OK | OK — unchanged |  |
| M539.1 | 539 | These safeguards make the history auditable, but they cannot undo prior exposure to development truth, so none of the development results is confirmatory. | LEN, REP | These safeguards document the history but cannot undo prior exposure to development truth. None of the development results is confirmatory. |  |
| M540.1 | 540 | A subject-disjoint extension roster was frozen with its analysis protocol before any truth join; an amendment pinning release 3.5.0, the analysis code and the input manifest was signed on 26 October, and the roster is being processed, with the one-time truth join deferred until the signed plan is publicly deposited. | OK | OK — unchanged | Pending-study sentence retained verbatim under the task freeze. |
| M541.1 | 541 | The NCI-60 application is being regenerated under a separate decision signed the same day (Supplementary S9.6). | OK | OK — unchanged | Pending-study sentence retained verbatim under the task freeze. |

### Main — Software and audit trail

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| M543.H | 543 | ### Software and audit trail | OK | OK — unchanged |  |
| M545.1 | 545 | The reported results were regenerated in a pinned release environment: Python 3.11.15 with NumPy 1.26.4, SciPy 1.14.1 and Matplotlib 3.9.2 [47–49]; the software environment of the development caller run was not recorded. | PASS, LEN | We regenerated results in a pinned release environment: Python 3.11.15, NumPy 1.26.4, SciPy 1.14.1 and Matplotlib 3.9.2 [47–49]. The historical caller-run software environment was unrecorded. |  |
| M546.1 | 546 | Release 3.5.0 of the workflow, used for the development rerun, runs on the Roihu cluster of CSC – IT Center for Science (CSC) with Nextflow 25.10.2 [22], Apptainer (formerly Singularity) [50], SAMtools 1.21 [51] and BWA 0.7.19 [37]. | OK | OK — unchanged |  |
| M547.1 | 547 | Its caller images are pinned by SHA-256 in `configs/caller_resources_v2.json`, and the workflow stops before any task runs if an image differs from its pin (Supplementary S10). | OK | OK — unchanged |  |
| M548.1 | 548 | Inputs, truth, predictions and outputs carry SHA-256 identities, and prediction generation enforces a *truth firewall* in code: the step that produces caller predictions refuses to run if any input table carries a reference-genotype column. | JARG, LEN, REP | Inputs, truth, predictions and outputs carry SHA-256 identities. A *truth firewall* prevents prediction generation from running if any input table contains a reference-genotype column. |  |
| M549.1 | 549 | Figures read versioned tab-separated value (TSV) artifacts, and analysis decisions are kept as signed records that later decisions supersede without rewriting. | LEN, PASS | Figures read versioned tab-separated value (TSV) artifacts. Later signed analysis decisions supersede earlier records without rewriting them. |  |
| M550.1 | 550 | WGS outputs from the same caller run failed input-validity checks (Limitations); they are quarantined, and no quantitative WGS performance is reported. | OK | OK — unchanged |  |

### Main — Ethics and consent

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| M559.H | 559 | ### Ethics and consent | OK | OK — unchanged |  |

### Main — Data availability

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| M578.H | 578 | ## Data availability | OK | OK — unchanged |  |
| M580.1 | 580 | All input data are public. | CLAR | The primary input data are public. |  |
| M580.2 | 580 | The WES data are the 1000 Genomes Project GRCh38DH exome alignments distributed by the International Genome Sample Resource [52]. | OK | OK — unchanged |  |
| M580.3 | 580 | The RNA-seq data are from the Geuvadis project (ENA study PRJEB3366 [53]; ArrayExpress E-GEUV-1 [54]). | OK | OK — unchanged |  |
| M580.4 | 580 | Every subject–assay input is listed, with its URL and the source checksum where one exists, in `cohorts/official_1000g_assay_manifest.tsv`. | PASS, REP | `cohorts/official_1000g_assay_manifest.tsv` lists each subject–assay input, its URL and the source checksum where available. |  |
| M580.5 | 580 | The reference typing is the 2014 1000 Genomes HLA table [55] (SHA-256 `0455d0302ac12a29ab87091cab5e3e557416f6301e89fb122eef8d49cd5644ec`). | OK | OK — unchanged |  |
| M580.6 | 580 | The per-locus results, including every method's call at every exact-endpoint locus, the reference genotype and their agreement, are released as `artifacts/development_corrected/per_locus_results.tsv` and regenerated from these public inputs by `scripts/run_local_verification.sh`. | PASS, LEN | `artifacts/development_corrected/per_locus_results.tsv` releases every method's call, reference genotype and agreement at each exact-endpoint locus. `scripts/run_local_verification.sh` regenerates these results from public inputs. |  |
| M580.7 | 580 | The truth-free collected calls of the release 3.5.0 rerun, their per-sample provenance and the stored-to-rerun comparison are released in `provenance/development_rerun_v350/truth_free_collection/`. | OK | OK — unchanged |  |
| M580.8 | 580 | The public inputs of the frozen extension are listed in `cohorts/extension_v350_manifest.tsv`, and those of the NCI-60 application in `cohorts/nci60_v350_manifest.tsv`, with the ENA file reports and the published NCI-60 typing in `resources/nci60/`. | OK | OK — unchanged |  |
| M582.1 | 582 | Public human data remain subject to source-project terms. | OK | OK — unchanged |  |
| M582.2 | 582 | FIMM source workbooks, specimen–donor mappings and row-level calls remain in controlled storage and are not part of the public release; only privacy-reviewed aggregate artifacts are included. | OK | OK — unchanged |  |
| M582.3 | 582 | Submission of the FIMM material remains blocked pending the ethics and Finnish Hematology Registry and Clinical Biobank (FHRB) identifier, collection period, demographics, inclusion and exclusion rules, consent or biobank basis, and a checksum-frozen secure source manifest and specimen–donor crosswalk. | OK | OK — unchanged |  |

### Main — Code availability

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| M584.H | 584 | ## Code availability | OK | OK — unchanged |  |
| M586.1 | 586 | The paper repository is intended for archival release on GitHub [56] under the MIT licence. | OK | OK — unchanged |  |
| M586.2 | 586 | Its verified post-normalization boundary contains truth-free normalized outputs, checksum-pinned reference acquisition, deterministic reference selection, analysis code, tests, artifacts, all figure formats, manuscript sources and a release manifest. | JARG | The verified analysis starts from truth-free normalized outputs and covers checksum-pinned reference acquisition, reference selection, code, tests, artifacts, figure formats, manuscript sources and a release manifest. |  |
| M586.3 | 586 | The raw-read-to-caller workflow is maintained separately on GitHub [57]; the repository retains the interim name PanelHLA, and PanelHLA and ChampHLA denote the same software. | OK | OK — unchanged |  |
| M586.4 | 586 | The evaluated caller outputs were produced by release 3.5.0 (tag `v3.5.0`, commit `66d949d`), which is the release to cite; it implements the evaluated rule under `-profile paper`, verifies every caller image against its SHA-256 pin, rescues reads on HLA-allele and alternate contigs (introduced in release 3.4.0) and contains the corrected T1K parser. | LEN | Evaluated outputs came from release 3.5.0 (tag `v3.5.0`, commit `66d949d`), the release to cite. It implements the rule under `-profile paper`, verifies caller images against SHA-256 pins, rescues HLA-allele and alternate-contig reads (introduced in release 3.4.0) and corrects the T1K parser. |  |
| M586.5 | 586 | The historical stored outputs came from a pre-release revision of 7 April 2026 retained in the repository history. | LOGIC | OK — unchanged | AUTHOR DECISION 3: the statement assigns stored outputs to 7 April, while S10 says the whole historical run cannot be assigned to that tree. Preserve pending author provenance review. |
| M586.6 | 586 | Callers retain their own licences, and some distributions restrict commercial use; see `THIRD_PARTY_NOTICES.md`. | OK | OK — unchanged |  |

### Main — Figure legends

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| M727.H | 727 | ## Figure legends | OK | OK — unchanged |  |
| M729.1 | 729 | **Figure 1. | OK | OK — unchanged |  |
| M729.2 | 729 | ChampHLA workflow, consensus rule, study design and cohort flow.** | OK | OK — unchanged |  |
| M730.1 | 730 | (A) The workflow converts and routes FASTQ, BAM or CRAM input to the assay's caller panel (Table 1), parses and normalizes each caller's output to two-field genotypes and applies the consensus step. | REP | (A) The workflow routes FASTQ, BAM or CRAM input to the assay's caller panel (Table 1), parses and normalizes outputs to two-field genotypes, then applies consensus. |  |
| M731.1 | 731 | (B) An illustrative ChampHLA-Consensus vote at one WES locus: each callable caller casts one vote, a caller without a call is not counted, and the most-voted unordered genotype is reported; an exact tie goes to the lexicographically first genotype. | LEN, REP | (B) Example ChampHLA-Consensus vote at a WES locus: each callable caller casts one vote; callers without calls do not vote. The most-voted unordered genotype is reported, with exact ties going to the lexicographically first genotype. |  |
| M732.1 | 732 | The alleles shown are an example, not data. | OK | OK — unchanged |  |
| M733.1 | 733 | (C) Caller processing and normalization are completed and frozen before the independently parsed reference typing is joined, so caller output cannot influence how the reference is resolved. | LEN, NOM | (C) Caller processing and normalization are frozen before joining independently parsed reference typing. Caller output cannot influence reference resolution. |  |
| M734.1 | 734 | (D) Requested assay–gene loci partitioned into resolved, ambiguous, invalid and source-absent reference states. | OK | OK — unchanged |  |
| M735.1 | 735 | Source absence is a state of the reference record, not a caller no-call. | OK | OK — unchanged |  |
| M736.1 | 736 | Counts are generated from the truth-flow artifact. | OK | OK — unchanged |  |
| M738.1 | 738 | **Figure 2. | OK | OK — unchanged |  |
| M738.2 | 738 | Fixed-denominator exact genotype concordance and callability.** | OK | OK — unchanged |  |
| M739.1 | 739 | Exact unordered two-field genotype concordance and callability of each method in WES (A) and RNA-seq (B), over the same fixed denominator. | OK | OK — unchanged |  |
| M740.1 | 740 | Bars are 95% subject-cluster percentile bootstrap intervals, and the adjacent columns give correct/N and callable/N. | OK | OK — unchanged |  |
| M741.1 | 741 | Blue denotes ChampHLA-Consensus, the orange triangle the exploratory fitted nested-CV best-caller policy, and grey circles individual callers. | OK | OK — unchanged |  |
| M742.1 | 742 | Methods follow a fixed role-based order rather than observed performance. | OK | OK — unchanged |  |
| M743.1 | 743 | Both percentage axes are truncated below 100% to show the observed range and never extend above 100%. | OK | OK — unchanged |  |
| M745.1 | 745 | **Figure 3. | OK | OK — unchanged |  |
| M745.2 | 745 | Paired differences from ChampHLA-Consensus.** | OK | OK — unchanged |  |
| M746.1 | 746 | Each point is ChampHLA-Consensus minus one comparator, in percentage points, so positive values favour the vote. | OK | OK — unchanged |  |
| M747.1 | 747 | Bars are descriptive Bonferroni-adjusted cluster-*t* intervals over the same family used for Holm testing. | OK | OK — unchanged |  |
| M748.1 | 748 | Circles denote descriptive comparators and triangles exploratory fitted policies. | OK | OK — unchanged |  |
| M749.1 | 749 | Magenta with an asterisk marks an exact subject sign-flip Holm-adjusted *p*<0.05; grey is nonsignificant. | OK | OK — unchanged |  |
| M750.1 | 750 | Significance follows the governing sign-flip test, not the bars: in RNA-seq the strict-majority and two-thirds consensus bars exclude zero, but their sign-flip Holm-adjusted *p* values are not below 0.05, so they are grey (Supplementary S3). | LEN, REP | OK — unchanged | TEST PINNED: restored v5 verbatim with author approval on 26 October 2026; test unchanged. tests/test_figures_publication_ready.py::test_adjusted_interval_significance_is_coherent_with_holm. Proposed editorial alternative for author review: The sign-flip test governs significance. RNA-seq strict-majority and two-thirds consensus intervals exclude zero, but their sign-flip Holm-adjusted *p* values are not below 0.05; both are grey (Supplementary S3). |
| M751.1 | 751 | The right-hand columns give locus wins/losses and sign-flip Holm-adjusted *p* values. | OK | OK — unchanged |  |
| M752.1 | 752 | Comparisons with zero discordance are displayed at 0 with interval 0 to 0, wins/losses 0/0 and *p*=1. | OK | OK — unchanged |  |
| M753.1 | 753 | Cluster-*t* Holm-adjusted *p* values are in Supplementary S3. | OK | OK — unchanged |  |
| M754.1 | 754 | Non-significance is not equivalence. | OK | OK — unchanged |  |
| M756.1 | 756 | **Figure 4. | OK | OK — unchanged |  |
| M756.2 | 756 | Pairwise caller-error dependence.** | OK | OK — unchanged |  |
| M757.1 | 757 | Error φ between each pair of callers in WES (A) and RNA-seq (B), on one 0–1 colour scale and annotated to two decimals. | OK | OK — unchanged |  |
| M758.1 | 758 | Both triangles use the exact-endpoint loci: above the diagonal φ is computed on the fixed denominator, and below it φ is restricted further to mutually callable loci, removing loci at which either caller made no call. | LEN, NOM | Both triangles use exact-endpoint loci. Above the diagonal, φ uses the fixed denominator; below it, φ uses mutually callable loci, excluding any locus where either caller made no call. |  |
| M759.1 | 759 | Most joint errors lie at loci where a second typing disagrees with the reference, and on the loci where the typings agree the dependence largely disappears (Supplementary S7). | LEN, REP | Most joint errors occur where second typing disagrees with the reference. Where the typings agree, dependence largely disappears (Supplementary S7). |  |
| M760.1 | 760 | The matrices are descriptive and do not identify a causal error mechanism. | OK | OK — unchanged |  |

### Main — Supplementary information

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| M762.H | 762 | ## Supplementary information | OK | OK — unchanged |  |
| M764.1 | 764 | Supplementary methods, results, tables and figures are supplied as a separate document. | OK | OK — unchanged |  |
| M764.2 | 764 | They cover the cohort and reference-source audit, complete method performance, paired comparisons, stratified results, call states and ties, caller-resource provenance, oracle headroom and fitted policies, excluded earlier analyses, aggregate-only exploratory FIMM, VenEx and NCI-60 analyses, the reproducibility contract, workflow execution, disagreement classes, and background and design rationale. | OK | OK — unchanged |  |

### Supplement — Supplementary material

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| S1.H | 1 | # Supplementary material | OK | OK — unchanged |  |
| S3.1 | 3 | Supporting methods and complete development results for *ChampHLA: an audited evaluation of a plurality baseline for short-read classical HLA class I genotyping*. | TERM | Supporting methods and complete development results for *ChampHLA: a fail-closed benchmark of plurality voting across short-read HLA class I callers*. | Use the unchanged main-manuscript title instead of the superseded supplementary title. |
| S5.1 | 5 | All scientific tables below are regenerated from versioned TSV artifacts; values must not be edited in this document. | REP | Scientific tables are regenerated from versioned TSV artifacts; their values must not be edited here. |  |
| S7.1 | 7 | Numerical citations continue the reference numbering of the main manuscript. | OK | OK — unchanged |  |

### Supplement — S1. Cohort and truth-source audit

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| S9.H | 9 | ## S1. Cohort and truth-source audit | OK | OK — unchanged |  |
| S11.1 | 11 | The signed v3.5.0 rerun roster had 390 WES loci from 130 subjects and 318 RNA-seq loci from 106 subjects. | OK | OK — unchanged |  |
| S12.1 | 12 | It excludes the NA07000 RNA-seq input, which in the historical stored outputs was absent from the official assay manifest and failed the cross-assay identity check (Methods; decisions/20261008_identity_check_na07000.json); every rerun input is in the manifest. | CLAR, LEN | The roster excludes NA07000 RNA-seq because the historical input was absent from the official assay manifest and failed cross-assay identity checks (Methods; decisions/20261008_identity_check_na07000.json). Every rerun input is in the manifest. |  |
| S16.1 | 16 | Identity evidence for every rerun subject is in `artifacts/development_characterisation/identity_check.tsv`, and the historical evidence for the withheld input is kept in `provenance/development_rerun_v350/historical_artifacts/`. | PASS, LEN | `artifacts/development_characterisation/identity_check.tsv` contains identity evidence for every rerun subject. `provenance/development_rerun_v350/historical_artifacts/` retains the withheld input's historical evidence. |  |
| S19.1 | 19 | The public truth parser retained a locus only when all reported ambiguity alternatives collapsed to one unordered two-field genotype. | OK | OK — unchanged |  |
| S21.1 | 21 | The fail-closed duplicate-record rule produced an exact endpoint containing 153 WES loci from 63 subjects and 118 RNA-seq loci from 51 subjects; 50 filtered subjects occurred in both assays. | LEN, REP | The fail-closed duplicate-record rule retained 153 WES loci from 63 subjects and 118 RNA-seq loci from 51 subjects. The filtered sets shared 50 subjects. |  |
| S23.1 | 23 | The set-valued secondary endpoint retained 335 WES and 263 RNA-seq loci with at least one parseable candidate genotype. | OK | OK — unchanged |  |
| S26.1 | 26 | Populations use the 1000 Genomes codes: CEU (Utah residents with Northern and Western European ancestry), YRI (Yoruba in Ibadan, Nigeria), CHB (Han Chinese in Beijing), JPT (Japanese in Tokyo), FIN (Finnish), GBR (British), TSI (Toscani in Italy) and PUR (Puerto Rican). | OK | OK — unchanged |  |
| S29.1 | 29 | The 2014 reference table labels the CEU samples "CEPH" and pools CHB and JPT as "CHB+JPT"; tables derived from it keep those labels. | OK | OK — unchanged |  |
| S31.1 | 31 | Candidate-occurrence bounds are internal benchmark counts, not population allele frequencies. | OK | OK — unchanged |  |
| S101.1 | 101 | The public source is `20140702_hla_diversity.txt`, obtained from the IGSR 2014 HLA technical directory. | OK | OK — unchanged |  |
| S103.1 | 103 | Its required SHA-256 is `0455d0302ac12a29ab87091cab5e3e557416f6301e89fb122eef8d49cd5644ec`. | OK | OK — unchanged |  |
| S105.1 | 105 | The selection manifest records all excluded subject-modality-gene keys. | TERM | The selection manifest records each excluded subject–assay–gene key. |  |
| S105.2 | 105 | The large exclusion fraction means the exact results apply only to uniquely resolved truth loci. | CLAR, TERM | Because many loci were excluded, exact results apply only to uniquely resolved reference loci. |  |
| S107.1 | 107 | Retained-versus-excluded comparisons use gene, population, source-truth state and candidate-pair count. | OK | OK — unchanged |  |
| S108.1 | 108 | Candidate occurrence bounds are benchmark-set counts, not population allele frequencies. | TERM, REP | Candidate-occurrence bounds are benchmark counts, not population allele frequencies. |  |
| S110.1 | 110 | Retention was strongly population-dependent: after pooling genes, exact truth was retained for 84.7% of CEU (CEPH) and 92.8% of YRI WES source-present loci, but only 3.9% of FIN, 3.9% of GBR and 8.3% of PUR loci. | OK | OK — unchanged |  |
| S112.1 | 112 | The corresponding RNA-seq rates were 85.5%, 90.2%, 3.9% and 7.4% for CEU, YRI, FIN and GBR [RESULT:DEV_TRUTH_RETENTION_RNASEQ_CEPH]. | OK | OK — unchanged |  |
| S114.1 | 114 | These are properties of the 2014 truth representation, not biological population accuracy estimates. | OK | OK — unchanged |  |
| S204.1 | 204 | Two-field compatibility counts a call when it equals any allowed unordered candidate genotype. | OK | OK — unchanged |  |
| S205.1 | 205 | The P- and G-group sensitivities map each two-field designation to all compatible official IPD-IMGT/HLA 3.65.0 groups of the stated kind and test a bijective set intersection across the two alleles. | LEN | The P- and G-group sensitivities map each two-field designation to all compatible official IPD-IMGT/HLA 3.65.0 groups of that kind. They test a bijective set intersection across the two alleles. |  |
| S207.1 | 207 | They are compatibility analyses under a two-field mapping, not exact P- or G-group calls. | OK | OK — unchanged |  |
| S209.1 | 209 | Two truth loci per assay could not be mapped for either endpoint and remain explicit. | CLAR, TERM | Two reference loci per assay could not be mapped for either endpoint; these exclusions remain explicit. |  |
| S210.1 | 210 | Every method is reported for all three set-valued endpoints. | OK | OK — unchanged |  |
| S212.1 | 212 | Subject-level paired inference for the set-valued two-field endpoint used the same fixed locus denominator as the compatibility estimates. | OK | OK — unchanged |  |
| S213.1 | 213 | Positive differences favour ChampHLA-Consensus. | OK | OK — unchanged |  |
| S214.1 | 214 | Two-sided sign assignments were enumerated exactly through 25 nonzero subjects and otherwise sampled with 1,000,000 plus-one-corrected assignments; Holm adjustment was applied within assay and the predeclared descriptive or fitted comparator family. | PASS, LEN | We enumerated two-sided sign assignments exactly through 25 nonzero subjects, otherwise sampling 1,000,000 plus-one-corrected assignments. We applied Holm adjustment within each assay and predeclared descriptive or fitted comparator family. |  |
| S252.1 | 252 | Because the exact endpoint keeps only uniquely resolved reference typings, the audit also selects which subjects and populations are scored. | JARG, REP | By retaining only uniquely resolved reference typings, the exact endpoint also selects which subjects and populations are scored. |  |
| S253.1 | 253 | The next table scores the same two-field compatibility separately on the retained loci, where it equals exact concordance, and on the excluded loci whose ambiguous typing could still be scored. | REP | The next table reports two-field compatibility separately for retained loci, where it equals exact concordance, and excluded loci with scoreable ambiguous typing. |  |
| S256.1 | 256 | The profile table compares the two strata without truth labels: population composition, how often the panel callers agreed, and how many candidate genotypes an excluded locus allowed. | NOM, REP | The profile table compares population composition, panel-caller agreement and the number of candidate genotypes per excluded locus without using truth labels. |  |
| S258.1 | 258 | Compatibility on excluded loci is lenient, because any allowed candidate counts. | OK | OK — unchanged |  |

### Supplement — S2. Complete method performance

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| S302.H | 302 | ## S2. Complete method performance | OK | OK — unchanged |  |
| S304.1 | 304 | Scope is one of `primary`, `descriptive_comparator`, or `exploratory_fitted`. | OK | OK — unchanged |  |
| S305.1 | 305 | Individual callers are descriptive comparisons. | OK | OK — unchanged |  |
| S305.2 | 305 | Callability and concordance use the same fixed truth denominator. | OK | OK — unchanged |  |
| S306.1 | 306 | Intervals are 95% subject-cluster percentile bootstrap intervals, except that an estimate of 0% or 100% takes the exact Clopper–Pearson interval, where a bootstrap would collapse to a point. | LEN | Intervals are 95% subject-cluster percentile bootstrap intervals. Estimates of 0% or 100% use exact Clopper–Pearson intervals because a bootstrap would collapse to a point. |  |
| S343.1 | 343 | **Singleton sensitivity.** | OK | OK — unchanged |  |
| S343.2 | 343 | The table below repeats the analysis with every single-allele caller output abstaining, including the homozygous declarations of HLA-HD, arcasHLA and (in the v3.5.0 rerun) T1K that the primary scoring completes (decisions/20261008_singleton_native_homozygosity.json). | REP, LEN | The table repeats the analysis with every single-allele output abstaining, including HLA-HD, arcasHLA and v3.5.0 rerun T1K homozygous declarations completed in primary scoring (decisions/20261008_singleton_native_homozygosity.json). |  |
| S346.1 | 346 | It reproduces the scoring rule used before that decision. | OK | OK — unchanged |  |

### Supplement — S3. Paired comparisons

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| S381.H | 381 | ## S3. Paired comparisons | OK | OK — unchanged |  |
| S383.1 | 383 | Every delta is `ChampHLA-Consensus − comparator`. | OK | OK — unchanged |  |
| S383.2 | 383 | Missing or non-callable comparator predictions score incorrect. | OK | OK — unchanged |  |
| S384.1 | 384 | Significance is decided by the exact (or, above 20 nonzero subject aggregates, Monte Carlo) two-sided subject sign-flip test of the locus-weighted difference, with Holm correction; the "Significant" column is its Holm-adjusted *p*<0.05 (decisions/20261009_signflip_governs.json). | LEN | The two-sided subject sign-flip test of the locus-weighted difference governs significance, with Holm correction. It is exact through 20 nonzero subject aggregates and Monte Carlo above that. The "Significant" column marks Holm-adjusted *p*<0.05 (decisions/20261009_signflip_governs.json). |  |
| S388.1 | 388 | The interval columns and the cluster-*t* *p* values are descriptive: they use a CR1 (finite-cluster-corrected cluster-robust) subject-clustered standard error with a Student *t* reference distribution and `G−1` degrees of freedom, which is anti-conservative when few subjects are discordant; Bonferroni-adjusted intervals and cluster-*t* Holm *p* values use the same active family. | LEN | Intervals and cluster-*t* *p* values are descriptive. They use a CR1 (finite-cluster-corrected cluster-robust) subject-clustered standard error, a Student *t* distribution and `G−1` degrees of freedom; this is anti-conservative with few discordant subjects. Bonferroni-adjusted intervals and cluster-*t* Holm *p* values use the same active family. |  |
| S393.1 | 393 | Descriptive comparators and exploratory fitted policies form separate families; zero-discordance rows are displayed but excluded from multiplicity. | OK | OK — unchanged |  |
| S395.1 | 395 | Because the intervals are descriptive, one can exclude zero while the governing sign-flip test is not significant; in the v3.5.0 rerun this happens for the RNA-seq strict-majority and two-thirds consensus comparisons, which are therefore not called significant. | LEN, REP | A descriptive interval can exclude zero while the governing sign-flip test is not significant. In the v3.5.0 rerun, this occurs for RNA-seq strict-majority and two-thirds consensus; neither comparison is called significant. |  |
| S399.1 | 399 | The two-percentage-point non-inferiority analysis is post hoc, not confirmatory. | OK | OK — unchanged |  |
| S400.1 | 400 | The sign-flip seed for each row is a deterministic SHA-256 derivation from base seed 20260831 and is recorded with the assignment count in the source TSV. | OK | OK — unchanged |  |
| S402.1 | 402 | Exact rows enumerate all 2^d assignments for d nonzero subject aggregates; rows with d>20 use 1,000,000 assignments and the plus-one correction. | OK | OK — unchanged |  |
| S404.1 | 404 | Some comparators return identical genotypes and share a multiplicity slot anyway, because the families were fixed before this was checked: in WES the vote-stratum-gated and logistic meta-consensus policies return the plurality genotype at every locus, the three champion–challenger variants return identical genotypes, and the refitted best-caller policy returns POLYSOLVER's genotype at every locus; in RNA-seq the strict-majority and two-thirds rules are identical for a four-caller panel. | LOGIC, LEN | OK — unchanged | AUTHOR DECISION 4: this sentence says the refitted WES policy returns POLYSOLVER, whereas S7 reports OptiType in every WES fold. The adjacent registered method totals also differ. Leave caller attribution unchanged pending author review; no analysis or method selection was rerun. |
| S410.1 | 410 | Removing the duplicates would only lower m and changes no significance verdict here. | OK | OK — unchanged |  |
| S473.1 | 473 | The minimum attainable p is the exact enumeration minimum, attained when every nonzero subject favours one method. | OK | OK — unchanged |  |
| S474.1 | 474 | Rows with more than 20 nonzero subject aggregates were tested with 1,000,000 Monte Carlo assignments, whose attainable floor is about 1.0×10⁻⁶ before multiplicity adjustment. | OK | OK — unchanged |  |
| S478.1 | 478 | The families were fixed on 28 September 2026, after development results had been seen (main Methods, Protocol history), so the table below shows each active comparison's sign-flip verdict under alternative family definitions: the primary families (within each assay, descriptive and fitted separately), one family per assay, and one family pooling both assays. | LEN | The families were fixed on 28 September 2026 after development results had been seen (main Methods, Protocol history). The table compares sign-flip verdicts under the primary families (within assay, descriptive and fitted separately), one family per assay and one family pooling both assays. |  |
| S482.1 | 482 | The same four comparisons are significant under every definition; only the WES two-thirds consensus comparison would be significant, and only without any correction. | CLAR | The same four comparisons are significant under every definition. Only WES two-thirds consensus would additionally be significant without any correction. |  |
| S511.1 | 511 | Detectability refers specifically to the discrete sign-flip test that decides significance; it does not imply that every valid clustered analysis is incapable of detecting a difference. | LEN, REP | Detectability concerns the discrete sign-flip test that governs significance. It does not imply that every valid clustered analysis is incapable of detecting a difference. |  |
| S513.1 | 513 | Non-significance is not interpreted as equivalence. | OK | OK — unchanged |  |

### Supplement — S4. Stratified primary results

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| S515.H | 515 | ## S4. Stratified primary results | OK | OK — unchanged |  |
| S517.1 | 517 | Strata were not used to fit or select the primary method. | PASS | We did not use strata to fit or select the primary method. |  |
| S517.2 | 517 | Population labels are the source population codes, not broad continental superpopulations. | OK | OK — unchanged |  |
| S518.1 | 518 | The rare-allele stratum uses the smaller of the two truth alleles' counts within the filtered assay denominator; this count is not an external population frequency. | OK | OK — unchanged |  |
| S521.1 | 521 | Intervals are exact and unadjusted; all strata are descriptive. | OK | OK — unchanged |  |

### Supplement — S5. Missingness, support and ties

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| S556.H | 556 | ## S5. Missingness, support and ties | OK | OK — unchanged |  |
| S558.1 | 558 | A partial row contains one valid allele and an undetermined second allele. | OK | OK — unchanged |  |
| S558.2 | 558 | Such rows abstain. | OK | OK — unchanged |  |
| S559.1 | 559 | An absent row is missing from the collected caller table. | OK | OK — unchanged |  |
| S561.1 | 561 | The support profiles below and the error-correlation tables in S7 summarise caller disagreement quantitatively; S12.1 gives the truth-free disagreement classes that were computed. | GRAM, REP | The support profiles below and error-correlation tables in S7 summarize caller disagreement; S12.1 reports the truth-free disagreement classes. |  |
| S579.1 | 579 | In the v3.5.0 rerun no panel caller row is absent. | OK | OK — unchanged |  |
| S579.2 | 579 | The historical stored table had lacked HLA-HD, OptiType and T1K rows at the HLA-A, -B and -C loci of NA19130, so its plurality there was an arcasHLA-only 1/1 vote. | LEN, CLAR | The historical table lacked HLA-HD, OptiType and T1K rows at NA19130's HLA-A, -B and -C loci. Its plurality at those loci was an arcasHLA-only 1/1 vote. |  |
| S581.1 | 581 | Historical task reports, traces and raw outputs were not preserved, so the stored artifacts cannot distinguish whether those caller tasks ran and produced no retained output, failed, or were never submitted; the rerun records every task state explicitly (Supplementary Table S10.1), and the mutually available comparison below is therefore identical to the fixed-denominator one. | LEN | Historical task reports, traces and raw outputs were not preserved. Stored artifacts cannot distinguish tasks that ran without retained output, failed or were never submitted. The rerun records task states explicitly (Supplementary Table S10.1), so the mutually available comparison below equals the fixed-denominator comparison. |  |
| S602.1 | 602 | Support is recorded as the unreduced number of callable callers selecting the emitted pair (`k`) and the number of callable panel callers (`n`). | OK | OK — unchanged |  |
| S603.1 | 603 | Distinct profiles such as 1/1 and 4/4 are never pooled, even though both reduce to one. | OK | OK — unchanged |  |
| S605.1 | 605 | These are descriptive concordance strata, not calibrated probabilities. | OK | OK — unchanged |  |
| S620.1 | 620 | There was one tied WES locus and one tied RNA-seq locus. | LOGIC | No locus was tied in either assay, so lexicographic tie-breaking did not affect either result. | Author explicitly approved this correction on 26 October 2026. DEV_TIEBREAK_WES_TIED_LOCI and DEV_TIEBREAK_RNASEQ_TIED_LOCI both register zero, agreeing with main Results and the generated support table. No registered value changed. |
| S620.2 | 620 | Lexicographic tie-breaking selected the truth genotype at both. | LOGIC, REP | Removed; incorporated in the preceding author-approved correction. | Author-approved companion correction: remove the claim that tie-breaking selected truth at both tied loci, because the registered rerun has no tied locus. The preceding replacement states the complete approved correction. |
| S621.1 | 621 | A production implementation should route ties to review or validate a locked biologically informed rule on independent data. | OK | OK — unchanged |  |

### Supplement — S6. Caller-resource provenance

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| S625.H | 625 | ## S6. Caller-resource provenance | OK | OK — unchanged |  |
| S636.1 | 636 | HLA\*LA and HISAT-genotype were not run. | OK | OK — unchanged |  |
| S636.2 | 636 | Historical outputs exist for Kourami on WES, seq2HLA on RNA-seq, arcasHLA on WES and SpecHLA on RNA-seq; these caller–assay combinations fall outside the declared panels (`src/champhla_confirmation/panels.py`), and the Kourami and seq2HLA outputs are incomplete. | LEN | Historical off-panel outputs exist for Kourami on WES, seq2HLA on RNA-seq, arcasHLA on WES and SpecHLA on RNA-seq (`src/champhla_confirmation/panels.py`). Kourami and seq2HLA outputs are incomplete. |  |
| S640.1 | 640 | They are not part of the released normalized table and are excluded from benchmark comparisons. | OK | OK — unchanged |  |
| S641.1 | 641 | seq2HLA was also run in the current single-sample test workflow (S10), under different conditions from the development run. | OK | OK — unchanged |  |
| S642.1 | 642 | No comparative claim about any of these callers is made here. | OK | OK — unchanged |  |
| S645.1 | 645 | The historical stored calls carried IPD-IMGT/HLA 3.59.0 metadata, but their normalization was syntactic two-field reduction and did not verify release membership. | OK | OK — unchanged |  |
| S647.1 | 647 | In WES, the historical exact-concordance ordering—POLYSOLVER, OptiType, HLA-HD, SpecHLA and T1K—also orders the audited bundled database releases from oldest (3.11.0) to newest (3.63.0). | OK | OK — unchanged |  |
| S650.1 | 650 | This descriptive ordering is not evidence that an older database improves accuracy. | OK | OK — unchanged |  |
| S653.1 | 653 | Neither that normalization nor the rerun's maps renamed or deleted alleles: the rerun collector records each allele's IPD-IMGT/HLA 3.65.0 membership status but compares calls on their reported first two fields, so the development results are syntax-normalized rather than database-harmonized. | LEN | Neither normalization maps renamed or deleted alleles. The rerun collector records each allele's IPD-IMGT/HLA 3.65.0 membership and compares its reported first two fields. Results are syntax-normalized rather than database-harmonized. |  |
| S656.1 | 656 | For the historical caller run, which reads each caller received is only partly recorded: at the workflow revision of 7 April 2026, POLYSOLVER and SpecHLA received the whole input alignment, and the FASTQ-based callers received reads from the HLA region only when region extraction was switched on, which that run did not record. | LEN, CLAR | The historical caller run only partly records what reads each caller received. At the workflow revision of 7 April 2026, POLYSOLVER and SpecHLA received whole input alignments. FASTQ-based callers received HLA-region reads only if region extraction was enabled; the run did not record that setting. |  |
| S660.1 | 660 | In the release 3.5.0 rerun, WES reads on HLA-allele and alternate contigs are realigned to primary chromosome 6 before every DNA caller, and each sample records its inputs, container digests and workflow files (S10). | LEN | In the release 3.5.0 rerun, WES reads on HLA-allele and alternate contigs are realigned to primary chromosome 6 before every DNA caller. Each sample records inputs, container digests and workflow files (S10). |  |
| S665.1 | 665 | A bounded membership check used checksum-verified allele lists extracted from the current deployment and only the intended-use assay panels. | PASS, REP | We checked membership using checksum-verified allele lists from the current deployment, restricted to intended-use assay panels. |  |
| S666.1 | 666 | Every exact reference genotype and allele copy was present in every applicable list. | OK | OK — unchanged |  |
| S686.1 | 686 | These current-deployment lists do not reconstruct the April caller-run databases, prove that every listed allele survived caller-specific filtering, or show that sequence evidence could distinguish it. | OK | OK — unchanged |  |
| S688.1 | 688 | Presence is necessary but not sufficient for a caller to emit an allele. | OK | OK — unchanged |  |
| S689.1 | 689 | SpecHLA's heterogeneous components are summarized by the verified 3.38.0 native list used here, not the separate 3.51.0 component. | OK | OK — unchanged |  |
| S691.1 | 691 | No representability-adjusted concordance claim is made. | OK | OK — unchanged |  |
| S692.1 | 692 | All 15 ChampHLA-Consensus errors (10 WES, 5 RNA-seq) were callable discordances, and every truth and predicted allele at them was also a current release-3.65 designation. | LEN, TERM, CLAR | All 15 ChampHLA-Consensus errors (10 WES, 5 RNA-seq) were callable discordances. Every reference and predicted allele at those loci was a current release-3.65 designation. |  |
| S694.1 | 694 | Thus neither the bounded native-list check nor the current-release nomenclature audit attributes a development error to allele absence, but both remain unable to exclude historical search-space differences. | LEN, REP | Neither the native-list check nor the current-release nomenclature audit attributes a development error to allele absence. Neither excludes historical search-space differences. |  |

### Supplement — S7. Oracle headroom and exploratory fitted policies

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| S698.H | 698 | ## S7. Oracle headroom and exploratory fitted policies | OK | OK — unchanged |  |
| S700.1 | 700 | Error φ is the phi coefficient between two callers' per-locus error indicators. | OK | OK — unchanged |  |
| S701.1 | 701 | The 2×2 column gives, in order, the loci both callers got right, those only the second got wrong, those only the first got wrong and those both got wrong. | OK | OK — unchanged |  |
| S702.1 | 702 | On the fixed denominator a locus where both callers made no call counts as a joint error; the mutually callable φ removes such loci. | OK | OK — unchanged |  |
| S704.1 | 704 | Intervals are subject-cluster percentile bootstrap intervals (100,000 resamples). | OK | OK — unchanged |  |
| S728.1 | 728 | The first φ coefficient treats every no-call as an error, matching the fixed denominator. | OK | OK — unchanged |  |
| S729.1 | 729 | The mutually-callable sensitivity excludes loci at which either caller abstained. | OK | OK — unchanged |  |
| S730.1 | 730 | On all exact loci positive dependence is common, but most of it comes from loci where the callers jointly disagree with the 2014 reference: on the loci where the reference and the second typing agree, the dependence largely disappears (reference-agreement tables below). | LEN | Positive dependence is common across exact loci, mostly at loci where callers jointly disagree with the 2014 reference. Where reference and second typing agree, dependence largely disappears (reference-agreement tables below). |  |
| S735.1 | 735 | The oracle marks a locus correct if any intended-use caller produced the truth genotype. | OK | OK — unchanged |  |
| S736.1 | 736 | It is an upper bound for methods that only select among caller outputs, not an implementable method. | OK | OK — unchanged |  |
| S746.1 | 746 | **Second-typing adjudication.** | OK | OK — unchanged |  |
| S746.2 | 746 | The second typing is the in silico retyping of the same exomes by Abi-Rached *et al.* [31], pinned by SHA-256 (decisions/20261009_reference_adjudication.json). | OK | OK — unchanged |  |
| S748.1 | 748 | The signed rule treats any value that is not two or more colon-separated numeric fields as unavailable. | OK | OK — unchanged |  |
| S750.1 | 750 | Some values carry a trailing asterisk. | OK | OK — unchanged |  |
| S750.2 | 750 | The README distributed with the file does not explain it, but the source article does: an asterisk marks a typing that disagreed with the previously published type and that the authors kept after verification (legend and footnote of their S1 Table; their S3 Fig lists each case with the published type it replaced and how it was confirmed) [31]. | OK | OK — unchanged |  |
| S755.1 | 755 | Under the signed rule an asterisked value is unavailable, so the second typing is available only where the source did not retain a disagreement with the earlier published type, and its agreement with the reference wherever it is available follows from the rule. | LEN | Under the signed rule, asterisked values are unavailable. The second typing is therefore available only where its source retained no disagreement with the earlier published type. Agreement with the reference at available loci follows from that rule. |  |
| S758.1 | 758 | The column giving the corrected value strips the asterisk; it was added after the signed results had been seen (decisions/20261009_reference_adjudication_posthoc.json), and the asterisk's documented meaning is recorded in decisions/20261012_second_typing_asterisk_documented.json. | LEN, PASS | The corrected-value column strips the asterisk. We added it after seeing the signed results (decisions/20261009_reference_adjudication_posthoc.json); decisions/20261012_second_typing_asterisk_documented.json records the asterisk's documented meaning. |  |
| S762.1 | 762 | The G column is the lenient compatibility result obtained by mapping each two-field allele to every compatible official IPD-IMGT/HLA 3.65.0 G group; it is not exact G-group equivalence. | OK | OK — unchanged |  |
| S765.1 | 765 | The P column applies the corresponding official P-group mapping. | OK | OK — unchanged |  |
| S766.1 | 766 | Both require a bijective pairing of the two alleles. | OK | OK — unchanged |  |
| S788.1 | 788 | The sensitivity analysis rescores every method on the loci where both typings agree. | OK | OK — unchanged |  |
| S789.1 | 789 | It is chosen by agreement between the typings, never by agreement with any method. | OK | OK — unchanged |  |
| S824.1 | 824 | The next table repeats the caller-error φ of the correlation table on the same subset. | REP | The next table repeats caller-error φ on the same subset. |  |
| S825.1 | 825 | In WES it ranged from −0.08 to 0.31 over the ten caller pairs (median 0.02), against 0.28 to 0.59 on all exact loci. | OK | OK — unchanged |  |
| S826.1 | 826 | OptiType and POLYSOLVER, the most correlated WES pair on all loci (φ=0.59, eight loci where both were wrong), had no locus where both were wrong on this subset. | LEN | OptiType and POLYSOLVER were the most correlated WES pair across all loci (φ=0.59, eight joint-error loci). The pair had no joint error on this subset. | “Neither had a joint error” refers to the pair, not the absence of each caller’s individual errors; retained pair-level endpoint. |
| S828.1 | 828 | In RNA-seq φ ranged from −0.09 to 0.01 (median 0.00), against 0.11 to 0.82 on all exact loci: HLA-HD and OptiType, the most correlated pair on all loci (φ=0.82), had no locus where both were wrong on this subset, nor had arcasHLA and HLA-HD; the only pair wrong together on the subset was arcasHLA and T1K. | LEN | In RNA-seq, φ ranged from −0.09 to 0.01 (median 0.00), against 0.11 to 0.82 across all exact loci. HLA-HD and OptiType were the most correlated pair overall (φ=0.82) but shared no error on this subset, nor did arcasHLA and HLA-HD. Only arcasHLA and T1K were wrong together on the subset. |  |
| S832.1 | 832 | These values rest on few errors (two for OptiType in WES; none for HLA-HD and one for OptiType in RNA-seq) and carry no intervals. | OK | OK — unchanged |  |
| S834.1 | 834 | The subset is also conditioned on a further exome-based caller agreeing with the reference, which by itself removes loci where exome callers jointly disagree with it; it shows what the all-loci φ measures and is not an estimate of independence. | LEN, REP | The subset also requires a further exome-based caller to agree with the reference, removing loci where exome callers jointly disagree. It explains the all-loci φ and does not estimate independence. |  |
| S873.1 | 873 | The last table of this group counts, on the same subset, each caller's errors and how many of them the vote corrects. | REP | The last table counts each caller's errors on this subset and those the vote corrects. |  |
| S874.1 | 874 | In WES the vote was correct at all 12 of HLA-HD's errors, all 12 of SpecHLA's and all 19 of T1K's, and it made no error on the subset in either assay. | OK | OK — unchanged |  |
| S876.1 | 876 | Where the reference is corroborated, then, the vote removes the individual-caller errors, and it nearly equals the strongest caller because that caller makes almost none (OptiType, two errors in 143 WES loci; HLA-HD, none in 112 RNA-seq loci), not because errors are shared. | LEN, REP | Where the typings agree, the vote removes individual-caller errors and nearly equals the strongest caller, which makes almost none (OptiType, two errors in 143 WES loci; HLA-HD, none in 112 RNA-seq loci). Shared errors do not explain this pattern. |  |
| S902.1 | 902 | Previously fitted policies are retained for transparency and labelled `exploratory_fitted` because development labels or performance informed their construction. | PASS | We retain previously fitted policies for transparency, labelled `exploratory_fitted` because development labels or performance informed their construction. |  |
| S904.1 | 904 | Their results were not used to reselect the primary rule: | OK | OK — unchanged |  |
| S907.1 | 907 | - Best single caller (nested CV) uses the ten subject-level outer folds recovered with the earlier predictions. | OK | OK — unchanged |  |
| S908.1 | 908 | For each assay and fold it selects the panel caller with the most exact correct calls on the other nine folds' truth-retained loci (ties to the alphabetically first caller) and applies that caller's calls to the held-out fold, so a subject's own truth never informs its prediction. | LEN | For each assay and fold, it selects the panel caller with the most exact correct calls on truth-retained loci in the other nine folds, breaking ties alphabetically. It applies that caller to the held-out fold, so a subject's truth never informs its own prediction. |  |
| S912.1 | 912 | It was refitted under the current truth and call-state rules (decisions/20261009_nestedcv_refit.json) and is frozen as a separate fitted stage after the truth-free predictions. | OK | OK — unchanged |  |
| S915.1 | 915 | - Champion–challenger uses a gene/assay champion and permits a reliability-weighted challenger only when its support and supporting-caller gates pass (full definition in S7.1; Supplementary Figure S5). | OK | OK — unchanged |  |
| S918.1 | 918 | - Two-thirds-guarded champion–challenger preserves a two-thirds vote when one exists, otherwise uses champion–challenger and then plurality as fallback. | OK | OK — unchanged |  |
| S920.1 | 920 | - Vote-stratum-gated champion–challenger permits overrides only in vote strata supported during development; otherwise it returns plurality. | OK | OK — unchanged |  |
| S922.1 | 922 | - Logistic meta-consensus is an L2-regularized candidate scorer using vote, caller, assay, gene and confidence features. | OK | OK — unchanged |  |
| S924.1 | 924 | - Algorithm-family-gated champion–challenger requires support from at least two caller families before an override. | OK | OK — unchanged |  |
| S925.1 | 925 | Its families are those fixed in decisions/20260918_family_gate_measurement.json: alignment (OptiType, HLA-HD, POLYSOLVER), assembly or graph (Kourami, SpecHLA, T1K) and k-mer (arcasHLA, seq2HLA). | OK | OK — unchanged |  |
| S928.1 | 928 | This grouping is the gate's own and differs from the per-caller descriptions of inference in S6. | OK | OK — unchanged |  |
| S931.1 | 931 | The refitted best single caller chose OptiType in every WES fold and HLA-HD or OptiType in every RNA-seq fold. | OK | OK — unchanged |  |
| S932.1 | 932 | It scored 142/153 on WES and 111/118 on RNA-seq, compared with 143/153 and 113/118 for ChampHLA-Consensus. | OK | OK — unchanged |  |
| S933.1 | 933 | Neither difference was significant (WES `+0.65` points, exact sign-flip Holm *p*=1.0; RNA-seq `+1.69` points, exact sign-flip Holm *p*=0.5, descriptive cluster-*t* Holm *p*=0.155). | OK | OK — unchanged |  |
| S936.1 | 936 | The frozen predictions it replaced, fitted in the earlier analysis under superseded labels and call states, had scored 140/153 and 99/118 and appeared significantly worse than the vote in RNA-seq; that difference reflected the scoring change rather than the policy. | LEN | The replaced frozen predictions were fitted under superseded labels and call states. They scored 140/153 and 99/118 and appeared significantly worse than the vote in RNA-seq; the scoring change, rather than the policy, explained that difference. |  |
| S939.1 | 939 | The policy's fitted status precludes a superiority claim in either direction. | OK | OK — unchanged |  |
| S948.1 | 948 | The power projection resamples development subjects with replacement to each cohort size and applies the Holm step-down procedure in each replicate, within each comparison's family and over the comparisons that differ from the vote, as in the observed analysis. | LEN | The power projection resamples development subjects with replacement to each cohort size. It applies Holm step-down within each comparison's family to comparisons differing from the vote, as in the observed analysis. |  |
| S951.1 | 951 | It treats the observed subject-level differences as the true ones, so it shows what a larger cohort would detect if the development differences were real; where few subjects were discordant those differences are themselves imprecise. | CLAR, LEN | The projection assumes observed subject-level differences are true. It shows what a larger cohort would detect under that assumption; with few discordant subjects, the differences are themselves imprecise. |  |
| S954.1 | 954 | It uses a normal approximation to the subject sign-flip statistic inside simulation, whereas observed tests are exact. | OK | OK — unchanged |  |
| S955.1 | 955 | Entries are the proportion of replicates in which the comparison was significant; it is a conditional sensitivity analysis, not a sample-size guarantee. | CLAR, GRAM | Entries are the proportion of replicates with a significant comparison. This is a conditional sensitivity analysis, not a sample-size guarantee. |  |

### Supplement — Protocol-change ledger

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| S989.H | 989 | ### Protocol-change ledger | OK | OK — unchanged |  |
| S991.1 | 991 | This ledger consolidates every material development-analysis change and states its observed direction, size and consequence. | REP | This ledger records each material development-analysis change, its observed direction and size, and its consequence. |  |
| S992.1 | 992 | “Before truth join” in the 31 August protocol refers only to the later confirmation-protocol join; the analysts had already seen truth joined to these caller outputs in the earlier analysis that fitted champions and weights. | OK | OK — unchanged |  |
| S995.1 | 995 | The frozen primary did not outperform the vote on the current endpoint. | OK | OK — unchanged |  |

### Supplement — S7.1 Rule definitions

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| S1014.H | 1014 | ### S7.1 Rule definitions | OK | OK — unchanged |  |
| S1016.1 | 1016 | Both rules act on one subject, assay and gene at a time, over the assay's intended-use panel (main Table 1). | OK | OK — unchanged |  |
| S1017.1 | 1017 | A caller is callable at a locus when it reports a complete unordered two-field genotype or a caller-native homozygous declaration that is completed under the Methods rule. | OK | OK — unchanged |  |
| S1019.1 | 1019 | A generic single reported allele remains partial and is not completed into a homozygous genotype. | OK | OK — unchanged |  |
| S1022.1 | 1022 | **ChampHLA-Consensus (equal-weight plurality, primary).** | OK | OK — unchanged |  |
| S1033.1 | 1033 | **Champion–challenger (exploratory fitted comparator; Supplementary Figure S8).** | OK | OK — unchanged |  |
| S1034.1 | 1034 | Each caller receives a weight for each assay and gene, fitted in the earlier analysis on the superseded 390-locus WES and 321-locus RNA-seq sets (and on WGS rows), not on the current exact-endpoint loci: w = 0.7 r + 0.3 e, where r is the caller's exact concordance for that gene and assay. | LEN | Each caller receives an assay- and gene-specific weight fitted in the earlier analysis on superseded 390-locus WES and 321-locus RNA-seq sets (and WGS rows). These are not the current exact-endpoint loci. The weight is w = 0.7 r + 0.3 e, where r is exact concordance for that gene and assay. |  |
| S1037.1 | 1037 | The calibrated term e equals r unless the caller reports confidence values for at least half of its callable loci and both its Brier score and expected calibration error are at most 0.35, in which case e = r + (1 − max(Brier, ECE))(p̄ − r), with p̄ the caller's mean calibrated probability. | OK | OK — unchanged |  |
| S1041.1 | 1041 | Champions and gates were frozen per assay: for WES the champion is OptiType for HLA-A, -B and -C, and a challenger needs a support fraction of at least 0.35 and one supporting caller; for RNA-seq the champion is OptiType for HLA-A and arcasHLA for HLA-B and HLA-C, with the same support gate and two supporting callers. | OK | OK — unchanged |  |
| S1045.1 | 1045 | The frozen policy also declares a margin gate (0 for WES and RNA-seq), but as implemented the margin compares the challenger with itself, so it is always zero and never blocks an override. | LEN | The frozen policy declares a margin gate (0 for WES and RNA-seq). As implemented, it compares the challenger with itself, so the margin is always zero and never blocks an override. |  |
| S1047.1 | 1047 | The rule below is the one that produced the results, including those of the policies built on it. | OK | OK — unchanged |  |
| S1068.1 | 1068 | Because the champions, weights and gates were chosen with development labels, champion–challenger results on the same subjects are optimistic and are reported only as exploratory comparisons. | OK | OK — unchanged |  |
| S1072.1 | 1072 | The logistic meta-consensus refit is seeded, but it is not guaranteed to be bit-for-bit reproducible across processes. | OK | OK — unchanged |  |
| S1073.1 | 1073 | In one verification run a single prediction, at a WES locus outside the exact endpoint where two candidate pairs are nearly tied, differed from the approved run; no reported result changed, and the next run reproduced the approved registry exactly (`decisions/20261026_metaconsensus_floating_point_drift.json`). | LEN | In one verification run, a prediction at a WES locus outside the exact endpoint differed from the approved run because two candidate pairs were nearly tied. No reported result changed; the next run reproduced the approved registry exactly (`decisions/20261026_metaconsensus_floating_point_drift.json`). |  |
| S1077.1 | 1077 | The fitted comparators should therefore be read as approximate as well as exploratory. | OK | OK — unchanged |  |

### Supplement — S8. Earlier analyses excluded from evidence

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| S1080.H | 1080 | ## S8. Earlier analyses excluded from evidence | OK | OK — unchanged |  |
| S1082.1 | 1082 | Earlier files reported different WES and RNA-seq headline values under an invalid truth collapse and generic singleton completion. | JARG | Earlier files reported different WES and RNA-seq headline values after invalid reference-ambiguity collapse and generic singleton completion. |  |
| S1083.1 | 1083 | Those numbers remain only in superseded decision records and quarantined artifacts; they are not active results. | OK | OK — unchanged |  |
| S1085.1 | 1085 | A signed superseding decision adopts caller-native homozygous completion, generic-singleton abstention and the audited public-truth denominator. | OK | OK — unchanged |  |
| S1088.1 | 1088 | WGS inputs to the caller run failed validity review because extraction did not preserve all HLA-relevant alternate-contig and mate evidence. | OK | OK — unchanged |  |
| S1089.1 | 1089 | No WGS concordance, ranking, accuracy or denominator is reproduced in this submission. | OK | OK — unchanged |  |
| S1090.1 | 1090 | The WGS material is provenance only. | OK | OK — unchanged |  |
| S1093.1 | 1093 | An earlier draft of this work, prepared under the same project name, also combined several distinct study aims. | OK | OK — unchanged |  |
| S1094.1 | 1094 | Their disposition in the present analysis is recorded below so that earlier material cannot be mistaken for current evidence. | NOM, REP | The table records how each earlier component is treated, so it cannot be mistaken for current evidence. |  |

### Supplement — S9. Aggregate-only exploratory FIMM, VenEx and NCI-60 applications

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| S1108.H | 1108 | ## S9. Aggregate-only exploratory FIMM, VenEx and NCI-60 applications | OK | OK — unchanged |  |

### Supplement — S9.1 Scope, governance and source provenance

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| S1110.H | 1110 | ### S9.1 Scope, governance and source provenance | OK | OK — unchanged |  |
| S1112.1 | 1112 | These post hoc applications are retained only to show that agreement and within-panel dissent do not establish accuracy. | OK | OK — unchanged |  |
| S1113.1 | 1113 | They are ineligible for accuracy, external-validation, clinical-utility or abstract claims. | OK | OK — unchanged |  |
| S1115.1 | 1115 | `FIMM_AML_MDS` and `VENEX_WES` are separate exploratory datasets. | OK | OK — unchanged |  |
| S1115.2 | 1115 | The FIMM three-caller deviation applies only to this cohort and to non-accuracy reporting; it does not change the frozen 1000 Genomes panels. | OK | OK — unchanged |  |
| S1117.1 | 1117 | The source workbooks, row-level calls and specimen–donor mappings remain in controlled storage. | OK | OK — unchanged |  |
| S1119.1 | 1119 | Public release is limited to privacy-reviewed aggregate artifacts, their SHA-256 manifest and the figures derived from them. | OK | OK — unchanged |  |
| S1122.1 | 1122 | Submission remains blocked until the following are verified for both cohorts: | OK | OK — unchanged |  |
| S1123.1 | 1123 | - the approving committee names and approval or permit identifiers; | OK | OK — unchanged |  |
| S1124.1 | 1124 | - the consent or biobank basis and the FHRB or other biobank identifier; | OK | OK — unchanged |  |
| S1125.1 | 1125 | - the collection period, demographics, and inclusion and exclusion rules; | OK | OK — unchanged |  |
| S1126.1 | 1126 | - checksum-frozen secure manifests and specimen–donor crosswalks. | OK | OK — unchanged |  |
| S1128.1 | 1128 | This is a submission gate, not permission to expose patient-level files: source workbooks, mappings and row-level calls remain outside public repositories and publication artifacts. | JARG, LEN | Submission requires those fields; it does not permit disclosure of patient-level files. Source workbooks, mappings and row-level calls remain outside public repositories and publication artifacts. |  |
| S1130.1 | 1130 | The gate does not invalidate the reproducible aggregate analysis. | OK | OK — unchanged |  |

### Supplement — S9.2 Withdrawal of the fingerprint-paired analysis and FIMM import rules

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| S1133.H | 1133 | ### S9.2 Withdrawal of the fingerprint-paired analysis and FIMM import rules | OK | OK — unchanged |  |
| S1135.1 | 1135 | The earlier FIMM concordance analysis is withdrawn. | OK | OK — unchanged |  |
| S1135.2 | 1135 | A stripped workbook had no specimen identifier, so specimens were paired by HLA allele fingerprint before HLA concordance was calculated, and the endpoint was circular. | LEN | A stripped workbook lacked specimen identifiers. Specimens were paired by HLA allele fingerprint before calculating HLA concordance, making the endpoint circular. |  |
| S1137.1 | 1137 | Its figures and numbers are not evidence. | OK | OK — unchanged |  |
| S1138.1 | 1138 | The empty WES allele-imbalance screen is also withdrawn; no LOH claim is made. | OK | OK — unchanged |  |
| S1139.1 | 1139 | HLA evolutionary divergence, survival and clinical-utility analyses remain out of scope. | OK | OK — unchanged |  |
| S1142.1 | 1142 | The importer used here requires an explicit specimen identifier. | OK | OK — unchanged |  |
| S1142.2 | 1142 | Repeated rows for one specimen, assay and caller are collapsed only when their genotypes agree; a disagreement becomes a caller no-call. | LEN | Repeated rows for one specimen, assay and caller are collapsed only if their genotypes agree. A disagreement becomes a caller no-call. |  |
| S1144.1 | 1144 | Singleton alleles are partial calls, bare integers are invalid and missing tokens are no-calls. | OK | OK — unchanged |  |
| S1145.1 | 1145 | Of 2,642 source rows, 2,610 were imported, and 7,179 caller-level locus rows (one per specimen, assay, caller and gene) remained after replicate collapse. | LEN | OK — unchanged | TEST PINNED: restored v5 verbatim with author approval on 26 October 2026; test unchanged. tests/test_sr023_consistency.py::test_fimm_locus_row_units_are_explicit. Proposed editorial alternative for author review: Of 2,642 source rows, 2,610 were imported. After replicate collapse, 7,179 caller-level locus rows remained, one per specimen, assay, caller and gene. |
| S1147.1 | 1147 | There were 81 replicate conflicts and 89 numeric-allele artefacts. | OK | OK — unchanged |  |
| S1148.1 | 1148 | The consensus unit used below is coarser: one specimen–assay–gene locus, which combines the caller-level rows of up to three callers. | OK | OK — unchanged |  |
| S1157.1 | 1157 | The cross-modality unit is the specimen. | OK | OK — unchanged |  |
| S1157.2 | 1157 | Two eligibility definitions are coequal: | OK | OK — unchanged |  |
| S1159.1 | 1159 | - `all_callable` requires a complete unordered two-field plurality pair in both assays; | OK | OK — unchanged |  |
| S1161.1 | 1161 | - `contested_both` additionally requires at least two valid callers in each assay. | OK | OK — unchanged |  |
| S1164.1 | 1164 | The denominator difference therefore reflects caller availability rather than selection of different specimens. | OK | OK — unchanged |  |
| S1165.1 | 1165 | Donor collapse is sensitivity-only. | OK | OK — unchanged |  |
| S1165.2 | 1165 | All complete longitudinal calls must agree; otherwise the donor–modality locus is a `longitudinal_conflict` and is excluded. | OK | OK — unchanged |  |
| S1167.1 | 1167 | A collapsed donor call meets `contested_both` only when every contributing callable longitudinal specimen had at least two valid callers. | OK | OK — unchanged |  |
| S1171.1 | 1171 | Specimen–assay–gene loci by the number of valid callers: | OK | OK — unchanged |  |
| S1179.1 | 1179 | The zero cells in the scRNA-seq row are structural absences from the frozen aggregate, not suppressed observations. | OK | OK — unchanged |  |
| S1180.1 | 1180 | Supplementary Figure S6 shows the panel composition next to the specimen-level endpoint. | OK | OK — unchanged |  |

### Supplement — S9.3 FIMM cross-modality results

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| S1183.H | 1183 | ### S9.3 FIMM cross-modality results | OK | OK — unchanged |  |
| S1185.1 | 1185 | Specimen-level Wilson intervals [32] are unadjusted for donor clustering, because several specimens can come from one donor. | OK | OK — unchanged |  |
| S1186.1 | 1186 | The donor-collapsed rows give the donor-level view. | OK | OK — unchanged |  |
| S1189.1 | 1189 | When both assays had at least two valid callers, exact-pair agreement was: | OK | OK — unchanged |  |
| S1190.1 | 1190 | - bulk RNA–WES: 62/70 (88.6%; Wilson 95% CI 79.0–94.1%); | OK | OK — unchanged |  |
| S1191.1 | 1191 | - scRNA-seq–WES: 21/24 (87.5%; 69.0–95.7%); | OK | OK — unchanged |  |
| S1192.1 | 1192 | - bulk RNA–scRNA-seq: 18/21 (85.7%; 65.4–95.0%). | OK | OK — unchanged |  |
| S1194.1 | 1194 | Across all complete callable pairs, the results were 854/958 (89.1%; 87.0–91.0%), 85/93 (91.4%; 83.9–95.6%) and 84/93 (90.3%; 82.6–94.8%) in the same order. | OK | OK — unchanged |  |
| S1196.1 | 1196 | The denominator difference reflects caller availability, not selection of a different biological cohort. | OK | OK — unchanged |  |
| S1220.1 | 1220 | The donor collapse removed 233 WES and 28 bulk-RNA donor–loci with conflicting longitudinal calls, so the donor estimates are not promoted over the specimen analysis. | OK | OK — unchanged |  |
| S1222.1 | 1222 | [RESULT:FIMM_PANEL_WES_LONGITUDINAL_CONFLICTS] All assay pairs use overlapping caller sets. | OK | OK — unchanged |  |
| S1224.1 | 1224 | Removing the shared callers leaves zero overlap for each pair, so the caller-disjoint sensitivity is explicitly non-estimable. | OK | OK — unchanged |  |
| S1226.1 | 1226 | [RESULT:FIMM_PANEL_DISJOINT_BULKRNA_WES_NON_ESTIMABLE] | OK | OK — unchanged |  |
| S1230.1 | 1230 | All-callable pairs are dominated by loci with a single valid caller (2,211 of 3,042 WES locus rows), so the contested-in-both rows are the more informative view. | LOGIC | OK — unchanged | AUTHOR DECISION 5: calling contested-in-both the “more informative view” appears to rank the two eligibility definitions that S9.2 and the registry require to be coequal exploratory views. Leave unchanged pending author judgement; propose describing different caller availability without ranking the views. |
| S1232.1 | 1232 | Within WES, dissent from the panel plurality at contested loci was: | OK | OK — unchanged |  |
| S1233.1 | 1233 | - arcasHLA: 167/486 (34.4%; Wilson 95% CI 30.3–38.7%); | OK | OK — unchanged |  |
| S1234.1 | 1234 | - OptiType: 36/391 (9.2%; 6.7–12.5%); | OK | OK — unchanged |  |
| S1235.1 | 1235 | - SpecHLA: 13/118 (11.0%; 6.6–17.9%). | OK | OK — unchanged |  |
| S1237.1 | 1237 | This is within-panel dissent, not error against truth. | OK | OK — unchanged |  |
| S1243.1 | 1243 | These estimates measure the reproducibility of related caller panels on different assay inputs. | TERM | These estimates measure agreement between related caller panels on different assay inputs. | The next sentence retains the explicit no-accuracy boundary and shared-caller limitation. |
| S1244.1 | 1244 | They do not measure accuracy, and shared callers can raise agreement through correlated decisions. | OK | OK — unchanged |  |

### Supplement — S9.4 FIMM BB7.2 serogroup agreement

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| S1247.H | 1247 | ### S9.4 FIMM BB7.2 serogroup agreement | OK | OK — unchanged |  |
| S1249.1 | 1249 | BB7.2 flow status was joined by donor identity. | OK | OK — unchanged |  |
| S1249.2 | 1249 | The antibody was first characterized as an HLA-A2 typing reagent that also recognizes an HLA-A28 variant [34]. | OK | OK — unchanged |  |
| S1251.1 | 1251 | On single-antigen beads it is specific for HLA-A\*02 and A\*69 at low concentration, and cross-reacts with A\*68, A\*23 and A\*24 only at high concentration [35]. | OK | OK — unchanged |  |
| S1253.1 | 1253 | A\*02 is therefore the primary mapping. | OK | OK — unchanged |  |
| S1253.2 | 1253 | The A\*02/A\*68/A\*69 sensitivity mapping is a deliberately broad, high-concentration bound; an A\*02/A\*69 mapping alone was not computed. | OK | OK — unchanged |  |
| S1257.1 | 1257 | The metrics use the flow-linked subset (analysis tier C). | OK | OK — unchanged |  |
| S1257.2 | 1257 | They are donor-collapsed plurality calls over every caller available for that subset, not the three-caller FIMM panel of S9.1. | GRAM, CLAR | They use donor-collapsed plurality calls from every caller available in that subset, rather than the three-caller FIMM panel of S9.1. |  |
| S1260.1 | 1260 | - Only 16 of 53 flow records linked to the sequenced subset. | OK | OK — unchanged |  |
| S1261.1 | 1261 | - The informative linked donors were 8 for scRNA-seq, 14 for bulk RNA and 13 for WES. | OK | OK — unchanged |  |
| S1263.1 | 1263 | - All unlinked records remain in the source aggregate. | OK | OK — unchanged |  |
| S1265.1 | 1265 | These are serogroup agreement metrics, not allele-level accuracy. | OK | OK — unchanged |  |
| S1265.2 | 1265 | The table reports every confusion matrix and interval estimate. | OK | OK — unchanged |  |
| S1277.1 | 1277 | The brace notation in the final column denotes the five separately registered metric rows sharing that prefix. | REP | Braces in the final column denote five separately registered metric rows sharing that prefix. |  |
| S1278.1 | 1278 | Supplementary Figure S7 shows the primary confusion matrices and Wilson intervals for the primary and cross-reactivity mappings. | OK | OK — unchanged |  |
| S1282.1 | 1282 | Under the strict A\*02 mapping, the WES row has two false positives (specificity 0.667): two BB7.2-negative donors were assigned an A\*02 allele by the WES plurality. | LEN | Under the strict A\*02 mapping, the WES row has two false positives (specificity 0.667). WES plurality assigned an A\*02 allele to two BB7.2-negative donors. |  |
| S1284.1 | 1284 | With only two such donors, no caller- or assay-specific conclusion is drawn. | OK | OK — unchanged |  |
| S1285.1 | 1285 | Under the primary mapping, bulk RNA had no false positives (specificity 1.000). | OK | OK — unchanged |  |

### Supplement — S9.5 Separate VenEx WES diagnostic cohort

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| S1288.H | 1288 | ### S9.5 Separate VenEx WES diagnostic cohort | OK | OK — unchanged |  |
| S1290.1 | 1290 | VenEx contains 86 WES samples and 258 class I sample–gene loci. | OK | OK — unchanged |  |
| S1290.2 | 1290 | Dissent is measured against a plurality that includes the caller being compared, so it is not error against truth. | OK | OK — unchanged |  |
| S1292.1 | 1292 | POLYSOLVER had no usable output: 64 samples had no file and 22 had an empty output. | OK | OK — unchanged |  |
| S1296.1 | 1296 | It therefore had no mutually callable loci, and its dissent rate is non-estimable. | OK | OK — unchanged |  |
| S1297.1 | 1297 | [RESULT:VENEX_WES_POLYSOLVER_CONTESTED_DISSENT] | OK | OK — unchanged |  |
| S1312.1 | 1312 | SpecHLA's 11.3% is within-panel dissent. | CLAR | SpecHLA's 11.3% measures within-panel dissent. |  |
| S1312.2 | 1312 | Neither it nor any other VenEx diagnostic establishes HLA accuracy. | OK | OK — unchanged |  |
| S1313.1 | 1313 | Supplementary Figure S8 presents caller availability and contested-locus dissent together. | OK | OK — unchanged |  |

### Supplement — S9.6 NCI-60 cell-line application (legacy analysis withdrawn; regeneration under way)

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| S1316.H | 1316 | ### S9.6 NCI-60 cell-line application (legacy analysis withdrawn; regeneration under way) | OK | OK — unchanged |  |
| S1318.1 | 1318 | HLA class I genotypes of the NCI-60 cancer cell lines have been published from sequence-based typing of exons 2 and 3 [36]. | OK | OK — unchanged |  |
| S1319.1 | 1319 | An earlier analysis ran callers on 42 NCI-60 cell lines, before the current singleton rule and the fail-closed reference parser existed: | OK | OK — unchanged |  |
| S1322.1 | 1322 | - WES: HLA-HD, OptiType, SpecHLA and T1K (no POLYSOLVER); | OK | OK — unchanged |  |
| S1323.1 | 1323 | - RNA-seq: arcasHLA, HLA-HD, OptiType, seq2HLA, SpecHLA and T1K. | OK | OK — unchanged |  |
| S1325.1 | 1325 | It scored them with the earlier harmonisation and a heuristic confidence weighting (`artifacts/source_results/publication_assessment.json`). | GRAM | It scored them with the earlier harmonization and a heuristic confidence weighting (`artifacts/source_results/publication_assessment.json`). | Oxford -ize convention; identifiers unchanged. |
| S1326.1 | 1326 | Its panels, call states, reference parsing and caller run all differ from those of the development analysis. | OK | OK — unchanged |  |
| S1328.1 | 1328 | The stored artifact also lacks the scored per-locus results, so its concordance estimates cannot be traced to a registered result, and they are withdrawn rather than reported. | OK | OK — unchanged |  |
| S1330.1 | 1330 | Before any NCI-60 estimate is reported, the analysis would have to be regenerated under the current rules, with the current workflow release and registry rows. | OK | OK — unchanged |  |
| S1332.1 | 1332 | In no case is it external validation. | OK | OK — unchanged |  |
| S1335.1 | 1335 | That regeneration is under way under a decision signed on 26 October 2026, before any NCI-60 prediction existed (`decisions/20261026_nci60_v350_regeneration.json`). | OK | OK — unchanged |  |
| S1337.1 | 1337 | Every cell line in the class I table of the published typing that has public paired reads is run once per assay with workflow release 3.5.0 and the development panels: 57 WES and 58 RNA-seq lines (`cohorts/nci60_v350_manifest.tsv`). | OK | OK — unchanged |  |
| S1340.1 | 1340 | One line has no paired WES reads and is excluded and listed, and RNA-seq reads are subsampled to 50 million pairs as in the earlier run. | OK | OK — unchanged |  |
| S1342.1 | 1342 | POLYSOLVER cannot run from FASTQ input in this release and is a declared non-call. | OK | OK — unchanged |  |
| S1343.1 | 1343 | The published typing is parsed fail-closed (`src/champhla_recovery/nci60.py`): its tabulation must match the article's own table cell by cell. | OK | OK — unchanged |  |
| S1345.1 | 1345 | Unresolved two-digit ambiguities, new alleles, unresolved entries, designations absent from IPD-IMGT/HLA 3.65.0 and any other token shape are excluded and listed. | OK | OK — unchanged |  |
| S1347.1 | 1347 | A single listed allele is read as a homozygous genotype, with a sensitivity analysis that excludes such loci. | OK | OK — unchanged |  |
| S1349.1 | 1349 | Predictions are frozen before the typing is joined once, and the result will be reported here, whatever its direction, as an exploratory descriptive application with registry rows and binomial intervals. | OK | OK — unchanged |  |

### Supplement — Supplementary figure legends

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| S1353.H | 1353 | ## Supplementary figure legends | OK | OK — unchanged |  |
| S1355.1 | 1355 | **Supplementary Figure S1. | OK | OK — unchanged |  |
| S1355.2 | 1355 | Caller call-state composition.** | OK | OK — unchanged |  |
| S1355.3 | 1355 | WES (A) and RNA-seq (B) bars partition each fixed assay–locus denominator into callable, singleton/partial, missing/failed-output, absent-row and invalid states; segment labels are counts. | OK | OK — unchanged |  |
| S1358.1 | 1358 | The normalized development table does not separate runtime failure from an empty or missing output, so no independent runtime-failure rate is inferred; the rerun's caller-task dispositions are in Supplementary Table S10.1. | LEN, REP | The normalized development table does not separate runtime failure from empty or missing output. No independent runtime-failure rate is inferred; Supplementary Table S10.1 gives rerun task dispositions. |  |
| S1362.1 | 1362 | **Supplementary Figure S2. | OK | OK — unchanged |  |
| S1362.2 | 1362 | Vote-threshold callability–concordance trade-off.** | OK | OK — unchanged |  |
| S1363.1 | 1363 | WES (A) and RNA-seq (B) show ChampHLA-Consensus, strict majority and two-thirds consensus in threshold order. | OK | OK — unchanged |  |
| S1364.1 | 1364 | Horizontal and vertical bars are marginal 95% subject-cluster percentile bootstrap intervals for callability and fixed-denominator concordance. | OK | OK — unchanged |  |
| S1366.1 | 1366 | Both axes are truncated to the observed range. | OK | OK — unchanged |  |
| S1367.1 | 1367 | The blue circle denotes ChampHLA-Consensus, the dark square strict majority and the grey diamond two-thirds consensus. | OK | OK — unchanged |  |
| S1368.1 | 1368 | The identical RNA-seq strict-majority and two-thirds point estimates use a composite marker and shared label; no jitter is applied. | OK | OK — unchanged |  |
| S1372.1 | 1372 | **Supplementary Figure S3. | OK | OK — unchanged |  |
| S1372.2 | 1372 | Support-profile concordance.** | OK | OK — unchanged |  |
| S1372.3 | 1372 | WES (A) and RNA-seq (B) use unreduced k-of-n profiles. | OK | OK — unchanged |  |
| S1373.1 | 1373 | Points and exact 95% binomial intervals are shown only for strata with at least five loci. | OK | OK — unchanged |  |
| S1374.1 | 1374 | Profiles with fewer than five loci remain listed with their denominators but their percentages and intervals are suppressed. | OK | OK — unchanged |  |
| S1376.1 | 1376 | The 0/0 profile is a non-call state outside the concordance scale. | OK | OK — unchanged |  |
| S1377.1 | 1377 | These strata are descriptive, not calibrated probabilities. | OK | OK — unchanged |  |
| S1379.1 | 1379 | **Supplementary Figure S4. | OK | OK — unchanged |  |
| S1379.2 | 1379 | Truth-definition sensitivity.** | OK | OK — unchanged |  |
| S1379.3 | 1379 | WES (A) and RNA-seq (B) compare exact two-field, ambiguity-compatible, G-compatible under a two-field mapping and P-group-compatible under a two-field mapping endpoints. | OK | OK — unchanged |  |
| S1381.1 | 1381 | Points and bars are estimates and 95% subject-cluster percentile bootstrap intervals. | OK | OK — unchanged |  |
| S1382.1 | 1382 | Each facet states its own denominator; estimates across different truth definitions are not connected or treated as paired. | OK | OK — unchanged |  |
| S1384.1 | 1384 | Each percentage axis is truncated below 100% to the observed range and stops at 100%. | OK | OK — unchanged |  |
| S1385.1 | 1385 | Colours and shapes follow Figure 2. | OK | OK — unchanged |  |
| S1387.1 | 1387 | **Supplementary Figure S5. | OK | OK — unchanged |  |
| S1387.2 | 1387 | Champion–challenger decision flow.** | OK | OK — unchanged |  |
| S1387.3 | 1387 | The exploratory fitted comparator defined in Supplementary S7.1. | OK | OK — unchanged |  |
| S1388.1 | 1388 | When the gene's frozen champion caller is callable, its genotype is reported unless the highest-weighted alternative passes every override gate; the declared margin gate is inactive as implemented (S7.1). | OK | OK — unchanged |  |
| S1391.1 | 1391 | When the champion has no call, a reliability-weighted consensus is reported only if it is untied and clears fixed support and margin thresholds. | OK | OK — unchanged |  |
| S1393.1 | 1393 | Weights and champions were fitted in the earlier analysis on the superseded development denominators. | OK | OK — unchanged |  |
| S1396.1 | 1396 | **Supplementary Figure S6. | OK | OK — unchanged |  |
| S1396.2 | 1396 | Exploratory FIMM cross-modality agreement and eligibility.** | OK | OK — unchanged |  |
| S1397.1 | 1397 | (A) Specimen-level exact unordered two-field agreement with Wilson 95% intervals for two coequal definitions: all complete callable pairs, and pairs with at least two valid callers in both assays. | OK | OK — unchanged |  |
| S1399.1 | 1399 | Counts are agreement/overlap; their denominator difference reflects caller availability, not biological sample selection. | OK | OK — unchanged |  |
| S1401.1 | 1401 | (B) Locus-row composition by the number of valid callers. | OK | OK — unchanged |  |
| S1402.1 | 1402 | Zero valid callers means missing consensus evidence, and one valid caller is not a vote. | OK | OK — unchanged |  |
| S1403.1 | 1403 | Because the callers are shared, panel agreement is not independent HLA truth. | OK | OK — unchanged |  |
| S1404.1 | 1404 | The recorded replicate-conflict, numeric-artefact, partial and missing counts are printed below the endpoint panel. | OK | OK — unchanged |  |
| S1407.1 | 1407 | **Supplementary Figure S7. | OK | OK — unchanged |  |
| S1407.2 | 1407 | Exploratory FIMM BB7.2 serogroup agreement.** | OK | OK — unchanged |  |
| S1407.3 | 1407 | (A) Primary A*02 confusion matrices for scRNA-seq, bulk RNA and WES; panel titles give the informative linked donors out of all 53 flow records. | OK | OK — unchanged |  |
| S1409.1 | 1409 | (B) Sensitivity, specificity and overall agreement with Wilson 95% intervals, under the A*02 primary mapping and the A*02/A*68/A*69 cross-reactivity sensitivity mapping. | OK | OK — unchanged |  |
| S1412.1 | 1412 | BB7.2 supplies serogroup-level evidence only; linkage is incomplete, and the endpoint is not allele-level accuracy. | OK | OK — unchanged |  |
| S1415.1 | 1415 | **Supplementary Figure S8. | OK | OK — unchanged |  |
| S1415.2 | 1415 | Exploratory VenEx WES diagnostics.** | OK | OK — unchanged |  |
| S1415.3 | 1415 | (A) Native caller-output availability across 86 samples. | OK | OK — unchanged |  |
| S1416.1 | 1416 | (B) Contested-locus dissent from the inclusive ChampHLA plurality, with Wilson 95% intervals. | OK | OK — unchanged |  |
| S1417.1 | 1417 | POLYSOLVER is shown as non-estimable at zero mutually callable loci. | OK | OK — unchanged |  |
| S1418.1 | 1418 | Dissent is not error against truth. | OK | OK — unchanged |  |
| S1421.1 | 1421 | **Supplementary Figure S9. | OK | OK — unchanged |  |
| S1421.2 | 1421 | Stored-to-v3.5.0 caller-cell changes.** | OK | OK — unchanged |  |
| S1421.3 | 1421 | WES (A) and RNA-seq (B) bars partition each panel caller's caller–gene cells by how the v3.5.0 rerun call relates to the historical stored call. | OK | OK — unchanged |  |
| S1423.1 | 1423 | The categories are identical, call changed, non-call to callable, callable to non-call, and cells present only in the rerun. | REP | Categories are identical, call changed, non-call to callable, callable to non-call, and present only in the rerun. |  |
| S1425.1 | 1425 | Values are percentages of that caller's cells, and the counts are in Supplementary Table S10.2. | OK | OK — unchanged |  |
| S1426.1 | 1426 | The figure is aggregate-only and uses no reference typing. | OK | OK — unchanged |  |

### Supplement — S10. Reproducibility contract

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| S1429.H | 1429 | ## S10. Reproducibility contract | OK | OK — unchanged |  |

### Supplement — Full-cohort v3.5.0 rerun audit tables

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| S1431.H | 1431 | ### Full-cohort v3.5.0 rerun audit tables | OK | OK — unchanged |  |
| S1433.1 | 1433 | These aggregate tables are populated only after the signed 236-run roster has passed the checksum, release-provenance and caller-grid gates. | OK | OK — unchanged |  |
| S1434.1 | 1434 | They contain no subject identifiers and are not used as interim performance evidence. | OK | OK — unchanged |  |
| S1483.1 | 1483 | Supplementary Figure S9 shows the same counts as proportions of each caller's cells. | OK | OK — unchanged |  |
| S1484.1 | 1484 | Supplementary Table S10.3 classifies every changed cell without the reference typing. | OK | OK — unchanged |  |
| S1485.1 | 1485 | Each cell is classed by its zygosity transition, by whether one or both alleles were replaced, by whether an allele group (first field) changed, and, for T1K, by whether the rerun call follows a release 3.5.0 parser rule recorded in that sample's checksummed parser audit. | PASS, REP | We classify cells by zygosity transition, replacement of one or both alleles, change in allele group (first field) and, for T1K, agreement with a release 3.5.0 parser rule in the sample's checksummed audit. |  |
| S1488.1 | 1488 | It also records whether any other caller changed at the same locus, and whether the stored or the rerun call matches the complete pair of more of the other panel callers' rerun calls there. | CLAR, REP | The classification also records whether another caller changed at the locus and whether more other panel callers' rerun genotypes match the stored or rerun pair. |  |
| S1491.1 | 1491 | Cells present only in the rerun are excluded. | OK | OK — unchanged |  |
| S1493.1 | 1493 | In WES, OptiType changed least. | OK | OK — unchanged |  |
| S1493.2 | 1493 | Most changed allele pairs in the other callers replace one allele of a heterozygous pair. | OK | OK — unchanged |  |
| S1494.1 | 1494 | Only a minority turn a homozygous call into a heterozygous one, so the changes are mostly not the haplotype-loss pattern that the read rescue repaired. | LEN | Only a minority change homozygous calls to heterozygous ones. Most changes therefore lack the haplotype-loss pattern repaired by read rescue. |  |
| S1496.1 | 1496 | Most WES changed cells are the only change at their locus. | GRAM | Most changed WES cells are the only change at their locus. |  |
| S1497.1 | 1497 | That points to caller-specific responses rather than a swapped sample input. | OK | OK — unchanged |  |
| S1500.1 | 1500 | Most T1K changes of call state follow a release 3.5.0 parser rule: either a partial call became a native homozygous declaration, or the quality filter reduced a pair. | OK | OK — unchanged |  |
| S1502.1 | 1502 | For HLA-HD, SpecHLA, T1K and OptiType in WES, the rerun call more often matches the other callers; for POLYSOLVER, the stored call more often does. | OK | OK — unchanged |  |
| S1504.1 | 1504 | In RNA-seq, the stored arcasHLA call matched more of the other callers in almost every changed cell, consistent with the deployment defect described in the main-text Limitations. | OK | OK — unchanged |  |
| S1508.1 | 1508 | The historical run recorded neither its read handling nor its caller executables and databases. | OK | OK — unchanged |  |
| S1509.1 | 1509 | The remaining changes therefore cannot be divided between the rerun's read route (HLA-read rescue with realignment to primary chr6) and differences in caller version or database. | NOM, PASS | We therefore cannot separate effects of the rerun's read route (HLA-read rescue and realignment to primary chr6) from caller-version or database differences. |  |
| S1511.1 | 1511 | This classification is descriptive and was not used to choose any input, caller or rule. | OK | OK — unchanged |  |
| S1529.1 | 1529 | The release boundary starts at: | OK | OK — unchanged |  |
| S1531.1 | 1531 | - `data/development/normalized_caller_calls.tsv`, which is truth-free; | OK | OK — unchanged |  |
| S1532.1 | 1532 | - `data/development/normalized_secondary_calls.tsv`, for frozen exploratory predictions; and | OK | OK — unchanged |  |
| S1534.1 | 1534 | - a downloaded public truth file whose checksum must match the pinned value. | OK | OK — unchanged |  |
| S1536.1 | 1536 | One top-level command (`scripts/run_local_verification.sh`) regenerates the selected truth, primary and secondary predictions, truth join, statistical outputs, the S12 restored analyses (given the recovered caller table), tables, figures, claim audit and DOCX. | REP | One command (`scripts/run_local_verification.sh`) regenerates selected truth, primary and secondary predictions, the truth join, statistics, S12 restored analyses (given the recovered caller table), tables, figures, claim audit and DOCX. |  |
| S1539.1 | 1539 | The exploratory FIMM and VenEx aggregates are regenerated only inside the controlled environment that holds the patient data. | OK | OK — unchanged |  |
| S1540.1 | 1540 | Release mode must fail if any scientific stage is skipped, if generated artifacts are stale, if truth columns appear in prediction inputs, if active artifacts contain WGS results, or if unresolved scientific placeholders remain. | REP | Release mode fails if scientific stages are skipped, artifacts are stale, prediction inputs contain truth columns, active artifacts contain WGS results or scientific placeholders remain unresolved. |  |
| S1543.1 | 1543 | The only permitted pre-submission gate is the consolidated author/archive input block listed in the manuscript. | OK | OK — unchanged |  |
| S1546.1 | 1546 | The raw-read-to-caller Nextflow workflow is an external dependency and is not inside this verified boundary. | JARG, REP | The raw-read-to-caller Nextflow workflow is an external dependency outside this verified analysis. |  |
| S1547.1 | 1547 | For the historical caller run, exact caller executable versions, container digests, scheduler job identifiers and measured historical caller resource use remain unavailable; historical costs were neither reconstructed nor estimated. | LEN | OK — unchanged | TEST PINNED: test_compute_smoke_claims_preserve_actual_input_and_scope requires “historical caller resource use remain unavailable”. Retain the complete original sentence. Possible wording for a later test-reviewed pass: “Historical caller executables, container digests, scheduler jobs and measured resource use are unavailable; costs were not reconstructed or estimated.” |
| S1550.1 | 1550 | The v3.5.0 rerun that supplies the primary inputs records the following for every sample (`provenance/development_rerun_v350/truth_free_collection/sample_run_provenance.tsv`): | OK | OK — unchanged |  |
| S1554.1 | 1554 | - the workflow release commit; | OK | OK — unchanged |  |
| S1555.1 | 1555 | - the scheduler job identifier; and | OK | OK — unchanged |  |
| S1556.1 | 1556 | - checksummed manifests of its inputs, container images, workflow files and result files. | OK | OK — unchanged |  |
| S1559.1 | 1559 | Two later single-sample test runs on HG00096 provide current workflow, container and scheduler evidence. | OK | OK — unchanged |  |
| S1560.1 | 1560 | These operational measurements cannot be attributed retrospectively to the development cohort or extrapolated to cohort requirements. | REP | These operational measurements do not reconstruct development-cohort use or establish cohort requirements. |  |
| S1562.1 | 1562 | The analysis environment is pinned to Python 3.11.15, NumPy 1.26.4, SciPy 1.14.1, Matplotlib 3.9.2 and python-docx 1.2.0. | OK | OK — unchanged |  |
| S1563.1 | 1563 | The analysis release is reproducible from the normalized outputs. | JARG | The analysis can be reproduced from normalized outputs. |  |
| S1564.1 | 1564 | Regenerating those outputs means re-running the workflow from the reads, which lies outside this boundary. | JARG, REP | Regenerating those outputs requires re-running the workflow from reads, outside the verified analysis. |  |

### Supplement — Caller-run and current-workflow provenance

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| S1568.H | 1568 | ### Caller-run and current-workflow provenance | OK | OK — unchanged |  |
| S1570.1 | 1570 | The development callers were run in April and May 2026 with an unarchived pre-release ChampHLA deployment on CSC – IT Center for Science (CSC) infrastructure, by inference the Puhti cluster, since no job of this project on its successor system predates July 2026. | OK | OK — unchanged |  |
| S1573.1 | 1573 | The stored T1K representation is consistent with a parser change made on 18 April 2026 (commit `304abfc`), so the whole caller run cannot be assigned to the earlier 7 April tree. | OK | OK — unchanged |  |
| S1575.1 | 1575 | The stored development calls do not show the read-loss pattern described below: POLYSOLVER, the caller it affects most, matched the vote's WES total in those outputs, but how the development run reached those reads is not recorded. | LEN, REP | The stored development calls lack the read-loss pattern described below. POLYSOLVER, the most affected caller, matched the vote's WES total in those outputs, but its historical read route is unrecorded. |  |
| S1578.1 | 1578 | The v3.5.0 rerun includes the read rescue, and there POLYSOLVER scored 138/153. | OK | OK — unchanged |  |
| S1582.1 | 1582 | The current workflow (release 3.5.0, which changes only the T1K parser relative to release 3.4.1) uses SAMtools 1.21 and BWA 0.7.19 from the software-module collection that CSC maintains on Roihu (bio-apps release v202603). | REP | The current workflow (release 3.5.0, differing from release 3.4.1 only in the T1K parser) uses SAMtools 1.21 and BWA 0.7.19 from CSC's Roihu software-module collection (bio-apps release v202603). |  |
| S1583.1 | 1583 | Its caller images are Singularity images converted from public Docker and BioContainers images, each pinned by SHA-256 in `configs/caller_resources_v2.json`, and SpecHLA runs from a native installation. | REP | Caller images are Singularity conversions of public Docker and BioContainers images, pinned by SHA-256 in `configs/caller_resources_v2.json`; SpecHLA uses a native installation. |  |
| S1586.1 | 1586 | The official IPD-IMGT/HLA 3.65.0 resources used for the G-group and nomenclature sensitivity analyses are pinned to their upstream release tag and locally checksummed. | OK | OK — unchanged |  |
| S1588.1 | 1588 | Single-sample task measurements of the current workflow, below, do not reconstruct the resource use of the development caller run or support cost or scaling claims. | REP | The single-sample task measurements below do not reconstruct historical development-run resource use or establish cost or scaling. |  |

### Supplement — HG00096 re-run against the stored development calls

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| S1592.H | 1592 | ### HG00096 re-run against the stored development calls | OK | OK — unchanged |  |
| S1594.1 | 1594 | On 19 September 2026, HG00096 was run with pre-release revision `91f035f6f0`. | OK | OK — unchanged |  |
| S1595.1 | 1595 | All 12 RNA-seq caller–gene calls from the Geuvadis BAM matched the stored calls, whereas 4 of 12 WES calls from an HLA-region pre-extract matched; the WES denominator was four callers by three genes because SpecHLA was absent. | OK | OK — unchanged |  |
| S1598.1 | 1598 | On 9 October 2026, release 3.3.0 (tag `v3.3.0`, commit `360a449`) was run on the whole-exome CRAM and matched 5 of 15 stored calls. | OK | OK — unchanged |  |
| S1599.1 | 1599 | These two WES routes lost reads: the GRCh38 alignments place many reads from non-reference HLA alleles on HLA-allele and chromosome 6 alternate-haplotype contigs, so the second haplotype disappeared. | OK | OK — unchanged |  |
| S1604.1 | 1604 | Also on 9 October, the release-3.4.0-equivalent WES tree `15f45cf` collected those reads and realigned them to chromosome 6. | OK | OK — unchanged |  |
| S1605.1 | 1605 | Release tag `v3.4.0` (commit `2a72a4b`) differs from that run tree only by version strings and the changelog. | OK | OK — unchanged |  |
| S1607.1 | 1607 | All five callers then reported the same genotype at all three genes and 11 of 15 calls matched the stored calls. | OK | OK — unchanged |  |
| S1608.1 | 1608 | The four differences were HLA-HD at HLA-B and HLA-C, SpecHLA at HLA-C and T1K at HLA-B. | OK | OK — unchanged |  |
| S1609.1 | 1609 | The 9 October RNA-seq run used release 3.4.0 on the Geuvadis BAM and matched 11 of 12 stored calls; arcasHLA reported a different HLA-C allele. | OK | OK — unchanged |  |
| S1611.1 | 1611 | These diagnostics are from one subject only, and the four old/new WES differences were not explained by the read-rescue result. | REP | These one-subject diagnostics did not explain the four old/new WES differences through read rescue. |  |

### Supplement — Current single-sample workflow test measurements

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| S1620.H | 1620 | ### Current single-sample workflow test measurements | OK | OK — unchanged |  |
| S1622.1 | 1622 | Two successful HG00096 runs on the CSC Roihu cluster are reported. | OK | OK — unchanged |  |
| S1622.2 | 1622 | Both used pre-release workflow revisions that break exact ties toward the last-sorting pair, unlike release 3.4.0, and the RNA-seq run had a locally modified seq2HLA module; the table gives each revision and image hash. | LEN | Both used pre-release revisions that break exact ties toward the last-sorting pair, unlike release 3.4.0. The RNA-seq run also used a locally modified seq2HLA module; the table gives revisions and image hashes. |  |
| S1625.1 | 1625 | The DNA caller route used a WGS-derived mate-aware HLA BAM, not WES reads; it therefore does not estimate WES runtime. | OK | OK — unchanged | Protected scope wording retained; pinned by manuscript reconciliation tests. |
| S1627.1 | 1627 | The RNA-seq route used paired FASTQ. | OK | OK — unchanged |  |
| S1627.2 | 1627 | Nextflow `realtime` and `peak_rss` are task-level trace fields. | OK | OK — unchanged |  |
| S1628.1 | 1628 | Slurm `Elapsed`, `TotalCPU` and batch-step `MaxRSS` are reported separately because their definitions and instrumentation differ. | OK | OK — unchanged |  |
| S1630.1 | 1630 | Disagreement between the two sources is retained, rather than resolved by selecting the smaller or larger value. | CLAR, REP | Disagreement between the measurement sources is retained; neither smaller nor larger values are selected. |  |
| S1631.1 | 1631 | Versions are reported exactly as emitted: OptiType produced usage text, and T1K and arcasHLA produced empty version fields, so those versions remain unresolved. | LEN | Version fields are reported as emitted. OptiType produced usage text; T1K and arcasHLA produced empty fields, leaving those versions unresolved. |  |
| S1633.1 | 1633 | SpecHLA ran from a native local installation; the other caller rows used the named SIF. | OK | OK — unchanged |  |
| S1652.1 | 1652 | All rows describe one sample and successful tasks only. | OK | OK — unchanged |  |
| S1652.2 | 1652 | They are not monetary costs, historical development-cohort measurements, scaling estimates or accuracy evidence. | OK | OK — unchanged | Protected scope wording retained; pinned by manuscript reconciliation tests. |
| S1654.1 | 1654 | Raw traces, task commands, launch wrappers, workflow source, version files, container inspection output and scheduler records are preserved under `provenance/compute_smoke/raw`; their hashes and row-level provenance are recorded in `artifacts/compute_smoke_benchmark.tsv`. | OK | OK — unchanged |  |

### Supplement — S11. Running the ChampHLA workflow

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| S1659.H | 1659 | ## S11. Running the ChampHLA workflow | OK | OK — unchanged |  |
| S1661.1 | 1661 | This section describes the workflow release in the pipeline repository (Data and software availability). | OK | OK — unchanged |  |
| S1662.1 | 1662 | The commands below were checked against that release's parameter definitions; they are usage guidance, not part of the verified evidence chain of this paper. | OK | OK — unchanged |  |

### Supplement — S11.1 Requirements and inputs

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| S1666.H | 1666 | ### S11.1 Requirements and inputs | OK | OK — unchanged |  |
| S1668.1 | 1668 | The workflow requires Nextflow and either Docker or Singularity. | OK | OK — unchanged |  |
| S1668.2 | 1668 | Callers run from containers; in the deployment used here SpecHLA ran from a native installation (Supplementary S10). | OK | OK — unchanged |  |
| S1670.1 | 1670 | HLA-HD and T1K need separately obtained reference databases, and the workflow stops at start-up if a requested caller's database path is not set. | OK | OK — unchanged |  |
| S1672.1 | 1672 | Input is either a directory (`--input` with `--input_type bam`, `cram` or `fastq`) or a CSV samplesheet (`--input_samplesheet`) with columns `sample_id,bam_path`, `sample_id,cram_path` or `sample_id,fastq_1,fastq_2`. | OK | OK — unchanged |  |
| S1675.1 | 1675 | CRAM input also needs `--reference_fasta`. | OK | OK — unchanged |  |
| S1678.1 | 1678 | The workflow wraps eight callers (main Table 1), each run as its own process and container with its own preprocessing, invocation and output parser. | REP | The workflow wraps eight callers (main Table 1), each with its own process, container, preprocessing, invocation and parser. |  |
| S1679.1 | 1679 | A sequencing mode (DNA, bulk RNA-seq, PacBio HiFi or Oxford Nanopore) and the resolved assay determine which callers run. | OK | OK — unchanged |  |
| S1681.1 | 1681 | Unless a caller list is given, the workflow runs the assay's reference panel, declared in one configuration file so that a partial installation can be detected. | OK | OK — unchanged |  |
| S1683.1 | 1683 | DNA-only callers are skipped for RNA-seq input. | OK | OK — unchanged |  |
| S1684.1 | 1684 | The long-read modes currently run T1K only and, like WGS (Supplementary S8), are not evaluated here. | OK | OK — unchanged |  |
| S1685.1 | 1685 | Each run also writes an HTML report. | OK | OK — unchanged |  |
| S1687.1 | 1687 | From release 3.4.0, every DNA BAM or CRAM passes through a read-rescue step before any caller. | OK | OK — unchanged |  |
| S1688.1 | 1688 | It collects the reads in the chromosome 6 MHC window, on every HLA-allele and chromosome 6 alternate-haplotype contig and the unplaced reads in one streaming pass, keeps complete pairs and realigns them to primary chromosome 6 with bwa. | LEN | In one streaming pass, it collects reads from the chromosome 6 MHC window, every HLA-allele and chromosome 6 alternate-haplotype contig, and unplaced reads. It keeps complete pairs and realigns them to primary chromosome 6 with bwa. |  |
| S1691.1 | 1691 | This needs `--hla_rescue_reference`, a primary chromosome 6 FASTA with a bwa index, built by the workflow's `build_hla_rescue_reference.sh` script. | OK | OK — unchanged |  |
| S1693.1 | 1693 | Release 3.3.0 lacked this step and lost the second haplotype on GRCh38 alignments that carry such contigs (main Methods, Study design). | OK | OK — unchanged |  |
| S1695.1 | 1695 | Alignments without those contigs keep their alignments. | OK | OK — unchanged |  |

### Supplement — S11.2 Reproducing the evaluated rule

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| S1697.H | 1697 | ### S11.2 Reproducing the evaluated rule | OK | OK — unchanged |  |
| S1699.1 | 1699 | The consensus step is off by default and, when enabled, defaults to a calibrated weighting and a gene list that includes class II genes. | LEN, REP | The consensus step is off by default. When enabled, it defaults to calibrated weighting and a gene list including class II genes. |  |
| S1700.1 | 1700 | The `paper` profile applies the rule evaluated in this paper: it enables the consensus step with equal weights, runs the assay's reference panel (`--tools` unset), restricts voting to HLA-A, -B and -C, and applies the call-state rules of the Methods (`--mv_call_states paper`). | REP | The `paper` profile enables the evaluated rule: equal weights, the assay's reference panel (`--tools` unset), HLA-A, -B and -C voting, and Methods call states (`--mv_call_states paper`). |  |
| S1704.1 | 1704 | Combine it with an execution profile: | OK | OK — unchanged |  |
| S1724.1 | 1724 | The workflow repository's parity test (<https://github.com/uoozcan/PanelHLA/blob/71f037d/tests/test_paper_parity.py>) feeds the stored raw caller outputs of the development set through the consensus step under these settings and requires the ChampHLA-Consensus call, including every abstention, at all 708 development loci (workflow commit `71f037d`; the release tag is given under Data availability). | LEN, REP | The workflow parity test (<https://github.com/uoozcan/PanelHLA/blob/71f037d/tests/test_paper_parity.py>) feeds stored raw development outputs through consensus with these settings. It requires the ChampHLA-Consensus call, including abstentions, at all 708 loci (workflow commit `71f037d`; release tag under Data availability). |  |
| S1730.1 | 1730 | Earlier workflow revisions broke exact ties in the opposite lexicographic order and abstained on caller-declared homozygotes; both are corrected in that commit. | OK | OK — unchanged |  |

### Supplement — S11.3 Execution profiles and resources

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| S1734.H | 1734 | ### S11.3 Execution profiles and resources | OK | OK — unchanged |  |
| S1736.1 | 1736 | Profiles are provided for local Docker (`docker`), Singularity (`singularity`), generic Slurm clusters (`slurm`) and the CSC Roihu and Puhti systems (`roihu`, `puhti`), plus `test` and `stub` profiles. | OK | OK — unchanged |  |
| S1738.1 | 1738 | Caller processes carry one of three resource labels; failed tasks are retried with resources multiplied by the attempt number, capped by `--max_cpus`, `--max_memory` and `--max_time`. | OK | OK — unchanged |  |
| S1741.1 | 1741 | `-resume` reuses completed tasks when samples are added or a run is restarted. | OK | OK — unchanged |  |

### Supplement — S11.4 Outputs

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| S1749.H | 1749 | ### S11.4 Outputs | OK | OK — unchanged |  |
| S1751.1 | 1751 | Each caller writes its native output to its own directory under `--outdir`. | OK | OK — unchanged |  |
| S1752.1 | 1752 | When the consensus step is enabled, the `consensus/` directory contains the files below, and `report/` contains an HTML run report. | OK | OK — unchanged |  |

### Supplement — S12. Disagreement classes, cross-assay agreement, per-gene concordance and caller calibration

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| S1762.H | 1762 | ## S12. Disagreement classes, cross-assay agreement, per-gene concordance and caller calibration | OK | OK — unchanged |  |
| S1764.1 | 1764 | These analyses were part of earlier drafts of this work. | REP | These analyses appeared in earlier drafts. |  |
| S1764.2 | 1764 | They describe the historical stored outputs, not the v3.5.0 rerun: they were computed on the exact-endpoint loci of the frozen historical joined development table by `scripts/restored_analyses.py`, which writes `artifacts/restored_analyses/` with an input-checksum manifest, and they are not recomputed on the rerun inputs. | LEN | They describe historical stored outputs, not the v3.5.0 rerun. `scripts/restored_analyses.py` computed them from exact-endpoint loci in the frozen historical joined development table and wrote `artifacts/restored_analyses/` with an input-checksum manifest. They are not recomputed from rerun inputs. |  |
| S1769.1 | 1769 | Their numbers are reconciled against the archived historical result registry (`provenance/development_rerun_v350/`) and are reported as provenance only. | OK | OK — unchanged |  |
| S1771.1 | 1771 | All four are post hoc and descriptive; S12.4 is additionally exploratory because its probabilities were calibrated in the earlier analysis on the superseded 390-locus WES and 321-locus RNA-seq sets, including WGS rows, not on the current exact loci. | LEN | All four are post hoc and descriptive. S12.4 is also exploratory: its probabilities were calibrated on superseded 390-locus WES and 321-locus RNA-seq sets, including WGS rows, not current exact loci. |  |

### Supplement — S12.1 Truth-free disagreement classes

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| S1776.H | 1776 | ### S12.1 Truth-free disagreement classes | OK | OK — unchanged |  |
| S1778.1 | 1778 | Each locus was assigned to one class using only the calls of its callable panel callers: no callable caller; a single callable caller; unanimous agreement among two or more callers; a one-allele conflict, in which every dissenting genotype shares one allele with the reported genotype; or a two-allele conflict, in which at least one dissenting genotype shares no allele with it. | PASS, REP | Using callable panel outputs alone, we assigned loci to classes: no callable caller; a single callable caller; unanimity among two or more callers; one-allele conflict, where every dissenting genotype shares one allele with the reported pair; or two-allele conflict, where at least one shares none. |  |
| S1783.1 | 1783 | In RNA-seq, one-allele conflicts are the pattern expected when one allele of a heterozygous genotype is under-sampled. | OK | OK — unchanged |  |
| S1784.1 | 1784 | Intervals are exact Clopper–Pearson 95% intervals. | OK | OK — unchanged |  |
| S1801.1 | 1801 | In WES, all callable callers agreed at 93 of 153 loci, where ChampHLA-Consensus was correct at 90 (96.8%). | OK | OK — unchanged |  |
| S1802.1 | 1802 | At the 57 loci where every dissenting caller differed from the reported genotype at one allele, it was correct at 51 (89.5%), and 3 loci had a dissenting genotype sharing no allele with it. | OK | OK — unchanged |  |
| S1804.1 | 1804 | In RNA-seq, callers agreed unanimously at 102 of 118 loci (98 correct; 96.1%), one-allele conflicts occurred at 13 loci with 12 correct (92.3%), and 3 loci had a single callable caller, all of which were correct. | OK | OK — unchanged |  |

### Supplement — S12.2 Cross-assay agreement

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| S1815.H | 1815 | ### S12.2 Cross-assay agreement | OK | OK — unchanged |  |
| S1817.1 | 1817 | Loci of the 50 subjects with exact reference typing in both assays. | OK | OK — unchanged |  |
| S1817.2 | 1817 | The pooled vote is a post hoc plurality over the calls of both panels, with each caller contributing one vote per assay and the same lexicographic tie-break; it is shown for comparison only. | OK | OK — unchanged |  |
| S1833.1 | 1833 | The WES and RNA-seq consensus calls agreed at 115 of the 116 loci, of which 110 were correct. | OK | OK — unchanged |  |
| S1834.1 | 1834 | At the one locus where they disagreed, the RNA-seq call was correct and the WES call was not. | OK | OK — unchanged |  |
| S1835.1 | 1835 | The pooled vote was correct at 111 of 116 loci, compared with 110 for WES and 111 for RNA-seq consensus alone. | OK | OK — unchanged |  |
| S1836.1 | 1836 | Because the same callers appear in both panels and the pooled rule was examined after the fact, cross-assay agreement is a consistency check rather than independent truth, and the pooled vote is not a validated method. | LEN | Both panels share callers, and the pooled rule was examined post hoc. Cross-assay agreement is therefore a consistency check, not independent truth; the pooled vote is not validated. |  |

### Supplement — S12.3 Per-gene caller concordance

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| S1847.H | 1847 | ### S12.3 Per-gene caller concordance | OK | OK — unchanged |  |
| S1849.1 | 1849 | Exact two-field concordance on the fixed denominator, so a no-call counts as incorrect; cells give correct/loci (percent). | OK | OK — unchanged |  |
| S1868.1 | 1868 | In WES the least concordant caller was T1K for HLA-A and HLA-C and SpecHLA for HLA-B, whereas in RNA-seq no caller led for every gene: HLA-HD and OptiType tied for HLA-A and HLA-C, and arcasHLA led for HLA-B. | OK | OK — unchanged |  |

### Supplement — S12.4 Caller calibration (exploratory)

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| S1880.H | 1880 | ### S12.4 Caller calibration (exploratory) | OK | OK — unchanged |  |
| S1882.1 | 1882 | Out-of-fold calibrated probabilities from the recovered caller table, scored against exact correctness at the current loci. | GRAM | Out-of-fold calibrated probabilities from the recovered caller table were scored against exact correctness at current loci. |  |
| S1883.1 | 1883 | The table reports scored loci over callable loci; six of 115 callable HLA-HD RNA-seq loci lacked a preserved calibrated probability and were excluded from calibration scoring. | LEN | OK — unchanged | TEST PINNED: restored v5 verbatim with author approval on 26 October 2026; test unchanged. tests/test_sr023_consistency.py::test_s12_uses_exact_intervals_and_explains_calibration_denominator. Proposed editorial alternative for author review: The table reports scored over callable loci. Six of 115 callable HLA-HD RNA-seq loci lacked preserved calibrated probabilities and were excluded from calibration scoring. |
| S1885.1 | 1885 | ECE is the expected calibration error over five equal-width probability bins. | OK | OK — unchanged |  |
| S1886.1 | 1886 | POLYSOLVER and SpecHLA report no confidence value. | OK | OK — unchanged |  |
| S1887.1 | 1887 | The calibration models were fitted against earlier development labels, so these values describe agreement between stated confidence and observed concordance on this resource only. | OK | OK — unchanged |  |
| S1889.1 | 1889 | The original caller table is checksum-pinned but is not in this checkout; this calibration table is therefore retained as a checksum-pinned historical artifact, whereas the other S12 tables were computed from the historical joined locus table. | LEN, PASS | The original caller table is checksum-pinned but absent from this checkout. We retain the calibration table as a checksum-pinned historical artifact; other S12 tables were computed from the historical joined locus table. |  |

### Supplement — S13. Background and design rationale

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| S1908.H | 1908 | ## S13. Background and design rationale | OK | OK — unchanged |  |
| S1910.1 | 1910 | This section gives the fuller background and design reasoning that the main text compresses. | NOM, REP | This section expands the background and design rationale summarized in the main text. |  |
| S1911.1 | 1911 | It contains no results. | OK | OK — unchanged |  |

### Supplement — S13.1 Why HLA typing is hard, and why callers disagree

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| S1913.H | 1913 | ### S13.1 Why HLA typing is hard, and why callers disagree | OK | OK — unchanged |  |
| S1915.1 | 1915 | The classical class I genes HLA-A, HLA-B and HLA-C present intracellular peptides to CD8-positive T cells. | OK | OK — unchanged |  |
| S1916.1 | 1916 | The classical class II genes HLA-DR, HLA-DQ and HLA-DP present extracellular peptides to CD4-positive helper T cells [1]. | OK | OK — unchanged |  |
| S1918.1 | 1918 | Together they are the main route by which adaptive immunity distinguishes self from infected, transformed or transplanted cells. | OK | OK — unchanged |  |
| S1921.1 | 1921 | That role explains both the extreme polymorphism of the region and why typing errors matter. | CLAR | This immune role explains the region's extreme polymorphism and the consequences of typing errors. |  |
| S1922.1 | 1922 | In unrelated-donor haematopoietic cell transplantation, matching is counted per allele: a donor matched at both alleles of HLA-A, -B, -C and -DRB1 is an 8/8 match, and adding HLA-DQB1 gives a 10/10 match [2, 3]. | OK | OK — unchanged |  |
| S1926.1 | 1926 | Three properties of the MHC make short-read typing difficult. | OK | OK — unchanged |  |
| S1927.1 | 1927 | - **Diversity.** | OK | OK — unchanged |  |
| S1927.2 | 1927 | The allele space is large and keeps growing with every IPD-IMGT/HLA release [8]. | OK | OK — unchanged |  |
| S1928.1 | 1928 | Reads from an allele that is poorly represented in a single linear reference are lost or misplaced before any caller sees them. | OK | OK — unchanged |  |
| S1930.1 | 1930 | - **Paralogy.** | OK | OK — unchanged |  |
| S1930.2 | 1930 | The region also contains pseudogenes, the class I chain-related genes MICA and MICB, and non-classical HLA-like loci. | OK | OK — unchanged |  |
| S1931.1 | 1931 | Reads from a polymorphic site of a classical gene can therefore align as well, or better, to a paralogous sequence. | OK | OK — unchanged |  |
| S1934.1 | 1934 | - **Expression.** | OK | OK — unchanged |  |
| S1934.2 | 1934 | RNA-seq samples expressed copies rather than genomic ones. | OK | OK — unchanged |  |
| S1935.1 | 1935 | When one allele of a heterozygote is weakly expressed, a caller can under-represent or miss it. | OK | OK — unchanged |  |
| S1938.1 | 1938 | No single alignment strategy, reference space or scoring model handles all three equally well across genes, assays and populations. | OK | OK — unchanged |  |
| S1939.1 | 1939 | That is why callers built on different evidence disagree, and why their rankings change between assays. | OK | OK — unchanged |  |

### Supplement — S13.2 Caller choice as a selection problem

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| S1943.H | 1943 | ### S13.2 Caller choice as a selection problem | OK | OK — unchanged |  |
| S1945.1 | 1945 | For a given assay, a practitioner faces a selection problem before an accuracy problem: which caller should be trusted for these data? | AI | For a given assay, users must choose a caller before they can assess its accuracy on their data. |  |
| S1946.1 | 1946 | Published rankings depend on the assay, the gene and the dataset, so the best caller for a new cohort is usually unknown in advance. | OK | OK — unchanged |  |
| S1948.1 | 1948 | A rule that combines callers without learned parameters avoids that choice instead of guessing it. | TERM, REP | Combining callers without fitted parameters avoids choosing a single caller. |  |
| S1951.1 | 1951 | Fitted integration policies bring costs that an equal-weight vote does not: | OK | OK — unchanged |  |
| S1952.1 | 1952 | - parameters that must be estimated; | OK | OK — unchanged |  |
| S1953.1 | 1953 | - a training resource that must resemble the target data; | OK | OK — unchanged |  |
| S1954.1 | 1954 | - a decision path that a user cannot easily audit. | OK | OK — unchanged |  |
| S1956.1 | 1956 | With one labelled development resource, any apparent gain of a fitted policy cannot be separated from fitting to that resource. | OK | OK — unchanged |  |
| S1957.1 | 1957 | This is why fitted policies are reported only as exploratory comparators (Supplementary S7). | PASS, REP | We therefore report fitted policies only as exploratory comparators (Supplementary S7). |  |

### Supplement — S13.3 Harmonisation is not a neutral preprocessing step

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| S1960.H | 1960 | ### S13.3 Harmonisation is not a neutral preprocessing step | GRAM | ### S13.3 Harmonization is not a neutral preprocessing step | Oxford -ize convention; identifiers unchanged. |
| S1962.1 | 1962 | A vote aggregates its panel. | OK | OK — unchanged |  |
| S1962.2 | 1962 | A harmonisation convention that several panel members share is therefore concentrated, not diluted, by the vote. | GRAM, AI | A harmonization convention shared by several panel members is concentrated by voting. |  |
| S1964.1 | 1964 | Completing a single reported allele into a homozygous pair is the clearest example. | OK | OK — unchanged |  |
| S1965.1 | 1965 | The completion is correct when the caller's own format declares homozygosity. | OK | OK — unchanged |  |
| S1966.1 | 1966 | It is wrong when a missing second allele marks a failed or partial call. | OK | OK — unchanged |  |
| S1967.1 | 1967 | Whether the convention helps or harms depends on the input, not on the voting rule. | OK | OK — unchanged |  |
| S1970.1 | 1970 | The transferable requirement is that a harmonisation layer deserves the same scrutiny as the integration rule. | AI, NOM, GRAM | Harmonization deserves the same scrutiny as the integration rule. |  |
| S1971.1 | 1971 | This benchmark therefore completes single alleles only where the caller declares homozygosity and reports the abstain-all alternative beside it (Supplementary S2). | OK | OK — unchanged |  |

### Supplement — S13.4 Why "no significant difference" is not equivalence

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| S1975.H | 1975 | ### S13.4 Why "no significant difference" is not equivalence | OK | OK — unchanged |  |
| S1977.1 | 1977 | A criterion phrased as the absence of a significant improvement passes automatically wherever a comparison is underpowered. | OK | OK — unchanged |  |
| S1978.1 | 1978 | Many comparisons in this benchmark are underpowered by construction: some could not reach significance at any effect size, because the number of discordant loci available to them is too small (detectability table in Supplementary S3; power table in Supplementary S7). | LOGIC, LEN | OK — unchanged | AUTHOR DECISION 6: the governing test counts nonzero subject aggregates, while this sentence attributes its limit to discordant loci. Leave this scientific unit unchanged pending author review; propose “discordant subjects” with explicit sign-flip scope. |
| S1981.1 | 1981 | The development results therefore support "could not be distinguished from" and never "equivalent to". | OK | OK — unchanged |  |
| S1983.1 | 1983 | Equivalence would need a pre-specified margin and a test designed for it. | OK | OK — unchanged |  |

### Supplement — S13.5 Deployed tools, database vintage and nomenclature

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| S1986.H | 1986 | ### S13.5 Deployed tools, database vintage and nomenclature | OK | OK — unchanged |  |
| S1988.1 | 1988 | Callers were evaluated as deployed, each with its own bundled IPD-IMGT/HLA release (Table 1 and Supplementary S6). | OK | OK — unchanged |  |
| S1989.1 | 1989 | This is how the tools are distributed, but it confounds the comparison. | OK | OK — unchanged |  |
| S1990.1 | 1990 | Part of what appears as caller disagreement is a difference in database vintage rather than in inference, and a caller whose bundled database predates an allele cannot call that allele. | LEN, REP, HEDGE | Database vintage can contribute to apparent caller disagreement; a caller cannot call an allele absent from its bundled database. | “Can contribute” preserves a possible database explanation without asserting that any observed error was caused by release age; the native-list audit does not attribute one. |
| S1992.1 | 1992 | The effect is not symmetric across callers. | OK | OK — unchanged |  |
| S1993.1 | 1993 | The caller ranking is therefore a ranking of deployed tools, not of algorithms; rebuilding every caller against one release would be a different study. | LEN, REP | Rankings therefore describe deployed tools, not algorithms. Rebuilding all callers against one database release would be a different study. |  |
| S1997.1 | 1997 | For the same reason, every step that compares alleles is pinned to declared nomenclature resources [8, 41]: | OK | OK — unchanged |  |
| S1999.1 | 1999 | - truth normalisation, call normalisation and the G-group and P-group sensitivity mappings each use a checksummed release; | GRAM | - truth normalization, call normalization and the G-group and P-group sensitivity mappings each use a checksummed release; | Oxford -ize convention; identifiers unchanged. |
| S2001.1 | 2001 | - concordance is scored on the unordered genotype, not on two independent alleles, so partial credit cannot hide an ambiguous or failed call; | OK | OK — unchanged |  |
| S2003.1 | 2003 | - set-valued (ambiguity-compatible) endpoints are reported beside the exact endpoint rather than replacing it. | OK | OK — unchanged |  |

### Supplement — S13.6 Workflow engineering as part of the method

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| S2006.H | 2006 | ### S13.6 Workflow engineering as part of the method | OK | OK — unchanged |  |
| S2008.1 | 2008 | Reproducibility is part of the methodological contribution rather than a supplement to it. | AI, REP | Reproducibility contributes to the method. |  |
| S2010.1 | 2010 | - Each caller runs as its own containerized process with a checksummed image. | OK | OK — unchanged |  |
| S2011.1 | 2011 | - Inputs are defined by manifests. | OK | OK — unchanged |  |
| S2012.1 | 2012 | - The release, the panel and the consensus rule are declared in versioned configuration (Supplementary S10 and S11). | OK | OK — unchanged |  |
| S2015.1 | 2015 | The same release can therefore be run by another group on the same public inputs, and on a new cohort without changing workflow code. | PASS, REP | Other groups can run the same release on the same public inputs or a new cohort without changing workflow code. |  |
| S2016.1 | 2016 | The signed rerun manifests record what was executed for every development sample. | OK | OK — unchanged |  |

### Supplement — S13.7 Scope and outlook

| # | line | original | issues | revised | note |
|---|---|---|---|---|---|
| S2019.H | 2019 | ### S13.7 Scope and outlook | OK | OK — unchanged |  |
| S2021.1 | 2021 | HLA allele frequencies differ across ancestry groups, and callers developed or validated mainly on European panels may behave differently elsewhere. | OK | OK — unchanged |  |
| S2022.1 | 2022 | The development resource is too small for population-stratified inference, so these analyses report pooled results and treat population patterns in reference retention as properties of the reference rather than of the callers (Supplementary S1). | LEN, PASS | The development resource is too small for population-stratified inference. We report pooled results and interpret population differences in reference retention as properties of the reference, rather than callers (Supplementary S1). |  |
| S2028.1 | 2028 | Class II typing matters for transplantation. | OK | OK — unchanged |  |
| S2028.2 | 2028 | The workflow already exposes HLA-DRB1, HLA-DQB1 and HLA-DQA1 for voting, but truth-backed class II evaluation awaits suitable reference typing. | OK | OK — unchanged |  |
| S2030.1 | 2030 | The same applies to: | OK | OK — unchanged |  |
| S2031.1 | 2031 | - higher-field typing; | OK | OK — unchanged |  |
| S2032.1 | 2032 | - re-extracted whole-genome inputs; | OK | OK — unchanged |  |
| S2033.1 | 2033 | - long-read and pangenome-graph callers; | OK | OK — unchanged |  |
| S2034.1 | 2034 | - downstream uses such as neoantigen prediction. | OK | OK — unchanged |  |
