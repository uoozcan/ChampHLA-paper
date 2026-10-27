# Manuscript salvage ledger (2026-10-26)

This ledger compares every known version of the ChampHLA/PanelHLA manuscript with the current
Scientific Reports base and records what was carried forward. It contains no new results, and
every number in the manuscript still comes from `result_registry.tsv`.

- **Base:** `manuscripts/benchmark/{manuscript,supplementary}.md` on branch
  `scientific-reports-rerun-update`.
- **Scope decided by the author on 2026-10-26:** keep NCI-60, FIMM and VenEx; drop trimodal
  (`decisions/20261026_fimm_venex_s9_restored.json`, `decisions/20261026_manuscript_title.json`).

## Versions compared

| Version | Where | Date | Status |
|---|---|---|---|
| Scientific Reports base (v3.5.0 rerun) | this branch | 2026-10-25/26 | Base |
| Scientific Reports rewrite before the rerun | `champhla_scirep_rewrite_wt`, `ChampHLA_Scientific_Reports_package_20261019` | 2026-10-19 | Superseded by the base |
| BMC-format rewrite | `champhla_rewrite_wt` (branch manuscript-rewrite) | 2026-10-19 | Superseded |
| Publication candidate (BMC) | `champhla_publication_candidate` (commit 00f6e5e) | 2026-10-13 | Superseded |
| Drive v3 (`ChampHLA_Manuscript_v3.docx`) | Drive; markdown = commit e80a38f | 2026-10-12 | Last full S9.1–S9.6; **S9 restored from here** |
| Drive v2 / `PanelHLA_Manuscript_v2.docx` | Drive; markdown = commit 2c06794 | 2026-10-06 | Withdrawn NCI-60 numbers; not reused |
| Drive `PanelHLA_Manuscript_v1` (Google Doc) | Drive | 2026-09-30 to 10-07 | Holds the supervisor's 17 comment threads (see below) |
| Drive `PanelHLA_Manuscript_v1x`, "Updated Manuscript and Supplement", `PanelHLA_manuscript_COMBINED_DRIVE*.docx` | Drive | 2026-09-28 to 10-06 | PanelHLA-era imports in the same lineage as v1/v2; not read in full, superseded by the commits above |
| Pre-remediation benchmark | `manuscripts/historical/benchmark_manuscript_pre_remediation_20260924.md` | 2026-09-24 | Invalid 390/321-locus denominators; narrative partly reused |
| Draft V1–V5x line (`ChampHLA_Manuscript_Draft_V1/V3x/V4x/V5x/VX/Vxx.docx`) | Drive; local copies in Downloads | 2026-06 to 2026-10-06 | Ensemble/WGS-era method papers; gap-reviewed on 2026-10-07 (`reports/champhla_gap_review_20261007.md`) |
| Pipeline-repo drafts (`docs/CHAMPHLA_MANUSCRIPT_V3*.md`, `MANUSCRIPT_DRAFT_V1.md`, review files) | `D:\panelhla_work\panelhla-repo\docs` | 2026-07 to 2026-09 | Superseded; narrative partly reused; kept in the repo for now (author choice) |
| Downloads fork `champhla_publication_candidate_stage` and loose drafts | `D:\Users\uonur\Downloads` | various | **Stale; not used as a source** |

## Carried forward in this revision

**A. Narrative that is still valid (rewritten, no numbers):** new Supplementary S13
"Background and design rationale".

| S13 subsection | Source passages |
|---|---|
| S13.1 class I/II biology, 8/8 and 10/10 matching, paralogy, allele-specific expression | repo V3 lines 57, 59, 63–65 |
| S13.2 caller choice as a selection problem; costs of fitted policies | pre-remediation lines 74–85 |
| S13.3 harmonisation is not neutral | pre-remediation lines 551–563, without the WGS contrast or locus counts |
| S13.4 absence of significant improvement is not equivalence | pre-remediation lines 585–592, without the outdated "seven of ten" count |
| S13.5 database vintage, deployed tools versus algorithms, nomenclature pinning | pre-remediation lines 601–610; Draft V1 §3 |
| S13.6 workflow engineering | Draft V1 §4 |
| S13.7 ancestry and class II outlook | repo V3 lines 611 and 617, without per-population champions or the version roadmap |

The main text gains only two pointers to S13; the main-text word count stays under 4,500.

**Registered results restored:** Supplementary S9.1–S9.5 from Drive v3 (e80a38f):
- FIMM import rules and valid-caller composition;
- coequal specimen and donor-sensitivity agreement;
- within-panel dissent;
- BB7.2 serogroup agreement, always with tier C, the every-caller panel and the 16-of-53
  linkage;
- VenEx diagnostics.

All 57 cited registry IDs exist unchanged in the current registry, so no registry change is
needed. The three exploratory figures were regenerated from the committed aggregates as
Supplementary Figures S6–S8, and the rerun cell-change figure became S9.

**Number-free disclosure restored:** S9.6, the legacy NCI-60 analysis (Adams *et al.* 2005
cited). This fixes the dangling S8 pointer. NCI-60 estimates return only after regeneration on
release 3.5.0 under the current rules (plan, Phase 2).

**Corrections found during the comparison:**
- The Methods opening and the "ChampHLA workflow" section still described the April–May
  stored outputs as the evaluated data. They now state that the release 3.5.0 rerun supplies
  the primary inputs and that the stored outputs enter only S10 and S12.
- "Software and audit trail" named release 3.4.1; it now names 3.5.0.
- SHA-256 is explained at first use, and "CSC bio-apps" is spelled out (supervisor comments of
  2026-10-05).
- The Ethics line on BB7.2 is consistent again, because BB7.2 is back in S9.

## Supervisor comments (Drive `PanelHLA_Manuscript_v1`, Z. Tanoli, 2026-10-05)

The 17 threads were answered on 2026-10-06 (`reports/supervisor_review_response_20261006.md`).
The general rules they set still apply to every new passage:
- define abbreviations at first use;
- explain technical terms such as SHA-256, "subject" and cluster facilities;
- keep references at the end of the clause they support;
- keep shortcomings out of the abstract.

## B. Needs regeneration before any reuse

| Material | Why it cannot be reused as it stands |
|---|---|
| NCI-60 84.1%/81.7% and the per-gene values (v2, repo V3 Table 12, V5x) | No registry row, different panels, an invented citation |
| Bimodal WES+RNA voting (Draft V1 §9, repo V3 §7) | Superseded denominators; the only admissible form is a recomputation like S12.2 |
| Pre-remediation figures (96.8/96.1%, oracle misses) | Invalid 390/321-locus denominators |

## C. Never reused

| Material | Reason |
|---|---|
| Trimodal analyses (repo V3, Draft V1 §10) | Excluded by the author; they also rely on invalid WGS inputs |
| WGS accuracy (0.5012 vs 0.3844 and similar) | Invalid inputs |
| Superiority, transfer, "external validation" and "clinically relevant margin" claims | Unsupported |
| Silver-standard Locityper/HPRC truth | Not independent truth |
| FIMM LOH, HED and survival | Excluded |
| Fingerprint-paired FIMM concordance | Circular endpoint |
| Donor-level BB7.2 anecdotes | Breach the aggregate-only rule |
