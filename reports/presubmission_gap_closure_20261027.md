# Presubmission gap closure — 27 October 2026

| Item | Owner | Status | Evidence |
|---|---|---|---|
| Science: adopted v7 and unchanged negative headline | Umut / authors | closed | D1; v7 `1ed1f94`; title and concluding prose unchanged in this pass. |
| Science: SR-004 quality filtering and sensitivity reporting | Manuscript/workflow maintainers | closed | Existing v3.5.0 parser `66d949d`, fix `e1ea6c9`; one explicit Methods sentence; existing S2 native-homozygote/abstain-all sensitivity; both review TSVs synchronized. |
| Science: SR-025 evaluation framing | Manuscript maintainers | closed | Already addressed in v7; no conclusion or title edit; `reports/scientific_review_20261012.tsv`. |
| Science: D2 failure classification | Umut | closed | Earlier completed `CLASSIFIED HG01052 wes 2560328 input_transfer`, confirmed again by Umut; not repeated in this pass. |
| Science: NCI-60 full roster and S9.6 | Existing run / Umut | waits on runs | Read-only squeue/sacct check described below; D4 waits for results. Under-way sentences and S9.6 unchanged. |
| Science: confirmatory extension result / SR-006 | Umut / existing run plan | waits on runs | Extension is stopped; agent must never relaunch it. Completion, collection and the separately protected evaluation remain outstanding. |
| Science: extension relaunch decision after NCI-60 exit 10 | Umut | needs Umut | Later instruction overrides the old conditional permission. Report completion and ask Umut; no classify/control or launch command is authorized here. |
| Science: public extension pre-registration deposit | Umut | needs Umut | D5; reserved DOI 10.5281/zenodo.23251288 is not a published deposit. |
| Science: reference comparison on extension predictions | Umut | needs Umut | Remains separately protected; no truth join was performed or authorized by this pass. |
| Science: numeric abstract / SR-027 | Authors after extension | waits on runs | SR-027 remains open; no provisional performance values added. |
| Release: clean workflow refs and release archive checksum | Release lead | closed | Remote v3.5.0 resolves to `66d949d`; local git archive checksum matches the Roihu SHA256SUMS entry. |
| Release: bounded pushed-history sensitive-content scan | Release lead | closed | No targeted pattern hits in the union of pushed refs; audit states scope and limitations. Historical path-prefix metadata still needs an owner review before visibility changes. |
| Release: old PanelHLA Support request | Umut | closed | Umut confirms repository deletion on 27 October 2026; request unnecessary. No old history/API was accessed. |
| Release: root-prompt exclusion implementation | Paper maintainer | closed | Authorized `:(glob)*_PROMPT.md` addition to HOLD_BACK; controlled-data exclusions and scan patterns unchanged. The final committed build and tree proof are delivered separately. |
| Release: mixed cohort files and embedded figures | Umut / custodians | needs Umut | `reports/public_release_readiness_20261027.md`; withholding standalone S6–S8 images does not remove their embedded Word copies or mixed aggregate sources. |
| Release: five internal-document recommendations | Umut | needs Umut | Keep/hold-back table in release audit; none of those five files was newly held back. |
| Release: third-party resources, attribution and legacy binaries | Umut / workflow owner | needs Umut | Licence and binary inventory in release audit; top-level MIT does not clear caller images, database resources or legacy source documents. |
| Release: approval of the built snapshot and any push | Umut | needs Umut | Build only, without --push. Approval is required for the exact built snapshot before a push; no development branch may be pushed. |
| Release: visibility, final tags and archival DOIs | Umut / release lead | waits on release | No visibility change, tag, release or deposit performed. Actual archive identifiers must be supplied before submission. |
| Authors: names, affiliations, ORCIDs, CRediT, interests and approval | Every author | needs co-authors | Recipient section in `reports/AUTHOR_REQUEST_20261027.md`; provisional values remain visibly provisional. |
| Authors: contacts, reviewers, prior editorial discussions and submission declarations | Corresponding authors | needs co-authors | Author packet and placeholder-preserving cover-letter draft; no reviewer or contact details inferred. |
| Authors: support, grant recipient and funder role | Funding holder | needs co-authors | Provisional funding source retained as a request for confirmation, not a final declaration. |
| Ethics: FIMM governance and secure source provenance | FIMM custodian | needs co-authors | Committee/permit, biobank basis, collection period, demographics, inclusion/exclusion, publication permission and secure manifest/crosswalk checks; export hashes/schema only. |
| Ethics: equivalent VenEx governance | VenEx data owner | needs co-authors | Equivalent author-packet fields; no patient files or identifiers requested for export. |
| Ethics/declarations: public-data determination, CSC acknowledgement and LLM disclosure | Umut | needs Umut | Author packet; approved wording and placement remain outstanding. |
| Loose ends: tracking documents and cover-letter alignment | Manuscript maintainer | closed | README, submission/author checklists, coauthor checklist, RECOVERY_STATUS and current cover letter reconciled. |
| Loose ends: supported accessible full-text citation passages | Citation reviewer | closed | Trowsdale, Mallal, Matzaraki and Aguiar checks recorded with short source quotations and links. |
| Loose ends: three remaining full-text checks and neoantigen wording | Authors with lawful access | needs co-authors | Chung 2004, Schumacher & Schreiber 2015 and Lappalainen 2013 are explicitly “unverified: no full-text access”; proposed wording recorded but not applied. |
| Loose ends: grouped author request packet | Umut to review/forward | closed | Draft prepared and saved after the gate, never sent; every recipient has a separate section. |
| Loose ends: scientific-preservation, tests and Word review | Manuscript maintainer | closed | Verification evidence below; scientific gate status remains author_input_required. |

