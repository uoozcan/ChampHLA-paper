# Public-release readiness audit — 27 October 2026

Scope: read-only audit of the paper snapshot and the pushed workflow refs. No repository visibility, tag, release, remote history or GitHub content was changed. The only publisher-policy change in this pass is Umut's explicit root-prompt exclusion; the controlled-data paths and scan patterns are unchanged. This audit is not approval to publish controlled-cohort aggregates.

## Paper: contents and completeness of the hold-back

The inspected existing `public-snapshot` is `48aefe2d51ce59075e000ecf7e30d9c5bdaef303`, built from development commit `dc78ecf`. It contains the paper sources and Word copies; public-development inputs and result artifacts; code, tests and synthetic fixtures; public subject/cohort manifests; decisions and provenance; figures except S6–S8; reference-resource files; and internal review/tracking documents. An inventory of the prospective tree must accompany the final no-push build. Development commits never become snapshot parents.

The existing snapshot omits the dedicated `artifacts/fimm`, `artifacts/fimm_consensus` and `artifacts/venex` directories, standalone S6–S8 figure files and `reports/pre_submission_review_20261008.tsv`. That confirms the named hold-back paths are applied. It does **not** establish a complete embargo of cohort content: mixed sources, histories, documents and embedded figures remain. In particular, excluding standalone images does not remove their copies embedded in Word documents.

### Mixed content requiring an author decision before public visibility

| Files or exact path family | Content and required decision |
|---|---|
| `result_registry.tsv` | Mixed public-development and FIMM/VenEx aggregate result records. Decide whether the aggregate rows are cleared for public release. Do not drop rows or change the scientific registry in this pass. |
| `manuscripts/benchmark/manuscript.md`, `manuscripts/benchmark/supplementary.md`, `manuscripts/claim_audit.tsv` | Main-text cohort scope and supplementary aggregate results/claims. Governance approval or an explicitly approved alternative package is needed before public visibility. |
| `manuscripts/benchmark/ChampHLA_manuscript_COMBINED_DRIVE.docx`, `ChampHLA_manuscript_REVIEW_DRAFT.docx`, `ChampHLA_supplementary_REVIEW_DRAFT.docx` in the same directory | Reader copies embed cohort prose/tables; the combined and supplementary copies also carry the held-back cohort figures. These are mixed binaries despite their neutral filenames. |
| `manuscripts/historical/benchmark_manuscript_pre_remediation_20260924.md`, `benchmark_supplement_pre_remediation_20260924.md`, `claim_audit_pre_remediation_20260924.tsv` in the same directory | Superseded mixed scientific claims remain in the snapshot. Recommend holding historical draft material out of the eventual public scientific package, subject to author approval. No source was edited. |
| `provenance/development_rerun_v350/historical_result_registry_pre_v350.tsv`, `result_registry_delta.tsv` in that directory, and the corresponding files under `provenance/development_rerun_v350_superseded_20261025/` | Historical mixed-registry rows and comparisons can retain cohort aggregates even when dedicated cohort folders are withheld. Governance review must include these immutable copies; do not rewrite them. |
| Review narratives and review/closure TSVs listed in the inventory below | Some repeat cohort counts, interpretation, pending governance and prior manuscript claims. Decide on their publication as a group after checking each candidate. A cohort-name match alone is not evidence of patient-level content. |
| `manuscripts/benchmark/PanelHLA_Manuscript_v2.docx`, `manuscripts/source_original/ChatGPT_Bioinformatics_ChampHLA_Manuscript_V5x_reviewfix.docx`, `manuscripts/source_original/source_text.txt`, `manuscripts/source_original/issue_register.tsv` | Legacy/source material remains in the snapshot. The protected original sources were not opened for this audit. They cannot be certified from a filename or a binary-skipping text scan. Recommend hold-back pending an authorized owner review. |
| `figures/figure_manifest.json`, `artifacts/release_freeze.json`, benchmark claim audits and `artifacts/publication_readiness_gate.json` | Mixed provenance/governance metadata includes references to held-back artifacts. Retain traceability only with an accurate explanation of omissions; the old release-freeze record is not proof that the new snapshot is a complete validated release bundle. |

