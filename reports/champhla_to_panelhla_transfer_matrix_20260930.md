# CHAMPHLA-to-PanelHLA evidence-transfer ledger

**Date:** 2026-09-30  
**Decision:** Evidence-safe transfer into the active journal-neutral PanelHLA benchmark package

## Sources and classification

- Historical source: `D:/Users/uonur/Desktop/AML_project/a_aMANUSCRIPT/ChampHLA_Manuscript_Draft_V1.docx.md` and its corresponding PDF.
- Active source: `manuscripts/benchmark/manuscript.md` plus `manuscripts/benchmark/supplementary.md`.
- Governing records: `decisions/publication_route.json`, `decisions/20260924_publication_remediation.json`, `decisions/20260929_fimm_legacy_withdrawal.json`, and `decisions/20260929_fimm_panel_deviation.json`.

| Code | Meaning |
|---|---|
| A | Already represented in the active manuscript or supplement; no duplicate transfer. |
| R | Reusable only after rewriting, citation verification, and alignment to the active evidence boundary. |
| H | Historical context retained only as provenance or an explicitly exploratory method. |
| X | Excluded because invalid, unsupported, superseded, non-independent, or outside the active scope. |

No historical numerical result was transferred. No result registry, analysis code, figure, endpoint, denominator, or statistical method was changed.

## Section-by-section disposition

