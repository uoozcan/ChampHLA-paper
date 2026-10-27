# Supplementary material

Supporting methods and complete development results for *Benchmarking consensus HLA class I genotyping from exome and RNA sequencing with ChampHLA*. Tables report results from the accompanying versioned data files.
Numerical citations continue the reference numbering of the main manuscript.

## S1. Cohort and reference-source audit

The documented v3.5.0 rerun roster had 390 WES loci from 130 subjects and 318
RNA-seq loci from 106 subjects. The roster excludes NA07000 RNA-seq because the historical input was absent from the official assay manifest and failed cross-assay identity checks (Methods; decisions/20261008_identity_check_na07000.json). Every rerun input is in the manifest. `artifacts/development_characterisation/identity_check.tsv` contains identity evidence for every rerun subject. `provenance/development_rerun_v350/historical_artifacts/` retains the withheld input's historical evidence. The public reference-genotype parser retained a locus only when all
reported ambiguity alternatives collapsed to one unordered two-field genotype.
Excluding loci with any ambiguous, invalid or conflicting reference record retained 153 WES loci from 63 subjects and 118 RNA-seq loci from 51 subjects. The filtered sets shared 50 subjects. The set-valued secondary endpoint retained
335 WES and 263 RNA-seq loci with at least one parseable candidate genotype.

Populations use the 1000 Genomes codes: CEU (Utah residents with Northern and
Western European ancestry), YRI (Yoruba in Ibadan, Nigeria), CHB (Han Chinese in
Beijing), JPT (Japanese in Tokyo), FIN (Finnish), GBR (British), TSI (Toscani in
Italy) and PUR (Puerto Rican). The 2014 reference table labels the CEU samples
"CEPH" and pools CHB and JPT as "CHB+JPT"; tables derived from it keep those
labels. Candidate-occurrence bounds are internal benchmark counts, not
population allele frequencies.

<!-- BEGIN GENERATED COHORT TABLE -->
| Assay | Requested subjects | Requested loci | Retained subjects | Retained loci | Excluded loci | Retained cross-assay overlap |
|---|---:|---:|---:|---:|---:|---:|
| WES | 130 | 390 | 63 | 153 | 237 | 50 |
| RNA-seq | 106 | 318 | 51 | 118 | 200 | 50 |
<!-- END GENERATED COHORT TABLE -->

<!-- BEGIN GENERATED TRUTH FLOW TABLE -->
| Assay | Source-truth state | Loci | Requested loci |
|---|---|---:|---:|
| WES | resolved | 153 | 390 |
| WES | ambiguous | 182 | 390 |
| WES | invalid | 1 | 390 |
| WES | absent | 54 | 390 |
| RNA-seq | resolved | 118 | 318 |
| RNA-seq | ambiguous | 145 | 318 |
| RNA-seq | invalid | 1 | 318 |
| RNA-seq | absent | 54 | 318 |
<!-- END GENERATED TRUTH FLOW TABLE -->

<!-- BEGIN GENERATED EXCLUSION TABLE -->
| Assay | Gene | Source population | Resolved | Ambiguous | Invalid | Absent | Total | Exact retention, % |
|---|---|---|---:|---:|---:|---:|---:|---:|
| RNA-seq | HLA-A | CEPH | 23 | 0 | 0 | 0 | 23 | 100.0 |
| RNA-seq | HLA-A | FIN | 0 | 17 | 0 | 0 | 17 | 0.0 |
| RNA-seq | HLA-A | GBR | 0 | 18 | 0 | 0 | 18 | 0.0 |
| RNA-seq | HLA-A | TSI | 0 | 13 | 0 | 0 | 13 | 0.0 |
| RNA-seq | HLA-A | YRI | 15 | 2 | 0 | 0 | 17 | 88.2 |
| RNA-seq | HLA-A | unknown | 0 | 0 | 0 | 18 | 18 | 0.0 |
| RNA-seq | HLA-B | CEPH | 19 | 4 | 0 | 0 | 23 | 82.6 |
| RNA-seq | HLA-B | FIN | 0 | 17 | 0 | 0 | 17 | 0.0 |
| RNA-seq | HLA-B | GBR | 1 | 17 | 0 | 0 | 18 | 5.6 |
| RNA-seq | HLA-B | TSI | 5 | 8 | 0 | 0 | 13 | 38.5 |
| RNA-seq | HLA-B | YRI | 15 | 2 | 0 | 0 | 17 | 88.2 |
| RNA-seq | HLA-B | unknown | 0 | 0 | 0 | 18 | 18 | 0.0 |
| RNA-seq | HLA-C | CEPH | 17 | 5 | 1 | 0 | 23 | 73.9 |
| RNA-seq | HLA-C | FIN | 2 | 15 | 0 | 0 | 17 | 11.8 |
| RNA-seq | HLA-C | GBR | 3 | 15 | 0 | 0 | 18 | 16.7 |
| RNA-seq | HLA-C | TSI | 2 | 11 | 0 | 0 | 13 | 15.4 |
| RNA-seq | HLA-C | YRI | 16 | 1 | 0 | 0 | 17 | 94.1 |
| RNA-seq | HLA-C | unknown | 0 | 0 | 0 | 18 | 18 | 0.0 |
| WES | HLA-A | CEPH | 24 | 0 | 0 | 0 | 24 | 100.0 |
| WES | HLA-A | CHB+JPT | 5 | 5 | 0 | 0 | 10 | 50.0 |
| WES | HLA-A | FIN | 0 | 17 | 0 | 0 | 17 | 0.0 |
| WES | HLA-A | GBR | 0 | 17 | 0 | 0 | 17 | 0.0 |
| WES | HLA-A | PUR | 0 | 8 | 0 | 0 | 8 | 0.0 |
| WES | HLA-A | TSI | 0 | 13 | 0 | 0 | 13 | 0.0 |
| WES | HLA-A | YRI | 21 | 2 | 0 | 0 | 23 | 91.3 |
| WES | HLA-A | unknown | 0 | 0 | 0 | 18 | 18 | 0.0 |
| WES | HLA-B | CEPH | 20 | 4 | 0 | 0 | 24 | 83.3 |
| WES | HLA-B | CHB+JPT | 5 | 5 | 0 | 0 | 10 | 50.0 |
| WES | HLA-B | FIN | 0 | 17 | 0 | 0 | 17 | 0.0 |
| WES | HLA-B | GBR | 0 | 17 | 0 | 0 | 17 | 0.0 |
| WES | HLA-B | PUR | 1 | 7 | 0 | 0 | 8 | 12.5 |
| WES | HLA-B | TSI | 5 | 8 | 0 | 0 | 13 | 38.5 |
| WES | HLA-B | YRI | 21 | 2 | 0 | 0 | 23 | 91.3 |
| WES | HLA-B | unknown | 0 | 0 | 0 | 18 | 18 | 0.0 |
| WES | HLA-C | CEPH | 17 | 6 | 1 | 0 | 24 | 70.8 |
| WES | HLA-C | CHB+JPT | 5 | 5 | 0 | 0 | 10 | 50.0 |
| WES | HLA-C | FIN | 2 | 15 | 0 | 0 | 17 | 11.8 |
| WES | HLA-C | GBR | 2 | 15 | 0 | 0 | 17 | 11.8 |
| WES | HLA-C | PUR | 1 | 7 | 0 | 0 | 8 | 12.5 |
| WES | HLA-C | TSI | 2 | 11 | 0 | 0 | 13 | 15.4 |
| WES | HLA-C | YRI | 22 | 1 | 0 | 0 | 23 | 95.7 |
| WES | HLA-C | unknown | 0 | 0 | 0 | 18 | 18 | 0.0 |
<!-- END GENERATED EXCLUSION TABLE -->

The public source is
`20140702_hla_diversity.txt`, obtained from the IGSR 2014 HLA technical
directory. Its required SHA-256 is
`0455d0302ac12a29ab87091cab5e3e557416f6301e89fb122eef8d49cd5644ec`.
The selection manifest records each excluded subject–assay–gene key. Because many loci were excluded, exact results apply only to uniquely resolved reference loci. Retained-versus-excluded comparisons use gene, population,
reference-typing state and candidate-pair count. Candidate-occurrence bounds are benchmark counts, not population allele frequencies.
Retention was strongly population-dependent: after pooling genes, exact truth
was retained for 84.7% of CEU (CEPH) and 92.8% of YRI WES source-present loci, but
only 3.9% of FIN, 3.9% of GBR and 8.3% of PUR loci. The corresponding RNA-seq
rates were 85.5%, 90.2%, 3.9% and 7.4% for CEU, YRI, FIN and GBR
[RESULT:DEV_TRUTH_RETENTION_RNASEQ_CEPH]. These are
properties of the 2014 truth representation, not biological population
accuracy estimates.

<!-- BEGIN GENERATED COMPATIBILITY TABLE -->
| Assay | Method | Compatibility endpoint | Compatible | Concordance, % (95% CI) |
|---|---|---|---:|---:|
| RNA-seq | Algorithm-family-restricted champion–challenger | Allowed two-field candidate | 248/263 | 94.3 (91.2–97.0) |
| RNA-seq | Best single caller (nested CV) | Allowed two-field candidate | 253/263 | 96.2 (93.9–98.1) |
| RNA-seq | ChampHLA-Consensus | Allowed two-field candidate | 257/263 | 97.7 (95.8–99.2) |
| RNA-seq | Champion–challenger | Allowed two-field candidate | 256/263 | 97.3 (95.4–99.2) |
| RNA-seq | HLA-HD | Allowed two-field candidate | 254/263 | 96.6 (94.3–98.5) |
| RNA-seq | Logistic meta-consensus | Allowed two-field candidate | 256/263 | 97.3 (95.4–99.2) |
| RNA-seq | OptiType | Allowed two-field candidate | 255/263 | 97.0 (94.7–98.9) |
| RNA-seq | Strict majority | Allowed two-field candidate | 235/263 | 89.4 (85.5–92.8) |
| RNA-seq | T1K | Allowed two-field candidate | 230/263 | 87.5 (83.3–91.3) |
| RNA-seq | Two-thirds consensus | Allowed two-field candidate | 235/263 | 89.4 (85.5–92.8) |
| RNA-seq | Two-thirds-guarded champion–challenger | Allowed two-field candidate | 256/263 | 97.3 (95.4–99.2) |
| RNA-seq | Vote-support-restricted champion–challenger | Allowed two-field candidate | 257/263 | 97.7 (95.8–99.2) |
| RNA-seq | arcasHLA | Allowed two-field candidate | 114/263 | 43.3 (37.6–48.9) |
| WES | Algorithm-family-restricted champion–challenger | Allowed two-field candidate | 320/335 | 95.5 (93.4–97.6) |
| WES | Best single caller (nested CV) | Allowed two-field candidate | 318/335 | 94.9 (92.5–97.0) |
| WES | ChampHLA-Consensus | Allowed two-field candidate | 321/335 | 95.8 (93.7–97.6) |
| WES | Champion–challenger | Allowed two-field candidate | 320/335 | 95.5 (93.4–97.6) |
| WES | HLA-HD | Allowed two-field candidate | 282/335 | 84.2 (79.4–88.7) |
| WES | Logistic meta-consensus | Allowed two-field candidate | 319/335 | 95.2 (92.8–97.3) |
| WES | OptiType | Allowed two-field candidate | 318/335 | 94.9 (92.5–97.0) |
| WES | POLYSOLVER | Allowed two-field candidate | 306/335 | 91.3 (88.4–94.0) |
| WES | SpecHLA | Allowed two-field candidate | 291/335 | 86.9 (82.7–90.7) |
| WES | Strict majority | Allowed two-field candidate | 312/335 | 93.1 (90.2–95.8) |
| WES | T1K | Allowed two-field candidate | 285/335 | 85.1 (81.1–88.9) |
| WES | Two-thirds consensus | Allowed two-field candidate | 293/335 | 87.5 (83.5–91.3) |
| WES | Two-thirds-guarded champion–challenger | Allowed two-field candidate | 320/335 | 95.5 (93.4–97.6) |
| WES | Vote-support-restricted champion–challenger | Allowed two-field candidate | 321/335 | 95.8 (93.7–97.6) |
| RNA-seq | Algorithm-family-restricted champion–challenger | G-compatible under a two-field mapping | 247/261 | 94.6 (91.5–97.3) |
| RNA-seq | Best single caller (nested CV) | G-compatible under a two-field mapping | 253/261 | 96.9 (94.7–98.9) |
| RNA-seq | ChampHLA-Consensus | G-compatible under a two-field mapping | 256/261 | 98.1 (96.2–99.6) |
| RNA-seq | Champion–challenger | G-compatible under a two-field mapping | 255/261 | 97.7 (95.8–99.2) |
| RNA-seq | HLA-HD | G-compatible under a two-field mapping | 254/261 | 97.3 (95.4–99.2) |
| RNA-seq | Logistic meta-consensus | G-compatible under a two-field mapping | 255/261 | 97.7 (95.8–99.2) |
| RNA-seq | OptiType | G-compatible under a two-field mapping | 254/261 | 97.3 (95.4–99.2) |
| RNA-seq | Strict majority | G-compatible under a two-field mapping | 234/261 | 89.7 (85.8–93.2) |
| RNA-seq | T1K | G-compatible under a two-field mapping | 239/261 | 91.6 (87.8–95.0) |
| RNA-seq | Two-thirds consensus | G-compatible under a two-field mapping | 234/261 | 89.7 (85.8–93.2) |
| RNA-seq | Two-thirds-guarded champion–challenger | G-compatible under a two-field mapping | 255/261 | 97.7 (95.8–99.2) |
| RNA-seq | Vote-support-restricted champion–challenger | G-compatible under a two-field mapping | 256/261 | 98.1 (96.2–99.6) |
| RNA-seq | arcasHLA | G-compatible under a two-field mapping | 172/261 | 65.9 (60.7–71.0) |
| WES | Algorithm-family-restricted champion–challenger | G-compatible under a two-field mapping | 324/333 | 97.3 (95.5–98.8) |
| WES | Best single caller (nested CV) | G-compatible under a two-field mapping | 320/333 | 96.1 (93.7–98.2) |
| WES | ChampHLA-Consensus | G-compatible under a two-field mapping | 324/333 | 97.3 (95.5–98.8) |
| WES | Champion–challenger | G-compatible under a two-field mapping | 324/333 | 97.3 (95.5–98.8) |
| WES | HLA-HD | G-compatible under a two-field mapping | 284/333 | 85.3 (80.6–89.6) |
| WES | Logistic meta-consensus | G-compatible under a two-field mapping | 323/333 | 97.0 (94.9–98.8) |
| WES | OptiType | G-compatible under a two-field mapping | 320/333 | 96.1 (93.7–98.2) |
| WES | POLYSOLVER | G-compatible under a two-field mapping | 310/333 | 93.1 (90.4–95.5) |
| WES | SpecHLA | G-compatible under a two-field mapping | 293/333 | 88.0 (83.8–91.8) |
| WES | Strict majority | G-compatible under a two-field mapping | 314/333 | 94.3 (91.5–96.7) |
| WES | T1K | G-compatible under a two-field mapping | 293/333 | 88.0 (84.2–91.6) |
| WES | Two-thirds consensus | G-compatible under a two-field mapping | 295/333 | 88.6 (84.6–92.2) |
| WES | Two-thirds-guarded champion–challenger | G-compatible under a two-field mapping | 324/333 | 97.3 (95.5–98.8) |
| WES | Vote-support-restricted champion–challenger | G-compatible under a two-field mapping | 324/333 | 97.3 (95.5–98.8) |
| RNA-seq | Algorithm-family-restricted champion–challenger | P-group-compatible under a two-field mapping | 247/261 | 94.6 (91.5–97.3) |
| RNA-seq | Best single caller (nested CV) | P-group-compatible under a two-field mapping | 253/261 | 96.9 (94.7–98.9) |
| RNA-seq | ChampHLA-Consensus | P-group-compatible under a two-field mapping | 256/261 | 98.1 (96.2–99.6) |
| RNA-seq | Champion–challenger | P-group-compatible under a two-field mapping | 255/261 | 97.7 (95.8–99.2) |
| RNA-seq | HLA-HD | P-group-compatible under a two-field mapping | 254/261 | 97.3 (95.4–99.2) |
| RNA-seq | Logistic meta-consensus | P-group-compatible under a two-field mapping | 255/261 | 97.7 (95.8–99.2) |
| RNA-seq | OptiType | P-group-compatible under a two-field mapping | 254/261 | 97.3 (95.4–99.2) |
| RNA-seq | Strict majority | P-group-compatible under a two-field mapping | 234/261 | 89.7 (85.8–93.2) |
| RNA-seq | T1K | P-group-compatible under a two-field mapping | 230/261 | 88.1 (84.0–92.0) |
| RNA-seq | Two-thirds consensus | P-group-compatible under a two-field mapping | 234/261 | 89.7 (85.8–93.2) |
| RNA-seq | Two-thirds-guarded champion–challenger | P-group-compatible under a two-field mapping | 255/261 | 97.7 (95.8–99.2) |
| RNA-seq | Vote-support-restricted champion–challenger | P-group-compatible under a two-field mapping | 256/261 | 98.1 (96.2–99.6) |
| RNA-seq | arcasHLA | P-group-compatible under a two-field mapping | 165/261 | 63.2 (57.6–68.7) |
| WES | Algorithm-family-restricted champion–challenger | P-group-compatible under a two-field mapping | 324/333 | 97.3 (95.5–98.8) |
| WES | Best single caller (nested CV) | P-group-compatible under a two-field mapping | 320/333 | 96.1 (93.8–98.2) |
| WES | ChampHLA-Consensus | P-group-compatible under a two-field mapping | 324/333 | 97.3 (95.5–98.8) |
| WES | Champion–challenger | P-group-compatible under a two-field mapping | 324/333 | 97.3 (95.5–98.8) |
| WES | HLA-HD | P-group-compatible under a two-field mapping | 284/333 | 85.3 (80.6–89.6) |
| WES | Logistic meta-consensus | P-group-compatible under a two-field mapping | 323/333 | 97.0 (94.9–98.8) |
| WES | OptiType | P-group-compatible under a two-field mapping | 320/333 | 96.1 (93.7–98.2) |
| WES | POLYSOLVER | P-group-compatible under a two-field mapping | 310/333 | 93.1 (90.4–95.5) |
| WES | SpecHLA | P-group-compatible under a two-field mapping | 293/333 | 88.0 (83.8–91.8) |
| WES | Strict majority | P-group-compatible under a two-field mapping | 314/333 | 94.3 (91.5–96.7) |
| WES | T1K | P-group-compatible under a two-field mapping | 290/333 | 87.1 (83.2–90.7) |
| WES | Two-thirds consensus | P-group-compatible under a two-field mapping | 295/333 | 88.6 (84.5–92.2) |
| WES | Two-thirds-guarded champion–challenger | P-group-compatible under a two-field mapping | 324/333 | 97.3 (95.5–98.8) |
| WES | Vote-support-restricted champion–challenger | P-group-compatible under a two-field mapping | 324/333 | 97.3 (95.5–98.8) |
<!-- END GENERATED COMPATIBILITY TABLE -->

Two-field compatibility counts a call when it equals any allowed unordered
candidate genotype. The P- and G-group sensitivities map each two-field designation to all compatible official IPD-IMGT/HLA 3.65.0 groups of that kind. They test a bijective set intersection across the two alleles. They are
compatibility analyses under a two-field mapping, not exact P- or G-group calls.
Two reference loci per assay could not be mapped for either endpoint; these exclusions remain explicit. Every method is reported for all three set-valued endpoints.

Subject-level paired inference for the set-valued two-field endpoint used the
same fixed locus denominator as the compatibility estimates. Positive
differences favour ChampHLA-Consensus. We enumerated two-sided sign assignments exactly through 25 nonzero subjects, otherwise sampling 1,000,000 plus-one-corrected assignments. We applied Holm adjustment within each assay and predeclared descriptive or fitted comparator family.