The complete cohort-mention inventory below is deliberately conservative: it also lists code, synthetic fixtures and public-development files whose source path merely mentions a cohort. Those are not automatically clinical data. Dedicated controlled patient files, crosswalks and old contaminated development-history commits were not opened. No assertion of a complete sensitive-data clearance is made for uninspected binaries or protected historical sources.

### Requested keep/hold-back recommendations — recommendations only

| File | Recommendation for eventual public tree | Reason |
|---|---|---|
| `AUTHOR_FIELDS_TO_COMPLETE.md` | **Hold back** | Internal provisional authorship, funding and governance collection; publish confirmed declarations in the manuscript instead. |
| `AUTHOR_REQUEST_20261008.md` | **Hold back** | Superseded internal request, old venue wording and a historical Sent label; unnecessary for reproducing the paper. |
| `COAUTHOR_REVIEW_CHECKLIST.md` | **Hold back** | Internal approval workflow and cohort review requests. |
| `CITATIONS_TO_VERIFY.md` | **Keep**, clearly marked as a verification record | Provides source links, supported claims and explicit unverified items. Preserve the distinction between abstract support and full-text verification. |
| `RECOVERY_STATUS.md` | **Hold back** | Long internal recovery history with superseded results and operating instructions; the current README and final closure report are clearer public entry points. |

None of these five files was newly held back. The new author request packet is likewise an internal draft; recommend author review of its inclusion before public visibility. No email was sent.

### Root prompts and other private working instructions

Umut authorized `':(glob)*_PROMPT.md'` in HOLD_BACK with the comment “internal AI working instructions, not paper material”. The final committed snapshot will be built **without `--push`** and its full file list checked for prompt files, `.ai-vault/`, `AGENTS.md`, `CLAUDE.md` and `.claude/settings.local.json`. The exclusion removes prompt files from the new tree; earlier snapshot commits retain their prior trees, since no history rewrite is authorized.

Existing tracked root prompt files to omit:

- `FINAL_PUBLICATION_REVIEW_PROMPT.md`
- `MANUSCRIPT_REMEDIATION_PROMPT.md`
- `PRE_SUBMISSION_REVIEW_PROMPT.md`
- `SCIENTIFIC_REVIEW_PROMPT.md`

The current untracked instruction prompts must remain untracked and unstaged. The new pattern does not authorize any relaxation of the controlled-data scan.

## Workflow: tag, archive and pushed-history scan

- Remote v3.5.0 tag object: `c07fc95ad3103bdfda18b45664587aef2fa3d380`; peeled release commit: `66d949da90861da6cf60cf1d4bee2f094f2518bd`. The freshly read remote refs agree with the refs used for the scan.
- SHA-256 of `git archive --format=tar.gz --prefix=PanelHLA-3.5.0/ v3.5.0`: `22d9ed3bd808aec7364fbe869ad048c561be38bd02479dff530fe13fee4da7ed`. It exactly matches the Roihu `PanelHLA-3.5.0.tar.gz` entry in `champhla_publication_remediation/SHA256SUMS` read earlier in this session. No deployment file was changed.
- The union of remote `main`, `release-3.5.1`, `champhla-rename` and tags v3.3.0–v3.5.0 covers **90 commits and 725 unique blobs**. The scan found no targeted controlled-subject identifier, private-key, GitHub-token or AWS-access-key patterns. This is a bounded pattern scan, not a guarantee that every possible secret or identifier is absent. The purged commit is not reachable from those refs. Old remotes and backups were not traversed.
- Historical `bin/create_fimm_pseudo_ids.py` has no targeted identifier matches, but retains secure cluster path strings and ID-prefix conventions. Recommend leaving the clean existing history unchanged in this pass; keep the script absent from the current tree and have Umut assess its metadata before public visibility. Removing old objects would require a separately authorized history policy; none was attempted.
- The old PanelHLA workflow repository was deleted on 27 October 2026, as confirmed by Umut. No GitHub Support purge request remains. No old-repository API or historical controlled-data lookup was performed here.

## Licences and third-party notices

Both current repositories have a top-level MIT licence and THIRD_PARTY_NOTICES.md. That licence covers the project code, not every caller image, reference database or donor resource.