This report follows Umut's reconciled instructions, which override stale text in the root prompt and vault. It records completed local work; it does not make unresolved author fields or pending analyses complete. The vault was left unchanged for Claude, as requested.

## Changes and editorial evidence

### SR-025 — already addressed

The historical finding quoted a concluding lead about a “benchmark of six … callers”. That text is absent from adopted v7. The current conclusion begins:

> ChampHLA-Consensus is an auditable development baseline.

Before and after this pass are identical. The concluding paragraph retains the negative comparison, retrospective limits and need for independent validation. The title is unchanged. SR-025 is marked fixed in both the scientific-review TSV and the closure master, with v7 `1ed1f94` as evidence.

### SR-004 — historical finding superseded by the existing release

The old finding describes a wrapper without T1K quality filtering. The v3.5.0 source already retains alleles only when quality is positive, validates the native schema, separates declared homozygosity from partial calls and does not promote secondary alleles. No parser file was edited and no caller execution was repeated. The existing S2 singleton table already contains T1K native-declaration versus abstain-all sensitivity. Historical unconditional-completion estimates were not imported.

Before:

> The rerun T1K parser records `num_diff_alleles` and quality fields distinguishing native homozygotes from missing alleles. We complete T1K's declared homozygotes; other single-allele rows abstain.

After:

> The rerun T1K parser records `num_diff_alleles` and quality fields distinguishing native homozygotes from missing alleles. It ignores alleles with non-positive quality and does not promote secondary alleles into the genotype. We complete T1K's declared homozygotes; other single-allele rows abstain.

The short added sentence has no numeric values. SR-004 is fixed for the active deployment after this explicit Methods statement, as Umut instructed. The parser fix and prior completed rerun are existing evidence, not work newly performed here.

### Tracking and cover-letter changes

- Replaced the stale “no extension input has been staged” README paragraph with the signed-amendment/current-priority state, completed D2 classification and the requirement for Umut to approve any future extension action.
- Replaced the README statement that NCI-60 is not being regenerated with the completed-pilot/full-roster-in-progress state. No NCI-60 result was added.
- Updated the submission checklist for adopted v7/IMRAD, current automated length checks, the location of provisional declarations, pending NCI-60, signed amendment, unpublished deposit and private snapshot-based release.
- Ticked the already signed amended pre-registration with `04cc6d1`; added the still-open public Zenodo deposit and mixed-file/snapshot approval decisions.
- Reconciled RECOVERY_STATUS with a new current-status note while retaining its explicitly historical entries. Updated the coauthor checklist's old figure location and description of where provisional fields are held.
- Updated the cover-letter title and current retrospective-rerun scope; retained all placeholders and converted unconfirmed not-submitted-elsewhere/accountability/LLM statements into explicit author-confirmation requests.
- Recorded the old PanelHLA repository deletion and removed the need for a Support request in current tracking notes. No old-repository lookup or remote modification was performed.

## Citation checks

`CITATIONS_TO_VERIFY.md` inventories every current cited sentence for the seven requested sources. It separates checked full-text passages from abstract/summary-only evidence. Four sources have accessible full-text support. Three remain **unverified: no full-text access**. No paid service is required, and no unavailable full text is described as checked.

The clinical association wording in Mallal is read as prediction of susceptibility, not certainty. The Schumacher & Schreiber citation does not yet have verified full-text support for the typing-error/therapy-design consequence; a narrower proposed sentence is recorded for the authors, without editing the manuscript. Reference entries, numbering and citation-bearing scientific prose were left unchanged.

## Roihu status and boundaries