<!-- BEGIN GENERATED AMBIGUITY PAIRED TABLE -->
| Assay | Comparator | Family | ChampHLA compatible | Comparator compatible | Difference, points | Wins/losses | Raw sign-flip p | Holm p | Test |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| WES | HLA-HD | descriptive comparator | 321/335 | 282/335 | 11.64 | 39/0 | 1.00e-06 | 6.00e-06 | monte carlo plus one |
| WES | OptiType | descriptive comparator | 321/335 | 318/335 | 0.90 | 4/1 | 0.5 | 0.5 | exact enumeration |
| WES | POLYSOLVER | descriptive comparator | 321/335 | 306/335 | 4.48 | 18/3 | 0.001 | 0.004 | exact enumeration |
| WES | SpecHLA | descriptive comparator | 321/335 | 291/335 | 8.96 | 33/3 | 2.00e-06 | 8.00e-06 | monte carlo plus one |
| WES | Strict majority | descriptive comparator | 321/335 | 312/335 | 2.69 | 9/0 | 0.004 | 0.008 | exact enumeration |
| WES | T1K | descriptive comparator | 321/335 | 285/335 | 10.75 | 39/3 | 1.00e-06 | 6.00e-06 | monte carlo plus one |
| WES | Two-thirds consensus | descriptive comparator | 321/335 | 293/335 | 8.36 | 28/0 | 1.19e-07 | 8.34e-07 | exact enumeration |
| WES | Algorithm-family-restricted champion–challenger | exploratory fitted | 321/335 | 320/335 | 0.30 | 2/1 | 1 | 1 | exact enumeration |
| WES | Best single caller (nested CV) | exploratory fitted | 321/335 | 318/335 | 0.90 | 4/1 | 0.5 | 1 | exact enumeration |
| WES | Champion–challenger | exploratory fitted | 321/335 | 320/335 | 0.30 | 2/1 | 1 | 1 | exact enumeration |
| WES | Logistic meta-consensus | exploratory fitted | 321/335 | 319/335 | 0.60 | 3/1 | 0.75 | 1 | exact enumeration |
| WES | Two-thirds-guarded champion–challenger | exploratory fitted | 321/335 | 320/335 | 0.30 | 2/1 | 1 | 1 | exact enumeration |
| WES | Vote-support-restricted champion–challenger | exploratory fitted | 321/335 | 321/335 | 0.00 | 0/0 | 1 | 1 | exact enumeration |
| RNA-seq | HLA-HD | descriptive comparator | 257/263 | 254/263 | 1.14 | 3/0 | 0.25 | 0.5 | exact enumeration |
| RNA-seq | OptiType | descriptive comparator | 257/263 | 255/263 | 0.76 | 2/0 | 0.5 | 0.5 | exact enumeration |
| RNA-seq | Strict majority | descriptive comparator | 257/263 | 235/263 | 8.37 | 22/0 | 1.91e-06 | 7.63e-06 | exact enumeration |
| RNA-seq | T1K | descriptive comparator | 257/263 | 230/263 | 10.27 | 27/0 | 1.19e-07 | 7.15e-07 | exact enumeration |
| RNA-seq | Two-thirds consensus | descriptive comparator | 257/263 | 235/263 | 8.37 | 22/0 | 1.91e-06 | 7.63e-06 | exact enumeration |
| RNA-seq | arcasHLA | descriptive comparator | 257/263 | 114/263 | 54.37 | 143/0 | 1.00e-06 | 5.00e-06 | monte carlo plus one |
| RNA-seq | Algorithm-family-restricted champion–challenger | exploratory fitted | 257/263 | 248/263 | 3.42 | 9/0 | 0.008 | 0.039 | exact enumeration |
| RNA-seq | Best single caller (nested CV) | exploratory fitted | 257/263 | 253/263 | 1.52 | 4/0 | 0.125 | 0.5 | exact enumeration |
| RNA-seq | Champion–challenger | exploratory fitted | 257/263 | 256/263 | 0.38 | 1/0 | 1 | 1 | exact enumeration |
| RNA-seq | Logistic meta-consensus | exploratory fitted | 257/263 | 256/263 | 0.38 | 1/0 | 1 | 1 | exact enumeration |
| RNA-seq | Two-thirds-guarded champion–challenger | exploratory fitted | 257/263 | 256/263 | 0.38 | 1/0 | 1 | 1 | exact enumeration |
| RNA-seq | Vote-support-restricted champion–challenger | exploratory fitted | 257/263 | 257/263 | 0.00 | 0/0 | 1 | 1 | exact enumeration |
<!-- END GENERATED AMBIGUITY PAIRED TABLE -->

[RESULT:DEV_AMBIGUITY_PAIRED_WES_BESTSINGLETOOL_NESTEDCV]
[RESULT:DEV_AMBIGUITY_PAIRED_RNASEQ_BESTSINGLETOOL_NESTEDCV]

By retaining only uniquely resolved reference typings, the exact endpoint also selects which subjects and populations are scored. The next table reports two-field compatibility separately for retained loci, where it equals exact concordance, and excluded loci with scoreable ambiguous typing. The profile table compares population composition, panel-caller agreement and the number of candidate genotypes per excluded locus without using truth labels. Compatibility on excluded
loci is lenient, because any allowed candidate counts.

<!-- BEGIN GENERATED TRUTH SELECTION TABLE -->
| Assay | Method | Retained exact loci, correct (%) | Excluded ambiguous loci, compatible (%) |
|---|---|---:|---:|
| WES | ChampHLA-Consensus | 143/153 (93.5) | 178/182 (97.8) |
| WES | Algorithm-family-restricted champion–challenger | 141/153 (92.2) | 179/182 (98.4) |
| WES | Best single caller (nested CV) | 142/153 (92.8) | 176/182 (96.7) |
| WES | Champion–challenger | 141/153 (92.2) | 179/182 (98.4) |
| WES | Logistic meta-consensus | 140/153 (91.5) | 179/182 (98.4) |
| WES | Strict majority | 141/153 (92.2) | 171/182 (94.0) |
| WES | Two-thirds consensus | 136/153 (88.9) | 157/182 (86.3) |
| WES | Two-thirds-guarded champion–challenger | 141/153 (92.2) | 179/182 (98.4) |
| WES | Vote-support-restricted champion–challenger | 143/153 (93.5) | 178/182 (97.8) |
| WES | HLA-HD | 131/153 (85.6) | 151/182 (83.0) |
| WES | OptiType | 142/153 (92.8) | 176/182 (96.7) |
| WES | POLYSOLVER | 138/153 (90.2) | 168/182 (92.3) |
| WES | SpecHLA | 134/153 (87.6) | 157/182 (86.3) |
| WES | T1K | 125/153 (81.7) | 160/182 (87.9) |
| RNA-seq | ChampHLA-Consensus | 113/118 (95.8) | 144/145 (99.3) |
| RNA-seq | Algorithm-family-restricted champion–challenger | 109/118 (92.4) | 139/145 (95.9) |
| RNA-seq | Best single caller (nested CV) | 111/118 (94.1) | 142/145 (97.9) |
| RNA-seq | Champion–challenger | 113/118 (95.8) | 143/145 (98.6) |
| RNA-seq | Logistic meta-consensus | 113/118 (95.8) | 143/145 (98.6) |
| RNA-seq | Strict majority | 106/118 (89.8) | 129/145 (89.0) |
| RNA-seq | Two-thirds consensus | 106/118 (89.8) | 129/145 (89.0) |
| RNA-seq | Two-thirds-guarded champion–challenger | 113/118 (95.8) | 143/145 (98.6) |
| RNA-seq | Vote-support-restricted champion–challenger | 113/118 (95.8) | 144/145 (99.3) |
| RNA-seq | HLA-HD | 112/118 (94.9) | 142/145 (97.9) |
| RNA-seq | OptiType | 112/118 (94.9) | 143/145 (98.6) |
| RNA-seq | T1K | 101/118 (85.6) | 129/145 (89.0) |
| RNA-seq | arcasHLA | 58/118 (49.2) | 56/145 (38.6) |
<!-- END GENERATED TRUTH SELECTION TABLE -->

<!-- BEGIN GENERATED TRUTH SELECTION PROFILE TABLE -->
| Assay | Reference loci | Loci | Subjects | CEU or YRI loci (%) | Caller-unanimous loci (%) | Median candidate pairs |
|---|---|---:|---:|---:|---:|---:|
| WES | retained (resolved) | 153 | 63 | 125 (81.7) | 104 (68.0) | 1.0 |
| WES | excluded (ambiguous) | 182 | 72 | 15 (8.2) | 111 (61.0) | 7.5 |
| RNA-seq | retained (resolved) | 118 | 51 | 105 (89.0) | 53 (44.9) | 1.0 |
| RNA-seq | excluded (ambiguous) | 145 | 59 | 14 (9.7) | 49 (33.8) | 8.0 |
<!-- END GENERATED TRUTH SELECTION PROFILE TABLE -->

## S2. Complete method performance

Scope is one of `primary`, `descriptive_comparator`, or `exploratory_fitted`.
Individual callers are descriptive comparisons. Callability and
concordance use the same fixed truth denominator. Intervals are 95% subject-cluster percentile bootstrap intervals. Estimates of 0% or 100% use exact Clopper–Pearson intervals because a bootstrap would collapse to a point.

<!-- BEGIN GENERATED PERFORMANCE TABLE -->
| Assay | Method | Scope | Callable (95% CI) | Genotypes correct | Fixed-denominator genotype %, 95% CI | Called-only genotype %, 95% CI | Alleles correct | Allele %, 95% CI |
|---|---|---|---:|---:|---:|---:|---:|---:|
| RNA-seq | Best single caller (nested CV) | exploratory fitted | 118/118 (96.9–100.0) | 111/118 | 94.1 (89.9–97.6) | 94.1 (89.9–97.6) | 229/236 | 97.0 (95.0–98.8) |
| RNA-seq | arcasHLA | descriptive comparator | 118/118 (96.9–100.0) | 58/118 | 49.2 (40.9–57.1) | 49.2 (40.9–57.1) | 148/236 | 62.7 (55.8–69.2) |
| RNA-seq | HLA-HD | descriptive comparator | 118/118 (96.9–100.0) | 112/118 | 94.9 (91.0–98.3) | 94.9 (91.0–98.3) | 230/236 | 97.5 (95.5–99.2) |
| RNA-seq | OptiType | descriptive comparator | 118/118 (96.9–100.0) | 112/118 | 94.9 (91.0–98.3) | 94.9 (91.0–98.3) | 230/236 | 97.5 (95.5–99.2) |
| RNA-seq | T1K | descriptive comparator | 118/118 (96.9–100.0) | 101/118 | 85.6 (79.0–91.7) | 85.6 (79.0–91.7) | 219/236 | 92.8 (89.5–95.8) |
| RNA-seq | Champion–challenger | exploratory fitted | 118/118 (96.9–100.0) | 113/118 | 95.8 (92.1–99.1) | 95.8 (92.1–99.1) | 231/236 | 97.9 (96.1–99.6) |
| RNA-seq | Algorithm-family-restricted champion–challenger | exploratory fitted | 118/118 (96.9–100.0) | 109/118 | 92.4 (87.1–96.8) | 92.4 (87.1–96.8) | 225/236 | 95.3 (92.0–98.2) |
| RNA-seq | Vote-support-restricted champion–challenger | exploratory fitted | 118/118 (96.9–100.0) | 113/118 | 95.8 (92.1–99.1) | 95.8 (92.1–99.1) | 231/236 | 97.9 (96.1–99.6) |
| RNA-seq | Logistic meta-consensus | exploratory fitted | 118/118 (96.9–100.0) | 113/118 | 95.8 (92.1–99.1) | 95.8 (92.1–99.1) | 231/236 | 97.9 (96.1–99.6) |
| RNA-seq | ChampHLA-Consensus | primary | 118/118 (96.9–100.0) | 113/118 | 95.8 (92.1–99.1) | 95.8 (92.1–99.1) | 231/236 | 97.9 (96.1–99.6) |
| RNA-seq | Strict majority | descriptive comparator | 110/118 (88.7–97.3) | 106/118 | 89.8 (84.2–94.9) | 96.4 (92.7–99.1) | 216/236 | 91.5 (86.7–95.9) |
| RNA-seq | Two-thirds consensus | descriptive comparator | 110/118 (88.7–97.3) | 106/118 | 89.8 (84.2–94.9) | 96.4 (92.7–99.1) | 216/236 | 91.5 (86.7–95.8) |
| RNA-seq | Two-thirds-guarded champion–challenger | exploratory fitted | 118/118 (96.9–100.0) | 113/118 | 95.8 (92.1–99.1) | 95.8 (92.1–99.1) | 231/236 | 97.9 (96.0–99.6) |
| WES | Best single caller (nested CV) | exploratory fitted | 153/153 (97.6–100.0) | 142/153 | 92.8 (88.4–96.7) | 92.8 (88.4–96.7) | 295/306 | 96.4 (94.2–98.3) |
| WES | HLA-HD | descriptive comparator | 153/153 (97.6–100.0) | 131/153 | 85.6 (79.0–91.6) | 85.6 (79.0–91.6) | 281/306 | 91.8 (88.2–95.2) |
| WES | OptiType | descriptive comparator | 153/153 (97.6–100.0) | 142/153 | 92.8 (88.5–96.7) | 92.8 (88.5–96.7) | 295/306 | 96.4 (94.2–98.3) |
| WES | POLYSOLVER | descriptive comparator | 153/153 (97.6–100.0) | 138/153 | 90.2 (85.5–94.6) | 90.2 (85.5–94.6) | 291/306 | 95.1 (92.8–97.3) |
| WES | SpecHLA | descriptive comparator | 153/153 (97.6–100.0) | 134/153 | 87.6 (82.3–92.6) | 87.6 (82.3–92.6) | 284/306 | 92.8 (89.5–95.8) |
| WES | T1K | descriptive comparator | 150/153 (95.6–100.0) | 125/153 | 81.7 (75.6–87.5) | 83.3 (77.7–88.7) | 273/306 | 89.2 (85.2–92.9) |
| WES | Champion–challenger | exploratory fitted | 153/153 (97.6–100.0) | 141/153 | 92.2 (88.2–95.9) | 92.2 (88.2–95.9) | 294/306 | 96.1 (94.1–97.9) |
| WES | Algorithm-family-restricted champion–challenger | exploratory fitted | 153/153 (97.6–100.0) | 141/153 | 92.2 (88.2–95.9) | 92.2 (88.2–95.9) | 294/306 | 96.1 (94.1–97.9) |
| WES | Vote-support-restricted champion–challenger | exploratory fitted | 153/153 (97.6–100.0) | 143/153 | 93.5 (89.8–96.8) | 93.5 (89.8–96.8) | 296/306 | 96.7 (94.9–98.4) |
| WES | Logistic meta-consensus | exploratory fitted | 153/153 (97.6–100.0) | 140/153 | 91.5 (87.0–95.6) | 91.5 (87.0–95.6) | 293/306 | 95.8 (93.5–97.8) |
| WES | ChampHLA-Consensus | primary | 153/153 (97.6–100.0) | 143/153 | 93.5 (89.7–96.8) | 93.5 (89.7–96.8) | 296/306 | 96.7 (94.9–98.4) |
| WES | Strict majority | descriptive comparator | 150/153 (95.6–100.0) | 141/153 | 92.2 (88.2–95.9) | 94.0 (90.3–97.3) | 291/306 | 95.1 (92.3–97.6) |
| WES | Two-thirds consensus | descriptive comparator | 144/153 (90.3–97.4) | 136/153 | 88.9 (84.0–93.4) | 94.4 (90.8–97.8) | 280/306 | 91.5 (87.5–95.2) |
| WES | Two-thirds-guarded champion–challenger | exploratory fitted | 153/153 (97.6–100.0) | 141/153 | 92.2 (88.3–95.9) | 92.2 (88.3–95.9) | 294/306 | 96.1 (94.1–97.9) |
<!-- END GENERATED PERFORMANCE TABLE -->

**Singleton sensitivity.** The table repeats the analysis with every single-allele output abstaining, including HLA-HD, arcasHLA and v3.5.0 rerun T1K homozygous declarations completed in primary scoring (decisions/20261008_singleton_native_homozygosity.json). It
reproduces the scoring rule used before that decision.

<!-- BEGIN GENERATED SINGLETON SENSITIVITY TABLE -->
| Assay | Method | Scope | Native-declaration correct | Abstain-all correct | Native-declaration callable | Abstain-all callable |
|---|---|---|---:|---:|---:|---:|
| WES | Algorithm-family-restricted champion–challenger | exploratory fitted | 141/153 | 141/153 | 153/153 | 153/153 |
| WES | Best single caller (nested CV) | exploratory fitted | 142/153 | 142/153 | 153/153 | 153/153 |
| WES | ChampHLA-Consensus | primary | 143/153 | 143/153 | 153/153 | 153/153 |
| WES | Champion–challenger | exploratory fitted | 141/153 | 141/153 | 153/153 | 153/153 |
| WES | HLA-HD | descriptive comparator | 131/153 | 115/153 | 153/153 | 137/153 |
| WES | Logistic meta-consensus | exploratory fitted | 140/153 | 143/153 | 153/153 | 153/153 |
| WES | OptiType | descriptive comparator | 142/153 | 142/153 | 153/153 | 153/153 |
| WES | POLYSOLVER | descriptive comparator | 138/153 | 138/153 | 153/153 | 153/153 |
| WES | SpecHLA | descriptive comparator | 134/153 | 134/153 | 153/153 | 153/153 |
| WES | Strict majority | descriptive comparator | 141/153 | 141/153 | 150/153 | 150/153 |
| WES | T1K | descriptive comparator | 125/153 | 114/153 | 150/153 | 138/153 |
| WES | Two-thirds consensus | descriptive comparator | 136/153 | 136/153 | 144/153 | 144/153 |
| WES | Two-thirds-guarded champion–challenger | exploratory fitted | 141/153 | 141/153 | 153/153 | 153/153 |
| WES | Vote-support-restricted champion–challenger | exploratory fitted | 143/153 | 143/153 | 153/153 | 153/153 |
| RNA-seq | Algorithm-family-restricted champion–challenger | exploratory fitted | 109/118 | 104/118 | 118/118 | 116/118 |
| RNA-seq | Best single caller (nested CV) | exploratory fitted | 111/118 | 112/118 | 118/118 | 118/118 |
| RNA-seq | ChampHLA-Consensus | primary | 113/118 | 112/118 | 118/118 | 118/118 |
| RNA-seq | Champion–challenger | exploratory fitted | 113/118 | 107/118 | 118/118 | 116/118 |
| RNA-seq | HLA-HD | descriptive comparator | 112/118 | 98/118 | 118/118 | 104/118 |
| RNA-seq | Logistic meta-consensus | exploratory fitted | 113/118 | 113/118 | 118/118 | 118/118 |
| RNA-seq | OptiType | descriptive comparator | 112/118 | 112/118 | 118/118 | 118/118 |
| RNA-seq | Strict majority | descriptive comparator | 106/118 | 96/118 | 110/118 | 101/118 |
| RNA-seq | T1K | descriptive comparator | 101/118 | 90/118 | 118/118 | 107/118 |
| RNA-seq | Two-thirds consensus | descriptive comparator | 106/118 | 96/118 | 110/118 | 101/118 |
| RNA-seq | Two-thirds-guarded champion–challenger | exploratory fitted | 113/118 | 108/118 | 118/118 | 118/118 |
| RNA-seq | Vote-support-restricted champion–challenger | exploratory fitted | 113/118 | 112/118 | 118/118 | 118/118 |
| RNA-seq | arcasHLA | descriptive comparator | 58/118 | 55/118 | 118/118 | 109/118 |
<!-- END GENERATED SINGLETON SENSITIVITY TABLE -->

## S3. Paired comparisons

