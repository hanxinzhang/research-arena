#!/usr/bin/env python3
"""Audit Research Arena event-log state order and self-certification risks."""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


FINAL_DECISION_NAMES = {"final_decision.md", "final_decision.json", "summary.md"}
POST_DECISION_ALLOWED_ACTION_FRAGMENTS = {
    "archive",
    "post-decision audit",
    "post decision audit",
    "run-state audit",
    "run state audit",
    "state audit",
    "freeze verification",
    "archive verification",
    "verified archive",
}
SELF_CERTIFYING_EVIDENCE_NAMES = {"final_decision.md", "final_decision.json", "summary.md"}
PRE_DECISION_FREEZE_NAMES = {"pre_decision_freeze_manifest.json"}
LEGACY_FREEZE_NAMES = {"run_freeze_manifest.json"}
POST_DECISION_ARCHIVE_NAMES = {"post_decision_archive_manifest.json"}
POST_DECISION_ALLOWED_RUN_OUTPUT_NAMES = {
    "archive_hygiene_audit.csv",
    "archive_hygiene_audit.json",
    "artifact_authority_audit.csv",
    "artifact_authority_audit.json",
    "event_log.jsonl",
    "post_decision_archive_manifest.json",
    "post_decision_archive_verification.json",
    "run_state_audit.csv",
    "run_state_audit.json",
}


@dataclass
class Finding:
    severity: str
    category: str
    event_line: str
    path: str
    message: str


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


def list_value(event: dict[str, Any], key: str) -> list[str]:
    value = event.get(key, [])
    if isinstance(value, list):
        return [str(item) for item in value]
    if value:
        return [str(value)]
    return []


def is_final_decision_event(event: dict[str, Any], run_id: str) -> bool:
    action = str(event.get("action", "")).lower()
    if "final" in action and "decision" in action:
        return True
    for output in list_value(event, "output_artifacts"):
        normalized = output.removeprefix("./")
        if normalized.startswith(f"runs/{run_id}/") and Path(normalized).name in FINAL_DECISION_NAMES:
            return True
    return False


def is_research_mutation_event(event: dict[str, Any], run_id: str) -> bool:
    action = str(event.get("action", "")).lower()
    outputs = [output.removeprefix("./") for output in list_value(event, "output_artifacts")]
    if not outputs and any(fragment in action for fragment in POST_DECISION_ALLOWED_ACTION_FRAGMENTS):
        return False
    for normalized in outputs:
        if normalized == f"runs/{run_id}/event_log.jsonl":
            continue
        if normalized.startswith(f"runs/{run_id}/") and Path(normalized).name in POST_DECISION_ALLOWED_RUN_OUTPUT_NAMES:
            continue
        if normalized.startswith((f"submissions/{run_id}/", f"agents/", f"human_readable_outputs/{run_id}/", f"work_packets/{run_id}/")):
            return True
        if normalized.startswith(f"runs/{run_id}/"):
            return True
    return False


def event_mentions_freeze(event: dict[str, Any], run_id: str) -> bool:
    text = " ".join(
        [
            str(event.get("action", "")),
            str(event.get("reason", "")),
            " ".join(list_value(event, "input_artifacts")),
            " ".join(list_value(event, "output_artifacts")),
        ]
    )
    return any(f"runs/{run_id}/{name}" in text or name in text for name in PRE_DECISION_FREEZE_NAMES)