- Existing notices distinguish POLYSOLVER source terms from the academic/non-profit restrictions of the bundled image and Novoalign. Keep that distinction; the project's MIT licence does not grant commercial rights to those dependencies.
- HLA-HD is obtained under upstream academic/non-commercial terms without a redistribution grant. Confirm the release contains build instructions rather than a redistributed caller image. T1K/seq2HLA notice evidence is upstream rather than in-container; retain those source links.
- `resources/ipd_imgt_hla/3.65.0/LICENCE.md` is present. It states Attribution–NoDerivs terms, requests specific citations, discourages mirroring and requires permission for modified data. Its requested credits include newer database publications than the manuscript's current database citation. Umut must review the packaged resource files and credit/redistribution requirements before public release; this pass does not alter the protected resources or references.
- Copied caller-native headers/allele lists under `resources/caller_native/` require a resource-by-resource source, licence and attribution record; top-level MIT is insufficient. Confirm any transformed lists are covered by the relevant permission. No caller image or third-party binary redistribution was approved by this audit.
- Public sequencing inputs retain source-consortium terms. Controlled FIMM/VenEx governance is a separate requirement. Do not imply that public-code licensing clears clinical cohort data.
- Legacy DOCX and copied reports need owner approval for public inclusion. Their presence in a private snapshot is not licence or privacy clearance.

## Ordered release procedure

| Step | Owner | Prerequisite and what it blocks |
|---|---|---|
| 1. Confirm FIMM/VenEx governance or approve an explicit mixed-file publication decision | Umut and the data custodians | Required before changing visibility or publishing cohort-bearing material. Review the mixed sources, binary copies and historical records above. |
| 2. Approve the built snapshot; then authorize its push and make ChampHLA/ChampHLA-paper public | Umut | Snapshot build and scan evidence first. This session stops before push or visibility changes. |
| 3. Select final commits and create final release tags | Umut/release lead | After final scientific and author review. Existing v3.5.0 remains the evaluated workflow release. No tag invented or created here. |
| 4. Archive through the Zenodo–GitHub integration | Umut/release lead | Approved immutable tags and visibility/access arrangements. The separate extension pre-registration deposit is still Umut's task. |
| 5. Insert assigned DOIs into Data/Code availability, references 56–57 and CITATION.cff | Authors/release lead | Actual archive records, not reserved or invented identifiers. Rebuild and recheck citations afterward. |
| 6. Recover externally controlled caller-container digests, or explicitly mark unavailable historical identifiers | Workflow owner and Umut | Reproducible release metadata. Do not reconstruct missing historical versions by assumption. |
| 7. Run the README release command with `--submission` | Release lead | Completed analyses, author/governance fields, reference checks and release metadata. No reduced resampling or skipped checks. |

## Large existing snapshot objects (at least 1 MiB)

These are an inventory, not newly added downloads. No object in this list approaches GitHub's single-file hard limit; cumulative repeated binary versions still inflate history. Confirm which legacy copies belong in an eventual public package. Protected originals were not opened.

