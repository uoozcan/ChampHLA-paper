from __future__ import annotations

import argparse

from .assays import build_assay_manifest
from .exposure import build_exposure_ledger
from .manuscript import audit_claims, write_docx_text, write_source_issue_register
from .provenance import build_originals_manifest
from .registry import render_tables, validate_registry
from .release import freeze_release, validate_release
from .rosters import freeze_rosters
from .truth import prepare_ambiguity_aware_truth, prepare_locked_truth


def build_subject_exposure_ledger_main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Build a cross-project subject exposure ledger")
    parser.add_argument("--source", action="append", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--summary", required=True)
    args = parser.parse_args(argv)
    build_exposure_ledger(args.source, args.output, args.summary)
    return 0


def prepare_locked_1000g_truth_main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Normalize and seal 2014 laboratory HLA truth")
    parser.add_argument("--source", required=True)
    parser.add_argument("--truth-output", required=True)
    parser.add_argument("--registry-output", required=True)
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args(argv)
    prepare_locked_truth(args.source, args.truth_output, args.registry_output, args.manifest)
    return 0


def prepare_ambiguity_aware_1000g_truth_main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Preserve all two-field candidates in 1000G HLA truth")
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args(argv)
    prepare_ambiguity_aware_truth(args.source, args.output, args.manifest)
    return 0


def freeze_extension_rosters_main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Freeze truth-blind 1000G extension rosters")
    parser.add_argument("--truth-registry", required=True)
    parser.add_argument("--assay-manifest", required=True)
    parser.add_argument("--exposure-ledger", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--summary", required=True)
    args = parser.parse_args(argv)
    result = freeze_rosters(args.truth_registry, args.assay_manifest, args.exposure_ledger,
                            args.config, args.output, args.summary)
    print(f"all_minimums_met={result['all_minimums_met']}")
    return 0 if result["all_minimums_met"] else 2


def freeze_release_bundle_main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Checksum the compact release candidate")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    result = freeze_release(args.project_root, args.output)
    print(f"release files={result['file_count']} git_dirty={result['git_dirty']}")
    return 0


def validate_release_freeze_main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Check a release freeze manifest against the working tree")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args(argv)
    result = validate_release(args.project_root, args.manifest)
    print(f"release freeze valid={result['valid']} recorded={result['recorded_file_count']} "
          f"missing={len(result['missing'])} mismatched={len(result['mismatched'])} "
          f"unfrozen={len(result['untracked'])}")
    print(f"  content_tree_sha256={result['recorded_content_tree_sha256']} "
          f"git_dirty={result['recorded_git_dirty']} "
          f"metadata_mismatch={result['metadata_mismatch']}")
    for path in result["missing"]:
        print(f"  MISSING    {path}")
    for path in result["mismatched"]:
        print(f"  MISMATCH   {path}")
    for path in result["untracked"]:
        print(f"  UNFROZEN   {path}")
    return 0 if result["valid"] else 2


def render_manuscript_tables_main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Render manuscript tables from the result registry")
    parser.add_argument("--registry", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--root")
    args = parser.parse_args(argv)
    failures = validate_registry(args.registry, args.root)
    if failures:
        raise ValueError("; ".join(failures))
    render_tables(args.registry, args.output)
    return 0


def audit_manuscript_claims_main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Audit manuscript claims against frozen results")
    parser.add_argument("--manuscript", required=True)
    parser.add_argument("--registry", required=True)
    parser.add_argument("--claims", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--root")
    parser.add_argument(
        "--author-gate",
        help="JSON gate whose unresolved items are pending author input; malformed gates fail closed")
    parser.add_argument(
        "--allow-pending-author-input", action="store_true",
        help="Exit 0 when the only failures are unresolved author-input placeholders. "
             "submission_ready is still reported False. Intended for continuous "
             "integration; the submission gate must run without this flag.")
    args = parser.parse_args(argv)
    result = audit_claims(
        args.manuscript, args.registry, args.claims, args.output, args.root,
        author_gate=args.author_gate,
    )
    print(f"submission_ready={result['submission_ready']} "
          f"failures={len(result['failures'])} warnings={len(result['warnings'])}")
    if result["pending_author_input"]:
        print(f"  pending author input: {', '.join(result['pending_author_input'])}")
    if args.allow_pending_author_input:
        return 0 if not result["blocking_failures"] else 2
    return 0 if result["submission_ready"] else 2


def build_review_docx_main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Render a manuscript to DOCX for co-author review")
    parser.add_argument("--manuscript", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--figures", help="directory holding figure<N>_*.png")
    parser.add_argument("--title", default="ChampHLA manuscript")
    parser.add_argument(
        "--note", action="append", default=[],
        help="a line of the draft notice; repeat for several lines")
    parser.add_argument(
        "--keep-result-tags", action="store_true",
        help="leave [RESULT:...] provenance tags in the rendered text")
    args = parser.parse_args(argv)
    from .submission import render_docx, validate_docx_parity
    strip = not args.keep_result_tags
    result = render_docx(args.manuscript, args.output, figures_dir=args.figures,
                         strip_result_tags=strip, header_note=args.note, title=args.title)
    parity = validate_docx_parity(args.manuscript, args.output,
                                  figures_dir=args.figures, strip_result_tags=strip)
    print(f"wrote {args.output}")
    print(f"  blocks={result['blocks']} figures_embedded={result['figures_embedded']} "
          f"result_tags_stripped={result['result_tags_stripped']}")
    print(f"  sha256={result['sha256']}")
    print(f"  parity text={parity['text_parity']} figures={parity['figure_order_valid']} "
          f"blocks_compared={parity['blocks_compared']}")
    for failure in parity["failures"]:
        print(f"  FAILURE: {failure}")
    return 0 if not parity["failures"] else 2


def build_drive_docx_main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Render the manuscript and supplement as one shareable DOCX")
    parser.add_argument("--manuscript", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--supplementary", help="rendered as a nested appendix")
    parser.add_argument("--figures", help="directory holding figure<N>_*.png")
    parser.add_argument("--title", default="ChampHLA manuscript")
    parser.add_argument(
        "--note", action="append", default=[],
        help="a line of the draft notice; repeat for several lines")
    parser.add_argument(
        "--keep-result-tags", action="store_true",
        help="leave [RESULT:...] provenance tags in the rendered text")
    parser.add_argument(
        "--preface",
        help="markdown note rendered on its own page before the paper "
             "(for example, what changed since the last shared copy)")
    args = parser.parse_args(argv)
    from .drive_document import render_combined_docx
    result = render_combined_docx(
        args.manuscript, args.output, supplementary_path=args.supplementary,
        figures_dir=args.figures, strip_result_tags=not args.keep_result_tags,
        header_note=args.note, title=args.title, preface_path=args.preface)
    print(f"wrote {args.output}")
    print(f"  blocks={result['blocks']} figures_embedded={result['figures_embedded']} "
          f"tables={result['tables']} result_tags_stripped={result['result_tags_stripped']}")
    print(f"  figures={', '.join(result['figure_order'])}")
    print(f"  sha256={result['sha256']}")
    return 0


def build_originals_manifest_main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Verify immutable source copies")
    parser.add_argument("--source-map", required=True)
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    result = build_originals_manifest(args.source_map, args.project_root, args.output)
    print(f"originals passed={result['passed']} records={len(result['records'])}")
    return 0 if result["passed"] else 2


def extract_source_manuscript_main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Extract and audit the immutable source DOCX")
    parser.add_argument("--source", required=True)
    parser.add_argument("--text-output", required=True)
    parser.add_argument("--issues-output", required=True)
    parser.add_argument("--summary", required=True)
    args = parser.parse_args(argv)
    write_docx_text(args.source, args.text_output)
    write_source_issue_register(args.source, args.issues_output, args.summary)
    return 0


def build_fimm_exploratory_results_main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Build checksum-gated, de-identified exploratory FIMM results")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args(argv)
    from .fimm import run_fimm_analysis
    status = run_fimm_analysis(args.manifest, args.output_dir)
    print(f"FIMM tier={status.get('tier', '')} status={status['status']} "
          f"numeric_outputs_emitted={status['numeric_outputs_emitted']}")
    for failure in status.get("failures", []):
        print(f"  BLOCKED: {failure}")
    return 0 if status["status"] == "COMPLETE" else 2


def build_1000g_assay_manifest_main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Build truth-blind official WGS/WES/RNA input manifest")
    parser.add_argument("--wgs-index", required=True)
    parser.add_argument("--wes-index", required=True)
    parser.add_argument("--rna-sdrf", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args(argv)
    build_assay_manifest(args.wgs_index, args.wes_index, args.rna_sdrf, args.output, args.manifest)
    return 0


def _main() -> int:
    parser = argparse.ArgumentParser(description="ChampHLA publication recovery utilities")
    subparsers = parser.add_subparsers(dest="command", required=True)
    commands = {
        "build-subject-exposure-ledger": build_subject_exposure_ledger_main,
        "prepare-locked-1000g-truth": prepare_locked_1000g_truth_main,
        "freeze-extension-rosters": freeze_extension_rosters_main,
        "freeze-release-bundle": freeze_release_bundle_main,
        "validate-release-freeze": validate_release_freeze_main,
        "render-manuscript-tables": render_manuscript_tables_main,
        "audit-manuscript-claims": audit_manuscript_claims_main,
        "build-review-docx": build_review_docx_main,
        "build-drive-docx": build_drive_docx_main,
        "build-originals-manifest": build_originals_manifest_main,
        "extract-source-manuscript": extract_source_manuscript_main,
        "build-1000g-assay-manifest": build_1000g_assay_manifest_main,
        "build-fimm-exploratory-results": build_fimm_exploratory_results_main,
    }
    for name in commands:
        subparsers.add_parser(name, add_help=False)
    args, remaining = parser.parse_known_args()
    return commands[args.command](remaining)


if __name__ == "__main__":
    raise SystemExit(_main())
