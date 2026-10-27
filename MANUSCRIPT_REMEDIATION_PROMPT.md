# PanelHLA — Manuscript Remediation Prompt

## How to use this

1. Open a **fresh** Claude Code session with the working directory set to this repository
   (`D:\projects\project_2008084\champhla_publication_candidate`).
2. Copy everything between `BEGIN PROMPT` and `END PROMPT` into that session.
3. The prompt is self-contained — it names every path, command and guardrail it needs.
   Nothing has to be pasted in alongside it.
4. Re-run it after each remediation round. It is designed to be idempotent: a second run
   over an already-clean manuscript should find nothing to change and say so.

**Companion documents.** Current source of findings: `PRE_SUBMISSION_REVIEW_PROMPT.md`
(this tree), whose `reports/pre_submission_review_<date>.tsv` is the work list for Step 2.
Historical: `THREE_REVIEWER_CRITIQUE_PROMPT.md` (in the
`champhla_publication_candidate_stage` tree under Downloads) generates the reviewer
findings this prompt consumes in Step 2. The critique results from 2026-09-21 in that same
folder were produced against the **stale fork** and are not a valid work list — Step 3
below re-checks them rather than trusting them.

---

## BEGIN PROMPT

You are remediating the PanelHLA manuscript ahead of submission to a mid-tier
bioinformatics journal. Work methodically, one issue at a time, verifying with the
project's own tooling after each change. This is a scientific manuscript with a
checksummed provenance chain, not ordinary source code — the guardrails below are
absolute and override any instinct to be helpful by filling a gap.

### Non-negotiable guardrails

**1. Never invent a number.** Every numeric value that appears in the manuscript must be
copied verbatim from a named artifact on disk. When you add or change any number, record
the source path in your change log. If a number you need does not exist on disk, the
outcome for that issue is `BLOCKED — requires <artifact>`. Never estimate, interpolate,
round differently, or carry a number over from memory or from another document.

**2. `[RESULT:...]` tags are provenance citations, not placeholders to be filled in.**
What `audit_claims()` in `src/champhla_recovery/manuscript.py` actually enforces:
  - every `[RESULT:X]` tag must resolve to a row in `result_registry.tsv`, and that row's
    `validity` must be `valid` — otherwise a failure;
  - `PLACEHOLDER_RE` fails on `TO CONFIRM`, `TODO`, `TBD`, `[AUTHOR…]`, "author verification";
  - `INVALID_WGS_RE` hard-fails on the withdrawn literals `0.399`, `0.494`, `+30.66`,
    `79/411`, `205/411`;
  - the main text must carry each required front/back-matter element (references, authors,
    author contributions, ethics, funding, competing interests, data availability,
    keywords, a numbered figure reference); a supplement must carry numbered `S<n>.` sections;
  - an `exploratory` claim must be hedged in the section where its result tag appears;
  - a `supported` claim must cite either an `evidence_result_id` or an `evidence_source`
    file, and that file must exist.

So: never strip a tag, and never cite a result that is not in the registry as valid.
Adding a number means first confirming (or adding) the corresponding registry row, then
citing it.

**There is no rule that catches a fabricated number.** An earlier version of this file
claimed the auditor fails any numeric paragraph lacking a `[RESULT:...]` tag. That rule
(`NUMERIC_RESULT_RE`) exists only in the superseded Downloads fork and is **absent here**.
Treat guardrail 1 as policy you honour manually: the tooling will not catch you.

**3. Never fill a `TO CONFIRM` field.** There are 13 of them and every one is information
about the authors that nothing in this repository records — author order, affiliations,
ORCIDs, corresponding author, CRediT roles, ethics, funding, competing interests,
acknowledgements, the release DOI, container digests. They are collected in
`AUTHOR_FIELDS_TO_COMPLETE.md`. Your job is to report them as outstanding, never to guess
or to write a plausible-looking placeholder. `scripts/run_local_verification.sh` fails
closed on them by design.

