# Confirmatory extension: readiness assessment (2026-10-09)

**Scope.** Before any extension input is staged: what the locked protocol already
fixes, what is ready, what is missing, and what needs an author decision. No
extension data has been touched. All facts below are from the repository and Roihu,
read-only.

## Already locked (`configs/benchmark_resource_protocol_v2.json`, SHA-256 `0981d6b6…`)

- **Status:** `locked_before_extension_truth_join`. The protocol audit is valid and
  `truth_join_permitted: true`.
- **Roster:** subject-disjoint (`cohorts/frozen_initial_rosters.tsv`, seed
  `ChampHLA-CC-expansion-20260901`).
  - 89 WES and 99 RNA-seq subjects; 164 unique, 24 in both assays.
  - Re-verified today: **zero overlap** with development, evaluation and hold-out
    exposure (`cohorts/subject_exposure_ledger.tsv`).
- **Method:** `SimplePluralityLex`, equal weights, lexicographic tie-break, and
  "abstain unless caller-native output explicitly declares homozygosity".
  - This is exactly the signed 2026-10-08 rule (`native_declaration`), so the
    extension runs with no rule conflict.
- **Endpoint:** fixed-denominator exact unordered two-field genotype concordance.
- **Inference:**
  - subject-cluster bootstrap and subject sign-flip test;
  - Holm within each assay;
  - **non-inferiority is locked as "post hoc supplementary sensitivity only".**
- **Retention:**
  - results are reported whatever their direction;
  - no method reselection and no subject replacement;
  - the extension may not be called "independent clinical validation".
- **Normalization:** alleles validated against IPD-IMGT/HLA 3.65.0. The paper's
  normalizer supports this through its `reference` argument; the development set ran
  syntax-only.

## Blocking gates

| Gate | State |
|---|---|
| Zero development–extension subject overlap | **met** (re-verified) |
| Truth-free prediction freeze validates before the truth join | met by design (the gate's freeze chain) |
| All expected caller outputs present or explicitly failed | pending the run |
| All extension alleles validated against IPD-IMGT/HLA 3.65.0 | pending the run; resources present (`resources/ipd_imgt_hla/3.65.0`) |
| Clean Python 3.11.15 full-suite run | not yet (gates have run on Python 3.13); needs a 3.11.15 environment |
| **Clean immutable public release with DOI** | **blocked.** The workflow repository must stay private until GitHub purges the cached FIMM commits. |

## Caller resources (`configs/caller_resources_v2.json`)

The readiness audit requires every listed caller to have a database release, a
native allele list on disk, an immutable container digest and `status: ready`.

| Caller | Role | Digest | Database release | Native allele list |
|---|---|---|---|---|
| HLA-HD | voting | yes | 3.15.0 (resolved) | extracted on Roihu, SHA-256 pinned |
| OptiType | voting | yes | 3.13.1 (resolved) | extracted on Roihu, pinned |
| POLYSOLVER | voting | yes | 3.11.0 (resolved) | extracted on Roihu, pinned |
| SpecHLA | voting | yes | 3.38.0 + 3.51.0 (resolved) | extracted on Roihu, pinned |
| T1K | voting | yes | 3.63.0 (resolved) | extracted on Roihu, pinned |
| arcasHLA | voting | yes | 3.40.0 (bundled report) | **missing: extract from its image** |
| Kourami | non-voting | yes | 3.24.0 (resolved) | extracted on Roihu |
| HLA\*LA | non-voting | yes | unknown | missing; never smoke-tested |
| seq2HLA | non-voting | yes | unknown | missing |
| HISAT-genotype | non-voting | **no container** | unknown | missing |

The six voting callers can be made ready by recording the resolved releases, copying
the pinned native components, and extracting arcasHLA's list. The four non-voting
comparators feed no primary or confirmatory quantity. HISAT-genotype would need a
container and database built from scratch.

## Inputs and compute

- **WES:** indexed exome CRAMs on `ftp.1000genomes.ebi.ac.uk`, across populations
  under-represented in the development set (e.g. JPT, LWK, CHB, ASW). The HLA region
  can be streamed by index, with no whole-file download.
- **RNA-seq:** Geuvadis BAMs, GRCh37. The assembly is verified from each header, never
  from the manifest (the 2026-08-31 lesson).
- **Roihu:** 134 GB scratch free. Region streaming keeps per-sample storage small.

## Decisions needed before a signed pre-registration

1. **Non-voting comparators.** Either amend to require only the voting panels
   (recommended: they affect no confirmatory quantity), or make all four ready (build
   HISAT-genotype; smoke-test HLA\*LA).
2. **DOI gate.** Either Umut creates a Zenodo deposit by uploading the tagged release
   archive (a private GitHub repository is fine), or amend the gate to a checksummed,
   signed tag recorded before staging, with the DOI after.
3. **Non-inferiority.** Either honour the lock (sensitivity only), or amend before
   staging to make a pre-specified margin the primary hypothesis.
