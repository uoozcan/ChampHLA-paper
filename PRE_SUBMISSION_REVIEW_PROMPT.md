# ChampHLA — Pre-Submission Scientific Review Prompt

## How to use this

1. Open a **fresh** Claude Code session with the working directory set to this repository
   (`D:\projects\project_2008084\champhla_publication_candidate`).
2. Optionally set the venue on the first line of your message, e.g.
   `TARGET_VENUE = Bioinformatics (Original Paper)`. If you leave it out, the review
   assesses venue fit itself and recommends one.
3. Copy everything between `BEGIN PROMPT` and `END PROMPT` into that session.
4. The prompt **reads and reports only**. It never edits the manuscript, the registry,
   the decisions or the code. It writes two files under `reports/`.
5. Feed the TSV it produces to `MANUSCRIPT_REMEDIATION_PROMPT.md` (Step 2 there), then
   re-run this prompt. It carries finding IDs forward and marks fixed items closed, so
   the two prompts form a review → remediate → re-review loop.

**Why this exists.** `reports/peer_review_20260928.md` reviewed the Sep 25 PanelHLA text.
Since then the paper has been renamed back to ChampHLA (Oct 7), the narrative has been
rewritten (Oct 6–7), and the gap review has restored a large amount of Draft V1 material
(Oct 7–8). Restored text is where old overclaims and stale numbers are most likely to
reappear. Several of the issues most visible to a reviewer also sit **outside** this tree,
in the pipeline repository and in run provenance. This prompt audits all of it.

---

## BEGIN PROMPT

You are conducting a full pre-submission scientific review of the ChampHLA manuscript and
the project behind it, ahead of submission to a bioinformatics journal. Your job is to find
**every** issue an editor or peer reviewer could raise, verify each one against the
repository's own evidence, and rank them so the authors can fix them before submission.
You are not fixing anything. You are producing the review the authors would rather
receive from you than from the journal.

If a line `TARGET_VENUE = …` was given above this prompt, use it. Otherwise treat the
venue as undecided and carry out the venue-fit assessment in §4A.

### 0. The review panel

Review as a panel of five independent personas. Each brings its own expertise and its own
reasons to object:

- **R1, HLA immunogenetics expert.** Histocompatibility and typing methods, nomenclature,
  IPD-IMGT/HLA releases, reference-typing quality, and population genetics.
- **R2, biostatistician / methodologist.** Study design, paired inference, multiplicity,
  clustering, power, selection bias, and the line between pre-specified and post hoc.
- **R3, computational reproducibility and software reviewer.** Workflow, code-to-paper
  correspondence, provenance, containers, releases, licences, and data availability.
- **R4, handling editor.** Contribution, novelty, framing, venue fit, journal compliance,
  ethics, authorship, references, clarity and length.
- **R5, adversarial "Reviewer 2".** Builds the strongest honest case for rejection.

If your environment supports subagents, run R1–R5 in parallel. Give each one this entire
prompt plus its persona, then synthesise their reports yourself, de-duplicating and
reconciling severities. Otherwise run the personas sequentially, writing each persona's
notes before starting the next, so earlier conclusions do not anchor later ones.

### 1. Guardrails (absolute)

These override any instinct to be helpful by filling a gap.

1. **Read-only.** Never edit `manuscripts/`, `decisions/`, `result_registry.tsv`,
   `artifacts/`, `configs/`, `cohorts/`, `provenance/`, `src/`, `scripts/` or the
   pipeline repository. Never commit, push, rename, or regenerate artifacts in place. The
   only files you write are the two report files in §6. Scratch computations go in a
   temporary directory outside the repo.
