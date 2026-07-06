#!/usr/bin/env python3
"""Audit Research Arena runs for central scripted-generation risk.

This deterministic clerk looks for two process risks:

1. code files outside the framework tools that appear to write artifacts for
   several roles; and
2. event-log bursts where many role actions happen at the same timestamp.

It does not decide whether the scientific content is adequate.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


CODE_SUFFIXES = {".py", ".sh", ".bash", ".zsh", ".ipynb"}
SKIP_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    ".ipynb_checkpoints",
    ".venv",
    "venv",
    "env",
    "node_modules",
}
SKIP_PREFIXES = {
    "tools",
    "agents/templates",
    "assets/fonts",
    "assets/brand",
}
ROLE_PATTERNS = {
    "researcher_submission": [
        r"submissions/",
        r"revision_00",
        r"revision_0[1-9]",
        r"manuscript\.md",
        r"results\.json",
        r"analysis\.py",
        r"verification_matrix",
        r"revision_response",
    ],
    "study_design_board": [
        r"study_design_board",
        r"proposal_gate_summary",
        r"proposal_review",
        r"approve_for_analysis",
        r"downgrade_article_type",
    ],
    "referee": [
        r"agents/referee_",
        r"review_round_\d+",
        r"\bR[1-9]-",
        r"reviewer\s+quality",
    ],
    "integrity_checker": [
        r"integrity_checker",
        r"integrity_report",
        r"reproducibility",
        r"rerun",
        r"issue_ledger",
    ],
    "editor": [
        r"editor_publisher",
        r"final_decision",
        r"reject all",
        r"accepted_submission",
        r"publication_status",
    ],
    "llm_auditor": [
        r"scientific_depth_review",
        r"revision_trajectory_review",
        r"novelty_article_fit_review",
        r"reviewer_quality_review",
        r"manuscript_article_voice_review",
        r"display_item_narrative_review",
        r"display_item_grouping_review",
        r"display_program_independence_review",
    ],
}
WRITE_HINTS = [
    ".write_text",
    ".write_bytes",
    "open(",
    "json.dump",
    "to_csv(",
    "to_excel(",
    "mkdir(",
    "copyfile",
    "shutil.copy",
]


@dataclass
class Finding:
    severity: str
    category: str
    path: str
    message: str
    evidence: str


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def read_event_log(root: Path, run_id: str) -> list[dict[str, Any]]:
    path = root / "runs" / run_id / "event_log.jsonl"
    events: list[dict[str, Any]] = []
    if not path.is_file():
        return events
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                payload = {"action": "unparseable_event", "raw": line}
            if isinstance(payload, dict):
                payload["_line"] = line_number
                events.append(payload)
    return events


def should_skip(path: Path, root: Path) -> bool:
    relative = rel(path, root)
    if any(part in SKIP_PARTS for part in path.parts):
        return True
    return any(relative == prefix or relative.startswith(prefix + "/") for prefix in SKIP_PREFIXES)


def iter_code_files(root: Path, run_id: str) -> list[Path]:
    candidates: list[Path] = []
    for base in [root / "scripts", root / "runs" / run_id, root / "submissions" / run_id, root]:
        if not base.exists():
            continue
        if base == root:
            direct_files = [path for path in base.iterdir() if path.is_file()]
            candidates.extend(path for path in direct_files if path.suffix in CODE_SUFFIXES)
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.suffix in CODE_SUFFIXES and not should_skip(path, root):
                candidates.append(path)
    return sorted(set(candidates))


def compact_text(path: Path) -> str:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    if path.suffix == ".ipynb":
        try:
            payload = json.loads(raw)
            pieces: list[str] = []
            for cell in payload.get("cells", []):
                source = cell.get("source", [])
                pieces.append("".join(source) if isinstance(source, list) else str(source))
            raw = "\n".join(pieces)
        except Exception:
            pass
    return raw


def role_classes(text: str) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    lowered = text.lower()
    for role_class, patterns in ROLE_PATTERNS.items():
        hits = [pattern for pattern in patterns if re.search(pattern, lowered, flags=re.IGNORECASE)]
        if hits:
            found[role_class] = hits
    return found


def sample_lines(text: str, patterns: list[str], limit: int = 4) -> list[str]:
    samples: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if any(re.search(pattern, stripped, flags=re.IGNORECASE) for pattern in patterns):
            samples.append(stripped[:220])
        if len(samples) >= limit:
            break
    return samples


def audit_code_files(root: Path, run_id: str) -> list[Finding]:
    findings: list[Finding] = []
    for path in iter_code_files(root, run_id):
        text = compact_text(path)
        classes = role_classes(text)
        if len(classes) < 2:
            continue
        write_count = sum(1 for hint in WRITE_HINTS if hint in text)
        all_patterns = [pattern for patterns in classes.values() for pattern in patterns]
        samples = sample_lines(text, all_patterns)
        if len(classes) >= 3 and write_count:
            findings.append(
                Finding(
                    "major",
                    "central_script",
                    rel(path, root),
                    "Code file appears to combine write logic or artifact paths for multiple Research Arena roles. Use separate agent turns or work packets instead of a central role-output generator.",
                    json.dumps({"role_classes": sorted(classes), "write_hint_count": write_count, "samples": samples}, sort_keys=True),
                )
            )
        elif len(classes) >= 2 and write_count:
            findings.append(
                Finding(
                    "minor",
                    "mixed_role_script",
                    rel(path, root),
                    "Code file mentions writable artifacts for more than one role. Inspect manually to ensure it is only orchestration or analysis, not scripted role generation.",
                    json.dumps({"role_classes": sorted(classes), "write_hint_count": write_count, "samples": samples}, sort_keys=True),
                )
            )
    return findings


def audit_event_bursts(root: Path, run_id: str) -> list[Finding]:
    findings: list[Finding] = []
    events = read_event_log(root, run_id)
    if not events:
        findings.append(
            Finding(
                "minor",
                "event_log",
                f"runs/{run_id}/event_log.jsonl",
                "Event log is missing or empty, so scripted-generation timing could not be audited.",
                "",
            )
        )
        return findings

    by_time: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_agent: dict[str, set[str]] = defaultdict(set)
    for event in events:
        time = str(event.get("time", "")).strip() or "<missing>"
        by_time[time].append(event)
        agent = str(event.get("agent", "")).strip()
        role = str(event.get("role", "")).strip()
        if agent and role:
            by_agent[agent].add(role)

    for time, rows in sorted(by_time.items()):
        roles = {str(row.get("role", "")).strip() for row in rows if row.get("role")}
        agents = {str(row.get("agent", "")).strip() for row in rows if row.get("agent")}
        if len(rows) >= 6 and len(roles) >= 3:
            findings.append(
                Finding(
                    "major",
                    "timestamp_burst",
                    f"runs/{run_id}/event_log.jsonl",
                    "Many events across several roles have the same timestamp. This can indicate a scripted batch rather than sequential role interaction.",
                    json.dumps({"time": time, "event_count": len(rows), "roles": sorted(roles), "agents": sorted(agents)}, sort_keys=True),
                )
            )

    for agent, roles in sorted(by_agent.items()):
        if agent in {"orchestrator", "codex", "assistant"} and len(roles) >= 3:
            findings.append(
                Finding(
                    "minor",
                    "single_actor_many_roles",
                    f"runs/{run_id}/event_log.jsonl",
                    "One logged actor appears across many roles. This is allowed for a file-aware LLM run only if each role turn used separate inputs and produced independent reasoning.",
                    json.dumps({"agent": agent, "roles": sorted(roles)}, sort_keys=True),
                )
            )
    return findings


def write_csv(path: Path, findings: list[Finding]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["severity", "category", "path", "message", "evidence"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for finding in findings:
            writer.writerow(asdict(finding))


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit central scripted-generation risk for a Research Arena run.")
    parser.add_argument("run_id", help="Run id under runs/<run_id>.")
    parser.add_argument("--root", default=".", help="Research Arena repository root.")
    parser.add_argument("--output-json", help="Optional JSON output path.")
    parser.add_argument("--output-csv", help="Optional CSV output path.")
    parser.add_argument("--write-default", action="store_true", help="Write runs/<run_id>/scripted_generation_audit.json and .csv.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    findings = audit_code_files(root, args.run_id) + audit_event_bursts(root, args.run_id)
    blocking_or_major = [row for row in findings if row.severity in {"blocking", "major"}]
    payload = {
        "run_id": args.run_id,
        "clerk_type": "scripted_generation_risk",
        "scientific_judgment": "not_evaluated",
        "status": "flagged" if blocking_or_major else "pass",
        "finding_count": len(findings),
        "blocking_or_major_count": len(blocking_or_major),
        "notes": [
            "This clerk flags process-risk evidence only.",
            "A pass does not prove that reviews or editorial judgments were independent.",
            "Major findings block acceptance until the Editor or Integrity Checker resolves them in writing.",
        ],
        "findings": [asdict(row) for row in findings],
    }

    output_json = Path(args.output_json) if args.output_json else None
    output_csv = Path(args.output_csv) if args.output_csv else None
    if args.write_default:
        output_json = root / "runs" / args.run_id / "scripted_generation_audit.json"
        output_csv = root / "runs" / args.run_id / "scripted_generation_audit.csv"

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