| Path | Bytes |
|---|---:|
| `manuscripts/source_original/ChatGPT_Bioinformatics_ChampHLA_Manuscript_V5x_reviewfix.docx` | 8340162 |
| `manuscripts/benchmark/ChampHLA_manuscript_COMBINED_DRIVE.docx` | 3604525 |
| `provenance/compute_smoke/raw/dna/pipeline_info/execution_report.html` | 2993131 |
| `provenance/compute_smoke/raw/rna/pipeline_info/execution_report.html` | 2958036 |
| `manuscripts/benchmark/PanelHLA_Manuscript_v2.docx` | 2603543 |
| `resources/caller_native/components/t1k__dna_seq.headers` | 2301440 |
| `figures/figure1_study_design_truth_flow.tiff` | 2168818 |
| `cohorts/official_1000g_assay_manifest.tsv` | 1992756 |
| `manuscripts/benchmark/ChampHLA_manuscript_REVIEW_DRAFT.docx` | 1879384 |
| `manuscripts/benchmark/ChampHLA_supplementary_REVIEW_DRAFT.docx` | 1672326 |
| `provenance/development_rerun_v350/truth_free_collection/sensitivity_abstain/normalized_caller_calls.tsv` | 1277337 |
| `provenance/development_rerun_v350_superseded_20261025/truth_free_collection/sensitivity_abstain/normalized_caller_calls.tsv` | 1273058 |
| `provenance/development_rerun_v350/truth_free_collection/normalized_caller_calls.tsv` | 1272215 |
| `provenance/development_rerun_v350_superseded_20261025/truth_free_collection/normalized_caller_calls.tsv` | 1271088 |
| `figures/figure4_caller_error_dependence.tiff` | 1245972 |
| `data/development/sensitivity_abstain/normalized_caller_calls.tsv` | 1235451 |
| `data/development/normalized_caller_calls.tsv` | 1230329 |
| `figures/supplementary_figure_s5_champion_challenger.tiff` | 1100686 |
| `provenance/development_rerun_v350/historical_inputs_pre_v350/normalized_caller_calls.tsv` | 1093986 |
| `provenance/development_rerun_v350_superseded_20261025/historical_inputs_pre_v350/normalized_caller_calls.tsv` | 1093986 |
| `provenance/development_rerun_v350/historical_inputs_pre_v350/sensitivity_abstain/normalized_caller_calls.tsv` | 1092626 |
| `provenance/development_rerun_v350_superseded_20261025/historical_inputs_pre_v350/sensitivity_abstain/normalized_caller_calls.tsv` | 1092626 |
| `figures/figure2_primary_performance.tiff` | 1075198 |

## Complete cohort-mention file inventory in the existing snapshot

Files below contain a cohort name or agreement term; a match is not itself an aggregate-data or patient-data finding. Use the mixed-content assessment above and owner review rather than automatically publishing or excluding a file based on its name.

