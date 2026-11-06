"""Generate the journal-neutral ChampHLA main and supplementary figures."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import sys
from pathlib import Path

os.environ.setdefault("SOURCE_DATE_EPOCH", "1790208000")

import matplotlib  # noqa: E402

matplotlib.use("Agg")
matplotlib.rcParams.update({
    "svg.hashsalt": "panelhla-development-20260928-figure-restructure",
    "pdf.compression": 0,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import Normalize  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
EVAL = ROOT / "artifacts" / "development_corrected"
CHAR = ROOT / "artifacts" / "development_characterisation"
SOURCES = {
    "truth_flow": CHAR / "truth_flow.tsv",
    "performance": EVAL / "method_performance.tsv",
    "comparisons": EVAL / "secondary_method_results.tsv",
    "missingness": CHAR / "caller_missingness.tsv",
    "support": CHAR / "support_stratified_concordance.tsv",
    "correlation": CHAR / "caller_error_correlation.tsv",
    "ambiguity": CHAR / "ambiguity_compatibility.tsv",
    "g_group": CHAR / "g_group_compatibility.tsv",
    "p_group": CHAR / "p_group_compatibility.tsv",
}
# Aggregate-only exploratory cohorts (Supplementary S9); no row-level patient data.
ASSAYS = ("wes", "rnaseq")
LABEL = {"wes": "WES", "rnaseq": "RNA-seq"}
DISPLAY = {
    "SimplePluralityLex": "ChampHLA-Consensus",
    "SimpleStrictMajority": "Strict majority",
    "SimpleTwoThirdsConsensus": "Two-thirds consensus",
    "ArcasHLA": "arcasHLA",
    "BestSingleTool_nestedCV": "Best caller (nested CV)",
    "ChampionChallenger": "Champion–challenger",
    "TwoThirdsGuardedCC": "Two-thirds guarded",
    "MVFlooredCC": "Vote-support restricted",
    "MetaConsensus": "Logistic meta-consensus",
    "FamilyGatedCC": "Algorithm-family restricted",
}
CALLER_ORDER = ("ArcasHLA", "HLA-HD", "OptiType", "POLYSOLVER", "SpecHLA", "T1K")
# The frozen assay panels; tests/test_rerun_figure_s9.py keeps them identical to
# champhla_confirmation.panels.PANELS. ArcasHLA is an RNA-seq-only caller.
FROZEN_PANELS = {
    "wes": ("HLA-HD", "OptiType", "POLYSOLVER", "SpecHLA", "T1K"),
    "rnaseq": ("ArcasHLA", "HLA-HD", "OptiType", "T1K"),
}
FITTED_ORDER = (
    "BestSingleTool_nestedCV", "ChampionChallenger", "TwoThirdsGuardedCC",
    "MVFlooredCC", "MetaConsensus", "FamilyGatedCC",
)
THRESHOLD_ORDER = ("SimplePluralityLex", "SimpleStrictMajority",
                   "SimpleTwoThirdsConsensus")

DOUBLE = 7.087  # 180 mm
BLUE = "#0072B2"
ORANGE = "#E69F00"
GREY = "#8A8A8A"
LIGHT_GREY = "#C7CDD4"
DARK = "#222222"
MAGENTA = "#AA3377"  # reserved for statistical significance
FIREWALL_PURPLE = "#6F4E7C"
STATE_COLOURS = {
    "resolved": "#009E73", "ambiguous": "#56B4E9",
    "invalid": "#CC79A7", "absent": "#B8B8B8",
}
RERUN_CHANGE_ORDER = (
    "identical", "call_changed", "noncall_to_callable", "callable_to_noncall",
    "noncall_state_changed", "new_rerun_cell", "stored_cell_missing_from_rerun",
)
# Reader labels shared with Supplementary Table S10.2 (round 4 amendment, A3).
RERUN_CHANGE_LABELS = {
    "identical": "identical",
    "call_changed": "call changed",
    "noncall_to_callable": "non-call to callable",
    "callable_to_noncall": "callable to non-call",
    "noncall_state_changed": "non-call state changed",
    "new_rerun_cell": "present only in the study run",
    "stored_cell_missing_from_rerun": "present only in the archived outputs",
}
RERUN_CHANGE_COLOURS = {
    "identical": "#999999",
    "call_changed": "#0072B2",
    "noncall_to_callable": "#009E73",
    "callable_to_noncall": "#D55E00",
    "noncall_state_changed": "#CC79A7",
    "new_rerun_cell": "#56B4E9",
    "stored_cell_missing_from_rerun": "#E69F00",
}

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.titlesize": 9,
    "axes.titlelocation": "left",
    "axes.labelsize": 8,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 7,
    "figure.dpi": 600,
})


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise SystemExit(f"missing figure source artifact: {path}")
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def pretty(method: str) -> str:
    method = method[7:] if method.startswith("Caller:") else method
    return DISPLAY.get(method, method)


def marked(method: str) -> str:
    """Figures 2 and 3 flag the defective arcasHLA deployment (round 4 amendment, A2)."""
    label = pretty(method)
    return label + "†" if label == "arcasHLA" else label


def slug(value: str) -> str:
    import re
    return re.sub(r"[^A-Z0-9]+", "_", value.upper()).strip("_")


def panel_label(ax, label: str) -> None:
    ax.text(-0.10, 1.06, label, transform=ax.transAxes, fontsize=10,
            fontweight="bold", ha="left", va="bottom")


def save(fig, out_dir: Path, name: str) -> dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {suffix: out_dir / f"{name}.{suffix}"
             for suffix in ("pdf", "svg", "png", "tiff")}
    fig.savefig(paths["pdf"], bbox_inches="tight",
                metadata={"Creator": "ChampHLA reproducible figure generator",
                          "CreationDate": None})
    fig.savefig(paths["svg"], bbox_inches="tight", metadata={"Date": None})
    svg_text = paths["svg"].read_text(encoding="utf-8")
    with paths["svg"].open("w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(line.rstrip() for line in svg_text.splitlines()) + "\n")
    fig.savefig(paths["png"], bbox_inches="tight", dpi=600,
                metadata={"Software": "ChampHLA"})
    fig.savefig(paths["tiff"], bbox_inches="tight", dpi=600,
                pil_kwargs={"compression": "tiff_lzw"})
    plt.close(fig)
    print(f"  wrote {name} (.pdf, .svg, .png, .tiff)")
    return {suffix: sha256(path) for suffix, path in paths.items()}


def save_exploratory(fig, out_dir: Path, name: str) -> dict[str, str]:
    """Save aggregate-only exploratory figures in the three requested formats."""
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {suffix: out_dir / f"{name}.{suffix}" for suffix in ("pdf", "svg", "png")}
    fig.savefig(paths["pdf"], bbox_inches="tight",
                metadata={"Creator": "ChampHLA reproducible figure generator",
                          "CreationDate": None})
    fig.savefig(paths["svg"], bbox_inches="tight", metadata={"Date": None})
    svg_text = paths["svg"].read_text(encoding="utf-8")
    with paths["svg"].open("w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(line.rstrip() for line in svg_text.splitlines()) + "\n")
    fig.savefig(paths["png"], bbox_inches="tight", dpi=300,
                metadata={"Software": "ChampHLA", "dpi": "300"})
    plt.close(fig)
    print(f"  wrote {name} (.pdf, .svg, .png; PNG 300 dpi)")
    return {suffix: sha256(path) for suffix, path in paths.items()}


def _box(ax, x: float, y: float, width: float, height: float, text: str,
         face: str = "#F3F5F7", edge: str = GREY) -> None:
    patch = FancyBboxPatch(
        (x, y), width, height, boxstyle="round,pad=0.018,rounding_size=0.02",
        linewidth=0.8, edgecolor=edge, facecolor=face,
    )
    ax.add_patch(patch)
    ax.text(x + width / 2, y + height / 2, text, ha="center", va="center",
            fontsize=7, linespacing=1.25)


def _arrow(ax, start: tuple[float, float], end: tuple[float, float]) -> None:
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=8,
                                 linewidth=0.8, color=DARK))


def _pipeline_panel(ax) -> None:
    """Panel A: the ChampHLA workflow, as implemented in the pipeline repository."""
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    panel_label(ax, "A")
    ax.set_title("ChampHLA workflow", pad=12)
    steps = [
        (0.02, "Input\nFASTQ, BAM or\nCRAM + reference"),
        (0.22, "Preprocessing\nDNA: HLA reads\nrealigned to\nchromosome 6\nBAM → FASTQ"),
        (0.42, "Assay panel\nWES: 5 callers\nRNA-seq: 4 callers\n(Table 1)"),
        (0.62, "Parse outputs;\nnormalize to\ntwo-field\ngenotypes"),
        (0.82, "Consensus\nEqual-weight\ngenotype vote"),
    ]
    width = 0.15
    for x, text in steps:
        _box(ax, x, 0.24, width, 0.56, text,
             face="#E8F5E9" if x == 0.82 else "#EAF2F8")
    for left, right in zip(steps[:-1], steps[1:]):
        _arrow(ax, (left[0] + width + 0.012, 0.52), (right[0] - 0.012, 0.52))
    ax.text(0.50, 0.06,
            "Each caller runs as its own Nextflow process, in a container except SpecHLA, "
            "which ran natively here; the assay panel is the default caller set.",
            ha="center", va="center", fontsize=7, color=DARK)


def _vote_panel(ax) -> None:
    """Panel B: an illustrative ChampHLA-Consensus vote at one WES locus."""
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    panel_label(ax, "B")
    ax.set_title("ChampHLA-Consensus vote (illustrative)", pad=12)
    calls = [
        ("HLA-HD", "A*02:01 / A*24:02", "#EAF2F8"),
        ("OptiType", "A*02:01 / A*24:02", "#EAF2F8"),
        ("POLYSOLVER", "A*02:01 / A*24:02", "#EAF2F8"),
        ("SpecHLA", "A*02:01 / A*11:01", "#FDF2E9"),
        ("T1K", "no call: not counted", "#F3F5F7"),
    ]
    for i, (caller, genotype, face) in enumerate(calls):
        y = 0.80 - i * 0.135
        ax.text(0.00, y, caller, ha="left", va="center", fontsize=7, color=DARK)
        _box(ax, 0.31, y - 0.05, 0.36, 0.10, genotype, face=face)
    _arrow(ax, (0.69, 0.53), (0.735, 0.53))
    _box(ax, 0.75, 0.36, 0.20, 0.34,
         "Reported\nA*02:01\nA*24:02\n3 of 4\ncallable", face="#E8F5E9")
    ax.text(0.50, 0.02,
            "One vote per callable caller; the most-voted\nunordered genotype is "
            "reported. An exact tie goes\nto the alphabetically first genotype.",
            ha="center", va="center", fontsize=7, color=DARK)


def figure1(truth_flow: list[dict[str, str]], out_dir: Path) -> tuple[dict, dict]:
    fig = plt.figure(figsize=(DOUBLE, 8.4))
    grid = fig.add_gridspec(3, 2, height_ratios=(0.78, 1.0, 0.95), width_ratios=(1, 1.18))
    _pipeline_panel(fig.add_subplot(grid[0, :]))
    _vote_panel(fig.add_subplot(grid[1, 0]))
    workflow = fig.add_subplot(grid[1, 1])
    flow = fig.add_subplot(grid[2, :])
    workflow.set_xlim(0, 1)
    workflow.set_ylim(0, 1)
    workflow.axis("off")
    panel_label(workflow, "C")
    workflow.set_title("Separating predictions from reference typing", pad=12)
    boxes = [
        (0.02, "Requested\nloci"),
        (0.36, "Caller processing\n+ normalization"),
        (0.70, "Predictions\ncompleted"),
    ]
    for x, text in boxes:
        _box(workflow, x, 0.63, 0.27, 0.18, text, face="#EAF2F8")
    for left, right in zip(boxes[:-1], boxes[1:]):
        workflow.add_patch(FancyArrowPatch(
            (left[0] + 0.27, 0.72), (right[0], 0.72), arrowstyle="-|>",
            mutation_scale=8, linewidth=0.8, color=DARK,
        ))
    _box(workflow, 0.05, 0.22, 0.39, 0.20,
         "Published typing\nExact genotypes +\ncandidate sets", face="#E8F5E9")
    _box(workflow, 0.66, 0.22, 0.30, 0.20,
         "Compare with\nreference typing", face="#F4ECF7")
    workflow.add_patch(FancyArrowPatch(
        (0.46, 0.32), (0.66, 0.32), arrowstyle="-|>", mutation_scale=8,
        linewidth=0.8, color=DARK,
    ))
    workflow.add_patch(FancyArrowPatch(
        (0.84, 0.63), (0.82, 0.42), arrowstyle="-|>", mutation_scale=8,
        linewidth=0.8, color=DARK,
    ))
    workflow.plot([0.56, 0.56], [0.16, 0.51], color=FIREWALL_PURPLE, linewidth=1.8)
    workflow.text(0.56, 0.53, "SEPARATE INPUTS", color=FIREWALL_PURPLE, fontsize=7,
                  fontweight="bold", ha="center", va="bottom")
    workflow.text(0.50, 0.06,
                  "Predictions are completed before comparison with reference typing.",
                  ha="center", va="center", fontsize=7, color=DARK)

    panel_label(flow, "D")
    flow.set_title("Eligibility of reference genotypes", pad=12)
    states = ("resolved", "ambiguous", "invalid", "absent")
    by_assay = {(row["modality"], row["truth_state"]): int(row["loci"])
                for row in truth_flow}
    requested = {modality: int(next(row["requested_loci"] for row in truth_flow
                                    if row["modality"] == modality))
                 for modality in ASSAYS}
    y = np.arange(len(ASSAYS))
    left = np.zeros(len(ASSAYS))
    for state in states:
        values = np.array([by_assay[(modality, state)] for modality in ASSAYS])
        bars = flow.barh(y, values, left=left, color=STATE_COLOURS[state],
                         edgecolor="white", linewidth=0.5, label=state.capitalize())
        for bar, value in zip(bars, values):
            if value >= 12:
                flow.text(bar.get_x() + bar.get_width() / 2,
                          bar.get_y() + bar.get_height() / 2, str(value),
                          ha="center", va="center", fontsize=7,
                          color="white" if state in {"resolved", "ambiguous"} else DARK)
        left += values
    flow.set_yticks(y, [LABEL[m] for m in ASSAYS])
    flow.invert_yaxis()
    flow.set_xlabel("Requested assay–gene loci")
    flow.set_xlim(0, max(requested.values()) * 1.06)
    flow.legend(frameon=False, ncol=4, loc="lower center",
                bbox_to_anchor=(0.5, -0.42))
    for yi, modality in enumerate(ASSAYS):
        present = requested[modality] - by_assay[(modality, "absent")]
        invalid = by_assay[(modality, "invalid")]
        flow.text(0, yi - 0.48,
                  f"requested {requested[modality]}; reference present {present}; "
                  f"invalid {invalid}",
                  ha="left", va="center", fontsize=7, color=DARK)
    flow.set_ylim(len(ASSAYS) - 0.35, -0.68)
    fig.subplots_adjust(left=0.10, right=0.97, top=0.95, bottom=0.09,
                        wspace=0.22, hspace=0.45)
    spec = {
        "figure_id": "Figure 1", "caption_key": "study_design_truth_flow",
        "panels": ["workflow", "consensus_vote", "truth_firewall", "truth_disposition"],
        "axis_limits": {"truth_disposition_x": [0, max(requested.values()) * 1.06]},
        "flow_counts": {
            modality: {
                "requested": requested[modality],
                "truth_source_present": requested[modality] - by_assay[(modality, "absent")],
                **{state: by_assay[(modality, state)] for state in states},
            }
            for modality in ASSAYS
        },
        "suppression_rule": None,
    }
    return spec, save(fig, out_dir, "figure1_study_design_truth_flow")


def _performance_rows(performance: list[dict[str, str]], modality: str) -> list[dict[str, str]]:
    candidates = [row for row in performance if row["modality"] == modality and (
        row["method"] in {"SimplePluralityLex", "BestSingleTool_nestedCV"}
        or row["method"].startswith("Caller:")
    )]
    order = {"SimplePluralityLex": 0, "BestSingleTool_nestedCV": 1}
    order.update({f"Caller:{caller}": index + 2 for index, caller in enumerate(CALLER_ORDER)})
    return sorted(candidates, key=lambda row: order[row["method"]])


def _metric_limit(rows: list[dict[str, str]], field: str) -> float:
    minimum = min(100 * float(row[field]) for row in rows)
    return max(0.0, 5 * math.floor((minimum - 3) / 5))


def figure2(performance: list[dict[str, str]], out_dir: Path) -> tuple[dict, dict]:
    displayed = [row for modality in ASSAYS for row in _performance_rows(performance, modality)]
    concordance_lo = _metric_limit(displayed, "genotype_ci_lo")
    callability_lo = _metric_limit(displayed, "callability_ci_lo")
    fig = plt.figure(figsize=(DOUBLE, 6.0))
    grid = fig.add_gridspec(2, 5, width_ratios=(2.25, 2.25, 1.0, 2.25, 1.0),
                            hspace=0.42, wspace=0.06)
    letters = iter("AB")
    for row_index, modality in enumerate(ASSAYS):
        rows = _performance_rows(performance, modality)
        y = np.arange(len(rows))[::-1]
        label_ax = fig.add_subplot(grid[row_index, 0])
        concordance_ax = fig.add_subplot(grid[row_index, 1], sharey=label_ax)
        correct_ax = fig.add_subplot(grid[row_index, 2], sharey=label_ax)
        callability_ax = fig.add_subplot(grid[row_index, 3], sharey=label_ax)
        callable_ax = fig.add_subplot(grid[row_index, 4], sharey=label_ax)
        panel_label(label_ax, next(letters))
        label_ax.set_title(f"{LABEL[modality]} ({rows[0]['loci']} loci)", pad=10)
        label_ax.set_xlim(0, 1)
        label_ax.set_ylim(-0.6, len(rows) - 0.4)
        label_ax.axis("off")
        for yi, item in zip(y, rows):
            label = marked(item["method"])
            if item["method"] == "BestSingleTool_nestedCV":
                label = "Best caller\n(nested cross-validation)"
            label_ax.text(0.98, yi, label, ha="right", va="center", fontsize=7.5,
                          fontweight="bold" if item["method"] == "SimplePluralityLex" else "normal")
        for ax, metric, low_field, high_field, lower, title in (
            (concordance_ax, "genotype_accuracy", "genotype_ci_lo", "genotype_ci_hi",
             concordance_lo, "Exact concordance (%)"),
            (callability_ax, "callability", "callability_ci_lo", "callability_ci_hi",
             callability_lo, "Callability (%)"),
        ):
            values = [100 * float(item[metric]) for item in rows]
            lo = [value - 100 * float(item[low_field]) for value, item in zip(values, rows)]
            hi = [100 * float(item[high_field]) - value for value, item in zip(values, rows)]
            ax.errorbar(values, y, xerr=[lo, hi], fmt="none", ecolor=LIGHT_GREY,
                        elinewidth=1, capsize=2, zorder=1)
            for value, yi, item in zip(values, y, rows):
                fitted = item["method"] == "BestSingleTool_nestedCV"
                colour = BLUE if item["method"] == "SimplePluralityLex" else (
                    ORANGE if fitted else GREY)
                ax.scatter(value, yi, color=colour, marker="^" if fitted else "o",
                           s=30, zorder=2, edgecolor="white", linewidth=0.3,
                           clip_on=False)
            ax.set_xlim(lower, 100)
            ax.set_ylim(-0.6, len(rows) - 0.4)
            ax.set_yticks([])
            ax.set_title(title, fontsize=8, loc="center")
            ax.axhspan(y[0] - 0.45, y[0] + 0.45, color="#EAF2F8", zorder=0)
            ax.grid(axis="x", color="#E5E5E5", linewidth=0.5)
        for text_ax, value_field, title in (
            (correct_ax, "genotypes_correct", "Correct / total"),
            (callable_ax, "callable", "Called / total"),
        ):
            text_ax.set_xlim(0, 1)
            text_ax.set_ylim(-0.6, len(rows) - 0.4)
            text_ax.axis("off")
            text_ax.set_title(title, fontsize=7, loc="center")
            for yi, item in zip(y, rows):
                text_ax.text(0.5, yi, f"{item[value_field]}/{item['loci']}",
                             ha="center", va="center", fontsize=7)
    fig.subplots_adjust(left=0.035, right=0.99, top=0.94, bottom=0.08)
    spec = {
        "figure_id": "Figure 2", "caption_key": "primary_performance_callability",
        "panels": ["wes_performance", "rnaseq_performance"],
        "axis_limits": {"concordance": [concordance_lo, 100],
                        "callability": [callability_lo, 100]},
        "displayed_methods": {
            modality: [row["method"] for row in _performance_rows(performance, modality)]
            for modality in ASSAYS
        },
        "metrics": ["genotype_accuracy", "callability"],
        "count_columns": ["genotypes_correct/loci", "callable/loci"],
        "suppression_rule": None,
    }
    return spec, save(fig, out_dir, "figure2_primary_performance")


def _comparison_order(rows: list[dict[str, str]], family: str) -> list[dict[str, str]]:
    subset = [row for row in rows if row["inference_family"] == family]
    descriptive_order = {f"Caller:{caller}": index for index, caller in enumerate(CALLER_ORDER)}
    descriptive_order.update({"SimpleStrictMajority": 100, "SimpleTwoThirdsConsensus": 101})
    fitted_order = {method: index for index, method in enumerate(FITTED_ORDER)}
    order = descriptive_order if family == "descriptive_comparator" else fitted_order
    return sorted(subset, key=lambda row: order.get(row["comparator"], 999))


def _format_p(value: str) -> str:
    number = float(value)
    if number < 0.001:
        return "<0.001"
    return f"{number:.3f}".rstrip("0").rstrip(".")


def figure3(comparisons: list[dict[str, str]], out_dir: Path) -> tuple[dict, dict]:
    limit = math.ceil(max(abs(float(row[field])) for row in comparisons
                          for field in ("simultaneous_ci_lo_points",
                                        "simultaneous_ci_hi_points")) / 5) * 5
    fig, axes = plt.subplots(2, 1, figsize=(DOUBLE, 7.0), sharex=True)
    for index, (ax, modality) in enumerate(zip(axes, ASSAYS)):
        assay_rows = [row for row in comparisons if row["modality"] == modality]
        layout: list[tuple[str, dict[str, str] | str]] = []
        for family, heading in (("descriptive_comparator", "DESCRIPTIVE COMPARATORS"),
                                ("exploratory_fitted", "EXPLORATORY FITTED POLICIES")):
            layout.append(("header", heading))
            layout.extend(("method", row) for row in _comparison_order(assay_rows, family))
        y_positions = np.arange(len(layout))[::-1]
        ticks, labels = [], []
        for y, (kind, content) in zip(y_positions, layout):
            if kind == "header":
                ax.text(-limit, y, str(content), fontsize=7, fontweight="bold",
                        ha="left", va="center", color=DARK)
                ax.axhline(y - 0.48, color="#E5E5E5", linewidth=0.6)
                continue
            row = content
            assert isinstance(row, dict)
            estimate = float(row["delta_points"])
            lower = float(row["simultaneous_ci_lo_points"])
            upper = float(row["simultaneous_ci_hi_points"])
            # Significance is the sign-flip Holm decision (decisions/20261009_signflip_governs.json);
            # the interval is the descriptive Bonferroni-adjusted cluster-t interval.
            significant = row["signflip_holm_significant"] == "1"
            fitted = row["inference_family"] == "exploratory_fitted"
            colour = MAGENTA if significant else GREY
            ax.errorbar(estimate, y, xerr=[[estimate - lower], [upper - estimate]],
                        fmt="none", ecolor=colour, elinewidth=1.2, capsize=2, zorder=1)
            ax.scatter(estimate, y, color=colour, marker="^" if fitted else "o",
                       s=30, edgecolor=DARK if significant else "white",
                       linewidth=0.7 if significant else 0.3, zorder=2)
            ticks.append(y)
            labels.append(marked(row["comparator"]))
            ax.text(1.03, y, f"{row['wins']}/{row['losses']}", transform=ax.get_yaxis_transform(),
                    ha="left", va="center", fontsize=7, clip_on=False)
            p_label = _format_p(row["signflip_holm_adjusted_p"]) + ("*" if significant else "")
            ax.text(1.24, y, p_label, transform=ax.get_yaxis_transform(),
                    ha="left", va="center", fontsize=7,
                    fontweight="bold" if significant else "normal", clip_on=False)
        ax.set_yticks(ticks, labels)
        ax.set_ylim(-0.7, len(layout) - 0.3)
        ax.set_xlim(-limit, limit)
        ax.axvline(0, color=DARK, linewidth=0.8)
        ax.grid(axis="x", color="#E5E5E5", linewidth=0.5)
        ax.set_title(f"{chr(65 + index)}  {LABEL[modality]} ({assay_rows[0]['loci']} loci)",
                     fontweight="bold")
        ax.text(1.03, 1.015, "wins/losses", transform=ax.transAxes,
                fontsize=7, ha="left")
        ax.text(1.24, 1.015, "sign-flip\nHolm p", transform=ax.transAxes,
                fontsize=7, ha="left")
    axes[-1].set_xlabel("ChampHLA-Consensus − comparator (percentage points)")
    fig.subplots_adjust(left=0.34, right=0.75, top=0.96, bottom=0.07, hspace=0.28)
    spec = {
        "figure_id": "Figure 3", "caption_key": "paired_cluster_robust_differences",
        "panels": ["wes_paired", "rnaseq_paired"],
        "axis_limits": {"difference_points": [-limit, limit]},
        "displayed_methods": {
            modality: {
                family: [row["comparator"] for row in _comparison_order(
                    [item for item in comparisons if item["modality"] == modality], family)]
                for family in ("descriptive_comparator", "exploratory_fitted")
            }
            for modality in ASSAYS
        },
        "right_columns": ["wins/losses", "signflip_holm_adjusted_p"],
        "suppression_rule": None, "significance_colour": MAGENTA,
    }
    return spec, save(fig, out_dir, "figure3_paired_differences")


def figure4(correlations: list[dict[str, str]], out_dir: Path) -> tuple[dict, dict]:
    fig, axes = plt.subplots(1, 2, figsize=(DOUBLE, 3.4))
    colour_map = plt.get_cmap("cividis")
    normalizer = Normalize(vmin=0, vmax=1)
    for index, (ax, modality) in enumerate(zip(axes, ASSAYS)):
        rows = [row for row in correlations if row["modality"] == modality]
        callers = [caller for caller in CALLER_ORDER
                   if any(caller in (row["caller1"], row["caller2"]) for row in rows)]
        positions = {caller: position for position, caller in enumerate(callers)}
        matrix = np.full((len(callers), len(callers)), np.nan)
        for row in rows:
            first, second = positions[row["caller1"]], positions[row["caller2"]]
            matrix[first, second] = float(row["error_phi"])
            matrix[second, first] = float(row["mutually_callable_error_phi"])
        for row_index in range(len(callers)):
            for column_index in range(len(callers)):
                value = matrix[row_index, column_index]
                face = "white" if np.isnan(value) else colour_map(normalizer(value))
                ax.add_patch(Rectangle(
                    (column_index - 0.5, row_index - 0.5), 1, 1,
                    facecolor=face, edgecolor="none",
                ))
        ax.set_xlim(-0.5, len(callers) - 0.5)
        ax.set_ylim(len(callers) - 0.5, -0.5)
        ax.set_aspect("equal")
        ax.set_xticks(range(len(callers)), [pretty(caller) for caller in callers],
                      rotation=42, ha="right")
        ax.set_yticks(range(len(callers)), [pretty(caller) for caller in callers])
        for row_index in range(len(callers)):
            for column_index in range(len(callers)):
                value = matrix[row_index, column_index]
                if not np.isnan(value):
                    ax.text(column_index, row_index, f"{value:.2f}", ha="center", va="center",
                            fontsize=7, color="white" if value < 0.30 or value > 0.72 else DARK)
                elif row_index == column_index:
                    ax.text(column_index, row_index, "—", ha="center", va="center",
                            fontsize=7, color=GREY)
        ax.set_title(f"{chr(65 + index)}  {LABEL[modality]}", fontweight="bold")
        ax.text(0.5, -0.28,
                "upper: fixed denominator φ    lower: mutually callable φ",
                transform=ax.transAxes, ha="center", va="top", fontsize=7)
    fig.subplots_adjust(left=0.10, right=0.86, top=0.90, bottom=0.27, wspace=0.34)
    colourbar_ax = fig.add_axes([0.91, 0.27, 0.018, 0.62])
    scalar_map = matplotlib.cm.ScalarMappable(norm=normalizer, cmap=colour_map)
    colourbar = fig.colorbar(scalar_map, cax=colourbar_ax)
    colourbar.set_label("Error φ", fontsize=7)
    spec = {
        "figure_id": "Figure 4", "caption_key": "caller_error_dependence",
        "panels": ["wes_error_phi", "rnaseq_error_phi"],
        "axis_limits": {"error_phi_colour_scale": [0, 1]},
        "matrix_values": {
            modality: [
                {
                    "caller1": row["caller1"], "caller2": row["caller2"],
                    "fixed_denominator_phi": float(row["error_phi"]),
                    "mutually_callable_phi": float(row["mutually_callable_error_phi"]),
                }
                for row in correlations if row["modality"] == modality
            ]
            for modality in ASSAYS
        },
        "suppression_rule": None,
    }
    return spec, save(fig, out_dir, "figure4_caller_error_dependence")


def supplementary_figure1(missingness: list[dict[str, str]], out_dir: Path) -> tuple[dict, dict]:
    states = ("callable", "partial", "missing", "absent", "invalid")
    labels = {"callable": "Callable", "partial": "Singleton/partial",
              "missing": "Missing/failed output", "absent": "Absent row",
              "invalid": "Invalid"}
    colours = {"callable": "#009E73", "partial": "#D8A200", "missing": "#4C78A8",
               "absent": "#999999", "invalid": "#CC79A7"}
    fig, axes = plt.subplots(1, 2, figsize=(DOUBLE, 3.2))
    for index, (ax, modality) in enumerate(zip(axes, ASSAYS)):
        rows = [row for row in missingness if row["modality"] == modality]
        rows.sort(key=lambda row: CALLER_ORDER.index(row["caller"]))
        y = np.arange(len(rows))
        left = np.zeros(len(rows))
        for state in states:
            values = np.array([100 * int(row[state]) / int(row["loci"]) for row in rows])
            bars = ax.barh(y, values, left=left, color=colours[state], height=0.65,
                           label=labels[state])
            for bar, row in zip(bars, rows):
                count = int(row[state])
                if count:
                    ax.text(bar.get_x() + bar.get_width() / 2,
                            bar.get_y() + bar.get_height() / 2, str(count),
                            ha="center", va="center", fontsize=7,
                            color="white" if state != "partial" else DARK)
            left += values
        ax.set_yticks(y, [pretty(row["caller"]) for row in rows])
        ax.invert_yaxis()
        ax.set_xlim(0, 100)
        ax.set_xlabel("Share of fixed assay–locus denominator (%)")
        ax.set_title(f"{chr(65 + index)}  {LABEL[modality]}", fontweight="bold")
    handles, legend_labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, legend_labels, frameon=False, ncol=3,
               loc="lower center", bbox_to_anchor=(0.5, -0.01))
    fig.subplots_adjust(left=0.12, right=0.98, top=0.90, bottom=0.23, wspace=0.34)
    spec = {
        "figure_id": "Supplementary Figure S1", "caption_key": "call_state_composition",
        "panels": ["wes_call_states", "rnaseq_call_states"],
        "axis_limits": {"percentage": [0, 100]}, "suppression_rule": None,
        "state_counts": {
            modality: [
                {field: (row[field] if field == "caller" else int(row[field]))
                 for field in ("caller", "loci", *states)}
                for row in missingness if row["modality"] == modality
            ]
            for modality in ASSAYS
        },
    }
    return spec, save(fig, out_dir, "supplementary_figure_s1_call_states")


def supplementary_figure2(performance: list[dict[str, str]], out_dir: Path) -> tuple[dict, dict]:
    fig, axes = plt.subplots(1, 2, figsize=(DOUBLE, 3.25), sharex=True, sharey=True)
    all_rows = [row for row in performance if row["method"] in THRESHOLD_ORDER]
    x_low = _metric_limit(all_rows, "callability_ci_lo")
    y_low = _metric_limit(all_rows, "genotype_ci_lo")
    for index, (ax, modality) in enumerate(zip(axes, ASSAYS)):
        rows = [next(row for row in performance
                     if row["modality"] == modality and row["method"] == method)
                for method in THRESHOLD_ORDER]
        x = [100 * float(row["callability"]) for row in rows]
        y = [100 * float(row["genotype_accuracy"]) for row in rows]
        xerr = [[value - 100 * float(row["callability_ci_lo"]) for value, row in zip(x, rows)],
                [100 * float(row["callability_ci_hi"]) - value for value, row in zip(x, rows)]]
        yerr = [[value - 100 * float(row["genotype_ci_lo"]) for value, row in zip(y, rows)],
                [100 * float(row["genotype_ci_hi"]) - value for value, row in zip(y, rows)]]
        ax.plot(x, y, color=LIGHT_GREY, linewidth=1, zorder=1)
        # Unclipped, so a bar that ends at 100% callability is drawn in full.
        ax.errorbar(x, y, xerr=xerr, yerr=yerr, fmt="none", ecolor=LIGHT_GREY,
                    elinewidth=0.8, capsize=2, zorder=1, clip_on=False)
        coincident = x[1] == x[2] and y[1] == y[2]
        styles = ((BLUE, "o"), (DARK, "s"), (GREY, "D"))
        for method, xi, yi, (colour, marker) in zip(THRESHOLD_ORDER, x, y, styles):
            ax.scatter(xi, yi, color=colour, marker=marker, s=42, zorder=2,
                       edgecolor="white", linewidth=0.4, clip_on=False)
            if coincident and method != "SimplePluralityLex":
                continue
            if coincident:
                offset, alignment = ((0, 10), "center")
            else:
                offset = (-4, 5) if method == "SimplePluralityLex" else (4, 5)
                alignment = "right" if method == "SimplePluralityLex" else "left"
            ax.annotate(pretty(method), (xi, yi), xytext=offset,
                        textcoords="offset points", fontsize=7, ha=alignment)
        if coincident:
            ax.scatter(x[1], y[1], facecolors="none", edgecolors=DARK, s=76,
                       linewidth=0.8, zorder=3, clip_on=False)
            ax.annotate("strict majority = two-thirds\n(identical estimate)",
                        (x[1], y[1]), xytext=(0, -17), textcoords="offset points",
                        fontsize=7, ha="center", va="top")
        ax.set_xlim(x_low, 100)
        ax.set_ylim(y_low, 100)
        ax.grid(color="#E5E5E5", linewidth=0.5)
        ax.set_title(f"{chr(65 + index)}  {LABEL[modality]}", fontweight="bold")
        ax.set_xlabel("Callability (%)")
    axes[0].set_ylabel("Fixed-denominator exact concordance (%)")
    fig.subplots_adjust(left=0.10, right=0.98, top=0.90, bottom=0.16, wspace=0.18)
    spec = {
        "figure_id": "Supplementary Figure S2", "caption_key": "threshold_tradeoff",
        "panels": ["wes_thresholds", "rnaseq_thresholds"],
        "axis_limits": {"callability": [x_low, 100], "concordance": [y_low, 100]},
        "threshold_points": {
            modality: [
                {
                    "method": row["method"],
                    "callability": 100 * float(row["callability"]),
                    "concordance": 100 * float(row["genotype_accuracy"]),
                }
                for row in performance
                if row["modality"] == modality and row["method"] in THRESHOLD_ORDER
            ]
            for modality in ASSAYS
        },
        "suppression_rule": None, "identical_points_not_jittered": True,
    }
    return spec, save(fig, out_dir, "supplementary_figure_s2_threshold_tradeoff")


def supplementary_figure3(support: list[dict[str, str]], out_dir: Path) -> tuple[dict, dict]:
    fig, axes = plt.subplots(1, 2, figsize=(DOUBLE, 3.4), sharey=True)
    profile_contract = {}
    for index, (ax, modality) in enumerate(zip(axes, ASSAYS)):
        all_rows = [row for row in support if row["modality"] == modality]
        defined = [row for row in all_rows if row["support_defined"] == "1"]
        defined.sort(key=lambda row: (int(row["callable_callers"]),
                                      int(row["support_numerator"])))
        shown = [row for row in defined if int(row["loci"]) >= 5]
        suppressed = [row for row in defined if int(row["loci"]) < 5]
        x = np.arange(len(shown))
        y = [100 * float(row["accuracy"]) for row in shown]
        lo = [value - 100 * float(row["ci_lo"]) for value, row in zip(y, shown)]
        hi = [100 * float(row["ci_hi"]) - value for value, row in zip(y, shown)]
        ax.errorbar(x, y, yerr=[lo, hi], fmt="none", ecolor=GREY,
                    capsize=2)
        ax.scatter(x, y, color=BLUE, marker="o", s=24, clip_on=False, zorder=2)
        for xi, yi, row in zip(x, y, shown):
            offset = (0, -13) if yi >= 95 else (0, 6)
            ax.annotate(f"n={row['loci']}", (xi, yi), xytext=offset,
                        textcoords="offset points", ha="center", fontsize=7)
        ax.set_xticks(x, [row["support_profile"] for row in shown])
        ax.set_xlim(-0.6, max(0.6, len(shown) - 0.4))
        ax.set_ylim(0, 100)
        ax.set_xlabel("Displayed support profile (supporting/callable)")
        ax.set_title(f"{chr(65 + index)}  {LABEL[modality]}", fontweight="bold")
        suppressed_text = ", ".join(
            f"{row['support_profile']} (n={row['loci']})" for row in suppressed
        ) or "none"
        undefined = [row for row in all_rows if row["support_defined"] == "0"]
        undefined_text = ", ".join(
            f"{row['support_profile']} (n={row['loci']}; non-call)" for row in undefined
        ) or "none"
        profile_contract[modality] = {
            "displayed": [row["support_profile"] for row in shown],
            "suppressed": [row["support_profile"] for row in suppressed],
            "outside_scale": [row["support_profile"] for row in undefined],
        }
        ax.text(0.0, -0.25, f"Estimate suppressed (n<5): {suppressed_text}",
                transform=ax.transAxes, ha="left", va="top", fontsize=7)
        ax.text(0.0, -0.34, f"Outside concordance scale: {undefined_text}",
                transform=ax.transAxes, ha="left", va="top", fontsize=7)
    axes[0].set_ylabel("Exact genotype concordance (%)")
    fig.subplots_adjust(left=0.09, right=0.98, top=0.90, bottom=0.31, wspace=0.18)
    spec = {
        "figure_id": "Supplementary Figure S3", "caption_key": "support_profiles",
        "panels": ["wes_support", "rnaseq_support"],
        "axis_limits": {"concordance": [0, 100]},
        "profile_contract": profile_contract,
        "suppression_rule": "point estimate and interval suppressed when loci < 5",
        "zero_support_outside_scale": True,
    }
    return spec, save(fig, out_dir, "supplementary_figure_s3_support_profiles")


def supplementary_figure4(performance: list[dict[str, str]], ambiguity: list[dict[str, str]],
                          g_group: list[dict[str, str]], p_group: list[dict[str, str]],
                          out_dir: Path) -> tuple[dict, dict]:
    allowed = {"SimplePluralityLex", "BestSingleTool_nestedCV"} | {
        f"Caller:{caller}" for caller in CALLER_ORDER
    }
    endpoint_rows = {
        "Exact two-field": [row for row in performance if row["method"] in allowed],
        "Ambiguity-compatible": [row for row in ambiguity if row["method"] in allowed],
        "G-compatible (two-field mapping)": [
            row for row in g_group if row["method"] in allowed
        ],
        "P-group-compatible (two-field mapping)": [
            row for row in p_group if row["method"] in allowed
        ],
    }
    endpoint_titles = {
        "Exact two-field": "Exact\ntwo-field",
        "Ambiguity-compatible": "Ambiguity-\ncompatible",
        "G-compatible (two-field mapping)": "G-compatible\n(two-field map)",
        "P-group-compatible (two-field mapping)": "P-compatible\n(two-field map)",
    }
    fig, axes = plt.subplots(2, 4, figsize=(DOUBLE, 5.8), sharex=False)
    for assay_index, modality in enumerate(ASSAYS):
        for endpoint_index, (endpoint, candidates) in enumerate(endpoint_rows.items()):
            ax = axes[assay_index, endpoint_index]
            rows = [row for row in candidates if row["modality"] == modality]
            order = {"SimplePluralityLex": 0, "BestSingleTool_nestedCV": 1}
            order.update({f"Caller:{caller}": index + 2
                          for index, caller in enumerate(CALLER_ORDER)})
            rows.sort(key=lambda row: order[row["method"]])
            y = np.arange(len(rows))[::-1]
            if endpoint == "Exact two-field":
                value_field, lower_field, upper_field = (
                    "genotype_accuracy", "genotype_ci_lo", "genotype_ci_hi")
            else:
                value_field, lower_field, upper_field = (
                    "compatibility_concordance", "ci_lo", "ci_hi")
            values = [100 * float(row[value_field]) for row in rows]
            lo = [value - 100 * float(row[lower_field]) for value, row in zip(values, rows)]
            hi = [100 * float(row[upper_field]) - value for value, row in zip(values, rows)]
            ax.errorbar(values, y, xerr=[lo, hi], fmt="none", ecolor=LIGHT_GREY,
                        elinewidth=0.9, capsize=2)
            for value, yi, row in zip(values, y, rows):
                fitted = row["method"] == "BestSingleTool_nestedCV"
                colour = BLUE if row["method"] == "SimplePluralityLex" else (
                    ORANGE if fitted else GREY)
                ax.scatter(value, yi, color=colour, marker="^" if fitted else "o", s=24)
            ax.set_yticks(y, [pretty(row["method"]) for row in rows]
                          if endpoint_index == 0 else [])
            ax.set_title(
                f"{endpoint_titles[endpoint]}\nN={rows[0]['loci']}",
                fontsize=7.5, loc="center", linespacing=1.05,
            )
            ax.set_xlim(_metric_limit(rows, lower_field), 100)
            ax.grid(axis="x", color="#E5E5E5", linewidth=0.5)
            if endpoint_index == 0:
                ax.set_ylabel(f"{LABEL[modality]}")
            if assay_index == 1:
                ax.set_xlabel("Concordance (%)")
    fig.text(0.015, 0.965, "A", fontsize=10, fontweight="bold")
    fig.text(0.015, 0.485, "B", fontsize=10, fontweight="bold")
    fig.subplots_adjust(left=0.24, right=0.98, top=0.91, bottom=0.09,
                        hspace=0.48, wspace=0.28)
    spec = {
        "figure_id": "Supplementary Figure S4", "caption_key": "truth_sensitivity",
        "panels": ["wes_endpoints", "rnaseq_endpoints"],
        "axis_limits": {"percentage_upper": 100},
        "endpoint_display_titles": endpoint_titles,
        "endpoint_contract": {
            modality: {
                endpoint: {
                    "denominators": sorted({int(row["loci"]) for row in rows
                                            if row["modality"] == modality}),
                    "methods": [row["method"] for row in rows
                                if row["modality"] == modality],
                }
                for endpoint, rows in endpoint_rows.items()
            }
            for modality in ASSAYS
        },
        "suppression_rule": None, "different_denominators_not_connected": True,
    }
    return spec, save(fig, out_dir, "supplementary_figure_s4_truth_sensitivity")


def supplementary_figure5(out_dir: Path) -> tuple[dict, dict]:
    """Champion–challenger decision flow, as implemented in raw_cc.predict_raw_cc."""
    fig, ax = plt.subplots(figsize=(DOUBLE, 3.9))
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.03, 1)
    ax.axis("off")
    _box(ax, 0.30, 0.86, 0.40, 0.10,
         "Intended-use caller calls at one subject–gene locus")
    _box(ax, 0.33, 0.67, 0.34, 0.11, "Is the selected default\ncaller callable?")
    _arrow(ax, (0.50, 0.86), (0.50, 0.78))
    # Champion callable branch.
    _box(ax, 0.02, 0.44, 0.30, 0.15,
         "Yes: champion genotype is the default.\nChallenger = highest-weighted\nnon-champion genotype")
    _box(ax, 0.02, 0.16, 0.30, 0.20,
         "Override only if all conditions hold:\nsupport fraction,\nminimum supporting callers,\nno ambiguous allele\n(margin term is 0 as implemented)")
    _box(ax, 0.02, 0.01, 0.13, 0.08, "Challenger", face="#E8F5E9")
    _box(ax, 0.19, 0.01, 0.13, 0.08, "Champion", face="#EAF2F8")
    _arrow(ax, (0.40, 0.67), (0.20, 0.59))
    _arrow(ax, (0.17, 0.44), (0.17, 0.36))
    _arrow(ax, (0.11, 0.16), (0.085, 0.09))
    _arrow(ax, (0.23, 0.16), (0.255, 0.09))
    ax.text(0.055, 0.125, "pass", fontsize=7, ha="center", color=DARK)
    ax.text(0.285, 0.125, "fail", fontsize=7, ha="center", color=DARK)
    # Champion missing branch.
    _box(ax, 0.68, 0.44, 0.30, 0.15,
         "No: weighted consensus.\nTop genotype by summed\nreliability weight")
    _box(ax, 0.68, 0.16, 0.30, 0.20,
         "Report only if not tied,\nsupport fraction ≥ 0.55\nand margin ≥ 0.15")
    _box(ax, 0.68, 0.01, 0.13, 0.08, "Top genotype", face="#E8F5E9")
    _box(ax, 0.85, 0.01, 0.13, 0.08, "No call", face="#F3F5F7")
    _arrow(ax, (0.60, 0.67), (0.80, 0.59))
    _arrow(ax, (0.83, 0.44), (0.83, 0.36))
    _arrow(ax, (0.77, 0.16), (0.745, 0.09))
    _arrow(ax, (0.89, 0.16), (0.915, 0.09))
    ax.text(0.715, 0.125, "pass", fontsize=7, ha="center", color=DARK)
    ax.text(0.945, 0.125, "fail", fontsize=7, ha="center", color=DARK)
    ax.text(0.50, 0.42,
            "Caller weight =\n0.7 × exact reliability\n+ 0.3 × guarded\ncalibrated confidence\n"
            "(fitted on the\ndevelopment set)",
            ha="center", va="center", fontsize=7, color=DARK)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02)
    spec = {
        "figure_id": "Supplementary Figure S5", "caption_key": "champion_challenger_flow",
        "panels": ["decision_flow"], "axis_limits": {}, "suppression_rule": None,
    }
    return spec, save(fig, out_dir, "supplementary_figure_s5_champion_challenger")


def supplementary_figure_rerun_changes(
    cell_changes: list[dict[str, str]], out_dir: Path
) -> tuple[dict, dict]:
    """Aggregate historical-to-v3.5.0 caller-cell changes; never expose subjects."""
    allowed = set(RERUN_CHANGE_ORDER)
    unexpected = sorted({row.get("difference_class", "") for row in cell_changes} - allowed)
    if unexpected:
        raise ValueError(f"unknown stored-to-rerun change classes: {unexpected}")
    grouped: dict[tuple[str, str], dict[str, int]] = {}
    for row in cell_changes:
        modality, caller = row.get("modality", ""), row.get("caller", "")
        if modality not in ASSAYS or caller not in CALLER_ORDER:
            raise ValueError(f"unexpected assay/caller in rerun cell ledger: {modality}/{caller}")
        counts = grouped.setdefault(
            (modality, caller), {change: 0 for change in RERUN_CHANGE_ORDER}
        )
        counts[row["difference_class"]] += 1
    expected_groups = {
        (modality, caller) for modality in ASSAYS for caller in FROZEN_PANELS[modality]
    }
    if set(grouped) != expected_groups:
        missing = sorted(expected_groups - set(grouped))
        extra = sorted(set(grouped) - expected_groups)
        raise ValueError(f"rerun figure caller panels differ: missing={missing}, extra={extra}")

    fig, axes = plt.subplots(1, 2, figsize=(DOUBLE, 4.4), sharex=True)
    aggregate_counts: dict[str, dict[str, dict[str, int]]] = {}
    for index, (ax, modality) in enumerate(zip(axes, ASSAYS)):
        callers = [caller for caller in CALLER_ORDER if (modality, caller) in grouped]
        y = np.arange(len(callers))
        left = np.zeros(len(callers))
        aggregate_counts[modality] = {}
        for change in RERUN_CHANGE_ORDER:
            values = []
            for caller in callers:
                counts = grouped[(modality, caller)]
                total = sum(counts.values())
                if not total:
                    raise ValueError(f"empty rerun change group: {modality}/{caller}")
                values.append(100 * counts[change] / total)
                aggregate_counts[modality][caller] = dict(counts)
            ax.barh(
                y, values, left=left, color=RERUN_CHANGE_COLOURS[change],
                edgecolor="white", linewidth=0.25,
                label=RERUN_CHANGE_LABELS[change],
            )
            left += np.asarray(values)
        ax.set_yticks(y, [pretty(caller) for caller in callers])
        ax.invert_yaxis()
        ax.set_xlim(0, 100)
        ax.set_xlabel("Caller–gene cells (%)")
        ax.set_title(f"{chr(65 + index)}  {LABEL[modality]}", fontweight="bold")
        ax.grid(axis="x", color="#E5E5E5", linewidth=0.5)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, frameon=False,
               bbox_to_anchor=(0.5, -0.01))
    fig.subplots_adjust(left=0.13, right=0.98, top=0.90, bottom=0.27, wspace=0.30)
    spec = {
        "figure_id": "Supplementary Figure S6",
        "caption_key": "stored_to_v350_caller_cell_changes",
        "panels": ["wes", "rnaseq"],
        "axis_limits": {"percentage_lower": 0, "percentage_upper": 100},
        "aggregate_only": True,
        "grouping": ["modality", "caller", "difference_class"],
        "change_order": list(RERUN_CHANGE_ORDER),
        "colours": RERUN_CHANGE_COLOURS,
        "aggregate_counts": aggregate_counts,
        "suppression_rule": None,
    }
    return spec, save(fig, out_dir, "supplementary_figure_s6_rerun_cell_changes")


def write_manifest(out_dir: Path, records: list[tuple[dict, dict]],
                   extra_sources: dict[str, Path] | None = None) -> None:
    render_profiles = {
        "publication_600dpi_four_format": {
            "formats": ["pdf", "svg", "png", "tiff"], "raster_dpi": 600,
        },
        "exploratory_300dpi_three_format": {
            "formats": ["pdf", "svg", "png"], "raster_dpi": 300,
        },
    }
    figures = []
    for raw_spec, hashes in records:
        spec = dict(raw_spec)
        profile = spec.setdefault("render_profile", "publication_600dpi_four_format")
        if profile not in render_profiles:
            raise ValueError(f"unknown figure render profile: {profile}")
        expected_formats = render_profiles[profile]["formats"]
        if list(hashes) != expected_formats:
            raise ValueError(
                f"{spec['figure_id']} render profile {profile} requires "
                f"{expected_formats}, observed {list(hashes)}"
            )
        figures.append({**spec, "output_sha256": hashes})

    payload = {
        "schema_version": "panelhla-figure-manifest-1",
        "style_contract": {
            "main_width_mm": 180, "minimum_font_points": 7,
            "percentage_upper_bound": 100, "significance_colour": MAGENTA,
            "formats": ["pdf", "svg", "png", "tiff"], "raster_dpi": 600,
            "exploratory_formats": ["pdf", "svg", "png"],
            "exploratory_raster_dpi": 300,
            "render_profiles": render_profiles,
        },
        "source_artifacts": {
            name: {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)}
            for name, path in {**SOURCES, **(extra_sources or {})}.items()
        },
        "figures": figures,
    }
    target = out_dir / "figure_manifest.json"
    with target.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"  wrote {target.resolve().relative_to(ROOT)}")


def main(argv: list[str]) -> int:
    out_dir = Path(argv[1]) if len(argv) > 1 else ROOT / "figures"
    data = {name: read_tsv(path) for name, path in SOURCES.items()}
    if any(row.get("modality") == "wgs" for rows in data.values() for row in rows):
        raise SystemExit("corrected publication artifacts must not contain WGS rows")
    records = [
        figure1(data["truth_flow"], out_dir),
        figure2(data["performance"], out_dir),
        figure3(data["comparisons"], out_dir),
        figure4(data["correlation"], out_dir),
        supplementary_figure1(data["missingness"], out_dir),
        supplementary_figure2(data["performance"], out_dir),
        supplementary_figure3(data["support"], out_dir),
        supplementary_figure4(
            data["performance"], data["ambiguity"], data["g_group"], data["p_group"],
            out_dir
        ),
        supplementary_figure5(out_dir),
    ]
    rerun_cells = (
        ROOT / "provenance/development_rerun_v350/truth_free_collection/"
        "stored_vs_rerun_cells.tsv"
    )
    extra_sources: dict[str, Path] = {}
    if rerun_cells.is_file():
        records.append(supplementary_figure_rerun_changes(read_tsv(rerun_cells), out_dir))
        extra_sources["stored_vs_rerun_cells"] = rerun_cells
    write_manifest(out_dir, records, extra_sources)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