At **2026-10-27 11:21:28 +02:00**, read-only squeue and sacct showed NCI-60 controller **2566221 RUNNING**, with elapsed time **06:04:20**. The batch and extern records were also RUNNING. The running record's `0:0` field is not evidence of roster completion. The extension remains stopped. D2 was completed earlier (`CLASSIFIED HG01052 wes 2560328 input_transfer`) and was not repeated. No classify/control, sbatch, scancel, sample-job intervention, relaunch, manual staging or reference comparison was performed in this pass. If a later read-only check reports NCI-60 exit 10, report it and ask Umut; the agent never relaunches the extension.

## Release audit and snapshot scope

The detailed audit is `reports/public_release_readiness_20261027.md`. It includes the existing snapshot inventory, mixed source and binary copies, expected hold-back coverage, the five requested document recommendations, large objects, licence/credit gaps, workflow tag/archive checks, bounded full-pushed-history scan and an ordered owner-specific release procedure.

Only the author-approved `:(glob)*_PROMPT.md` pathspec was added to HOLD_BACK, with the comment “internal AI working instructions, not paper material”. No controlled-data exclusion or pattern was weakened. The five reviewed internal documents remain in the candidate tree pending the author's decision. The original untracked instruction prompts remain unstaged.

The final local commit and built snapshot identifiers, parent relationship, file inventory and zero-prompt proof are reported with the no-push build, outside this self-referencing report. The snapshot must be shown to Umut and approved before any push. No development branch, workflow branch, tag or release was pushed.

## Verification

- Focused tests: **95 passed**; source/DOCX text and figure parity passed for both standard review drafts.
- Full gate: **545 passed, 3 skipped, 14 warnings in 94.14s (0:01:34)**; lint passed, bootstrap iterations 100,000, power iterations 2,000. Status `author_input_required` with no scientific failures. No caller execution or extension/NCI-60 reference comparison was performed.
- Registry SHA-256 remains `6fd741d6e4427ef84268cd6b114df098ac982370262ba448e0bd185ca0be9f2a`. The multiset of **175 tags** is identical to the session baseline. All source numeric tokens, generated blocks, title, reference entries and concluding prose are unchanged apart from the explicitly authorized non-numeric Methods sentence.
- Main narrative remains **4,011 words**, excluding Methods/tables/tags; abstract **180 words**. The protected extension implementation and fitted.py are unchanged. No test was weakened.
- Combined review PDF: **79 pages**, no detected text-boundary overflow. All six changed page bodies were visually inspected; 73 bodies match the previously reviewed v7 copy. Native equations, pseudocode and table layouts remain readable.
- Word SHA-256: `d6b8628dd8444c8fc21a42245d33c74fe9586b773276f260cc8bcab51c7b85f8`. The tracked combined Word file matches this local review copy.
- PDF SHA-256: `5b4db351fc35c697ac984280f56da0899f48e89c5845d52844013510c60cf90f`.
- Detailed machine-readable checks: `reports/presubmission_checks_20261027.json`. Local logs and rendered proof: `D:/panelhla_work/presubmission_gaps_20261027/`, including `focused_tests.log`, `full_gate.log`, `review_build.log` and `qa_review/qa.json`.
- The full gate completed before the author packet and closure report were written, as requested. These post-gate additions are administrative documentation; no scientific source or analysis was changed after that run.


## Notes for Claude to reconcile in the vault

The vault was not edited. Its next update should record adopted v7/current project history, completed D2, no further classify/control action, no agent extension relaunch, old PanelHLA repository deletion, the citation-access distinction, the final local commit and unpushed snapshot proof, and the remaining author/governance/run/release decisions. Umut's latest instructions supersede the older conditional relaunch and immediate-push wording.

## Shortest ordered path to submission

1. Umut reviews this closure report, the unsent author packet and built snapshot; obtains the author/custodian answers and resolves the mixed-file/permission decisions. Only then approve the exact snapshot for any push; visibility changes remain a separate owner action.
2. Wait for NCI-60 completion; report its exit status to Umut and obtain instructions. Umut decides the extension restart. Complete the remaining runs and collections under their existing plans without anticipating results.
3. Umut publishes the extension pre-registration and satisfies its remaining prediction-freeze/release requirements before any separately authorized one-time reference comparison. Incorporate only the resulting authorized, registered evidence; revisit SR-027 afterward.
4. Complete the three full-text citation checks, final declarations and resource credits/permissions. Approve the final main text, supplement, figures and cover letter with all authors.
5. Follow the release audit's ordered visibility/tag/archive/DOI/digest procedure, then rebuild and run the full README release command with --submission. Submit only after its requirements and author approvals are satisfied.