**4. Rename only prose labels — never identifiers that live in data.** The project was
renamed ChampHLA → PanelHLA on 2026-09-17, and the manuscript prose has already been
updated. Should you find any remaining occurrence, apply it to human-facing text only.
**Do not rename**, under any circumstance:
  - method keys: `SimplePluralityLex`, `TwoThirdsGuardedCC`
  - the `MajorityVote` legacy input alias
  - selection seeds: `ChampHLA-CC-expansion-20260901`, `ChampHLA-CC-confirmation-20260831`
  - `schema_version` strings
  - Python packages `champhla_confirmation`, `champhla_recovery`
  - the CSC path `/scratch/project_2008084/pihla-publish`
  - anything under `decisions/`, `provenance/`, `reports/`, `cohorts/`,
    `manuscripts/source_original/`

A seed is an *input*: renaming it changes which subjects a frozen roster reproduces.
Package names are hashed into every freeze manifest. Renaming any of these silently breaks
reproducibility while appearing to succeed.

**5. Work in this tree only.** The canonical tree is this one, on branch
`panelhla-rename-and-statistical-corrections`. A stale fork exists at
`d:\Users\uonur\Downloads\champhla_publication_candidate_stage\` (branch
`roihu-first-closure-20260909`, dirty, last commits 2026-09-16). Never edit the stale fork.

---

### Step 0 — Orient and quarantine

1. Confirm you are in the canonical tree: `git branch --show-current` should report
   `panelhla-rename-and-statistical-corrections`, and `git status --short` should be clean.
   If it is dirty, stop and report what is uncommitted before changing anything.
2. Confirm the stale fork is untouched, then write (or refresh) a file
   `STALE_DO_NOT_EDIT.md` at its root stating that it is superseded, naming the canonical
   tree path and branch, and dating the note. This is the only write permitted in that tree.
3. Report — as a decision item for the author, do **not** act on it — anything the stale
   fork has that this tree lacks. As of 2026-09-21 that is: the `.docx` submission builder
   (`src/champhla_recovery/submission.py`, with `manuscripts/submission/`),
   `configs/comparator_manifest.json`, and `artifacts/generated/`. Do not port these
   silently and do not delete them.

### Step 1 — Re-run the three-reviewer critique against the canonical manuscript

Apply `THREE_REVIEWER_CRITIQUE_PROMPT.md` to the **canonical** documents:
  - `manuscripts/benchmark/manuscript.md`
  - `manuscripts/benchmark/supplementary.md`

Produce its full structured output (three reviews plus the synthesis punch list). Save it
to `artifacts/critique/critique_results_<YYYY-MM-DD>.md`, dated so earlier rounds are not
overwritten.

Do not skip this because a prior critique exists. The 2026-09-21 critique was run against
the stale fork's `ChampHLA_manuscript.md` and describes a substantially different, older
paper.

### Step 2 — Run the project's own claim auditor

```
export PYTHONPATH=src
python3 -m champhla_recovery.cli audit-manuscript-claims \
  --manuscript manuscripts/benchmark/manuscript.md \
  --registry result_registry.tsv \
  --claims manuscripts/claim_audit.tsv \
  --root . \
  --output artifacts/benchmark_manuscript_audit.json \
  --allow-pending-author-input
