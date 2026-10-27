# ChampHLA manuscript review for Scientific Reports

Date: 19 October 2026  
Target: *Scientific Reports*, Article  
Review state: editorially revised submission candidate; not cleared for submission

## Verdict

The manuscript has a defensible and unusually transparent scientific core. Its strongest contribution is not a new inference algorithm but a fail-closed way to evaluate multi-caller HLA genotyping without hiding failed calls, ambiguous reference typing or incomplete provenance. The earlier draft obscured that contribution through BMC-specific structure, repeated caveats, method-heavy sequencing and an internal revision memo. The previous Nature-standard rewrite corrected much of the prose, but it remained formatted for BMC Bioinformatics and was based on a slightly older repository state.

The Scientific Reports version now uses an unstructured abstract, Introduction–Results–Discussion–Methods order, separate Data and Code availability statements, ethics inside Methods and separate Supplementary Information. The central narrative is clearer: the vote could not be distinguished from the strongest caller on the historical development data; fitted rules did not improve it; and most apparent shared errors lie at loci where a published re-typing supports the vote. That final interpretation remains explicitly post hoc and non-independent.

The manuscript must not yet be submitted. The v3.5.x rerun is still pending, and author metadata, repository release identifiers and FIMM/VenEx governance fields remain unresolved.

## Source reconciliation

| Source | Use in this revision | Authority |
|---|---|---|
| Current canonical repository at `2b9929a` | Scientific state, evidence slots, registry, decisions and tests | Primary |
| Earlier `manuscript-rewrite` worktree | Sentence craft, architecture and RW-001–RW-032 fixes | Secondary; prose only |
| `ChampHLA_Manuscript_v3.docx` | Layout and document-level comparison | Tertiary |
| Historical manuscripts and Drive summaries | Provenance only | Never used to restore results |

The registry and signed decisions override all prose. No sealed holdout, immutable preregistration snapshot or patient-level FIMM/VenEx file was inspected.

## Scientific Reports compliance findings

| ID | Severity | Finding | Resolution |
|---|---|---|---|
| SRP-001 | Structural | The abstract was BMC-structured and exceeded the Scientific Reports 200-word recommendation. | Rewritten as an unstructured 179-word abstract without citations or performance estimates. |
| SRP-002 | Structural | Methods preceded Results, and a standalone Conclusions section duplicated the Discussion. | Reordered to Introduction, Results, Discussion, Methods; the conclusion is now the final Discussion paragraph. |
| SRP-003 | Major | Data and code availability were combined under a BMC heading. | Split into separate Data availability and Code availability sections before References. |
| SRP-004 | Major | Human-participant ethics appeared only in Declarations. | Moved the public-data and controlled-cohort ethics/consent text into Methods. Unresolved identifiers remain explicit. |
| SRP-005 | Major | Reference numbers no longer followed order of first citation after Methods moved. | Renumbered the manuscript, supplement and 54-entry reference list together. |
| SRP-006 | Minor | Eight keywords exceeded the journal's allowance of six. | Reduced to six indexing phrases. |
| SRP-007 | Minor | “Additional file 1” and other BMC-specific labels remained. | Replaced with a separate Supplementary Information statement and removed BMC-only headings. |
| SRP-008 | Minor | Main-text length risked exceeding the 4,500-word recommendation. | Introduction + Results + Discussion are 4,398 words after excluding table bodies and provenance tags. |
| SRP-009 | Major | The abstract could be accidentally populated with provisional rerun values. | Kept performance values out while `abstract_numeric_performance_allowed=false`; added an automated check. |
| SRP-010 | Blocking | FIMM/VenEx ethics, governance and source-provenance details are incomplete. | Retained the analyses only with explicit submission blockers and no clinical-utility claim. |

## Reconciliation of RW-001–RW-032

