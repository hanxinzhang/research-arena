#!/usr/bin/env python3
"""Audit whether Research Arena artifacts were written by the proper role.

This deterministic clerk checks event-log output paths against the role that is
allowed to author them. It does not judge scientific adequacy.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class Finding:
    severity: str
    category: str
    event_line: int
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


def researcher_from_submission(path: str, run_id: str) -> str | None:
    match = re.search(rf"^submissions/{re.escape(run_id)}/submission_\d+_(?P<researcher>[^/]+)/", path)
    return match.group("researcher") if match else None


def allowed_authors(path: str, run_id: str) -> tuple[set[str], set[str], str] | None:
    """Return allowed roles, allowed agent ids, and artifact class."""
    if path.startswith(f"submissions/{run_id}/"):
        researcher = researcher_from_submission(path, run_id)
        if researcher:
            return {"researcher"}, {researcher}, "researcher_submission"

    if path.startswith(f"agents/study_design_board/workspace/{run_id}/"):
        return {"study_design_board"}, {"study_design_board"}, "study_design_board_review"

    if path.startswith(f"agents/integrity_checker/workspace/{run_id}/"):
        return {"integrity_checker"}, {"integrity_checker"}, "integrity_report"

    referee_match = re.match(rf"^agents/(referee_\d+)/workspace/{re.escape(run_id)}/", path)
    if referee_match:
        referee = referee_match.group(1)
        return {"referee"}, {referee}, "referee_review"

    if path.startswith(f"agents/editor_publisher/workspace/{run_id}/"):
        return {"editor"}, {"editor_publisher"}, "editorial_workspace"

    if path in {
        f"runs/{run_id}/final_decision.md",
        f"runs/{run_id}/final_decision.json",
        f"runs/{run_id}/summary.md",
    }:
        return {"editor"}, {"editor_publisher"}, "editorial_decision"

    if path in {
        f"runs/{run_id}/proposal_gate_summary.md",
    }:
        return {"study_design_board"}, {"study_design_board"}, "proposal_gate_summary"

    llm_judgment_names = {
        "scientific_depth_review.md",
        "scientific_depth_review.json",
        "revision_trajectory_review.md",
        "revision_trajectory_review.json",
        "novelty_article_fit_review.md",
        "novelty_article_fit_review.json",
        "reviewer_quality_review.md",
        "reviewer_quality_review.json",
        "manuscript_article_voice_review.md",
        "manuscript_article_voice_review.json",
        "display_item_narrative_review.md",
        "display_item_narrative_review.json",
        "display_item_grouping_review.md",
        "display_item_grouping_review.json",
        "display_program_independence_review.md",
        "display_program_independence_review.json",
    }
    if path.startswith(f"runs/{run_id}/") and Path(path).name in llm_judgment_names:
        return {"auditor", "editor"}, {"auditor", "editor_publisher"}, "llm_backed_judgment"

    clerk_names = {
        "research_depth_audit.json",
        "research_depth_audit.csv",
        "review_similarity_audit.json",
        "review_similarity_audit.csv",
        "trajectory_clerk.json",
        "trajectory_clerk.csv",
        "render_toolchain_report.json",
        "artifact_authority_audit.json",
        "artifact_authority_audit.csv",
        "run_state_audit.json",
        "run_state_audit.csv",
        "scripted_generation_audit.json",
        "scripted_generation_audit.csv",
        "archive_hygiene_audit.json",
        "archive_hygiene_audit.csv",
        "pre_decision_freeze_manifest.json",
        "pre_decision_freeze_verification.json",
        "post_decision_archive_manifest.json",
        "post_decision_archive_verification.json",
        "run_freeze_manifest.json",
        "run_freeze_verification.json",
    }
    if path.startswith(f"runs/{run_id}/") and Path(path).name in clerk_names:
        return {"integrity_checker", "auditor", "editor"}, {"integrity_checker", "auditor", "editor_publisher"}, "deterministic_clerk"

    if path.startswith(f"runs/{run_id}/") and Path(path).name.startswith("non_scientific_change_record"):
        return {"integrity_checker", "auditor", "editor"}, {"integrity_checker", "auditor", "editor_publisher"}, "non_scientific_change_record"

    if path.startswith(f"human_readable_outputs/{run_id}/"):
        return {"integrity_checker", "auditor", "editor"}, {"integrity_checker", "auditor", "editor_publisher"}, "human_readable_package"

    if path.startswith(f"work_packets/{run_id}/"):
        return (
            {"orchestrator", "integrity_checker", "auditor", "editor"},
            {"orchestrator", "codex", "assistant", "integrity_checker", "auditor", "editor_publisher"},
            "work_packet",
        )

    if path.startswith(f"outputs/{run_id}/"):
        return (
            {"orchestrator", "integrity_checker", "auditor", "editor"},
            {"orchestrator", "codex", "assistant", "integrity_checker", "auditor", "editor_publisher"},
            "final_output_bundle",
        )

    return None


def event_outputs(event: dict[str, Any]) -> list[str]:
    value = event.get("output_artifacts", [])
    if isinstance(value, list):
        return [str(item) for item in value]
    if value:
        return [str(value)]
    return []


def event_values(event: dict[str, Any], key: str) -> list[str]:
    value = event.get(key, [])
    if isinstance(value, list):
        return [str(item) for item in value]
    if value:
        return [str(value)]
    return []


def has_non_scientific_change_record(event: dict[str, Any], run_id: str) -> bool:
    text = " ".join(
        event_values(event, "input_artifacts")
        + event_values(event, "output_artifacts")
        + [str(event.get("reason", "")), str(event.get("decision", ""))]
    )
    return f"runs/{run_id}/non_scientific_change_record" in text or "non_scientific_change_record" in text


def is_submission_cleanup_path(path: str, run_id: str) -> bool:
    if not path.startswith(f"submissions/{run_id}/"):
        return False
    return Path(path).name in {
        "manuscript.md",
        "manuscript.pdf",
        "article.md",
        "article.pdf",
        "article_build_report.json",
        "display_item_plan.md",
        "display_item_explanations.md",
        "presentation_checklist.md",
        "artifact_manifest.json",
    }


def audit(root: Path, run_id: str) -> list[Finding]:
    findings: list[Finding] = []
    events = read_event_log(root, run_id)
    if not events:
        findings.append(
            Finding(
                "major",
                "event_log",
                0,
                f"runs/{run_id}/event_log.jsonl",
                "Event log is missing or empty, so artifact authority cannot be reconstructed.",
            )
        )
        return findings

    for event in events:
        role = str(event.get("role", "")).strip()
        agent = str(event.get("agent", "")).strip()
        for output in event_outputs(event):
            normalized = output.removeprefix("./")
            if is_submission_cleanup_path(normalized, run_id) and role not in {"researcher"}:
                if not has_non_scientific_change_record(event, run_id):
                    findings.append(
                        Finding(
                            "major",
                            "artifact_authority",
                            int(event.get("_line", 0)),
                            normalized,
                            "Non-Researcher cleanup of submitted manuscript/package artifacts requires either a reviewer-owned re-review event or a `runs/<run-id>/non_scientific_change_record*.json|md` with before/after hashes and a statement that scientific claims and metrics did not change.",
                        )
                    )
                continue
            allowed = allowed_authors(normalized, run_id)
            if allowed is None:
                continue
            allowed_roles, allowed_agents, artifact_class = allowed
            if role not in allowed_roles and agent not in allowed_agents:
                findings.append(
                    Finding(
                        "major",
                        "artifact_authority",
                        int(event.get("_line", 0)),
                        normalized,
                        f"{artifact_class} should be written by role(s) {sorted(allowed_roles)} or agent(s) {sorted(allowed_agents)}, but event has role `{role}` and agent `{agent}`.",
                    )
                )
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
    parser = argparse.ArgumentParser(description="Audit Research Arena artifact authoring authority.")
    parser.add_argument("run_id", help="Run id under runs/<run_id>.")
    parser.add_argument("--root", default=".", help="Research Arena repository root.")
    parser.add_argument("--output-json", help="Optional JSON output path.")
    parser.add_argument("--output-csv", help="Optional CSV output path.")
    parser.add_argument("--write-default", action="store_true", help="Write runs/<run_id>/artifact_authority_audit.json and .csv.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    findings = audit(root, args.run_id)
    blocking_or_major = [row for row in findings if row.severity in {"blocking", "major"}]
    payload = {
        "run_id": args.run_id,
        "clerk_type": "artifact_authority",
        "scientific_judgment": "not_evaluated",
        "status": "flagged" if blocking_or_major else "pass",
        "finding_count": len(findings),
        "blocking_or_major_count": len(blocking_or_major),
        "notes": [
            "This clerk checks event-log authorship against artifact path authority.",
            "A pass does not prove the role reasoning was scientifically adequate.",
        ],
        "findings": [asdict(row) for row in findings],
    }

    output_json = Path(args.output_json) if args.output_json else None
    output_csv = Path(args.output_csv) if args.output_csv else None
    if args.write_default:
        output_json = root / "runs" / args.run_id / "artifact_authority_audit.json"
        output_csv = root / "runs" / args.run_id / "artifact_authority_audit.csv"

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
