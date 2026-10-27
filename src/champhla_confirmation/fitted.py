"""Fold-local refits of the historical MV-floor and MetaConsensus comparators.

This module is the paper-boundary port of the recovered implementations.  Caller
rows are accepted in the v3.5.0 normalized per-locus schema.  Truth is supplied as
a separate mapping and is used only inside training folds; scoring a held-out fold
uses caller rows plus the fitted policy/model.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from collections import defaultdict

import numpy as np

from .consensus import build_consensus
from .families import family_of
from .io import canonical_pair, is_callable, reject_truth_columns
from .panels import METHOD_PLURALITY, PANELS
from .raw_cc import predict_raw_cc

GENES = ("A", "B", "C")
MV_FLOOR_METHOD = "MVFlooredCC"
META_METHOD = "MetaConsensus"
L2_GRID = (0.01, 0.1, 1.0, 10.0)

NUMERIC_FEATURES = (
    "equal_support_fraction",
    "equal_support_margin",
    "vote_entropy",
    "weighted_support_fraction",
    "weighted_support_margin",
    "supporting_tool_fraction",
    "supporting_family_fraction",
    "mean_support_confidence",
    "max_support_confidence",
    "min_support_confidence",
    "confidence_coverage",
    "callable_tool_fraction",
    "missing_tool_fraction",
    "is_equal_vote_winner",
    "is_weighted_vote_winner",
    "is_homozygous",
    "is_ciwd_plausible",
    "has_ambiguity_notation",
)


def _locus(row: dict[str, str]) -> tuple[str, str, str, str]:
    return (row.get("cohort", ""), row["subject"], row["modality"], row["gene"])


def _pair(row: dict[str, str]) -> tuple[str, str] | None:
    if not is_callable(row):
        return None
    return canonical_pair(row["allele1"], row["allele2"], row["gene"])


def agreement_bucket(vote: dict[str, str]) -> str:
    """Recovered MV-floor agreement strata, derived without truth."""
    try:
        agreeing = int(vote.get("top_support", vote.get("agreeing_tools", 0)) or 0)
        contributing = int(vote.get("callable_tools", vote.get("contributing_tools", 0)) or 0)
    except (TypeError, ValueError):
        return "unknown"
    if contributing <= 1:
        return "single_tool"
    if agreeing == contributing:
        return "unanimous"
    if agreeing > contributing / 2:
        return "clear_majority"
    return "split"


def _exact_mcnemar_p(wins: int, losses: int) -> float:
    discordant = wins + losses
    if not discordant:
        return 1.0
    tail = sum(math.comb(discordant, i) for i in range(min(wins, losses) + 1))
    return min(1.0, 2.0 * tail / (2 ** discordant))


def learn_mv_floor_routing(
    training_vote: list[dict[str, str]],
    training_cc: list[dict[str, str]],
    truth: dict[tuple[str, str, str, str], tuple[str, str]],
    *,
    min_gain: float = 0.0,
    alpha: float = 0.05,
    min_loci: int = 20,
) -> dict[str, dict[str, object]]:
    """Learn the recovered conservative stratum router on training loci only."""
    vote = {_locus(row): row for row in training_vote}
    cc = {_locus(row): row for row in training_cc}
    grouped: dict[str, list[tuple[int, int]]] = defaultdict(list)
    for key in sorted(set(vote) & set(cc) & set(truth)):
        grouped[agreement_bucket(vote[key])].append(
            (int(_pair(cc[key]) == truth[key]), int(_pair(vote[key]) == truth[key]))
        )
    routing: dict[str, dict[str, object]] = {}
    for bucket, outcomes in sorted(grouped.items()):
        count = len(outcomes)
        cc_correct = sum(item[0] for item in outcomes)
        vote_correct = sum(item[1] for item in outcomes)
        wins = sum(a > b for a, b in outcomes)
        losses = sum(a < b for a, b in outcomes)
        p_value = _exact_mcnemar_p(wins, losses)
        route = (
            "cc"
            if count >= min_loci
            and cc_correct / count > vote_correct / count + min_gain
            and wins > losses
            and p_value < alpha
            else "mv"
        )
        routing[bucket] = {
            "route": route,
            "training_loci": count,
            "cc_correct": cc_correct,
            "mv_correct": vote_correct,
            "mcnemar_wins": wins,
            "mcnemar_losses": losses,
            "mcnemar_p": p_value,
        }
    return routing


def compose_mv_floor(
    held_vote: list[dict[str, str]],
    held_cc: list[dict[str, str]],
    routing: dict[str, dict[str, object]],
    fold: str,
) -> list[dict[str, str]]:
    vote = {_locus(row): row for row in held_vote}
    cc = {_locus(row): row for row in held_cc}
    output = []
    for key in sorted(vote):
        bucket = agreement_bucket(vote[key])
        route = str(routing.get(bucket, {}).get("route", "mv"))
        source = cc.get(key) if route == "cc" else vote[key]
        if source is None:
            source = vote[key]
            route = "mv"
        row = dict(source)
        row.update({
            "method": MV_FLOOR_METHOD,
            "decision_reason": f"mv_floor:{bucket}:{route}",
            "analysis_scope": "exploratory_fitted",
            "outer_fold": fold,
        })
        output.append(row)
    return output


def _feature_schema() -> dict[str, list[str]]:
    tools = sorted({tool for panel in PANELS.values() for tool in panel})
    families = sorted({family_of(tool) for tool in tools})
    names = list(NUMERIC_FEATURES)
    names.extend(f"modality={value}" for value in PANELS)
    names.extend(f"gene={value}" for value in GENES)
    names.extend(f"support_tool={value}" for value in tools)
    names.extend(f"callable_tool={value}" for value in tools)
    names.extend(f"support_family={value}" for value in families)
    return {"feature_names": names, "tools": tools, "families": families}


def _fit_context(
    rows: list[dict[str, str]],
    truth: dict[tuple[str, str, str, str], tuple[str, str]],
) -> dict[str, float]:
    """Jeffreys-smoothed fold-local caller reliability on fixed loci."""
    by_caller: dict[tuple[str, str, str], list[int]] = defaultdict(list)
    by_modality: dict[tuple[str, str], list[int]] = defaultdict(list)
    indexed = {(_locus(row), row["caller"]): row for row in rows}
    training_loci = sorted(set(_locus(row) for row in rows) & set(truth))
    for key in training_loci:
        _, _, modality, gene = key
        for caller in PANELS[modality]:
            row = indexed.get((key, caller))
            hit = int(bool(row) and _pair(row) == truth[key])
            by_caller[(caller, modality, gene)].append(hit)
            by_modality[(caller, modality)].append(hit)
    reliability: dict[str, float] = {}
    for (caller, modality, gene), values in by_caller.items():
        fallback = by_modality[(caller, modality)]
        reliability[f"{caller}|{modality}|{gene}"] = (
            (sum(values) + 0.5) / (len(values) + 1.0)
            if values
            else (sum(fallback) + 0.5) / (len(fallback) + 1.0)
        )
    return reliability


def _reliability(context: dict[str, float], caller: str, modality: str, gene: str) -> float:
    return float(context.get(f"{caller}|{modality}|{gene}", 0.5))


def _entropy(counts: list[int]) -> float:
    total = sum(counts)
    if total <= 0 or len(counts) <= 1:
        return 0.0
    return -sum((n / total) * math.log(n / total) for n in counts if n) / math.log(len(counts))


def _candidate_records(
    rows: list[dict[str, str]],
    context: dict[str, float],
    schema: dict[str, list[str]],
    truth: dict[tuple[str, str, str, str], tuple[str, str]] | None = None,
) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[_locus(row)].append(row)
    output = []
    for key, entries in sorted(grouped.items()):
        cohort, subject, modality, gene = key
        expected = set(PANELS[modality])
        callable_rows = [row for row in entries if row["caller"] in expected and _pair(row)]
        if not callable_rows:
            continue
        candidates: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
        for row in callable_rows:
            pair = _pair(row)
            assert pair is not None
            candidates[pair].append(row)
        counts = {pair: len(support) for pair, support in candidates.items()}
        weights = {
            pair: sum(_reliability(context, row["caller"], modality, gene) for row in support)
            for pair, support in candidates.items()
        }
        total_count = len(callable_rows)
        total_weight = sum(weights.values()) or float(total_count)
        vote_winner = sorted(candidates, key=lambda pair: (-counts[pair], pair))[0]
        weighted_winner = sorted(candidates, key=lambda pair: (-weights[pair], pair))[0]
        callable_tools = {row["caller"] for row in callable_rows}
        all_families = {family_of(tool) for tool in expected}
        for pair, support in sorted(candidates.items()):
            support_tools = {row["caller"] for row in support}
            support_families = {family_of(tool) for tool in support_tools}
            confidences = [_reliability(context, tool, modality, gene) for tool in support_tools]
            others = [value for candidate, value in counts.items() if candidate != pair]
            other_weights = [value for candidate, value in weights.items() if candidate != pair]
            numeric = {
                "equal_support_fraction": counts[pair] / total_count,
                "equal_support_margin": (counts[pair] - max(others or [0])) / total_count,
                "vote_entropy": _entropy(list(counts.values())),
                "weighted_support_fraction": weights[pair] / total_weight,
                "weighted_support_margin": (weights[pair] - max(other_weights or [0.0])) / total_weight,
                "supporting_tool_fraction": len(support_tools) / len(expected),
                "supporting_family_fraction": len(support_families) / len(all_families),
                "mean_support_confidence": sum(confidences) / len(confidences),
                "max_support_confidence": max(confidences),
                "min_support_confidence": min(confidences),
                "confidence_coverage": 0.0,
                "callable_tool_fraction": len(callable_tools) / len(expected),
                "missing_tool_fraction": 1.0 - len(callable_tools) / len(expected),
                "is_equal_vote_winner": float(pair == vote_winner),
                "is_weighted_vote_winner": float(pair == weighted_winner),
                "is_homozygous": float(pair[0] == pair[1]),
                "is_ciwd_plausible": 0.0,
                "has_ambiguity_notation": float(any("/" in allele for allele in pair)),
            }
            values = dict(numeric)
            values.update({f"modality={value}": float(modality == value) for value in PANELS})
            values.update({f"gene={value}": float(gene == value) for value in GENES})
            values.update({f"support_tool={tool}": float(tool in support_tools)
                           for tool in schema["tools"]})
            values.update({f"callable_tool={tool}": float(tool in callable_tools)
                           for tool in schema["tools"]})
            values.update({f"support_family={family}": float(family in support_families)
                           for family in schema["families"]})
            record: dict[str, object] = {
                "cohort": cohort,
                "subject": subject,
                "modality": modality,
                "gene": gene,
                "allele1": pair[0],
                "allele2": pair[1],
                "candidate_pair": "+".join(pair),
                "supporting_callers": ",".join(sorted(support_tools)),
                "features": [float(values.get(name, 0.0)) for name in schema["feature_names"]],
            }
            if truth is not None:
                record["label"] = int(pair == truth.get(key))
            output.append(record)
    return output


def _locus_weights(records: list[dict[str, object]]) -> np.ndarray:
    grouped: dict[tuple[str, str, str], list[int]] = defaultdict(list)
    for index, row in enumerate(records):
        grouped[(str(row["subject"]), str(row["modality"]), str(row["gene"]))].append(index)
    result = np.zeros(len(records), dtype=float)
    for indices in grouped.values():
        positives = [index for index in indices if int(records[index].get("label", 0))]
        negatives = [index for index in indices if index not in positives]
        for members in (positives, negatives):
            for index in members:
                result[index] = (0.5 if positives and negatives else 1.0) / len(members)
    return result


def _sigmoid(values: np.ndarray) -> np.ndarray:
    """Numerically stable sigmoid (both ``np.where`` branches are evaluated)."""
    output = np.empty_like(values, dtype=float)
    positive = values >= 0
    output[positive] = 1.0 / (1.0 + np.exp(-values[positive]))
    exponent = np.exp(values[~positive])
    output[~positive] = exponent / (1.0 + exponent)
    return output


def fit_logistic(records: list[dict[str, object]], l2: float = 1.0) -> dict[str, object]:
    """Recovered deterministic, locus-weighted L2 logistic fit."""
    if not records:
        raise ValueError("cannot fit MetaConsensus without candidates")
    x = np.asarray([row["features"] for row in records], dtype=float)
    y = np.asarray([int(row.get("label", 0)) for row in records], dtype=float)
    weights = _locus_weights(records)
    mean, std = x.mean(axis=0), x.std(axis=0)
    std[std < 1e-8] = 1.0
    z = (x - mean) / std
    coef = np.zeros(z.shape[1], dtype=float)
    positives = float((weights * y).sum())
    negatives = float((weights * (1.0 - y)).sum())
    intercept = math.log((positives + 0.5) / (negatives + 0.5))
    total = max(float(weights.sum()), 1e-9)
    m = np.zeros_like(coef)
    v = np.zeros_like(coef)
    mb = vb = 0.0
    for step in range(1, 1201):
        linear = intercept + z.dot(coef)
        probability = _sigmoid(linear)
        error = weights * (probability - y)
        gradient = z.T.dot(error) / total + l2 * coef / len(records)
        gradient_b = float(error.sum() / total)
        m = 0.9 * m + 0.1 * gradient
        v = 0.999 * v + 0.001 * gradient * gradient
        mb = 0.9 * mb + 0.1 * gradient_b
        vb = 0.999 * vb + 0.001 * gradient_b * gradient_b
        coef -= 0.2 * (m / (1.0 - 0.9 ** step)) / (np.sqrt(v / (1.0 - 0.999 ** step)) + 1e-8)
        intercept -= 0.2 * (mb / (1.0 - 0.9 ** step)) / (math.sqrt(vb / (1.0 - 0.999 ** step)) + 1e-8)
    return {
        "intercept": float(intercept),
        "coef": coef.tolist(),
        "mean": mean.tolist(),
        "std": std.tolist(),
        "l2": l2,
    }


def _probabilities(records: list[dict[str, object]], model: dict[str, object]) -> np.ndarray:
    if not records:
        return np.asarray([], dtype=float)
    x = np.asarray([row["features"] for row in records], dtype=float)
    linear = float(model["intercept"]) + (
        (x - np.asarray(model["mean"])) / np.asarray(model["std"])
    ).dot(np.asarray(model["coef"]))
    return _sigmoid(linear)


def _top(records: list[dict[str, object]], probabilities: np.ndarray) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row, probability in zip(records, probabilities):
        candidate = dict(row)
        candidate["probability"] = float(probability)
        grouped[(str(row["subject"]), str(row["modality"]), str(row["gene"]))].append(candidate)
    return [
        sorted(rows, key=lambda row: (-float(row["probability"]), str(row["candidate_pair"])))[0]
        for _, rows in sorted(grouped.items())
    ]


def _inner_fold_map(rows: list[dict[str, str]], folds: int, seed: int) -> dict[str, int]:
    populations: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        populations[row.get("superpopulation", "unknown") or "unknown"].add(row["subject"])
    rng = random.Random(seed)
    mapping = {}
    for population in sorted(populations):
        subjects = sorted(populations[population])
        rng.shuffle(subjects)
        for index, subject in enumerate(subjects):
            mapping[subject] = index % min(folds, len(subjects))
    return mapping


def fit_meta_model(
    rows: list[dict[str, str]],
    truth: dict[tuple[str, str, str, str], tuple[str, str]],
    *,
    inner_folds: int = 5,
    seed: int = 42,
    l2_grid: tuple[float, ...] = L2_GRID,
) -> dict[str, object]:
    """Select L2 in grouped inner folds, then refit on all outer-training rows."""
    schema = _feature_schema()
    fold_of = _inner_fold_map(rows, inner_folds, seed)
    scores: dict[float, list[float]] = {value: [] for value in l2_grid}
    for fold in sorted(set(fold_of.values())):
        training = [row for row in rows if fold_of[row["subject"]] != fold]
        held = [row for row in rows if fold_of[row["subject"]] == fold]
        if not training or not held:
            continue
        training_truth = {key: value for key, value in truth.items() if fold_of.get(key[1]) != fold}
        held_truth = {key: value for key, value in truth.items() if fold_of.get(key[1]) == fold}
        context = _fit_context(training, training_truth)
        train_candidates = _candidate_records(training, context, schema, training_truth)
        held_candidates = _candidate_records(held, context, schema, held_truth)
        for l2 in l2_grid:
            selected = _top(held_candidates, _probabilities(held_candidates, fit_logistic(train_candidates, l2)))
            scores[l2].append(sum(int(row.get("label", 0)) for row in selected) / max(1, len(selected)))
    available = {l2: sum(values) / len(values) for l2, values in scores.items() if values}
    if not available:
        raise ValueError("inner folds produced no MetaConsensus validation split")
    selected_l2 = sorted(available, key=lambda value: (-available[value], -value))[0]
    context = _fit_context(rows, truth)
    candidates = _candidate_records(rows, context, schema, truth)
    model = {
        "schema_version": "champhla-metaconsensus-v350-1",
        "feature_schema": schema,
        "context": context,
        "candidate_model": fit_logistic(candidates, selected_l2),
        "selected_l2": selected_l2,
        "inner_folds": inner_folds,
    }
    encoded = json.dumps(model, sort_keys=True, separators=(",", ":")).encode()
    model["model_sha256"] = hashlib.sha256(encoded).hexdigest()
    return model


def score_meta(rows: list[dict[str, str]], model: dict[str, object], fold: str) -> list[dict[str, str]]:
    reject_truth_columns(rows, "MetaConsensus held-out caller input")
    candidates = _candidate_records(
        rows,
        model["context"],  # type: ignore[arg-type]
        model["feature_schema"],  # type: ignore[arg-type]
    )
    selected = _top(candidates, _probabilities(candidates, model["candidate_model"]))  # type: ignore[arg-type]
    by_locus = {(str(row["cohort"]), str(row["subject"]), str(row["modality"]),
                 str(row["gene"])): row for row in selected}
    loci = sorted({_locus(row) for row in rows})
    output = []
    for key in loci:
        candidate = by_locus.get(key)
        cohort, subject, modality, gene = key
        output.append({
            "cohort": cohort,
            "subject": subject,
            "superpopulation": next((row.get("superpopulation", "") for row in rows
                                      if _locus(row) == key), ""),
            "modality": modality,
            "gene": gene,
            "method": META_METHOD,
            "allele1": str(candidate["allele1"]) if candidate else "",
            "allele2": str(candidate["allele2"]) if candidate else "",
            "call_status": "callable" if candidate else "no_evidence",
            "decision_reason": "metaconsensus_refit" if candidate else "no_candidate",
            "analysis_scope": "exploratory_fitted",
            "outer_fold": fold,
            "model_sha256": str(model["model_sha256"]),
        })
    return output


def refit_fitted_methods(
    calls: list[dict[str, str]],
    truth: dict[tuple[str, str, str, str], tuple[str, str]],
    outer_folds: dict[tuple[str, str], str],
    raw_cc_policy: str,
    *,
    inner_folds: int = 5,
    seed: int = 42,
    mv_min_loci: int = 20,
) -> tuple[list[dict[str, str]], dict[str, object]]:
    """Refit both historical comparators without using held-out truth for prediction."""
    reject_truth_columns(calls, "fitted-method caller input")
    vote = [row for row in build_consensus(calls) if row["method"] == METHOD_PLURALITY]
    cc = predict_raw_cc(calls, raw_cc_policy)
    output: list[dict[str, str]] = []
    folds_manifest: dict[str, object] = {}
    for modality in sorted({row["modality"] for row in calls}):
        fold_values = sorted({fold for (subject, mod), fold in outer_folds.items()
                              if mod == modality}, key=int)
        folds_manifest[modality] = {}
        for fold in fold_values:
            held_subjects = {subject for (subject, mod), value in outer_folds.items()
                             if mod == modality and value == fold}
            train_subjects = {subject for (subject, mod), value in outer_folds.items()
                              if mod == modality and value != fold}
            training_truth = {key: value for key, value in truth.items()
                              if key[2] == modality and key[1] in train_subjects}
            training_vote = [row for row in vote if row["modality"] == modality
                             and row["subject"] in train_subjects]
            training_cc = [row for row in cc if row["modality"] == modality
                           and row["subject"] in train_subjects]
            routing = learn_mv_floor_routing(
                training_vote, training_cc, training_truth, min_loci=mv_min_loci
            )
            held_vote = [row for row in vote if row["modality"] == modality
                         and row["subject"] in held_subjects]
            held_cc = [row for row in cc if row["modality"] == modality
                       and row["subject"] in held_subjects]
            output.extend(compose_mv_floor(held_vote, held_cc, routing, fold))
            training_calls = [row for row in calls if row["modality"] == modality
                              and row["subject"] in train_subjects]
            held_calls = [row for row in calls if row["modality"] == modality
                          and row["subject"] in held_subjects]
            model = fit_meta_model(
                training_calls,
                training_truth,
                inner_folds=inner_folds,
                seed=seed + int(fold),
            )
            output.extend(score_meta(held_calls, model, fold))
            folds_manifest[modality][fold] = {
                "training_subjects": len(train_subjects),
                "held_subjects": len(held_subjects),
                "mv_floor_routing": routing,
                "metaconsensus_model_sha256": model["model_sha256"],
                "metaconsensus_selected_l2": model["selected_l2"],
            }
    output.sort(key=lambda row: (*_locus(row), row["method"]))
    manifest = {
        "schema_version": "champhla-fitted-comparators-v350-1",
        "methods": [MV_FLOOR_METHOD, META_METHOD],
        "truth_values_used_for_prediction": "training_folds_only",
        "held_out_truth_columns_in_prediction_input": False,
        "folds": folds_manifest,
    }
    return output, manifest
