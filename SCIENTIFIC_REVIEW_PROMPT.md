# ChampHLA — Scientific Review Prompt (v3 manuscript)

## How to use this

1. Open a **fresh** Claude Code session with the working directory set to this repository
   (`D:\projects\project_2008084\champhla_publication_candidate`).
2. Copy everything between `BEGIN PROMPT` and `END PROMPT` into that session.
3. The prompt **reads and reports only**. It writes two files under `reports/` and
   changes nothing else.
4. The TSV it produces has the same columns as `reports/pre_submission_review_20261008.tsv`,
   so it can be given to `MANUSCRIPT_REMEDIATION_PROMPT.md` as a work list.

**How this differs from `PRE_SUBMISSION_REVIEW_PROMPT.md` (8 October).** That prompt
reviewed the markdown as it stood before the single-allele rule changed, the nested-CV
comparator was refitted, the sign-flip test became the deciding test and the paper was
restructured for BMC Bioinformatics. It also read the earlier findings first. This prompt
reviews the version co-authors are reading (Drive v3), reads it cold before consulting any
earlier review, and weights the science above the compliance checks.

---

## BEGIN PROMPT

I'm Umut, the lead author of the manuscript you are about to referee: "ChampHLA: an
auditable benchmark and plurality baseline for short-read classical HLA class I
genotyping". It is headed for BMC Bioinformatics as a Research article. My co-authors are
reading the same version now, and after their sign-off it goes to the journal.

I want the review a demanding referee would write, with one advantage a referee never
has: you can open the repository behind the paper and check each objection against the
data, the code and the recorded decisions. Use that to separate objections that are real
from ones the evidence already answers, and to find problems a referee could only suspect.

The paper has had an internal review (8 October) and many fixes since. That history is a
risk as well as a help. The text has been edited heavily by people and AI assistants who
know what it is supposed to say, and I need a reader who does not. So review it fresh
first, and compare against the earlier review only at the end (Phase 4).

What matters most is the science: whether the design can support the conclusions,
whether the reference typing can bear the weight the endpoint puts on it, whether the
statistics are correct and say what the text says they say, and whether a specialist in
HLA typing would believe the caller results. Journal compliance is in scope too, but a
well-formatted paper that is scientifically unconvincing is the outcome I am trying to
avoid. If you conclude that the central design cannot support the paper's claims, say so
plainly and near the top of the report. I would much rather hear it from you than from
the journal.

Do not soften findings, and do not pad them either. A finding is useful to me when it
states what is wrong, where, the evidence, and what would fix it. One finding per root
cause is better than five symptoms of it.

This is a long, read-only task. Work through it to the end without checking in; nothing
here needs my approval, and I will read the report when it is finished.

### Orientation

The study scores six short-read HLA callers (five on whole-exome data, four on RNA-seq)
and an equal-weight plurality vote across them, called ChampHLA-Consensus, against the
2014 1000 Genomes laboratory HLA typing. The genes are HLA-A, -B and -C at two-field
resolution; the data are 1000 Genomes exomes and Geuvadis RNA-seq. The comparative result
is a null: the vote is not distinguishable from the best single caller, and no fitted
integration method beats it. The contribution the paper claims is the way the evaluation
was done. Two patient cohorts without reference typing (FIMM, VenEx) appear as
exploratory applications.

That paragraph is orientation only. Take the paper's claims from the paper.

There are two repositories. This one, the paper repository, starts from stored,
normalized caller outputs and regenerates everything downstream: truth selection,
statistics, tables, figures and the manuscript. The workflow that runs the callers from
reads is a separate repository at `D:\panelhla_work\panelhla-repo` (GitHub
`uoozcan/PanelHLA`, private at present; release tags `v3.3.0`, `v3.4.0`, `v3.4.1`).

### The text under review

Review the document co-authors are reading: `ChampHLA_Manuscript_v3.docx` on Google
Drive, file ID `1T9Gc-tXFc4eAV6FD7bco8d3Ra63DiDYa`. It is one stored .docx holding the
main text, the figures and the supplement (as an appendix). Its first page, "What changed
since the 6 October version", is a note to co-authors and not part of the manuscript, but
check that what it says is accurate.

