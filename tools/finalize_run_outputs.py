#!/usr/bin/env python3
"""Build a clean final Research Arena run output bundle.

The active workflow writes to several roots while agents generate, review, audit,
and decide a run. This tool creates one handoff folder:

outputs/<run-id>/
  human_readable_outputs/
  diagnosis_process_files/

By default, source workflow folders are copied and left in place. Pass
`--cleanup-source-roots` after a verified bundle is built when the desired final
state is a single `outputs/<run-id>/` folder.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SKIP_NAMES = {
    ".DS_Store",
    "__pycache__",
    ".ipynb_checkpoints",
    ".pytest_cache",
}

SKIP_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".tmp",
    ".bak",
    ".swp",
}

HUMAN_READABLE_MACHINE_NAMES = {
    "index.json",
    "human_readable_package_manifest.json",
    "article_build_report.json",
}

RUN_OVERVIEW_FILES = [
    "final_decision.md",
    "summary.md",
    "proposal_gate_summary.md",
    "integrity_report.md",
]

MANIFEST_NAME = "final_output_manifest.json"
VERIFICATION_NAME = "final_output_verification.json"

TEXT_SANITIZE_SUFFIXES = {
    ".csv",
    ".html",
    ".json",
    ".log",
    ".md",
    ".tex",
    ".tsv",
    ".txt",
    ".yaml",
    ".yml",
}


@dataclass
class CopiedItem:
    category: str
    source: str
    destination: str
    bytes: int
    sha256: str


@dataclass
class SkippedItem:
    source: str
    reason: str


def rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sanitize_text_file(path: Path, root: Path) -> None:
    if path.suffix.lower() not in TEXT_SANITIZE_SUFFIXES:
        return
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return

    replacements = [
        (root.resolve().as_posix(), "<research_arena_root>"),
        ((root.parent / "required tools").resolve().as_posix(), "<required_tools>"),
        (Path.home().resolve().as_posix(), "<home>"),
    ]
    replacements = sorted(set(replacements), key=lambda item: len(item[0]), reverse=True)
    for source, replacement in replacements:
        if source:
            text = text.replace(source, replacement)
    text = re.sub(r"/private/var/folders/[^\s\"']+", "<local_temp>", text)
    text = re.sub(r"/var/folders/[^\s\"']+", "<local_temp>", text)
    text = re.sub(r"/private/tmp/[^\s\"']+", "<local_temp>", text)
    text = re.sub(r"/tmp/[^\s\"']+", "<local_temp>", text)
    path.write_text(text, encoding="utf-8")


def is_skipped(path: Path, skip_human_machine_metadata: bool = False) -> bool:
    if any(part in SKIP_NAMES or part.startswith(".") for part in path.parts) or path.suffix.lower() in SKIP_SUFFIXES:
        return True
    return skip_human_machine_metadata and path.name in HUMAN_READABLE_MACHINE_NAMES


def copy_file(source: Path, destination: Path, category: str, root: Path) -> CopiedItem:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    sanitize_text_file(destination, root)
    return CopiedItem(
        category=category,
        source=rel(source, root),
        destination=rel(destination, root),
        bytes=destination.stat().st_size,
        sha256=sha256(destination),
    )


def copy_tree(
    source_dir: Path,
    destination_dir: Path,
    category: str,
    root: Path,
    skip_human_machine_metadata: bool = False,
) -> tuple[list[CopiedItem], list[SkippedItem]]:
    copied: list[CopiedItem] = []
    skipped: list[SkippedItem] = []
    if not source_dir.is_dir():
        return copied, skipped
    destination_dir.mkdir(parents=True, exist_ok=True)
    for source in sorted(path for path in source_dir.rglob("*") if path.is_file()):
        relative_source = source.relative_to(source_dir)
        if is_skipped(relative_source, skip_human_machine_metadata):
            reason = (
                "machine-readable package metadata omitted from human-readable handoff"
                if skip_human_machine_metadata and relative_source.name in HUMAN_READABLE_MACHINE_NAMES
                else "transient, hidden, cache, or editor-generated file"
            )
            skipped.append(SkippedItem(rel(source, root), reason))
            continue
        destination = destination_dir / relative_source
        copied.append(copy_file(source, destination, category, root))
    return copied, skipped


def copy_optional_tree(
    source_dir: Path,
    destination_dir: Path,
    category: str,
    root: Path,
    missing: list[str],
    skipped: list[SkippedItem],
    skip_human_machine_metadata: bool = False,
) -> list[CopiedItem]:
    if not source_dir.exists():
        missing.append(rel(source_dir, root))
        return []
    copied, tree_skipped = copy_tree(source_dir, destination_dir, category, root, skip_human_machine_metadata)
    skipped.extend(tree_skipped)
    return copied


def agent_workspace_roots(root: Path, run_id: str) -> list[tuple[Path, Path]]:
    roots: list[tuple[Path, Path]] = []
    for workspace in sorted(root.glob(f"agents/*/workspace/{run_id}")):
        if not workspace.is_dir():
            continue
        agent_id = workspace.parents[1].name
        roots.append((workspace, Path("agent_workspaces") / agent_id))
    return roots


def remove_transient_items(folder: Path) -> list[str]:
    removed: list[str] = []
    if not folder.exists():
        return removed
    for path in sorted(folder.rglob("*"), key=lambda item: len(item.parts), reverse=True):
        if path.name in SKIP_NAMES or path.suffix.lower() in SKIP_SUFFIXES:
            if path.is_dir():
                shutil.rmtree(path)
            elif path.is_file():
                path.unlink()
            removed.append(str(path))
    return removed


def cleanup_source_roots(root: Path, run_id: str, output_dir: Path) -> dict[str, Any]:
    output_dir = output_dir.resolve()
    removed: list[str] = []
    skipped: list[str] = []
    candidates: list[Path] = [
        root / "runs" / run_id,
        root / "submissions" / run_id,
        root / "human_readable_outputs" / run_id,
        root / "work_packets" / run_id,
    ]
    candidates.extend(root.glob(f"agents/*/workspace/{run_id}"))

    for path in sorted({candidate.resolve() for candidate in candidates}):
        if not path.exists():
            continue
        if path == output_dir or output_dir in path.parents:
            skipped.append(rel(path, root) + " (inside final output folder)")
            continue
        if root.resolve() not in [path, *path.parents]:
            skipped.append(rel(path, root) + " (outside repository root)")
            continue
        shutil.rmtree(path)
        removed.append(rel(path, root))

    parent_roots = [
        root / "runs",
        root / "submissions",
        root / "human_readable_outputs",
        root / "work_packets",
        *sorted(root.glob("agents/*/workspace")),
    ]
    for path in parent_roots:
        remove_transient_items(path)

    pruned_empty_roots: list[str] = []
    for path in parent_roots:
        if path.is_dir() and not any(path.iterdir()):
            path.rmdir()
            pruned_empty_roots.append(rel(path, root))

    return {
        "status": "complete" if not skipped else "partial",
        "removed": removed,
        "removed_count": len(removed),
        "pruned_empty_roots": pruned_empty_roots,
        "pruned_empty_root_count": len(pruned_empty_roots),
        "skipped": skipped,
        "skipped_count": len(skipped),
    }


def update_manifest_with_cleanup(output_dir: Path, root: Path, cleanup: dict[str, Any]) -> dict[str, Any]:
    manifest_path = output_dir / MANIFEST_NAME
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["source_cleanup"] = cleanup
    manifest.setdefault("source_cleanup_history", []).append(cleanup)
    manifest.setdefault("notes", []).append(
        "Run-specific source workflow folders were removed after the final output bundle verified successfully."
    )
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    verification = verify_bundle(root, manifest_path)
    (output_dir / VERIFICATION_NAME).write_text(json.dumps(verification, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def write_readme(output_dir: Path, run_id: str, root: Path) -> CopiedItem:
    readme = output_dir / "README.md"
    text = f"""# Research Arena Final Output Bundle