Every delta is `ChampHLA-Consensus − comparator`. Missing or non-callable
comparator predictions score incorrect. The two-sided subject sign-flip test of the locus-weighted difference governs significance, with Holm correction. It is exact through 20 nonzero subject aggregates and Monte Carlo above that. The "Significant" column marks Holm-adjusted *p*<0.05 (decisions/20261009_signflip_governs.json). Intervals and cluster-*t* *p* values are descriptive. They use a CR1 (finite-cluster-corrected cluster-robust) subject-clustered standard error, a Student *t* distribution and `G−1` degrees of freedom; this is anti-conservative with few discordant subjects. Bonferroni-adjusted intervals and cluster-*t* Holm *p* values use the same active family. Descriptive comparators and exploratory
fitted policies form separate families; zero-discordance rows are displayed but
excluded from multiplicity. A descriptive interval can exclude zero while the governing sign-flip test is not significant. In the v3.5.0 rerun, this occurs for RNA-seq strict-majority and two-thirds consensus; neither comparison is called significant.
The two-percentage-point non-inferiority analysis is post hoc, not confirmatory.
The sign-flip seed for each row is a deterministic SHA-256 derivation from base
seed 20260831 and is recorded with the assignment count in the source TSV.
Exact rows enumerate all 2^d assignments for d nonzero subject aggregates;
rows with d>20 use 1,000,000 assignments and the plus-one correction.
Some comparators return identical genotypes. Each still counts in its prespecified testing family, because we fixed the families before checking for duplicates. In WES, the vote-support-restricted and logistic meta-consensus policies return the plurality genotype at every locus, and the three champion–challenger variants return identical genotypes. The refitted best-caller policy selected OptiType in every WES fold. In RNA-seq, strict majority and two-thirds consensus return identical genotypes for a four-caller panel. Removing the duplicates would only lower
m and changes no significance verdict here.

<!-- BEGIN GENERATED COMPARISON TABLE -->
| Assay | Comparator | Comparator correct | Delta, points | Family | m | Pointwise cluster-t 95% CI | Bonferroni-adjusted cluster-t 95% CI | Wins/losses | Sign-flip raw p | Sign-flip Holm p | Significant | Cluster-t Holm p |
|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---|---:|
| RNA-seq | arcasHLA | 58/118 | 46.61 | descriptive comparator | 6 | 37.27 to 55.95 | 33.83 to 59.39 | 55/0 | 1.00e-06 | 6.00e-06 | yes | 9.03e-13 |
| RNA-seq | HLA-HD | 112/118 | 0.85 | descriptive comparator | 6 | -0.85 to 2.54 | -1.47 to 3.16 | 1/0 | 1 | 1 | no | 0.64 |
| RNA-seq | OptiType | 112/118 | 0.85 | descriptive comparator | 6 | -0.85 to 2.54 | -1.47 to 3.16 | 1/0 | 1 | 1 | no | 0.64 |
| RNA-seq | T1K | 101/118 | 10.17 | descriptive comparator | 6 | 4.45 to 15.89 | 2.34 to 18.00 | 12/0 | 9.77e-04 | 0.005 | yes | 0.004 |
| RNA-seq | Strict majority | 106/118 | 5.93 | descriptive comparator | 6 | 1.74 to 10.12 | 0.20 to 11.67 | 7/0 | 0.016 | 0.062 | no | 0.026 |
| RNA-seq | Two-thirds consensus | 106/118 | 5.93 | descriptive comparator | 6 | 1.74 to 10.12 | 0.20 to 11.67 | 7/0 | 0.016 | 0.062 | no | 0.026 |
| RNA-seq | Best single caller (nested CV) | 111/118 | 1.69 | exploratory fitted | 2 | -0.67 to 4.06 | -1.02 to 4.41 | 2/0 | 0.5 | 0.5 | no | 0.155 |
| RNA-seq | Champion–challenger | 113/118 | 0.00 | exploratory fitted | 2 | 0.00 to 0.00 | 0.00 to 0.00 | 0/0 | 1 | 1 | no | 1 |
| RNA-seq | Algorithm-family-restricted champion–challenger | 109/118 | 3.39 | exploratory fitted | 2 | 0.09 to 6.69 | -0.40 to 7.18 | 4/0 | 0.125 | 0.25 | no | 0.088 |
| RNA-seq | Vote-support-restricted champion–challenger | 113/118 | 0.00 | exploratory fitted | 2 | 0.00 to 0.00 | 0.00 to 0.00 | 0/0 | 1 | 1 | no | 1 |
| RNA-seq | Logistic meta-consensus | 113/118 | 0.00 | exploratory fitted | 2 | 0.00 to 0.00 | 0.00 to 0.00 | 0/0 | 1 | 1 | no | 1 |
| RNA-seq | Two-thirds-guarded champion–challenger | 113/118 | 0.00 | exploratory fitted | 2 | 0.00 to 0.00 | 0.00 to 0.00 | 0/0 | 1 | 1 | no | 1 |
| WES | HLA-HD | 131/153 | 7.84 | descriptive comparator | 7 | 3.41 to 12.28 | 1.67 to 14.02 | 12/0 | 9.77e-04 | 0.006 | yes | 0.005 |
| WES | OptiType | 142/153 | 0.65 | descriptive comparator | 7 | -2.28 to 3.59 | -3.44 to 4.74 | 2/1 | 1 | 1 | no | 0.658 |
| WES | POLYSOLVER | 138/153 | 3.27 | descriptive comparator | 7 | -0.10 to 6.63 | -1.41 to 7.95 | 6/1 | 0.125 | 0.375 | no | 0.17 |
| WES | SpecHLA | 134/153 | 5.88 | descriptive comparator | 7 | 1.00 to 10.76 | -0.91 to 12.67 | 12/3 | 0.033 | 0.133 | no | 0.076 |
| WES | T1K | 125/153 | 11.76 | descriptive comparator | 7 | 6.39 to 17.14 | 4.29 to 19.24 | 19/1 | 3.05e-05 | 2.14e-04 | yes | 3.27e-04 |
| WES | Strict majority | 141/153 | 1.31 | descriptive comparator | 7 | -0.53 to 3.14 | -1.25 to 3.86 | 2/0 | 0.5 | 1 | no | 0.319 |
| WES | Two-thirds consensus | 136/153 | 4.58 | descriptive comparator | 7 | 1.27 to 7.88 | -0.03 to 9.18 | 7/0 | 0.016 | 0.078 | no | 0.037 |
| WES | Best single caller (nested CV) | 142/153 | 0.65 | exploratory fitted | 5 | -2.28 to 3.59 | -3.25 to 4.56 | 2/1 | 1 | 1 | no | 0.782 |
| WES | Champion–challenger | 141/153 | 1.31 | exploratory fitted | 5 | -0.51 to 3.13 | -1.11 to 3.73 | 2/0 | 0.5 | 1 | no | 0.782 |
| WES | Algorithm-family-restricted champion–challenger | 141/153 | 1.31 | exploratory fitted | 5 | -0.51 to 3.13 | -1.11 to 3.73 | 2/0 | 0.5 | 1 | no | 0.782 |
| WES | Vote-support-restricted champion–challenger | 143/153 | 0.00 | exploratory fitted | 5 | 0.00 to 0.00 | 0.00 to 0.00 | 0/0 | 1 | 1 | no | 1 |
| WES | Logistic meta-consensus | 140/153 | 1.96 | exploratory fitted | 5 | -0.93 to 4.85 | -1.88 to 5.80 | 3/0 | 0.5 | 1 | no | 0.782 |
| WES | Two-thirds-guarded champion–challenger | 141/153 | 1.31 | exploratory fitted | 5 | -0.51 to 3.13 | -1.11 to 3.73 | 2/0 | 0.5 | 1 | no | 0.782 |
<!-- END GENERATED COMPARISON TABLE -->

<!-- BEGIN GENERATED DETECTABILITY TABLE -->
| Assay | Comparator | Sign-flip family | m | Nonzero subject aggregates | Minimum attainable raw p | Holm significance reachable in worst rank | All-win subjects needed (points) |
|---|---|---|---:|---:|---:|---|---:|
| RNA-seq | arcasHLA | descriptive comparator | 6 | 39 | 3.64e-12 | yes | 8 (6.78) |
| RNA-seq | HLA-HD | descriptive comparator | 6 | 1 | 1 | no | 8 (6.78) |
| RNA-seq | OptiType | descriptive comparator | 6 | 1 | 1 | no | 8 (6.78) |
| RNA-seq | T1K | descriptive comparator | 6 | 11 | 9.77e-04 | yes | 8 (6.78) |
| RNA-seq | Strict majority | descriptive comparator | 6 | 7 | 0.016 | no | 8 (6.78) |
| RNA-seq | Two-thirds consensus | descriptive comparator | 6 | 7 | 0.016 | no | 8 (6.78) |
| RNA-seq | Best single caller (nested CV) | exploratory fitted | 2 | 2 | 0.5 | no | 7 (5.93) |
| RNA-seq | Champion–challenger | exploratory fitted | 2 | 0 | 1 | no | 7 (5.93) |
| RNA-seq | Algorithm-family-restricted champion–challenger | exploratory fitted | 2 | 4 | 0.125 | no | 7 (5.93) |
| RNA-seq | Vote-support-restricted champion–challenger | exploratory fitted | 2 | 0 | 1 | no | 7 (5.93) |
| RNA-seq | Logistic meta-consensus | exploratory fitted | 2 | 0 | 1 | no | 7 (5.93) |
| RNA-seq | Two-thirds-guarded champion–challenger | exploratory fitted | 2 | 0 | 1 | no | 7 (5.93) |
| WES | HLA-HD | descriptive comparator | 7 | 11 | 9.77e-04 | yes | 9 (5.88) |
| WES | OptiType | descriptive comparator | 7 | 2 | 0.5 | no | 9 (5.88) |
| WES | POLYSOLVER | descriptive comparator | 7 | 7 | 0.016 | no | 9 (5.88) |
| WES | SpecHLA | descriptive comparator | 7 | 12 | 4.88e-04 | yes | 9 (5.88) |
| WES | T1K | descriptive comparator | 7 | 16 | 3.05e-05 | yes | 9 (5.88) |
| WES | Strict majority | descriptive comparator | 7 | 2 | 0.5 | no | 9 (5.88) |
| WES | Two-thirds consensus | descriptive comparator | 7 | 7 | 0.016 | no | 9 (5.88) |
| WES | Best single caller (nested CV) | exploratory fitted | 5 | 2 | 0.5 | no | 8 (5.23) |
| WES | Champion–challenger | exploratory fitted | 5 | 2 | 0.5 | no | 8 (5.23) |
| WES | Algorithm-family-restricted champion–challenger | exploratory fitted | 5 | 2 | 0.5 | no | 8 (5.23) |
| WES | Vote-support-restricted champion–challenger | exploratory fitted | 5 | 0 | 1 | no | 8 (5.23) |
| WES | Logistic meta-consensus | exploratory fitted | 5 | 2 | 0.5 | no | 8 (5.23) |
| WES | Two-thirds-guarded champion–challenger | exploratory fitted | 5 | 2 | 0.5 | no | 8 (5.23) |
<!-- END GENERATED DETECTABILITY TABLE -->

The minimum attainable p is the exact enumeration minimum, attained when every
nonzero subject favours one method. Rows with more than 20
nonzero subject aggregates were tested with 1,000,000 Monte Carlo assignments,
whose attainable floor is about 1.0×10⁻⁶ before multiplicity adjustment.

The families were fixed on 28 September 2026 after development results had been seen (Supplementary S14). The table compares sign-flip verdicts under the primary families (within assay, descriptive and fitted separately), one family per assay and one family pooling both assays. The same four comparisons are significant under every definition. Only WES two-thirds consensus would additionally be significant without any correction.

<!-- BEGIN GENERATED FAMILY SENSITIVITY TABLE -->
| Assay | Comparator | Family | Raw sign-flip p | Holm: assay and family (primary) | Holm: assay | Holm: both assays pooled | p<0.05 under |
|---|---|---|---:|---:|---:|---:|---|
| WES | HLA-HD | descriptive comparator | 9.77e-04 | 0.006 | 0.011 | 0.018 | unadjusted; assay and family (primary); assay; both assays pooled |
| WES | OptiType | descriptive comparator | 1 | 1 | 1 | 1 | none |
| WES | POLYSOLVER | descriptive comparator | 0.125 | 0.375 | 1 | 1 | none |
| WES | SpecHLA | descriptive comparator | 0.033 | 0.133 | 0.299 | 0.432 | unadjusted |
| WES | Strict majority | descriptive comparator | 0.5 | 1 | 1 | 1 | none |
| WES | T1K | descriptive comparator | 3.05e-05 | 2.14e-04 | 3.66e-04 | 5.80e-04 | unadjusted; assay and family (primary); assay; both assays pooled |
| WES | Two-thirds consensus | descriptive comparator | 0.016 | 0.078 | 0.156 | 0.25 | unadjusted |
| WES | Algorithm-family-restricted champion–challenger | exploratory fitted | 0.5 | 1 | 1 | 1 | none |
| WES | Best single caller (nested CV) | exploratory fitted | 1 | 1 | 1 | 1 | none |
| WES | Champion–challenger | exploratory fitted | 0.5 | 1 | 1 | 1 | none |
| WES | Logistic meta-consensus | exploratory fitted | 0.5 | 1 | 1 | 1 | none |
| WES | Two-thirds-guarded champion–challenger | exploratory fitted | 0.5 | 1 | 1 | 1 | none |
| RNA-seq | HLA-HD | descriptive comparator | 1 | 1 | 1 | 1 | none |
| RNA-seq | OptiType | descriptive comparator | 1 | 1 | 1 | 1 | none |
| RNA-seq | Strict majority | descriptive comparator | 0.016 | 0.062 | 0.094 | 0.25 | unadjusted |
| RNA-seq | T1K | descriptive comparator | 9.77e-04 | 0.005 | 0.007 | 0.018 | unadjusted; assay and family (primary); assay; both assays pooled |
| RNA-seq | Two-thirds consensus | descriptive comparator | 0.016 | 0.062 | 0.094 | 0.25 | unadjusted |
| RNA-seq | arcasHLA | descriptive comparator | 1.00e-06 | 6.00e-06 | 8.00e-06 | 2.00e-05 | unadjusted; assay and family (primary); assay; both assays pooled |
| RNA-seq | Algorithm-family-restricted champion–challenger | exploratory fitted | 0.125 | 0.25 | 0.5 | 1 | none |
| RNA-seq | Best single caller (nested CV) | exploratory fitted | 0.5 | 0.5 | 1 | 1 | none |
<!-- END GENERATED FAMILY SENSITIVITY TABLE -->

Detectability concerns the discrete sign-flip test that governs significance. It does not imply that every valid clustered analysis is incapable of detecting a difference. Non-significance is not interpreted as equivalence.

## S4. Stratified primary results

We did not use strata to fit or select the primary method. Population labels are
the source population codes, not broad continental superpopulations. The
rare-allele stratum uses the smaller of the two truth alleles' counts within the
filtered assay denominator; this count is not an external population
frequency. Intervals are exact and unadjusted; all strata are descriptive.

<!-- BEGIN GENERATED STRATIFIED TABLE -->
| Assay | Stratum type | Stratum | Correct | Concordance, % (95% CI) |
|---|---|---|---:|---:|
| RNA-seq | gene | HLA-A | 37/38 | 97.4 (86.2–99.9) |
| RNA-seq | gene | HLA-B | 38/40 | 95.0 (83.1–99.4) |
| RNA-seq | gene | HLA-C | 38/40 | 95.0 (83.1–99.4) |
| RNA-seq | rarer truth allele: within-benchmark count | 1 | 22/25 | 88.0 (68.8–97.5) |
| RNA-seq | rarer truth allele: within-benchmark count | 2-4 | 51/52 | 98.1 (89.7–100.0) |
| RNA-seq | rarer truth allele: within-benchmark count | >=5 | 40/41 | 97.6 (87.1–99.9) |
| RNA-seq | population | British | 4/4 | suppressed (n<5) |
| RNA-seq | population | Finland | 2/2 | suppressed (n<5) |
| RNA-seq | population | Tuscan | 7/7 | 100.0 (59.0–100.0) |
| RNA-seq | population | Utah | 57/59 | 96.6 (88.3–99.6) |
| RNA-seq | population | Yoruba | 43/46 | 93.5 (82.1–98.6) |
| RNA-seq | truth zygosity | heterozygous | 98/103 | 95.1 (89.0–98.4) |
| RNA-seq | truth zygosity | homozygous | 15/15 | 100.0 (78.2–100.0) |
| WES | gene | HLA-A | 48/50 | 96.0 (86.3–99.5) |
| WES | gene | HLA-B | 50/52 | 96.2 (86.8–99.5) |
| WES | gene | HLA-C | 45/51 | 88.2 (76.1–95.6) |
| WES | rarer truth allele: within-benchmark count | 1 | 21/23 | 91.3 (72.0–98.9) |
| WES | rarer truth allele: within-benchmark count | 2-4 | 59/63 | 93.7 (84.5–98.2) |
| WES | rarer truth allele: within-benchmark count | >=5 | 63/67 | 94.0 (85.4–98.3) |
| WES | population | CEU | 59/61 | 96.7 (88.7–99.6) |
| WES | population | CHB | 14/15 | 93.3 (68.1–99.8) |
| WES | population | FIN | 2/2 | suppressed (n<5) |
| WES | population | GBR | 2/2 | suppressed (n<5) |
| WES | population | PUR | 2/2 | suppressed (n<5) |
| WES | population | TSI | 7/7 | 100.0 (59.0–100.0) |
| WES | population | YRI | 57/64 | 89.1 (78.8–95.5) |
| WES | truth zygosity | heterozygous | 125/135 | 92.6 (86.8–96.4) |
| WES | truth zygosity | homozygous | 18/18 | 100.0 (81.5–100.0) |
<!-- END GENERATED STRATIFIED TABLE -->

## S5. Missingness, support and ties

A partial row contains one valid allele and an undetermined second allele. Such
rows abstain. An absent row is missing from the collected caller table.

The support profiles below and error-correlation tables in S7 summarize caller disagreement; S12.1 classifies disagreement using caller outputs without reference genotypes.

<!-- BEGIN GENERATED MISSINGNESS TABLE -->
| Assay | Caller | Loci | Rows | Callable | Partial | Missing | Absent | Invalid |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| WES | HLA-HD | 153 | 153 | 153 | 0 | 0 | 0 | 0 |
| WES | OptiType | 153 | 153 | 153 | 0 | 0 | 0 | 0 |
| WES | POLYSOLVER | 153 | 153 | 153 | 0 | 0 | 0 | 0 |
| WES | SpecHLA | 153 | 153 | 153 | 0 | 0 | 0 | 0 |
| WES | T1K | 153 | 153 | 150 | 2 | 1 | 0 | 0 |
| RNA-seq | arcasHLA | 118 | 118 | 118 | 0 | 0 | 0 | 0 |
| RNA-seq | HLA-HD | 118 | 118 | 118 | 0 | 0 | 0 | 0 |
| RNA-seq | OptiType | 118 | 118 | 118 | 0 | 0 | 0 | 0 |
| RNA-seq | T1K | 118 | 118 | 118 | 0 | 0 | 0 | 0 |
<!-- END GENERATED MISSINGNESS TABLE -->

In the v3.5.0 rerun no panel caller row is absent. The historical table lacked HLA-HD, OptiType and T1K rows at NA19130's HLA-A, -B and -C loci. Its plurality at those loci was an arcasHLA-only 1/1 vote. Historical task reports, traces and raw outputs were not preserved. Stored artifacts cannot distinguish tasks that ran without retained output, failed or were never submitted. The rerun records task states explicitly (Supplementary Table S10.1), so the mutually available comparison below equals the fixed-denominator comparison.

<!-- BEGIN GENERATED MUTUALLY AVAILABLE TABLE -->
| Assay | Caller | Plurality, fixed | Caller, fixed | Plurality, mutually available | Caller, mutually available | Plurality wins/losses, mutually available | Absent stored rows |
|---|---|---:|---:|---:|---:|---:|---|
| RNA-seq | arcasHLA | 113/118 | 58/118 | 113/118 | 58/118 | 55/0 | none |
| RNA-seq | HLA-HD | 113/118 | 112/118 | 113/118 | 112/118 | 1/0 | none |
| RNA-seq | OptiType | 113/118 | 112/118 | 113/118 | 112/118 | 1/0 | none |
| RNA-seq | T1K | 113/118 | 101/118 | 113/118 | 101/118 | 12/0 | none |
| WES | HLA-HD | 143/153 | 131/153 | 143/153 | 131/153 | 12/0 | none |
| WES | OptiType | 143/153 | 142/153 | 143/153 | 142/153 | 2/1 | none |
| WES | POLYSOLVER | 143/153 | 138/153 | 143/153 | 138/153 | 6/1 | none |
| WES | SpecHLA | 143/153 | 134/153 | 143/153 | 134/153 | 12/3 | none |
| WES | T1K | 143/153 | 125/153 | 143/153 | 125/153 | 19/1 | none |
<!-- END GENERATED MUTUALLY AVAILABLE TABLE -->

