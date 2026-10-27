# Citation verification record

Regenerated 2026-10-09 for pre-submission review finding PSR-052, from the current
reference list in `manuscripts/benchmark/manuscript.md`. The earlier version of this
file listed references that are no longer cited (Mishima 2019, Chin 2020) and
omitted those added since.

**How each entry was checked.** Each bibliographic record was resolved by DOI against
Crossref, or against Europe PMC where noted, on 2026-10-09. A claim was checked
against the abstract or full text wherever the manuscript attributes a specific
finding to a source. Holm 1979 has no DOI.

**BMC Vancouver format (2026-10-10).** The lists were converted from author-year to
numbered Vancouver style for BMC Bioinformatics. Author lists (first six, then
"et al"), titles, volumes and pages come from the Crossref records of each DOI,
and NLM journal abbreviations are used. Where Crossref has no volume (Bauer 2018,
Robinson 2020), the issue values verified above are kept. Cited years are print
years: Crossref gives the earlier online year for Bauer, Kiyotani, Orenbuch and
Robinson. Web resources that were cited inline (the HLA-HD documentation, the
arcasHLA v0.2.0 source, data URLs and accessions, and the two project
repositories) are now numbered references with access dates. The repositories
receive their dates at public release. The supplement has its own four-entry
list.

`tests/test_reference_facts.py` checks:
- every journal entry except Holm 1979 carries a DOI, and every web resource has a URL;
- in both documents, references are numbered in order of first citation, every
  entry is cited, and no author-year citation remains;
- the stated 3.65.0 allele count matches the pinned allele list.

## Corrections made during verification

| Reference as cited before | Problem | Now |
|---|---|---|
| Petersdorf *et al.* 2007, *Immunol Rev* 214:229–244 | Does not exist. | Lee SJ *et al.* 2007, *Blood* 110:4576 (8/8 matching, mismatch mortality) and Petersdorf 2007, *Best Pract Res Clin Haematol* 20:155 (GVHD and graft failure). The unsupported "preferably 10/10" clause was removed: Lee 2007 found no DQ effect on survival. |
| Claeys *et al.* 2023, *BMC Genomics* 24:292, "…HLA genotypes…" | Wrong title and article number. | "…MHC class I and class II genotypes…", 24:247. |
| Lee, H. *et al.* 2021 | Wrong first author. | Lee, M. *et al.* 2021. |
| Robinson 2020 for ">45,000 alleles" | The source states over 25,000. | The count of the pinned 3.65.0 allele list (46,652), with Robinson 2020 cited for the database. |
| Kiyotani 2017 for assay-dependent rankings | Exome-only study. | Cited only for platform-specific caller errors; Claeys 2023 for rankings. |
| Reinhold 2019 (NCI-60 typing) | Does not exist (PSR-004). | Adams 2005. |

## Claims checked against the source

| Claim in the manuscript | Source | What the source says |
|---|---|---|
| Reference typing: exon 2–3 Sanger SBT, IMGT/HLA 2.26.0, earlier HapMap/CEPH typings reused, ambiguities retained | Gourraud 2014 (PMC4079705) | Stated in Methods. |
| 221 of 263 samples typed in more than one study (84%) agreed | Bauer 2018 (PMC6019030) | Quoted. |
| Re-typing of 992 exomes; 105 results that disagreed with the published types confirmed by resequencing | Abi-Rached 2018 (PMC6203392) | Quoted. The paper does not call these "errors". |
| OptiType β chosen by nested CV on 253 1000 Genomes exome runs; POLYSOLVER, arcasHLA, T1K and SpecHLA evaluated on 1000 Genomes/Geuvadis samples | Szolek 2014, Shukla 2015, Orenbuch 2020, Song 2023, Wang 2023 (full texts) | Confirmed. For HLA-HD (Kawaguchi 2017) the evaluation data could not be verified from an open source, and the manuscript says so. |
| Majority vote on 1000 Genomes WES and Geuvadis, ties to the best tool, 99.0% vs 98.0% for WES class I | Claeys 2023 (PMC10170851) | Quoted. |
| Accept a genotype when ≥6 of 8 tools agree | Lee M 2021 (abstract) | Confirmed. |
| Top-3 ensemble beats any single tool, on TCGA | Li 2021 (abstract) | Confirmed. |
| Ensemble prediction can improve accuracy | Larjo 2017 (abstract) | Confirmed. |
| Cluster-robust t is anti-conservative with few clusters | Cameron and Miller 2015 | Crossref record confirmed. |

## Still to check against full text before submission

- Mallal 2008 and Chung 2004: the pharmacogenomic examples.
- Matzaraki 2017 and Schumacher and Schreiber 2015: the introductory motivation.
- Trowsdale and Knight 2013: the general MHC complexity statement.
- Aguiar 2019 and Lappalainen 2013: where cited for Geuvadis data and HLA expression.
