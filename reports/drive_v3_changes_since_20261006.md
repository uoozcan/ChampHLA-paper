## What changed since the 6 October version (v2)

This page is not part of the manuscript. It summarises the changes between
PanelHLA_Manuscript_v2.docx (6 October) and this version, which was generated on
12 October 2026 from the manuscript sources. Old values are taken from v2; new values
come from the current manuscript and its results registry.

### Headline results

- **WES: unchanged.** 143/153 loci (93.5%), tied with POLYSOLVER, the strongest WES
  caller.
- **RNA-seq: 110/120 (91.7%) became 113/118 (95.8%).** There are two reasons:
  - A single reported allele is now completed into a homozygous genotype when the
    caller's own output format declares it, as HLA-HD and arcasHLA do. Scoring every
    single allele as missing is reported alongside, as a sensitivity analysis.
  - One RNA-seq input, labelled NA07000, failed a sample-identity check and was
    withheld. With it, the result would be 113/120.
- **The strongest RNA-seq caller is now HLA-HD (110/118), not OptiType.**
- **Neither comparison establishes equivalence.** The paired 95% intervals are −2.59 to
  2.59 points for WES and −4.41 to 9.49 points for RNA-seq.
- **The fitted best-single-caller policy was refitted under the current rules.** It now
  scores 106/118 on RNA-seq, not significantly different from the vote. In v2 it scored
  99/120 and was nominally significant. No fitted policy beats the vote.
- **Consensus errors are now 10 in WES and 5 in RNA-seq** (v2: 10 and 10). A second
  typing of the same samples suggests that most of them may be errors in the 2014
  reference typing rather than caller errors. This reading is post hoc (Results, "Caller
  error dependence and oracle headroom").

### Methods and statistics

- An exact subject-level sign-flip test now decides significance. The cluster-*t* test
  is descriptive only.
- A new "Protocol history" paragraph lists every change made after results had been
  seen.
- **Reference typing:** the limits of the reference typing are described (exon 2–3
  typing against a 2009 allele release). The text also discloses that most callers were
  developed or evaluated on the same 1000 Genomes samples.
- **Ties:** the tie-break rule is stated exactly, with a reverse tie-break sensitivity
  analysis.

### New analyses, mostly in the supplement

- detectability: how large a difference these comparisons could detect;
- second-typing adjudication of every consensus error;
- which loci the exact endpoint keeps (mostly CEU and YRI) and how callers rank on the
  excluded loci;
- caller-error correlations with intervals;
- alternative multiplicity families;
- a re-run of subject HG00096 with the current workflow, which reproduced 11 of 15
  stored WES calls and 11 of 12 RNA-seq calls.

### Withdrawn or corrected

- The NCI-60 cell-line estimates were withdrawn from the main text. The analysis is
  kept only as legacy material (Supplementary S9.6).
- A non-existent reference, the NCI-60 typing source and the Claeys *et al.* citation
  were corrected, and every reference was checked against its DOI.
- The BB7.2 attribution sentence was removed.

### Format for BMC Bioinformatics

- **Structure:**
  - The abstract is structured.
  - The main text follows Background, Methods, Results, Discussion and Conclusions,
    with Limitations inside the Discussion.
  - There is a list of abbreviations and a Declarations section with BMC's seven
    required headings.
  - References are numbered (Vancouver style).
- **Length:** the main text was shortened from about 9,200 to about 7,300 words. The
  detail moved to the supplement, which is Additional file 1.
- **Name:** the project name was restored to ChampHLA. The software repository keeps
  the name PanelHLA.

### Software

Three workflow releases since v2:
- **3.3.0** implements the paper's rule under `-profile paper`.
- **3.4.0** recovers reads that were lost on HLA alternate contigs in WES alignments.
- **3.4.1** checks every caller container image against its recorded checksum before
  a run starts.

### Still needed from co-authors

These fields are highlighted or marked PROVISIONAL in the text:
- authors, affiliations, ORCIDs, contributions and corresponding author;
- funding and the funder's role;
- competing interests;
- acknowledgements, including whether CSC may be named;
- ethics wording for the public data and for the FIMM and VenEx cohorts;
- approval of the proposed AI-use statement and the "Consent for publication" wording.
