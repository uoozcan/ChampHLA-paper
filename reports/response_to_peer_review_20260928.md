# Response to the 28 September 2026 peer review

We thank the reviewer for a close and constructive audit. We treated the report
as a major-revision specification and preserved the original review unchanged.
The revision changes the exact-truth cohort, statistical framework, displays,
and interpretation. It does not add external validation, reactivate historical
WGS analyses, or join truth to the frozen extension cohorts.

The machine-readable issue-by-issue record is
`reports/peer_review_20260928_remediation.tsv`. It covers all 16 major and 26
minor issues and links each to code, regenerated evidence, manuscript location,
validation, and any remaining gate.

## Corrections that change the scientific record

During remediation we found that a resolved duplicate truth row could conceal
an ambiguous duplicate for the same subject and gene. The amended fail-closed
rule excludes a locus if any duplicate is ambiguous, conflicting, invalid, or
unparseable. This changes the exact endpoint from the withdrawn 158 WES and 125
RNA-seq loci to 153 and 120. The corrected primary results are 143/153 (93.5%)
for WES and 110/120 (91.7%) for RNA-seq. The signed version-2 protocol was not
edited; `decisions/20260928_truth_and_inference_amendment.json` records the
correction and preserves its checksum.

Predictions are now constructed and frozen over all 711 requested assay-loci
before truth is read. Truth is represented as sets of unordered candidate
genotypes. Secondary ambiguity-compatible analyses include 335 WES and 266
RNA-seq loci; IPD-IMGT/HLA 3.65 G-group compatibility includes 333 and 264.

The prior paired percentile-bootstrap/sign-flip combination has been replaced
as the primary inference by a locus-weighted CR1 subject-clustered estimate and
Student-t reference distribution with G−1 degrees of freedom. Holm P values and
Bonferroni-adjusted cluster-t intervals use the same active family. Exact or
Monte Carlo sign-flip tests remain a labelled sensitivity analysis. The RNA-seq
nested-CV best-caller result illustrates the resulting transparency: the
cluster-t analysis gives +9.17 points, adjusted 95% CI 0.18 to 18.16 and Holm
P=0.044, while the exact sign-flip sensitivity gives Holm P=0.078. The text now
states that this fitted result is inference-method sensitive and cannot support
a general superiority claim.

## Responses to the major concerns

- MAJ-01 to MAJ-03: set-valued and G-group sensitivities, complete truth flow,
  gene/population exclusion summaries, candidate-occurrence bounds, and a
  release-3.65 nomenclature audit were added. Exact-truth retention is strongly
  population-dependent. No primary error was explained solely by a current
  release rename, deletion, or membership failure, but native caller database
  effects remain unidentifiable and are not attributed to algorithms.
- MAJ-04 and MAJ-12: BestSingleTool_nestedCV now appears in the abstract,
  Results, Table 1 and Figures 1–2. All six fitted policies have publication
  display names and operational definitions.
- MAJ-05 and MAJ-06: the complete caller-error correlation matrix and a
  mutually-callable sensitivity are reported. The Discussion connects the
  observed dependence to the panel's narrow algorithmic coverage and limits the
  intended use of the resource.
- MAJ-07: after CSC certificate renewal, we recovered two current HG00096
  workflow smoke runs with task commands, launch wrappers, container hashes,
  Nextflow traces and Slurm accounting. Supplementary S9 reports the sources
  separately. The DNA route used a WGS-derived mate-aware HLA BAM and is not
  described as WES runtime. Historical development resource use remains
  unavailable, and no monetary cost or cohort-scale estimate was substituted.
- MAJ-08 to MAJ-11 and MAJ-16: paired inference now uses one coherent estimand,
  test and interval framework; descriptive and fitted families are separate;
  zero-discordance rows do not consume multiplicity; resampling counts, seeds,
  cluster counts and sensitivity-test resolution are disclosed. Detectability
  is reported specifically for exact sign-flip sensitivity, not as universal
  statistical power.
- MAJ-13 and MAJ-14: clinical and immunogenomic motivation and an explicit aim
  were restored. The practical recommendation is limited to research use:
  plurality is an auditable robustness baseline when caller choice is uncertain,
  not evidence that panels improve a validated single caller and not a clinical
  typing system.
- MAJ-15: support is now categorical k-of-n. Single-voter 1/1 loci are never
  pooled with 3/3, 4/4 or 5/5 unanimity, and the observed nonmonotonicity is
  discussed.

## Responses to the minor concerns

The title names HLA-A, HLA-B and HLA-C; the abstract is 250 words and defines
the main endpoint terms; recovered outputs and all fitted policies are defined;
citations and the arcasHLA year were corrected; software versions are reported;
small subgroup percentages are suppressed; internal field names have readable
labels; and assay metadata that cannot be recovered are explicitly marked
unavailable. Figures 1, 2 and 5 were redesigned as requested. Historical result
directories now carry `SUPERSEDED.md` sentinels and are excluded from release
manifests. The paper and workflow repository names are distinguished by role.

## Remaining submission gates

MIN-26 requires author-controlled names, order, affiliations, ORCIDs,
   correspondence, ethics, funding, conflicts, acknowledgements and archive
   identifiers. These remain consolidated in `AUTHOR_FIELDS_TO_COMPLETE.md` and
   are a hard submission gate.

Release certification also remains distinct from scientific regeneration. The
authoritative analysis was regenerated and checked on Roihu under Python
3.11.15. A public tag, archival DOI and submission archive remain withheld
until author metadata is supplied and publication is authorized.