Fetch it with the Google Drive connector, by file ID. Then make sure you have all of it:
the connector can truncate large files, so confirm the text runs through Supplementary
S12 and the supplement's reference list. If it is truncated or the connector is not
available, use the repository's own build of the same sources,
`manuscripts/benchmark/ChampHLA_manuscript_COMBINED_DRIVE.docx` (no preface page), and say
in the report which one you reviewed. `.venv/Scripts/python.exe` has python-docx for
extracting text and embedded images.

The document was generated from `manuscripts/benchmark/manuscript.md` and
`supplementary.md`. Before reviewing, establish whether it still matches them. On
12 October it was created at 00:56 UTC with 3,423,697 bytes; a later modified time or a
different size means someone has edited it. Compare the document's paragraphs with the
two markdown files, normalising whitespace and punctuation. Expected differences that are
not edits: the markdown carries `[RESULT:ID]` tags and `<!-- GENERATED -->` markers, both
removed at build time; markdown escapes such as `HLA-B\*15:02`; and main-text figures
placed after their first citation in the document but collected under "Figure legends" in
the markdown. Report any real divergence as its own finding, since a hand edit in Drive
would be lost at the next rebuild. Where the two agree, cite findings by section and by
markdown line, so the fix can be made at the source.

Look at the figures as images, not only their legends: the PNGs are in `figures/`, and
you should confirm the images embedded in the document are those files.

### Ground rules

These exist because each one has already cost this project time. The reason is given so
you can apply it to cases the rule does not name.