| Earlier finding | Status in Scientific Reports version |
|---|---|
| RW-001 title describes process, not study | Addressed with the 13-word fail-closed benchmark title; it avoids the post hoc reference-error interpretation. |
| RW-002 thesis buried | Addressed; primary comparison, fitted policies and reference adjudication now drive Results. |
| RW-003 Methods archaeology | Addressed; diagnostic history is summarized and detailed in Supplementary S10. |
| RW-004 descriptive Results headings | Addressed with declarative headings. |
| RW-005 Discussion restates Results | Addressed; the opening interprets why the vote gains little. |
| RW-006 Conclusions repeat Abstract | Addressed; no standalone Conclusions section remains. |
| RW-007 protocol history duplicates supplement | Addressed; main text is condensed and S7 carries the ledger. |
| RW-008 Abstract stronger than body | Addressed; the re-typing claim is explicitly post hoc and non-independent. |
| RW-009 Abstract Results was a procedural list | Addressed by a single narrative abstract. |
| RW-010 NA19130 explanation misattached | Addressed in the earlier rewrite and retained. |
| RW-011 interval-method mapping ambiguous | Addressed with direct method-to-result wording. |
| RW-012 cluster-t caveat opaque | Addressed in plain language; the exact sign-flip test governs significance. |
| RW-013 Figure 4 legend contradictory | Addressed; fixed-denominator and mutually callable triangles are distinguished. |
| RW-014 caller list too dense | Addressed by grouping evidence types and using Table 1. |
| RW-015 caveats repeated | Substantially addressed; caveats are concentrated in Methods and Limitations prose. |
| RW-016 final Introduction paragraph mixed jobs | Addressed; it ends on the question and reason for the untrained rule. |
| RW-017 fitted-policy orphan paragraph | Addressed by integration with the primary comparison. |
| RW-018 figure-design detail in Results | Removed from Results and retained in the legend. |
| RW-019 reference-typing paragraph too long | Split into source limitations, adjudication and denominator construction. |
| RW-020 call-state paragraph too long | Split into taxonomy and singleton semantics. |
| RW-021 limitations mixed threats | Addressed with design, reference, panel/provenance and statistics run-ins. |
| RW-022 unused HED abbreviation | Removed. |
| RW-023 stray backticks | Corrected. |
| RW-024 redundant intended-use gloss | Removed. |
| RW-025 keywords omit method | Addressed; consensus genotyping and benchmarking are retained among six keywords. |
| RW-026 checksum repeated | Kept in Data availability and referenced from Methods. |
| RW-027 clumsy selection sentence | Rewritten. |
| RW-028 CSC defined in wrong place | Addressed in the software/audit text. |
| RW-029 long sentences | Substantially reduced; remaining long sentences carry technical definitions or fixed disclosures. |
| RW-030 terminology drift | Reader-facing prose uses “reference typing”; “truth” remains only in established pipeline objects and artifact names. |
| RW-031 mixed number formats | Standardized in narrative while leaving generated tables unchanged. |
| RW-032 legends open with encoding | Addressed; legends begin with the scientific content. |

## Remaining scientific and submission blockers

| Blocker | Owner | Required resolution |
|---|---|---|
| v3.5.x development rerun and registry refresh | Analysis/release process | Complete the frozen rerun, approve the registry and update only tag-dependent sentences. |
| Final author list, order, affiliations and ORCIDs | All authors | Confirm every title-page field. |
| Corresponding author contact information | Corresponding authors | Supply postal address and email. |
| CRediT statement | All authors | Confirm contributions by initials. |
| Public-data ethics determination | Host institution/authors | Supply approval, exemption or not-applicable wording. |
| FIMM/VenEx governance | Cohort custodians/authors | Supply committees, identifiers, dates, demographics, criteria and consent/biobank basis. |
| Secure FIMM source provenance | Authorized analyst | Freeze and report aggregate-safe hashes and schema provenance only. |
| Funding and funder role | Authors | Confirm grant, recipient, other support and funder role. |
| Competing interests | Every author | Confirm the provisional statement. |
| Repository release metadata | Release owner | Supply final tag, commit and archival DOIs. |
| Historical caller identifiers | Authors/workflow maintainers | Supply recoverable digests and label genuinely unavailable identifiers. |

## Editorial recommendation

After the blockers are resolved and the final rerun-dependent sentences are regenerated, the manuscript should receive one independent HLA-specialist read and one non-specialist methods read. The paper is suitable for editorial consideration as a transparent computational benchmark, but the submission should foreground technical validity and auditability rather than novelty or clinical impact.