Support is recorded as the unreduced number of callable callers selecting the
emitted pair (`k`) and the number of callable panel callers (`n`). Distinct
profiles such as 1/1 and 4/4 are never pooled, even though both reduce to one.
These are descriptive concordance strata, not calibrated probabilities.

<!-- BEGIN GENERATED SUPPORT TABLE -->
| Assay | Support profile (supporting/callable) | Tied loci | Correct | Concordance, % (95% CI) |
|---|---:|---:|---:|---:|
| RNA-seq | 2/4 | 0 | 7/8 | 87.5 (47.3–99.7) |
| RNA-seq | 3/4 | 0 | 55/57 | 96.5 (87.9–99.6) |
| RNA-seq | 4/4 | 0 | 51/53 | 96.2 (87.0–99.5) |
| WES | 2/5 | 0 | 2/3 | 66.7 (9.4–99.2) |
| WES | 3/4 | 0 | 2/3 | 66.7 (9.4–99.2) |
| WES | 3/5 | 0 | 5/6 | 83.3 (35.9–99.6) |
| WES | 4/5 | 0 | 31/37 | 83.8 (68.0–93.8) |
| WES | 5/5 | 0 | 103/104 | 99.0 (94.8–100.0) |
<!-- END GENERATED SUPPORT TABLE -->

No locus was tied in either assay, so lexicographic tie-breaking did not affect either result.  A
production implementation should route ties to review or validate a prespecified
biologically informed rule on independent data.

## S6. Caller-resource provenance

| Caller | Assay role | Algorithm family | Audited IPD-IMGT/HLA resource | Evidence | Executable/container provenance |
| --- | --- | --- | --- | --- | --- |
| arcasHLA | RNA-seq | transcript abundance/EM | 3.40.0 | bundled version report from the caller run; report file not preserved here | unavailable |
| HLA-HD | WES, RNA-seq | alignment/dictionary scoring | 3.15.0 | content-derived lower bound | unavailable |
| OptiType | WES, RNA-seq | integer programming | 3.13.1 | content-derived lower bound | unavailable |
| POLYSOLVER | WES | alignment/population model | 3.11.0 | content-derived lower bound; filtered database | unavailable |
| SpecHLA | WES | alignment/local assembly | 3.38.0 + 3.51.0 | heterogeneous bundled components | unavailable |
| T1K | WES, RNA-seq | alignment/expectation maximization | 3.63.0 | deployment declaration plus content audit | unavailable |

HLA\*LA and HISAT-genotype were not run. Historical off-panel outputs exist for Kourami on WES, seq2HLA on RNA-seq, arcasHLA on WES and SpecHLA on RNA-seq (`src/champhla_confirmation/panels.py`). Kourami and seq2HLA outputs are incomplete. They are not part of the released normalized table and are excluded
from benchmark comparisons. seq2HLA was also run in the current single-sample
test workflow (S10), under different conditions from the development run. No
comparative claim about any of these callers is made here.

The historical stored calls carried IPD-IMGT/HLA 3.59.0 metadata, but their
normalization was syntactic two-field reduction and did not verify release
membership. In WES,
the historical exact-concordance ordering—POLYSOLVER, OptiType, HLA-HD,
SpecHLA and T1K—also orders the audited bundled database releases from oldest
(3.11.0) to newest (3.63.0). This descriptive ordering is not evidence that an
older database improves accuracy.

Neither normalization maps renamed or deleted alleles. The rerun collector records each allele's IPD-IMGT/HLA 3.65.0 membership and compares its reported first two fields. Results are syntax-normalized rather than database-harmonized. The historical caller run only partly records what reads each caller received. At the workflow revision of 7 April 2026, POLYSOLVER and SpecHLA received whole input alignments. FASTQ-based callers received HLA-region reads only if region extraction was enabled; the run did not record that setting. In the release 3.5.0 rerun, WES reads on HLA-allele and alternate contigs are realigned to primary chromosome 6 before every DNA caller. Each sample records inputs, container digests and workflow files (S10).

We checked membership using checksum-verified allele lists from the current deployment, restricted to intended-use assay panels. Every exact
reference genotype and allele copy was present in every applicable list.

<!-- BEGIN GENERATED REPRESENTABILITY TABLE -->
| Assay | Caller | Verified native-list release | Catalog alleles | Exact-truth genotypes represented | Truth allele copies represented |
|---|---|---|---:|---:|---:|
| WES | HLA-HD | 3.15.0 | 10700 | 153/153 | 306/306 |
| WES | OptiType | 3.13.1 | 7332 | 153/153 | 306/306 |
| WES | POLYSOLVER | 3.11.0 | 6597 | 153/153 | 306/306 |
| WES | SpecHLA | 3.38.0 | 25958 | 153/153 | 306/306 |
| WES | T1K | 3.63.0 | 27764 | 153/153 | 306/306 |
| RNA-seq | arcasHLA | 3.40.0 | 27273 | 118/118 | 236/236 |
| RNA-seq | HLA-HD | 3.15.0 | 10700 | 118/118 | 236/236 |
| RNA-seq | OptiType | 3.13.1 | 7332 | 118/118 | 236/236 |
| RNA-seq | T1K | 3.63.0 | 27764 | 118/118 | 236/236 |
<!-- END GENERATED REPRESENTABILITY TABLE -->

[RESULT:DEV_NATIVE_REPRESENTABILITY_WES_POLYSOLVER]
[RESULT:DEV_NATIVE_REPRESENTABILITY_RNASEQ_ARCASHLA]

These current-deployment lists do not reconstruct the April caller-run
databases, prove that every listed allele survived caller-specific filtering,
or show that sequence evidence could distinguish it. Presence is necessary but
not sufficient for a caller to emit an allele. SpecHLA's heterogeneous
components are summarized by the verified 3.38.0 native list used here, not the
separate 3.51.0 component. No representability-adjusted concordance claim is
made. All 15 ChampHLA-Consensus errors (10 WES, 5 RNA-seq) were callable discordances. Every reference and predicted allele at those loci was a current release-3.65 designation. Neither the native-list check nor the current-release nomenclature audit attributes a development error to allele absence. Neither excludes historical search-space differences.

## S7. Oracle headroom and exploratory fitted policies

Error φ is the phi coefficient between two callers' per-locus error indicators.
The 2×2 column gives, in order, the loci both callers got right, those only the
second got wrong, those only the first got wrong and those both got wrong. On the
fixed denominator a locus where both callers made no call counts as a joint error;
the mutually callable φ removes such loci. Intervals are subject-cluster
percentile bootstrap intervals (100,000 resamples).

<!-- BEGIN GENERATED CORRELATION TABLE -->
| Assay | Caller 1 | Caller 2 | Fixed-denominator loci | Both right / only 2 wrong / only 1 wrong / both wrong | Error φ (95% CI) | Mutually callable loci | Mutually callable error φ |
|---|---|---|---:|---:|---:|---:|---:|
| WES | HLA-HD | OptiType | 153 | 129/2/13/9 | 0.53 (0.33 to 0.71) | 153 | 0.53 |
| WES | HLA-HD | POLYSOLVER | 153 | 126/5/12/10 | 0.49 (0.30 to 0.67) | 153 | 0.49 |
| WES | HLA-HD | SpecHLA | 153 | 121/10/13/9 | 0.35 (0.17 to 0.52) | 153 | 0.35 |
| WES | HLA-HD | T1K | 153 | 116/15/9/13 | 0.43 (0.25 to 0.60) | 150 | 0.40 |
| WES | OptiType | POLYSOLVER | 153 | 135/7/3/8 | 0.59 (0.33 to 0.81) | 153 | 0.59 |
| WES | OptiType | SpecHLA | 153 | 129/13/5/6 | 0.36 (0.10 to 0.60) | 153 | 0.36 |
| WES | OptiType | T1K | 153 | 122/20/3/8 | 0.39 (0.17 to 0.59) | 150 | 0.38 |
| WES | POLYSOLVER | SpecHLA | 153 | 128/10/6/9 | 0.48 (0.25 to 0.68) | 153 | 0.48 |
| WES | POLYSOLVER | T1K | 153 | 118/20/7/8 | 0.30 (0.09 to 0.50) | 150 | 0.29 |
| WES | SpecHLA | T1K | 153 | 115/19/10/9 | 0.28 (0.07 to 0.48) | 150 | 0.24 |
| RNA-seq | arcasHLA | HLA-HD | 118 | 58/0/54/6 | 0.23 (0.12 to 0.32) | 118 | 0.23 |
| RNA-seq | arcasHLA | OptiType | 118 | 57/1/55/5 | 0.15 (-0.02 to 0.28) | 118 | 0.15 |
| RNA-seq | arcasHLA | T1K | 118 | 52/6/49/11 | 0.11 (-0.08 to 0.30) | 118 | 0.11 |
| RNA-seq | HLA-HD | OptiType | 118 | 111/1/1/5 | 0.82 (0.49 to 1.00) | 118 | 0.82 |
| RNA-seq | HLA-HD | T1K | 118 | 100/12/1/5 | 0.45 (0.18 to 0.66) | 118 | 0.45 |
| RNA-seq | OptiType | T1K | 118 | 100/12/1/5 | 0.45 (0.16 to 0.68) | 118 | 0.45 |
<!-- END GENERATED CORRELATION TABLE -->

The first φ coefficient treats every no-call as an error, matching the fixed
denominator. The mutually-callable sensitivity excludes loci at which either
caller abstained. Positive dependence is common across exact loci, mostly at loci where callers jointly disagree with the 2014 reference. Where reference and second typing agree, dependence largely disappears (reference-agreement tables below).

The oracle marks a locus correct if any intended-use caller produced the truth
genotype. It is an upper bound for methods that only select among caller
outputs, not an implementable method.

<!-- BEGIN GENERATED HEADROOM TABLE -->
| Assay | Loci | Consensus correct | Oracle correct | Consensus errors | Recoverable | No caller correct |
|---|---:|---:|---:|---:|---:|---:|
| WES | 153 | 143 | 149 | 10 | 6 | 4 |
| RNA-seq | 118 | 113 | 113 | 5 | 0 | 5 |
<!-- END GENERATED HEADROOM TABLE -->

**Second-typing adjudication.** The second typing is the in silico retyping of
the same exomes by Abi-Rached *et al.* [37], specified by SHA-256
(decisions/20261009_reference_adjudication.json). The specified rule treats any
value that is not two or more colon-separated numeric fields as unavailable.
Some values carry a trailing asterisk. The README distributed with the file
does not explain it, but the source article does: an asterisk marks a typing
that disagreed with the previously published type and that the authors kept
after verification (legend and footnote of their S1 Table; their S3 Fig lists
each case with the published type it replaced and how it was confirmed) [37].
Under the specified rule, asterisked values are unavailable. The second typing is therefore available only where its source retained no disagreement with the earlier published type. Agreement with the reference at available loci follows from that rule. The corrected-value column strips the asterisk. We added it after seeing the earlier results (decisions/20261009_reference_adjudication_posthoc.json); decisions/20261012_second_typing_asterisk_documented.json records the asterisk's documented meaning. The G column is
the lenient compatibility result obtained by mapping each two-field allele to
every compatible official IPD-IMGT/HLA 3.65.0 G group; it is not exact
G-group equivalence. The P column applies the corresponding official P-group
mapping. Both require a bijective pairing of the two alleles.

<!-- BEGIN GENERATED ADJUDICATION TABLE -->
| Assay | Subject | Gene | Reference | ChampHLA-Consensus | Planned adjudication | Second typing's corrected value (asterisked in the source) | G-compatible under a two-field mapping | P-compatible under a two-field mapping |
|---|---|---|---|---|---|---|---|---|
| WES | NA10847 | HLA-C | C*07:02+C*12:03 | C*07:01+C*12:03 | unavailable | C*07:01+C*12:03 | no | no |
| WES | NA11840 | HLA-B | B*27:03+B*57:01 | B*27:05+B*57:01 | unavailable | B*27:05+B*57:01 | no | no |
| WES | NA18504 | HLA-C | C*02:02+C*12:03 | C*02:10+C*12:03 | unavailable | C*02:10+C*12:03 | yes | yes |
| WES | NA18505 | HLA-C | C*02:02+C*07:01 | C*02:10+C*07:01 | unavailable | C*02:10+C*07:01 | yes | yes |
| WES | NA18507 | HLA-C | C*02:02+C*17:01 | C*02:10+C*17:01 | unavailable | C*02:10+C*17:01 | yes | yes |
| WES | NA18522 | HLA-C | C*02:02+C*07:01 | C*02:10+C*07:01 | unavailable | C*02:10+C*07:01 | yes | yes |
| WES | NA18537 | HLA-A | A*02:01+A*11:01 | A*02:07+A*11:01 | unavailable | A*02:07+A*11:01 | no | no |
| WES | NA19116 | HLA-B | B*07:02+B*39:03 | B*07:02+B*39:24 | unavailable | B*07:02+B*39:24 | no | no |
| WES | NA19129 | HLA-C | C*07:01+C*07:02 | C*07:02+C*07:18 | unavailable | C*07:02+C*07:18 | yes | yes |
| WES | NA19131 | HLA-A | A*66:02+A*68:02 | A*66:03+A*68:02 | unavailable | A*66:03+A*68:02 | no | no |
| RNA-seq | NA10847 | HLA-C | C*07:02+C*12:03 | C*07:01+C*12:03 | unavailable | C*07:01+C*12:03 | no | no |
| RNA-seq | NA11840 | HLA-B | B*27:03+B*57:01 | B*27:05+B*57:01 | unavailable | B*27:05+B*57:01 | no | no |
| RNA-seq | NA18505 | HLA-C | C*02:02+C*07:01 | C*02:10+C*07:01 | unavailable | C*02:10+C*07:01 | yes | yes |
| RNA-seq | NA19116 | HLA-B | B*07:02+B*39:03 | B*07:02+B*39:24 | unavailable | B*07:02+B*39:24 | no | no |
| RNA-seq | NA19131 | HLA-A | A*66:02+A*68:02 | A*66:03+A*68:02 | unavailable | A*66:03+A*68:02 | no | no |
<!-- END GENERATED ADJUDICATION TABLE -->

The sensitivity analysis rescores every method on the loci where both typings
agree. It is chosen by agreement between the typings, never by agreement with
any method.

<!-- BEGIN GENERATED REFERENCE AGREEMENT TABLE -->
| Assay | Method | All exact loci, correct | Loci where both typings agree, correct |
|---|---|---:|---:|
| WES | ChampHLA-Consensus | 143/153 | 143/143 |
| WES | Algorithm-family-restricted champion–challenger | 141/153 | 141/143 |
| WES | Best single caller (nested CV) | 142/153 | 141/143 |
| WES | Champion–challenger | 141/153 | 141/143 |
| WES | Logistic meta-consensus | 140/153 | 140/143 |
| WES | Strict majority | 141/153 | 141/143 |
| WES | Two-thirds consensus | 136/153 | 136/143 |
| WES | Two-thirds-guarded champion–challenger | 141/153 | 141/143 |
| WES | Vote-support-restricted champion–challenger | 143/153 | 143/143 |
| WES | HLA-HD | 131/153 | 131/143 |
| WES | OptiType | 142/153 | 141/143 |
| WES | POLYSOLVER | 138/153 | 137/143 |
| WES | SpecHLA | 134/153 | 131/143 |
| WES | T1K | 125/153 | 124/143 |
| RNA-seq | ChampHLA-Consensus | 113/118 | 112/112 |
| RNA-seq | Algorithm-family-restricted champion–challenger | 109/118 | 108/112 |
| RNA-seq | Best single caller (nested CV) | 111/118 | 111/112 |
| RNA-seq | Champion–challenger | 113/118 | 112/112 |
| RNA-seq | Logistic meta-consensus | 113/118 | 112/112 |
| RNA-seq | Strict majority | 106/118 | 106/112 |
| RNA-seq | Two-thirds consensus | 106/118 | 106/112 |
| RNA-seq | Two-thirds-guarded champion–challenger | 113/118 | 112/112 |
| RNA-seq | Vote-support-restricted champion–challenger | 113/118 | 112/112 |
| RNA-seq | HLA-HD | 112/118 | 112/112 |
| RNA-seq | OptiType | 112/118 | 111/112 |
| RNA-seq | T1K | 101/118 | 100/112 |
| RNA-seq | arcasHLA | 58/118 | 58/112 |
<!-- END GENERATED REFERENCE AGREEMENT TABLE -->

The next table repeats caller-error φ on the same subset. In WES it ranged from −0.08 to 0.31 over the ten caller pairs (median
0.02), against 0.28 to 0.59 on all exact loci. OptiType and POLYSOLVER were the most correlated WES pair across all loci (φ=0.59, eight joint-error loci). The pair had no joint error on this subset. In RNA-seq, φ ranged from −0.09 to 0.01 (median 0.00), against 0.11 to 0.82 across all exact loci. HLA-HD and OptiType were the most correlated pair overall (φ=0.82) but shared no error on this subset, nor did arcasHLA and HLA-HD. Only arcasHLA and T1K were wrong together on the subset. These values rest
on few errors (two for OptiType in WES; none for HLA-HD and one for OptiType in
RNA-seq) and carry no intervals. The subset also requires a further exome-based caller to agree with the reference, removing loci where exome callers jointly disagree. It explains the all-loci φ and does not estimate independence.
[RESULT:DEV_REFERENCE_AGREEMENT_PHI_WES_RANGE]
[RESULT:DEV_REFERENCE_AGREEMENT_PHI_RNASEQ_RANGE]
[RESULT:DEV_ERROR_PHI_WES_RANGE_ALL]
[RESULT:DEV_REFERENCE_AGREEMENT_PHI_WES_OPTITYPE_POLYSOLVER]
[RESULT:DEV_REFERENCE_AGREEMENT_PHI_RNASEQ_HLA_HD_OPTITYPE]
[RESULT:DEV_REFERENCE_AGREEMENT_PHI_RNASEQ_ARCASHLA_HLA_HD]
[RESULT:DEV_REFERENCE_AGREEMENT_PHI_RNASEQ_ARCASHLA_T1K]
[RESULT:DEV_ERROR_PHI_WES_OPTITYPE_POLYSOLVER]
[RESULT:DEV_ERROR_PHI_RNASEQ_HLA_HD_OPTITYPE]
[RESULT:DEV_ERROR_PHI_RNASEQ_RANGE_ALL]
[RESULT:DEV_REFERENCE_AGREEMENT_WES_CALLER_OPTITYPE]
[RESULT:DEV_REFERENCE_AGREEMENT_RNASEQ_CALLER_HLA_HD]
[RESULT:DEV_REFERENCE_AGREEMENT_RNASEQ_CALLER_OPTITYPE]