Run id: `{run_id}`

Start with `human_readable_outputs/`. It contains the final decision, run summary,
article PDFs, manuscript PDFs, figures, tables, and source code intended for
normal reading. Machine-readable package manifests are intentionally omitted
from this reader-facing area.

Use `diagnosis_process_files/` only when auditing how the run was produced. It
contains run records, submitted revisions, work packets, and role workspaces.

## Folder Layout

```text
human_readable_outputs/
  run_overview/
  <submission>/<revision>/
diagnosis_process_files/
  run_records/
  submitted_revisions/
  work_packets/
  agent_workspaces/
final_output_manifest.json
final_output_verification.json
```

This bundle is a post-decision handoff view. It does not rewrite scientific
claims, reviewer judgments, or editor decisions; it only separates reading
artifacts from process and diagnosis files.
"""
    readme.write_text(text, encoding="utf-8")
    return CopiedItem(
        category="bundle_readme",
        source=rel(readme, root),
        destination=rel(readme, root),
        bytes=readme.stat().st_size,
        sha256=sha256(readme),
    )


def build_bundle(root: Path, run_id: str, output_dir: Path, replace: bool) -> dict[str, Any]:
    if output_dir.exists():
        if not replace:
            raise SystemExit(f"{rel(output_dir, root)} already exists; pass --replace to rebuild it.")
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    copied: list[CopiedItem] = []
    skipped: list[SkippedItem] = []
    missing: list[str] = []

    human_dir = output_dir / "human_readable_outputs"
    diagnosis_dir = output_dir / "diagnosis_process_files"

    copied.append(write_readme(output_dir, run_id, root))

    run_dir = root / "runs" / run_id
    overview_dir = human_dir / "run_overview"
    if run_dir.is_dir():
        for name in RUN_OVERVIEW_FILES:
            source = run_dir / name
            if source.is_file():
                copied.append(copy_file(source, overview_dir / name, "run_overview", root))
    else:
        missing.append(rel(run_dir, root))

    copied.extend(
        copy_optional_tree(
            root / "human_readable_outputs" / run_id,
            human_dir,
            "human_readable_output",
            root,
            missing,
            skipped,
            skip_human_machine_metadata=True,
        )
    )

    diagnosis_roots = [
        (root / "runs" / run_id, diagnosis_dir / "run_records", "run_record"),
        (root / "submissions" / run_id, diagnosis_dir / "submitted_revisions", "submitted_revision"),
        (root / "work_packets" / run_id, diagnosis_dir / "work_packets", "work_packet"),
    ]
    for source_dir, destination_dir, category in diagnosis_roots:
        copied.extend(copy_optional_tree(source_dir, destination_dir, category, root, missing, skipped))

    agent_roots = agent_workspace_roots(root, run_id)
    if not agent_roots:
        missing.append(rel(root / "agents" / "*" / "workspace" / run_id, root))
    for source_dir, relative_destination in agent_roots:
        copied.extend(
            copy_optional_tree(
                source_dir,
                diagnosis_dir / relative_destination,
                "agent_workspace",
                root,
                missing,
                skipped,
            )
        )

    remove_transient_items(output_dir)

    manifest = {
        "run_id": run_id,
        "manifest_type": "research_arena_final_output_bundle",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "output_folder": rel(output_dir, root),
        "layout": {
            "human_readable_outputs": rel(human_dir, root),
            "diagnosis_process_files": rel(diagnosis_dir, root),
        },
        "status": "complete" if not missing else "incomplete",
        "copied_item_count": len(copied),
        "skipped_item_count": len(skipped),
        "missing_expected_roots": missing,
        "copied_items": [asdict(item) for item in copied],
        "skipped_items": [asdict(item) for item in skipped],
        "notes": [
            "The bundle separates final reading artifacts from diagnosis and process files.",
            "Source workflow folders are copied first; pass --cleanup-source-roots to remove run-specific source folders after verification.",
            "Machine-readable package manifests are omitted from human_readable_outputs and retained only through the final manifest or diagnosis files.",
            "Transient/cache/editor files are skipped.",
        ],
    }
    manifest_path = output_dir / MANIFEST_NAME
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    verification = verify_bundle(root, manifest_path)
    (output_dir / VERIFICATION_NAME).write_text(json.dumps(verification, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def verify_bundle(root: Path, manifest_path: Path) -> dict[str, Any]:
    remove_transient_items(manifest_path.parent)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    missing: list[str] = []
    mismatches: list[dict[str, str]] = []
    for item in manifest.get("copied_items", []):
        destination = root / str(item.get("destination", ""))
        expected = str(item.get("sha256", ""))
        if not destination.is_file():
            missing.append(str(item.get("destination", "")))
            continue
        observed = sha256(destination)
        if observed != expected:
            mismatches.append(
                {
                    "path": str(item.get("destination", "")),
                    "expected_sha256": expected,
                    "observed_sha256": observed,
                }
            )
    return {
        "run_id": manifest.get("run_id"),
        "manifest": rel(manifest_path, root),
        "verified_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "pass" if not missing and not mismatches else "flagged",
        "missing_count": len(missing),
        "mismatch_count": len(mismatches),
        "missing": missing,
        "mismatches": mismatches,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build or verify a clean final Research Arena output bundle.")
    parser.add_argument("run_id", help="Run id.")
    parser.add_argument("--root", default=".", help="Root containing runs/, submissions/, human_readable_outputs/, work_packets/, and agents/.")
    parser.add_argument("--output-dir", help="Final output folder. Defaults to outputs/<run-id> under --root.")
    parser.add_argument("--replace", action="store_true", help="Replace an existing final output folder.")
    parser.add_argument("--verify", action="store_true", help="Verify an existing final output bundle instead of rebuilding it.")
    parser.add_argument(
        "--cleanup-source-roots",
        action="store_true",
        help=(
            "After the final output bundle verifies successfully, remove run-specific source roots "
            "from runs/, submissions/, human_readable_outputs/, work_packets/, and agent workspaces."
        ),
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    output_dir = Path(args.output_dir) if args.output_dir else root / "outputs" / args.run_id
    if not output_dir.is_absolute():
        output_dir = root / output_dir
    output_dir = output_dir.resolve()

    if args.verify:
        manifest_path = output_dir / MANIFEST_NAME
        if not manifest_path.is_file():
            raise SystemExit(f"Missing final output manifest: {rel(manifest_path, root)}")
        verification = verify_bundle(root, manifest_path)
        (output_dir / VERIFICATION_NAME).write_text(json.dumps(verification, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if args.cleanup_source_roots and verification["status"] == "pass":
            cleanup = cleanup_source_roots(root, args.run_id, output_dir)
            update_manifest_with_cleanup(output_dir, root, cleanup)
            print(
                f"source_cleanup {cleanup['status']} "
                f"{cleanup['removed_count']} removed {cleanup['pruned_empty_root_count']} empty roots"
            )
        print(f"{verification['status']} {verification['mismatch_count']} {verification['missing_count']}")
        return 2 if verification["status"] != "pass" else 0

    manifest = build_bundle(root, args.run_id, output_dir, args.replace)
    if args.cleanup_source_roots:
        verification = verify_bundle(root, output_dir / MANIFEST_NAME)
        if verification["status"] != "pass":
            (output_dir / VERIFICATION_NAME).write_text(json.dumps(verification, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            raise SystemExit("Final output bundle did not verify; source roots were not removed.")
        cleanup = cleanup_source_roots(root, args.run_id, output_dir)
        manifest = update_manifest_with_cleanup(output_dir, root, cleanup)
        print(
            f"source cleanup: {cleanup['status']} "
            f"({cleanup['removed_count']} run-specific roots removed, "
            f"{cleanup['pruned_empty_root_count']} empty roots pruned)"
        )
    print(f"Final output bundle: {manifest['output_folder']}")
    print(f"- copied items: {manifest['copied_item_count']}")
    print(f"- skipped transient items: {manifest['skipped_item_count']}")
    if manifest["missing_expected_roots"]:
        print("- missing expected roots: " + ", ".join(manifest["missing_expected_roots"]))
    return 0 if manifest["status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
