# ChampHLA publication candidate

This is the canonical analysis repository for the ChampHLA benchmark/resource
article. Equal-weight plurality is a transparent development baseline, not a
novel or clinically validated HLA caller. The verified reproducibility boundary begins with
truth-free normalized caller outputs and ends with the manuscript, supplement,
figures, review DOCX and release manifest. Historical raw-read caller execution
is an external dependency and is retained only as a labelled comparison. A new
public-input run from the frozen 130-WES/106-RNA roster through PanelHLA v3.5.0
is in progress; when complete and frozen, that run replaces the historical
normalized calls as the starting boundary for the primary development results.

The live route is the benchmark paper in `manuscripts/benchmark/`. The
conditional method manuscript is **superseded**, not pending: the 2026-09-08
amendment made equal-weight consensus the primary method and demoted
Champion-Challenger to an ablation. See `decisions/publication_route.json`.
Historical WGS performance from the mate-discarding chromosome-6 slice is
invalid and cannot enter a concordance claim, abstract, or figure.

### A note on naming

The project was renamed from **ChampHLA** to **PanelHLA** on 2026-09-17, because
the primary method is no longer Champion-Challenger, and the name **ChampHLA**
was restored on 2026-10-07 (`decisions/20261007_name_restore_champhla.json`).
The primary method is still the equal-weight plurality vote,
`ChampHLA-Consensus`; Champion-Challenger remains an exploratory comparator.
Both renames cover prose and display names only. Checksum-pinned configuration
files keep the display name they were frozen with. The Python packages remain
`champhla_confirmation` and `champhla_recovery`, and selection seeds, schema
version strings, and the immutable records under `decisions/`, `provenance/` and
`cohorts/` keep their original text. Those strings are inputs or checksummed
content rather than labels: renaming them would invalidate artifacts or change
what a frozen roster reproduces. The rationale and the full exclusion list are
in `decisions/20260917_project_rename.json`.

On 2026-10-27 the GitHub repositories moved to the ChampHLA name:
`github.com/uoozcan/ChampHLA-paper` (this repository) and
`github.com/uoozcan/ChampHLA` (the workflow). The workflow release that produced
the evaluated outputs keeps its released name, **PanelHLA v3.5.0** (tag `v3.5.0`,
commit `66d949d`), as do the Roihu deployment paths and archive names derived
from it. The paper repository on GitHub is a scanned snapshot built by
`scripts/publish_snapshot.sh`: its development history stays local because early
commits held controlled-cohort files, and FIMM/VenEx-only artifacts are held back
until their governance is confirmed.

## Scientific boundary

- Research-only HLA-A, HLA-B, and HLA-C typing.
- Exact unordered two-field genotype concordance is primary.
- Only loci with uniquely resolvable laboratory truth enter the locked
  denominator; a subject may contribute one, two, or three A/B/C loci.
- Missing and `no_consensus` calls count as incorrect at the fixed denominator.
- `ChampHLA-Consensus` (internal identifier `SimplePluralityLex`) is the primary
  method: unweighted plurality over the modality-appropriate caller panel.
- In the development analysis, every individual caller, strict majority,
  two-thirds consensus and nested-CV best-single-tool selection appear in the
  main comparison. Champion-Challenger, TwoThirdsGuardedCC, MVFlooredCC,
  MetaConsensus and FamilyGatedCC are fitted exploratory policies reported in
  the supplement and paired-effect figure.
- A singleton allele with an undetermined second allele abstains; generic
  singleton-to-homozygote completion is prohibited.
- The active analysis is retrospective development evidence. It contains no
  independent external validation and no quantitative WGS result.
- The subject-disjoint extension uses the signed v3.5.0 amendment (`04cc6d1`).
  Processing has started but is stopped while the exploratory NCI-60 full-roster
  run takes priority. The failed WES transfer has been classified on author
  instruction; no classification remains pending. Only Umut may approve an
  extension relaunch after the NCI-60 controller reports roster completion.
  No extension performance is reported. The public pre-registration deposit,
  prediction freeze and separately authorized comparison with reference typing
  remain outstanding; no truth join is authorized here.