<!-- BEGIN GENERATED REFERENCE AGREEMENT PHI TABLE -->
| Assay | Caller 1 | Caller 2 | All exact loci: error φ (both wrong/loci) | Loci where both typings agree | Both right / only 2 wrong / only 1 wrong / both wrong | Error φ where both typings agree |
|---|---|---|---:|---:|---:|---:|
| WES | HLA-HD | OptiType | 0.53 (9/153) | 143 | 129/2/12/0 | -0.04 |
| WES | HLA-HD | POLYSOLVER | 0.49 (10/153) | 143 | 126/5/11/1 | 0.06 |
| WES | HLA-HD | SpecHLA | 0.35 (9/153) | 143 | 121/10/10/2 | 0.09 |
| WES | HLA-HD | T1K | 0.43 (13/153) | 143 | 116/15/8/4 | 0.18 |
| WES | OptiType | POLYSOLVER | 0.59 (8/153) | 143 | 135/6/2/0 | -0.02 |
| WES | OptiType | SpecHLA | 0.36 (6/153) | 143 | 129/12/2/0 | -0.04 |
| WES | OptiType | T1K | 0.39 (8/153) | 143 | 122/19/2/0 | -0.05 |
| WES | POLYSOLVER | SpecHLA | 0.48 (9/153) | 143 | 128/9/3/3 | 0.31 |
| WES | POLYSOLVER | T1K | 0.30 (8/153) | 143 | 118/19/6/0 | -0.08 |
| WES | SpecHLA | T1K | 0.28 (9/153) | 143 | 115/16/9/3 | 0.10 |
| RNA-seq | arcasHLA | HLA-HD | 0.23 (6/118) | 112 | 58/0/54/0 | 0.00 |
| RNA-seq | arcasHLA | OptiType | 0.15 (5/118) | 112 | 57/1/54/0 | -0.09 |
| RNA-seq | arcasHLA | T1K | 0.11 (11/118) | 112 | 52/6/48/6 | 0.01 |
| RNA-seq | HLA-HD | OptiType | 0.82 (5/118) | 112 | 111/1/0/0 | 0.00 |
| RNA-seq | HLA-HD | T1K | 0.45 (5/118) | 112 | 100/12/0/0 | 0.00 |
| RNA-seq | OptiType | T1K | 0.45 (5/118) | 112 | 99/12/1/0 | -0.03 |
<!-- END GENERATED REFERENCE AGREEMENT PHI TABLE -->

The last table counts each caller's errors on this subset and those the vote corrects. In WES the vote was correct at all 12
of HLA-HD's errors, all 12 of SpecHLA's and all 19 of T1K's, and it made no
error on the subset in either assay. Where the typings agree, the vote removes individual-caller errors and nearly equals the strongest caller, which makes almost none (OptiType, two errors in 143 WES loci; HLA-HD, none in 112 RNA-seq loci). Shared errors do not explain this pattern.
[RESULT:DEV_REFERENCE_AGREEMENT_WES_VOTE_CORRECTS_HLA_HD]
[RESULT:DEV_REFERENCE_AGREEMENT_WES_VOTE_CORRECTS_SPECHLA]
[RESULT:DEV_REFERENCE_AGREEMENT_WES_VOTE_CORRECTS_T1K]
[RESULT:DEV_REFERENCE_AGREEMENT_WES_SIMPLEPLURALITYLEX]
[RESULT:DEV_REFERENCE_AGREEMENT_WES_CALLER_OPTITYPE]
[RESULT:DEV_REFERENCE_AGREEMENT_RNASEQ_SIMPLEPLURALITYLEX]
[RESULT:DEV_REFERENCE_AGREEMENT_RNASEQ_CALLER_HLA_HD]

<!-- BEGIN GENERATED REFERENCE AGREEMENT CORRECTION TABLE -->
| Assay | Caller | Loci where both typings agree | Caller errors | Of these, vote correct | Vote errors | Of these, caller correct |
|---|---|---:|---:|---:|---:|---:|
| WES | HLA-HD | 143 | 12 | 12 | 0 | 0 |
| WES | OptiType | 143 | 2 | 2 | 0 | 0 |
| WES | POLYSOLVER | 143 | 6 | 6 | 0 | 0 |
| WES | SpecHLA | 143 | 12 | 12 | 0 | 0 |
| WES | T1K | 143 | 19 | 19 | 0 | 0 |
| RNA-seq | arcasHLA | 112 | 54 | 54 | 0 | 0 |
| RNA-seq | HLA-HD | 112 | 0 | 0 | 0 | 0 |
| RNA-seq | OptiType | 112 | 1 | 1 | 0 | 0 |
| RNA-seq | T1K | 112 | 12 | 12 | 0 | 0 |
<!-- END GENERATED REFERENCE AGREEMENT CORRECTION TABLE -->

We retain previously fitted policies for transparency, labelled `exploratory_fitted` because development labels or performance informed their construction. Their results were not used
to reselect the primary rule:

- Best single caller (nested CV) uses the ten subject-level outer folds
  recovered with the earlier predictions. For each assay and fold, it selects the panel caller with the most exact correct calls on truth-retained loci in the other nine folds, breaking ties alphabetically. It applies that caller to the held-out fold, so a subject's truth never informs its own prediction. It was refitted under the current truth and call-state rules
  (decisions/20261009_nestedcv_refit.json) and is evaluated as a separate fitted
  stage after the predictions generated without reference genotypes.
- Champion–challenger uses a gene/assay champion and permits a
  reliability-weighted challenger only when its support and supporting-caller
  conditions are met (full definition in S7.1; Supplementary Figure S5).
- Two-thirds-guarded champion–challenger preserves a two-thirds vote when one
  exists, otherwise uses champion–challenger and then plurality as fallback.
- Vote-support-restricted champion–challenger permits overrides only in vote strata
  supported during development; otherwise it returns plurality.
- Logistic meta-consensus is an L2-regularized candidate scorer using vote,
  caller, assay, gene and confidence features.
- Algorithm-family-restricted champion–challenger requires support from at least two
  caller families before an override. Its families are those fixed in
  decisions/20260918_family_gate_measurement.json: alignment (OptiType, HLA-HD,
  POLYSOLVER), assembly or graph (Kourami, SpecHLA, T1K) and k-mer (arcasHLA,
  seq2HLA). This grouping is specific to this rule and differs from the per-caller
  descriptions of inference in S6.

The refitted best single caller chose OptiType in every WES fold and HLA-HD or
OptiType in every RNA-seq fold. It scored 142/153 on WES and 111/118 on
RNA-seq, compared with 143/153 and 113/118 for ChampHLA-Consensus. Neither
difference was significant (WES `+0.65` points, exact sign-flip Holm *p*=1.0;
RNA-seq `+1.69` points, exact sign-flip Holm *p*=0.5, descriptive cluster-*t*
Holm *p*=0.155). The replaced previous predictions were fitted under superseded labels and call states. They scored 140/153 and 99/118 and appeared significantly worse than the vote in RNA-seq; the scoring change, rather than the policy, explained that difference. The policy's fitted status
precludes a superiority claim in either direction.
[RESULT:DEV_CORRECTED_WES_BESTSINGLETOOL_NESTEDCV]
[RESULT:DEV_CORRECTED_RNASEQ_BESTSINGLETOOL_NESTEDCV]
[RESULT:DEV_PAIRED_WES_BESTSINGLETOOL_NESTEDCV]
[RESULT:DEV_PAIRED_RNASEQ_BESTSINGLETOOL_NESTEDCV]
[RESULT:DEV_FROZEN_NESTEDCV_LEGACY_WES]
[RESULT:DEV_FROZEN_NESTEDCV_LEGACY_RNASEQ]

The power projection resamples development subjects with replacement to each cohort size. It applies Holm step-down within each comparison's family to comparisons differing from the vote, as in the observed analysis. The projection assumes observed subject-level differences are true. It shows what a larger cohort would detect under that assumption; with few discordant subjects, the differences are themselves imprecise. It uses a normal approximation to the subject sign-flip
statistic inside simulation, whereas observed tests are exact. Entries are the proportion of replicates with a significant comparison. This is a conditional sensitivity analysis, not a sample-size guarantee.

<!-- BEGIN GENERATED POWER TABLE -->
| Assay | Comparator | Family | 130 subjects | 200 subjects | 300 subjects | 500 subjects | 1000 subjects |
|---|---|---|---:|---:|---:|---:|---:|
| WES | HLA-HD | descriptive comparator | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| WES | OptiType | descriptive comparator | 0.020 | 0.068 | 0.135 | 0.192 | 0.429 |
| WES | POLYSOLVER | descriptive comparator | 0.661 | 0.905 | 0.985 | 1.000 | 1.000 |
| WES | SpecHLA | descriptive comparator | 0.875 | 0.984 | 0.999 | 1.000 | 1.000 |
| WES | T1K | descriptive comparator | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| WES | Strict majority | descriptive comparator | 0.223 | 0.619 | 0.922 | 0.999 | 1.000 |
| WES | Two-thirds consensus | descriptive comparator | 0.995 | 1.000 | 1.000 | 1.000 | 1.000 |
| WES | Best single caller (nested CV) | exploratory fitted | 0.003 | 0.038 | 0.111 | 0.199 | 0.418 |
| WES | Champion–challenger | exploratory fitted | 0.101 | 0.451 | 0.835 | 0.997 | 1.000 |
| WES | Algorithm-family-restricted champion–challenger | exploratory fitted | 0.101 | 0.451 | 0.835 | 0.997 | 1.000 |
| WES | Vote-support-restricted champion–challenger | exploratory fitted | identical | identical | identical | identical | identical |
| WES | Logistic meta-consensus | exploratory fitted | 0.090 | 0.455 | 0.881 | 0.998 | 1.000 |
| WES | Two-thirds-guarded champion–challenger | exploratory fitted | 0.101 | 0.451 | 0.835 | 0.997 | 1.000 |
| RNA-seq | arcasHLA | descriptive comparator | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| RNA-seq | HLA-HD | descriptive comparator | 0.059 | 0.271 | 0.712 | 0.988 | 1.000 |
| RNA-seq | OptiType | descriptive comparator | 0.056 | 0.279 | 0.709 | 0.988 | 1.000 |
| RNA-seq | T1K | descriptive comparator | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| RNA-seq | Strict majority | descriptive comparator | 0.999 | 1.000 | 1.000 | 1.000 | 1.000 |
| RNA-seq | Two-thirds consensus | descriptive comparator | 0.999 | 1.000 | 1.000 | 1.000 | 1.000 |
| RNA-seq | Best single caller (nested CV) | exploratory fitted | 0.756 | 0.957 | 0.997 | 1.000 | 1.000 |
| RNA-seq | Champion–challenger | exploratory fitted | identical | identical | identical | identical | identical |
| RNA-seq | Algorithm-family-restricted champion–challenger | exploratory fitted | 0.965 | 1.000 | 1.000 | 1.000 | 1.000 |
| RNA-seq | Vote-support-restricted champion–challenger | exploratory fitted | identical | identical | identical | identical | identical |
| RNA-seq | Logistic meta-consensus | exploratory fitted | identical | identical | identical | identical | identical |
| RNA-seq | Two-thirds-guarded champion–challenger | exploratory fitted | identical | identical | identical | identical | identical |
<!-- END GENERATED POWER TABLE -->

### Analysis choices and their interpretation

This ledger records each material development-analysis change, its observed direction and size, and its consequence. “Before comparison with reference genotypes” in the
31 August protocol refers only to the later confirmation-protocol join; the
analysts had already compared reference genotypes with these caller outputs in the earlier
analysis that fitted champions and weights. The previous primary method did not
outperform the vote on the current scoring definition.

<!-- BEGIN GENERATED PROTOCOL CHANGE TABLE -->
| Date | Change | Direction and size | Effect on verdict | Truth exposure at decision |
|---|---|---|---|---|
| 2026-08-31 | Specify the two-thirds-guarded rule as primary; require it to outperform; Holm across WGS/WES/RNA-seq | Historical stored-output endpoint: guarded 142/153 versus plurality 143/153 WES; tied 113/118 RNA-seq | Previous primary failed to outperform: WES Holm p=1.0 against plurality; RNA-seq exact tie | Before the confirmation protocol comparison with reference typing, but not before analysts first saw truth: earlier truth on these caller outputs fitted champions and weights |
| 2026-09-08 (recorded 2026-09-18) | Make equal-weight plurality primary; Holm within assay; exclude invalid WGS | Changed the primary method after per-method accuracy was inspected; exact WES +1 correct versus previous primary, RNA-seq unchanged | Primary claim changed from superiority of a fitted rule to audited performance of plurality | After development truth and method accuracies had been seen |
| 2026-09-18 | Pre-register and run abstention on every singleton caller output | Lowered concordance; result not adopted at that time | No primary change; retained as sensitivity | After development results had been seen |
| 2026-09-24 | Adopt singleton abstention as then implemented; add post hoc 2-point non-inferiority margin | RNA-seq plurality 110/118 on current truth-retained loci under abstain-all scoring | Lowered the RNA-seq headline; non-inferiority remained sensitivity-only | After development results had been seen |
| 2026-09-28 | Exclude unresolved reference genotypes; finalize predictions; CR1 cluster-t test; separate descriptive/fitted Holm families | Exact denominators became 153 WES and 120 RNA-seq before later identity withholding | Four comparisons significant under the declared family structure; development status remained post hoc | After earlier analyses had joined truth to the same caller outputs |
| 2026-10-08 | Implement caller-native homozygous completion; keep abstain-all sensitivity | RNA-seq plurality 110 to 113; HLA-HD RNA-seq 97 to 110; arcasHLA 95 to 109; HLA-HD WES 110 to 126 | Raised RNA-seq headline and changed strongest RNA-seq caller from OptiType to HLA-HD | Rule implementation corrected after consequences were known |
| 2026-10-08 | Withhold NA07000 RNA-seq after truth-free sample-identity failure | RNA-seq plurality 113/120 to 113/118; both removed loci were errors | Raised RNA-seq proportion by reducing the denominator; numerator unchanged | Identity decision used truth-free cross-assay calls, but development outcomes were already known |
| 2026-10-09 | Refit nested-CV best-caller comparator under current truth and call-state rules | RNA-seq comparator 99/118 to 106/118 | Comparison became non-significant after Holm adjustment (p=0.188 in the recorded analysis) | Post hoc refit using development truth within training folds |
| 2026-10-09 | Make subject sign-flip, rather than CR1 cluster-t, govern significance | No result count changed | Same four comparisons significant under both tests at the time | Adopted after development results and both test outputs were available |
| 2026-10-09 to 2026-10-12 | Add recorded second-typing adjudication, then correct the documented asterisk interpretation | No registered primary count changed; historical corrected-reference vote checksums 142/143 WES and 112/112 RNA-seq | Reference-corrected sensitivity must accompany exact results; it does not replace the primary endpoint | Rules and correction recorded after development discordances and source values were inspected |
| 2026-10-13 | Correct T1K deployment and make the full reproducible v3.5.0 rerun the primary development evidence | v3.5.0 rerun endpoint: guarded 141/153 versus plurality 143/153 WES; guarded 113/118 versus plurality 113/118 RNA-seq; historical 142/143 and 112/112 remain checksums only | The reproducible v3.5.0 rerun replaced the historical stored outputs as the primary development evidence; extension and final headlines follow | Specified after all historical development and adjudication results were known; extension reference genotypes have not been used for scoring |
<!-- END GENERATED PROTOCOL CHANGE TABLE -->

### S7.1 Rule definitions

Both rules act on one subject, assay and gene at a time, over the assay's
intended-use panel (main Table 1). A caller is callable at a locus when it reports a complete unordered
two-field genotype or a caller-native homozygous declaration that is completed
under the Methods rule. A generic single reported allele remains partial and
is not completed into a homozygous genotype.

**ChampHLA-Consensus (equal-weight plurality, primary).**

```text
for each subject s, assay a, gene g:
    V = callers in panel(a) with a callable genotype x_c at (s, g)
    if V is empty: report no call
    n(x) = number of callers in V reporting genotype x
    report the x with the largest n(x)
    if several x share the largest n(x): report the lexicographically first
```

**Champion–challenger (exploratory fitted comparator; Supplementary Figure
S5).** Each caller receives an assay- and gene-specific weight fitted in the earlier analysis on superseded 390-locus WES and 321-locus RNA-seq sets (and WGS rows). These are not the current exact-endpoint loci. The weight is w = 0.7 r + 0.3 e, where r is exact concordance for that gene and assay. The calibrated term e equals r unless the caller
reports confidence values for at least half of its callable loci and both its
Brier score and expected calibration error are at most 0.35, in which case e =
r + (1 − max(Brier, ECE))(p̄ − r), with p̄ the caller's mean calibrated
probability. Default callers and override criteria were specified for each assay: for WES the champion is
OptiType for HLA-A, -B and -C, and a challenger needs a support fraction of at
least 0.35 and one supporting caller; for RNA-seq the champion is OptiType for
HLA-A and arcasHLA for HLA-B and HLA-C, with the same support threshold and two
supporting callers. The previously specified policy declares a margin criterion (0 for WES and RNA-seq). As implemented, it compares the challenger with itself, so the margin is always zero and never blocks an override. The rule below is the one that
produced the results, including those of the policies built on it.

```text
for each subject s, assay a, gene g:
    W(x) = sum of weights of callable panel callers reporting genotype x
    T    = sum of W(x) over all genotypes
    if the champion caller for (a, g) is callable with genotype x_ch:
        q = genotype with the largest W among genotypes other than x_ch
        support = W(q) / T
        if support and the number of callers supporting q meet the specified
           thresholds, and no allele of q is ambiguous: report q
        else: report x_ch
        (the implemented margin term is identically 0, so it adds no restriction)
    else (champion has no call):
        x1, x2 = genotypes with the largest and second-largest W
        if W(x1) > W(x2) and W(x1)/T >= 0.55 and (W(x1) - W(x2))/T >= 0.15:
            report x1
        else: report no call
```

Because the champions, weights and override criteria were chosen with development labels,
champion–challenger results on the same subjects are optimistic and are
reported only as exploratory comparisons.

The logistic meta-consensus refit is seeded, but it is not guaranteed to be
bit-for-bit reproducible across processes. In one verification run, a prediction at a WES locus outside the exact endpoint differed from the approved run because two candidate pairs were nearly tied. No reported result changed; the next run reproduced the approved registry exactly (`decisions/20261026_metaconsensus_floating_point_drift.json`). The fitted
comparators should therefore be read as approximate as well as exploratory.

## S8. Earlier analyses excluded from evidence

Earlier files reported different WES and RNA-seq headline values after invalid reference-ambiguity collapse and generic singleton completion. Those numbers remain
only in superseded decision records and quarantined artifacts; they are not
active results. A documented revision adopts caller-native homozygous completion,
generic-singleton abstention and the audited public-truth denominator.

WGS inputs to the caller run failed validity review because extraction did not
preserve all HLA-relevant alternate-contig and mate evidence. No WGS concordance,
ranking, accuracy or denominator is reproduced in this submission. The WGS
material is provenance only.

An earlier draft of this work, prepared under the same project name, also
combined several distinct study aims. The table records how each earlier component is treated, so it cannot be mistaken for current evidence.

| Earlier component | Present disposition | Reason |
| --- | --- | --- |
| WGS performance and rankings | Excluded; provenance only | HLA-relevant alternate-contig and mate evidence was not preserved. |
| Champion–challenger and MV-floor headline claims | Exploratory methods; limited definitions and development results retained in S7 | The policies were fitted or selected using the development resource and have no unseen validation. |
| Locityper/Immuannot pangenome “silver truth” | Excluded from evidence | The components act on the same selected haplotypes and do not provide independent biological truth; required databases and complete call-level provenance are unavailable. |
| NCI-60, GIAB and IHWG “external validation” | Excluded from active validation claims; NCI-60 estimates withdrawn (S9.6) | The arms are small, mixed-resolution, partly summary-only and lack a consistent call-level provenance chain. |
| Fingerprint-paired FIMM cross-modality concordance | Withdrawn and replaced by the identity-linked analysis in S9 | The earlier workbook lacked specimen identifiers and paired records by HLA allele fingerprint, making the endpoint circular. |
| FIMM WES LOH, HED and survival analyses | Excluded | The imbalance input was non-informative, and the clinical endpoints lack the evidence and governance required for this benchmark paper. |
| HPC/local installation tutorials and cohort-scale resource claims | Kept in versioned software documentation, not as manuscript evidence | The current single-sample test runs do not reconstruct the original execution or establish cohort-scale cost, runtime or reproducibility. |

## S9. Aggregate-only exploratory FIMM, VenEx and NCI-60 applications

### S9.1 Data scope and access

