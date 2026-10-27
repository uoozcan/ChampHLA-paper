# ChampHLA publication recovery status

## Current status — 27 October 2026

V7 was adopted and committed in `1ed1f94`; the repository rename and snapshot publisher followed. The earlier dated entries below are historical and are not the current operating instructions. The v3.5.0 development gate passes; submission still requires author and controlled-cohort governance inputs, pending extension/NCI-60 results and release/archive metadata. D2 transfer classification is complete; no further classify/control action is pending. NCI-60 has priority. Never relaunch the extension: report NCI-60 roster completion to Umut and ask for instructions.

The old PanelHLA workflow repository was deleted on 27 October 2026; no Support purge request remains. New repositories remain private pending the release decisions. The paper development history must never be pushed. Build the scanned snapshot and obtain approval before pushing it. See `reports/public_release_readiness_20261027.md` and `reports/presubmission_gap_closure_20261027.md`. The vault is left for Claude to reconcile.


## Completed locally and on Roihu

- Immutable source DOCX copied and checksummed.
- Nine manuscript problems registered; four are critical.
- Source DOCX audit fails as intended: eight verification markers and invalid
  historical WGS performance remain.
- Benchmark manuscript is the live route. Its claim audit reports
  `submission_ready = false` with the remaining gaps enumerated, which is the
  intended state until the author fills the outstanding `TO CONFIRM` fields.
- Conditional method manuscript is **superseded**, not pending: the 2026-09-08
  amendment made equal-weight consensus primary and demoted
  Champion-Challenger to an ablation.
- Canonical result registry created; invalid WGS rows cannot be abstract-eligible.
- Cross-project exposure ledger covers 138 unique previously exposed 1000G
  subjects across ten training, fold, pilot, prediction, and evaluation sources.
- Official WGS/WES/RNA assay manifest created without reading HLA genotypes.
- The 2014 laboratory truth parser never selects an arbitrary representative
  from a cross-two-field ambiguity.
- Frozen initial WGS (120) and WES (89) rosters are feasible.
- Strict RNA feasibility is 99 unexposed donors, below the locked minimum of
  130; RNA three-modality confirmation is therefore currently infeasible.
- Core release-candidate tests pass. RefFormer is isolated as a negative
  ablation with a separate pinned CPU test environment.
- The cleanliness assertion in this document previously pinned commit
  `b9770d6` (2026-09-01), which is now 44 commits behind HEAD and predates the
  rename, the statistical corrections, the headline reframing and the figure
  regeneration. Treat `git status` and the verification gate as the live
  signal; this file is a narrative record, not a state assertion.
- The Roihu preflight passes with Python 3.11.15, samtools 1.21, Nextflow
  25.10.2, Apptainer 1.4.5, the required reference/index, caller containers,
  configuration checksums, and adequate scratch availability.
- The suite contains **157 collected tests** across 28 modules under `tests/`
  (149 `def test_` plus parametrised expansions). This supersedes an earlier
  claim of 45 here, and a claim of 53 in
  `decisions/20260917_project_rename.json`; both were frozen at older commits
  and understated the suite by more than a factor of three. RefFormer's 30
  tests under `ablations/refformer/tests/` are NOT in that 157: `testpaths`
  excludes them and nothing invokes
  `scripts/run_refformer_cpu_tests.sh` (open issue).
- Two discarded Python 3.9 environment attempts are retained under
  ignored audit names; they contain no analysis output.
- Both bounded full-CRAM WGS pilots (HG00096 and HG00097) completed extraction,
  all five caller runs, compact collection, and a valid truth-blind freeze.
- Automated native-source, checksum, normalization, and parser checks pass for
  all 30 pilot caller/locus records. Independent source-line review also found
  exact agreement for all 30; named human sign-off and the locked 50-record
  production review gate remain incomplete.
- The only discovered general WES/RNA Nextflow runner is in the dirty,
  read-only `pihla-publish` tree and uses a permissive task-failure policy.
  It has not been copied or run for confirmation; a fail-closed runner must be
  isolated and stub/integration-tested before the frozen WES roster is started.

## Roihu gates

1. Obtain named human sign-off for the 30 reviewed pilot records.
2. Accumulate and manually review 20 additional valid records so the frozen
   ten-record-per-caller (50 total) production gate can be met.
3. Require five nonempty caller-native outputs and 100% parser agreement for
   every new batch.
4. Run the frozen WGS/WES rosters in rolling batches without truth.
5. Freeze predictions, then join sealed truth exactly once.

No new WGS accuracy or three-modality method claim is currently authorized.
The two-subject capacity gate also fails by design (only two discordant
subjects), and the strict unseen RNA roster remains below its locked minimum.

## 2026-09-20 update

Resolved since the 2026-09-17 entry, which listed three blockers:

- The 2026-09-08 amendment is **signed**, as are all ten records under
  `decisions/`. Nothing awaits signature.
- The harmonisation-defect correction **was run** on Roihu. It is not a defect on
  WES or RNA-seq: the placeholder loci are 92.1% and 97.0% homozygous against a 13%
  baseline, a 6.9x and 7.4x enrichment. Recorded in
  `decisions/20260918_harmonisation_correction_result.json` and reported as a
  disclosed deviation with the counter-reading kept.
- Front-matter `TO CONFIRM` fields **still need author input** — the one remaining
  blocker, now collected in `AUTHOR_FIELDS_TO_COMPLETE.md`.

Added since:

- A seventh integration method. The algorithm-family diversity gate
  (FamilyGatedCC) is implemented, pre-registered before it was run, measured once
  and reported: it reverted 4 of 25 challenger overrides, every one backed by two
  callers from a single family, three of the four wrong. Net +1 WES locus, 0 on
  RNA-seq; Holm p = 0.88 and 1.0, so no verdict flipped. It entered each modality's
  Holm-corrected comparator family rather than being quoted uncorrected beside
  siblings that are corrected.
- Caller licences verified by reading them inside the container images rather than
  assuming. HLA-HD's apparent GPL-3 file turned out to belong to bowtie2, and
  POLYSOLVER's code is BSD-style while its image is academic/non-profit only
  because of Novoalign.
- Figures 1, 2 and 4 regenerated. They had not been rebuilt since the family gate
  entered the comparator family, so Figure 2 showed 11 comparators where Table 1
  and S1 showed 12.
- The four `TO CONFIRM` references resolved from
  `cohorts/official_1000g_assay_manifest.tsv`, which records the source URL of every
  sample. The exomes are 1000 Genomes phase 3 and the whole genomes are the 30x
  high-coverage resequencing, so that placeholder needed two citations, not one.
- `artifacts/release_freeze.json` was refreshed from 198 to 206 entries and
  carries no truth-joined table. **It no longer validates:** 26 of the 206
  recorded hashes do not match the working tree, and its header pins
  `git_commit: f545f82` with `git_dirty: false`, which is 24 commits behind
  HEAD. Both manuscripts, all four regenerated figures, `statistics.py`,
  `evaluation.py` and `confirmation_decision.json` are among the mismatches.
  It must be regenerated as the final step before a release, and
  `scripts/run_local_verification.sh` does not yet check it.

Pipeline, in the separate `uoozcan/panelhla` repository (this tree is `uoozcan/PanelHLA-paper`):

- Fifteen defects found by running it end to end on Roihu across WGS, WES and
  RNA-seq, all fixed. Among them: `module load nextflow` cannot work on Roihu;
  HLA-HD's database path did not exist; POLYSOLVER queried `6:` on `chr6`-named
  BAMs and reported success while producing nothing; fifteen modules wrote
  placeholder results and exited 0; the consensus step scored every tool zero
  because the shipped weight files use a schema the voting code could not read;
  seq2HLA's p-value filter was inverted, discarding its own best calls.
- All five RNA callers and the WGS and WES consensus type HG00096's class I
  exactly: A*01:01/A*29:02, B*08:01/B*44:03, C*07:01/C*16:01.
- `scripts/validate_caller_outputs.py` reports the WES panel complete, 5 of 5
  members producing calls, on the run of 2026-09-19.

Still the author's: the fields in `AUTHOR_FIELDS_TO_COMPLETE.md`, the release tag,
and the Zenodo DOI.


## 2026-09-17 update

- Project renamed ChampHLA -> PanelHLA; see `decisions/20260917_project_rename.json`.
- Statistical defects corrected: the plurality rule was present twice under two
  names and compared against itself in every Holm family; the per-gene harm gate
  tested the demoted ablation rather than the primary method. Every adjusted
  p value was regenerated and no significance verdict changed.
- Freeze manifests are now POSIX-path and platform-stable and carry a
  `content_sha256` that excludes build time and absolute root, so the same tree
  freezes to the same content identity on any machine.
- The claim audit now checks submission completeness (references, authors,
  ethics, funding, competing interests, figures) and rejects unrecognised claim
  statuses. It previously reported `submission_ready = true` for a manuscript
  with none of those.
- `scripts/run_local_verification.sh` is fail-closed and regenerates every
  artifact it audits. Continuous integration runs it on Linux and Windows.
- Manuscript: references, figures, front and back matter added; Methods inlined;
  caller count corrected; the IPD-IMGT/HLA release spread disclosed.

Outstanding and blocking:

- The 2026-09-08 amendment is still `UNSIGNED_AWAITING_AUTHOR`.
- The harmonisation defect correction needs Roihu access to determine whether
  the stored per-tool WES and RNA outputs survive.
- Front-matter `TO CONFIRM` fields need author input.