def event_mentions_legacy_freeze(event: dict[str, Any], run_id: str) -> bool:
    text = " ".join(
        [
            str(event.get("action", "")),
            str(event.get("reason", "")),
            " ".join(list_value(event, "input_artifacts")),
            " ".join(list_value(event, "output_artifacts")),
        ]
    )
    return any(f"runs/{run_id}/{name}" in text or name in text for name in LEGACY_FREEZE_NAMES)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_json_rows(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    if isinstance(payload, dict):
        rows = payload.get("rows") or payload.get("verification_matrix") or payload.get("issues")
        if isinstance(rows, list):
            return [row for row in rows if isinstance(row, dict)]
    return []


def audit_self_certification(root: Path, run_id: str) -> list[Finding]:
    findings: list[Finding] = []
    submissions_root = root / "submissions" / run_id
    for matrix in sorted(submissions_root.glob("submission_*/revision_*/verification_matrix.*")):
        try:
            rows = read_csv(matrix) if matrix.suffix == ".csv" else read_json_rows(matrix)
        except Exception as exc:
            findings.append(
                Finding(
                    "major",
                    "verification_matrix",
                    "",
                    rel(matrix, root),
                    f"Could not parse verification matrix: {exc}.",
                )
            )
            continue
        for idx, row in enumerate(rows, start=1):
            evidence = str(row.get("evidence_path", "") or row.get("evidence", ""))
            names = {Path(part.strip()).name for part in evidence.replace(",", ";").split(";") if part.strip()}
            if names & SELF_CERTIFYING_EVIDENCE_NAMES:
                findings.append(
                    Finding(
                        "major",
                        "self_certification",
                        "",
                        rel(matrix, root),
                        f"Row {idx} cites final editorial artifact(s) {sorted(names & SELF_CERTIFYING_EVIDENCE_NAMES)} as issue-resolution evidence; revision artifacts must not certify themselves by relying on future final decisions.",
                    )
                )
    return findings


def audit(root: Path, run_id: str) -> list[Finding]:
    findings: list[Finding] = []
    events = read_event_log(root, run_id)
    event_log = root / "runs" / run_id / "event_log.jsonl"
    if not events:
        findings.append(
            Finding(
                "major",
                "event_log",
                "",
                rel(event_log, root),
                "Event log is missing or empty.",
            )
        )
        findings.extend(audit_self_certification(root, run_id))
        return findings

    final_lines = [int(event["_line"]) for event in events if is_final_decision_event(event, run_id)]
    if len(final_lines) > 1:
        findings.append(
            Finding(
                "major",
                "state_order",
                ",".join(str(line) for line in final_lines),
                rel(event_log, root),
                "Multiple final-decision events are recorded. Reopen events must be explicit, and stale final decisions must be invalidated.",
            )
        )
    if final_lines:
        first_final = min(final_lines)
        for event in events:
            line = int(event["_line"])
            if line <= first_final:
                continue
            if is_research_mutation_event(event, run_id):
                findings.append(
                    Finding(
                        "blocking",
                        "state_order",
                        str(line),
                        rel(event_log, root),
                        "Research, review, audit, package, or run artifact was written after a final decision. Reopen the run explicitly or discard the stale decision.",
                    )
                )

        final_event = next(event for event in events if int(event["_line"]) == first_final)
        if not event_mentions_freeze(final_event, run_id):
            legacy_note = " It cites only legacy `run_freeze_manifest.json`; current framework runs must create and cite the pre-decision freeze." if event_mentions_legacy_freeze(final_event, run_id) else ""
            findings.append(
                Finding(
                    "major",
                    "freeze",
                    str(first_final),
                    rel(event_log, root),
                    "Final decision event does not cite `runs/<run-id>/pre_decision_freeze_manifest.json` as an input. Freeze the evidence package before editorial decision."
                    + legacy_note,
            )
        )
    else:
        findings.append(
            Finding(
                "minor",
                "state_order",
                "",
                rel(event_log, root),
                "No final-decision event found. This is acceptable for an unfinished run.",
            )
        )

    run_dir = root / "runs" / run_id
    freeze_paths = [run_dir / name for name in PRE_DECISION_FREEZE_NAMES]
    if final_lines and not any(path.is_file() for path in freeze_paths):
        findings.append(
            Finding(
                "major",
                "freeze",
                "",
                rel(run_dir / "pre_decision_freeze_manifest.json", root),
                "Run has a final decision but no pre-decision freeze manifest.",
            )
        )

    if final_lines and not any((run_dir / name).is_file() for name in POST_DECISION_ARCHIVE_NAMES):
        findings.append(
            Finding(
                "minor",
                "archive",
                "",
                rel(run_dir / "post_decision_archive_manifest.json", root),
                "Run has a final decision but no post-decision archive manifest yet. Create it with `python tools/freeze_run.py <run-id> --stage post-decision` after the final event log entry.",
            )
        )

    findings.extend(audit_self_certification(root, run_id))
    return findings


def write_csv(path: Path, findings: list[Finding]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["severity", "category", "event_line", "path", "message"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for finding in findings:
            writer.writerow(asdict(finding))


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Research Arena run state order and self-certification.")
    parser.add_argument("run_id", help="Run id under runs/<run_id>.")
    parser.add_argument("--root", default=".", help="Research Arena repository root.")
    parser.add_argument("--output-json", help="Optional JSON output path.")
    parser.add_argument("--output-csv", help="Optional CSV output path.")
    parser.add_argument("--write-default", action="store_true", help="Write runs/<run_id>/run_state_audit.json and .csv.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    findings = audit(root, args.run_id)
    blocking_or_major = [row for row in findings if row.severity in {"blocking", "major"}]
    payload = {
        "run_id": args.run_id,
        "clerk_type": "run_state_order",
        "scientific_judgment": "not_evaluated",
        "status": "flagged" if blocking_or_major else "pass",
        "finding_count": len(findings),
        "blocking_or_major_count": len(blocking_or_major),
        "notes": [
            "This clerk checks event-log order, freeze presence, and verification self-certification risk.",
            "A final decision should be the last research-mutating event unless the run is explicitly reopened.",
        ],
        "findings": [asdict(row) for row in findings],
    }

    output_json = Path(args.output_json) if args.output_json else None
    output_csv = Path(args.output_csv) if args.output_csv else None
    if args.write_default:
        output_json = root / "runs" / args.run_id / "run_state_audit.json"
        output_csv = root / "runs" / args.run_id / "run_state_audit.csv"

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