- `.gitignore`
- `AUTHOR_FIELDS_TO_COMPLETE.md`
- `AUTHOR_REQUEST_20261008.md`
- `COAUTHOR_REVIEW_CHECKLIST.md`
- `FINAL_PUBLICATION_REVIEW_PROMPT.md`
- `PRE_SUBMISSION_REVIEW_PROMPT.md`
- `README.md`
- `SCIENTIFIC_REVIEW_PROMPT.md`
- `artifacts/benchmark_manuscript_audit.json`
- `artifacts/benchmark_supplementary_audit.json`
- `artifacts/publication_readiness_gate.json`
- `artifacts/release_freeze.json`
- `cohorts/official_1000g_assay_manifest.tsv`
- `configs/dataset_roles.json`
- `configs/fimm_analysis_manifest.template.json`
- `configs/fimm_submission_gate.json`
- `data/development/normalized_caller_calls.tsv`
- `data/development/sensitivity_abstain/normalized_caller_calls.tsv`
- `decisions/20260929_fimm_legacy_withdrawal.json`
- `decisions/20260929_fimm_panel_deviation.json`
- `decisions/20261013_fimm_venex_scope_and_gate.json`
- `decisions/20261013_publication_remediation_scope.json`
- `decisions/20261026_fimm_venex_s9_restored.json`
- `figures/figure_manifest.json`
- `manuscripts/benchmark/manuscript.md`
- `manuscripts/benchmark/supplementary.md`
- `manuscripts/claim_audit.tsv`
- `manuscripts/historical/benchmark_manuscript_pre_remediation_20260924.md`
- `manuscripts/historical/benchmark_supplement_pre_remediation_20260924.md`
- `manuscripts/historical/claim_audit_pre_remediation_20260924.tsv`
- `manuscripts/source_original/issue_register.tsv`
- `manuscripts/source_original/source_text.txt`
- `provenance/development_rerun_v350/historical_result_registry_pre_v350.tsv`
- `provenance/development_rerun_v350/result_registry_delta.tsv`
- `provenance/development_rerun_v350/truth_free_collection/normalized_caller_calls.tsv`
- `provenance/development_rerun_v350/truth_free_collection/sample_run_provenance.tsv`
- `provenance/development_rerun_v350/truth_free_collection/sensitivity_abstain/normalized_caller_calls.tsv`
- `provenance/development_rerun_v350/truth_free_collection/t1k_parser_provenance.tsv`
- `provenance/development_rerun_v350_superseded_20261025/historical_result_registry_pre_v350.tsv`
- `provenance/development_rerun_v350_superseded_20261025/result_registry_delta.tsv`
- `provenance/development_rerun_v350_superseded_20261025/truth_free_collection/normalized_caller_calls.tsv`
- `provenance/development_rerun_v350_superseded_20261025/truth_free_collection/sample_run_provenance.tsv`
- `provenance/development_rerun_v350_superseded_20261025/truth_free_collection/sensitivity_abstain/normalized_caller_calls.tsv`
- `provenance/development_rerun_v350_superseded_20261025/truth_free_collection/t1k_parser_provenance.tsv`
- `pyproject.toml`
- `reports/AUTHOR_INPUT_REQUIRED_SCIENTIFIC_REPORTS.md`
- `reports/ChampHLA_Scientific_Reports_Cover_Letter.md`
- `reports/SCIENTIFIC_REPORTS_SUBMISSION_CHECKLIST.md`
- `reports/SUPERVISOR_PROJECT_AND_METHOD_REPORT_2026-09-02.md`
- `reports/champhla_gap_review_20261007.md`
- `reports/champhla_scientific_reports_change_log_20261019.md`
- `reports/champhla_scientific_reports_rerun_review_20261021.md`
- `reports/champhla_scientific_reports_review_20261019.md`
- `reports/champhla_to_panelhla_transfer_matrix_20260930.md`
- `reports/drive_v3_changes_since_20261006.md`
- `reports/drive_v4_changes_since_20261012.md`
- `reports/drive_v5_changes_since_20261026.md`
- `reports/drive_v6_changes_since_20261026.md`
- `reports/drive_v6_followup_changes_20261026.md`
- `reports/extension_readiness_assessment_20261009.md`
- `reports/manuscript_salvage_ledger_20261026.md`
- `reports/manuscript_v6_followup_review_20261026.md`
- `reports/manuscript_v6_gate_stop_20261026.md`
- `reports/manuscript_v6_sentence_review_20261026.md`
- `reports/manuscript_v7_preservation_20261027.json`
- `reports/peer_review_remediation_matrix.tsv`
- `reports/pre_submission_review_20261008.md`
- `reports/publication_remediation_closure_20261013.tsv`
- `reports/scientific_review_20261012.md`
- `reports/scientific_review_20261012.tsv`
- `reports/supervisor_review_response_20261006.md`
- `reports/tools/check_scirep_rewrite.py`
- `result_registry.tsv`
- `scripts/build_drive_document.sh`
- `scripts/collect_cohort_caller_calls.py`
- `scripts/compare_cross_modality.py`
- `scripts/fimm_roihu_to_long.py`
- `scripts/freeze_exploratory_aggregates.py`
- `scripts/generate_figures.py`
- `scripts/generate_result_registry.py`
- `scripts/import_fimm_caller_predictions.py`
- `scripts/publish_snapshot.sh`
- `scripts/reproduce_development_benchmark.py`
- `scripts/summarise_cohort_consensus.py`
- `src/champhla_recovery/cli.py`
- `src/champhla_recovery/exploratory.py`
- `src/champhla_recovery/fimm.py`
- `src/champhla_recovery/manuscript.py`
- `tests/fixtures/fimm/crosswalk.tsv`
- `tests/fixtures/fimm/manifest.json`
- `tests/test_drive_document.py`
- `tests/test_exploratory_integration.py`
- `tests/test_figures_publication_ready.py`
- `tests/test_fimm.py`
- `tests/test_fimm_import.py`
- `tests/test_publication_remediation_decisions.py`
- `tests/test_recovery_manuscript.py`
- `tests/test_sr023_consistency.py`

## Verification scope for the final build

The scientific gate is run in the full local development checkout, which includes author-held aggregate artifacts. It is not a fresh-clone regeneration of the filtered snapshot. A successful no-push build establishes the candidate tree, its snapshot-only ancestry and the publisher's bounded text/path scan; it does not certify uninspected legacy binaries or satisfy missing governance, resource permissions or release metadata. Resolve those items before public visibility or a final submission release.
