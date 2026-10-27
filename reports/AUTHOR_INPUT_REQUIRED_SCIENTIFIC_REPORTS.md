# ChampHLA author input required before Scientific Reports submission

This checklist contains information that cannot be inferred from the repository or supplied by an editor. The current DOCX files are review candidates until every applicable item is confirmed.

## Authorship and title page

- [ ] Confirm every author's full name, spelling, order and affiliation mapping.
- [ ] Supply department, institution, city and country for each affiliation.
- [ ] Supply each ORCID or explicitly confirm that none is available.
- [ ] Identify the corresponding author or authors with an asterisk.
- [ ] Supply corresponding-author postal address and email.
- [ ] Confirm the title and running title.
- [ ] Confirm a CRediT contribution statement for every author, by initials.

## Ethics and participant governance

- [ ] Supply the host-institution determination for secondary analysis of public 1000 Genomes and Geuvadis data, including approval/exemption identifiers where applicable.
- [ ] For FIMM, supply approving committee name, reference number, FHRB/biobank identifier, collection period, demographics, inclusion/exclusion rules and consent or biobank basis.
- [ ] Supply the equivalent governance information for VenEx.
- [ ] Confirm that aggregate publication of HLA and BB7.2 results is permitted.
- [ ] Confirm that no identifiable participant information appears in any submission file.
- [ ] Have an authorized analyst checksum-freeze the secure source manifest and specimen–donor crosswalk; export only hashes and schema-level provenance.

## Funding, interests and acknowledgements

- [ ] Confirm Research Council of Finland grant 351507, recipient and exact funder name, or correct the provisional entry.
- [ ] List all additional support or confirm that none exists.
- [ ] State the role of each funder in design, analysis, publication and manuscript preparation.
- [ ] Obtain an explicit competing-interests confirmation from every author.
- [ ] Confirm whether CSC — IT Center for Science, Finland may be acknowledged and name relevant systems.
- [ ] Confirm all non-author contributions.

## Rerun, code and data release

- [x] Confirm the full v3.5.0 operational gate: 236/236 checksum-valid, no rerun jobs and normal controller completion. (gate PASS 25 October 2026, `provenance/development_rerun_v350/operational_gate/`; the author approved the one regeneration on it)
- [x] Review the complete old-versus-new registry delta. (25 October 2026, `decisions/20261025_rerun_registry_delta_approved_corrected.json`)
- [x] If triggered, approve the revised headline before any rerun-dependent prose is finalized. (same signed record)
- [x] Revalidate every conditional headline sentence against the final registry. (claim audit, 0 scientific failures, 25 October 2026)
- [x] Sign the amended extension pre-registration (`decisions/20261013_extension_v350_preregistration_amendment.json`): signed in `04cc6d1`.
- [ ] Publish the extension pre-registration on Zenodo (reserved DOI 10.5281/zenodo.23251288). Umut will deposit it; the reserved identifier is not evidence of publication.
- [ ] Complete the extension and NCI-60 runs, then collect their results under the applicable plans. The D2 transfer classification is already complete. Only Umut may approve an extension relaunch; no new truth join is authorized.
- [ ] Approve the built paper snapshot before any push, and decide whether mixed files containing cohort aggregates may become public before governance is confirmed.
- [ ] Cut the final paper-repository tag and record its commit.
- [ ] Archive both repositories and supply persistent DOIs.
- [ ] Confirm the workflow release to cite.
- [ ] Supply externally controlled caller-container digests where recoverable and label unavailable historical identifiers explicitly.
- [ ] Confirm that all data/code links are public or review-accessible at submission.

## Submission declarations

- [ ] Confirm that the work is not submitted or published elsewhere.
- [ ] Confirm that all authors approve the manuscript and submission.
- [ ] Confirm the LLM-use disclosure.
- [ ] Supply suggested reviewers and any justified exclusions, or explicitly state none.
- [ ] State whether the authors had prior discussions with a Scientific Reports Editorial Board Member.
- [ ] Approve the cover letter.
