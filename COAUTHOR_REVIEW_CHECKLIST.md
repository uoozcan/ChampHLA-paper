# ChampHLA coauthor review checklist

This package is for scientific and authorship review, not submission. FIMM and
VenEx are exploratory applications without independent HLA truth. Provisional values and unresolved
declarations are retained in AUTHOR_FIELDS_TO_COMPLETE.md, outside the reader manuscript.

## FIMM data custodian

- [ ] Verify the FHRB or ethics identifier and approved cohort wording.
- [ ] Verify collection period, cohort demographics, and inclusion/exclusion rules.
- [ ] Verify the consent or biobank basis for aggregate HLA and BB7.2 reporting.
- [ ] Run the secure source-manifest check on Roihu and return only checksums and
  schema-level provenance; do not return identifiers or the specimen–donor map.

## Analysis lead

- [ ] Confirm the coequal all-callable and contested-both specimen definitions.
- [ ] Review the current aggregate specimen results and uncertainty intervals in
  Supplementary S9 and Figures S6–S8 against their source artifacts; do not treat agreement as accuracy.
- [ ] Confirm that donor collapse remains sensitivity-only and that contested donor
  calls require every contributing callable specimen to have at least two callers.
- [ ] Confirm BB7.2 linkage: 16/53 flow records linked, with informative counts of
  8 for scRNA-seq, 14 for bulk RNA, and 13 for WES.
- [ ] Confirm that no FIMM or VenEx statement is phrased as accuracy, external
  validation, clinical utility, LOH, HED, or survival evidence.

## All authors

- [ ] Confirm author names, order, affiliations, and corresponding author details.
- [ ] Supply ORCIDs or explicitly state that none is available.
- [ ] Approve CRediT roles, funding, competing interests, and acknowledgements.
- [ ] Approve the exploratory/no-truth boundaries for FIMM and VenEx.
- [ ] Approve the final main manuscript, supplement, and figure set.

## Release lead, after coauthor approval

- [ ] Resolve every item in `AUTHOR_FIELDS_TO_COMPLETE.md`.
- [ ] Run the full release gate without reduced resampling or skipped tests.
- [ ] Cut the immutable release tag only after the clean review candidate passes.
- [ ] Archive that final tag and insert the assigned DOI; do not invent either value.
