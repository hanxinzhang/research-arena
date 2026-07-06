#!/usr/bin/env python3
"""Audit Research Arena figure typography and article-effective figure scale."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


FIGURE_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
TARGET_TEXT_SIZE_PT = 8.5
SOURCE_TEXT_TOLERANCE_PT = 0.75
MAX_SOURCE_TEXT_SIZE_RANGE_PT = 1.0
MIN_EFFECTIVE_ARTICLE_TEXT_SIZE_PT = 7.4
MAX_EFFECTIVE_ARTICLE_TEXT_SIZE_PT = 8.8
RAW_FONT_SIZE_PATTERN = re.compile(rb"/[A-Za-z0-9]+\s+([0-9]+(?:\.[0-9]+)?)\s+Tf")
MANUAL_FONTSIZE_PATTERN = re.compile(
    r"(?:fontsize\s*=\s*|set_fontsize\(|tick_params\([^)]*labelsize\s*=\s*)([0-9]+(?:\.[0-9]+)?)",
    flags=re.MULTILINE,
)
ACCEPTABLE_FONT_FRAGMENTS = [
    "Inter",
    "TeXGyreHeros",
    "NimbusSans",
    "LiberationSans",
    "NotoSans",
    "SourceSans",
]


@dataclass
class FigureAudit:
    artifact: str
    status: str
    text_size_values_pt: list[float]
    text_size_min_pt: float | None
    text_size_max_pt: float | None
    text_size_range_pt: float | None
    font_status: str
    font_fragments_found: list[str]
    findings: list[str]


@dataclass
class ManualFontSizeAudit:
    file: str
    status: str
    values_pt: list[float]
    findings: list[str]


@dataclass
class ArticleFigureScaleAudit:
    artifact: str
    status: str
    effective_text_size_pt: float | None
    source_text_size_pt: float | None
    scale_factor: float | None
    findings: list[str]


def repo_root_from(start: Path) -> Path:
    start = start.resolve()
    for parent in [start, *start.parents]:
        if (parent / "program.md").is_file() and (parent / "agents").is_dir():
            return parent
    raise SystemExit("Could not locate the research-arena root.")


def rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def qdf_bytes(pdf_path: Path) -> bytes | None:
    qpdf = shutil.which("qpdf")
    if not qpdf:
        return None
    with tempfile.TemporaryDirectory(prefix="ra_figure_audit_") as tmp:
        output = Path(tmp) / "figure.qdf.pdf"
        completed = subprocess.run(
            [qpdf, "--qdf", "--object-streams=disable", str(pdf_path), str(output)],
            text=True,
            capture_output=True,
            timeout=30,
            check=False,
        )
        if completed.returncode != 0 or not output.is_file():
            return None
        return output.read_bytes()


def inspect_pdf_figure(path: Path, revision_dir: Path, root: Path) -> FigureAudit:
    data = qdf_bytes(path)
    findings: list[str] = []
    if data is None:
        return FigureAudit(
            artifact=rel(path, revision_dir),
            status="flagged",
            text_size_values_pt=[],
            text_size_min_pt=None,
            text_size_max_pt=None,
            text_size_range_pt=None,
            font_status="unknown",
            font_fragments_found=[],
            findings=["could not inspect PDF text sizes because qpdf was unavailable or failed"],
        )

    values = sorted({round(float(match.group(1)), 2) for match in RAW_FONT_SIZE_PATTERN.finditer(data)})
    font_fragments = sorted(fragment for fragment in ACCEPTABLE_FONT_FRAGMENTS if fragment.encode() in data)
    if not values:
        findings.append("no vector PDF text was detected; visual inspection is required")
        text_min = None
        text_max = None
        text_range = None
    else:
        text_min = min(values)
        text_max = max(values)
        text_range = text_max - text_min
        if text_min < TARGET_TEXT_SIZE_PT - SOURCE_TEXT_TOLERANCE_PT:
            findings.append(f"smallest source figure text is {text_min:.1f} pt, below the {TARGET_TEXT_SIZE_PT:.1f} pt target")
        if text_max > TARGET_TEXT_SIZE_PT + SOURCE_TEXT_TOLERANCE_PT:
            findings.append(f"largest source figure text is {text_max:.1f} pt, above the {TARGET_TEXT_SIZE_PT:.1f} pt target")
        if text_range > MAX_SOURCE_TEXT_SIZE_RANGE_PT:
            findings.append(f"source figure text sizes vary by {text_range:.1f} pt; titles, labels, ticks, and legends should use one size")

    font_status = "pass" if font_fragments else "flagged"
    if not font_fragments:
        findings.append("no accepted open-source sans-serif figure font fragment was detected")

    return FigureAudit(
        artifact=rel(path, revision_dir),
        status="pass" if not findings else "flagged",
        text_size_values_pt=values,
        text_size_min_pt=text_min,
        text_size_max_pt=text_max,
        text_size_range_pt=text_range,
        font_status=font_status,
        font_fragments_found=font_fragments,
        findings=findings,
    )


def inspect_raster_figure(path: Path, revision_dir: Path) -> FigureAudit:
    return FigureAudit(
        artifact=rel(path, revision_dir),
        status="flagged",
        text_size_values_pt=[],
        text_size_min_pt=None,
        text_size_max_pt=None,
        text_size_range_pt=None,
        font_status="unknown",
        font_fragments_found=[],
        findings=["raster figure text size cannot be audited from PDF vectors; use PDF figures for article output"],
    )


def figure_paths(revision_dir: Path) -> list[Path]:
    figures_dir = revision_dir / "figures"
    if not figures_dir.is_dir():
        return []
    return sorted(path for path in figures_dir.iterdir() if path.is_file() and path.suffix.lower() in FIGURE_EXTENSIONS)


def inspect_manual_font_sizes(revision_dir: Path, root: Path) -> list[ManualFontSizeAudit]:
    audits: list[ManualFontSizeAudit] = []
    candidates = sorted(path for path in revision_dir.glob("*.py") if path.is_file())
    source_dir = revision_dir / "source_code"
    if source_dir.is_dir():
        candidates.extend(sorted(path for path in source_dir.glob("*.py") if path.is_file()))
    for path in candidates:
        text = path.read_text(encoding="utf-8", errors="replace")
        values = [round(float(match.group(1)), 2) for match in MANUAL_FONTSIZE_PATTERN.finditer(text)]
        findings = [
            f"manual fontsize {value:.1f} pt differs from the {TARGET_TEXT_SIZE_PT:.1f} pt article figure target; exported figure PDFs remain authoritative"
            for value in values
            if abs(value - TARGET_TEXT_SIZE_PT) > SOURCE_TEXT_TOLERANCE_PT
        ]
        if values:
            audits.append(
                ManualFontSizeAudit(
                    file=rel(path, root),
                    status="pass" if not findings else "advisory",
                    values_pt=values,
                    findings=findings,
                )
            )
    return audits


def walk_article_figure_records(report: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for figure in report.get("included_figures", []):
        if not isinstance(figure, dict):
            continue
        if "panels" in figure and isinstance(figure["panels"], list):
            for panel in figure["panels"]:
                if isinstance(panel, dict):
                    records.append(panel)
        else:
            records.append(figure)
    return records


def parse_float(value: object) -> float | None:
    if value in {None, ""}:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def inspect_article_report(article_report: Path, root: Path) -> list[ArticleFigureScaleAudit]:
    if not article_report.is_file():
        return []
    report = json.loads(article_report.read_text(encoding="utf-8", errors="replace"))
    audits: list[ArticleFigureScaleAudit] = []
    for record in walk_article_figure_records(report):
        effective = parse_float(record.get("effective_article_text_size_pt"))
        source_size = parse_float(record.get("source_text_size_pt"))
        scale = parse_float(record.get("article_scale_factor"))
        findings: list[str] = []
        if effective is None:
            findings.append("article-effective figure text size is missing from the build report")
        elif effective < MIN_EFFECTIVE_ARTICLE_TEXT_SIZE_PT:
            findings.append(f"article-effective text is {effective:.1f} pt, below readable article scale")
        elif effective > MAX_EFFECTIVE_ARTICLE_TEXT_SIZE_PT:
            findings.append(f"article-effective text is {effective:.1f} pt, above the article text scale")
        if record.get("figure_text_size_status") not in {None, "pass"}:
            findings.append(str(record.get("figure_text_size_status")))
        audits.append(
            ArticleFigureScaleAudit(
                artifact=str(record.get("artifact") or record.get("copied_to") or "unknown"),
                status="pass" if not findings else "flagged",
                effective_text_size_pt=effective,
                source_text_size_pt=source_size,
                scale_factor=scale,
                findings=findings,
            )
        )
    return audits


def resolve_revision_dir(root: Path, args: argparse.Namespace) -> Path:
    if args.revision_dir:
        return Path(args.revision_dir).resolve()
    if not args.run_id or not args.submission:
        raise SystemExit("Provide either a revision_dir argument or --run-id plus --submission.")
    submission_dir = root / "submissions" / args.run_id / args.submission
    if not submission_dir.is_dir():
        raise SystemExit(f"Missing submission folder: {rel(submission_dir, root)}")
    if args.revision == "latest":
        revisions = sorted(path for path in submission_dir.glob("revision_*") if path.is_dir())
        if not revisions:
            raise SystemExit(f"No revision folders found under {rel(submission_dir, root)}")
        return revisions[-1].resolve()
    return (submission_dir / args.revision).resolve()


def build_audit(revision_dir: Path, root: Path, article_report: Path | None) -> dict[str, Any]:
    figures = [
        inspect_pdf_figure(path, revision_dir, root) if path.suffix.lower() == ".pdf" else inspect_raster_figure(path, revision_dir)
        for path in figure_paths(revision_dir)
    ]
    manual = inspect_manual_font_sizes(revision_dir, root)
    resolved_article_report = article_report or revision_dir / "article" / "article_build_report.json"
    article_scales = inspect_article_report(resolved_article_report, root)
    flagged = [
        *[audit for audit in figures if audit.status != "pass"],
        *[audit for audit in article_scales if audit.status != "pass"],
    ]
    return {
        "status": "pass" if not flagged else "flagged",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_revision": rel(revision_dir, root),
        "article_report": rel(resolved_article_report, root) if resolved_article_report.is_file() else "",
        "target_source_text_size_pt": TARGET_TEXT_SIZE_PT,
        "source_text_tolerance_pt": SOURCE_TEXT_TOLERANCE_PT,
        "max_source_text_size_range_pt": MAX_SOURCE_TEXT_SIZE_RANGE_PT,
        "effective_article_text_size_range_pt": [
            MIN_EFFECTIVE_ARTICLE_TEXT_SIZE_PT,
            MAX_EFFECTIVE_ARTICLE_TEXT_SIZE_PT,
        ],
        "figure_count": len(figures),
        "flagged_count": len(flagged),
        "figure_audits": [asdict(audit) for audit in figures],
        "manual_fontsize_audits": [asdict(audit) for audit in manual],
        "article_figure_scale_audits": [asdict(audit) for audit in article_scales],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Research Arena figure presentation normalization.")
    parser.add_argument("revision_dir", nargs="?", help="Revision folder containing figures/ and optionally article/article_build_report.json.")
    parser.add_argument("--root", default=".", help="Research Arena repository root.")
    parser.add_argument("--run-id", help="Run id under submissions/<run-id> when revision_dir is omitted.")
    parser.add_argument("--submission", help="Submission folder name when revision_dir is omitted.")
    parser.add_argument("--revision", default="latest", help="Revision folder name or `latest` when revision_dir is omitted.")
    parser.add_argument("--article-report", help="Explicit article_build_report.json path.")
    parser.add_argument("--write", action="store_true", help="Write figure_presentation_audit.json into the revision folder.")
    parser.add_argument("--no-fail", action="store_true", help="Always exit 0 after writing/printing the audit.")
    args = parser.parse_args()

    root = repo_root_from(Path(args.root))
    revision_dir = resolve_revision_dir(root, args)
    article_report = Path(args.article_report).resolve() if args.article_report else None
    audit = build_audit(revision_dir, root, article_report)
    output = json.dumps(audit, indent=2, sort_keys=True) + "\n"
    if args.write:
        target = revision_dir / "figure_presentation_audit.json"
        target.write_text(output, encoding="utf-8")
        print(f"Wrote {rel(target, root)}")
    print(f"{audit['status']} {audit['flagged_count']} flagged issue(s) across {audit['figure_count']} figure(s)")
    return 0 if args.no_fail or audit["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
