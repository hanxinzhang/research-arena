#!/usr/bin/env python3
"""Summarize Research Arena revision trajectories without judging scientific merit.

This tool is a deterministic clerk. It reports file, hash, compute, issue, and
revision-plan facts so LLM-backed agents can judge the trajectory. It must not be
treated as deciding novelty, scientific depth, article fit, or acceptance.

Usage examples:

  python tools/trajectory_clerk.py my_run
  python tools/trajectory_clerk.py my_run --write-default
  python tools/trajectory_clerk.py my_run --root /path/to/research-arena
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


EMPIRICAL_FILES = [
    "analysis.py",
    "analysis_plan.md",
    "experiment_registry.csv",
    "experiment_registry.json",
    "compute_log.csv",
    "compute_log.json",
    "results.json",
    "stable_results.json",
    "empirical_provenance.json",
    "tables/model_performance.csv",
    "tables/paired_comparisons.csv",
    "tables/bootstrap_ci.csv",
    "tables/subgroup_metrics.csv",
    "tables/calibration_bins.csv",
]

PACKAGING_FILES = [
    "artifact_manifest.json",
    "issue_ledger.md",
    "issue_ledger.json",
    "revision_response.md",
    "verification_matrix.csv",
    "verification_matrix.json",
    "material_research_delta.md",
    "presentation_checklist.md",
    "manuscript.md",
    "manuscript.pdf",
]

TRANSIENT_NAMES = {".DS_Store", "__pycache__"}
UNRESOLVED_STATUSES = {"pending", "open", "opened", "response_submitted", "partially_resolved", "unresolved"}


@dataclass
class RevisionRow:
    submission: str
    revision: str
    revision_type: str
    research_delta_tier: str
    material_research_delta_present: bool
    empirical_provenance_status: str
    revision_plan_present: bool
    empirical_changed_from_previous: str
    packaging_changed_from_previous: str
    analysis_change_kind: str
    primary_metrics_change_kind: str
    primary_metric_max_abs_delta: float
    empirical_files_changed: str
    packaging_files_changed: str
    compute_numeric_cpu_core_hours: float
    compute_delta_from_previous_cpu_core_hours: float
    compute_change_ratio_from_previous: str
    compute_rows: int
    unresolved_issue_count: int
    transient_file_count: int
    prior_review_event_status: str
    revision_start_event_line: str
    prior_review_event_line: str


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def file_hashes(revision: Path, relative_paths: list[str]) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for name in relative_paths:
        path = revision / name
        if path.is_file():
            hashes[name] = sha256(path)
    return hashes


def normalized_analysis_text(path: Path) -> str:
    """Normalize revision markers so staged templates do not look substantive."""
    if not path.is_file():
        return ""
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(errors="replace")
    replacements = [
        (r"^(\s*REVISION_LEVEL\s*=\s*)\d+(\s*(?:#.*)?)$", r"\1<REVISION>\2"),
        (r"^(\s*REVISION\s*=\s*)\d+(\s*(?:#.*)?)$", r"\1<REVISION>\2"),
        (r"^(\s*revision_level\s*=\s*)\d+(\s*(?:#.*)?)$", r"\1<REVISION>\2"),
    ]
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.MULTILINE)
    return text


def analysis_change_kind(previous: Path | None, current: Path) -> str:
    if previous is None:
        return "not_applicable_initial"
    previous_path = previous / "analysis.py"
    current_path = current / "analysis.py"
    if not previous_path.is_file() and not current_path.is_file():
        return "missing_both"
    if not previous_path.is_file() or not current_path.is_file():
        return "added_or_removed"
    previous_hash = sha256(previous_path)
    current_hash = sha256(current_path)
    if previous_hash == current_hash:
        return "unchanged"
    if normalized_analysis_text(previous_path) == normalized_analysis_text(current_path):
        return "revision_marker_only"
    return "substantive_or_unclassified_change"


def read_primary_metrics(revision: Path) -> dict[str, float] | None:
    for name in ["stable_results.json", "results.json"]:
        path = revision / name
        if not path.is_file():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        metrics = payload.get("primary_metrics") if isinstance(payload, dict) else None
        if not isinstance(metrics, dict):
            continue
        numeric: dict[str, float] = {}
        for key, value in metrics.items():
            try:
                numeric[str(key)] = float(value)
            except (TypeError, ValueError):
                continue
        if numeric:
            return numeric
    return None


def primary_metrics_delta(previous: Path | None, current: Path) -> tuple[str, float]:
    if previous is None:
        return "not_applicable_initial", 0.0
    previous_metrics = read_primary_metrics(previous)
    current_metrics = read_primary_metrics(current)
    if previous_metrics is None and current_metrics is None:
        return "missing_both", 0.0
    if previous_metrics is None or current_metrics is None:
        return "added_or_removed", 0.0
    names = sorted(set(previous_metrics) | set(current_metrics))
    deltas = [
        abs(current_metrics.get(name, 0.0) - previous_metrics.get(name, 0.0))
        for name in names
    ]
    max_delta = max(deltas) if deltas else 0.0
    if max_delta == 0:
        return "unchanged", 0.0
    return "changed", max_delta


def changed_files(previous: dict[str, str] | None, current: dict[str, str]) -> list[str]:
    if previous is None:
        return []
    names = sorted(set(previous) | set(current))
    return [name for name in names if previous.get(name) != current.get(name)]


def read_event_log(root: Path, run_id: str) -> list[dict[str, Any]]:
    path = root / "runs" / run_id / "event_log.jsonl"
    if not path.is_file():
        return []
    events: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                event = {"action": "unparseable_event", "raw": line}
            if isinstance(event, dict):
                event["_line"] = line_number
                events.append(event)
    return events


def event_text(event: dict[str, Any]) -> str:
    parts = [
        str(event.get("action", "")),
        str(event.get("agent", "")),
        str(event.get("role", "")),
    ]
    for key in ["input_artifacts", "output_artifacts", "issue_ids"]:
        value = event.get(key, [])
        if isinstance(value, list):
            parts.extend(str(item) for item in value)
        else:
            parts.append(str(value))
    return " ".join(parts)


def first_event_line(events: list[dict[str, Any]], patterns: list[str]) -> int | None:
    for event in events:
        text = event_text(event)
        if all(pattern in text for pattern in patterns):
            return int(event["_line"])
    return None


def revision_start_event_line(events: list[dict[str, Any]], submission: str, revision: Path) -> int | None:
    revision_path = f"{submission}/{revision.name}"
    plan_line = first_event_line(events, [revision_path, "revision_plan"])
    analysis_line = first_event_line(events, [revision_path, "analysis.py"])
    candidates = [line for line in [plan_line, analysis_line] if line is not None]
    return min(candidates) if candidates else None


def prior_review_event_line(events: list[dict[str, Any]], submission: str, revision: Path) -> int | None:
    previous_number = revision_number(revision) - 1
    if previous_number < 0:
        return None
    previous_revision = f"revision_{previous_number:02d}"
    previous_path = f"{submission}/{previous_revision}"
    integrity_line = first_event_line(events, [previous_path, "integrity"])
    referee_line = first_event_line(events, [previous_path, "review"])
    candidates = [line for line in [integrity_line, referee_line] if line is not None]
    return min(candidates) if candidates else None


def prior_review_status(events: list[dict[str, Any]], submission: str, revision: Path) -> tuple[str, str, str]:
    if revision_number(revision) == 0:
        return "not_applicable_initial", "", ""
    start_line = revision_start_event_line(events, submission, revision)
    review_line = prior_review_event_line(events, submission, revision)
    if start_line is None and review_line is None:
        return "missing_revision_start_and_prior_review_events", "", ""
    if start_line is None:
        return "missing_revision_start_event", "", str(review_line or "")
    if review_line is None:
        return "missing_prior_review_event", str(start_line), ""
    if review_line > start_line:
        return "prior_review_after_revision_started", str(start_line), str(review_line)
    return "ok", str(start_line), str(review_line)


def revision_number(path: Path) -> int:
    match = re.search(r"revision_(\d+)$", path.name)
    return int(match.group(1)) if match else -1


def revisions_for(submission_dir: Path) -> list[Path]:
    return sorted(
        [p for p in submission_dir.glob("revision_*") if p.is_dir()],
        key=revision_number,
    )


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            return list(csv.DictReader(handle))
    except Exception:
        return []


def parse_key_values(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in text.splitlines():
        match = re.match(r"^\s*([A-Za-z0-9_+-]+)\s*:\s*(.*?)\s*$", line)
        if match:
            values[match.group(1).strip().lower()] = match.group(2).strip()
    return values


def revision_plan_values(revision: Path) -> dict[str, str]:
    plan = revision / "revision_plan.md"
    if not plan.is_file():
        return {}
    try:
        return parse_key_values(plan.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return {}


def revision_type(revision: Path) -> str:
    values = revision_plan_values(revision)
    return values.get("revision_type", "not_declared") or "not_declared"


def research_delta_tier(revision: Path) -> str:
    values = revision_plan_values(revision)
    return values.get("research_delta_tier", "not_declared") or "not_declared"


def empirical_provenance_status(revision: Path) -> str:
    path = revision / "empirical_provenance.json"
    if not path.is_file():
        return "not_declared"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return "unparseable"
    if not isinstance(payload, dict):
        return "unparseable"
    return str(payload.get("empirical_status") or "not_declared")


def numeric_value(mapping: dict[str, Any], keys: list[str]) -> float | None:
    for key in keys:
        raw = mapping.get(key, "")
        try:
            return float(raw)
        except (TypeError, ValueError):
            continue
    return None


def compute_row_label(row: dict[str, Any]) -> str:
    for key in ["component", "step", "name", "task", "phase"]:
        value = row.get(key)
        if value is not None and str(value).strip():
            return str(value).strip().lower()
    return ""


def is_total_compute_row(row: dict[str, Any]) -> bool:
    label = compute_row_label(row)
    return label.startswith("total") or label.endswith("_total") or "total_" in label or label == "overall"


def summarize_compute_items(items: list[dict[str, Any]]) -> tuple[float, int]:
    rows_count = len(items)
    total_rows = [row for row in items if is_total_compute_row(row)]
    rows_to_sum = total_rows if total_rows else items
    total = 0.0
    for row in rows_to_sum:
        value = numeric_value(row, ["estimated_cpu_core_hours", "cpu_core_hours", "core_hours"])
        if value is not None:
            total += value
    return total, rows_count


def compute_summary(revision: Path) -> tuple[float, int]:
    csv_path = revision / "compute_log.csv"
    json_path = revision / "compute_log.json"
    if csv_path.is_file():
        rows = read_csv_rows(csv_path)
        return summarize_compute_items(rows)
    elif json_path.is_file():
        try:
            payload = json.loads(json_path.read_text(encoding="utf-8"))
        except Exception:
            payload = None
        items: list[Any]
        if isinstance(payload, list):
            items = payload
        elif isinstance(payload, dict):
            items = payload.get("rows") or payload.get("compute_log") or [payload]
        else:
            items = []
        return summarize_compute_items([item for item in items if isinstance(item, dict)])
    return 0.0, 0


def unresolved_issue_count(revision: Path) -> int:
    csv_path = revision / "verification_matrix.csv"
    json_path = revision / "verification_matrix.json"
    rows: list[dict[str, Any]] = []
    if csv_path.is_file():
        rows = read_csv_rows(csv_path)
    elif json_path.is_file():
        try:
            payload = json.loads(json_path.read_text(encoding="utf-8"))
        except Exception:
            payload = None
        if isinstance(payload, list):
            rows = [r for r in payload if isinstance(r, dict)]
        elif isinstance(payload, dict):
            candidates = payload.get("rows") or payload.get("issues") or payload.get("verification_matrix")
            if isinstance(candidates, list):
                rows = [r for r in candidates if isinstance(r, dict)]
    count = 0
    for row in rows:
        status = str(
            row.get("verification_status")
            or row.get("status")
            or row.get("resolution_status")
            or ""
        ).strip().lower()
        if status in UNRESOLVED_STATUSES:
            count += 1
    return count


def transient_count(revision: Path) -> int:
    count = 0
    for path in revision.rglob("*"):
        if path.name in TRANSIENT_NAMES:
            count += 1
    return count


def summarize_submission(root: Path, run_id: str, submission_dir: Path, events: list[dict[str, Any]]) -> tuple[list[RevisionRow], dict[str, Any]]:
    rows: list[RevisionRow] = []
    previous_empirical: dict[str, str] | None = None
    previous_packaging: dict[str, str] | None = None
    previous_revision: Path | None = None
    previous_compute: float | None = None
    stagnant_empirical_revisions: list[str] = []
    revision_marker_only_revisions: list[str] = []
    unchanged_primary_metric_revisions: list[str] = []
    event_order_warnings: list[str] = []
    low_compute_revisions: list[str] = []
    nonmaterial_revisions_with_open_issues: list[str] = []

    for revision in revisions_for(submission_dir):
        empirical_hashes = file_hashes(revision, EMPIRICAL_FILES)
        packaging_hashes = file_hashes(revision, PACKAGING_FILES)
        empirical_changed = changed_files(previous_empirical, empirical_hashes)
        packaging_changed = changed_files(previous_packaging, packaging_hashes)
        analysis_kind = analysis_change_kind(previous_revision, revision)
        primary_metrics_kind, primary_metric_delta = primary_metrics_delta(previous_revision, revision)
        compute_total, compute_rows = compute_summary(revision)
        if previous_compute is None:
            compute_delta = 0.0
            compute_ratio = "not_applicable_initial"
        else:
            compute_delta = compute_total - previous_compute
            if previous_compute == 0:
                compute_ratio = "undefined_previous_zero"
            else:
                compute_ratio = f"{compute_total / previous_compute:.6f}"
        unresolved = unresolved_issue_count(revision)
        plan_present = revision_number(revision) == 0 or (revision / "revision_plan.md").is_file()
        delta_tier = research_delta_tier(revision)
        review_status, start_line, review_line = prior_review_status(events, submission_dir.name, revision)

        empirical_changed_label = "not_applicable_initial" if previous_empirical is None else str(bool(empirical_changed)).lower()
        packaging_changed_label = "not_applicable_initial" if previous_packaging is None else str(bool(packaging_changed)).lower()
        if previous_empirical is not None and not empirical_changed:
            stagnant_empirical_revisions.append(revision.name)
        if analysis_kind == "revision_marker_only":
            revision_marker_only_revisions.append(revision.name)
        if revision_number(revision) > 0 and primary_metrics_kind == "unchanged":
            unchanged_primary_metric_revisions.append(revision.name)
        if review_status not in {"not_applicable_initial", "ok"}:
            event_order_warnings.append(f"{revision.name}:{review_status}")
        if revision_number(revision) > 0 and unresolved > 0 and compute_delta <= 0:
            low_compute_revisions.append(revision.name)
        if revision_number(revision) > 0 and unresolved > 0 and delta_tier == "tier_c_nonmaterial":
            nonmaterial_revisions_with_open_issues.append(revision.name)

        rows.append(
            RevisionRow(
                submission=submission_dir.name,
                revision=revision.name,
                revision_type=revision_type(revision),
                research_delta_tier=delta_tier,
                material_research_delta_present=(revision / "material_research_delta.md").is_file(),
                empirical_provenance_status=empirical_provenance_status(revision),
                revision_plan_present=plan_present,
                empirical_changed_from_previous=empirical_changed_label,
                packaging_changed_from_previous=packaging_changed_label,
                analysis_change_kind=analysis_kind,
                primary_metrics_change_kind=primary_metrics_kind,
                primary_metric_max_abs_delta=round(primary_metric_delta, 12),
                empirical_files_changed=";".join(empirical_changed),
                packaging_files_changed=";".join(packaging_changed),
                compute_numeric_cpu_core_hours=round(compute_total, 6),
                compute_delta_from_previous_cpu_core_hours=round(compute_delta, 6),
                compute_change_ratio_from_previous=compute_ratio,
                compute_rows=compute_rows,
                unresolved_issue_count=unresolved,
                transient_file_count=transient_count(revision),
                prior_review_event_status=review_status,
                revision_start_event_line=start_line,
                prior_review_event_line=review_line,
            )
        )
        previous_empirical = empirical_hashes
        previous_packaging = packaging_hashes
        previous_revision = revision
        previous_compute = compute_total

    missing_plans = [row.revision for row in rows if not row.revision_plan_present]
    summary = {
        "submission": submission_dir.name,
        "revision_count": len(rows),
        "stagnant_empirical_revisions": stagnant_empirical_revisions,
        "revision_marker_only_analysis_revisions": revision_marker_only_revisions,
        "unchanged_primary_metric_revisions": unchanged_primary_metric_revisions,
        "event_order_warnings": event_order_warnings,
        "nonincreasing_compute_with_open_issues": low_compute_revisions,
        "nonmaterial_revisions_with_open_issues": nonmaterial_revisions_with_open_issues,
        "missing_revision_plans": missing_plans,
        "latest_revision": rows[-1].revision if rows else None,
        "latest_research_delta_tier": rows[-1].research_delta_tier if rows else None,
        "latest_material_research_delta_present": rows[-1].material_research_delta_present if rows else None,
        "latest_unresolved_issue_count": rows[-1].unresolved_issue_count if rows else None,
        "latest_compute_numeric_cpu_core_hours": rows[-1].compute_numeric_cpu_core_hours if rows else None,
        "latest_transient_file_count": rows[-1].transient_file_count if rows else None,
    }
    return rows, summary


def write_csv(path: Path, rows: list[RevisionRow]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(asdict(rows[0]).keys()) if rows else [field.name for field in RevisionRow.__dataclass_fields__.values()]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize Research Arena revision trajectories as clerk evidence.")
    parser.add_argument("run_id", help="Run id under submissions/<run_id>.")
    parser.add_argument("--root", default=".", help="Research Arena repository root.")
    parser.add_argument("--output-json", help="Optional JSON output path.")
    parser.add_argument("--output-csv", help="Optional CSV output path.")
    parser.add_argument(
        "--write-default",
        action="store_true",
        help="Write runs/<run_id>/trajectory_clerk.json and .csv.",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    submission_root = root / "submissions" / args.run_id
    events = read_event_log(root, args.run_id)
    all_rows: list[RevisionRow] = []
    submission_summaries: list[dict[str, Any]] = []

    if submission_root.is_dir():
        for submission_dir in sorted(p for p in submission_root.iterdir() if p.is_dir()):
            rows, summary = summarize_submission(root, args.run_id, submission_dir, events)
            all_rows.extend(rows)
            submission_summaries.append(summary)

    output = {
        "run_id": args.run_id,
        "clerk_type": "revision_trajectory_summary",
        "scientific_judgment": "not_evaluated",
        "notes": [
            "This tool reports deterministic trajectory facts only.",
            "LLM-backed agents must judge whether the trajectory is scientifically adequate.",
            "A lack of empirical file changes is a signal for review, not an automatic verdict.",
            "A revision_marker_only analysis change means analysis.py changed only in a recognized revision-number marker after normalization.",
            "prior_review_event_status checks event-log order only; it does not judge review quality.",
            "revision_type and empirical_provenance_status are Researcher-declared fields; use them to distinguish empirical, interpretive, packaging, and mixed revisions.",
            "research_delta_tier and material_research_delta_present are Researcher-declared or structural fields; LLM-backed agents must judge whether the claimed research-state change is scientifically material.",
        ],
        "event_log_present": bool(events),
        "submission_count": len(submission_summaries),
        "submissions": submission_summaries,
        "rows": [asdict(row) for row in all_rows],
    }

    output_json = Path(args.output_json) if args.output_json else None
    output_csv = Path(args.output_csv) if args.output_csv else None
    if args.write_default:
        output_json = root / "runs" / args.run_id / "trajectory_clerk.json"
        output_csv = root / "runs" / args.run_id / "trajectory_clerk.csv"

    if output_json:
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        print(json.dumps(output, indent=2, sort_keys=True))

    if output_csv:
        write_csv(output_csv, all_rows)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
