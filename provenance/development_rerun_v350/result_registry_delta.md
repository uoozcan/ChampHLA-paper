# ChampHLA result-registry delta

Old rows: 631; new rows: 630.

| Unchanged | Changed | Added | Removed |
|---:|---:|---:|---:|
| 209 | 421 | 0 | 1 |

## Author-approval gate

STOP: author approval is required before prose is revised.

- fitted-policy conclusion changed
- fitted-policy ranking changed
- headline direction changed: DEV_PAIRED_RNASEQ_METACONSENSUS
- headline direction changed: DEV_PAIRED_WES_BESTSINGLETOOL_NESTEDCV
- headline direction changed: DEV_PAIRED_WES_CALLER_POLYSOLVER
- headline direction changed: DEV_PAIRED_WES_METACONSENSUS
- significance interpretation changed (adjusted_p): DEV_AMBIGUITY_PAIRED_RNASEQ_BESTSINGLETOOL_NESTEDCV
- significance interpretation changed (adjusted_p): DEV_AMBIGUITY_PAIRED_RNASEQ_FAMILYGATEDCC
- significance interpretation changed (adjusted_p): DEV_AMBIGUITY_PAIRED_WES_CALLER_POLYSOLVER
- significance interpretation changed (adjusted_p): DEV_PAIRED_RNASEQ_CALLER_ARCASHLA
- significance interpretation changed (adjusted_p): DEV_PAIRED_WES_CALLER_SPECHLA
- significance interpretation changed (adjusted_p): DEV_SINGLETON_ABSTAIN_PAIRED_RNASEQ_SIMPLESTRICTMAJORITY
- significance interpretation changed (adjusted_p): DEV_SINGLETON_ABSTAIN_PAIRED_RNASEQ_SIMPLETWOTHIRDSCONSENSUS
- significance interpretation changed (adjusted_p): DEV_SINGLETON_ABSTAIN_PAIRED_WES_CALLER_SPECHLA
- significance interpretation changed (sensitivity_adjusted_p): DEV_PAIRED_RNASEQ_CALLER_ARCASHLA
- significance interpretation changed (sensitivity_adjusted_p): DEV_PAIRED_RNASEQ_SIMPLESTRICTMAJORITY
- significance interpretation changed (sensitivity_adjusted_p): DEV_PAIRED_RNASEQ_SIMPLETWOTHIRDSCONSENSUS
- significance interpretation changed (sensitivity_adjusted_p): DEV_PAIRED_WES_CALLER_SPECHLA
- significance interpretation changed (sensitivity_adjusted_p): DEV_PAIRED_WES_SIMPLETWOTHIRDSCONSENSUS
- significance interpretation changed (sensitivity_adjusted_p): DEV_SINGLETON_ABSTAIN_PAIRED_RNASEQ_FAMILYGATEDCC
- significance interpretation changed (sensitivity_adjusted_p): DEV_SINGLETON_ABSTAIN_PAIRED_RNASEQ_SIMPLESTRICTMAJORITY
- significance interpretation changed (sensitivity_adjusted_p): DEV_SINGLETON_ABSTAIN_PAIRED_RNASEQ_SIMPLETWOTHIRDSCONSENSUS
- significance interpretation changed (sensitivity_adjusted_p): DEV_SINGLETON_ABSTAIN_PAIRED_WES_CALLER_SPECHLA
- significance interpretation changed (sensitivity_adjusted_p): DEV_SINGLETON_ABSTAIN_PAIRED_WES_SIMPLETWOTHIRDSCONSENSUS
- strongest-caller identity changed

## Ranking checks

- Old strongest callers: `{"rnaseq": ["Caller:HLA-HD"], "wes": ["Caller:POLYSOLVER", "Caller:POLYSOLVER"]}`
- New strongest callers: `{"rnaseq": ["Caller:HLA-HD", "Caller:OptiType", "Caller:OptiType"], "wes": ["Caller:OptiType", "Caller:OptiType"]}`
- Old best fitted: `{"rnaseq": ["ChampionChallenger", "MVFlooredCC", "MVFlooredCC", "TwoThirdsGuardedCC"], "wes": ["BestSingleTool_nestedCV", "BestSingleTool_nestedCV", "MVFlooredCC", "MVFlooredCC", "MetaConsensus", "MetaConsensus"]}`
- New best fitted: `{"rnaseq": ["ChampionChallenger", "MVFlooredCC", "MetaConsensus", "MetaConsensus", "TwoThirdsGuardedCC"], "wes": ["MVFlooredCC", "MVFlooredCC", "MetaConsensus"]}`

The TSV contains one row for every identifier in either registry, including denominators, callability, estimates, intervals, tests and artifact hashes.