<!-- Registry mapping for the S9 aggregate tables, in original row order: 21; 48; `FIMM_PANEL_SPECIMEN_BULKRNA_WES_EXACT_PAIR`; `FIMM_PANEL_SPECIMEN_SCRNA_WES_EXACT_PAIR`; `FIMM_PANEL_SPECIMEN_BULKRNA_SCRNA_EXACT_PAIR`; `FIMM_PANEL_SPECIMEN_CONTESTED_BULKRNA_WES_EXACT_PAIR`; `FIMM_PANEL_SPECIMEN_CONTESTED_SCRNA_WES_EXACT_PAIR`; `FIMM_PANEL_SPECIMEN_CONTESTED_BULKRNA_SCRNA_EXACT_PAIR`; `FIMM_PANEL_DONOR_BULKRNA_WES_EXACT_PAIR_SENSITIVITY`; `FIMM_PANEL_DONOR_SCRNA_WES_EXACT_PAIR_SENSITIVITY`; `FIMM_PANEL_DONOR_BULKRNA_SCRNA_EXACT_PAIR_SENSITIVITY`; `FIMM_PANEL_DONOR_CONTESTED_BULKRNA_WES_EXACT_PAIR_SENSITIVITY`; `FIMM_PANEL_DONOR_CONTESTED_SCRNA_WES_EXACT_PAIR_SENSITIVITY`; `FIMM_PANEL_DONOR_CONTESTED_BULKRNA_SCRNA_EXACT_PAIR_SENSITIVITY`; `FIMM_BB72_SCRNA_A02_{SENSITIVITY,SPECIFICITY,PPV,NPV,AGREEMENT}`; `FIMM_BB72_SCRNA_A02_A68_A69_{SENSITIVITY,SPECIFICITY,PPV,NPV,AGREEMENT}`; `FIMM_BB72_BULK_RNA_A02_{SENSITIVITY,SPECIFICITY,PPV,NPV,AGREEMENT}`; `FIMM_BB72_BULK_RNA_A02_A68_A69_{SENSITIVITY,SPECIFICITY,PPV,NPV,AGREEMENT}`; `FIMM_BB72_WES_A02_{SENSITIVITY,SPECIFICITY,PPV,NPV,AGREEMENT}`; `FIMM_BB72_WES_A02_A68_A69_{SENSITIVITY,SPECIFICITY,PPV,NPV,AGREEMENT}`; `VENEX_WES_HLA_HD_CONTESTED_DISSENT`; `VENEX_WES_OPTITYPE_CONTESTED_DISSENT`; `VENEX_WES_SPECHLA_CONTESTED_DISSENT`; `VENEX_WES_T1K_CONTESTED_DISSENT`; `VENEX_WES_POLYSOLVER_CONTESTED_DISSENT` -->

These post hoc applications are retained only to show that agreement and
within-panel dissent do not establish accuracy. They are ineligible for
accuracy, external-validation, clinical-utility or abstract claims.
`FIMM_AML_MDS` and `VENEX_WES` are separate exploratory datasets. The FIMM
three-caller deviation applies only to this cohort and to non-accuracy
reporting; it does not change the specified 1000 Genomes panels. The source
workbooks, row-level calls and specimen–donor mappings remain in controlled
storage. Public release is limited to privacy-reviewed aggregate artifacts,
their SHA-256 manifest and the figures derived from them.

The controlled source files remain restricted; the public release contains only aggregate results.

### S9.2 Withdrawal of the fingerprint-paired analysis and FIMM import rules

The earlier FIMM concordance analysis is withdrawn. A stripped workbook lacked specimen identifiers. Specimens were paired by HLA allele fingerprint before calculating HLA concordance, making the endpoint circular. Its figures and
numbers are not evidence. The empty WES allele-imbalance screen is also
withdrawn; no LOH claim is made. HLA evolutionary divergence, survival and
clinical-utility analyses remain out of scope.

The importer used here requires an explicit specimen identifier. Repeated rows for one specimen, assay and caller are collapsed only if their genotypes agree. A disagreement becomes a caller no-call. Singleton alleles are partial
calls, bare integers are invalid and missing tokens are no-calls. Of 2,642 source rows, 2,610 were imported. Replicate collapse left 7,179 caller-level locus rows (one per specimen, assay, caller and gene). There
were 81 replicate conflicts and 89 numeric-allele artefacts. The consensus
unit used below is coarser: one specimen–assay–gene locus, which combines the
caller-level rows of up to three callers.
[RESULT:FIMM_PANEL_FLOW_ROWS_READ]
[RESULT:FIMM_PANEL_FLOW_ROWS_IMPORTED]
[RESULT:FIMM_PANEL_FLOW_LOCUS_ROWS_AFTER_REPLICATE_COLLAPSE]
[RESULT:FIMM_PANEL_FLOW_REPLICATE_CONFLICTS]
[RESULT:FIMM_PANEL_FLOW_LOCUS_CELLS_NUMERIC_ARTEFACT]

The cross-modality unit is the specimen. Two eligibility definitions are
coequal:
- `all_callable` requires a complete unordered two-field plurality pair in
  both assays;
- `contested_both` additionally requires at least two valid callers in each
  assay.

The denominator difference therefore reflects caller availability rather than
selection of different specimens. Donor collapse is sensitivity-only. All
complete longitudinal calls must agree; otherwise the donor–modality locus is
a `longitudinal_conflict` and is excluded. A collapsed donor call meets
`contested_both` only when every contributing callable longitudinal specimen
had at least two valid callers.

<!-- Registry mapping for panel-composition counts: FIMM_PANEL_WES_CALLABLE_CALLERS_3; FIMM_PANEL_BULKRNA_CALLABLE_CALLERS_3; FIMM_PANEL_WES_CALLABLE_CALLERS_0; FIMM_PANEL_WES_CALLABLE_CALLERS_1; FIMM_PANEL_WES_CALLABLE_CALLERS_2; FIMM_PANEL_WES_CALLABLE_CALLERS_3; FIMM_PANEL_BULKRNA_CALLABLE_CALLERS_0; FIMM_PANEL_BULKRNA_CALLABLE_CALLERS_1; FIMM_PANEL_BULKRNA_CALLABLE_CALLERS_2; FIMM_PANEL_BULKRNA_CALLABLE_CALLERS_3; FIMM_PANEL_SCRNA_CALLABLE_CALLERS_1; FIMM_PANEL_SCRNA_CALLABLE_CALLERS_2 -->

Specimen–assay–gene loci by the number of valid callers:

| Assay | 0 valid callers | 1 valid caller | 2 valid callers | 3 valid callers |
| --- | ---: | ---: | ---: | ---: |
| WES | 344 | 2,211 | 466 | 21 |
| Bulk RNA | 207 | 696 | 330 | 48 |
| scRNA-seq | 0 | 18 | 75 | 0 |

The zero cells in the scRNA-seq row are structural absences from the released
aggregate, not suppressed observations. Supplementary Figure S6 shows the
panel composition next to the specimen-level endpoint.

### S9.3 FIMM cross-modality results

Specimen-level Wilson intervals [44] are unadjusted for donor clustering,
because several specimens can come from one donor. The donor-collapsed rows
give the donor-level view.

When both assays had at least two valid callers, exact-pair agreement was:
- bulk RNA–WES: 62/70 (88.6%; Wilson 95% CI 79.0–94.1%);
- scRNA-seq–WES: 21/24 (87.5%; 69.0–95.7%);
- bulk RNA–scRNA-seq: 18/21 (85.7%; 65.4–95.0%).

Across all complete callable pairs, the results were 854/958 (89.1%;
87.0–91.0%), 85/93 (91.4%; 83.9–95.6%) and 84/93 (90.3%; 82.6–94.8%) in the
same order. The denominator difference reflects caller availability, not
selection of a different biological cohort.
[RESULT:FIMM_PANEL_SPECIMEN_BULKRNA_WES_EXACT_PAIR]
[RESULT:FIMM_PANEL_SPECIMEN_SCRNA_WES_EXACT_PAIR]
[RESULT:FIMM_PANEL_SPECIMEN_BULKRNA_SCRNA_EXACT_PAIR]
[RESULT:FIMM_PANEL_SPECIMEN_CONTESTED_BULKRNA_WES_EXACT_PAIR]
[RESULT:FIMM_PANEL_SPECIMEN_CONTESTED_SCRNA_WES_EXACT_PAIR]
[RESULT:FIMM_PANEL_SPECIMEN_CONTESTED_BULKRNA_SCRNA_EXACT_PAIR]

| Pairing | Eligibility | Assay pair | Agreement/overlap | Estimate, % (Wilson 95% CI) |
| --- | --- | --- | ---: | ---: |
| Specimen, coequal | All callable | Bulk RNA–WES | 854/958 | 89.1 (87.0–91.0) |
| Specimen, coequal | All callable | scRNA-seq–WES | 85/93 | 91.4 (83.9–95.6) |
| Specimen, coequal | All callable | Bulk RNA–scRNA-seq | 84/93 | 90.3 (82.6–94.8) |
| Specimen, coequal | Contested in both | Bulk RNA–WES | 62/70 | 88.6 (79.0–94.1) |
| Specimen, coequal | Contested in both | scRNA-seq–WES | 21/24 | 87.5 (69.0–95.7) |
| Specimen, coequal | Contested in both | Bulk RNA–scRNA-seq | 18/21 | 85.7 (65.4–95.0) |
| Donor, sensitivity | All callable | Bulk RNA–WES | 340/350 | 97.1 (94.8–98.4) |
| Donor, sensitivity | All callable | scRNA-seq–WES | 58/63 | 92.1 (82.7–96.6) |
| Donor, sensitivity | All callable | Bulk RNA–scRNA-seq | 72/80 | 90.0 (81.5–94.8) |
| Donor, sensitivity | Contested in both | Bulk RNA–WES | 2/2 | 100.0 (34.2–100.0) |
| Donor, sensitivity | Contested in both | scRNA-seq–WES | 0/0 | non-estimable |
| Donor, sensitivity | Contested in both | Bulk RNA–scRNA-seq | 0/0 | non-estimable |

The donor collapse removed 233 WES and 28 bulk-RNA donor–loci with conflicting
longitudinal calls, so the donor estimates are not promoted over the specimen
analysis. [RESULT:FIMM_PANEL_WES_LONGITUDINAL_CONFLICTS]
[RESULT:FIMM_PANEL_BULKRNA_LONGITUDINAL_CONFLICTS]
All assay pairs use overlapping caller sets. Removing the shared callers leaves
zero overlap for each pair, so the caller-disjoint sensitivity is explicitly
non-estimable. [RESULT:FIMM_PANEL_DISJOINT_BULKRNA_WES_NON_ESTIMABLE]
[RESULT:FIMM_PANEL_DISJOINT_SCRNA_WES_NON_ESTIMABLE]
[RESULT:FIMM_PANEL_DISJOINT_BULKRNA_SCRNA_NON_ESTIMABLE]

All-callable pairs include many loci with a single valid caller (2,211 of 3,042 WES locus rows). The contested-in-both rows require at least two valid callers in each assay; both eligibility definitions are coequal exploratory views. Within WES, dissent from the panel plurality at contested loci was:
- arcasHLA: 167/486 (34.4%; Wilson 95% CI 30.3–38.7%);
- OptiType: 36/391 (9.2%; 6.7–12.5%);
- SpecHLA: 13/118 (11.0%; 6.6–17.9%).

This is within-panel dissent, not error against truth.
[RESULT:FIMM_PANEL_WES_CALLABLE_CALLERS_1]
[RESULT:FIMM_PANEL_WES_ARCASHLA_CONTESTED_DISSENT]
[RESULT:FIMM_PANEL_WES_OPTITYPE_CONTESTED_DISSENT]
[RESULT:FIMM_PANEL_WES_SPECHLA_CONTESTED_DISSENT]

These estimates measure agreement between related caller panels on different assay inputs. They do not measure accuracy, and shared callers can
raise agreement through correlated decisions.

### S9.4 FIMM BB7.2 serogroup agreement

BB7.2 flow status was joined by donor identity. The antibody was first
characterized as an HLA-A2 typing reagent that also recognizes an HLA-A28
variant [32]. On single-antigen beads it is specific for HLA-A\*02 and A\*69
at low concentration, and cross-reacts with A\*68, A\*23 and A\*24 only at high
concentration [33]. A\*02 is therefore the primary mapping. The
A\*02/A\*68/A\*69 sensitivity mapping is a deliberately broad,
high-concentration bound; an A\*02/A\*69 mapping alone was not computed.

The metrics use the flow-linked subset (analysis tier C). They use donor-collapsed plurality calls from every caller available in that subset, rather than the three-caller FIMM panel of S9.1.
- Only 16 of 53 flow records linked to the sequenced subset.
- The informative linked donors were 8 for scRNA-seq, 14 for bulk RNA and 13
  for WES.
- All unlinked records remain in the source aggregate.

These are serogroup agreement metrics, not allele-level accuracy. The table
reports every confusion matrix and interval estimate.

| Modality | Mapping | TP/TN/FP/FN | Sensitivity | Specificity | PPV | NPV | Agreement |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| scRNA-seq | A*02 | 4/3/0/1 | 0.800 (0.376–0.964) | 1.000 (0.439–1.000) | 1.000 (0.510–1.000) | 0.750 (0.301–0.954) | 0.875 (0.529–0.978) |
| scRNA-seq | A*02/A*68/A*69 | 5/2/1/0 | 1.000 (0.566–1.000) | 0.667 (0.208–0.939) | 0.833 (0.436–0.970) | 1.000 (0.342–1.000) | 0.875 (0.529–0.978) |
| Bulk RNA | A*02 | 7/7/0/0 | 1.000 (0.646–1.000) | 1.000 (0.646–1.000) | 1.000 (0.646–1.000) | 1.000 (0.646–1.000) | 1.000 (0.785–1.000) |
| Bulk RNA | A*02/A*68/A*69 | 7/6/1/0 | 1.000 (0.646–1.000) | 0.857 (0.487–0.974) | 0.875 (0.529–0.978) | 1.000 (0.610–1.000) | 0.929 (0.685–0.987) |
| WES | A*02 | 7/4/2/0 | 1.000 (0.646–1.000) | 0.667 (0.300–0.903) | 0.778 (0.453–0.937) | 1.000 (0.510–1.000) | 0.846 (0.578–0.957) |
| WES | A*02/A*68/A*69 | 7/3/3/0 | 1.000 (0.646–1.000) | 0.500 (0.188–0.812) | 0.700 (0.397–0.892) | 1.000 (0.439–1.000) | 0.769 (0.497–0.918) |

Supplementary Figure S7 shows the primary
confusion matrices and Wilson intervals for the primary and cross-reactivity
mappings.

Under the strict A\*02 mapping, the WES row has two false positives (specificity 0.667). WES plurality assigned an A\*02 allele to two BB7.2-negative donors. With only two such donors, no caller- or assay-specific
conclusion is drawn. Under the primary mapping, bulk RNA had no false
positives (specificity 1.000).

### S9.5 Separate VenEx WES diagnostic cohort

VenEx contains 86 WES samples and 258 class I sample–gene loci. Dissent is
measured against a plurality that includes the caller being compared, so it is
not error against truth. POLYSOLVER had no usable output: 64 samples had no
file and 22 had an empty output.
[RESULT:VENEX_WES_POLYSOLVER_MISSING]
[RESULT:VENEX_WES_POLYSOLVER_EMPTY]
It therefore had no mutually callable loci, and its dissent rate is
non-estimable. [RESULT:VENEX_WES_POLYSOLVER_CONTESTED_DISSENT]

| Caller | Contested loci | Dissents | Dissent, % (Wilson 95% CI) | Note |
| --- | ---: | ---: | ---: | --- |
| HLA-HD | 230 | 0 | 0.0 (0.0–1.6) | Within-panel dissent, not error |
| OptiType | 256 | 2 | 0.8 (0.2–2.8) | Within-panel dissent, not error |
| SpecHLA | 231 | 26 | 11.3 (7.8–16.0) | Within-panel dissent, not error |
| T1K | 230 | 1 | 0.4 (0.1–2.4) | Historical deployment only; excluded from the corrected main development analysis |
| POLYSOLVER | 0 | 0 | non-estimable | No usable output in 86 samples (64 missing, 22 empty) |

[RESULT:VENEX_WES_HLA_HD_CONTESTED_DISSENT]
[RESULT:VENEX_WES_OPTITYPE_CONTESTED_DISSENT]
[RESULT:VENEX_WES_SPECHLA_CONTESTED_DISSENT]
[RESULT:VENEX_WES_T1K_CONTESTED_DISSENT]

SpecHLA's 11.3% measures within-panel dissent. Neither it nor any other VenEx
diagnostic establishes HLA accuracy. Supplementary Figure S8 presents caller
availability and contested-locus dissent together.

### S9.6 NCI-60 cell-line application (legacy analysis withdrawn; regeneration under way)

HLA class I genotypes of the NCI-60 cancer cell lines have been published from
sequence-based typing of exons 2 and 3 [34]. An earlier analysis ran callers on
42 NCI-60 cell lines, before the current singleton rule and the revised
reference parser existed:
- WES: HLA-HD, OptiType, SpecHLA and T1K (no POLYSOLVER);
- RNA-seq: arcasHLA, HLA-HD, OptiType, seq2HLA, SpecHLA and T1K.

It scored them with the earlier harmonization and a heuristic confidence weighting (`artifacts/source_results/publication_assessment.json`). Its panels,
call states, reference parsing and caller run all differ from those of the
development analysis. The stored artifact also lacks the scored per-locus
results, so its concordance estimates cannot be traced to a registered result,
and they are withdrawn rather than reported. Before any NCI-60 estimate is
reported, the analysis would have to be regenerated under the current rules,
with the current workflow release and registry rows. In no case is it external
validation.

That regeneration is under way under a decision documented on 26 October 2026,
before any NCI-60 prediction existed
(`decisions/20261026_nci60_v350_regeneration.json`). Every cell line in the
class I table of the published typing that has public paired reads is run once
per assay with workflow release 3.5.0 and the development panels: 57 WES and 58
RNA-seq lines (`cohorts/nci60_v350_manifest.tsv`). One line has no paired WES
reads and is excluded and listed, and RNA-seq reads are subsampled to 50 million
pairs as in the earlier run. POLYSOLVER cannot run from FASTQ input in this
release and is a declared non-call. The published typing is parsed with unresolved or invalid entries excluded
(`src/champhla_recovery/nci60.py`): its tabulation must match the article's
own table cell by cell. Unresolved two-digit ambiguities, new alleles,
unresolved entries, designations absent from IPD-IMGT/HLA 3.65.0 and any other
token shape are excluded and listed. A single listed allele is read as a
homozygous genotype, with a sensitivity analysis that excludes such loci.
Predictions are finalized before a single comparison with the reference typing, and the result will be
reported here, whatever its direction, as an exploratory descriptive
application with registry rows and binomial intervals.

## Supplementary figure legends

**Supplementary Figure S1. Caller call-state composition.** WES (A) and RNA-seq
(B) bars partition each fixed assay–locus denominator into callable,
singleton/partial, missing/failed-output, absent-row and invalid states; segment
labels are counts. The normalized development table does not separate runtime failure from empty or missing output. No independent runtime-failure rate is inferred; Supplementary Table S10.1 gives rerun task dispositions.

**Supplementary Figure S2. Vote-threshold callability–concordance trade-off.**
WES (A) and RNA-seq (B) show ChampHLA-Consensus, strict majority and two-thirds
consensus in threshold order. Horizontal and vertical bars are marginal 95%
subject-cluster percentile bootstrap intervals for callability and
fixed-denominator concordance. Both axes are truncated to the observed range.
The blue circle denotes ChampHLA-Consensus, the dark square strict majority and
the grey diamond two-thirds consensus. The identical RNA-seq strict-majority
and two-thirds point estimates use a composite marker and shared label; no
jitter is applied.

**Supplementary Figure S3. Support-profile concordance.** WES (A) and RNA-seq
(B) use unreduced k-of-n profiles. Points and exact 95% binomial intervals are
shown only for strata with at least five loci. Profiles with fewer than five
loci remain listed with their denominators but their percentages and intervals
are suppressed. The 0/0 profile is a non-call state outside the concordance
scale. These strata are descriptive, not calibrated probabilities.

