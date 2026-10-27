from __future__ import annotations

GENES = ("A", "B", "C")
MODALITIES = ("wgs", "wes", "rnaseq")
PANELS = {
    "wgs": ("HLA-HD", "Kourami", "OptiType", "SpecHLA", "T1K"),
    "wes": ("HLA-HD", "OptiType", "POLYSOLVER", "SpecHLA", "T1K"),
    "rnaseq": ("ArcasHLA", "HLA-HD", "OptiType", "T1K"),
}

METHOD_BASELINE = "SimpleTwoThirdsConsensus"
METHOD_PLURALITY = "SimplePluralityLex"
METHOD_STRICT_MAJORITY = "SimpleStrictMajority"
METHOD_RAW_CC = "ChampionChallenger"
METHOD_GUARDED_CC = "TwoThirdsGuardedCC"

# "MajorityVote" is the historical name for the plurality rule and is emitted
# alongside it. The two are the same rule -- identical at every locus, in both
# correctness and emitted pair -- so the alias must never enter a comparator
# family, where it would compare the primary method to itself and inflate the
# Holm correction for every other comparator in that family.
METHOD_PLURALITY_ALIAS = "MajorityVote"
REFERENCE_ALIASES = frozenset({METHOD_PLURALITY, METHOD_PLURALITY_ALIAS})