## Public-input v3.5.0 development rerun

`cohorts/development_rerun_manifest.tsv` is the truth-free execution manifest.
It fixes the original 130 WES and 106 RNA-seq sample/modality pairs, their public
input URLs and checksums, expected assemblies, and restartable batches of no
more than five. It contains no HLA truth or performance outcome. The historical
selection rule could not be reconstructed, so the roster is described as a
convenience/development sample rather than assigned a post hoc rule.

On Roihu, first verify the exact v3.5.0 archive, release commit, tools, reference
assets, manifests and storage:

```bash
bash scripts/audit_development_rerun_readiness.sh
```

The batch manager defaults to a non-mutating dry run. It skips a subject only
after verifying its marker, output inventories, hashes, caller dispositions,
zero Nextflow exit and exact workflow commit. An already-recorded incomplete
submission is never silently resubmitted.

```bash
# Plan one exact batch (no submission).
python3 scripts/manage_development_batches.py submit wes-001 \
  --prune-on-success --max-submit 4

# Submit only after reviewing that plan.
python3 scripts/manage_development_batches.py submit wes-001 \
  --prune-on-success --max-submit 4 --execute

# Validate artifacts; a nonzero exit means at least one sample is incomplete or invalid.
python3 scripts/manage_development_batches.py validate wes-001
```

`development/submission_ledger.tsv` records UTC submission time, batch,
sample/modality, Slurm job, release commit and pruning choice. Pruning occurs
only after results and provenance are hashed and `SAMPLE_COMPLETE` is written.
Rows beyond `--max-submit` are explicitly deferred, not dropped. Use at most two
concurrent RNA-seq samples on the current quota because the accepted RNA smoke
used 29 GB of temporary work; rerun the same batch after those rows validate to
advance to its next rows.
Caller failures remain explicit non-calls. Cluster state is not publication
evidence: final sample manifests, traces, raw-output hashes, parser audits and
the job ledger must be exported into the immutable paper release.

## Locked extension and HLA reference resources

Validate the frozen rosters and the zero-overlap rule:

```bash
validate_benchmark_resource_protocol \
  --protocol configs/benchmark_resource_protocol_v2.json \
  --roster cohorts/frozen_initial_rosters.tsv \
  --exposure-ledger cohorts/subject_exposure_ledger.tsv \
  --output artifacts/benchmark_resource_protocol_audit.json
```

The secondary G-group and nomenclature audits, and the future extension
normalizer, use archived IPD-IMGT/HLA 3.65.0 allele,
renamed/deleted-allele, P-group and G-group files. Reacquire and verify them with:

```bash
bash scripts/fetch_ipd_imgt_hla_365.sh
```

The caller-resource gate is deliberately fail-closed:

```bash
audit_extension_readiness \
  --project-root . \
  --protocol-audit artifacts/benchmark_resource_protocol_audit.json \
  --caller-resources configs/caller_resources_v2.json \
  --output artifacts/extension_readiness.json
```

Do not join extension truth unless that report has `ready=true`.

Frozen extension preparation accepts only complete, truth-free collector output
directories. Each directory must contain `collection_manifest.json`,
`normalized_caller_calls.tsv`, `t1k_parser_provenance.tsv`,
`sample_run_provenance.tsv` and the exact `selected_input_manifest.tsv`; every
recorded SHA-256, the v3.5.0 release commit,
the run roster and the full caller-by-locus grid are checked before predictions
can be frozen. Raw `aggregated_calls.tsv` input is deliberately forbidden for
the frozen roster because it cannot preserve T1K quality dispositions or
caller-native homozygosity provenance. It remains available only for historical
non-frozen dry runs. After exporting all checksummed collection directories:

```bash
python scripts/run_extension.py prepare \
  --collection-dir exported/extension_collection_part001 \
  --collection-dir exported/extension_collection_part002
python scripts/run_extension.py predict
```

Neither command joins truth. `unblind` remains separately protected by the
signed-pre-registration, immutable-release and one-time-join gates.

## Canonical checks

