# Abstract options (JP-007) — 5 November 2026

Drafted for the author's decision. None of this is in the manuscript. The headline claim is the author's.

## Option A: counts (185 words)

HLA class I typing from short reads depends on the caller, assay and reference database; voting is proposed when the best caller is unknown. We evaluated ChampHLA-Consensus, an equal-weight plurality vote over five exome and four RNA-seq callers, made primary after a fitted rule failed to outperform it on these data. In 1000 Genomes and Geuvadis subjects with one recorded 2014 reference genotype, the vote agreed with it at 143/153 exome loci (63 subjects) and 113/118 RNA-seq loci (51 subjects), one locus above the strongest caller in each assay. They differed at three exome loci and one RNA-seq locus, too few to compare. After multiplicity correction the vote exceeded HLA-HD and T1K in exome data and T1K in RNA-seq; a deployment defect affected one RNA-seq caller. All 15 vote errors, at 10 loci, fell where a re-typing of the same exomes reports the 2014 type as incorrect; laboratory typing, checked post hoc and only there, gives the vote's type at nine. Retained loci came mainly from two populations. These development results establish neither equivalence nor clinical validity; testing on unseen subjects is incomplete.

## Option A-plus: counts and the corrected-value result (200 words)

HLA class I typing from short reads depends on the caller, assay and reference database; voting is proposed when the best caller is unknown. We evaluated ChampHLA-Consensus, an equal-weight plurality vote over five exome and four RNA-seq callers, made primary after a fitted rule failed to outperform it on these data. In 1000 Genomes and Geuvadis subjects with one recorded 2014 reference genotype, the vote agreed with it at 143/153 exome loci (63 subjects) and 113/118 RNA-seq loci (51 subjects), one locus above the strongest caller in each assay. They differed at three exome loci and one RNA-seq locus, too few to compare. After multiplicity correction the vote exceeded HLA-HD and T1K in exome data and T1K in RNA-seq; a deployment defect affected one RNA-seq caller. All 15 vote errors, at 10 loci, fell where a re-typing of the same exomes reports the 2014 type as incorrect; laboratory typing, checked post hoc and only there, gives the vote's type at nine. With corrected values there, HLA-HD scored 118/118 and the vote 117/118 in RNA-seq. Retained loci came mainly from two populations. These development results establish neither equivalence nor clinical validity; testing on unseen subjects is incomplete.

## Option B: no performance counts, route flag unchanged (173 words)

HLA class I typing from short reads depends on the caller, assay and reference database; voting is proposed when the best caller is unknown. We evaluated ChampHLA-Consensus, an equal-weight plurality vote over five exome and four RNA-seq callers, made primary after a fitted rule failed to outperform it on these data. In 1000 Genomes and Geuvadis subjects with one recorded 2014 reference genotype, the vote agreed with it one locus more often than the strongest caller in each assay. They differed at three exome loci and one RNA-seq locus, too few to compare. After multiplicity correction the vote exceeded HLA-HD and T1K in exome data and T1K in RNA-seq; a deployment defect affected one RNA-seq caller. All vote errors fell where a re-typing of the same exomes reports the 2014 type as incorrect; laboratory typing, checked post hoc and only there, gives the vote's type at nine of the ten loci. Retained loci came mainly from two populations. These development results establish neither equivalence nor clinical validity; testing on unseen subjects is incomplete.

## What each option needs

- A and A-plus report counts, so `decisions/publication_route.json` must set `abstract_numeric_performance_allowed` to true. That needs a signed record. The two vote counts already have `abstract_allowed` set in the registry, so no registry change follows.
- A-plus also reports the post hoc 118/118 and 117/118, which are registered rows but not marked for the abstract. The abstract cites no result tags, so the audit does not block this.
- B keeps the flag as it is. Its counts of differing loci, nine of ten and 'one locus' are in words and pass the audit's numeric check, but readers still cannot get the headline concordance from the abstract, which is what JP-007 objected to.

## Checks

Word counts use the rule in `tests/test_scientific_reports_manuscript.py` (limit 200). Each option was run through the claim audit's abstract rules on a scratch copy, with no abstract failure. Numbers were checked against `artifacts/development_corrected/per_locus_results.tsv`, the flagged-locus artifact and the registry: 63 and 51 subjects; OptiType 142/153; HLA-HD and OptiType 112/118; three and one differing loci; 125 of 153 and 105 of 118 retained loci from CEU and YRI.