| Historical item | Code | Active disposition |
|---|:---:|---|
| Title and running title | R | Replaced by the PanelHLA benchmark title; a concise PanelHLA running title was added. |
| Author list and affiliations | R | Restored provisionally with an explicit confirmation gate; no ORCID, address, email or CRediT role was inferred. |
| Abstract | X | The historical workflow, WGS, fitted-policy, silver-truth and external-validation claims are superseded; the current abstract is retained unchanged. |
| 1. Introduction | R/A | Clinical motivation and class-I biology were condensed; current benchmark aim and scope remain authoritative. |
| 2.1 ChampHLA architecture | H | The historical workflow remains an external dependency; only the verified post-normalization boundary and current smoke evidence are reported. |
| 2.2 Champion–challenger ensemble | H | Operational definitions and development-only status remain in Supplementary S7; no headline method claim is restored. |
| 2.3 Benchmark-derived confidence weights and guardrail | H | Retained only as exploratory fitted-policy provenance in S7. |
| 2.4 Tool harmonization and allele normalization | A | Replaced by audited call states, syntactic normalization disclosure, and release-3.65 compatibility analyses. |
| 2.5 Discordance taxonomy | A | Covered by call-state, support-profile, caller-correlation and oracle-headroom analyses. |
| 2.6 FIMM haematological dataset | R/X | Only the corrected identity-linked exploratory analysis is active; legacy fingerprint pairing, LOH, HED and survival are excluded. |
| 2.7 1000 Genomes benchmark cohort | A | Covered by the corrected truth firewall, checksum-pinned source and fail-closed denominator construction. |
| 2.8 Computational performance benchmarking | H | Historical cohort-scale performance claims are excluded; current single-sample smoke measurements remain narrowly scoped in S10. |
| 2.9 Orthogonal silver-standard truth and pangenome validation | X | Locityper/Immuannot agreement is not independent biological truth and lacks the required reproducibility chain. |
| 2.10 External validation cohorts | X | NCI-60, GIAB and IHWG arms do not meet the active external-validation standard. |
| 2.11 Flow-cytometry HLA-A2 serotyping | R | Corrected donor-identity linkage and serogroup-only interpretation remain in S9.4; the BB7.2 primary citation was added. |
| 2.12 Consensus baselines, eligibility and independence | A | Covered by the current panel definitions, explicit call states, plurality rules and correlated-error analysis. |
| 3.1 Computational performance comparison | X/H | Historical cohort-scale runtime claims are excluded; only current smoke evidence is retained. |
| 3.1 HLA typing accuracy versus individual tools | X/A | Historical denominators and WGS values are excluded; corrected WES/RNA results are already in Table 1. |
| 3.2 Primary accuracy and adaptive MV-floor result | X/H | WGS and headline MV-floor claims are excluded; fitted policies remain development-only in S7. |
| 3.3 Concordance and heterogeneity across tools | A | Covered by current support profiles, missingness and error-correlation results. |
| 3.4 Confidence calibration and weights | H | Historical fitted analysis only; not promoted as a current validated contribution. |
| 3.5 Truth-set resolution ceiling | A | Replaced by exact, set-valued and G-group compatibility analyses. |
| 3.6 Pangenome silver-standard validation, including duplicate section | X | Excluded for non-independence and incomplete reproducibility. |
| 3.7 Bimodal/trimodal robustness | X | Historical WGS-containing and cross-modality performance claims are not active evidence. |
| 3.8 Descriptive frozen-policy external checks | X | Excluded from active validation claims. |
| 3.8 NCI-60 external validation, duplicate numbering | X | Excluded from active validation claims. |
| 3.9 FIMM HLA-A2 flow analysis | R | Replaced by the corrected, incomplete-linkage, serogroup-only analysis in S9.4. |
| 3.10 MV-floor routing diagnostics | H/X | Limited policy definitions remain in S7; WGS routing gains and deployment recommendations are excluded. |
| Discussion | R/A | Practical context was retained only where compatible with a research benchmark; promotional, clinical and deployment claims remain excluded. |
| Conclusions | X/A | Current restrained conclusion remains authoritative; no historical performance or usability claim was restored. |
| Acknowledgements | R | CSC acknowledgement restored provisionally; exact systems and contributors require confirmation. |
| Funding | R | Research Council of Finland grant 351507 to Ziaurrehman Tanoli restored provisionally. |
| Competing interests | R | “No competing interests” restored provisionally and still requires confirmation from every author. |
| Data availability | R/A | Public-data and controlled-FIMM boundaries were clarified; historical promised deposits and validation resources were not restored. |
| S1 Recommendations | X | End-user recommendations based on superseded method claims remain outside the paper. |
| S2 Limitations and future directions | A | Covered by the active Discussion and Limitations. |
| S3 HPC usage guide | X | Kept in versioned software documentation, not manuscript evidence. |
| S4 Local-computer usage guide | X | Kept in versioned software documentation, not manuscript evidence. |
| S5 Scenario walkthroughs | X | Kept in versioned software documentation, not manuscript evidence. |
| S6 (unstable/missing heading in converted source) | H | No uniquely attributable evidence-safe content was found for direct transfer. |
| S7 Champion–challenger sweep surface | H | Fitted-policy definitions and limitations remain in current S7; sweep claims are not promoted. |
| S8 (unstable/missing heading in converted source) | H | Historical figure material is handled by the figure ledger below. |
| S9 FIMM clinical/LOH analysis | R/X | Corrected agreement and BB7.2 components retained; LOH, dropout-as-LOH, HED and survival excluded. |
| S10 HPC execution | H/X | Current smoke records remain in S10; historical tutorial and scaling claims are excluded. |
| S11 Local execution | X | Software documentation only. |
| S12 Output schema | H | Workflow documentation only; no public schema change is made by this manuscript revision. |

## Main-figure disposition

The converted historical Markdown contains duplicated and inconsistent figure numbering. Every main figure number appearing in the source or its stated 14-figure sequence is accounted for below.