**Supplementary Figure S4. Truth-definition sensitivity.** WES (A) and RNA-seq
(B) compare exact two-field, ambiguity-compatible, G-compatible under a
two-field mapping and P-group-compatible under a two-field mapping endpoints. Points and bars are estimates and 95%
subject-cluster percentile bootstrap intervals. Each facet states its own
denominator; estimates across different truth definitions are not connected or
treated as paired. Each percentage axis is truncated below 100% to the observed
range and stops at 100%. Colours and shapes follow Figure 2.

**Supplementary Figure S5. Champion–challenger decision flow.** The exploratory
fitted comparator defined in Supplementary S7.1. When the gene's selected
champion caller is callable, its genotype is reported unless the
highest-weighted alternative passes every override condition; the declared margin
criterion is inactive as implemented (S7.1). When the champion has no call, a
reliability-weighted consensus is reported only if it is untied and clears
fixed support and margin thresholds. Weights and champions were fitted in the
earlier analysis on the superseded development denominators.

**Supplementary Figure S6. Exploratory FIMM cross-modality agreement and
eligibility.** (A) Specimen-level exact unordered two-field agreement with
Wilson 95% intervals for two coequal definitions: all complete callable pairs,
and pairs with at least two valid callers in both assays. Counts are
agreement/overlap; their denominator difference reflects caller availability,
not biological sample selection. (B) Locus-row composition by the number of
valid callers. Zero valid callers means missing consensus evidence, and one
valid caller is not a vote. Because the callers are shared, panel agreement is
not independent HLA truth. The recorded replicate-conflict, numeric-artefact,
partial and missing counts are printed below the endpoint panel.

**Supplementary Figure S7. Exploratory FIMM BB7.2 serogroup agreement.** (A)
Primary A*02 confusion matrices for scRNA-seq, bulk RNA and WES; panel titles
give the informative linked donors out of all 53 flow records. (B)
Sensitivity, specificity and overall agreement with Wilson 95% intervals, under
the A*02 primary mapping and the A*02/A*68/A*69 cross-reactivity sensitivity
mapping. BB7.2 supplies serogroup-level evidence only; linkage is incomplete,
and the endpoint is not allele-level accuracy.

**Supplementary Figure S8. Exploratory VenEx WES diagnostics.** (A) Native
caller-output availability across 86 samples. (B) Contested-locus dissent from
the inclusive ChampHLA plurality, with Wilson 95% intervals. POLYSOLVER is
shown as non-estimable at zero mutually callable loci. Dissent is not error
against truth.

**Supplementary Figure S9. Stored-to-v3.5.0 caller-cell changes.** WES (A) and
RNA-seq (B) bars partition each panel caller's caller–gene cells by how the
v3.5.0 rerun call relates to the historical stored call. Categories are identical, call changed, non-call to callable, callable to non-call, and present only in the rerun. Values are percentages of that caller's cells, and
the counts are in Supplementary Table S10.2. The figure is aggregate-only and
uses no reference typing.

## S10. Reproducibility and software details

### Full-cohort v3.5.0 rerun audit tables

These aggregate tables are populated only after the documented 236-run roster has
passed checks of file checksums, workflow provenance and caller coverage. They contain no
subject identifiers and are not used as interim performance evidence.

**Supplementary Table S10.1. Caller-task disposition by assay and caller.**

<!-- BEGIN GENERATED RERUN TASK STATE TABLE -->
| Assay | Caller | Recorded caller task disposition | Caller tasks |
|---|---|---|---:|
| RNA-seq | arcasHLA | outputs present | 106 |
| RNA-seq | HLA-HD | outputs present | 106 |
| RNA-seq | OptiType | outputs present | 106 |
| RNA-seq | T1K | outputs present | 106 |
| WES | HLA-HD | outputs present | 130 |
| WES | OptiType | outputs present | 130 |
| WES | POLYSOLVER | outputs present | 130 |
| WES | SpecHLA | outputs present | 130 |
| WES | T1K | outputs present | 130 |
<!-- END GENERATED RERUN TASK STATE TABLE -->

**Supplementary Table S10.2. Stored-to-v3.5.0 caller-cell changes by assay and caller.**

<!-- BEGIN GENERATED RERUN CELL COMPARISON TABLE -->
| Assay | Caller | Stored-to-rerun cell state | Caller–gene cells |
|---|---|---|---:|
| RNA-seq | arcasHLA | call changed | 176 |
| RNA-seq | arcasHLA | identical | 142 |
| RNA-seq | HLA-HD | call changed | 7 |
| RNA-seq | HLA-HD | identical | 305 |
| RNA-seq | HLA-HD | new rerun cell | 6 |
| RNA-seq | OptiType | identical | 312 |
| RNA-seq | OptiType | new rerun cell | 6 |
| RNA-seq | T1K | call changed | 6 |
| RNA-seq | T1K | identical | 278 |
| RNA-seq | T1K | new rerun cell | 6 |
| RNA-seq | T1K | noncall to callable | 28 |
| WES | HLA-HD | call changed | 31 |
| WES | HLA-HD | identical | 359 |
| WES | OptiType | call changed | 5 |
| WES | OptiType | identical | 385 |
| WES | POLYSOLVER | call changed | 34 |
| WES | POLYSOLVER | identical | 356 |
| WES | SpecHLA | call changed | 47 |
| WES | SpecHLA | identical | 343 |
| WES | T1K | call changed | 23 |
| WES | T1K | callable to noncall | 7 |
| WES | T1K | identical | 332 |
| WES | T1K | noncall to callable | 28 |
<!-- END GENERATED RERUN CELL COMPARISON TABLE -->

Supplementary Figure S9 shows the same counts as proportions of each caller's
cells. Supplementary Table S10.3 classifies every changed cell without the reference
typing. We classify cells by zygosity transition, replacement of one or both alleles, change in allele group (first field) and, for T1K, agreement with a release 3.5.0 parser rule in the sample's checksummed audit. The classification also records whether another caller changed at the locus and whether more other panel callers' rerun genotypes match the stored or rerun pair.
Cells present only in the rerun are excluded.

In WES, OptiType changed least. Most changed allele pairs in the other callers
replace one allele of a heterozygous pair. Only a minority change homozygous calls to heterozygous ones. Most changes therefore lack the haplotype-loss pattern repaired by read rescue. Most changed WES cells are the only change at their locus. That points to caller-specific responses rather than a
swapped sample input.

Most T1K changes of call state follow a release 3.5.0 parser rule: either a
partial call became a native homozygous declaration, or the quality filter
reduced a pair. For HLA-HD, SpecHLA, T1K and OptiType in WES, the rerun call
more often matches the other callers; for POLYSOLVER, the stored call more often
does. In RNA-seq, the stored arcasHLA call matched more of the other callers in
almost every changed cell, consistent with the deployment defect described in
the main-text Limitations.

The historical run recorded neither its read handling nor its caller
executables and databases. We therefore cannot separate effects of the rerun's read route (HLA-read rescue and realignment to primary chr6) from caller-version or database differences. This classification is
descriptive and was not used to choose any input, caller or rule.

**Supplementary Table S10.3. Changes in caller outputs classified without reference genotypes.**

<!-- BEGIN GENERATED RERUN CELL CHANGE CHARACTER TABLE -->
| Assay | Caller | Changed cells | Call state changed | Homozygous to heterozygous | Heterozygous to homozygous | One allele replaced | Both alleles replaced | Allele group changed | Follows a 3.5.0 T1K parser rule | Only changed caller at the locus | Rerun call matches more panel callers | Stored call matches more panel callers |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| RNA-seq | arcasHLA | 176 | 0 | 17 | 15 | 99 | 45 | 26 | – | 149 | 1 | 167 |
| RNA-seq | HLA-HD | 7 | 0 | 1 | 0 | 4 | 2 | 1 | – | 2 | 4 | 2 |
| RNA-seq | T1K | 34 | 28 | 0 | 0 | 5 | 1 | 4 | 28 | 10 | 28 | 5 |
| WES | HLA-HD | 31 | 0 | 2 | 2 | 23 | 4 | 9 | – | 17 | 22 | 4 |
| WES | OptiType | 5 | 0 | 1 | 1 | 3 | 0 | 2 | – | 2 | 4 | 1 |
| WES | POLYSOLVER | 34 | 0 | 8 | 2 | 23 | 1 | 17 | – | 22 | 10 | 21 |
| WES | SpecHLA | 47 | 0 | 4 | 0 | 40 | 3 | 32 | – | 32 | 30 | 7 |
| WES | T1K | 58 | 35 | 1 | 1 | 19 | 2 | 9 | 35 | 45 | 39 | 8 |
<!-- END GENERATED RERUN CELL CHANGE CHARACTER TABLE -->

### Inputs for reproducing the analysis

- `data/development/normalized_caller_calls.tsv`, which contains no reference genotypes;
- `data/development/normalized_secondary_calls.tsv`, for previously generated exploratory
  predictions; and
- a downloaded public truth file whose checksum must match the specified value.

One command (`scripts/run_local_verification.sh`) regenerates selected truth, primary and secondary predictions, the comparison with reference genotypes, statistics, S12 restored analyses (given the recovered caller table), tables, figures, claim audit and DOCX. The exploratory FIMM and VenEx aggregates are
regenerated only inside the controlled environment that holds the patient data. Release mode fails if scientific stages are skipped, artifacts are stale, prediction inputs contain truth columns, active artifacts contain WGS results or scientific placeholders remain unresolved.
Outstanding author declarations and archival details are recorded separately in the author completion checklist.

The raw-read-to-caller Nextflow workflow is an external dependency outside this verified analysis. For the historical caller run, exact caller
executable versions, container digests, scheduler job identifiers and measured
historical caller resource use remain unavailable; historical costs were neither
reconstructed nor estimated. The v3.5.0 rerun that supplies the primary inputs
records the following for every sample
(`provenance/development_rerun_v350/truth_free_collection/sample_run_provenance.tsv`):

- the workflow release commit;
- the scheduler job identifier; and
- checksummed manifests of its inputs, container images, workflow files and
  result files.

Two later single-sample test runs on HG00096 provide current workflow,
container and scheduler evidence. These operational measurements do not reconstruct development-cohort use or establish cohort requirements. The analysis used Python 3.11.15, NumPy
1.26.4, SciPy 1.14.1, Matplotlib 3.9.2 and python-docx 1.2.0. The analysis can be reproduced from normalized outputs. Regenerating those outputs requires re-running the workflow from reads, outside the verified analysis.

### Caller-run and current-workflow provenance

The development callers were run in April and May 2026 with an unarchived
pre-release ChampHLA deployment on CSC – IT Center for Science (CSC)
infrastructure, by inference the Puhti cluster, since no job of this project on
its successor system predates July 2026. The stored T1K representation is
consistent with a parser change made on 18 April 2026 (commit `304abfc`), so the
whole caller run cannot be assigned to the earlier 7 April tree. The stored development calls lack the read-loss pattern described below. POLYSOLVER, the most affected caller, matched the vote's WES total in those outputs, but its historical read route is unrecorded. The
v3.5.0 rerun includes the read rescue, and there POLYSOLVER scored 138/153.
[RESULT:DEV_CORRECTED_WES_CALLER_POLYSOLVER]

The current workflow (release 3.5.0, differing from release 3.4.1 only in the T1K parser) uses SAMtools 1.21 and BWA 0.7.19 from CSC's Roihu software-module collection (bio-apps release v202603). Caller images are Singularity conversions of public Docker and BioContainers images, specified by SHA-256 in `configs/caller_resources_v2.json`; SpecHLA uses a native installation. The official IPD-IMGT/HLA 3.65.0 resources used for the G-group
and nomenclature sensitivity analyses are identified by their upstream release tag
and locally checksummed. The single-sample task measurements below do not reconstruct historical development-run resource use or establish cost or scaling.

### HG00096 re-run against the stored development calls

On 19 September 2026, HG00096 was run with pre-release revision
`91f035f6f0`. All 12 RNA-seq caller–gene calls from the Geuvadis BAM matched the
stored calls, whereas 4 of 12 WES calls from an HLA-region pre-extract matched;
the WES denominator was four callers by three genes because SpecHLA was absent.
On 9 October 2026, release 3.3.0 (tag `v3.3.0`, commit `360a449`) was run on the
whole-exome CRAM and matched 5 of 15 stored calls. These two WES routes lost
reads: the GRCh38 alignments place many reads from non-reference HLA alleles on
HLA-allele and chromosome 6 alternate-haplotype contigs, so the second
haplotype disappeared.

Also on 9 October, the release-3.4.0-equivalent WES tree `15f45cf` collected
those reads and realigned them to chromosome 6. Release tag `v3.4.0` (commit
`2a72a4b`) differs from that run tree only by version strings and the changelog.
All five callers then reported the same genotype at all three genes and 11 of 15
calls matched the stored calls. The four differences were HLA-HD at HLA-B and
HLA-C, SpecHLA at HLA-C and T1K at HLA-B. The 9 October RNA-seq run used release
3.4.0 on the Geuvadis BAM and matched 11 of 12 stored calls; arcasHLA reported a
different HLA-C allele. These one-subject diagnostics did not explain the four old/new WES differences through read rescue.
[RESULT:DEV_HG00096_RERUN_RNASEQ]
[RESULT:DEV_HG00096_RERUN_WES]
[RESULT:DEV_HG00096_WES_V3_3_0_WHOLE_EXOME]
[RESULT:DEV_HG00096_WES_V3_4_0_WHOLE_EXOME]
[RESULT:DEV_HG00096_WES_V3_4_0_CALLERS_UNANIMOUS_GENES]
[RESULT:DEV_HG00096_RNASEQ_V3_4_0_GEUVADIS_BAM]

**Current single-sample workflow test measurements.** Two successful HG00096 runs on the CSC Roihu cluster are reported. Both used pre-release revisions that break exact ties toward the last-sorting pair, unlike release 3.4.0. The RNA-seq run also used a locally modified seq2HLA module; the table gives revisions and image hashes. The DNA caller route
used a WGS-derived mate-aware HLA BAM, not WES reads; it therefore does not
estimate WES runtime. The RNA-seq route used paired FASTQ. Nextflow `realtime`
and `peak_rss` are task-level trace fields. Slurm `Elapsed`, `TotalCPU` and
batch-step `MaxRSS` are reported separately because their definitions and
instrumentation differ. Disagreement between the measurement sources is retained; neither smaller nor larger values are selected. Version fields are reported as emitted. OptiType produced usage text; T1K and arcasHLA produced empty fields, leaving those versions unresolved. SpecHLA ran
from a native local installation; the other caller rows used the named SIF.

<!-- BEGIN GENERATED COMPUTE SMOKE TABLE -->
| Route and actual input | Caller | Version output | Execution artifact | SIF SHA-256 (first 12) | Workflow revision | Slurm job | Nextflow realtime | Nextflow peak RSS, GB | Slurm elapsed | Slurm TotalCPU | Slurm MaxRSS, GB |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|
| DNA route (WGS-derived HLA BAM) | POLYSOLVER | v4 | polysolver | b4f39a6dd86d | 987f5eb | 1427634 | 4 min 39 s | 1.40 | 4 min 41 s | 20 min 30 s | 3.82 |
| DNA route (WGS-derived HLA BAM) | HLA-HD | HLA-HD version 1.4.0 | hlahd | 8fb9fa5ec339 | 987f5eb | 1427636 | 1 min 3 s | 0.93 | 1 min 6 s | 4 min 42 s | 7.12 |
| DNA route (WGS-derived HLA BAM) | SpecHLA | 1.0.7 | /projappl/project_2008084/SpecHLAx | native install | 987f5eb | 1427637 | 6 h 13 min 26 s | 1.00 | 6 h 14 min 34 s | 31 min 45 s | 2.42 |
| DNA route (WGS-derived HLA BAM) | Kourami | 0.9.6 | kourami | c267052e9621 | 987f5eb | 1427638 | 2 min 0 s | 5.90 | 2 min 2 s | 22 min 17 s | 7.55 |
| DNA route (WGS-derived HLA BAM) | OptiType | unresolved (usage output) | optitype | 7f3f32904a25 | 987f5eb | 1427643 | 25.8 s | 0.51 | 28 s | 32.331 s | 1.55 |
| DNA route (WGS-derived HLA BAM) | T1K | unresolved (empty output) | t1k | e34c4433021c | 987f5eb | 1427644 | 1 min 26 s | 3.00 | 1 min 29 s | 7 min 47 s | 3.51 |
| RNA-seq route (paired FASTQ) | OptiType | unresolved (usage output) | optitype | 7f3f32904a25 | ce31c74 (modified) | 1410979 | 9 min 29 s | 8.50 | 9 min 33 s | 9 min 50 s | 21.03 |
| RNA-seq route (paired FASTQ) | T1K | unresolved (empty output) | t1k | e34c4433021c | ce31c74 (modified) | 1410980 | 14 min 8 s | 11.30 | 14 min 12 s | 1 h 3 min 3 s | 12.60 |
| RNA-seq route (paired FASTQ) | seq2HLA | 2.3 | seq2hla | e64318d6806f | ce31c74 (modified) | 1410981 | 12 min 12 s | 0.11 | 12 min 15 s | 1 h 31 min 1 s | 2.39 |
| RNA-seq route (paired FASTQ) | HLA-HD | HLA-HD version 1.4.0 | hlahd | 8fb9fa5ec339 | ce31c74 (modified) | 1410983 | 19 min 12 s | 5.40 | 19 min 18 s | 2 h 51 min 52 s | 10.40 |
| RNA-seq route (paired FASTQ) | arcasHLA | unresolved (empty output) | arcashla | 60c42737ccb8 | ce31c74 (modified) | 1410984 | 5 min 58 s | 10.80 | 6 min 3 s | 9 min 8 s | 11.34 |
<!-- END GENERATED COMPUTE SMOKE TABLE -->

All rows describe one sample and successful tasks only. They are not monetary
costs, historical development-cohort measurements, scaling estimates or
accuracy evidence. Raw traces, task commands, launch wrappers, workflow source,
version files, container inspection output and scheduler records are preserved
under `provenance/compute_smoke/raw`; their hashes and row-level provenance are
recorded in `artifacts/compute_smoke_benchmark.tsv`.

## S11. Practical guide to running ChampHLA

This section describes the workflow release in the pipeline repository (Data
and software availability). The commands below were checked against that
release's parameter definitions; they are usage guidance, not part of the
verified evidence chain of this paper.

### S11.1 Requirements and inputs

The workflow requires Nextflow and either Docker or Singularity. Callers run
from containers; in the deployment used here SpecHLA ran from a native
installation (Supplementary S10). HLA-HD and T1K need separately obtained
reference databases, and the workflow stops at start-up if a requested caller's
database path is not set. Input is either a directory (`--input` with
`--input_type bam`, `cram` or `fastq`) or a CSV samplesheet
(`--input_samplesheet`) with columns `sample_id,bam_path`,
`sample_id,cram_path` or `sample_id,fastq_1,fastq_2`. CRAM input also needs
`--reference_fasta`.

The workflow wraps eight callers (main Table 1), each with its own process, container, preprocessing, invocation and parser. A
sequencing mode (DNA, bulk RNA-seq, PacBio HiFi or Oxford Nanopore) and the
resolved assay determine which callers run. Unless a caller list is given, the
workflow runs the assay's reference panel, declared in one configuration file
so that a partial installation can be detected. DNA-only callers are skipped
for RNA-seq input. The long-read modes currently run T1K only and, like WGS
(Supplementary S8), are not evaluated here. Each run also writes an HTML report.

From release 3.4.0, every DNA BAM or CRAM passes through a read-rescue step
before any caller. In one streaming pass, it collects reads from the chromosome 6 MHC window, every HLA-allele and chromosome 6 alternate-haplotype contig, and unplaced reads. It keeps complete pairs and realigns them to primary chromosome 6 with bwa. This needs `--hla_rescue_reference`, a primary
chromosome 6 FASTA with a bwa index, built by the workflow's
`build_hla_rescue_reference.sh` script. Release 3.3.0 lacked this step and lost the
second haplotype on GRCh38 alignments that carry such contigs (main Methods,
Study design). Alignments without those contigs keep their alignments.

### S11.2 Reproducing the evaluated rule