```

Repeat for `manuscripts/benchmark/supplementary.md` (output
`artifacts/benchmark_supplementary_audit.json`) and for
`manuscripts/shared/generated_results.md` (output `artifacts/generated_results_audit.json`).

Read the `warnings`, `failures` and `blocking_failures` arrays from each. As of 2026-09-21,
after the auditor was corrected to perform the checks it reports, the state is:

- main text — `blocking_failures: []`, `warnings: []`, one failure: the `TO CONFIRM` marker
- supplementary — clean, `submission_ready: true`

So the expected finding is now **no warnings**. If any appear, they are new. Treat the live
audit output as authoritative, and look each claim id up in `manuscripts/claim_audit.tsv`
for its section, claim text, status, evidence result id, evidence source and prescribed
action.

Note that `submission_ready` requires zero warnings *and* zero failures, so the main text
stays false purely because of the outstanding author fields.

### Step 3 — Build one merged triage table

Combine three sources into a single deduplicated table, and note where sources agree:

**(a)** The fresh critique findings from Step 1.
**(b)** The live auditor warnings and failures from Step 2.
**(c)** The 2026-09-21 stale-fork findings, each re-checked against the canonical text and
marked `STILL TRUE`, `ALREADY FIXED`, or `N/A (stale fork only)`. The 14 findings were:
placeholder text in the results table; project named ChampHLA throughout; no inline
statistics for the integration comparators; four names for one method; no donor/subject N;
future-tense data/code availability with no URL or licence; POLYSOLVER input scope not
compared against the other callers; only one of three declared gates reported; amendment
signature status not stated; no prior-art positioning; no percentages or CIs beside raw
fractions; abstract states numbers before their caveat; cross-platform freeze-path check
status unstated; no practical guidance on the ablated integration methods. Verify each
against the canonical text rather than assuming — most were fixed by the rewrite, but say
which, with the line or sentence that fixes it.

Also carry this finding, which came from reading the canonical text directly and is not in
either machine list:

> The set of "seven integration methods" is enumerated inconsistently. The Abstract's list
> includes a reliability-weighted consensus; Table 1 lists MetaConsensus but not
> WeightedConsensus, which appears only in a prose sentence in the Results
> ("A reliability-weighted consensus rescued two WES loci without harm"). Reconcile the
> two enumerations so a reader can count the same seven in both places.

Sort the merged table by severity, then by fix effort. Put the 13 author-input fields in a
**separate** section labelled author-only — they are not yours to fix and should not
compete for position with issues you can act on.

Present the table and stop for confirmation before editing the manuscript.

### Step 4 — Fix, one issue at a time

For each issue, in order:

1. Make the single smallest change that resolves it.
2. Re-run the relevant audit from Step 2.
3. Confirm the warning or failure you targeted is gone **and** that no new one appeared,
   and that the counts moved in the direction you expect.
4. Commit that one fix alone, with a message naming the claim id or issue it closes.
5. Move to the next issue. Do not batch unrelated fixes into one commit.

If a fix would require a number that does not exist on disk, stop and mark it `BLOCKED`
with the artifact required. If a fix would require changing a statistical result rather
than the prose describing it, stop and escalate — that is an analysis decision, not an
editing one.

Values are regenerated, never transcribed. The regeneration entry points are:

```
python3 -m champhla_recovery.cli render-manuscript-tables \
  --registry result_registry.tsv --root . \
  --output manuscripts/shared/generated_results.md

python3 scripts/consensus_head_to_head.py \
  artifacts/consensus_eval_wes_rna/joined_wes_rna.tsv artifacts/head_to_head 100000

python3 scripts/generate_figures.py
```

Note: `scripts/consensus_head_to_head.py` writes to `artifacts/head_to_head` only at the
release bootstrap value of 100000; a smaller value deliberately diverts output to a scratch
directory so reduced-precision intervals cannot silently replace published ones. A 100k
bootstrap takes several minutes — run it in the background rather than blocking on it.

### Step 5 — Final verification

Run the project's full gate, which regenerates every artifact the manuscript cites before
auditing it:

```
ALLOW_PENDING_AUTHOR_INPUT=1 bash scripts/run_local_verification.sh
```

The `ALLOW_PENDING_AUTHOR_INPUT=1` is required only while the 13 author fields are
outstanding; the real submission gate must pass **without** it.

Target end state:
- `blocking_failures: []` and `warnings: []` on the main text, the supplementary, and the
  generated registry fragment.
- `submission_ready: false` **only** because of `pending_author_input`.
- `git status` clean, with one commit per fix.

Then report, in this order:
1. What you fixed, one line each, with the claim id and commit.
2. What is `BLOCKED`, and the exact artifact or decision each needs.
3. The 13 author fields, unchanged, pointing at `AUTHOR_FIELDS_TO_COMPLETE.md`.
4. Anything you deliberately did not touch, and why.

Do not describe the manuscript as submission-ready. With the author fields outstanding it
is not, and that judgment belongs to the authors in any case.

## END PROMPT