Install the package with every extra the gate uses, download the reference
typing from IGSR and check its pinned SHA-256 (the gate checks it again), then
run the whole gate, which regenerates every scientific output before auditing it:

```bash
python -m pip install -e ".[test,analysis,figures,documents]"
mkdir -p runtime_data/public_truth
curl -fsSL -o runtime_data/public_truth/20140702_hla_diversity.txt https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/technical/working/20140725_hla_genotypes/20140702_hla_diversity.txt
echo "0455d0302ac12a29ab87091cab5e3e557416f6301e89fb122eef8d49cd5644ec  runtime_data/public_truth/20140702_hla_diversity.txt" | sha256sum -c -
curl -fsSL -o runtime_data/public_truth/20181129_HLA_types_full_1000_Genomes_Project_panel.txt https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/data_collections/HLA_types/20181129_HLA_types_full_1000_Genomes_Project_panel.txt
echo "570b5cc5523273826a5695452f18b77f8742e568e1e35a34aed5d2a313472e8e  runtime_data/public_truth/20181129_HLA_types_full_1000_Genomes_Project_panel.txt" | sha256sum -c -
bash scripts/run_local_verification.sh
```

The second file is the in silico retyping used only to adjudicate consensus
errors (Abi-Rached et al. 2018); a release run requires it. `PUBLIC_TRUTH` overrides the default path above. Set `RESTORED_CALLER_SOURCE` to the
recovered `harmonized_population_enriched.tsv` (checksum pinned in
`data/development/input_manifest.json`) to rerun the S12 restored analyses inside
the gate; a release run requires it.

What needs more than a laptop:

- The development results, tables, figures and claim audits need only the
  public reference typing above.
- Caller execution (raw reads to caller outputs) uses the separate workflow
  repository and was run on CSC Roihu; it is not part of this gate.
- The exploratory FIMM and VenEx aggregates are regenerated only inside the
  controlled environment that holds the patient data; the repository carries
  the aggregates and their checksums, never row-level data.
- Earlier NCI-60 estimates were withdrawn (Supplementary S9). The pilot has
  completed and the full-roster workflow run is in progress; its results are
  awaited for this submission. This local gate does not run the NCI-60 workflow
  or compare that roster with reference typing.

For a quick developer pass, reduce resampling and optionally skip tests:

```bash
PUBLIC_TRUTH=/path/to/20140702_hla_diversity.txt BOOTSTRAP=2000 \
  POWER_ITERATIONS=200 SKIP_TESTS=1 bash scripts/run_local_verification.sh
```

The release gate forbids skipped tests and reduced resampling. It may finish
with the explicit consolidated author/archive-input blocker; `SUBMISSION=1`
also makes those fields fatal:

```bash
PUBLIC_TRUTH=/path/to/20140702_hla_diversity.txt RELEASE=1 \
  bash scripts/run_local_verification.sh
PUBLIC_TRUTH=/path/to/20140702_hla_diversity.txt RELEASE=1 SUBMISSION=1 \
  bash scripts/run_local_verification.sh
```

The full joins remain under ignored `runtime_data/`. The release contains the
truth-free normalized calls, acquisition/checksum code, generated results and
`artifacts/development_corrected/per_locus_results.tsv`: every method's call at
every exact-endpoint locus with the public 2014 reference genotype and whether
they agree. Both inputs are public.

## Roihu CPU environment

The CSC module stack changes the active Python only after `samtools/1.21` is
loaded. Use the checked setup script rather than creating a virtual environment
from the login-shell Python:

```bash
bash scripts/setup_roihu_test_env.sh
.venv/bin/python -m pytest -q
```

The script requires Python 3.11.15, installs the pinned test, analysis, figure
and document-generation extras inside `.venv`, records the exact environment,
and never changes the system Python. GPU RefFormer training is not part of this
release route.

Current single-sample workflow smoke provenance is stored under
`provenance/compute_smoke/`. It is intentionally separated from development
accuracy results and must not be interpreted as historical cohort resource use,
WES runtime, monetary cost or a scaling estimate.