The consensus step is off by default. When enabled, it defaults to calibrated weighting and a gene list including class II genes. The `paper` profile enables the evaluated rule: equal weights, the assay's reference panel (`--tools` unset), HLA-A, -B and -C voting, and Methods call states (`--mv_call_states paper`). Combine it with an execution profile:

```text
# WES, BAM samplesheet, Slurm cluster with Singularity
nextflow run main.nf \
    --input_samplesheet samples.csv \
    --seq_type dna --run_modality wes \
    --extract_hla_region \
    --singularity_cache_dir /path/to/cache \
    --outdir results_wes \
    -profile slurm,singularity,paper -resume

# Bulk RNA-seq, paired FASTQ samplesheet, local Docker
nextflow run main.nf \
    --input_samplesheet rna_samples.csv \
    --seq_type rna --optitype_seq_type rna \
    --outdir results_rna \
    -profile docker,paper
```

The workflow parity test (<https://github.com/uoozcan/ChampHLA/blob/71f037d/tests/test_paper_parity.py>) feeds stored raw development outputs through consensus with these settings. It requires the ChampHLA-Consensus call, including abstentions, at all 708 loci (workflow commit `71f037d`; release tag under Data availability). Earlier workflow revisions broke exact ties in the
opposite lexicographic order and abstained on caller-declared homozygotes; both
are corrected in that commit.

### S11.3 Execution profiles and resources

Profiles are provided for local Docker (`docker`), Singularity (`singularity`),
generic Slurm clusters (`slurm`) and the CSC Roihu and Puhti systems (`roihu`,
`puhti`), plus `test` and `stub` profiles. Caller processes carry one of three
resource labels; failed tasks are retried with resources multiplied by the
attempt number, capped by `--max_cpus`, `--max_memory` and `--max_time`.
`-resume` reuses completed tasks when samples are added or a run is restarted.

| Label | CPUs | Memory | Time | Scales on retry |
| --- | ---: | ---: | ---: | --- |
| `process_low` | 2 | 8 GB | 2 h | No |
| `process_medium` | 8 | 32 GB | 8 h | Yes |
| `process_high` | 16 | 64 GB | 16 h | Yes |

### S11.4 Outputs

Each caller writes its native output to its own directory under `--outdir`.
When the consensus step is enabled, the `consensus/` directory contains the
files below, and `report/` contains an HTML run report.

| File | Contents |
| --- | --- |
| `aggregated_calls.tsv` | One row per sample, caller and gene: `sample`, `tool`, `modality`, `gene`, `allele1`, `allele2`, `is_callable` |
| `consensus_calls.tsv` | One row per sample and gene: `sample`, `gene`, `allele1`, `allele2`, `total_weight`, `agreeing_tools`, `contributing_tools`, `consensus_status`, `chosen_by`, `warnings` |
| `consensus_calls_clinical_warnings.tsv` | Loci flagged by the consensus step, with a warning code and description |
| `runtime_weights.json` | The caller weights applied in the run (all 1.0 under `--weighting equal`) |

## S12. Disagreement classes, cross-assay agreement, per-gene concordance and caller calibration

These analyses appeared in earlier drafts. They describe historical stored outputs, not the v3.5.0 rerun. `scripts/restored_analyses.py` computed them from exact-endpoint loci in the historical joined development table and wrote `artifacts/restored_analyses/` with an input-checksum manifest. They are not recomputed from rerun inputs. Their numbers are reconciled against the archived historical result
registry (`provenance/development_rerun_v350/`) and are reported as provenance
only. All four are post hoc and descriptive. S12.4 is also exploratory: its probabilities were calibrated on superseded 390-locus WES and 321-locus RNA-seq sets, including WGS rows, not current exact loci.

### S12.1 Disagreement among caller outputs

Using callable panel outputs alone, we assigned loci to classes: no callable caller; a single callable caller; unanimity among two or more callers; one-allele conflict, where every dissenting genotype shares one allele with the reported pair; or two-allele conflict, where at least one shares none.
In RNA-seq, one-allele conflicts are the pattern expected when one allele of a
heterozygous genotype is under-sampled. Intervals are exact Clopper–Pearson 95% intervals.

<!-- BEGIN GENERATED S12 DISAGREEMENT TABLE -->
| Assay | Class | Loci | Consensus correct | Concordance, % (95% CI) |
|---|---|---:|---:|---|
| WES | No callable caller | 0 | — | — |
| WES | Single callable caller | 0 | — | — |
| WES | Unanimous | 93 | 90 | 96.8 (90.9–99.3) |
| WES | One-allele conflict | 57 | 51 | 89.5 (78.5–96.0) |
| WES | Two-allele conflict | 3 | 2 | 66.7 (9.4–99.2) |
| RNA-seq | No callable caller | 0 | — | — |
| RNA-seq | Single callable caller | 3 | 3 | 100.0 (29.2–100.0) |
| RNA-seq | Unanimous | 102 | 98 | 96.1 (90.3–98.9) |
| RNA-seq | One-allele conflict | 13 | 12 | 92.3 (64.0–99.8) |
| RNA-seq | Two-allele conflict | 0 | — | — |
<!-- END GENERATED S12 DISAGREEMENT TABLE -->

In WES, all callable callers agreed at 93 of 153 loci, where ChampHLA-Consensus
was correct at 90 (96.8%). At the 57 loci where every dissenting caller differed
from the reported genotype at one allele, it was correct at 51 (89.5%), and 3
loci had a dissenting genotype sharing no allele with it. In RNA-seq, callers
agreed unanimously at 102 of 118 loci (98 correct; 96.1%), one-allele conflicts
occurred at 13 loci with 12 correct (92.3%), and 3 loci had a single callable
caller, all of which were correct.
[RESULT:DEV_DISCORDANCE_WES_UNANIMOUS]
[RESULT:DEV_DISCORDANCE_WES_ONE_ALLELE_CONFLICT]
[RESULT:DEV_DISCORDANCE_WES_TWO_ALLELE_CONFLICT]
[RESULT:DEV_DISCORDANCE_RNASEQ_UNANIMOUS]
[RESULT:DEV_DISCORDANCE_RNASEQ_ONE_ALLELE_CONFLICT]
[RESULT:DEV_DISCORDANCE_RNASEQ_SINGLE_CALLER]

### S12.2 Cross-assay agreement

Loci of the 50 subjects with exact reference typing in both assays. The pooled
vote is a post hoc plurality over the calls of both panels, with each caller
contributing one vote per assay and the same lexicographic tie-break; it is
shown for comparison only.

<!-- BEGIN GENERATED S12 CROSS-ASSAY TABLE -->
| Stratum | Loci | WES consensus correct | RNA-seq consensus correct | Pooled vote correct |
|---|---:|---:|---:|---:|
| All shared loci | 116 | 110 | 111 | 111 |
| WES and RNA-seq calls agree | 115 | 110 | 110 | 110 |
| WES and RNA-seq calls disagree | 1 | 0 | 1 | 1 |
| HLA-A | 38 | 37 | 37 | 37 |
| HLA-B | 39 | 37 | 37 | 37 |
| HLA-C | 39 | 36 | 37 | 37 |
<!-- END GENERATED S12 CROSS-ASSAY TABLE -->

The WES and RNA-seq consensus calls agreed at 115 of the 116 loci, of which 110
were correct. At the one locus where they disagreed, the RNA-seq call was
correct and the WES call was not. The pooled vote was correct at 111 of 116
loci, compared with 110 for WES and 111 for RNA-seq consensus alone. Both panels share callers, and the pooled rule was examined post hoc. Cross-assay agreement is therefore a consistency check, not independent truth; the pooled vote is not validated.
[RESULT:DEV_CROSS_ASSAY_ALL_WES]
[RESULT:DEV_CROSS_ASSAY_ALL_RNASEQ]
[RESULT:DEV_CROSS_ASSAY_ALL_POOLED]
[RESULT:DEV_CROSS_ASSAY_ASSAYS_AGREE_WES]
[RESULT:DEV_CROSS_ASSAY_ASSAYS_DISAGREE_WES]
[RESULT:DEV_CROSS_ASSAY_ASSAYS_DISAGREE_RNASEQ]

### S12.3 Per-gene caller concordance

Exact two-field concordance on the fixed denominator, so a no-call counts as
incorrect; cells give correct/loci (percent).

<!-- BEGIN GENERATED S12 PER-GENE TABLE -->
| Assay | Method | HLA-A | HLA-B | HLA-C | All |
|---|---|---:|---:|---:|---:|
| WES | HLA-HD | 40/50 (80.0) | 45/52 (86.5) | 41/51 (80.4) | 126/153 (82.4) |
| WES | OptiType | 48/50 (96.0) | 48/52 (92.3) | 44/51 (86.3) | 140/153 (91.5) |
| WES | POLYSOLVER | 47/50 (94.0) | 50/52 (96.2) | 46/51 (90.2) | 143/153 (93.5) |
| WES | SpecHLA | 46/50 (92.0) | 33/52 (63.5) | 44/51 (86.3) | 123/153 (80.4) |
| WES | T1K | 37/50 (74.0) | 43/52 (82.7) | 33/51 (64.7) | 113/153 (73.9) |
| WES | ChampHLA-Consensus | 48/50 (96.0) | 50/52 (96.2) | 45/51 (88.2) | 143/153 (93.5) |
| RNA-seq | arcasHLA | 35/38 (92.1) | 38/40 (95.0) | 36/40 (90.0) | 109/118 (92.4) |
| RNA-seq | HLA-HD | 36/38 (94.7) | 37/40 (92.5) | 37/40 (92.5) | 110/118 (93.2) |
| RNA-seq | OptiType | 36/38 (94.7) | 36/40 (90.0) | 37/40 (92.5) | 109/118 (92.4) |
| RNA-seq | T1K | 29/38 (76.3) | 31/40 (77.5) | 31/40 (77.5) | 91/118 (77.1) |
| RNA-seq | ChampHLA-Consensus | 37/38 (97.4) | 38/40 (95.0) | 38/40 (95.0) | 113/118 (95.8) |
<!-- END GENERATED S12 PER-GENE TABLE -->

In WES the least concordant caller was T1K for HLA-A and HLA-C and SpecHLA for
HLA-B, whereas in RNA-seq no caller led for every gene: HLA-HD and OptiType tied
for HLA-A and HLA-C, and arcasHLA led for HLA-B.
[RESULT:DEV_PER_GENE_WES_T1K_A]
[RESULT:DEV_PER_GENE_WES_SPECHLA_B]
[RESULT:DEV_PER_GENE_WES_T1K_C]
[RESULT:DEV_PER_GENE_RNASEQ_HLA_HD_A]
[RESULT:DEV_PER_GENE_RNASEQ_OPTITYPE_A]
[RESULT:DEV_PER_GENE_RNASEQ_ARCASHLA_B]
[RESULT:DEV_PER_GENE_RNASEQ_HLA_HD_C]
[RESULT:DEV_PER_GENE_RNASEQ_OPTITYPE_C]

### S12.4 Caller calibration (exploratory)

Out-of-fold calibrated probabilities from the recovered caller table were scored against exact correctness at current loci. The table reports scored loci over callable loci. We excluded six of 115 callable HLA-HD RNA-seq loci because their calibrated probabilities were not preserved. ECE is the
expected calibration error over five equal-width probability bins. POLYSOLVER
and SpecHLA report no confidence value. The calibration models were fitted
against earlier development labels, so these values describe agreement between
stated confidence and observed concordance on this resource only. The original caller table is checksum-verified but absent from this checkout. We retain the calibration table as a checksum-verified historical artifact; other S12 tables were computed from the historical joined locus table.

<!-- BEGIN GENERATED S12 CALIBRATION TABLE -->
| Assay | Caller | Scored/callable loci | Mean probability | Observed concordance | Brier score | ECE |
|---|---|---:|---:|---:|---:|---:|
| WES | HLA-HD | 153/153 | 0.796 | 0.824 | 0.150 | 0.082 |
| WES | OptiType | 153/153 | 0.922 | 0.915 | 0.079 | 0.007 |
| WES | POLYSOLVER | 0/153 | — | — | — | — |
| WES | SpecHLA | 0/153 | — | — | — | — |
| WES | T1K | 142/142 | 0.858 | 0.796 | 0.158 | 0.077 |
| RNA-seq | arcasHLA | 118/118 | 0.913 | 0.924 | 0.070 | 0.011 |
| RNA-seq | HLA-HD | 109/115 | 0.948 | 0.954 | 0.044 | 0.007 |
| RNA-seq | OptiType | 115/115 | 0.937 | 0.948 | 0.050 | 0.011 |
| RNA-seq | T1K | 105/105 | 0.880 | 0.867 | 0.117 | 0.014 |
<!-- END GENERATED S12 CALIBRATION TABLE -->

## S13. Background and design rationale

This section expands the background and design rationale summarized in the main text. It contains no results.

### S13.1 Why HLA typing is hard, and why callers disagree

The classical class I genes HLA-A, HLA-B and HLA-C present intracellular
peptides to CD8-positive T cells. The classical class II genes HLA-DR, HLA-DQ
and HLA-DP present extracellular peptides to CD4-positive helper T cells [1].
Together they are the main route by which adaptive immunity distinguishes self
from infected, transformed or transplanted cells.

This immune role explains the region's extreme polymorphism and the consequences of typing errors. In unrelated-donor haematopoietic cell transplantation, matching
is counted per allele: a donor matched at both alleles of HLA-A, -B, -C and
-DRB1 is an 8/8 match, and adding HLA-DQB1 gives a 10/10 match [2, 3].

Three properties of the MHC make short-read typing difficult.
- **Diversity.** The allele space is large and keeps growing with every
  IPD-IMGT/HLA release [8]. Reads from an allele that is poorly represented in
  a single linear reference are lost or misplaced before any caller sees them.
- **Paralogy.** The region also contains pseudogenes, the class I
  chain-related genes MICA and MICB, and non-classical HLA-like loci. Reads
  from a polymorphic site of a classical gene can therefore align as well, or
  better, to a paralogous sequence.
- **Expression.** RNA-seq samples expressed copies rather than genomic ones.
  When one allele of a heterozygote is weakly expressed, a caller can
  under-represent or miss it.

No single alignment strategy, reference space or scoring model handles all
three equally well across genes, assays and populations. That is why callers
built on different evidence disagree, and why their rankings change between
assays.

### S13.2 Caller choice as a selection problem

For a given assay, users must choose a caller before they can assess its accuracy on their data. Published rankings
depend on the assay, the gene and the dataset, so the best caller for a new
cohort is usually unknown in advance. Combining callers without fitted parameters avoids choosing a single caller.

Fitted integration policies bring costs that an equal-weight vote does not:
- parameters that must be estimated;
- a training resource that must resemble the target data;
- a decision path that a user cannot easily audit.

With one labelled development resource, any apparent gain of a fitted policy
cannot be separated from fitting to that resource. We therefore report fitted policies only as exploratory comparators (Supplementary S7).

### S13.3 Harmonization is not a neutral preprocessing step

A vote aggregates its panel. A harmonization convention shared by several panel members is concentrated by voting.
Completing a single reported allele into a homozygous pair is the clearest
example. The completion is correct when the caller's own format declares
homozygosity. It is wrong when a missing second allele marks a failed or
partial call. Whether the convention helps or harms depends on the input, not
on the voting rule.

Harmonization deserves the same scrutiny as the integration rule. This benchmark therefore completes single
alleles only where the caller declares homozygosity and reports the
abstain-all alternative beside it (Supplementary S2).

### S13.4 Why "no significant difference" is not equivalence

A criterion phrased as the absence of a significant improvement passes
automatically wherever a comparison is underpowered. In some comparisons, too few subjects had nonzero score differences for the sign-flip test to reach significance at any effect size (detectability table in Supplementary S3; power table in Supplementary S7). The development
results therefore support "could not be distinguished from" and never
"equivalent to". Equivalence would need a pre-specified margin and a test
designed for it.

### S13.5 Deployed tools, database vintage and nomenclature

Callers were evaluated as deployed, each with its own bundled IPD-IMGT/HLA
release (Table 1 and Supplementary S6). This is how the tools are distributed,
but it confounds the comparison. Database vintage can contribute to apparent caller disagreement; a caller cannot call an allele absent from its bundled database. The effect
is not symmetric across callers. Rankings therefore describe deployed tools, not algorithms. Rebuilding all callers against one database release would be a different study.

For the same reason, every step that compares alleles uses declared
nomenclature resources [8, 40]:
- truth normalization, call normalization and the G-group and P-group sensitivity mappings each use a checksummed release;
- concordance is scored on the unordered genotype, not on two independent
  alleles, so partial credit cannot hide an ambiguous or failed call;
- set-valued (ambiguity-compatible) endpoints are reported beside the exact
  endpoint rather than replacing it.

### S13.6 Workflow engineering as part of the method

Reproducibility contributes to the method.
- Each caller runs as its own containerized process with a checksummed image.
- Inputs are defined by manifests.
- The release, the panel and the consensus rule are declared in versioned
  configuration (Supplementary S10 and S11).

Other groups can run the same release on the same public inputs or a new cohort without changing workflow code. The documented rerun
manifests record what was executed for every development sample.

### S13.7 Scope and outlook

HLA allele frequencies differ across ancestry groups, and callers developed or
validated mainly on European panels may behave differently elsewhere. The development resource is too small for population-stratified inference. We report pooled results and interpret population differences in reference retention as properties of the reference, rather than callers (Supplementary S1).

Class II typing matters for transplantation. The workflow already exposes
HLA-DRB1, HLA-DQB1 and HLA-DQA1 for voting, but truth-backed class II
evaluation awaits suitable reference typing. The same applies to:
- higher-field typing;
- re-extracted whole-genome inputs;
- long-read and pangenome-graph callers;
- downstream uses such as neoantigen prediction.

## S14. Interpreting the retrospective benchmark

### Why the development results are exploratory

The analysis plan changed after development results had been seen.
Each change is recorded in a dated decision file in the paper repository, and Supplementary S7 tabulates the direction and size of every change.

An analysis plan specified on 31 August 2026, before the planned comparison of predictions with reference genotypes, named a two-thirds-guarded champion–challenger rule as the primary method, corrected for multiplicity across WGS, WES and RNA-seq together, and required the primary method to outperform its comparators.
This was not the analysts' first sight of truth: an earlier analysis had already joined truth to these caller outputs to fit the champions and weights.
On the current scoring definition the previous primary method did not outperform: it scored 141/153 against the vote's 143/153 in WES (Holm *p*=1.0) and tied the vote at 113/118 in RNA-seq.

The equal-weight plurality vote was then made primary, with multiplicity corrected within each assay and invalid WGS excluded (8 September; documented 18 September).
Single-allele handling was revised three times, ending with caller-declared homozygotes completed (18 September to 8 October).
After a structured review, the reference parser was changed to exclude unresolved reference genotypes and predictions were finalized before reference genotypes were selected for evaluation (28 September).
We then withheld the RNA-seq input that failed identity checks, refitted the nested-CV comparator and made the exact sign-flip test govern significance instead of the cluster-*t* test (8–9 October). The significant comparisons did not change.
The full rerun followed (13–25 October). A corrected T1K parser was released in workflow release 3.5.0, and every development caller was re-run with it. The collector was corrected to complete caller-declared homozygotes before activation; the revised results were checked before manuscript revision.
The arcasHLA deployment defect found afterwards was reported as it stands rather than corrected.
These safeguards document the history but cannot undo prior exposure to development truth. None of the development results is confirmatory.
A separate extension cohort with no overlapping subjects was specified with its analysis plan before any comparison with reference genotypes; an amendment specifying release 3.5.0, the analysis code and the input manifest was documented on 26 October, and the roster is being processed, with the one-time comparison with reference genotypes deferred until the documented plan is publicly deposited.
The NCI-60 application is being regenerated under a separate decision documented the same day (Supplementary S9.6).

### Applying the method to a new dataset

Use the same assay-specific caller panel, allele normalization and missing-call rules described in Methods and Supplementary S11. Retain no-calls when reporting concordance, and report callability separately. Inspect tied or sparsely supported genotypes before downstream use. The benchmark does not validate consensus genotyping for clinical decisions; laboratory confirmation and independent evaluation are needed for that purpose.