1. **Read-only.** Write only the two report files named under "Output", plus scratch
   files in a directory you create under `D:\panelhla_work\tmp\` (the C: drive is nearly
   full and has run out of space mid-task before). Do not edit, regenerate, commit, push,
   or comment on the Drive document. Every number in the paper is tied to checksummed
   artifacts, and an in-place regeneration silently changes what the checksums cover.
2. **This tree only.** Confirm the working directory is
   `D:\projects\project_2008084\champhla_publication_candidate`, record the branch
   (expected `submission-remediation` or a descendant; HEAD was `ca70806` on 12 October),
   and run `git fsck` and `git status --short`. A corrupt object once made every git
   command fail here and hid two days of uncommitted work, so if `git fsck` fails, stop and
   report that. Three other copies of this manuscript exist and all are stale: the
   `champhla_publication_candidate_stage` folder under Downloads, the copy on the Roihu
   cluster, and `docs/CHAMPHLA_MANUSCRIPT_V3.md` in the workflow repository. Do not read
   them as the manuscript.
3. **No number from memory.** The paper's denominators have changed several times, and
   older reports, drafts and commit messages carry superseded values. Any number in a
   finding must be copied from a named file or recomputed by a command you ran, and the
   finding must say which. The few numbers quoted in this prompt are from the text as it
   stood on 12 October; re-read them before relying on them.
4. **No unverified literature.** When a finding cites a paper (a prior benchmark, a
   statistical reference, a caller's published accuracy), confirm by web search that the
   paper exists and says what you attribute to it. If you cannot confirm it, label it
   "unverified" and do not build a finding on it. An invented reference in this
   manuscript was one of the fatal findings last time.
5. **`[RESULT:ID]` tags are citations, not clutter.** In the markdown each one resolves
   to a row of `result_registry.tsv`. Their presence is not a defect. A tag that does not
   resolve to a `validity=valid` row, or a number in the prose that differs from its row,
   is.
6. **Author-only fields.** Passages marked PROVISIONAL, TO CONFIRM or AUTHOR INPUT
   REQUIRED wait on co-authors and institutions. Report their status once, in the table
   described under "Output"; never propose a value. Do raise a finding when the text
   around such a field is wrong whatever value arrives.
7. **Recorded decisions are to be tested, not obeyed.** `decisions/*.json` holds dated,
   often signed analysis choices. Before raising something a decision covers, read the
   record. Then raise it anyway if the choice is scientifically weak, or if the paper does
   not disclose and defend it well enough for a referee who will never see `decisions/`.
   Cite the record either way.
8. **Patient-level data stays closed.** The FIMM and VenEx cohorts are patient data.
   Work from the aggregate artifacts (`artifacts/fimm/`, `artifacts/fimm_consensus/`,
   `artifacts/venex/`). Do not open `data/fimm/`, any `*.SECURE.tsv` file or any identified
   workbook, and put no specimen or patient identifier in the report. Send nothing from
   the manuscript or the data to an external service except literature search queries.
9. **Roihu is not needed.** Do not connect to the cluster. If a finding can only be
   settled there, grade it PLAUSIBLE and say what would settle it.
10. **Identifiers that live in data are not naming errors.** Method keys such as
    `SimplePluralityLex`, selection seeds beginning `ChampHLA-CC-`, the package names
    `champhla_confirmation` and `champhla_recovery`, and the repository name PanelHLA were
    left unrenamed on purpose, because renaming an identifier changes what a frozen roster
    or checksum reproduces. Flag them only where they leak into reader-facing prose
    unexplained.

Practical notes for this Windows machine: pass `D:/...` paths to the `.venv` Python (it
misreads Git Bash `/d/...` paths); write scripts with the Write tool into your scratch
directory and run them, because shell heredocs here break on apostrophes and collapse
backslashes; and keep a running findings file in the scratch directory as you go, since
the session will be long and early context may be summarised.

### How to work

**Phase 0 — baseline.** Apply ground rule 2, obtain and reconcile the text as described
above, and record what you reviewed.

**Phase 1 — cold read.** Read the whole document once, main text and supplement, as a
referee who has only the document. Do not open code, artifacts, decision records or
earlier reviews yet. Then write down, in your scratch notes: the paper's claim in one
sentence; what kind of contribution it is (method, benchmark, or negative result) and
whether the title, abstract, discussion and conclusions agree on that; every point where
you did not believe something, could not follow it, or wanted evidence that was not
given; and what you would ask the authors. These first-reading notes are evidence in
themselves. If the repository later answers a question the paper left open, the paper
still has a disclosure gap, and that is a finding.

**Phase 2 — evidence.** Now use the repository. Work through the dimensions in "What to
examine" and the questions in "Questions a hard referee would ask". For each concern from
Phase 1, find out whether it is real.

**Phase 3 — try to refute your own findings.** Described below.

**Phase 4 — reconcile with the 8 October review.** Described below. Until this phase, do
not open `reports/pre_submission_review_*`, `reports/peer_review_*`,
`reports/response_to_peer_review_*`, `reports/supervisor_review_response_*`,
`PRE_SUBMISSION_REVIEW_PROMPT.md` or `MANUSCRIPT_REMEDIATION_PROMPT.md`. Decision records
and commit messages mention earlier finding IDs; that is unavoidable and fine.

**Phase 5 — write the two output files.**

You may use subagents for jobs that are separable and benefit from a fresh context:
verifying the reference list against sources, the literature and novelty search,
independent recomputation of the statistics, checking the code against the paper's
method description, and the Phase 3 refutation of your most serious findings. Give each
one the ground rules and the exact question. Keep the cold read and the overall judgement
yourself, because they need the whole paper in one head. If you would rather work
sequentially, that is fine.

### Where the evidence is

- **Per-locus results:** `artifacts/development_corrected/per_locus_results.tsv`. One row
  per subject, assay, gene and method at every exact-endpoint locus, with the call, the
  reference genotype and `correct`. This is the table to recompute from.
- **Registry and claim audit:** `result_registry.tsv`, `manuscripts/claim_audit.tsv`, and
  the audit JSONs at the top of `artifacts/`.
- **Other artifacts:** under `artifacts/`, notably `development_sensitivity_abstain/`
  (every single allele abstains), `head_to_head/`, `development_characterisation/`,
  `development_limits/`, `integration_limits/`, `plurality_characterisation/`,
  `restored_analyses/` (Supplementary S12), `harmonisation_correction/`.
- **Decisions:** every file in `decisions/`, with `publication_route.json` first.
- **Method and statistics code:** `src/champhla_confirmation/` (`panels.py`,
  `consensus.py`, `raw_cc.py`, `statistics.py`, `evaluation.py`, `development.py`);
  `src/champhla_recovery/manuscript.py` for what the claim audit enforces; `scripts/` for
  what generates each table and figure.
- **Cohorts and inputs:** `cohorts/` (rosters, the assay manifest),
  `configs/identity_exclusions.json`, `configs/caller_resources_v2.json`,
  `provenance/external_evidence/db_release_resolution.json`.
- **Workflow:** in `D:\panelhla_work\panelhla-repo`, `bin/majority_voting.py`,
  `nextflow.config` and its `paper` profile, `tests/test_paper_parity.py`, `README.md`,
  `CHANGELOG.md`. Read-only, and do not push.
- **Front and back matter:** `AUTHOR_FIELDS_TO_COMPLETE.md`, `AUTHOR_REQUEST_20261008.md`,
  `CITATIONS_TO_VERIFY.md`, `THIRD_PARTY_NOTICES.md`, `README.md`, `CITATION.cff`,
  `LICENSE`.

Two kinds of statement in the paper have **no automated check**, and deserve your direct
attention for that reason. The registry covers numbers this project computed. It does not
cover numbers quoted from other papers (other studies' accuracies and sample sizes, the
concordance between independent typings of 1000 Genomes samples, allele counts in a
database release, the parameters a caller was tuned on), and it does not cover statements
of HLA fact (nomenclature, what a typing method can resolve, what a caller's output
format means, drug–allele associations). Check each of these against its source.

The verification script, `ALLOW_PENDING_AUTHOR_INPUT=1 bash scripts/run_local_verification.sh`,
regenerates artifacts in place, and a freeze manifest is invalidated if any repository
file changes while it runs. If you want to run it, to learn whether the committed
artifacts are stale, do so only in a temporary `git worktree` on D:, and remove the
worktree afterwards. It is optional. The check I care about more is your own
recomputation, with your own short script rather than the project's statistics module, of
the headline results from the per-locus table: each method's concordance in each assay,
the subjects that differ between the vote and each comparator, the exact sign-flip
p-values and their Holm adjustment, the 2×2 counts behind each caller-error correlation,
and the oracle headroom. A recomputed value that differs from the paper is at least
MAJOR.

### What to examine

Treat these as the ground to cover, not a form to fill in. For each dimension either
raise findings or note in a line why it is sound. A through H are the science and deserve
most of your effort.

**A. The question, the contribution and novelty.** Is the research question clear, and
does the study answer it? Is this a method paper, a benchmark or a negative result, and
does every section commit to the same answer? Search the literature from 2015 onward for
benchmarks of short-read HLA callers on exome and RNA-seq data and for consensus or
ensemble HLA typing, verify what you find, and judge whether prior work is cited and
characterised fairly, including work that used the same public data at larger scale. What
does this paper add? Does the title promise what the paper delivers?

**B. The reference typing and the endpoint.** What is the 2014 table: its typing method,
its resolution, its known error rate, how it represents ambiguity? Can it support an
exact two-field label? Is the exclusion of ambiguous, invalid and conflicting loci
decided from the reference alone and never from caller output (confirm in code)? What
selection does that exclusion impose, by gene, population and allele frequency, and does
the paper's answer to it hold up? Is the choice of primary endpoint the defensible one
among the exact, set-valued and G-group versions? Is the second-typing adjudication
sound, and are its consequences followed through the rest of the paper?

**C. Cohort, sampling and power.** How were the subjects chosen, from what available
pool, and is that explained? What can a study of this size detect? Are the unit of
analysis, the clustering by subject, the overlap between the two assays and the ancestry
of the retained subjects handled and stated correctly? Is a held-out confirmation absent,
planned or possible, and what would a referee make of that?

**D. Callers, their deployment and the plausibility of their results.** Is the benchmark
measuring the callers or one unrecorded deployment of them? Consider the unknown
executable versions, the spread of bundled IPD-IMGT/HLA releases, what reads each caller
received, reference assemblies, and the read loss found in a later workflow release. Is
each caller's concordance here in line with what its own publication and independent
benchmarks report on comparable data? Where it is far lower, is that explained? Were the
assay panels chosen independently of the truth? Were these same samples used to develop
the callers, and is the consequence stated?

**E. Method definition and correspondence between paper and code.** Could a reader
re-implement ChampHLA-Consensus from the main text alone: the vote unit, unordered pairs,
ties, single-allele calls, no-calls? Does the pseudocode in Supplementary S7.1 match
`consensus.py` and `raw_cc.py`? Does the released workflow, run as the paper instructs,
produce the evaluated rule, and would someone following the README get there? Are the
comparators (strict majority, two-thirds, nested-CV best caller, the champion–challenger
variants, the logistic meta-consensus) fairly specified and fairly fitted?

**F. Statistics and inference.** Beyond the recomputation above: is the sign-flip test
valid for this design, with clusters of unequal size and very few discordant subjects?
Are the Holm families defined before the results, correctly sized and free of
self-comparisons? Is it coherent to decide significance with one method and report
intervals from another, particularly one the paper itself calls anti-conservative here?
Do the bootstrap intervals behave with this many clusters and proportions near the
boundary? Are the caller-error correlations estimated on enough joint errors to mean
anything, and what do no-calls scored as errors do to them? Is the detectability analysis
right, and does the text draw the correct conclusion from it? Is any equivalence,
non-inferiority or "no worse than" reading implied anywhere without support?

**G. Results, tables and figures.** Cross-check every number the reader meets across the
abstract, methods, results, tables, figure panels, legends, discussion, conclusions,
supplement and the preface page, with its denominator. Check every reference to a figure,
table or supplementary section resolves to the right item. For each figure: does it show
what the legend says, are axes, units, sample sizes and interval types labelled, is it
legible at column width and safe for colour-blind readers, and does it carry any
superseded number? Is every table self-explanatory?

**H. Interpretation, limitations and claims.** Pull out every evaluative or causal
sentence ("because", "explains", "within the uncertainty of", "limits", "robust",
"auditable", "useful when", "should") and check it against its evidence. Do the
conclusions follow from the results, and no further? Are the limitations complete, and
does any limitation as stated undermine a claim made elsewhere? Is the usage guidance
supported? Do the exploratory cohorts earn their place: what do they add to the argument,
against what they cost in length and governance risk? Is any agreement that is automatic
(a single caller agreeing with itself, shared callers across assays) presented as
evidence?

**I. Reproducibility, software and data.** What exactly can a reader regenerate, from
what starting point, and does the paper describe that boundary honestly, including what
the one re-run subject showed? Are releases, tags, container pins and caller database
versions stated and correct? Walk the README as a stranger would. Are the data
availability statement, accessions and licences accurate, including caller licences that
restrict use?

**J. Journal compliance (BMC Bioinformatics, Research article).** Fetch the current
author guidelines and check against them rather than against memory: structure and
required sections, abstract format and length, keywords, declarations, data and code
availability, the policy on AI-assisted writing, reference style, figures, tables and
additional files, and any length guidance. The guidelines page
(`link.springer.com/journal/12859/submission-guidelines/research-article`) blocks plain
fetches; `curl` with a cookie jar works. Check the ethics and consent wording for the
public data and for the patient cohorts for accuracy and internal consistency. Verify
every reference: that it exists, that its metadata are right, and that it supports the
sentence citing it.

**K. Writing and accessibility.** The readership is bioinformaticians, not all of them
HLA specialists, and my supervisor's earlier comments were mostly about undefined terms and
hard sentences. Flag jargon and project-internal vocabulary a reader cannot decode,
sentences that obscure their point with hedging, repetition between sections, and
anything in the main text that belongs in the supplement or the reverse.

**L. What referees will ask for.** List the further analyses, cohorts or experiments a
referee is likely to request. For each, say whether it can be done from the stored tables
now, needs the cluster, needs new data or cannot be done; whether its absence would sink
the paper at this journal or can stand as a stated limitation; and draft the one-sentence
reply.

### Questions a hard referee would ask

These came from one reading of the main text on 12 October, without the supplement. They
are questions, not findings. Some may turn out to be answered well, and saying so is a
useful result. They do not bound the review: I expect you to find things that are not on
this list.

1. **What does the exact endpoint measure?** The reference is Sanger typing of exons 2
   and 3 interpreted against a 2009 allele release. Can that support an exact two-field
   label, or is the reference in effect at a coarser, group-level resolution? If the
   latter, which endpoint should be primary?
2. **How much does selection shape the result?** The exact endpoint keeps well under half
   of the requested loci, mostly from two populations, and the paper reports that the
   strongest single caller is a different one on the excluded loci. What then do the
   exact-endpoint caller rankings mean?
3. **If the reference is wrong where the vote "errs", what follows?** The paper's post
   hoc reading of the second typing is that most consensus errors may be reference
   errors. If so, callers that agree with each other at those loci are agreeing on the
   right answer. What does that do to the caller-error correlations, to the oracle
   headroom, and to the conclusion that the vote gains little "because caller errors were
   strongly correlated"? Is that causal wording in the Conclusions consistent with the
   Results, which call the correlations descriptive? And is the asterisk in the second
   typing really undocumented, or is its meaning given in the source paper or its data
   files?
4. **Is there enough data to conclude anything?** The two headline comparisons differ in
   two subjects and in one. Published work has scored far more samples from the same
   public resource. Why this many here, how were they chosen, and does the paper say? A
   subject-disjoint extension roster is frozen and its analysis pre-specified but not
   run. Would a referee accept "planned", or ask for it before publication, and what
   would running it take?
5. **Which way did each protocol change move the result?** The Methods list every change
   made after results were seen. For each one, work out from the decision records and
   artifacts its direction and size of effect on the headline numbers and on which
   comparisons are significant. Do the changes lean one way? Is each effect disclosed in
   the paper itself?
6. **Are the weak callers really that weak?** Three of the five exome callers score far
   below the other two. Compare with their published accuracy on comparable data. If the
   gap is large, is it the caller, or the unrecorded deployment: an old database, read
   routing, or the loss of reads on alternate contigs found in workflow release 3.3.0?
   The paper argues from one caller's score that the stored calls do not show that
   read-loss pattern. Test it directly for every caller in the per-locus table, where the
   signature is a heterozygous reference genotype called as a homozygote. If some callers
   are artificially weak, what happens to the comparisons the vote wins, and to the
   correlations?
7. **What does the single re-run say?** The current workflow reproduced only part of one
   subject's stored exome calls. What does that imply for the statement that the workflow
   implements what was evaluated, and for the word "auditable" in the title, given that
   the caller run cannot be re-executed and its versions are unknown?
8. **Is "within the uncertainty of the strongest caller" a meaningful statement?** The
   strongest caller is identified on the same data, the comparison could not have reached
   significance at any effect size, and the interval comes from a method the paper says
   is unreliable with few discordant subjects. What can honestly be said?
9. **What is behind the largest correlation?** One RNA-seq caller pair has a very high
   error correlation on the fixed denominator. How many joint errors is that, are the
   missing rows for those callers the same loci or the same subject, and is the
   correlation produced by scoring no-calls as errors?
10. **Do the subject counts reconcile?** The numbers of subjects in both assays are given
    in several places with slightly different values, before and after one input was
    withheld. Check that every count of subjects and loci is consistent and that a reader
    can follow which is which.
11. **Is prior work represented correctly?** Check the figures quoted from earlier
    consensus studies against those papers, and whether "what differs here is the
    evaluation" is a fair and sufficient claim of novelty.
12. **An abstract of results without numbers.** By a recorded decision the abstract
    reports no performance figures, while the Conclusions do. Would an editor and a
    reader accept that? Test the decision.
13. **Do the exploratory cohorts help the paper?** They cannot measure accuracy, they
    carry the paper's only patient-data governance risk, and one earlier analysis of them
    was withdrawn as circular. Would the paper be stronger with them reduced or removed?

### Phase 3: try to refute your own findings

Before writing the report, take each FATAL and MAJOR finding, and each MINOR finding
that rests on a number, and try to knock it down. Re-read the passage in context, re-run
the command, and look for a decision record, a supplementary section or a limitation that
already answers it. A finding is stronger when someone who did not write it has attacked
it, so this is a good use of a subagent that is given only the claim and where to look.

- Refuted: drop it and list it in the appendix with the reason.
- Not checkable locally: keep it, graded PLAUSIBLE, with what would settle it.
- Stands: keep it, graded CONFIRMED, with the exact evidence.

Matters of judgement, framing or style are graded OPINION and need no refutation, only a
reason.

### Phase 4: reconcile with the 8 October review

Now read `reports/pre_submission_review_20261008.md` and its `.tsv` (60 findings,
PSR-001 to PSR-060, each with a status). For each of your findings, record whether it is
new, the same issue as a PSR finding that is still open, a PSR finding marked closed
whose closure you contest, or one that was fixed and has since regressed. Then go the
other way: for each PSR finding marked closed or partially closed, check briefly that
the current text and code bear that out, and report the ones that do not. Do not change
your severities to match the earlier review; where you disagree with it, say so and why.

### Output

Write exactly two files, with today's date as `YYYYMMDD`.

**`reports/scientific_review_<YYYYMMDD>.md`**, in this order:

1. **What was reviewed.** The Drive file's modified time and size, or the fallback used;
   repository branch and commit; whether the document matched the markdown; what you ran
   and what you did not.
2. **Referee summary.** The paper's claim in one sentence; your assessment in a short
   paragraph; the decision you predict at BMC Bioinformatics (accept, minor revision,
   major revision, reject) with your reasoning; and the three changes that would improve
   the paper most, in order.
3. **Strengths to preserve.** What a revision must not lose.
4. **Findings by severity.**
   - **FATAL**: cannot be submitted until fixed, such as a number that does not
     reproduce, a conclusion the design cannot support, or a statement that is false.
   - **MAJOR**: likely on its own to produce a major-revision or reject decision.
   - **MINOR**: a referee would raise it and it must be fixed, but it would not sink the
     paper.
   - **EDITORIAL**: language, formatting, compliance detail.

   Lay each finding out like this:
   ```
   ### SR-### — <one-line title>
   Severity · Dimension (A–L) · Referee (R1–R4) · Grade (CONFIRMED / PLAUSIBLE / OPINION)
   Where the reader meets it: <section, with a short quotation>
   Source: <manuscript.md or supplementary.md>:<line> (and any other location)
   Evidence: <file, command run, or recomputed value against stated value>
   Why a referee objects: <one or two sentences in a referee's voice>
   Fix: <the concrete change; exact replacement wording where it is prose>
   Fix type: rewording | new analysis from stored tables | needs cluster | needs new data | cannot be fixed, state as a limitation
   Effort: S / M / L
   Prior review: new | PSR-### still open | PSR-### closure contested | PSR-### regressed
   ```
   Referee codes: R1 HLA immunogeneticist, R2 biostatistician, R3 reproducibility and
   software reviewer, R4 handling editor.
5. **The case for rejection.** The strongest honest argument a referee could make for
   rejecting the paper, in a paragraph, then its component points with how ready the
   reply is (ready, needs work, no defence) and the findings that address each.
6. **Protocol-change ledger.** One row per change made after results were seen: date,
   what changed, its effect on the headline numbers and on significance verdicts, where
   the paper discloses it, and whether the disclosure is adequate.
7. **Number cross-check.** How many numbers you traced, and a table of every mismatch or
   unexplained difference.
8. **Author-side blockers.** One table of the fields and actions that wait on co-authors,
   institutions or a release, each with what it blocks. No values proposed.
9. **Reconciliation with the 8 October review.** From Phase 4.
10. **What referees will ask for.** From dimension L.
11. **BMC Bioinformatics compliance checklist.** Each requirement from the current
    guidelines, met or not, with the gap.
12. **What could not be checked, and why.**
13. **Appendix: findings considered and dropped**, with the reason for each.

**`reports/scientific_review_<YYYYMMDD>.tsv`**: one row per surviving finding,
tab-separated, with exactly this header so the remediation prompt can read it:

```
issue_id	severity	dimension	persona	verdict	location	evidence	fix	compute_needed	effort	prior_issue	status
```

`issue_id` is the `SR-###` number, `persona` the referee code, `verdict` the grade,
`compute_needed` one of `none`, `local`, `cluster`, `new data`, `impossible`, and
`status` is `open`.

**Final message to me.** The predicted decision and the reason in two sentences, the
counts by severity, each FATAL finding in one line, the three changes that matter most,
and the paths of the two files. Do not paste the report.

## END PROMPT
