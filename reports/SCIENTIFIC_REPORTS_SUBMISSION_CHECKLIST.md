# Scientific Reports submission checklist for ChampHLA

Status key: **Pass**, **Pending author**, **Pending rerun**, **Blocked**.

| Requirement | Status | Evidence/action |
|---|---|---|
| Article title ≤20 words | Pass | Provisional title is 13 words. |
| Title states the study accurately | Pass, author confirmation pending | Avoids a clinical or equivalence claim. |
| Unstructured abstract ≤200 words | Pass | 179 words; no headings or citations. |
| Abstract contains no provisional performance values | Pass | No performance values; final numbers enter only after the extension freeze (SR-027). |
| No more than six keywords | Pass | Six phrases. |
| Introduction–Results–Discussion–Methods order | Pass | Automated venue test. |
| Main text ≤4,500 words excluding tables and Methods | Pass | 4,455 words in the current source (25 October 2026). |
| Main display items ≤8 | Pass | Four figures and two tables. |
| Editable main tables | Pass subject to final DOCX inspection | Built from Markdown tables. |
| Figure legends ≤350 words each | Pass subject to final automated check | Four main legends. |
| References sequential by first citation | Pass subject to final test suite | Main and supplement renumbered together. |
| Data availability before References | Pass | Separate section. |
| Code availability before References | Pass | Separate section. |
| Ethics and consent in Methods | Blocked | Structure present; identifiers and approved wording require author input. |
| FIMM/VenEx aggregate-only claims | Pass | No accuracy or clinical-utility claim. |
| FIMM/VenEx submission authorization | Blocked | Governance and secure provenance incomplete. |
| Author list, affiliations and ORCIDs | Pending author | Provisional fields retained. |
| Corresponding-author contact details | Pending author | Missing. |
| Author contributions | Pending author | CRediT statement missing. |
| Funding and funder role | Pending author | Provisional grant statement. |
| Competing interests | Pending author | Requires confirmation from every author. |
| Acknowledgements | Pending author | CSC and contributors require confirmation. |
| AI-use disclosure | Pass, author confirmation pending | Present in Methods. |
| Full 236-run v3.5.0 operational gate | Pass | 25 October 2026: 236/236 complete and checksum-valid, controller finished normally, no rerun jobs (`provenance/development_rerun_v350/operational_gate/`). |
| Final v3.5.0 evidence | Pass | Truth-free collection, activation and one regeneration; registry delta in `provenance/development_rerun_v350/result_registry_delta.md`. |
| Rerun headline approval | Pass | Author-signed `decisions/20261025_rerun_registry_delta_approved_corrected.json`, bound to the registry SHA-256; arcasHLA reported as is (`decisions/20261025_arcashla_report_as_is.json`). |
| Frozen confirmatory extension | Pending author | Needs the signed amended pre-registration (`decisions/20261013_extension_v350_preregistration_amendment.json`) before it runs. |
| Repository tag, commit and DOI | Pending release | Required before submission. |
| Main manuscript DOCX | Pass subject to final parity/render checks | Generated separately. |
| Supplementary Information file | Pass subject to final parity/render checks | Generated separately. |
| Cover letter | Pending author | Draft includes explicit placeholders. |
| Suggested/excluded reviewers | Pending author | Not inferred. |
| All authors approve submission | Pending author | Must be confirmed outside the repository. |

Do not build or upload the versioned replacement package while any item marked **Blocked**,
**Pending rerun** or **Pending release** remains unresolved. Preserve the 19 October package unchanged.
