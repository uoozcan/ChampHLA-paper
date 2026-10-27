# Author request packet — 27 October 2026

**Draft — never sent.** Target: Scientific Reports, Article. V7 is adopted. This packet consolidates AUTHOR_FIELDS_TO_COMPLETE.md, reports/AUTHOR_INPUT_REQUIRED_SCIENTIFIC_REPORTS.md and COAUTHOR_REVIEW_CHECKLIST.md. Each section can be forwarded separately by Umut after review. A blank or provisional value remains unconfirmed; nothing below has been supplied on an author's behalf. Reply deadline: **[date to be set by Umut]**.

## Every author

Please check your details and confirm whether you approve the current main manuscript, supplement and figures. Give corrections explicitly; do not assume that a value carried forward from an earlier draft has been verified.

- [ ] Confirm your full name, spelling, author order and affiliation mapping.
- [ ] Supply department, institution, city and country for each affiliation, and your ORCID or explicitly state none.
- [ ] Confirm your CRediT roles and approve the contribution statement by initials.
- [ ] Give an explicit competing-interests declaration, including an explicit none where applicable.
- [ ] Confirm manuscript/submission approval and accountability for your contribution; approve the development/exploratory scope and the absence of a clinical-validation claim.
- [ ] Review the current aggregate FIMM/VenEx presentation in Supplementary S9 and Figures S6–S8, without treating caller agreement as accuracy. The analysis lead should verify specimen eligibility, donor-collapse sensitivity and BB7.2 linkage against the registered aggregate artifacts.

**Provisional, not confirmed:** earlier author order is Umut Onur Özcan, Nemo Ikonen, Philipp Sergeev, Ella Sinervuori, Khalid Saeed, Ziaurrehman Tanoli and Markus Vähä-Koskela. Earlier affiliation text is retained in AUTHOR_FIELDS_TO_COMPLETE.md. The provisional statement of no competing interests is not a substitute for individual declarations.

## Corresponding authors

Please confirm who will correspond and approve the submission declarations and cover letter. The current cover letter is a draft with explicit placeholders; it must not be sent until these answers are supplied.

- [ ] Confirm corresponding-author identities, postal addresses, affiliations and email addresses.
- [ ] Approve the title, running title, author order, manuscript and cover letter at reports/ChampHLA_Scientific_Reports_Cover_Letter.md.
- [ ] Confirm that the work is not submitted or published elsewhere, and that every author approves submission and accountability.
- [ ] Supply suggested reviewers and justified exclusions, or explicitly state none. No reviewer names have been inferred.
- [ ] State whether the authors discussed the work with a Scientific Reports Editorial Board Member; explicitly state none if applicable.
- [ ] Approve final funding, interests, acknowledgements, ethics and language-model disclosure wording once the relevant owners confirm it.
- [ ] Approve publication of the retained cohort aggregates only after custodian governance and secure provenance are confirmed.

**Provisional, not confirmed:** Ziaurrehman Tanoli and Markus Vähä-Koskela were carried forward as corresponding authors. Postal and email details remain missing.

## Funding holder

Please confirm the exact support and funder role. Grant text in the older draft is provisional, not an independently verified award statement.

- [ ] Confirm or correct the funder name, grant identifier and recipient for every source of support.
- [ ] List additional support or explicitly state none.
- [ ] Describe each funder's role in study design, data collection, analysis, manuscript preparation and the decision to publish, including an explicit no-role statement where appropriate.

**Provisional, not confirmed:** Research Council of Finland grant 351507 to Ziaurrehman Tanoli.

## FIMM data custodian

Please supply approved wording and confirm that the intended aggregate publication is permitted. Keep all patient-level source files, specimen–donor mappings and real identifiers in controlled storage.

