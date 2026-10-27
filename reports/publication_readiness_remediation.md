# PanelHLA publication-readiness remediation

## Baseline

- Baseline commit: `306ae81e79c78b22025d7abc4038c1f3ec722903`.
- The current implementation pass began from a worktree containing extensive
  pre-existing and in-progress changes. No unrelated change was reverted, and
  the final release remains blocked until the authors curate and commit the
  intended tree.
- Baseline tests: 183 passed under the locally available Python 3.8.10 and
  pytest 7.4.3; this was not the declared Python 3.11.15/pytest 8.3.5 release
  environment.
- Baseline release freeze: invalid (206 recorded files, 30 checksum mismatches,
  27 relevant unfrozen files).
- Baseline primary results: 365/390 WES and 306/321 RNA-seq under generic
  singleton-to-homozygote completion.
- The provisional 364/390 WES and 303/321 RNA-seq correction was superseded by
  the source-truth audit: the historical labels had silently selected one allele
  pair from ambiguous truth strings. Only 158 WES and 125 RNA-seq loci have a
  unique public two-field truth and are eligible for the corrected endpoint.
- Active publication route: benchmark/resource manuscript; WGS concordance evidence is
  invalid and the conditional-method manuscript is superseded.

The governing remediation decision is
`decisions/20260924_publication_remediation.json`. Historical records are not
rewritten.

## Change ledger

| ID | Root cause | Corrective change | Downstream evidence | Status |
|---|---|---|---|---|
| CODE-01 | Generic singleton parsing fabricated a diploid homozygote. | Make singleton output non-callable unless the native output explicitly declares homozygosity; centralize call states. | Parser tests, corrected caller rows, regenerated primary results. | Complete |
| CODE-02 | Allele normalization discarded clinically relevant suffix/ambiguity provenance. | Preserve raw allele and suffix metadata while evaluating the two-field endpoint explicitly. | Normalized-call schema tests and data dictionary. | Complete |
| CODE-03 | T1K was classified as an assembly-graph caller. | Classify T1K separately as an alignment/EM method and update family-gated analyses. | Family tests and regenerated exploratory results. | Complete |
| STAT-01 | A global Bonferroni-like multiplier was described as modality-specific Holm power. | Simulate each modality's whole comparison family and apply Holm in each replicate. | Power tests and regenerated power artifact. | Complete |
| STAT-02 | Non-significance and a post hoc margin were used as equivalence evidence. | Make non-inferiority explicitly exploratory and lead with effect sizes and uncertainty. | Result schema, manuscript, claim audit. | Complete |
| DATA-01 | The paper could not rebuild corrected results from versioned row-level inputs. | Release truth-free normalized caller outputs and checksum-pinned public-truth acquisition/join commands. | End-to-end reproduction command and checksum tests. | Complete |
| DATA-02 | Development WES/RNA were described without their 106-subject overlap and population limits. | Generate overlap, population, gene, zygosity, allele-count and missingness summaries. | Generated characterisation artifacts and supplement tables. | Complete |
| DATA-03 | The historical 390/321 labels selected a single two-field allele from ambiguity strings in the cited public truth. A clean parse finds only 158/125 uniquely resolvable loci. | Restrict the primary denominator to public truth whose ambiguity set collapses to one two-field allele; record every exclusion reason and retain the historical denominator only as invalidated provenance. | Public-source checksum, exclusion audit, truth-selection manifest, corrected benchmark. | Complete |
| FIG-01 | Figures contained hand-entered values and insufficient uncertainty. | Read every value from artifacts; add denominators/CIs and neutral singleton terminology. | Four generated formats per figure and source-table tests. | Complete |
| MS-01 | The paper over-positioned a development benchmark and omitted close prior ensemble work. | Reframe as a retrospective development benchmark, narrow comparator claims, and expand related work. | Revised manuscript, supplement, and reference audit. | Complete |
| MS-02 | Invalid WGS numbers and calibration/equivalence language remained. | Remove WGS performance values and replace those claims with bounded descriptive language. | Prohibited-claim and DOCX-parity audits. | Complete |
| REPRO-01 | CI could pass while scientific regeneration was skipped. | Add a single fail-closed reproduction command and require it for release. | Release-mode regeneration and test gate. | Complete |
| REPRO-02 | The release freeze described an older, incomplete tree. | Regenerate and validate the freeze only after all scientific outputs are final. | Final release-freeze validation. | Complete after final release run |

## Version-2 benchmark/resource implementation

The 2026-09-25 implementation adds a signed, fail-closed protocol for a
subject-disjoint extension while retaining the corrected development analysis
as post hoc evidence. The protocol fixes HLA-A, HLA-B and HLA-C; exact
unordered two-field genotype concordance; fixed-denominator scoring; 89 WES
subjects; 99 RNA-seq subjects; no WGS performance; and retention of extension
results regardless of direction. The protocol audit confirms zero overlap with
the complete exposure ledger.

Official IPD-IMGT/HLA 3.65.0 allele, renamed/deleted-allele, P-group and
G-group files are archived with checksums. The new parser verifies release
membership, preserves original identifiers, distinguishes expression suffixes
from P/G groups and records mapping failures. Set-valued truth construction and
caller-database representability evaluators are implemented. The development
analysis remains labelled syntax-normalized because its exact historical
caller databases cannot be reconstructed.

All primary development intervals were regenerated with 100,000 subject
resamples. Paired tests use subject-level exact sign flips when at most 20
nonzero subject aggregates are present and otherwise use 1,000,000 seeded
Monte Carlo assignments with a plus-one correction. Holm-adjusted P values and
Bonferroni-adjusted percentile subject-cluster intervals are generated for the
complete modality-specific comparison families.

The end-to-end development command completed under Python 3.11.15. The full
suite passed 179 tests, lint passed, the main and supplementary claim audits
reported no scientific failures, and Markdown–DOCX text/figure parity passed.
The five active figures were also inspected visually after regeneration.

The extension readiness gate remains closed. All ten required callers are
currently missing one or more immutable container digests, exact native allele
sets or completed resource/licence audits. Therefore no extension truth join
or performance estimate has been produced, and the frozen subjects have not
been replaced. Cluster execution is also unavailable: all three CSC SSH
certificates found in the local handoff directory are expired, with the latest
validity ending on 2026-09-19. A renewed certificate is required before any
Roihu execution.

## Residual evidence constraints

Exact historical database artifacts or container digests are unavailable for some
caller runs. Consequently, caller-database representability cannot be recomputed
definitively. The normalized input records the available version or lower-bound
provenance, and the manuscript treats this as a limitation rather than inferring
missing metadata. This constraint does not change the corrected endpoint but limits
attribution of individual discordances to database version versus caller method.

## Author-controlled blockers

The software and scientific remediation does not invent author order,
affiliations, ORCIDs, corresponding-author details, ethics determinations,
funding, conflicts, acknowledgments, release tags, archival DOI, or external
container identifiers. The final release gate reports these as one explicit
author-input class. Release tagging and DOI archiving also remain blocked by
the intentionally dirty worktree and unavailable external caller assets.
