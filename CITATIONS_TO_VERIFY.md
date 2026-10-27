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

## Claims checked — v7 follow-up, 27 October 2026

The following inventory covers every occurrence of these seven references in the current main text and supplement, outside the reference list. The exact cited sentences are retained below. Source quotations are deliberately short. Abstract support is distinguished from a full-text check; no inaccessible source is marked verified. No manuscript sentence or reference entry was changed for this check.

| Cited claim and location | Source and accessible evidence | Assessment |
|---|---|---|
| Main Introduction: HLA on chromosome 6p21.3 is among the most polymorphic regions; Supplementary S13.1: class I and II antigen presentation to T cells | Trowsdale & Knight (2013), [full text, MHC organization and polymorphism](https://pmc.ncbi.nlm.nih.gov/articles/PMC4426292/). “Remarkably high levels of polymorphism are seen, notably in classical HLA genes”. The review describes the chromosomal organization and antigen presentation by class I and II. | Full text checked; supports the general statements. |
| Main Introduction: HLA-B\*57:01 predicts abacavir hypersensitivity | Mallal et al. (2008), [primary NEJM article, article-text reproduction, Discussion](https://www.natap.org/2008/CROI/croi_56.htm), [DOI](https://doi.org/10.1056/NEJMoa0706135). “necessary, but not sufficient by itself”; screening can “identify patients at greatest risk”. | Full-text Discussion checked. Supports prediction of susceptibility, not certainty of reaction. Suggested clarification for the authors only: “HLA-B\*57:01 identifies increased risk of abacavir hypersensitivity”. Prose left unchanged. |
| Main Introduction: HLA-B\*15:02 association with carbamazepine-induced Stevens–Johnson syndrome in Han Chinese patients | Chung et al. (2004), [publisher abstract](https://www.nature.com/articles/428486a): “strong association in Han Chinese”, with Stevens–Johnson syndrome induced by carbamazepine. The publisher page identifies the rest as subscription content; the complete article was not available. | **unverified: no full-text access**. The abstract supports the stated association. Obtain the full article for the requested full-text sign-off; no prose change proposed. |
| Main Introduction: HLA genotype constrains tumour neoantigen presentation and typing errors propagate into vaccine and T-cell receptor therapy design | Schumacher & Schreiber (2015), [PubMed abstract and bibliographic record](https://pubmed.ncbi.nlm.nih.gov/25838375/): “development of novel therapeutic approaches that selectively enhance T cell reactivity against this class of antigens”. Publisher full text and a located reproduction were not readable through the available routes. | **unverified: no full-text access**. The abstract supports neoantigen-directed therapy, but does not directly establish the claimed consequences of typing errors. Proposed author revision, not applied: “HLA genotype constrains tumour neoantigen presentation, making correct typing relevant to neoantigen-directed therapy design.” Verify the source or add direct primary evidence before adopting this wording. |
| Main Introduction: the MHC carries many of the strongest autoimmune-disease associations | Matzaraki et al. (2017), [full text, Role of MHC variants in human diseases](https://link.springer.com/article/10.1186/s13059-017-1207-1): “they remain the strongest risk factors for autoimmune diseases”. | Full text checked; supports the statement. |
| Main Introduction: expression estimation is sensitive to polymorphism-aware mapping | Aguiar et al. (2019), [full text, Introduction and simulation analyses](https://journals.plos.org/plosgenetics/article?id=10.1371/journal.pgen.1008091): “many short reads originating from genes with extreme polymorphism fail to map to the reference genome”. | Full text checked; supports the mapping-bias statement. |
| Main Methods, Study design and data: Geuvadis RNA-seq source | Lappalainen et al. (2013), [PMC summary and bibliographic record](https://pmc.ncbi.nlm.nih.gov/articles/PMC3918453/): “mRNA and miRNA from lymphoblastoid cell lines of 462 individuals from the 1000 Genomes Project”. The complete body could not be retrieved from PMC, Europe PMC or the publisher through the available routes. | **unverified: no full-text access**. The source summary supports the dataset attribution; a full-text sign-off remains open. |

### Exact cited sentences in v7

- `manuscript.md:15`: The human leukocyte antigen (HLA) genes of the major histocompatibility complex (MHC) on chromosome 6p21.3 form one of the most polymorphic regions of the human genome [1].
- `manuscript.md:21`: HLA-B\*57:01 predicts abacavir hypersensitivity [4], and HLA-B\*15:02 is associated with carbamazepine-induced Stevens–Johnson syndrome in Han Chinese patients [5].
- `manuscript.md:22`: HLA genotype determines which tumour neoantigens can be presented, so typing errors propagate into vaccine and T-cell receptor therapy design [6]. The region also carries many of the strongest known associations with autoimmune disease [7].
- `manuscript.md:27`: RNA-seq samples expressed rather than genomic copies, so a weakly expressed allele can be missed. Expression estimation is itself sensitive to polymorphism-aware mapping [10].
- `manuscript.md:63`: We ran callers on 1000 Genomes WES and Geuvadis RNA-seq data [20, 31] with ChampHLA workflow release 3.5.0 in October 2026. This retrospective benchmark evaluates the caller outputs produced by that run. The prediction tables contain no reference genotypes; reference typing is used only for evaluation.
- `supplementary.md:1674`: and HLA-DP present extracellular peptides to CD4-positive helper T cells [1].

### Remaining full-text checks

- Chung 2004; Schumacher & Schreiber 2015; Lappalainen 2013: **unverified: no full-text access**. Ask an author with lawful full-text access to complete these checks; a Scite subscription is not required.
- Treat the typing-error/therapy-design clause attributed to Schumacher & Schreiber as unverified, with the proposed narrower wording above. No reference or prose change was made.
- The earlier Vancouver/BMC formatting note is historical. V7 targets Scientific Reports and uses one sequential main reference list shared with the supplement; the existing reference tests enforce that scheme.
