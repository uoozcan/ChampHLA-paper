# ChampHLA Scientific Reports rerun-update change log

**Date:** 21 October 2026  
**Branch:** `scientific-reports-rerun-update`  
**Canonical source HEAD:** `96ef6f83c2db45febbbfe0b141be1fa6e5c8eaee`  
**Status:** preparation complete; evidence-dependent update deferred

## Workspace and preservation

- Created a separate update worktree from the latest canonical HEAD.
- Ported the uncommitted 19 October Scientific Reports rewrite into the new worktree.
- Did not modify the canonical working copy, `champhla_scirep_rewrite_wt`, the earlier
  `manuscript-rewrite` worktree or the 19 October delivery package.
- Did not commit, merge, push, release, upload, collect caller outputs, join truth or inspect
  sealed, immutable or patient-level data.

## New gated machinery

- Added `validate_development_rerun_gate.py` for exact 236/236 validation, job quiescence,
  normal controller completion and canonical source hashes.
- Added `activate_development_rerun.py` with the requested three-path interface. It refuses
  partial rosters, wrong releases, checksum failures, truth columns, duplicate/missing
  caller cells, incomplete task/run ledgers and singleton-policy mismatches.
- Activation archives the truth-free collection and pre-v3.5.0 caller inputs, preserves
  historical secondary rows for folds, clears historical excluded caller rows and changes
  only primary/abstain caller inputs and their manifests.
- Added full registry-delta reporting with headline-sensitive author stop conditions.

## Figures and tables

- Added aggregate Supplementary S10 table slots for caller-task dispositions and
  stored-to-rerun caller-cell changes, both stratified by assay and caller.
- Added conditional Supplementary Figure S6 generation in PDF, SVG, PNG and TIFF using a
  fixed colour-blind-safe palette and aggregate counts only.
- Preserved the four main figures and two main tables; no rerun-specific main display was
  added.
- Corrected the shared Python 3.11 SVG/manifest writer so regenerated figures can be built
  reproducibly under the declared runtime.

## Scientific text and registry

- No Results, Discussion, Methods, legend, performance table or registry value was updated.
- The abstract remains unstructured and contains no performance number.
- The only Supplementary Information edit adds gated, aggregate-only S10 placeholders;
  it makes no scientific claim and contains no interim count or performance value.

## Verification completed so far

- Synthetic gate and activation tests cover incomplete roster, wrong release, checksum
  drift, missing caller cells, truth-column leakage, singleton mismatch and exact accounting.
- Synthetic table tests confirm caller stratification and exclusion of subject identifiers.
- Synthetic S6 tests confirm deterministic four-format hashes and aggregate-only metadata.
- Synthetic registry-delta tests confirm direction, ranking and significance stop conditions.

Final pipeline, claim, DOCX, figure, table and package-hash verification is intentionally
deferred until the signed full-roster gate passes.
