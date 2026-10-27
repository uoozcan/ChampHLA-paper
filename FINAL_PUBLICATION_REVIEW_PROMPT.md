# ChampHLA — final publication review prompt

## How to use this prompt

Run this prompt in a fresh review session whose working directory is the paper
repository. The review is read-only except for the three dated files named in
**Outputs**. It is the final independent acceptance review, not another editing
pass. If a required rerun, release, signature or ethics record is absent, report
that as a blocker; do not substitute historical results or invent a value.

The older `SCIENTIFIC_REVIEW_PROMPT.md` and its 12 October report are preserved
as historical review evidence. This prompt supersedes them only for the final
publication candidate.

---

## BEGIN PROMPT

I am preparing the final BMC Bioinformatics submission of:

> ChampHLA: an audited evaluation of a plurality baseline for short-read
> classical HLA class I genotyping

Act as a demanding external referee with access to the paper's audit trail. Your
job is to decide whether the submitted scientific story is true, reproducible
from its declared boundary, and ready for journal review. Do not repair the
paper. Produce evidence-backed findings and a closure audit.

### Required state before a final-pass verdict

The intended final state is:

- workflow release ChampHLA/PanelHLA v3.5.0 or a documented successor, with the
  quality-aware T1K parser;
- a complete reproducible rerun of all 130 WES and 106 RNA-seq development
  subjects, which is the primary development analysis;
- the earlier stored-output analysis retained only as a labelled historical
  provenance comparison;
- the frozen, subject-disjoint extension of 89 WES and 99 RNA-seq subjects run
  after a signed release-pinned pre-registration and reported regardless of
  direction;
- the registered exact two-field endpoint kept primary, with a
  corrected-reference sensitivity beside every headline and for every method;
- FIMM and VenEx reduced to one main-text paragraph and one consolidated
  supplementary section, with the submission gate closed unless every ethics
  and governance field is verified.

If any item is missing, the review may still proceed, but the verdict cannot be
submission-ready. Identify exactly which artifact or authorization is absent.

### Ground rules

1. **Read only.** Write only the three output files listed below and disposable
   scratch files outside the repository. Do not edit, regenerate, commit, push,
   upload, comment on Drive, publish a DOI or submit a cluster job.
2. **Protect patient data.** Use only aggregate FIMM/VenEx artifacts. Never open
   secure tables, identified workbooks, patient-level calls or specimen maps.
3. **No cluster dependency.** Publication evidence must already be exported as
   immutable checksummed artifacts. Do not connect to Roihu unless a required
   provenance record is absent; if it is absent, report the gap instead of
   treating unexported cluster state as publication evidence.
4. **No result from memory.** Copy a number only from a named artifact or from an
   independent recomputation you perform. Distinguish current rerun results from
   the historical stored-output checksums 142/143 WES and 112/112 RNA-seq.
5. **No unverified literature.** Check quoted facts, sample sizes, methods and
   claims against primary papers or authoritative documentation. Use current
   BMC Bioinformatics Research article instructions.
6. **Decisions are evidence, not immunity.** Read signed decision records, but
   retain a finding when the choice remains scientifically weak or the paper
   does not disclose it adequately.
7. **A commit message is not closure.** A prior issue closes only when the
   current source, generated document, artifact and appropriate test all agree.
8. **Do not conceal negative outcomes.** The extension and the corrected caller
   run must be reported whatever their direction. Any sign of method, subject,
   endpoint or denominator reselection after seeing them is FATAL.

### Phase 0 — establish the immutable candidate

Record:

- repository path, branch, commit, tags, `git status --short` and `git fsck`;
- the final workflow tag/commit, archive SHA-256, DOI and container/resource
  manifest;
- the manuscript source hashes, final combined DOCX hash, figure hashes and the
  build manifest linking them;
- the signed pre-registration/amendment hash and signature time;
- the development and extension freeze-manifest hashes.

The authoritative text is the final combined DOCX generated from
`manuscripts/benchmark/manuscript.md` and `supplementary.md`. Use the candidate
path recorded by the build manifest. If a Drive copy is named there, verify its
size and hash against the local document. Do not assume the old Drive v3 file
(ID `1T9Gc-tXFc4eAV6FD7bco8d3Ra63DiDYa`) is current: it predates the 12 October
SR-001/SR-002 correction unless the final manifest explicitly says otherwise.

