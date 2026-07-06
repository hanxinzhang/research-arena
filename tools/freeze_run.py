#!/usr/bin/env python3
"""Create or verify a Research Arena run freeze manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SKIP_NAMES = {".DS_Store", "__pycache__", ".ipynb_checkpoints"}

PRE_DECISION_MANIFEST = "pre_decision_freeze_manifest.json"
PRE_DECISION_VERIFICATION = "pre_decision_freeze_verification.json"
POST_DECISION_MANIFEST = "post_decision_archive_manifest.json"
POST_DECISION_VERIFICATION = "post_decision_archive_verification.json"

LEGACY_MANIFEST = "run_freeze_manifest.json"
LEGACY_VERIFICATION = "run_freeze_verification.json"

FINAL_DECISION_FILES = {"final_decision.md", "final_decision.json", "summary.md"}

PRE_DECISION_EXCLUDED_RUN_FILES = {
    PRE_DECISION_MANIFEST,
    PRE_DECISION_VERIFICATION,
    POST_DECISION_MANIFEST,
    POST_DECISION_VERIFICATION,
    LEGACY_MANIFEST,
    LEGACY_VERIFICATION,
    "event_log.jsonl",
    "run_state_audit.json",
    "run_state_audit.csv",
    "artifact_authority_audit.json",
    "artifact_authority_audit.csv",
    *FINAL_DECISION_FILES,
}

POST_DECISION_EXCLUDED_RUN_FILES = {
    POST_DECISION_MANIFEST,
    POST_DECISION_VERIFICATION,
}

LEGACY_EXCLUDED_RUN_FILES = {
    LEGACY_MANIFEST,
    LEGACY_VERIFICATION,
    *FINAL_DECISION_FILES,
}


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def should_skip(path: Path) -> bool:
    return any(part in SKIP_NAMES or part.startswith(".") for part in path.parts)


def candidate_roots(root: Path, run_id: str) -> list[Path]:
    return [
        root / "runs" / run_id,
        root / "submissions" / run_id,
        root / "human_readable_outputs" / run_id,
        root / "work_packets" / run_id,
        root / "agents" / "study_design_board" / "workspace" / run_id,
        root / "agents" / "integrity_checker" / "workspace" / run_id,
        root / "agents" / "editor_publisher" / "workspace" / run_id,
        *sorted(root.glob(f"agents/referee_*/workspace/{run_id}")),
        *sorted(root.glob(f"agents/researcher_*/workspace/{run_id}")),
    ]


def excluded_run_files(stage: str, include_decision_files: bool) -> set[str]:
    if stage == "pre-decision":
        excluded = set(PRE_DECISION_EXCLUDED_RUN_FILES)
        if include_decision_files:
            excluded -= FINAL_DECISION_FILES
        return excluded
    if stage == "post-decision":
        return set(POST_DECISION_EXCLUDED_RUN_FILES)
    excluded = set(LEGACY_EXCLUDED_RUN_FILES)
    if include_decision_files:
        excluded -= FINAL_DECISION_FILES
    return excluded


def default_output_name(stage: str) -> str:
    if stage == "pre-decision":
        return PRE_DECISION_MANIFEST
    if stage == "post-decision":
        return POST_DECISION_MANIFEST
    return LEGACY_MANIFEST


def default_verification_name(stage: str) -> str:
    if stage == "pre-decision":
        return PRE_DECISION_VERIFICATION
    if stage == "post-decision":
        return POST_DECISION_VERIFICATION
    return LEGACY_VERIFICATION


def iter_files(root: Path, run_id: str, stage: str, include_decision_files: bool) -> list[Path]:
    run_exclusions = excluded_run_files(stage, include_decision_files)
    files: list[Path] = []
    for base in candidate_roots(root, run_id):
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file():
                continue
            relative_parts = path.relative_to(base).parts
            if should_skip(Path(*relative_parts)):
                continue
            if base == root / "runs" / run_id and path.name in run_exclusions:
                continue
            files.append(path)
    return sorted(set(files))


def build_manifest(root: Path, run_id: str, stage: str, include_decision_files: bool) -> dict[str, Any]:
    items = []
    for path in iter_files(root, run_id, stage, include_decision_files):
        stat = path.stat()
        items.append(
            {
                "path": rel(path, root),
                "sha256": sha256(path),
                "bytes": stat.st_size,
            }
        )
    if stage == "pre-decision":
        manifest_type = "research_arena_pre_decision_freeze"
        notes = [
            "Create this manifest after all review/audit evidence is ready and immediately before the final editorial decision.",
            "`event_log.jsonl`, final-decision files, and mutable event-log-derived post-decision audits are excluded so the act of recording the final decision cannot break this freeze.",
            "The final decision should cite this pre-decision freeze as an input artifact.",
            "Create a post-decision archive manifest after the final decision and final event-log entry are written.",
        ]
    elif stage == "post-decision":
        manifest_type = "research_arena_post_decision_archive"
        notes = [
            "Create this manifest after the final decision and final event-log entry are written.",
            "This archive includes final-decision files and `event_log.jsonl`; it excludes only its own manifest and verification output.",
            "A complete run archive should verify this manifest cleanly.",
        ]
    else:
        manifest_type = "research_arena_run_freeze"
        notes = [
            "Legacy single-manifest mode. Prefer `--stage pre-decision` before final decision and `--stage post-decision` after final decision.",
            "By default, final_decision.md/json and summary.md are excluded so the decision can cite the frozen evidence package.",
        ]
    return {
        "run_id": run_id,
        "manifest_type": manifest_type,
        "manifest_stage": stage,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "include_decision_files": include_decision_files,
        "excluded_run_files": sorted(excluded_run_files(stage, include_decision_files)),
        "scientific_judgment": "not_evaluated",
        "notes": notes,
        "item_count": len(items),
        "items": items,
    }


def verify_manifest(root: Path, manifest_path: Path) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    mismatches = []
    missing = []
    for item in manifest.get("items", []):
        if not isinstance(item, dict):
            continue
        path = root / str(item.get("path", ""))
        expected = str(item.get("sha256", ""))
        if not path.is_file():
            missing.append(str(item.get("path", "")))
            continue
        observed = sha256(path)
        if observed != expected:
            mismatches.append({"path": str(item.get("path", "")), "expected_sha256": expected, "observed_sha256": observed})
    return {
        "run_id": manifest.get("run_id"),
        "manifest": rel(manifest_path, root),
        "manifest_stage": manifest.get("manifest_stage", "legacy"),
        "verified_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "pass" if not missing and not mismatches else "flagged",
        "missing_count": len(missing),
        "mismatch_count": len(mismatches),
        "missing": missing,
        "mismatches": mismatches,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Create or verify a Research Arena freeze or archive manifest.")
    parser.add_argument("run_id", help="Run id under runs/<run_id>.")
    parser.add_argument("--root", default=".", help="Research Arena repository root.")
    parser.add_argument(
        "--stage",
        choices=["pre-decision", "post-decision", "legacy"],
        default="pre-decision",
        help="Manifest stage. Use pre-decision before final decision and post-decision after final decision.",
    )
    parser.add_argument("--output", help="Output manifest path. Defaults to a stage-specific file under runs/<run_id>.")
    parser.add_argument("--include-decision-files", action="store_true", help="Legacy compatibility option. Prefer --stage post-decision after final decision.")
    parser.add_argument("--verify", action="store_true", help="Verify an existing freeze manifest instead of creating one.")
    parser.add_argument("--write-default", action="store_true", help="When verifying, write a stage-specific verification file under runs/<run_id>.")
    args = parser.parse_args()

    if args.include_decision_files and args.stage != "legacy":
        parser.error("--include-decision-files is only valid with --stage legacy; use --stage post-decision after the final decision.")

    root = Path(args.root).resolve()
    output = Path(args.output) if args.output else root / "runs" / args.run_id / default_output_name(args.stage)
    if not output.is_absolute():
        output = root / output

    if args.verify:
        verification = verify_manifest(root, output)
        if args.write_default:
            stage = str(verification.get("manifest_stage") or args.stage)
            verification_path = root / "runs" / args.run_id / default_verification_name(stage)
            verification_path.parent.mkdir(parents=True, exist_ok=True)
            verification_path.write_text(json.dumps(verification, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        else:
            print(json.dumps(verification, indent=2, sort_keys=True))
        return 2 if verification["status"] != "pass" else 0

    manifest = build_manifest(root, args.run_id, args.stage, args.include_decision_files)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote freeze manifest with {manifest['item_count']} item(s): {rel(output, root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
