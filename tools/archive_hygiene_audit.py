#!/usr/bin/env python3
"""Audit Research Arena run archives for transient or local-machine files."""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


BLOCKED_NAMES = {
    ".DS_Store",
    "__pycache__",
    ".ipynb_checkpoints",
    ".pytest_cache",
}

BLOCKED_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".tmp",
    ".bak",
    ".swp",
}


@dataclass
class Finding:
    severity: str
    category: str
    path: str
    message: str


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def candidate_roots(root: Path, run_id: str) -> list[Path]:
    return [
        root / "runs" / run_id,
        root / "submissions" / run_id,
        root / "human_readable_outputs" / run_id,
        root / "work_packets" / run_id,
        root / "outputs" / run_id,
        root / "agents" / "study_design_board" / "workspace" / run_id,
        root / "agents" / "integrity_checker" / "workspace" / run_id,
        root / "agents" / "editor_publisher" / "workspace" / run_id,
        *sorted(root.glob(f"agents/referee_*/workspace/{run_id}")),
        *sorted(root.glob(f"agents/researcher_*/workspace/{run_id}")),
    ]


def is_blocked(path: Path) -> bool:
    return path.name in BLOCKED_NAMES or path.suffix.lower() in BLOCKED_SUFFIXES


def audit(root: Path, run_id: str) -> list[Finding]:
    findings: list[Finding] = []
    for base in candidate_roots(root, run_id):
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if not is_blocked(path):
                continue
            findings.append(
                Finding(
                    "major",
                    "archive_hygiene",
                    rel(path, root),
                    "Archive contains a transient, cache, local-machine, or editor-generated file. Remove it before final archive.",
                )
            )
    return findings


def write_csv(path: Path, findings: list[Finding]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["severity", "category", "path", "message"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for finding in findings:
            writer.writerow(asdict(finding))


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Research Arena archive hygiene.")
    parser.add_argument("run_id", help="Run id under runs/<run_id>.")
    parser.add_argument("--root", default=".", help="Research Arena repository root.")
    parser.add_argument("--output-json", help="Optional JSON output path.")
    parser.add_argument("--output-csv", help="Optional CSV output path.")
    parser.add_argument("--write-default", action="store_true", help="Write runs/<run_id>/archive_hygiene_audit.json and .csv.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    findings = audit(root, args.run_id)
    blocking_or_major = [row for row in findings if row.severity in {"blocking", "major"}]
    payload: dict[str, Any] = {
        "run_id": args.run_id,
        "clerk_type": "archive_hygiene",
        "scientific_judgment": "not_evaluated",
        "status": "flagged" if blocking_or_major else "pass",
        "finding_count": len(findings),
        "blocking_or_major_count": len(blocking_or_major),
        "notes": [
            "This clerk checks the run archive for transient files only.",
            "A pass does not prove scientific adequacy; it only means the archive is free of common local-machine/cache artifacts.",
        ],
        "findings": [asdict(row) for row in findings],
    }

    output_json = Path(args.output_json) if args.output_json else None
    output_csv = Path(args.output_csv) if args.output_csv else None
    if args.write_default:
        output_json = root / "runs" / args.run_id / "archive_hygiene_audit.json"
        output_csv = root / "runs" / args.run_id / "archive_hygiene_audit.csv"

    if output_json:
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))

    if output_csv:
        write_csv(output_csv, findings)
    return 2 if blocking_or_major else 0


if __name__ == "__main__":
    raise SystemExit(main())
