"""Algorithmic families, and the correlation-aware challenger diversity gate.

Callers within a family share an alignment strategy and reference representation, so
they tend to fail on the same alleles. A raw count of supporting callers therefore
overstates how much independent evidence backs a challenger: three alignment-based
callers agreeing is weaker support than one alignment and one assembly-graph caller
agreeing.

The gate replaces the count of supporting callers with a count of distinct families.
It applies to Champion-Challenger, which is a retained ablation; the primary method
is unweighted plurality and is unaffected.

Grouping mirrors conf/tool_families.yaml in the pipeline repository.
"""
from __future__ import annotations

FAMILIES: dict[str, str] = {
    # alignment to IPD-IMGT/HLA, then optimisation or Bayesian inference
    "optitype": "alignment",
    "hla-hd": "alignment",
    "hlahd": "alignment",
    "polysolver": "alignment",
    # assembly, graph, or targeted exon reconstruction
    "kourami": "assembly_graph",
    "spechla": "assembly_graph",
    # allele-index alignment followed by weighted EM-style inference
    "t1k": "alignment_em",
    # k-mer and pseudo-alignment
    "arcashla": "kmer",
    "seq2hla": "kmer",
}

DEFAULT_MIN_SUPPORTING_FAMILIES = 2


def family_of(caller: str) -> str:
    """Family for a caller.

    A caller absent from the map gets its own singleton family. Failing open matters:
    an unknown caller must never be silently merged with another, which would make the
    gate weaker than it appears.
    """
    key = caller.strip().lower()
    return FAMILIES.get(key, f"singleton:{key}")


def supporting_families(callers: list[str] | set[str] | str) -> set[str]:
    """Distinct families represented among the supporting callers."""
    if isinstance(callers, str):
        callers = [c for c in callers.replace(";", ",").split(",") if c.strip()]
    return {family_of(caller) for caller in callers if caller.strip()}


def passes_family_gate(callers: list[str] | set[str] | str,
                       minimum: int = DEFAULT_MIN_SUPPORTING_FAMILIES) -> bool:
    """Whether supporting callers span enough distinct families to allow an override."""
    return len(supporting_families(callers)) >= minimum