| Old figure | Code | Disposition |
|---|:---:|---|
| Figure 1, workflow and benchmark governance | H/X | Historical architecture only; not inserted because the raw caller workflow is outside the verified paper boundary. |
| Figure 2 | H/X | Caption-to-image mapping is unstable in the conversion; no distinct evidence-safe content was transferred. |
| Figure 3, per-gene changes versus majority vote | X | Depends on superseded fitted-policy/WGS analyses. |
| Figure 4 | H/X | Caption-to-image mapping is unstable; valid callability/error-dependence concepts already have current figures. |
| Figure 5, confirmatory/accuracy variants | X | Uses withdrawn denominators, WGS and fitted-policy claims. |
| Figure 6 | H/X | Caption-to-image mapping is unstable; no direct transfer. |
| Figure 7, calibration variant | H | Historical fitted analysis only. |
| Figure 7, pangenome variant | X | Non-independent silver-truth claim. |
| Figure 8 | H/X | Caption-to-image mapping is unstable; no direct transfer. |
| Figure 9 | H/X | Caption-to-image mapping is unstable; external-cohort material is excluded. |
| Figure 10, NCI-60 variant | X | Unsupported external-validation framing. |
| Figure 10, frozen external arms variant | X | Unsupported external-validation framing. |
| Figure 11, routing diagnostics | X/H | WGS gains excluded; fitted method retained only textually as exploratory provenance. |
| Figure 12 | H/X | Caption-to-image mapping is unstable; no direct transfer. |
| Figure 13 | H/X | Caption-to-image mapping is unstable; no direct transfer. |
| Figure 14, strict WGS routing | X | Invalid WGS evidence. |

## Main-table disposition

| Old table | Code | Disposition |
|---|:---:|---|
| Table 1, callers/modalities/reliability | A/X | Caller roles and resource provenance are in current S6; historical performance-derived reliabilities are not reused. |
| Table 2, cohort design | A/X | Corrected cohort flow is in current S1; historical WGS and denominators are excluded. |
| Table 3, nested-CV accuracy | X | Superseded denominators and WGS/fitted claims. |
| Table 4, discordance | A/X | WES/RNA concepts are covered by current diagnostics; WGS content is excluded. |
| Table 5 | H/X | Numbering/content is unstable in the conversion; no unrepresented evidence-safe content was identified. |
| Table 6, pangenome and external-arm variants | X | Silver-truth and external-validation claims excluded. |
| Table 7, WGS/bimodal/trimodal variants | X | Invalid WGS and superseded multimodal claims. |
| Table 8, external-validation/routing variants | X/H | External validation excluded; fitted-policy definitions remain only in current S7. |
| Table 9, flow/routing variants | R/X | BB7.2 replaced by corrected S9.4; routing claims excluded. |
| Table 10, WGS diagnostic overlays | X | Invalid WGS evidence. |
| Table 11, selective-reporting metrics | X | Post hoc, development-only analysis outside the active benchmark claims. |
| Table 12, RNA external sensitivity | X | External-arm provenance and validation status are insufficient. |

## Supplementary-figure disposition

| Old figure | Code | Disposition |
|---|:---:|---|
| S1, per-gene caller accuracy | A/X | Corrected WES/RNA subgroup results exist; historical WGS values excluded. |
| S2, confidence calibration | H | Historical fitted analysis only. |
| S3, allele-resolution comparison | A/X | Replaced by audited set-valued and G-group sensitivities; old values excluded. |
| S4, abstention trade-off | A/X | Current callability/threshold display supersedes it. |
| S5, discordance categories | A/X | Current missingness, support and error-correlation analyses supersede it. |
| S6, champion–challenger versus vote | X | Superseded fitted/WGS headline claim. |
| S7, legacy FIMM cross-modality concordance | X | Circular fingerprint pairing; replaced by identity-linked S9. |
| S8, FIMM dropout | X | Dropout proxy is not validated LOH evidence. |
| S9, FIMM LOH | X | Non-informative imbalance input and no orthogonal copy-number validation. |
| S10, HED/survival | X | Underpowered, post hoc clinical analysis outside scope. |
| S11, algorithm-family agreement | A | Current fixed-denominator and mutually-callable error-correlation matrix supersedes it. |
| S12, per-gene changes | X/A | Historical fitted/WGS changes excluded; corrected gene strata remain text/table only. |
| S13 | H/X | No stable caption in the converted source; no direct transfer. |
| S14 | H/X | No stable caption in the converted source; no direct transfer. |
| S15 | H/X | No stable caption in the converted source; no direct transfer. |
| S16, base reliability | A/X | Current Table 1/S6 supersede the valid descriptive content; historical weights are not reused. |
| S17 | H/X | No stable caption in the converted source; no direct transfer. |
| S18, selective-accuracy curve | X | Truth-selected, error-enriched exploratory analysis. |
| S19 | H/X | No stable caption in the converted source; no direct transfer. |
| S20 | H/X | No stable caption in the converted source; no direct transfer. |
| S21 | H/X | No stable caption in the converted source; no direct transfer. |
| S22, post hoc routing novelty | X | Post hoc development analysis; not validation. |

