# ChampHLA WGS diagnosis, 2026-09-01

Phase 1 of the approved plan. Evidence comes from the surviving publication-run tables at
`/scratch/project_2008084/pihla-publish/analysis/benchmark_{wgs,wes,rna}_all_samples/tables/harmonized_benchmark_rows.tsv`,
which record each tool's **raw** output (`allele1_raw`, `allele2_raw`) alongside the
**harmonised** call (`allele1`, `allele2`). That pairing is what makes the diagnosis possible.

## Confirmed defect: a no-call second allele is converted into a homozygous genotype

When a tool cannot determine the second allele it writes a placeholder (`-`). ChampHLA's
harmonisation replaces that placeholder with **a copy of the first allele**, producing a
confident homozygous genotype from what was actually a partial call.

The conversion is total — `dup-from-nocall` equals the `-` count exactly, for every tool in
every modality:

| modality | tool | callable class-I rows | `allele2_raw` = `-` | became homozygous |
|---|---|---|---|---|
| WGS | HLA-HD | 363 | 193 (53%) | 193 |
| WGS | T1K | 363 | 145 (40%) | 145 |
| WGS | ArcasHLA | 363 | 9 | 9 |
| WES | HLA-HD | 1086 | 270 (25%) | 270 |
| WES | T1K | 1083 | 208 (19%) | 208 |
| RNA | ArcasHLA / HLA-HD / T1K | ~950 | 92 | 92 |
| **all** | **OptiType** | 1899 | **0** | **0** |

**The damage.** Of the 311 WGS no-call rows, the truth is heterozygous in **80.4%**; the
manufactured homozygous call is correct only **17.0%** of the time. Yet the single allele the
tool did report is genuinely one of the person's two in **85.5%** of cases. The tools are right
about what they know; the harmoniser is wrong about what they did not know.

WES is affected too (492 rows, 55.3% heterozygous truth, duplicated call correct 42.5%), and RNA
least (92 rows).

Excluding only the defective rows raises per-tool WGS accuracy immediately:

| tool (WGS class I) | all callable | excluding no-call rows |
|---|---|---|
| HLA-HD | 0.264 | **0.335** |
| T1K | 0.325 | **0.427** |
| OptiType | 0.500 | 0.500 (never emits `-`) |

## Second, smaller mechanism: two higher-field alleles from one two-field group

Kourami and SpecHLA sometimes report two distinct 4-field alleles that collapse to the same
2-field group (e.g. HG00096 SpecHLA `A*01:01:01:01 | A*01:01:20` → `A*01:01 | A*01:01`, truth
`A*01:01 | A*29:02`). WGS SpecHLA 59/253, Kourami 27/245.

Combined share of callable class-I calls that become **false homozygous**:
**WGS 20.5%**, WES 10.0%, RNA 6.8%.

This is why WGS MajorityVote calls homozygous 58.3% of the time against 13.4% truth.

## A residual WGS problem the bug does *not* explain

OptiType emits no `-` placeholders and no same-group collapses, yet still scores **0.500** on WGS
against **0.92** on WES. So a second, independent WGS issue remains. Note also that class II works
on WGS (HLA-HD DRB1 0.833, Kourami DRB1 0.881) while class I collapses, which argues against a
simple read-starvation explanation and points at something class I-specific in the WGS path.

The raw per-tool WGS outputs have been cleaned from `/scratch/project_2008084/hla_calibration/`
(only 6 `*_optitype.txt` survive anywhere), so this second question cannot be closed from
existing artifacts and needs a re-run of a few samples.

## What this means for the manuscript

- The WGS baseline is depressed by a **ChampHLA-side harmonisation defect**, not solely by tool
  behaviour. MajorityVote suffers most because it aggregates the tools that emit `-` most often.
- Table 9's "MV-called homozygous" overlay (239 loci, MajorityVote 0.188) is largely this defect.
- The correct handling is to treat a `-` second allele as a **partial call**, not a homozygous
  genotype — either excluded from the vote for that locus or voting only for the allele it
  actually determined.
- Because the defect is present in WES and RNA as well (10.0% and 6.8% of calls), **all three
  modalities need re-running after the fix**, not just WGS.
