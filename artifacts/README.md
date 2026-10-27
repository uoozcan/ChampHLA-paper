# Artifact status

The publication-bearing result tree is:

- `development_corrected/` — primary and comparator results;
- `development_characterisation/` — cohort and truth-flow audits, ambiguity and
  G-group compatibility, nomenclature, exclusions, stratified results,
  missingness, support profiles, and caller-error correlations;
- `development_limits/` — oracle headroom and power sensitivity;
- `figures/` — figures generated from those tables;
- `publication_readiness_gate.json` — current technical gate; and
- `release_freeze.json` — final file inventory and checksums.

Other result directories pre-date the September 2026 source-truth audit. They are
retained solely to preserve provenance and must not be used as evidence for the
active manuscript. In particular, they may contain the invalid historical WGS
analysis or results based on ambiguity-collapsed 390-locus WES and 321-locus
RNA-seq truth. The active result registry and claim audit point only to the
`development_*` artifacts above.