- [ ] Approving committee name, ethics reference/permit number and the applicable FHRB or biobank identifier.
- [ ] Collection period and a demographics summary suitable for aggregate publication.
- [ ] Inclusion and exclusion rules.
- [ ] Consent, biobank or other approved basis permitting secondary analysis and aggregate HLA genotype and BB7.2 serogroup publication.
- [ ] Confirm that the manuscript's retained aggregates and displays fall within that permission and contain no identifying participant information.
- [ ] Have an authorized analyst on Roihu checksum-freeze the source manifest linking the identity-bearing workbook, normalized caller calls and specimen–donor crosswalk. Return **hashes and schema-level provenance only**; never return the crosswalk, real identifiers or patient-level calls.
- [ ] Supply the approved cohort citation and any limits on open release of aggregate records.

All committee, identifier, collection, demographic and consent fields remain **AUTHOR/CUSTODIAN INPUT REQUIRED**.

## VenEx data owner

Please confirm the equivalent governance and publication conditions for the exploratory WES agreement diagnostics. These analyses are not independent HLA accuracy validation.

- [ ] Committee name, reference/permit number, applicable biobank identifier and trial/registry identifier where applicable.
- [ ] Collection period, aggregate demographics and inclusion/exclusion rules.
- [ ] Consent or legal/biobank basis for this secondary analysis and aggregate HLA reporting; confirm any BB7.2 publication permission if applicable, or state not applicable.
- [ ] Approved cohort wording and preferred study citation.
- [ ] Confirm absence of identifying participant information and the conditions on public aggregate release.
- [ ] Have an authorized analyst verify the secure source manifest and crosswalk. Export **hashes and schema-level provenance only**, without patient-level source files or identifiers.

All governance fields remain **AUTHOR/DATA-OWNER INPUT REQUIRED**.

## Umut and release lead

Please coordinate the remaining author-controlled decisions and completed-run/release work. The coding agent has not deposited, sent mail, changed repository visibility, created release tags or joined truth.

- [ ] Obtain the host-institution ethics determination/waiver wording for secondary analysis of public 1000 Genomes and Geuvadis data, including applicable identifiers or an explicit determination that none is required.
- [ ] Confirm the CSC — IT Center for Science, Finland acknowledgement, relevant systems and all non-author contributors.
- [ ] Confirm the complete language-model assistance disclosure and its placement under journal policy. Earlier provisional text mentions Claude/Anthropic; confirm the tools and their actual roles rather than treating that draft as complete.
- [ ] Publish the extension pre-registration on Zenodo. Reserved DOI **10.5281/zenodo.23251288** is not a published deposit. The extension truth join remains unavailable until its separate requirements and author authorization are met.
- [ ] D2 is already complete: the failed extension transfer was classified input_transfer. Run no further classify/control action for it. When NCI-60 controller 2566221 reports exit 10, review the completion evidence and decide the next extension action. **The agent must never relaunch it.**
- [ ] Wait for NCI-60 and extension results under their existing plans. Keep S9.6, under-way sentences and the numeric abstract status unchanged until the applicable results are collected and authorized for reporting.
- [ ] Review the built, unpushed paper snapshot and approve it before any push. All root *_PROMPT.md files are to be excluded. Decide on the mixed aggregate files and the five keep/hold-back recommendations in reports/public_release_readiness_20261027.md before public visibility.
- [ ] Resolve the resource-licence, attribution and legacy-binary review items in that release audit. The old PanelHLA workflow repository was deleted on 27 October 2026; a GitHub Support purge request is no longer needed.
- [ ] Select final release commits and tags, archive both repositories through the intended integration and supply actual DOIs. Insert the assigned identifiers into Data/Code availability, references 56–57 and CITATION.cff, and recover externally controlled container digests or explicitly document unavailable historical identifiers.
- [ ] Complete the remaining full-text checks for Chung 2004, Schumacher & Schreiber 2015 and Lappalainen 2013, each currently marked **unverified: no full-text access**. An author with lawful access can complete them; Scite is not required. Review the proposed narrower neoantigen/therapy wording in CITATIONS_TO_VERIFY.md before changing that sentence.
- [ ] After author/governance fields, analyses, citations and release metadata are complete, run the README release command with --submission. A scientific gate pass alone does not make the paper submission-ready.

No deadlines, ethics decisions, reviewer names, funding roles, contact details, DOI assignments or publication approvals have been inferred. Confirmed declarations should be inserted in the manuscript only after their owners approve them.