Extract every DOCX paragraph, table cell, header/footer and embedded image.
Confirm all source paragraphs and tables appear, all images are byte-identical
to the manifest, no result tags or build sentinels leak, and no HLA allele has
lost its asterisk. Search paragraphs, legends and every table cell for malformed
allele-like strings such as `C03:04`, `A02` or `HLA-B5701`.

### Phase 1 — cold referee read

Before opening prior reviews, decisions, registries or analysis code, read the
entire final document once. Record in scratch notes:

- the paper's question, contribution and answer in one sentence each;
- whether title, abstract, Introduction, Discussion and Conclusions tell the
  same story;
- every claim you did not believe, every denominator you could not follow and
  every result that lacked the evidence needed to interpret it;
- whether the development/confirmation distinction is obvious;
- the decision you would recommend from the document alone.

Inspect figures as figures at journal scale, not only their legends.

### Phase 2 — independent scientific reconstruction

Use exported per-locus and provenance artifacts, not project analysis modules,
to independently recompute:

1. For every method and assay in the corrected development rerun and extension:
   callable loci, exact correct loci, fixed-denominator and called-only
   concordance, allele concordance and subject counts.
2. The plurality call itself from raw normalized caller rows, including unordered
   pairs, caller-native homozygosity, missing/partial/invalid states and
   lexicographic tie-breaking.
3. Every paired subject difference, exact sign-flip p-value, Holm adjustment and
   reported confidence interval. Enumerate all sign assignments through at
   least 25 nonzero subjects.
4. Set-valued, two-field G-compatible and true P-group sensitivities, using the
   reported mapping resources and denominators.
5. Corrected-reference concordance for every method. Confirm that the exact
   registered endpoint is primary and the corrected-reference endpoint is
   explicitly sensitivity-only and conditioned on another exome-derived typing.
6. Pairwise caller-error 2x2 counts and phi on all exact loci and on loci where
   the two typings agree; oracle headroom; vote correction/loss counts.
7. NA19130 and every other locus where caller absence affects a paired result.
   Compare methods again on mutually available loci.
8. Native-database representability and every old-versus-new caller cell. Confirm
   that the primary manuscript uses v3.5.0 rerun calls and that historical calls
   appear only in a labelled provenance comparison.
9. Every exploratory fitted method, including MVFlooredCC and MetaConsensus, from
   the v3.5.0 caller artifacts under each reported scoring rule. Reject any row
   imported from the historical frozen-secondary table or reused unchanged while
   described as refitted or recomputed.

Any disagreement between independent recomputation and a headline, table,
figure, registry row or claim audit is at least MAJOR.

### Phase 3 — workflow and run provenance audit

Inspect workflow tag v3.5.0 or its documented successor. Verify:

- T1K's documented current nine-column schema (eight genotype fields plus
  `secondary_alleles`) and the explicitly supported legacy eight-column schema
  are distinguished and validated; unknown widths or headers fail closed;
- `num_diff_alleles`, both quality fields and the `quality > 0` rule are used;
- one positive-quality allele with count one becomes native homozygosity;
- one surviving allele from a two-allele row is partial, not homozygous;
- a zero-allele native non-call is accepted only when both allele triples are
  placeholders, and secondary candidates are audited but never promoted into
  the primary genotype;
- malformed/contradictory rows fail the task;
- raw T1K files, hashes, quality fields and parser dispositions are retained;
- the paper profile fixes the exact panels, genes, equal weights, call states and
  lexicographic tie-break;
- image digests, database releases and the native SpecHLA checkout match the
  release manifest.

For every requested development and extension subject, verify a run-manifest
entry containing input identity/checksum, assembly from the header, workflow
commit/profile, caller execution artifacts, task/Slurm identifiers, exit state,
raw-output hashes and parser disposition. Failed callers must remain explicit
non-calls. There must be no replacement subjects or undocumented setting changes.

Audit each schema-v2 collector bundle end to end: `collection_manifest.json`,
`selected_input_manifest.tsv`, `sample_run_provenance.tsv`,
`t1k_parser_provenance.tsv` and `normalized_caller_calls.tsv` must all exist and
hash-match. The selected manifest, run rows, T1K rows and caller grid must refer
to the same sample-assays, and their union must exactly cover the frozen roster.
Confirm that frozen extension `prepare` rejected aggregate-only input and consumed
only these checksummed truth-free bundles.

