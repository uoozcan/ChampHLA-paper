# Scientific Reports submission checklist for ChampHLA

Status key: **Pass**, **Pending author**, **Pending runs**, **Pending release**, **Blocked**.

| Requirement | Status | Evidence/action |
|---|---|---|
| Article title ≤20 words | Pass | V7 title adopted by Umut (`1ed1f94`); checked by the venue test. |
| Title states the study accurately | Pass | Adopted v7 title; no clinical or equivalence claim. |
| Unstructured abstract ≤200 words | Pass | Current source checked by the venue test; no headings or citations. |
| Abstract contains no provisional performance values | Pass | No performance values; final numbers enter only after the extension freeze (SR-027). |
| No more than six keywords | Pass | Six phrases. |
| Introduction–Methods–Results–Discussion order | Pass | V7 IMRAD structure and automated venue test. |
| Main text ≤4,500 words excluding tables and Methods | Pass | Current source checked by the venue test; no change to the concluding paragraph. |
| Main display items ≤8 | Pass | Four figures and two tables. |
| Editable main tables | Pass subject to final DOCX inspection | Built from Markdown tables. |
| Figure legends ≤350 words each | Pass subject to final automated check | Four main legends. |
| References sequential by first citation | Pass subject to final test suite | Main and supplement renumbered together. |
| Data availability before References | Pass | Separate section. |
| Code availability before References | Pass | Separate section. |
| Ethics and consent in Methods | Blocked | Structure present; identifiers and approved wording require author input. |
| FIMM/VenEx aggregate-only claims | Pass | No accuracy or clinical-utility claim. |
| FIMM/VenEx submission authorization | Blocked | Governance and secure provenance incomplete. |
| Author list, affiliations and ORCIDs | Pending author | Provisional values retained outside reader copies in AUTHOR_FIELDS_TO_COMPLETE.md. |
| Corresponding-author contact details | Pending author | Missing. |
| Author contributions | Pending author | CRediT statement missing. |
| Funding and funder role | Pending author | Provisional grant statement. |
| Competing interests | Pending author | Requires confirmation from every author. |
| Acknowledgements | Pending author | CSC and contributors require confirmation. |
| AI-use disclosure | Pending author | Provisional text is in AUTHOR_FIELDS_TO_COMPLETE.md; approved wording and placement remain to be confirmed. |
| Full 236-run v3.5.0 operational gate | Pass | 25 October 2026: 236/236 complete and checksum-valid, controller finished normally, no rerun jobs (`provenance/development_rerun_v350/operational_gate/`). |
| Final v3.5.0 evidence | Pass | Truth-free collection, activation and one regeneration; registry delta in `provenance/development_rerun_v350/result_registry_delta.md`. |
| Rerun headline approval | Pass | Author-signed `decisions/20261025_rerun_registry_delta_approved_corrected.json`, bound to the registry SHA-256; arcasHLA reported as is (`decisions/20261025_arcashla_report_as_is.json`). |
| Frozen confirmatory extension | Pending runs, deposit and author authorization | Amendment signed in `04cc6d1`; processing started, then stopped. D2 transfer classification is complete. Umut must approve any relaunch; public pre-registration deposit, prediction freeze and separately authorized reference comparison remain outstanding. |
| NCI-60 exploratory application | Pending runs | Pilot complete; full roster running at the read-only check on 27 October 2026. Umut waits for its results (D4); S9.6 and under-way statements remain unchanged. |
| Repositories, final tags and archival DOIs | Pending release | New private ChampHLA and snapshot-only ChampHLA-paper repositories exist. Final paper tag and archival DOIs remain unassigned; the existing workflow v3.5.0 tag is retained. Snapshot build only; push requires approval of the built snapshot. |
| Main manuscript DOCX | Pass subject to final parity/render checks | Generated separately. |
| Supplementary Information file | Pass subject to final parity/render checks | Generated separately. |
| Cover letter | Pending author | Draft includes explicit placeholders. |
| Suggested/excluded reviewers | Pending author | Not inferred. |
| All authors approve submission | Pending author | Must be confirmed outside the repository. |

Do not build or upload the versioned replacement package while any item marked **Blocked**,
**Pending rerun** or **Pending release** remains unresolved. Preserve the 19 October package unchanged.

## Reconciled operating instructions — 27 October 2026

D2 classification is complete. Run no further classify/control commands and never relaunch the extension. When the NCI-60 controller reports exit 10, report it to Umut and ask for instructions. The old PanelHLA workflow repository was deleted on 27 October 2026; no GitHub Support purge request remains. Build and show the new paper snapshot without pushing; approval of that built snapshot is required before any push. The vault is reserved for Claude to update.