2. **Canonical tree only.** Before anything else, confirm that the working directory is
   `D:\projects\project_2008084\champhla_publication_candidate`, report the current branch
   (expected `champhla-name-restore` or a later descendant), and run `git fsck`. A corrupt
   loose object once made every git command fail and hid two days of uncommitted work. If
   `git fsck` fails, stop and report it. **Never** read or cite these as the manuscript:
   - `D:\Users\uonur\Downloads\champhla_publication_candidate_stage\` (a stale fork, and
     ChampHLA-named, which makes it look current)
   - the Roihu copy at `/scratch/project_2008084/champhla_publication_candidate` (an older
     Sep 1 draft)
   - `docs/CHAMPHLA_MANUSCRIPT_V3.md` in the pipeline repo (superseded)
3. **No number from memory.** Do not quote any accuracy, count, p-value or CI from memory,
   from older drafts, from Draft V1, or from the 2026-09-28 review. The denominator has
   changed twice. Every number in a finding must be either copied from a named file or
   recomputed by a named command, and the finding must state which.
4. **No invented literature.** Any reference you cite in a finding (prior benchmarks,
   ensemble methods, statistical guidance) must be verified by web search: the DOI
   resolves, and the paper says what you claim it says. If you cannot verify a reference,
   label it `unverified suggestion` and do not present it as fact.
5. **`[RESULT:…]` tags are provenance citations, not defects.** They resolve to rows of
   `result_registry.tsv` and are stripped at build time. Do not report their presence in
   the markdown as an issue. **Do** report a tag that fails to resolve to a
   `validity=valid` row, or a numeric claim whose number does not match its row.
6. **`[TO CONFIRM]` fields are author-only.** Report each one and say what it blocks. Never
   propose a value for it.
7. **Respect recorded decisions, but test them.** `decisions/*.json` records deliberate,
   often signed choices (primary rule, protocol amendments, harmonisation correction not
   adopted, FIMM withdrawal, the name restoration). Before raising an issue a decision
   already covers, read that record. Raise the issue anyway if the decision is
   scientifically wrong, or if the manuscript does not disclose and defend it well enough
   for an outside reviewer who never sees `decisions/`. Cite the record either way.
8. **Grade every finding.**
   - `CONFIRMED`: verified against code, an artifact, or a command you ran.
   - `PLAUSIBLE`: reasoned, but not verifiable locally (e.g. it needs Roihu or a resource
     you cannot reach).
   - `OPINION`: a matter of judgement, style or framing.
9. **Identifiers that live in data are not naming errors.** Method keys
   (`SimplePluralityLex`, `TwoThirdsGuardedCC`), selection seeds (`ChampHLA-CC-…`),
   `schema_version` strings, the package names `champhla_confirmation` and
   `champhla_recovery`, the CSC path `pihla-publish`, and the PanelHLA-named
   checksum-pinned configs were deliberately left unrenamed. Flag them only where they leak
   into reader-facing prose.

### 2. Step 0: establish the baseline

Record each of the following in the report's front matter:

1. `git rev-parse HEAD`, `git branch --show-current`, `git status --short`, `git fsck`.
2. The environment. If `.venv/` is absent, build it:
   `python -m venv .venv && .venv/Scripts/python.exe -m pip install -e ".[test]"`.
   The CLI needs `PYTHONPATH=src` unless the package is installed.
3. `.venv/Scripts/python.exe -m pytest -q`. Record passed, failed and skipped.
   `tests/test_firewall_evaluation.py::test_freeze_hash_scope_excludes_truth_data` fails on
   Windows as a pre-existing path-separator issue. Note it, do not count it as new, but do
   assess (§4G) what it implies for freeze manifests built on different platforms.
4. `ALLOW_PENDING_AUTHOR_INPUT=1 bash scripts/run_local_verification.sh`. Record the exit
   code, every warning, and every `submission_ready` value. Do **not** run it with a
   `BOOTSTRAP` value other than the default. Smaller values divert output, and the gate
   only writes `artifacts/head_to_head` at `BOOTSTRAP=100000`.
5. Compare the SHA-256 of `manuscripts/benchmark/manuscript.md` and `supplementary.md`
   with the hashes pinned in `artifacts/release_freeze.json`. A mismatch means the freeze
   predates the current text.
6. In the pipeline repo `D:\panelhla_work\panelhla-repo`, record: `git branch -a`,
   `git tag`, `git status --short`, `git log --oneline -5` on `main` and on
   `fix-plurality-tie-break`, and whether `origin/main` contains the tie-break fix.

### 3. Read everything before judging anything

Read in full, not by excerpt:

**Manuscript**
- `manuscripts/benchmark/manuscript.md` and `manuscripts/benchmark/supplementary.md`
- The built `.docx` files in `manuscripts/benchmark/`. Check that the build matches the
  markdown, that `[RESULT:]` tags are stripped, and that no tracked changes or comments
  remain.
- `figures/` — **look at the rendered PNGs**, not only the captions and legends.

**Evidence and audit**
- `result_registry.tsv`, `manuscripts/claim_audit.tsv`, and the audit JSONs in
  `artifacts/` (`benchmark_manuscript_audit.json`, `benchmark_supplementary_audit.json`,
  `publication_readiness_gate.json`, `generated_results_audit.json`)
- Result artifacts as needed: `artifacts/development_corrected/`,
  `development_characterisation/`, `development_limits/`, `head_to_head/`,
  `integration_limits/`, `plurality_characterisation/`, `restored_analyses/`, `fimm/`,
  `fimm_consensus/`, `venex/`, `harmonisation_correction/`

**Decisions** — every file in `decisions/`, especially `publication_route.json`,
`20260908_consensus_primary_amendment.json`, `20260908_count_reconciliation.json`,
`20260917_protocol_amendment.json`, `20260918_harmonisation_correction_result.json`,
`20260921_integration_scope_split.json`, `20260928_truth_and_inference_amendment.json`,
`20260929_fimm_legacy_withdrawal.json`, `20260929_fimm_panel_deviation.json`,
`20261001_nci60_reactivation.json`, and `20261007_name_restore_champhla.json`.

**Earlier reviews**
- `reports/peer_review_20260928.md`, `reports/peer_review_20260928_remediation.tsv`,
  `reports/peer_review_remediation_matrix.tsv`, and
  `reports/response_to_peer_review_20260928.md`
- `reports/supervisor_review_response_20261006.md` (17 supervisor comments)
- `reports/champhla_gap_review_20261007.md` (what was restored on Oct 7–8, and what
  cannot be restored)
- Any earlier `reports/pre_submission_review_*.tsv` (see §7)

**Front and back matter**
- `AUTHOR_FIELDS_TO_COMPLETE.md`, `CITATIONS_TO_VERIFY.md`, `COAUTHOR_REVIEW_CHECKLIST.md`,
  `THIRD_PARTY_NOTICES.md`, `README.md`, `CITATION.cff`, `LICENSE`

**Code that defines the method and the numbers**
- `src/champhla_confirmation/`: `panels.py`, `consensus.py`, `raw_cc.py`,
  `statistics.py`, `evaluation.py`, `development.py`
- `src/champhla_recovery/`: `manuscript.py` (`audit_claims()`), `registry.py`
- `scripts/`: `consensus_head_to_head.py`, `reproduce_development_benchmark.py`,
  `restored_analyses.py`, `integration_headroom_and_power.py`,
  `plurality_support_calibration.py`, `generate_manuscript_tables.py`,
  `generate_figures.py`, `generate_result_registry.py`

**The released pipeline** (`D:\panelhla_work\panelhla-repo`, published as
`github.com/uoozcan/panelhla`)
- `bin/majority_voting.py` on `main` **and** on `fix-plurality-tie-break`
- `nextflow.config`: defaults (`weighting`, `enable_majority_voting`, `mv_genes`) **and**
  every profile that overrides them
- `README.md`, `CHANGELOG.md`, and `LICENSE`

### 4. Review dimensions

Work through every dimension. The checklists are minimums, not limits. For each item,
either raise a finding or record in one line in your working notes why it is sound.

#### A. Contribution, novelty, framing and venue fit (R4, R5)

- State the paper's contribution in one sentence. Is it a **method**, a **benchmark or
  resource**, or a **negative result**? Do the title, Abstract, the last paragraph of the
  Introduction, the Discussion and the Conclusions all commit to the same answer? Flag any
  residual presentation of ChampHLA-Consensus as a method being proposed for adoption, if
  the evidence supports only "a parameter-free baseline that does no worse".
- Novelty: search the literature (2015–2026) for benchmarks of short-read HLA callers on
  WES and RNA-seq, and for consensus or ensemble HLA typing (tools, pipelines, and papers
  that vote across callers). Verify each one (guardrail 4). What does this paper add that
  those do not? Is that prior work cited and fairly characterised?
- Headline framing: the main comparative result is negative or null. Is it framed so that
  an editor sees a contribution (an audited benchmark, a fail-closed truth audit, an
  ambiguity-respecting truth parser, singleton abstention, a correlated-error explanation
  of the null), rather than a method that failed?
- Consistency between the publication route and the text. `decisions/publication_route.json`
  carries flags such as `abstract_numeric_performance_allowed`,
  `external_validation_complete`, `rna_locked_minimum_met` and `historical_wgs_valid`.
  Check each flag against the current text. For example, does the Abstract report
  numeric performance while the flag says `false`? Decide whether the flag is stale or the
  text is in breach, and say which.
- **Venue fit.** For `TARGET_VENUE`, or if it is undecided, for the 4–6 most plausible
  venues (consider *Bioinformatics*, *BMC Bioinformatics*, *NAR Genomics and
  Bioinformatics*, *GigaScience*, *Briefings in Bioinformatics*, *HLA*, *Frontiers in
  Immunology / Genetics*, *PLOS Computational Biology*), look up the **current** author
  guidelines on the web. Tabulate article types, limits on main-text words, abstract
  words, figures, tables and references, the abstract format (structured or not), the
  data and code availability policy, required statements, and the reporting standards
  each one expects. Measure the manuscript against each: count main-text words excluding
  references and legends, and count figures and tables. Recommend one venue and article
  type, and say what has to change to fit it.

#### B. Data, reference truth and cohort (R1, R2)

- **Reference typing.** What is the 2014 1000 Genomes HLA table: its typing method, its
  resolution, who produced it, and its known error rate if one has been published? How is
  ambiguity represented, and how does the parser handle it? Which IPD-IMGT/HLA release do
  the reference typings use, compared with the callers? Is translating the reference
  allele names to the callers' nomenclature, or the reverse, described and correct?
- **Selection by the fail-closed audit.** The audit retained a fraction of the loci (verify
  the current WES and RNA-seq counts and subject numbers against `manuscript.md`). Confirm
  from code that exclusion depends **only** on the reference typing and never on caller
  output. Then test for selection bias. Do retained and excluded loci differ by gene,
  allele frequency, rare or common allele status, or population? Would concordance on the
  excluded loci plausibly be lower, in which case the reported concordance is optimistic?
  Is the ambiguity-compatible sensitivity analysis an adequate answer? Quantify these
  checks from the artifacts where you can.
- **Circularity and leakage.** Were 1000 Genomes or Geuvadis samples, or these same 2014
  typings, used to build, train or tune any caller (its reference panel, model or default
  parameters)? Check the caller publications. Is the assay-specific panel choice
  independent of the truth? Read `panels.py` and the decision records, and check whether
  the manuscript says how the panels were chosen.
- **Sample size and dependence.** Subjects versus loci (up to three loci per subject),
  overlap between the WES and RNA-seq subjects, and population and ancestry make-up of the
  **retained** subjects (Geuvadis is a limited set of populations). Does the text state
  the limits on generalisability?
- **Caller database releases.** The callers' bundled IPD-IMGT/HLA databases span a wide
  range of releases (verify the per-caller releases against
  `provenance/external_evidence/db_release_resolution.json` and the manuscript's caller
  table). How are renamed
  alleles, alleles extended to three fields, G and P groups, and null alleles handled in
  two-field scoring? Is the spread disclosed as a property of the benchmark, and is its
  possible effect on per-caller results discussed?
- **Assembly and read extraction.** The RNA-seq arm was once scored on reads extracted at
  GRCh38 coordinates from GRCh37 BAMs (fixed Aug 31 2026). Using provenance timestamps and
  manifests, confirm that **every** RNA-seq result in the paper was produced after the
  fix. Is the read-extraction strategy described (HLA-region reads, or full alignments,
  per caller)? Could it disadvantage any caller that expects whole-genome input?
- **Scope.** Class I only, no WGS accuracy claim (the WGS inputs are recorded as invalid),
  and no class II. Is each scope limit justified where a reviewer will look for it, in the
  Methods and the Limitations?

#### C. Method definition and code-to-paper correspondence (R1, R3)

- Is the plurality rule completely specified in the main text, so that a reader could
  re-implement it without the code? Check genotype-level versus allele-level voting, the
  unordered-pair representation, the alphabetical tie-break (how often ties occur on the
  endpoint loci, and whether any result depends on the tie-break), singleton abstention,
  when a single reported allele counts as homozygous, and whether no-calls are scored as
  incorrect with callability reported separately.
- Does the pseudocode in Supp S7.1 match `consensus.py` and `raw_cc.py` line for line in
  logic? Does the Supp S8 flow diagram match `raw_cc.py`?
- **Does the released pipeline implement the paper's method?** This is the check a
  reviewer who tries the software will make.
  - The pipeline's `bin/majority_voting.py` broke ties lexicographically **last**, while
    the paper takes the **first**. The fix lives on the local branch
    `fix-plurality-tie-break`. Is it on `origin/main`? Is there a release tag? Does Supp
    S11.2 still carry a tie disclosure that should change once the fix is released?
  - The `nextflow.config` defaults (`weighting`, `enable_majority_voting`, `mv_genes`) may
    not run the paper's rule (class I, equal weights, assay panel). Is there a documented
    profile or parameter set that does? Is it named in the manuscript and README? Would a
    reader who follows the README reproduce the paper's consensus calls?
- **Comparator fairness.** For the nested-CV best single tool, strict majority (>50%), the
  two-thirds rule, Champion–Challenger and its guarded variant, and each single caller:
  is any of them a straw man, mis-specified, or tuned on the same data it is evaluated
  on? Is the nested-CV procedure described well enough to reproduce?

#### D. Statistics and inference (R2)

- **Re-derive the primary results independently.** From the per-locus artifacts (find the
  joined per-locus correctness tables under `artifacts/development_corrected/` or
  `artifacts/head_to_head/`), recompute with your own short script in a scratch directory:
  the consensus concordance for each assay, each caller's concordance, and the paired
  discordant counts against the main comparators. Compare every recomputed value with the
  Abstract, the Results, Table 2, the figures and the supplement. Any mismatch is at
  least MAJOR.
- **Paired tests.** Are cluster-*t*, the exact sign-flip test and any McNemar tests
  appropriate for clustered binary outcomes with few discordant pairs? Is the resampling
  or clustering unit the subject? Do the tests agree, and where they disagree, does the
  text say which one governs?
- **Multiplicity.** For each Holm family, check its membership and size, and that no
  member is consensus compared with itself (see `panels.REFERENCE_ALIASES`; `MajorityVote`
  and `SimplePluralityLex` are the same rule). Check that the descriptive and fitted
  families are kept separate as stated, and that the families were declared before the
  results were seen (compare decision timestamps). Adding a comparator changes every Holm
  p-value in its family, so check that the artifact and the text use the same family.
- **Intervals versus tests.** In the 2026-09-28 review (MAJ-08), the adjusted CIs and the
  Holm verdicts reached opposite conclusions for some comparators, and a figure showed
  the contradiction. Is it resolved in the text, in Table 2 and in Figures 2 and 3?
- **"Matches", "protects", "no worse".** No non-inferiority or equivalence margin was
  pre-specified, and the paper says that neither is established. Search for every
  sentence that nonetheless implies equivalence, non-inferiority or "protection", and
  check that each is supported or is reworded as a description.
- **Power and detectability.** What effect size could n loci and n subjects detect? What
  is the minimum attainable p for the exact tests? Is the reader told plainly what this
  design could never have detected, so that the null is read as "not detected" rather
  than "absent"?
- **Error correlation (φ).** Is φ estimated sensibly when error counts are small? Are CIs
  given? Is the argument that correlated errors bound what voting can gain stated
  correctly, and is the oracle-headroom analysis consistent with it?
- **Post hoc choices.** The primary rule was selected post hoc. Pre-registrations were
  signed after data access. A homozygosity guard was found by inspecting truth-derived
  harms. Pooling decisions were made after seeing per-assay results. A pre-registered
  correction that lowered accuracy was not adopted. For each one: is it disclosed in the
  manuscript itself (not only in `decisions/`)? Is it labelled exploratory? Is it kept
  out of confirmatory language? Would a sceptical reader see p-hacking, and does the text
  pre-empt that reading?
- **Exploratory analyses.** Check the hedging of the subgroup analyses, the restored Supp
  S12 analyses, FIMM, VenEx and NCI-60: no inferential language without a confirmatory
  design.

#### E. Results, figures, tables and internal consistency (R2, R4)

- **Numbers.** Every number must agree across the Abstract, Results, tables, figure panels,
  legends, Discussion, Conclusions and supplement, with its denominator stated at least
  once in each section and rounding consistent. Build a cross-check table of each headline
  number against every place it appears.
- **Numbering.** After the restoration, Table 1 is the caller table and Table 2 the
  performance table. The main figures are 1–4, and Figure 1 now has four panels. The
  supplement runs S1–S12. Check that every in-text reference to a figure, table or
  supplementary section resolves to the right item, and that none points to the
  pre-restructure numbering.
- **Figures.** Check legibility at journal column width, colour-blind safety, axis labels
  and units, whether n and denominators are shown, and whether CIs or tests are labelled
  as adjusted or unadjusted. Check that no panel carries a superseded number or layout
  (compare against `provenance/quarantined_figures/`), and that each legend is complete
  and self-contained.
- **FIMM and other exploratory cohorts.** There is no truth for these cohorts, so there
  can be no accuracy claim and no claim of external validation. Specimen-level
  cross-modality agreement is primary. The **withdrawn** fingerprint-matched FIMM numbers
  must not appear anywhere: search the text, the tables and the figures. Every BB7.2
  flow-cytometry metric must carry its tier, panel policy and linkage fraction. "Agreement"
  must be read on contested loci; where only one caller calls, agreement is automatic.
  Check that the text never presents automatic agreement as evidence.
- **Restored material** (Introduction, "The ChampHLA workflow" in the Methods, Table 1,
  the Conclusions, usage guidance and future work, Supp S7.1, S8, S11 and S12). Give these
  extra scrutiny for re-introduced overclaims, numbers from the superseded denominators,
  WGS performance statements, "beats every caller" phrasing, and PanelHLA-era vocabulary.

#### F. Discussion, limitations and claim discipline (R5, R4)

- Extract every evaluative sentence ("improves", "outperforms", "robust", "reliable",
  "protects", "recommended", "should", "accurate", "validated") and check each against
  its evidence. Forbidden forms include "beats every caller", any claim of external
  validation (the auditor fails "externally validated" unless it is negated), and any WGS
  accuracy claim.
- **Limitations.** Check for completeness. At minimum: the age and method of the reference
  typing; selection by the audit; a single benchmark cohort; a post hoc primary rule; no
  held-out confirmation; no class II; no WGS; no external validation; the spread of
  database releases; that the stored caller outputs were not re-run end to end (the
  HG00096 re-run versus stored-calls comparison is still `[TO CONFIRM]`); and limited
  ancestry.
- Is the usage guidance in the Conclusions (when to use the vote, and when a single
  caller is enough) actually supported by the evidence presented?
- Does the Discussion engage with the prior work found in §4A, including results that
  disagree with this paper?

#### G. Reproducibility, software, data and licensing (R3)

- **Run provenance.** Which pipeline commit and branch produced the caller outputs the
  paper scores? The deployed Roihu checkout was reported on a non-`main` branch
  (`roihu-migration-locityper-docs`) with many uncommitted files. Is that disclosed? Can a
  released tag reproduce the results? The manuscript's `[TO CONFIRM]` markers for the
  computing system, commit or release tag, and date belong here.
- **Release artefacts.** Check for a pipeline release tag, an archived DOI (e.g. Zenodo)
  for both the pipeline and the paper repository, container images pinned by digest, the
  Nextflow version, and caller versions with their database releases.
- **Regeneration.** Can a reader regenerate every number, table and figure from the
  public repositories with documented commands? Walk through the README as a stranger
  would, and note every undocumented step, missing input, or step that needs CSC access.
- **Naming.** The software URL in the paper is the PanelHLA repository
  (`uoozcan/panelhla`), and the paper repository is `uoozcan/PanelHLA-paper`, while the
  paper is titled ChampHLA. Assess whether a reviewer would be confused, and recommend
  either a disclosure sentence or a rename. Recommend only; do not rename.
- **Portability of the freeze manifests.** Manifests built on Windows hash `src\…` paths,
  while Linux builds hash `src/…`. Can the checksummed provenance be verified
  independently of platform?
- **Compute resources.** The compute-resource figure or table is blocked (the local
  `execution_trace.txt` is empty). Does the paper make any runtime or resource claim
  without evidence?
- **Licences.** Some caller licences were never verified locally (HLA-HD, POLYSOLVER,
  T1K, seq2HLA; see `THIRD_PARTY_NOTICES.md`). Check the upstream licences on the web.
  Do any academic-only or restrictive terms conflict with the MIT statement, the
  container distribution, or the data-availability wording? Is `LICENSE` unmodified MIT
  text?
- **Data availability.** Give accessions for the 1000 Genomes WES and Geuvadis RNA-seq
  data and the reference-typing source. Check that the derived per-locus calls and the
  truth tables are released, and that restricted-access wording covers the FIMM, VenEx
  and NCI-60 material. Check all of this against the target venue's policy.

#### H. Ethics, authorship and compliance (R4)

- **Clinical cohorts.** The FIMM AML/MDS and VenEx data are patient-derived. Check what
  the Ethics section states (approvals, consent, permit numbers, data-controller
  agreements) and whether the repository holds any evidence for it. Earlier work found no
  ethics or permit record on the CSC project. An unsupported ethics statement is FATAL. A
  missing statement for patient data is FATAL.
- **Authorship.** Check the authors, order, affiliations, ORCIDs, CRediT contributions,
  funding (with grant numbers), competing interests and acknowledgements, together with
  every `[TO CONFIRM]` marker and `AUTHOR_FIELDS_TO_COMPLETE.md`. Record what is missing
  and who must supply it.
- **References.** Work through `CITATIONS_TO_VERIFY.md` and the reference list. For each
  reference: does it exist, is the DOI or PMID correct, are the metadata right, and does
  it support the sentence that cites it? Check that every caller is cited to its primary
  publication where it is first named, and that the reference format matches the venue.

#### I. Writing and presentation (R4)

- **Length.** If the main text is over the venue limit, list what should move to the
  supplement, ranked by how little the main argument needs it.
- **Jargon and internal vocabulary.** Look for terms an external reader cannot decode:
  IGSR, SHA-256, "diploid concordance", "development set" without a definition,
  "fail-closed", "callable", "singleton call", and internal method keys such as
  `MajorityVote` or `SimplePluralityLex`. Check that the 17 supervisor comments
  (2026-10-05) have not regressed.
- **Naming.** Check consistent use of ChampHLA (the workflow) and ChampHLA-Consensus (the
  rule), and that no reader-facing "PanelHLA" remains except in URLs, which should
  carry a disclosure.
- **Structure.** Does the Introduction move from gap to question to contribution? Does the
  Abstract stand alone? Is the Results section ordered by the argument, with the primary
  endpoint first?
- Check for sentence-level clarity, hedging that obscures the point, and repetition
  across sections.

#### J. Closure of earlier reviews

- For every issue in `reports/peer_review_20260928.md` (the issue summary, plus each major
  and minor concern), every row of both remediation matrices, and every item in the
  supervisor response, verify against the **current** text and code whether it is
  `closed`, `partially_closed`, `regressed` (once fixed, broken again, typically by the
  restoration or the narrative rewrite) or `open`. Cite the evidence for each verdict.

#### K. What reviewers will ask for

- List the additional analyses, cohorts or experiments a reviewer is likely to request.
  Examples: class II, an independent truth cohort (GIAB, IHWG, GeT-RM), WGS, a held-out
  confirmation, more callers, newer caller releases rebuilt on a single database release,
  runtime benchmarks, and a non-inferiority analysis. For each, state its feasibility:
  `doable_locally_now`, `needs_roihu`, `needs_new_data`, or `impossible`. Use
  `reports/champhla_gap_review_20261007.md` for what is known to be unrecoverable. Say
  whether its absence is fatal for the target venue, or defensible as a stated
  limitation, and draft the one-sentence rebuttal.

### 5. Verification pass

Before writing the report, take every FATAL and MAJOR finding and try to **refute** it.
Re-read the source at the cited line, re-run the command, and look for a decision record
or a manuscript passage that already answers it.

- If it is refuted, drop it and list it in the appendix with the reason.
- If it cannot be verified locally, downgrade it to `PLAUSIBLE` and say what would settle
  it.
- If it is confirmed, keep it, with the exact evidence.

Do the same for any MINOR finding that rests on a number.

### 6. Output

Write exactly two files. Use today's date in `YYYYMMDD` form. Nothing else in the
repository changes.

**`reports/pre_submission_review_<YYYYMMDD>.md`**, in this order:

1. **Front matter.** Reviewed commit and branch, pipeline repo state, test and gate
   results, freeze-hash comparison, and the venue(s) assessed.
2. **Verdict.** The decision you predict (accept / minor / major / reject) for the target
   venue, or for each candidate venue, with a one-paragraph rationale and the recommended
   venue and article type.
3. **Strengths to preserve.** What a revision must not lose.
4. **Findings by severity:**
   - **FATAL**: the paper cannot be submitted until this is fixed (e.g. an unsupported
     ethics statement, a number that does not reproduce, released code that does not
     implement the paper's method).
   - **MAJOR**: likely to cause a major-revision or reject decision.
   - **MINOR**: would be raised and must be fixed, but would not by itself sink the paper.
   - **EDITORIAL**: language, formatting and compliance.

   Each finding is laid out as:
   ```
   ### PSR-### — <one-line title>
   Severity · Dimension (A–K) · Persona (R1–R5) · Verdict (CONFIRMED/PLAUSIBLE/OPINION)
   Location: <file>:<line> (plus any other locations)
   Evidence: <artifact path / command run / recomputed value vs stated value>
   Why a reviewer objects: <one or two sentences, in a reviewer's voice>
   Fix: <the concrete change; the exact replacement wording where it is prose>
   Needs: none | local compute | Roihu | new data | impossible   ·   Effort: S / M / L
   Prior review: new | regressed <ID> | unresolved <ID>
   ```
5. **R5's top 10 reasons to reject.** Each with how ready a rebuttal is (ready / needs
   work / no defence) and the finding IDs that address it.
6. **Closure table for earlier reviews** (from §4J).
7. **Reviewer-request feasibility table** (from §4K).
8. **Submission-readiness checklist.** Title page; abstract within limits; keywords;
   statements (data and code availability, ethics, funding, COI, CRediT); pipeline release
   tag and DOI; figure files and resolution; supplementary format; references verified;
   reporting checklist if the venue requires one; draft cover-letter points (contribution,
   why this venue, the negative result as a feature); suggested reviewers and any
   reviewers to exclude, with reasons.
9. **Appendix: refuted findings**, with the reason each was dropped.

**`reports/pre_submission_review_<YYYYMMDD>.tsv`**: one row per surviving finding,
tab-separated, with this header:

```
issue_id	severity	dimension	persona	verdict	location	evidence	fix	compute_needed	effort	prior_issue	status
```

`status` is `open` for new findings. This file is the work list for
`MANUSCRIPT_REMEDIATION_PROMPT.md`.

**Final chat message.** Give the counts by severity, the FATAL findings as a list of one
line each, the recommended venue, and the paths of the two files. Do not paste the
report.

### 7. Idempotence and re-runs

If any `reports/pre_submission_review_*.tsv` already exists, read the most recent one
first. Carry each existing `issue_id` forward rather than issuing a new one for the same
problem. Set `status` to `closed`, `partially_closed`, `regressed` or `open` according to
the current state, with evidence. Number new findings after the highest existing ID. A run
over a manuscript with nothing left to fix should produce a report that says so, with every
earlier finding closed.

## END PROMPT