Confirm that extension prediction was truth-free, frozen before the one-time
truth join, permitted by the signed pre-registration/readiness gate, and
reported without reselection.

### Phase 4 — manuscript and literature audit

Check, at minimum:

- the abstract contains concise final development and extension numbers;
- exact and corrected-reference results remain adjacent everywhere a headline
  appears and cover every method in the main table;
- the asterisk in the second typing is described by its documented meaning;
- no causal correlated-error explanation survives where the agreeing-loci
  analysis contradicts it;
- Lee et al. and Claeys et al. receive credit for what they already did, and the
  remaining novelty claim is accurate;
- T1K statements describe the corrected deployment, not the historical parser;
- the original development selection rule is either evidenced or honestly
  described as unrecoverable/convenience sampling;
- the protocol-change ledger gives the direction and magnitude of every change;
- the limitations cover lymphoblastoid cell lines, cross-assay overlap of error
  loci, laboratory-dependent truth retention, caller/reference circularity and
  deployment/version uncertainty;
- FIMM/VenEx make no accuracy claim without truth and occupy only the approved
  reduced space;
- all references exist, metadata are correct and the cited source supports the
  sentence, including software/statistical references;
- author, funding, ethics, consent, competing-interest, AI-use, repository, DOI
  and availability fields contain no unresolved placeholder at submission.

### Phase 5 — prior-finding closure audit

Only after the cold and evidence reviews, open:

- `reports/scientific_review_20261012.md` and `.tsv`;
- `reports/pre_submission_review_20261008.md` and `.tsv`;
- `reports/publication_remediation_closure_20261013.tsv`;
- the decision records cited by those files.

Audit SR-001 through SR-027 and every unresolved/partially closed PSR item. For
each, assign exactly one final state:

- `closed`: current manuscript, artifact and test prove the root cause is gone;
- `partial`: some symptoms are fixed but the root cause remains;
- `open`: no adequate fix;
- `external_blocker`: a named author/institution/release action is still required;
- `regressed`: an earlier closure no longer holds.

Give direct evidence: paths, result IDs, test names and final document location.
Do not copy the remediation ledger's status without rechecking it.

### Phase 6 — refute your own findings

For every FATAL or MAJOR finding and every numeric MINOR finding:

- reread the full passage;
- independently rerun the relevant calculation;
- search the supplement, registry, decisions and provenance;
- ask what evidence would falsify the finding.

Drop refuted findings and list them in an appendix with the reason. Mark matters
that cannot be checked `PLAUSIBLE`; do not present them as established facts.

### Review dimensions

Cover contribution/novelty, reference truth and endpoints, cohort selection and
power, caller deployment, method/code correspondence, statistics, results and
figures, interpretation/limitations, reproducibility/software/data, current BMC
compliance, writing/accessibility and likely referee requests. Prioritize
scientific validity over formatting.

### Outputs

Write exactly three dated files:

1. `reports/final_scientific_review_<YYYYMMDD>.md`
   - candidate identity and hashes;
   - cold-read verdict;
   - strengths to preserve;
   - findings by FATAL/MAJOR/MINOR/EDITORIAL;
   - independent number cross-check;
   - workflow/run provenance audit;
   - BMC compliance and author-side blockers;
   - strongest honest case for rejection;
   - likely referee requests;
   - refuted/dropped findings appendix.
2. `reports/final_scientific_review_<YYYYMMDD>.tsv` with columns:
   `issue_id severity dimension persona verdict location evidence fix compute_needed effort prior_issue status`.
3. `reports/final_closure_audit_<YYYYMMDD>.tsv` with columns:
   `prior_issue prior_status final_status evidence test_or_artifact manuscript_location owner`.

A submission-ready verdict requires:

- no surviving FATAL or MAJOR finding;
- no open scientific/code issue in the closure audit;
- all external blockers resolved, not merely assigned;
- exact agreement among manuscript, registry, artifacts and independent
  recomputation;
- immutable resolving workflow/paper releases and DOIs;
- no provisional author or ethics marker.

Your final message should give the predicted journal decision, finding counts,
remaining blockers and the three output paths. Do not paste the report.

## END PROMPT