## Historical-reference disposition

| Reference in old draft | Code | Disposition |
|---|:---:|---|
| 1000 Genomes Project Consortium (2015) | A | Already retained. |
| Adams et al. (2005) | X | Linked to excluded external/silver-truth material. |
| Aguiar et al. (2019) | R | Added for polymorphism-aware HLA RNA expression and mapping context; primary record verified. |
| Boegel et al. (2012) | R | Added as the primary seq2HLA citation; primary record verified. |
| Chin et al. (2020) | X | Linked to excluded GIAB/pangenome validation. |
| Chung et al. (2004) | A | Already retained. |
| Di Tommaso et al. (2017) | A | Already retained for Nextflow. |
| Gourraud et al. (2014) | A | Already retained as the truth-source citation. |
| Hickey et al. (2024) | X | Linked to excluded pangenome silver-truth work. |
| Hurley et al. (2020) | X | No active CIWD-frequency analysis. |
| Johansson et al. (2022) | X | Not needed after adding the primary Aguiar RNA-expression source. |
| Kiyotani et al. (2017) | A | Already retained. |
| Lee and Kingsford (2018) | R | Added as the primary Kourami citation; publisher record verified. |
| Liao et al. (2023) | X | Linked to excluded pangenome silver-truth work. |
| Llamas et al. (2019) | X | Historical GIAB truth attribution was unresolved and is outside scope. |
| Mallal et al. (2008) | A | Already retained. |
| Matzaraki et al. (2017) | A | Already retained. |
| Mishima et al. (2019) | H | Not added; the active manuscript already cites the primary HLA-HD method paper. |
| Orenbuch et al. (2019/2020) | A | Already retained with the journal-year convention used by the active reference list. |
| Parham and Brodsky (1981) | R | Added as the primary BB7.2 citation; PubMed record verified. |
| Petersdorf et al. (2007) | A | Already retained. |
| Prodanov et al. (2025) | X | Linked to excluded pangenome silver-truth work. |
| Reinhold et al. (2019) | X | Linked to excluded NCI-60 validation. |
| Robinson et al. (2020) | A | Already retained. |
| Schumacher and Schreiber (2015) | A | Already retained. |
| Shukla et al. (2015) | A | Already retained. |
| Song et al. (2023) | A | Already retained. |
| Szolek et al. (2014) | A | Already retained. |
| Trowsdale and Knight (2013) | A | Already retained. |
| Wang et al. (2023) | A | Already retained. |
| Zhou et al. (2024) | X | Linked to excluded pangenome annotation work. |

## Verified added references

- Aguiar VRC et al. *PLoS Genetics* 15:e1008091 (2019), DOI `10.1371/journal.pgen.1008091`.
- Boegel S et al. *Genome Medicine* 4:102 (2012), DOI `10.1186/gm403`.
- Lee H, Kingsford C. *Genome Biology* 19:16 (2018), DOI `10.1186/s13059-018-1388-2`.
- Parham P, Brodsky FM. *Human Immunology* 3:277–299 (1981), DOI `10.1016/0198-8859(81)90065-3`.

## Acceptance boundary

The transfer is complete only if the active manuscript contains no restored WGS performance, external-validation, clinical-utility, state-of-the-art or end-to-end reproducibility claim; all provisional metadata remains visibly unconfirmed; claim audits report no scientific blocking failure; and the readiness state remains blocked on author/archive and FIMM governance inputs.
