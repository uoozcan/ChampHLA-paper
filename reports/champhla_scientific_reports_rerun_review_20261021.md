# ChampHLA Scientific Reports v3.5.0 rerun-update review

**Date:** 21 October 2026  
**State:** machinery prepared; scientific update blocked by the full-roster gate  
**Submission status:** do not submit

## Editorial verdict

The 19 October Scientific Reports rewrite remains the controlling submission candidate.
No new scientific claim can yet be evaluated: the latest successfully observed audit had
166 of 236 checksum-valid runs, with 70 RNA-seq runs outstanding. WES-only or otherwise
partial performance would violate the signed full-roster rule and distort cross-assay and
fitted-policy comparisons. The manuscript, result registry, main figures and numerical
tables therefore remain scientifically unchanged in this update workspace.

The update path is now fail-closed. A separate operational gate requires exact 236/236
validation, zero relevant jobs, a normally finished controller and matching execution-
manager and roster hashes. A second activation gate verifies release provenance, every
collected checksum, the complete 3,222-cell caller grid, the 1,074-task ledger, singleton
policies and absence of truth-bearing columns before replacing caller inputs. Historical
secondary rows remain available only for fixed outer-fold assignment; fitted predictions
must be regenerated.

## Prepared rerun-specific outputs

- Aggregate caller-task tables are grouped by assay, caller and disposition.
- Aggregate stored-to-rerun cell tables are grouped by assay, caller and change class.
- Supplementary Figure S6 is implemented as a colour-blind-safe stacked display and
  contains no subject identifiers.
- A complete result-registry delta report records added, removed, unchanged and changed
  rows, denominators, callability, estimates, intervals, tests, fitted status and artifact
  hashes.
- The delta report enforces an author stop when headline direction, strongest caller,
  significance interpretation, fitted ranking/conclusion or endpoint definition changes.

All new display code has been exercised only with synthetic fixtures. No synthetic value
has entered the manuscript or registry.

## Issues carried forward from RW-001–RW-032 and SRP-001–SRP-010

The 19 October resolutions remain editorially valid. None was reopened because no final
rerun evidence exists. The following items remain conditional:

| Finding | Current state |
|---|---|
| RW-002/RW-004: thesis and Results architecture | Retained; headings must be rechecked against the final registry delta. |
| RW-008/SRP-009: abstract claim strength | Retained; the abstract remains unstructured, qualitative and free of performance values. |
| RW-011/RW-012: intervals and inference | Retained; rerun intervals and tests must be regenerated at the registered iteration counts. |
| RW-015/RW-021: caveats and limitations | Retained; caller/deployment provenance must be updated after the full rerun. |
| RW-030/RW-031: terminology and number style | Retained; all new values must originate in registered generated blocks. |
| SRP-004/SRP-010: ethics and cohort governance | Still blocking; rerun work does not resolve FIMM/VenEx or public-data ethics wording. |

## Remaining blockers

1. Seventy RNA-seq runs remained incomplete or invalid at the last successful audit.
2. The controller had not finished and rerun-related jobs remained active.
3. No complete collection, frozen truth-free prediction set, refreshed registry or registry
   delta exists.
4. Any headline-sensitive delta requires author approval before prose is revised.
5. Author metadata, ethics/governance, funding, interests, CRediT roles, release commit/tag,
   archival DOI and unavailable container identifiers remain unresolved.

The versioned DOCX/figure/table package must not be built until the complete gate passes,
the analysis runs once, and any required author approval is recorded.
