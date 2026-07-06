#!/usr/bin/env python3
"""Clerk-check Research Arena runs for structural depth artifacts.

Usage examples:

  python tools/research_depth_audit.py oasis_demo
  python tools/research_depth_audit.py oasis_demo --write-default
  python tools/research_depth_audit.py my_run --root /path/to/research-arena

This deterministic tool checks artifact presence, presentation structure, and
basic independence signals. It does not judge scientific depth, novelty, article
fit, or acceptance. LLM-backed agents must make those judgments from the evidence.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


RUN_REQUIRED = [
    "article_type_contract.md",
    "study_design_contract.md",
    "proposal_gate_summary.md",
    "research_depth_contract.md",
    "manuscript_quality_contract.md",
    "agent_independence_plan.md",
    "editor_gate_plan.md",
]

RUN_REQUIRED_ANY = [
    ("compute_budget", ["compute_budget.md", "compute_budget.json"]),
]

INITIAL_REQUIRED = [
    "proposal.md",
    "research_dossier.md",
    "literature_notes.md",
    "analysis_plan.md",
    "model_or_method_cards.md",
    "analysis.py",
    "results.json",
]

PROPOSAL_GATE_REQUIRED = [
    "data_familiarization.md",
    "pilot_study_plan.md",
    "pilot_study_results.json",
    "pilot_lessons.md",
    "candidate_studies.md",
    "selected_proposal.md",
    "compute_budget_estimate.md",
]

PROPOSAL_GATE_REQUIRED_ANY = [
    ("pilot_compute_log", ["pilot_compute_log.csv", "pilot_compute_log.json"]),
]

INITIAL_REQUIRED_ANY = [
    ("eda_report", ["eda_report.md", "eda_report.ipynb"]),
    ("experiment_registry", ["experiment_registry.csv", "experiment_registry.json"]),
    ("compute_log", ["compute_log.csv", "compute_log.json"]),
]

LATEST_REQUIRED = [
    "analysis.py",
    "results.json",
    "artifact_manifest.json",
    "issue_ledger.md",
    "revision_response.md",
    "manuscript.md",
    "manuscript.pdf",
    "display_item_explanations.md",
    "presentation_checklist.md",
]

LATEST_REQUIRED_ANY = [
    ("verification_matrix", ["verification_matrix.csv", "verification_matrix.json"]),
    ("compute_log", ["compute_log.csv", "compute_log.json"]),
]

WRAPPER_PATTERNS = [
    r"runpy\.run_path",
    r"ENGINE\s*=",
    r"central\s+generator",
    r"run_single_analysis",
    r"scripts/.+arena",
    r"scripts\\.+arena",
]

QUALITY_DEFAULTS = {
    "minimum_manuscript_words": 1200,
    "minimum_methods_words": 250,
    "minimum_display_items": 1,
    "minimum_subsection_count": 2,
    "minimum_numbered_equations": 0,
    "allow_raw_markdown_pdf": False,
    "allow_fallback_renderer": False,
    "require_line_numbers": True,
    "require_numbered_equations": True,
    "require_rendered_math": True,
    "require_display_item_explanations": True,
    "require_human_readable_output": True,
    "require_manuscript_style_manifest": True,
    "require_preferred_sans_fonts": True,
    "require_rendering_toolchain": True,
    "require_integrated_article_pdf": True,
}

BUNDLED_FONT_DIR = Path("assets") / "fonts" / "inter"
BUNDLED_FONT_FILES = [
    "Inter-Regular.ttf",
    "Inter-Bold.ttf",
    "Inter-Italic.ttf",
    "Inter-BoldItalic.ttf",
    "LICENSE.txt",
]

PREFERRED_SANS_FONTS = [
    "Inter",
    "TeX Gyre Heros",
    "Nimbus Sans",
    "Nimbus Sans L",
    "Liberation Sans",
    "Noto Sans",
    "Source Sans 3",
    "Source Sans Pro",
]

EXPECTED_ARTICLE_BRAND_LOGO = "research_arena_logo_evidence_gain"

PRESENTATION_CHECKLIST_FIELDS = [
    "status",
    "manuscript_word_count",
    "methods_word_count",
    "display_item_count",
    "pdf_visual_check",
    "figure_label_check",
    "figure_text_size_normalization_check",
    "figure_mark_scale_check",
    "table_readability_check",
    "display_item_plan_check",
    "display_item_explanation_check",
    "raw_label_translation_check",
    "math_or_method_detail_check",
    "line_number_check",
    "equation_numbering_check",
    "math_rendering_check",
    "inline_math_rendering_check",
    "human_readable_output_check",
    "manuscript_typography_check",
    "figure_typography_check",
    "render_toolchain_check",
    "article_pdf_check",
    "known_presentation_limits",
]

STYLE_MANIFEST_FIELDS = [
    "line_numbers",
    "manuscript_font_family",
    "figure_font_family",
    "math_font_family",
    "numbered_equations",
    "math_rendering_check",
    "inline_math_rendering_check",
    "pdf_renderer",
    "visual_pdf_review",
    "figure_typography_review",
    "figure_presentation_audit",
    "known_style_limits",
]

REQUIRED_MANUSCRIPT_SECTIONS = {
    "abstract": [r"abstract"],
    "introduction_or_background": [r"introduction", r"background"],
    "results_or_findings": [r"results", r"findings"],
    "discussion_or_interpretation": [r"discussion", r"interpretation"],
    "figure_table_interpretation": [
        r"figure.*table",
        r"table.*figure",
        r"display item",
        r"display-item",
        r"figure annotation",
        r"table annotation",
        r"visual guide",
    ],
    "methods": [r"methods", r"methodology"],
    "limitations": [r"limitations"],
    "references": [r"references", r"bibliography"],
}

COMPUTE_OUTCOMES = {
    "compute_target_met",
    "compute_under_target_with_approved_efficiency_override",
    "compute_under_target_requires_downgrade",
    "compute_under_target_blocks_acceptance",
}

REVISION_TYPES = {
    "empirical_revision",
    "interpretive_revision",
    "packaging_revision",
    "mixed_revision",
}

RESEARCH_DELTA_TIERS = {
    "tier_a_material",
    "tier_b_supporting",
    "tier_c_nonmaterial",
}

EMPIRICAL_PROVENANCE_STATUSES = {
    "rerun_current_revision",
    "copied_forward",
    "unchanged_from_previous",
    "not_applicable_initial",
}

ISSUE_LIFECYCLE_STATUSES = {
    "opened",
    "response_submitted",
    "verified_resolved",
    "partially_resolved",
    "unresolved",
    "editorial_risk_accepted",
    "superseded",
}

STATUS_NORMALIZATION = {
    "pending": "opened",
    "open": "opened",
    "resolved": "verified_resolved",
    "verified": "verified_resolved",
    "editorial_risk_disclosed": "editorial_risk_accepted",
    "accepted_risk": "editorial_risk_accepted",
}


@dataclass
class Finding:
    severity: str
    category: str
    subject: str
    path: str
    message: str


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def nonempty_file(path: Path) -> bool:
    return path.is_file() and path.stat().st_size > 0


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def has_any(folder: Path, names: list[str]) -> bool:
    return any(nonempty_file(folder / name) for name in names)


def has_any_file(folder: Path) -> bool:
    return folder.is_dir() and any(path.is_file() for path in folder.rglob("*") if not path.name.startswith("."))


def human_readable_package_dir(root: Path, run_id: str, submission: str, revision: str) -> Path:
    return root / "human_readable_outputs" / run_id / submission / revision


def audit_human_readable_output(
    root: Path,
    run_id: str,
    submission: str,
    latest: Path,
    require_article_pdf: bool = False,
) -> list[Finding]:
    package = human_readable_package_dir(root, run_id, submission, latest.name)
    findings: list[Finding] = []
    for name in ["README.md", "human_readable_package_manifest.json", "manuscript.pdf"]:
        path = package / name
        if not nonempty_file(path):
            findings.append(
                Finding(
                    "major",
                    "presentation_gate",
                    submission,
                    rel(path, root),
                    "Missing human-readable output package artifact. Run `tools/package_human_readable_outputs.py --run-id "
                    + run_id
                    + " --replace`.",
                )
            )
    if require_article_pdf and not nonempty_file(package / "article.pdf"):
        findings.append(
            Finding(
                "major",
                "presentation_gate",
                submission,
                rel(package / "article.pdf", root),
                "Missing integrated `article.pdf` in the human-readable output package. Run `tools/build_article_pdf.py` for each revision, then refresh `tools/package_human_readable_outputs.py --run-id <run-id> --replace`.",
            )
        )
    for dirname in ["figures", "tables", "source_code"]:
        path = package / dirname
        if not path.is_dir():
            findings.append(
                Finding(
                    "major",
                    "presentation_gate",
                    submission,
                    rel(path, root),
                    f"Missing `{dirname}/` in the human-readable output package.",
                )
            )
    if not has_any_file(package / "source_code"):
        findings.append(
            Finding(
                "major",
                "presentation_gate",
                submission,
                rel(package / "source_code", root),
                "Human-readable output package must include source code, usually `source_code/analysis.py`.",
            )
        )
    manifest = package / "human_readable_package_manifest.json"
    if nonempty_file(manifest):
        try:
            payload = read_json(manifest)
        except Exception as exc:
            findings.append(
                Finding(
                    "major",
                    "presentation_gate",
                    submission,
                    rel(manifest, root),
                    f"Human-readable package manifest could not be parsed: {exc}.",
                )
            )
            return findings
        source_revision = str(payload.get("source_revision", ""))
        if source_revision and source_revision != rel(latest, root):
            findings.append(
                Finding(
                    "major",
                    "presentation_gate",
                    submission,
                    rel(manifest, root),
                    f"Package manifest source revision is `{source_revision}`, expected `{rel(latest, root)}`.",
                )
            )
        items = payload.get("copied_items", [])
        if not isinstance(items, list):
            findings.append(
                Finding(
                    "major",
                    "presentation_gate",
                    submission,
                    rel(manifest, root),
                    "`copied_items` must be a list with source and destination hashes.",
                )
            )
        else:
            for idx, item in enumerate(items, start=1):
                if not isinstance(item, dict):
                    continue
                source = root / str(item.get("source", ""))
                destination = root / str(item.get("destination", ""))
                expected_source_hash = str(item.get("source_sha256", ""))
                expected_destination_hash = str(item.get("destination_sha256", ""))
                if not expected_source_hash or not expected_destination_hash:
                    findings.append(
                        Finding(
                            "major",
                            "presentation_gate",
                            submission,
                            rel(manifest, root),
                            f"Package manifest item {idx} lacks source/destination SHA-256 hashes; rebuild with the current package tool.",
                        )
                    )
                    continue
                if not source.is_file():
                    findings.append(
                        Finding(
                            "major",
                            "presentation_gate",
                            submission,
                            rel(manifest, root),
                            f"Package manifest item {idx} source is missing: `{item.get('source')}`.",
                        )
                    )
                elif sha256(source) != expected_source_hash:
                    findings.append(
                        Finding(
                            "major",
                            "presentation_gate",
                            submission,
                            rel(manifest, root),
                            f"Package manifest item {idx} source hash is stale for `{item.get('source')}`; rebuild the human-readable package after source changes.",
                        )
                    )
                if not destination.is_file():
                    findings.append(
                        Finding(
                            "major",
                            "presentation_gate",
                            submission,
                            rel(manifest, root),
                            f"Package manifest item {idx} destination is missing: `{item.get('destination')}`.",
                        )
                    )
                elif sha256(destination) != expected_destination_hash:
                    findings.append(
                        Finding(
                            "major",
                            "presentation_gate",
                            submission,
                            rel(manifest, root),
                            f"Package manifest item {idx} destination hash does not match the manifest; rebuild the package.",
                        )
                    )
    return findings


def markdown_word_count(path: Path) -> int:
    if not path.exists():
        return 0
    text = path.read_text(encoding="utf-8", errors="replace")
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    return len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?", text))


def markdown_headings(text: str) -> list[str]:
    headings = []
    for line in text.splitlines():
        match = re.match(r"^\s{0,3}#{1,6}\s+(.+?)\s*$", line)
        if match:
            headings.append(match.group(1).strip().lower())
    return headings


def markdown_heading_levels(text: str) -> list[tuple[int, str]]:
    headings = []
    for line in text.splitlines():
        match = re.match(r"^\s{0,3}(#{1,6})\s+(.+?)\s*$", line)
        if match:
            headings.append((len(match.group(1)), match.group(2).strip().lower()))
    return headings


def section_text(text: str, names: list[str]) -> str:
    lines = text.splitlines()
    start = None
    start_level = None
    for idx, line in enumerate(lines):
        match = re.match(r"^\s{0,3}(#{1,6})\s+(.+?)\s*$", line)
        if not match:
            continue
        heading = match.group(2).strip().lower()
        if any(re.search(pattern, heading) for pattern in names):
            start = idx + 1
            start_level = len(match.group(1))
            break
    if start is None:
        return ""
    end = len(lines)
    for idx in range(start, len(lines)):
        match = re.match(r"^\s{0,3}(#{1,6})\s+", lines[idx])
        if match and start_level is not None and len(match.group(1)) <= start_level:
            end = idx
            break
    return "\n".join(lines[start:end])


def parse_key_values(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in text.splitlines():
        match = re.match(r"^\s*([A-Za-z0-9_+-]+)\s*:\s*(.*?)\s*$", line)
        if match:
            values[match.group(1).strip().lower()] = match.group(2).strip()
    return values


def normalize_font_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


PREFERRED_FONT_KEYS = [normalize_font_name(font) for font in PREFERRED_SANS_FONTS]


def uses_preferred_sans_font(value: str) -> bool:
    normalized = normalize_font_name(value)
    return any(key in normalized for key in PREFERRED_FONT_KEYS)


def equation_numbering_summary(text: str) -> dict[str, int]:
    numbered = 0
    unnumbered = 0
    spans: list[tuple[int, int]] = []
    env_pattern = re.compile(
        r"\\begin\{(?P<env>equation\*?|align\*?|gather\*?|multline\*?)\}"
        r"(?P<body>.*?)"
        r"\\end\{(?P=env)\}",
        flags=re.DOTALL,
    )
    for match in env_pattern.finditer(text):
        spans.append(match.span())
        env = match.group("env")
        body = match.group("body")
        if env.endswith("*"):
            unnumbered += 1
        elif r"\notag" in body or r"\nonumber" in body:
            unnumbered += 1
        else:
            numbered += 1

    masked = list(text)
    for start, end in spans:
        for idx in range(start, end):
            masked[idx] = " "
    remaining = "".join(masked)

    for pattern in [r"\$\$(.*?)\$\$", r"\\\[(.*?)\\\]"]:
        for match in re.finditer(pattern, remaining, flags=re.DOTALL):
            body = match.group(1)
            if re.search(r"\\tag\s*\{[^}]+\}", body):
                numbered += 1
            else:
                unnumbered += 1

    return {"numbered": numbered, "unnumbered": unnumbered}


def pdf_mentions_preferred_font(path: Path) -> bool:
    if not nonempty_file(path):
        return False
    pdffonts = shutil.which("pdffonts")
    if pdffonts:
        try:
            completed = subprocess.run(
                [pdffonts, str(path)],
                text=True,
                capture_output=True,
                timeout=30,
                check=False,
            )
        except Exception:
            completed = None
        if completed and completed.returncode == 0 and completed.stdout.strip():
            normalized_fonts = normalize_font_name(completed.stdout)
            if any(key in normalized_fonts for key in PREFERRED_FONT_KEYS):
                return True
    try:
        text = path.read_bytes().decode("latin-1", errors="ignore")
    except OSError:
        return False
    normalized = normalize_font_name(text)
    return any(key in normalized for key in PREFERRED_FONT_KEYS)


RAW_MATH_PDF_PATTERNS = [
    r"\\begin\{(?:equation|align|gather|multline)",
    r"\\end\{(?:equation|align|gather|multline)",
    r"\\label\{",
    r"\\tag\{",
    r"\\\(",
    r"\\\)",
    r"\\hat\{",
    r"\\frac\{",
    r"\\theta",
    r"\\qquad",
    r"\$\$",
    r"\\\[",
    r"\\\]",
]


def pdf_raw_math_markup_patterns(path: Path) -> list[str]:
    if not nonempty_file(path):
        return []
    pdftotext = shutil.which("pdftotext")
    if pdftotext:
        try:
            completed = subprocess.run(
                [pdftotext, str(path), "-"],
                text=True,
                capture_output=True,
                timeout=30,
                check=False,
            )
        except Exception:
            completed = None
        if completed and completed.returncode == 0:
            return [pattern for pattern in RAW_MATH_PDF_PATTERNS if re.search(pattern, completed.stdout)]
    try:
        text = path.read_bytes().decode("latin-1", errors="ignore")
    except OSError:
        return []
    return [pattern for pattern in RAW_MATH_PDF_PATTERNS if re.search(pattern, text)]


def svg_font_values(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    values = []
    values.extend(re.findall(r"font-family\s*:\s*([^;\"']+|['\"][^;]+?['\"])", text, flags=re.IGNORECASE))
    values.extend(re.findall(r"font-family\s*=\s*['\"]([^'\"]+)['\"]", text, flags=re.IGNORECASE))
    cleaned = []
    for value in values:
        cleaned.append(value.strip().strip("'\""))
    return cleaned


def display_item_count(latest: Path) -> int:
    count = 0
    figure_suffixes = {".pdf", ".svg", ".png", ".jpg", ".jpeg", ".tif", ".tiff"}
    figures_dir = latest / "figures"
    if not figures_dir.is_dir():
        concepts = set()
    else:
        concepts = {
            path.stem
            for path in figures_dir.iterdir()
            if path.is_file() and path.suffix.lower() in figure_suffixes
        }
    count += len(concepts)

    table_suffixes = {".csv", ".tsv", ".xlsx", ".xls", ".md", ".tex", ".json"}
    tables_dir = latest / "tables"
    if tables_dir.is_dir():
        count += sum(
            1
            for path in tables_dir.iterdir()
            if path.is_file() and path.suffix.lower() in table_suffixes
        )
    return count


def display_item_paths(latest: Path) -> list[Path]:
    paths: list[Path] = []
    figure_suffixes = {".pdf", ".svg", ".png", ".jpg", ".jpeg", ".tif", ".tiff"}
    figures_dir = latest / "figures"
    if figures_dir.is_dir():
        seen_stems: set[str] = set()
        for path in sorted(figures_dir.iterdir()):
            if path.is_file() and path.suffix.lower() in figure_suffixes and path.stem not in seen_stems:
                paths.append(path)
                seen_stems.add(path.stem)

    table_suffixes = {".csv", ".tsv", ".xlsx", ".xls", ".md", ".tex", ".json"}
    tables_dir = latest / "tables"
    if tables_dir.is_dir():
        for path in sorted(tables_dir.iterdir()):
            if path.is_file() and path.suffix.lower() in table_suffixes:
                paths.append(path)
    return paths


def display_item_field_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


def parse_display_item_explanation_entries(text: str) -> dict[str, dict[str, str]]:
    entries: dict[str, dict[str, str]] = {}
    matches = list(re.finditer(r"^##\s+(.+?)\s*$", text, flags=re.MULTILINE))
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        chunk = text[start:end].strip()
        fields: dict[str, str] = {}
        active_key: str | None = None
        in_subsection = False
        for line in chunk.splitlines():
            heading_match = re.match(r"^#{3,6}\s+(.+?)\s*$", line)
            if heading_match:
                in_subsection = True
                active_key = display_item_field_key(heading_match.group(1))
                fields.setdefault(active_key, "")
                continue
            field_match = None if in_subsection else re.match(r"^([A-Za-z][A-Za-z /-]+):\s*(.*)$", line)
            if field_match:
                active_key = display_item_field_key(field_match.group(1))
                fields[active_key] = field_match.group(2).strip().strip("`")
                continue
            if active_key and line.strip():
                line_text = re.sub(r"^[-*]\s*", "", line.strip())
                fields[active_key] = (fields[active_key] + " " + line_text).strip()
        artifact_path = fields.get("artifact_path", "").strip("` ")
        if artifact_path:
            entries[artifact_path.lower()] = fields
            entries[Path(artifact_path).name.lower()] = fields
            entries[Path(artifact_path).stem.lower()] = fields
    return entries


def display_item_entry_for_path(path: Path, latest: Path, entries: dict[str, dict[str, str]]) -> dict[str, str] | None:
    rel_path = rel(path, latest).lower()
    return entries.get(rel_path) or entries.get(path.name.lower()) or entries.get(path.stem.lower())


def pdf_figure_count(figures_dir: Path) -> int:
    if not figures_dir.is_dir():
        return 0
    return sum(1 for path in figures_dir.glob("*.pdf") if path.is_file())


RAW_IDENTIFIER_PATTERN = re.compile(r"\b[A-Za-z][A-Za-z0-9]*_[A-Za-z0-9_]{2,}\b")


def raw_identifier_candidates(text: str) -> list[str]:
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"`[^`]+\.(?:pdf|svg|png|jpg|jpeg|csv|tsv|xlsx|xls|json|md|tex)`", " ", text)
    text = re.sub(r"\b(?:figures|tables)/[A-Za-z0-9_.\-/]+\b", " ", text)
    ignored_prefixes = ("figure_", "table_", "eq_", "run_", "revision_")
    candidates = []
    for match in RAW_IDENTIFIER_PATTERN.finditer(text):
        token = match.group(0)
        if token.lower().startswith(ignored_prefixes):
            continue
        if len(token) < 12 and token.count("_") == 1:
            continue
        candidates.append(token)
    return sorted(set(candidates))


def parse_bool(value: str) -> bool | None:
    normalized = value.strip().lower()
    if normalized in {"true", "yes", "1"}:
        return True
    if normalized in {"false", "no", "0"}:
        return False
    return None


def read_quality_contract(root: Path, run_id: str) -> tuple[dict[str, int | bool], list[Finding]]:
    settings: dict[str, int | bool] = dict(QUALITY_DEFAULTS)
    findings: list[Finding] = []
    path = root / "runs" / run_id / "manuscript_quality_contract.md"
    if not nonempty_file(path):
        return settings, findings

    text = path.read_text(encoding="utf-8", errors="replace")
    required_integer_fields = {
        "minimum_manuscript_words",
        "minimum_methods_words",
        "minimum_display_items",
        "minimum_subsection_count",
        "minimum_numbered_equations",
    }
    required_bool_fields = {
        "allow_raw_markdown_pdf",
        "allow_fallback_renderer",
        "require_line_numbers",
        "require_numbered_equations",
        "require_rendered_math",
        "require_display_item_explanations",
        "require_human_readable_output",
        "require_manuscript_style_manifest",
        "require_preferred_sans_fonts",
        "require_rendering_toolchain",
    }
    optional_bool_fields: set[str] = set()
    required_bool_fields.add("require_integrated_article_pdf")
    found_fields: set[str] = set()
    for key in required_integer_fields:
        match = re.search(rf"^\s*{key}\s*:\s*(\d+)\s*$", text, flags=re.MULTILINE)
        if match:
            settings[key] = int(match.group(1))
            found_fields.add(key)
    for key in required_bool_fields:
        match = re.search(rf"^\s*{key}\s*:\s*([A-Za-z0-9_+-]+)\s*$", text, flags=re.MULTILINE)
        if not match:
            continue
        value = parse_bool(match.group(1))
        if value is None:
            findings.append(
                Finding(
                    "major",
                    "manuscript_quality_contract",
                    run_id,
                    rel(path, root),
                    f"`{key}` must be true or false.",
                )
            )
        else:
            settings[key] = value
            found_fields.add(key)
    for key in optional_bool_fields:
        match = re.search(rf"^\s*{key}\s*:\s*([A-Za-z0-9_+-]+)\s*$", text, flags=re.MULTILINE)
        if not match:
            continue
        value = parse_bool(match.group(1))
        if value is None:
            findings.append(
                Finding(
                    "major",
                    "manuscript_quality_contract",
                    run_id,
                    rel(path, root),
                    f"`{key}` must be true or false.",
                )
            )
        else:
            settings[key] = value
    missing = sorted((required_integer_fields | required_bool_fields) - found_fields)
    if missing:
        findings.append(
            Finding(
                "major",
                "manuscript_quality_contract",
                run_id,
                rel(path, root),
                "Missing required manuscript-quality setting(s): " + ", ".join(missing) + ".",
            )
        )
    return settings, findings


def audit_render_toolchain_report(root: Path, run_id: str, quality_settings: dict[str, int | bool]) -> list[Finding]:
    findings: list[Finding] = []
    if not bool(quality_settings.get("require_rendering_toolchain", True)):
        return findings
    path = root / "runs" / run_id / "render_toolchain_report.json"
    if not nonempty_file(path):
        findings.append(
            Finding(
                "major",
                "presentation_gate",
                run_id,
                rel(path, root),
                "Missing rendering toolchain report. Run `python tools/check_render_toolchain.py --run-id "
                + run_id
                + " --write-default` and resolve missing tools before accepting a manuscript.",
            )
        )
        return findings
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        findings.append(
            Finding(
                "major",
                "presentation_gate",
                run_id,
                rel(path, root),
                "`render_toolchain_report.json` could not be parsed.",
            )
        )
        return findings
    if payload.get("status") != "pass":
        missing_commands = payload.get("missing_commands") or []
        missing_packages = payload.get("missing_latex_packages") or []
        hints = payload.get("installation_hints") or []
        detail = []
        if missing_commands:
            detail.append("missing commands: " + ", ".join(str(item) for item in missing_commands))
        if missing_packages:
            detail.append("missing LaTeX packages: " + ", ".join(str(item) for item in missing_packages[:8]))
        if hints:
            detail.append("install hints: " + " ".join(str(item) for item in hints[:3]))
        findings.append(
            Finding(
                "major",
                "presentation_gate",
                run_id,
                rel(path, root),
                "Rendering toolchain is not ready for publication-quality manuscript QA"
                + (": " + "; ".join(detail) if detail else "."),
            )
        )
    return findings


def read_compute_budget_contract(root: Path, run_id: str) -> tuple[dict[str, float | int | None], list[Finding]]:
    settings: dict[str, float | int | None] = {
        "minimum_cpu_core_hours_per_researcher": None,
        "target_cpu_core_hours_per_researcher": None,
        "minimum_experiment_rows_per_researcher": None,
    }
    findings: list[Finding] = []
    run_dir = root / "runs" / run_id
    json_path = run_dir / "compute_budget.json"
    md_path = run_dir / "compute_budget.md"

    payload: Any = None
    text = ""
    path = json_path if json_path.is_file() else md_path
    if json_path.is_file():
        try:
            payload = json.loads(json_path.read_text(encoding="utf-8"))
        except Exception:
            findings.append(
                Finding(
                    "major",
                    "compute_budget",
                    run_id,
                    rel(json_path, root),
                    "`compute_budget.json` could not be parsed.",
                )
            )
    elif md_path.is_file():
        text = md_path.read_text(encoding="utf-8", errors="replace")

    def read_number(key: str) -> float | None:
        if isinstance(payload, dict) and key in payload:
            try:
                return float(payload[key])
            except (TypeError, ValueError):
                return None
        match = re.search(rf"^\s*{re.escape(key)}\s*:\s*([0-9]+(?:\.[0-9]+)?)\s*$", text, flags=re.MULTILINE)
        if match:
            return float(match.group(1))
        return None

    minimum = read_number("minimum_cpu_core_hours_per_researcher")
    target = read_number("target_cpu_core_hours_per_researcher")
    experiments = read_number("minimum_experiment_rows_per_researcher")

    if target is None and text:
        match = re.search(r"typical target\s*:.*?([0-9]+(?:\.[0-9]+)?)\s*CPU-core\s+hours", text, flags=re.IGNORECASE | re.DOTALL)
        if match:
            target = float(match.group(1))

    settings["minimum_cpu_core_hours_per_researcher"] = minimum
    settings["target_cpu_core_hours_per_researcher"] = target
    settings["minimum_experiment_rows_per_researcher"] = int(experiments) if experiments is not None else None

    missing = [
        key
        for key in [
            "minimum_cpu_core_hours_per_researcher",
            "target_cpu_core_hours_per_researcher",
            "minimum_experiment_rows_per_researcher",
        ]
        if settings[key] is None
    ]
    if path.is_file() and missing:
        findings.append(
            Finding(
                "major",
                "compute_budget",
                run_id,
                rel(path, root),
                "Missing structured compute-budget setting(s): " + ", ".join(missing) + ".",
            )
        )
    return settings, findings


def latest_revision(submission_dir: Path) -> Path | None:
    revisions = revision_dirs_for_submission(submission_dir)
    if not revisions:
        return None
    return revisions[-1]


def revision_number(path: Path) -> int:
    match = re.search(r"revision_(\d+)$", path.name)
    return int(match.group(1)) if match else -1


def first_existing(folder: Path, names: list[str]) -> Path | None:
    for name in names:
        path = folder / name
        if path.is_file():
            return path
    return None


def structured_values(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    if path.suffix == ".json":
        try:
            payload = read_json(path)
        except Exception:
            return {}
        if isinstance(payload, dict):
            return {str(key).lower(): str(value) for key, value in payload.items() if not isinstance(value, (dict, list))}
        return {}
    return parse_key_values(path.read_text(encoding="utf-8", errors="replace"))


def count_registry_rows(path: Path) -> int | None:
    if not path.exists():
        return None
    if path.suffix == ".json":
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None
        if isinstance(payload, list):
            return len(payload)
        if isinstance(payload, dict):
            for key in ["experiments", "rows", "items"]:
                value = payload.get(key)
                if isinstance(value, list):
                    return len(value)
        return None
    if path.suffix == ".csv":
        try:
            with path.open(newline="", encoding="utf-8") as handle:
                return max(sum(1 for _ in csv.DictReader(handle)), 0)
        except Exception:
            return None
    return None


def numeric_value(mapping: dict[str, Any], keys: list[str]) -> float | None:
    for key in keys:
        try:
            return float(mapping.get(key, ""))
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
    row_count = len(items)
    total_rows = [row for row in items if is_total_compute_row(row)]
    rows_to_sum = total_rows if total_rows else items
    total = 0.0
    for row in rows_to_sum:
        value = numeric_value(row, ["estimated_cpu_core_hours", "cpu_core_hours", "core_hours"])
        if value is not None:
            total += value
    return total, row_count


def compute_log_file_summary(csv_path: Path, json_path: Path) -> tuple[float, int]:
    if csv_path.is_file():
        try:
            with csv_path.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
        except Exception:
            return 0.0, 0
        return summarize_compute_items(rows)
    if json_path.is_file():
        try:
            payload = json.loads(json_path.read_text(encoding="utf-8"))
        except Exception:
            return 0.0, 0
        if isinstance(payload, list):
            items = payload
        elif isinstance(payload, dict):
            items = payload.get("rows") or payload.get("compute_log") or [payload]
        else:
            items = []
        return summarize_compute_items([item for item in items if isinstance(item, dict)])
    return 0.0, 0


def compute_log_summary(revision: Path) -> tuple[float, int]:
    return compute_log_file_summary(revision / "compute_log.csv", revision / "compute_log.json")


def compute_estimate_values(path: Path) -> dict[str, float]:
    if not path.is_file():
        return {}
    text = path.read_text(encoding="utf-8", errors="replace")
    values: dict[str, float] = {}
    for key in [
        "estimated_cpu_core_hours_low",
        "estimated_cpu_core_hours_expected",
        "estimated_cpu_core_hours_high",
        "estimated_gpu_hours_low",
        "estimated_gpu_hours_expected",
        "estimated_gpu_hours_high",
    ]:
        match = re.search(rf"^\s*{re.escape(key)}\s*:\s*([0-9]+(?:\.[0-9]+)?)\s*$", text, flags=re.MULTILINE)
        if match:
            values[key] = float(match.group(1))
    return values


def read_selected_article_type(root: Path, run_id: str) -> str:
    for path in [root / "runs" / run_id / "article_type_contract.md", root / "runs" / run_id / "compute_budget.md"]:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern in [
            r"^\s*selected_article_type\s*:\s*(.+?)\s*$",
            r"^\s*selected article type\s*:\s*(.+?)\s*$",
        ]:
            match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
            if match:
                value = match.group(1).strip().strip("`")
                if "<" in value or "|" in value:
                    continue
                return value
    return ""


def is_full_article_type(article_type: str) -> bool:
    normalized = article_type.lower()
    return "full" in normalized and ("article" in normalized or "analysis" in normalized or "research" in normalized)


def is_demo_article_type(article_type: str) -> bool:
    normalized = article_type.lower()
    return any(token in normalized for token in ["demo", "compact", "smoke", "internal"])


def revision_dirs_for_submission(submission_dir: Path) -> list[Path]:
    return sorted((p for p in submission_dir.glob("revision_*") if p.is_dir()), key=lambda path: (revision_number(path), path.name))


def normalize_table_key(value: str) -> str:
    key = re.sub(r"`", "", value.strip().lower())
    key = re.sub(r"[^a-z0-9]+", "_", key).strip("_")
    return key


def parse_number(value: Any) -> float | None:
    if value is None:
        return None
    match = re.search(r"-?[0-9]+(?:\.[0-9]+)?", str(value))
    if not match:
        return None
    try:
        return float(match.group(0))
    except ValueError:
        return None


def markdown_compute_component_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    rows: list[dict[str, str]] = []
    header: list[str] | None = None
    for line in text.splitlines():
        if "|" not in line:
            header = None
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not cells:
            continue
        if all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells):
            continue
        normalized = [normalize_table_key(cell) for cell in cells]
        if header is None:
            if "component" in normalized and (
                "estimated_cpu_core_hours" in normalized or "expected_cpu_core_hours" in normalized
            ):
                header = normalized
            continue
        padded = cells + [""] * max(0, len(header) - len(cells))
        row = {header[index]: padded[index].strip() for index in range(len(header))}
        if row.get("component"):
            rows.append(row)
    return rows


def component_estimate(row: dict[str, str]) -> float | None:
    return parse_number(row.get("estimated_cpu_core_hours") or row.get("expected_cpu_core_hours"))


def audit_compute_estimate_quality(
    root: Path,
    subject: str,
    estimate_path: Path,
    estimate_values: dict[str, float],
    compute_settings: dict[str, float | int | None],
    article_type: str,
) -> list[Finding]:
    findings: list[Finding] = []
    expected = estimate_values.get("estimated_cpu_core_hours_expected")
    high = estimate_values.get("estimated_cpu_core_hours_high")
    target = compute_settings.get("target_cpu_core_hours_per_researcher")
    target_float = float(target) if target is not None else None

    if is_full_article_type(article_type) and target_float is not None:
        if expected is not None and expected < target_float * 0.8:
            findings.append(
                Finding(
                    "major",
                    "proposal_gate",
                    subject,
                    rel(estimate_path, root),
                    f"Full Article/Analysis proposal estimates {expected:.6f} expected CPU-core hours, below 80% of target {target_float:.6f}; the Board should require a stronger plan, downgrade, or run-budget revision before analysis.",
                )
            )
        if high is not None and high < target_float:
            findings.append(
                Finding(
                    "major",
                    "proposal_gate",
                    subject,
                    rel(estimate_path, root),
                    f"Full Article/Analysis proposal high estimate {high:.6f} CPU-core hours is below target {target_float:.6f}; the target is not plausibly reachable under the proposed plan.",
                )
            )

    component_rows = markdown_compute_component_rows(estimate_path)
    if not component_rows:
        findings.append(
            Finding(
                "major",
                "proposal_gate",
                subject,
                rel(estimate_path, root),
                "Compute estimate has no parseable component table with `component` and `estimated_cpu_core_hours`/`expected_cpu_core_hours` columns.",
            )
        )
        return findings

    component_sum = 0.0
    for row in component_rows:
        estimated = component_estimate(row)
        if estimated is None or estimated <= 0:
            continue
        component_sum += estimated
        pilot_seconds = parse_number(row.get("pilot_seconds"))
        scale_factor = parse_number(row.get("scale_factor"))
        repeats = parse_number(row.get("planned_repeats")) or 1.0
        cores = parse_number(row.get("effective_cpu_cores")) or 1.0
        risk = parse_number(row.get("risk_multiplier")) or 1.0
        component_name = row.get("component", "unknown_component")
        large_component = False
        if expected is not None and expected > 0 and estimated >= expected * 0.2:
            large_component = True
        if target_float is not None and estimated >= target_float * 0.1:
            large_component = True
        measured = pilot_seconds is not None and pilot_seconds > 0 and scale_factor is not None and scale_factor > 0
        if large_component and not measured:
            findings.append(
                Finding(
                    "major",
                    "proposal_gate",
                    subject,
                    rel(estimate_path, root),
                    f"Large compute component `{component_name}` estimates {estimated:.6f} CPU-core hours without positive `pilot_seconds` and `scale_factor`; add a timing probe or reduce the claim.",
                )
            )
        if measured:
            formula_estimate = pilot_seconds * scale_factor * repeats * cores * risk / 3600.0
            tolerance = max(0.01, abs(formula_estimate) * 0.25)
            if abs(estimated - formula_estimate) > tolerance:
                findings.append(
                    Finding(
                        "major",
                        "proposal_gate",
                        subject,
                        rel(estimate_path, root),
                        f"Compute component `{component_name}` estimate {estimated:.6f} does not match formula result {formula_estimate:.6f} within 25% tolerance.",
                    )
                )

    if expected is not None and expected > 0 and component_sum > 0:
        tolerance = max(0.01, expected * 0.25)
        if abs(component_sum - expected) > tolerance:
            findings.append(
                Finding(
                    "major",
                    "proposal_gate",
                    subject,
                    rel(estimate_path, root),
                    f"Structured expected compute {expected:.6f} differs from component-table sum {component_sum:.6f} by more than 25%.",
                )
            )
    return findings


def normalize_issue_status(status: str) -> str:
    normalized = status.strip().lower()
    return STATUS_NORMALIZATION.get(normalized, normalized)


def read_issue_ledger(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    if path.suffix == ".json":
        try:
            payload = read_json(path)
        except Exception:
            return {}
        issues = payload.get("issues") if isinstance(payload, dict) else payload
        if not isinstance(issues, list):
            return {}
        rows = {}
        for row in issues:
            if not isinstance(row, dict):
                continue
            issue_id = str(row.get("issue_id", "")).strip()
            status = str(row.get("status", "")).strip()
            if issue_id:
                rows[issue_id] = status
        return rows

    rows: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.lstrip().startswith("|") or "---" in line:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 4 or cells[0].lower() == "issue_id":
            continue
        rows[cells[0]] = cells[3]
    return rows


def read_verification_statuses(latest: Path) -> dict[str, str]:
    matrix = first_existing(latest, ["verification_matrix.csv", "verification_matrix.json"])
    if matrix is None:
        return {}
    rows: list[dict[str, Any]] = []
    if matrix.suffix == ".csv":
        try:
            with matrix.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
        except Exception:
            return {}
    else:
        try:
            payload = read_json(matrix)
        except Exception:
            return {}
        if isinstance(payload, list):
            rows = [row for row in payload if isinstance(row, dict)]
        elif isinstance(payload, dict):
            values = payload.get("rows") or payload.get("verification_matrix") or payload.get("issues")
            if isinstance(values, list):
                rows = [row for row in values if isinstance(row, dict)]
    statuses: dict[str, str] = {}
    for row in rows:
        issue_id = str(row.get("issue_id", "")).strip()
        status = str(row.get("verification_status") or row.get("status") or row.get("resolution_status") or "").strip()
        if issue_id:
            statuses[issue_id] = status
    return statuses


def audit_issue_lifecycle(root: Path, subject: str, latest: Path) -> list[Finding]:
    findings: list[Finding] = []
    ledger_path = first_existing(latest, ["issue_ledger.json", "issue_ledger.md"])
    if ledger_path is None:
        return findings
    ledger = read_issue_ledger(ledger_path)
    matrix = read_verification_statuses(latest)
    for issue_id, raw_status in ledger.items():
        normalized = normalize_issue_status(raw_status)
        if normalized not in ISSUE_LIFECYCLE_STATUSES:
            findings.append(
                Finding(
                    "major",
                    "issue_lifecycle",
                    subject,
                    rel(ledger_path, root),
                    f"Issue `{issue_id}` has unsupported ledger status `{raw_status}`. Use one of {', '.join(sorted(ISSUE_LIFECYCLE_STATUSES))}.",
                )
            )
        if issue_id in matrix:
            matrix_status = normalize_issue_status(matrix[issue_id])
            if normalized != matrix_status:
                findings.append(
                    Finding(
                        "major",
                        "issue_lifecycle",
                        subject,
                        rel(ledger_path, root),
                        f"Issue `{issue_id}` ledger status `{raw_status}` disagrees with verification-matrix status `{matrix[issue_id]}`. The issue ledger must be the canonical reviewer-owned lifecycle record.",
                    )
                )
    for issue_id in sorted(set(matrix) - set(ledger)):
        findings.append(
            Finding(
                "major",
                "issue_lifecycle",
                subject,
                rel(latest, root),
                f"Verification matrix contains issue `{issue_id}` but the issue ledger has no matching lifecycle row.",
            )
        )
    return findings


def read_compute_reconciliation(latest: Path) -> tuple[Path | None, dict[str, str]]:
    path = first_existing(latest, ["compute_reconciliation.json", "compute_reconciliation.md"])
    if path is None:
        return None, {}
    return path, structured_values(path)


def read_empirical_provenance(latest: Path) -> tuple[Path | None, dict[str, str]]:
    path = latest / "empirical_provenance.json"
    if not path.is_file():
        return None, {}
    try:
        payload = read_json(path)
    except Exception:
        return path, {}
    if not isinstance(payload, dict):
        return path, {}
    values: dict[str, str] = {}
    for key, value in payload.items():
        if isinstance(value, (str, int, float, bool)):
            values[str(key).lower()] = str(value)
    return path, values


def compute_log_command_paths(revision: Path) -> list[str]:
    commands: list[str] = []
    csv_path = revision / "compute_log.csv"
    json_path = revision / "compute_log.json"
    if csv_path.is_file():
        try:
            with csv_path.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
        except Exception:
            rows = []
        for row in rows:
            value = row.get("command_or_script") or row.get("command") or row.get("script")
            if value:
                commands.append(str(value))
    elif json_path.is_file():
        try:
            payload = read_json(json_path)
        except Exception:
            payload = None
        if isinstance(payload, list):
            rows = payload
        elif isinstance(payload, dict):
            rows = payload.get("rows") or payload.get("compute_log") or [payload]
        else:
            rows = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            value = row.get("command_or_script") or row.get("command") or row.get("script")
            if value:
                commands.append(str(value))
    return commands


def audit_empirical_provenance(root: Path, subject: str, latest: Path) -> list[Finding]:
    findings: list[Finding] = []
    if revision_number(latest) <= 0:
        return findings

    revision_plan = latest / "revision_plan.md"
    plan_values = structured_values(revision_plan) if revision_plan.is_file() else {}
    revision_type = plan_values.get("revision_type", "")
    research_delta_tier = plan_values.get("research_delta_tier", "")
    if not revision_type:
        findings.append(
            Finding(
                "major",
                "revision_provenance",
                subject,
                rel(revision_plan, root),
                "Revisions after `revision_00` must declare `revision_type` as one of "
                + ", ".join(sorted(REVISION_TYPES))
                + ".",
            )
        )
    elif revision_type not in REVISION_TYPES:
        findings.append(
            Finding(
                "major",
                "revision_provenance",
                subject,
                rel(revision_plan, root),
                f"Unsupported revision_type `{revision_type}`. Use one of {', '.join(sorted(REVISION_TYPES))}.",
            )
        )

    if not research_delta_tier:
        findings.append(
            Finding(
                "major",
                "revision_material_delta",
                subject,
                rel(revision_plan, root),
                "Revisions after `revision_00` must declare `research_delta_tier` as one of "
                + ", ".join(sorted(RESEARCH_DELTA_TIERS))
                + ".",
            )
        )
    elif research_delta_tier not in RESEARCH_DELTA_TIERS:
        findings.append(
            Finding(
                "major",
                "revision_material_delta",
                subject,
                rel(revision_plan, root),
                f"Unsupported research_delta_tier `{research_delta_tier}`. Use one of {', '.join(sorted(RESEARCH_DELTA_TIERS))}.",
            )
        )
    if research_delta_tier == "tier_c_nonmaterial" and revision_type in {"empirical_revision", "mixed_revision"}:
        findings.append(
            Finding(
                "major",
                "revision_material_delta",
                subject,
                rel(revision_plan, root),
                "`tier_c_nonmaterial` is inconsistent with an empirical or mixed revision unless the plan explicitly says no central empirical issue is being resolved.",
            )
        )

    provenance_path, provenance = read_empirical_provenance(latest)
    provenance_status = provenance.get("empirical_status", "")
    if provenance_path is None:
        findings.append(
            Finding(
                "major",
                "revision_provenance",
                subject,
                rel(latest / "empirical_provenance.json", root),
                "Revisions after `revision_00` must include `empirical_provenance.json` declaring whether empirical artifacts were rerun, copied forward, or unchanged.",
            )
        )
        provenance = {}
    elif not provenance:
        findings.append(
            Finding(
                "major",
                "revision_provenance",
                subject,
                rel(provenance_path, root),
                "`empirical_provenance.json` could not be parsed as a flat JSON object.",
            )
        )
    elif provenance_status not in EMPIRICAL_PROVENANCE_STATUSES:
        findings.append(
            Finding(
                "major",
                "revision_provenance",
                subject,
                rel(provenance_path, root),
                f"Unsupported empirical_status `{provenance_status}`. Use one of {', '.join(sorted(EMPIRICAL_PROVENANCE_STATUSES))}.",
            )
        )

    copied_or_unchanged = provenance_status in {"copied_forward", "unchanged_from_previous"}
    material_delta = latest / "material_research_delta.md"
    if research_delta_tier in {"tier_a_material", "tier_b_supporting"}:
        if not nonempty_file(material_delta):
            findings.append(
                Finding(
                    "major",
                    "revision_material_delta",
                    subject,
                    rel(material_delta, root),
                    f"`{research_delta_tier}` revisions must include `material_research_delta.md` summarizing the research-state change, failed/null attempts, claim consequences, and issue map.",
                )
            )
        else:
            delta_values = structured_values(material_delta)
            delta_tier = delta_values.get("research_delta_tier", "")
            if delta_tier and delta_tier != research_delta_tier:
                findings.append(
                    Finding(
                        "major",
                        "revision_material_delta",
                        subject,
                        rel(material_delta, root),
                        f"`material_research_delta.md` declares research_delta_tier `{delta_tier}` but `revision_plan.md` declares `{research_delta_tier}`.",
                    )
                )
        if copied_or_unchanged:
            findings.append(
                Finding(
                    "major",
                    "revision_material_delta",
                    subject,
                    rel(provenance_path or (latest / "empirical_provenance.json"), root),
                    f"`{research_delta_tier}` claims material/supporting research change, but empirical provenance is `{provenance_status}`. The revision must justify how the research state changed without rerun empirical artifacts, revise the tier, downgrade, or reject.",
                )
            )
    elif research_delta_tier == "tier_c_nonmaterial" and nonempty_file(material_delta):
        delta_values = structured_values(material_delta)
        delta_tier = delta_values.get("research_delta_tier", "")
        if delta_tier in {"tier_a_material", "tier_b_supporting"}:
            findings.append(
                Finding(
                    "major",
                    "revision_material_delta",
                    subject,
                    rel(material_delta, root),
                    f"`revision_plan.md` declares `tier_c_nonmaterial`, but `material_research_delta.md` declares `{delta_tier}`.",
                )
            )

    results_path = latest / "results.json"
    if results_path.is_file():
        try:
            results = read_json(results_path)
        except Exception:
            results = None
        if isinstance(results, dict):
            result_revision = str(results.get("revision", ""))
            if result_revision and result_revision != latest.name and not copied_or_unchanged:
                findings.append(
                    Finding(
                        "major",
                        "revision_provenance",
                        subject,
                        rel(results_path, root),
                        f"`results.json` reports revision `{result_revision}` but is stored under `{latest.name}`. Either update the metadata or declare copied-forward empirical provenance.",
                    )
                )

    stale_commands = [
        command
        for command in compute_log_command_paths(latest)
        if "revision_" in command and latest.name not in command
    ]
    if stale_commands and not copied_or_unchanged:
        findings.append(
            Finding(
                "major",
                "revision_provenance",
                subject,
                rel(latest / "compute_log.csv", root),
                "Compute log command paths reference a previous revision without copied-forward empirical provenance: "
                + "; ".join(stale_commands[:3])
                + ".",
            )
        )
    return findings


def audit_run_contracts(root: Path, run_id: str) -> list[Finding]:
    findings: list[Finding] = []
    run_dir = root / "runs" / run_id
    for name in BUNDLED_FONT_FILES:
        path = root / BUNDLED_FONT_DIR / name
        if not nonempty_file(path):
            findings.append(
                Finding(
                    "major",
                    "presentation_gate",
                    run_id,
                    rel(path, root),
                    f"Missing bundled open-source font artifact `{name}`.",
                )
            )
    for name in RUN_REQUIRED:
        path = run_dir / name
        if not nonempty_file(path):
            findings.append(
                Finding(
                    "blocking",
                    "run_contract",
                    run_id,
                    rel(path, root),
                    f"Missing required run contract `{name}`.",
                )
            )
    for label, names in RUN_REQUIRED_ANY:
        if not has_any(run_dir, names):
            findings.append(
                Finding(
                    "blocking",
                    "run_contract",
                    run_id,
                    rel(run_dir, root),
                    f"Missing required run contract for `{label}`; expected one of {', '.join(names)}.",
                )
            )
    return findings


def audit_integrated_article_pdf(root: Path, subject: str, latest: Path) -> list[Finding]:
    findings: list[Finding] = []
    article_pdf = latest / "article" / "article.pdf"
    article_report = latest / "article" / "article_build_report.json"
    if not nonempty_file(article_pdf):
        findings.append(
            Finding(
                "major",
                "presentation_gate",
                subject,
                rel(article_pdf, root),
                "Missing required integrated article PDF. Run `python tools/build_article_pdf.py <revision_dir> --conda-env ag`.",
            )
        )
    if not nonempty_file(article_report):
        findings.append(
            Finding(
                "major",
                "presentation_gate",
                subject,
                rel(article_report, root),
                "Missing required integrated article build report.",
            )
        )
        return findings
    try:
        payload = read_json(article_report)
    except Exception as exc:
        findings.append(
            Finding(
                "major",
                "presentation_gate",
                subject,
                rel(article_report, root),
                f"Integrated article build report could not be parsed: {exc}.",
            )
        )
        return findings
    if str(payload.get("status", "")).lower() != "pass":
        findings.append(
            Finding(
                "major",
                "presentation_gate",
                subject,
                rel(article_report, root),
                "Integrated article build report must declare `status: pass`.",
            )
        )
    if str(payload.get("renderer", "")).lower() != "pandoc-xelatex":
        findings.append(
            Finding(
                "major",
                "presentation_gate",
                subject,
                rel(article_report, root),
                "Integrated article must be rendered with Pandoc/XeLaTeX for publication-style output.",
            )
        )
    if str(payload.get("brand_logo", "")) != EXPECTED_ARTICLE_BRAND_LOGO:
        findings.append(
            Finding(
                "major",
                "presentation_gate",
                subject,
                rel(article_report, root),
                "Integrated article build report must declare "
                f"`brand_logo: {EXPECTED_ARTICLE_BRAND_LOGO}` for the Research Arena Evidence Gain masthead.",
            )
        )
    figure_flag_count = int(payload.get("figure_presentation_flag_count", 0) or 0)
    if figure_flag_count:
        findings.append(
            Finding(
                "major",
                "presentation_gate",
                subject,
                rel(article_report, root),
                f"Integrated article build report declares {figure_flag_count} figure presentation flag(s). Rebuild figures with article-normalized typography or reduce panel density.",
            )
        )
    if payload.get("included_figures"):
        figure_audit = latest / "figure_presentation_audit.json"
        if not nonempty_file(figure_audit):
            findings.append(
                Finding(
                    "major",
                    "presentation_gate",
                    subject,
                    rel(figure_audit, root),
                    "Missing figure presentation audit for an integrated article with included figures.",
                )
            )
        else:
            try:
                audit_payload = read_json(figure_audit)
            except Exception as exc:
                findings.append(
                    Finding(
                        "major",
                        "presentation_gate",
                        subject,
                        rel(figure_audit, root),
                        f"Figure presentation audit could not be parsed: {exc}.",
                    )
                )
            else:
                if str(audit_payload.get("status", "")).lower() != "pass":
                    findings.append(
                        Finding(
                            "major",
                            "presentation_gate",
                            subject,
                            rel(figure_audit, root),
                            "Figure presentation audit must declare `status: pass` before article acceptance.",
                        )
                    )
    return findings


def audit_submission(
    root: Path,
    run_id: str,
    submission_dir: Path,
    quality_settings: dict[str, int | bool],
    compute_settings: dict[str, float | int | None],
    article_type: str,
) -> list[Finding]:
    findings: list[Finding] = []
    subject = submission_dir.name
    proposal_gate = submission_dir / "proposal_gate"
    initial = submission_dir / "revision_00"
    latest = latest_revision(submission_dir)
    all_revisions = revision_dirs_for_submission(submission_dir)
    proposal_estimate_values: dict[str, float] = {}
    if latest is None:
        return [
            Finding(
                "blocking",
                "submission",
                subject,
                rel(submission_dir, root),
                "No revision_* folders found.",
            )
        ]

    if bool(quality_settings.get("require_integrated_article_pdf", True)):
        for revision_dir in all_revisions:
            findings.extend(audit_integrated_article_pdf(root, f"{subject}/{revision_dir.name}", revision_dir))

    if not proposal_gate.is_dir():
        findings.append(
            Finding(
                "blocking",
                "proposal_gate",
                subject,
                rel(proposal_gate, root),
                "Missing `proposal_gate/`; pre-analysis study design cannot be audited.",
            )
        )
    else:
        for name in PROPOSAL_GATE_REQUIRED:
            path = proposal_gate / name
            if not nonempty_file(path):
                findings.append(
                    Finding(
                        "blocking",
                        "proposal_gate",
                        subject,
                        rel(path, root),
                        f"Missing required proposal-gate artifact `{name}`.",
                    )
                )
        for label, names in PROPOSAL_GATE_REQUIRED_ANY:
            if not has_any(proposal_gate, names):
                findings.append(
                    Finding(
                        "blocking",
                        "proposal_gate",
                        subject,
                        rel(proposal_gate, root),
                        f"Missing required proposal-gate artifact for `{label}`; expected one of {', '.join(names)}.",
                    )
                )
        pilot_total, pilot_rows = compute_log_file_summary(
            proposal_gate / "pilot_compute_log.csv",
            proposal_gate / "pilot_compute_log.json",
        )
        if pilot_rows == 0:
            findings.append(
                Finding(
                    "major",
                    "proposal_gate",
                    subject,
                    rel(proposal_gate, root),
                    "Pilot compute log has no parseable rows; the proposal compute estimate is not empirically grounded.",
                )
            )
        elif pilot_total <= 0:
            findings.append(
                Finding(
                    "major",
                    "proposal_gate",
                    subject,
                    rel(proposal_gate, root),
                    "Pilot compute log records no positive CPU-core-hour evidence.",
                )
            )
        estimate_path = proposal_gate / "compute_budget_estimate.md"
        if estimate_path.is_file():
            estimate_values = compute_estimate_values(estimate_path)
            proposal_estimate_values = estimate_values
            required_estimate_fields = [
                "estimated_cpu_core_hours_low",
                "estimated_cpu_core_hours_expected",
                "estimated_cpu_core_hours_high",
            ]
            missing_estimate_fields = [key for key in required_estimate_fields if key not in estimate_values]
            if missing_estimate_fields:
                findings.append(
                    Finding(
                        "major",
                        "proposal_gate",
                        subject,
                        rel(estimate_path, root),
                        "Missing structured compute-estimate field(s): " + ", ".join(missing_estimate_fields) + ".",
                    )
                )
            low = estimate_values.get("estimated_cpu_core_hours_low")
            expected = estimate_values.get("estimated_cpu_core_hours_expected")
            high = estimate_values.get("estimated_cpu_core_hours_high")
            if low is not None and expected is not None and high is not None and not (low <= expected <= high):
                findings.append(
                    Finding(
                        "major",
                        "proposal_gate",
                        subject,
                        rel(estimate_path, root),
                        "Compute estimate must satisfy low <= expected <= high for CPU-core hours.",
                    )
                )
            target_cpu = compute_settings.get("target_cpu_core_hours_per_researcher")
            if target_cpu is not None and expected is not None and expected < float(target_cpu):
                findings.append(
                    Finding(
                        "major",
                        "proposal_gate",
                        subject,
                        rel(estimate_path, root),
                        f"Proposal estimates {expected:.6f} expected CPU-core hours, below `target_cpu_core_hours_per_researcher` {float(target_cpu):.6f}; Study Design Board must document a downgrade, stronger plan, or override.",
                    )
                )
            findings.extend(audit_compute_estimate_quality(root, subject, estimate_path, estimate_values, compute_settings, article_type))

    if not initial.is_dir():
        findings.append(
            Finding(
                "blocking",
                "first_submission",
                subject,
                rel(initial, root),
                "Missing `revision_00`; initial research baseline cannot be audited.",
            )
        )
    else:
        for name in INITIAL_REQUIRED:
            path = initial / name
            if not nonempty_file(path):
                findings.append(
                    Finding(
                        "blocking",
                        "first_submission",
                        subject,
                        rel(path, root),
                        f"Missing required first-submission artifact `{name}`.",
                    )
                )
        for label, names in INITIAL_REQUIRED_ANY:
            if not has_any(initial, names):
                findings.append(
                    Finding(
                        "blocking",
                        "first_submission",
                        subject,
                        rel(initial, root),
                        f"Missing required first-submission artifact for `{label}`; expected one of {', '.join(names)}.",
                    )
                )
        for registry_name in ["experiment_registry.csv", "experiment_registry.json"]:
            registry_path = initial / registry_name
            rows = count_registry_rows(registry_path)
            if rows == 0:
                findings.append(
                    Finding(
                        "major",
                        "experiment_registry",
                        subject,
                        rel(registry_path, root),
                        "Experiment registry exists but has no experiment rows.",
                    )
                )

    for name in LATEST_REQUIRED:
        path = latest / name
        if not nonempty_file(path):
            findings.append(
                Finding(
                    "blocking",
                    "latest_revision",
                    subject,
                    rel(path, root),
                    f"Missing required latest-revision artifact `{name}`.",
                )
            )
    for label, names in LATEST_REQUIRED_ANY:
        if not has_any(latest, names):
            findings.append(
                Finding(
                    "blocking",
                    "latest_revision",
                    subject,
                    rel(latest, root),
                    f"Missing required latest-revision artifact for `{label}`; expected one of {', '.join(names)}.",
                )
            )

    findings.extend(audit_empirical_provenance(root, subject, latest))
    findings.extend(audit_issue_lifecycle(root, subject, latest))

    latest_compute_total, latest_compute_rows = compute_log_summary(latest)
    minimum_cpu = compute_settings.get("minimum_cpu_core_hours_per_researcher")
    target_cpu = compute_settings.get("target_cpu_core_hours_per_researcher")
    proposal_expected_cpu = proposal_estimate_values.get("estimated_cpu_core_hours_expected")
    reconciliation_needed_reasons: list[str] = []
    if minimum_cpu is not None and latest_compute_total < float(minimum_cpu):
        findings.append(
            Finding(
                "major",
                "compute_budget",
                subject,
                rel(latest, root),
                f"Latest revision records {latest_compute_total:.6f} CPU-core hours, below `minimum_cpu_core_hours_per_researcher` {float(minimum_cpu):.6f}.",
            )
        )
    if target_cpu is not None and latest_compute_total < float(target_cpu):
        reconciliation_needed_reasons.append(
            f"actual {latest_compute_total:.6f} CPU-core hours is below target {float(target_cpu):.6f}"
        )
    if proposal_expected_cpu is not None and proposal_expected_cpu > 0:
        if latest_compute_total < proposal_expected_cpu * 0.5:
            reconciliation_needed_reasons.append(
                f"actual {latest_compute_total:.6f} CPU-core hours is less than 50% of proposal expected {proposal_expected_cpu:.6f}"
            )
        elif latest_compute_total > proposal_expected_cpu * 1.5:
            reconciliation_needed_reasons.append(
                f"actual {latest_compute_total:.6f} CPU-core hours is more than 150% of proposal expected {proposal_expected_cpu:.6f}"
            )
    if reconciliation_needed_reasons:
        reconciliation_path, reconciliation = read_compute_reconciliation(latest)
        if reconciliation_path is None:
            findings.append(
                Finding(
                    "major",
                    "compute_budget",
                    subject,
                    rel(latest / "compute_reconciliation.md", root),
                    "Compute reconciliation is required because "
                    + "; ".join(reconciliation_needed_reasons)
                    + ". Add `compute_reconciliation.md` or `.json` with `compute_outcome`.",
                )
            )
        else:
            outcome = reconciliation.get("compute_outcome", "")
            if outcome not in COMPUTE_OUTCOMES:
                findings.append(
                    Finding(
                        "major",
                        "compute_budget",
                        subject,
                        rel(reconciliation_path, root),
                        f"`compute_outcome` must be one of {', '.join(sorted(COMPUTE_OUTCOMES))}; found `{outcome}`.",
                    )
                )
            elif target_cpu is not None and latest_compute_total < float(target_cpu):
                if outcome == "compute_target_met":
                    findings.append(
                        Finding(
                            "major",
                            "compute_budget",
                            subject,
                            rel(reconciliation_path, root),
                            "`compute_outcome` says target met, but latest compute is below the target.",
                        )
                    )
                elif outcome == "compute_under_target_blocks_acceptance":
                    findings.append(
                        Finding(
                            "blocking",
                            "compute_budget",
                            subject,
                            rel(reconciliation_path, root),
                            "Compute reconciliation declares `compute_under_target_blocks_acceptance`; the Editor must not accept this submission without new evidence or a revised reconciliation.",
                        )
                    )
                elif outcome == "compute_under_target_requires_downgrade":
                    findings.append(
                        Finding(
                            "major",
                            "compute_budget",
                            subject,
                            rel(reconciliation_path, root),
                            "Compute reconciliation declares `compute_under_target_requires_downgrade`; acceptance requires a formal article-type downgrade in the run contracts and final decision.",
                        )
                    )
                elif outcome == "compute_under_target_with_approved_efficiency_override":
                    required_keys = [
                        "proposed_expected_cpu_core_hours",
                        "actual_cpu_core_hours",
                        "planned_experiment_families",
                        "completed_experiment_families",
                    ]
                    missing = [key for key in required_keys if not reconciliation.get(key)]
                    if missing:
                        findings.append(
                            Finding(
                                "major",
                                "compute_budget",
                                subject,
                                rel(reconciliation_path, root),
                                "Efficiency overrides must include structured reconciliation field(s): "
                                + ", ".join(missing)
                                + ".",
                            )
                        )
    if latest_compute_rows == 0:
        findings.append(
            Finding(
                "major",
                "compute_budget",
                subject,
                rel(latest, root),
                "Latest revision has no parseable compute-log rows.",
            )
        )

    minimum_experiment_rows = compute_settings.get("minimum_experiment_rows_per_researcher")
    if minimum_experiment_rows is not None:
        registry_rows = None
        for registry_name in ["experiment_registry.csv", "experiment_registry.json"]:
            registry_rows = count_registry_rows(latest / registry_name)
            if registry_rows is not None:
                break
        if registry_rows is not None and registry_rows < int(minimum_experiment_rows):
            findings.append(
                Finding(
                    "major",
                    "compute_budget",
                    subject,
                    rel(latest, root),
                    f"Latest experiment registry has {registry_rows} row(s), below `minimum_experiment_rows_per_researcher` {int(minimum_experiment_rows)}.",
                )
            )

    manuscript_path = latest / "manuscript.md"
    manuscript_text = ""
    if nonempty_file(manuscript_path):
        manuscript_text = manuscript_path.read_text(encoding="utf-8", errors="replace")
        manuscript_words = markdown_word_count(manuscript_path)
        minimum_words = int(quality_settings["minimum_manuscript_words"])
        if manuscript_words < minimum_words:
            findings.append(
                Finding(
                    "major",
                    "presentation_gate",
                    subject,
                    rel(manuscript_path, root),
                    f"Manuscript has {manuscript_words} words, below `minimum_manuscript_words` {minimum_words}.",
                )
            )
        headings = markdown_headings(manuscript_text)
        heading_levels = markdown_heading_levels(manuscript_text)
        missing_sections = []
        for label, aliases in REQUIRED_MANUSCRIPT_SECTIONS.items():
            if not any(any(re.search(pattern, heading) for pattern in aliases) for heading in headings):
                missing_sections.append(label)
        if missing_sections:
            findings.append(
                Finding(
                    "major",
                    "presentation_gate",
                    subject,
                    rel(manuscript_path, root),
                    "Manuscript is missing required section(s): " + ", ".join(missing_sections) + ".",
                )
            )
        subsection_count = sum(1 for level, _heading in heading_levels if level >= 2)
        minimum_subsection_count = int(quality_settings["minimum_subsection_count"])
        if subsection_count < minimum_subsection_count:
            findings.append(
                Finding(
                    "major",
                    "presentation_gate",
                    subject,
                    rel(manuscript_path, root),
                    f"Manuscript has {subsection_count} subsection heading(s), below `minimum_subsection_count` {minimum_subsection_count}.",
                )
            )
        methods_words = len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?", section_text(manuscript_text, REQUIRED_MANUSCRIPT_SECTIONS["methods"])))
        minimum_methods_words = int(quality_settings["minimum_methods_words"])
        if methods_words < minimum_methods_words:
            findings.append(
                Finding(
                    "major",
                    "presentation_gate",
                    subject,
                    rel(manuscript_path, root),
                    f"Methods section has {methods_words} words, below `minimum_methods_words` {minimum_methods_words}.",
                )
            )
        equation_summary = equation_numbering_summary(manuscript_text)
        minimum_numbered_equations = int(quality_settings["minimum_numbered_equations"])
        if bool(quality_settings["require_numbered_equations"]):
            if equation_summary["numbered"] < minimum_numbered_equations:
                findings.append(
                    Finding(
                        "major",
                        "presentation_gate",
                        subject,
                        rel(manuscript_path, root),
                        f"Manuscript has {equation_summary['numbered']} numbered display equation(s), below `minimum_numbered_equations` {minimum_numbered_equations}.",
                    )
                )
            if equation_summary["unnumbered"] > 0:
                findings.append(
                    Finding(
                        "major",
                        "presentation_gate",
                        subject,
                        rel(manuscript_path, root),
                        f"Manuscript has {equation_summary['unnumbered']} unnumbered display equation block(s).",
                    )
                )

    style_path = latest / "manuscript_style_manifest.md"
    style_values: dict[str, str] = {}
    if bool(quality_settings["require_manuscript_style_manifest"]):
        if not nonempty_file(style_path):
            findings.append(
                Finding(
                    "major",
                    "presentation_gate",
                    subject,
                    rel(style_path, root),
                    "`manuscript_style_manifest.md` is required by the manuscript-quality contract.",
                )
            )
        else:
            style_values = parse_key_values(style_path.read_text(encoding="utf-8", errors="replace"))
            missing_style_fields = [field for field in STYLE_MANIFEST_FIELDS if field not in style_values]
            if missing_style_fields:
                findings.append(
                    Finding(
                        "major",
                        "presentation_gate",
                        subject,
                        rel(style_path, root),
                        "Style manifest is missing required field(s): " + ", ".join(missing_style_fields) + ".",
                    )
                )
            if bool(quality_settings["require_line_numbers"]):
                value = parse_bool(style_values.get("line_numbers", ""))
                if value is not True:
                    findings.append(
                        Finding(
                            "major",
                            "presentation_gate",
                            subject,
                            rel(style_path, root),
                            "Style manifest must declare `line_numbers: true`.",
                        )
                    )
            if bool(quality_settings["require_numbered_equations"]):
                value = parse_bool(style_values.get("numbered_equations", ""))
                if value is not True:
                    findings.append(
                        Finding(
                            "major",
                            "presentation_gate",
                            subject,
                            rel(style_path, root),
                            "Style manifest must declare `numbered_equations: true`.",
                        )
                    )
            if bool(quality_settings["require_rendered_math"]):
                value = style_values.get("math_rendering_check", "")
                if value.lower() != "pass":
                    findings.append(
                        Finding(
                            "major",
                            "presentation_gate",
                            subject,
                            rel(style_path, root),
                            "Style manifest must declare `math_rendering_check: pass` after visual/PDF inspection confirms equations are rendered, not raw LaTeX text.",
                        )
                    )
            if bool(quality_settings["require_preferred_sans_fonts"]):
                for field in ["manuscript_font_family", "figure_font_family"]:
                    value = style_values.get(field)
                    if value is not None and not uses_preferred_sans_font(value):
                        findings.append(
                            Finding(
                                "major",
                                "presentation_gate",
                                subject,
                                rel(style_path, root),
                                f"`{field}` must name an accepted open-source sans-serif family such as bundled Inter, TeX Gyre Heros, Nimbus Sans, Liberation Sans, Noto Sans, Source Sans 3, or Source Sans Pro.",
                            )
                        )
            for field in ["visual_pdf_review", "figure_typography_review"]:
                if field in style_values and style_values[field].lower() != "pass":
                    findings.append(
                        Finding(
                            "major",
                            "presentation_gate",
                            subject,
                            rel(style_path, root),
                            f"Style manifest must declare `{field}: pass` or record the limitation as a failed presentation gate.",
                        )
                    )
            renderer = style_values.get("pdf_renderer", "").strip().lower()
            if bool(quality_settings.get("require_rendering_toolchain", True)):
                report_value = style_values.get("render_toolchain_report", "").strip()
                if not report_value:
                    findings.append(
                        Finding(
                            "major",
                            "presentation_gate",
                            subject,
                            rel(style_path, root),
                            "Style manifest must cite `render_toolchain_report: runs/<run-id>/render_toolchain_report.json` when the rendering toolchain is required.",
                        )
                    )
            if renderer.startswith("research-arena-") and not bool(quality_settings.get("allow_fallback_renderer", False)):
                findings.append(
                    Finding(
                        "major",
                        "presentation_gate",
                        subject,
                        rel(style_path, root),
                        "`pdf_renderer` declares a Research Arena fallback renderer, but `allow_fallback_renderer` is false in the manuscript-quality contract. Use Pandoc/XeLaTeX or explicitly downgrade the run contract.",
                    )
                )
            if renderer.startswith("research-arena-") and style_values.get("known_style_limits", "").strip().lower() in {"", "none"}:
                findings.append(
                    Finding(
                        "major",
                        "presentation_gate",
                        subject,
                        rel(style_path, root),
                        "Fallback manuscript renderer must be disclosed in `known_style_limits`; do not declare `none` for fallback-rendered manuscripts.",
                    )
                )

    presentation_path = latest / "presentation_checklist.md"
    checklist_values: dict[str, str] = {}
    if nonempty_file(presentation_path):
        checklist = presentation_path.read_text(encoding="utf-8", errors="replace")
        checklist_values = parse_key_values(checklist)
        missing_checklist_fields = [field for field in PRESENTATION_CHECKLIST_FIELDS if field not in checklist_values]
        if missing_checklist_fields:
            findings.append(
                Finding(
                    "major",
                    "presentation_gate",
                    subject,
                    rel(presentation_path, root),
                    "`presentation_checklist.md` is missing required field(s): " + ", ".join(missing_checklist_fields) + ".",
                )
            )
        status_match = re.search(r"^\s*status\s*:\s*(\w+)\s*$", checklist, flags=re.MULTILINE | re.IGNORECASE)
        if not status_match:
            findings.append(
                Finding(
                    "major",
                    "presentation_gate",
                    subject,
                    rel(presentation_path, root),
                    "`presentation_checklist.md` must include `status: pass` or `status: fail`.",
                )
            )
        elif status_match.group(1).lower() != "pass":
            findings.append(
                Finding(
                    "major",
                    "presentation_gate",
                    subject,
                    rel(presentation_path, root),
                    "`presentation_checklist.md` does not declare `status: pass`.",
                )
            )
        pass_fail_fields = [
            "pdf_visual_check",
            "figure_label_check",
            "figure_text_size_normalization_check",
            "figure_mark_scale_check",
            "table_readability_check",
            "display_item_explanation_check",
            "raw_label_translation_check",
            "math_or_method_detail_check",
            "line_number_check",
            "equation_numbering_check",
            "math_rendering_check",
            "inline_math_rendering_check",
            "human_readable_output_check",
            "manuscript_typography_check",
            "figure_typography_check",
        ]
        for field in pass_fail_fields:
            if field in checklist_values and checklist_values[field].lower() != "pass":
                findings.append(
                    Finding(
                        "major",
                        "presentation_gate",
                        subject,
                        rel(presentation_path, root),
                        f"`presentation_checklist.md` declares `{field}: {checklist_values[field]}`.",
                    )
                )
        if "render_toolchain_check" in checklist_values:
            toolchain_value = checklist_values["render_toolchain_check"].strip().lower()
            if bool(quality_settings.get("require_rendering_toolchain", True)):
                if toolchain_value != "pass":
                    findings.append(
                        Finding(
                            "major",
                            "presentation_gate",
                            subject,
                            rel(presentation_path, root),
                            "`presentation_checklist.md` must declare `render_toolchain_check: pass` when the manuscript-quality contract requires the rendering toolchain.",
                        )
                    )
            elif toolchain_value not in {"pass", "waived", "not_required", "not required", "n/a"}:
                findings.append(
                    Finding(
                        "major",
                        "presentation_gate",
                        subject,
                        rel(presentation_path, root),
                            "`presentation_checklist.md` must declare `render_toolchain_check: pass` or `waived` when the rendering toolchain is not required.",
                        )
                    )
        if "article_pdf_check" in checklist_values:
            article_value = checklist_values["article_pdf_check"].strip().lower()
            if bool(quality_settings.get("require_integrated_article_pdf", True)):
                if article_value != "pass":
                    findings.append(
                        Finding(
                            "major",
                            "presentation_gate",
                            subject,
                            rel(presentation_path, root),
                            "`presentation_checklist.md` must declare `article_pdf_check: pass` when the manuscript-quality contract requires an integrated article PDF.",
                        )
                    )
            elif article_value not in {"pass", "waived", "not_required", "not required", "n/a"}:
                findings.append(
                    Finding(
                        "major",
                        "presentation_gate",
                        subject,
                        rel(presentation_path, root),
                        "`presentation_checklist.md` must declare `article_pdf_check: pass` or `not_required`.",
                    )
                )

    display_items = display_item_count(latest)
    pdf_figures = pdf_figure_count(latest / "figures")
    display_paths = display_item_paths(latest)
    display_plan_path = latest / "display_item_plan.md"
    minimum_display_items = int(quality_settings["minimum_display_items"])
    if display_items < minimum_display_items:
        findings.append(
            Finding(
                "major",
                "presentation_gate",
                subject,
                rel(latest / "figures", root),
                f"Found {display_items} display item(s), below `minimum_display_items` {minimum_display_items}.",
            )
        )
    if display_items > 0 and pdf_figures == 0:
        findings.append(
            Finding(
                "major",
                "presentation_gate",
                subject,
                rel(latest / "figures", root),
                "Figure artifacts are present but no PDF figure file was found; SVG and raster images are optional extras, not replacements for PDF figures.",
            )
        )
    figure_table_section = section_text(manuscript_text, REQUIRED_MANUSCRIPT_SECTIONS["figure_table_interpretation"])
    if display_paths and len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?", figure_table_section)) < 80:
        findings.append(
            Finding(
                "major",
                "presentation_gate",
                subject,
                rel(manuscript_path, root),
                "Manuscript must include a substantive figure/table guide section explaining display-item purpose, labels/legends, annotations, conclusions, and caveats.",
            )
        )
    if display_paths:
        if not nonempty_file(display_plan_path):
            findings.append(
                Finding(
                    "major",
                    "presentation_gate",
                    subject,
                    rel(display_plan_path, root),
                    "`display_item_plan.md` is required when main-text figures or tables are present; it records the Researcher's claim-led display strategy and routes display-program similarity to LLM/editor judgment.",
                )
            )
        plan_check_value = checklist_values.get("display_item_plan_check", "").strip().lower()
        if plan_check_value and plan_check_value != "pass":
            findings.append(
                Finding(
                    "major",
                    "presentation_gate",
                    subject,
                    rel(presentation_path, root),
                    "`presentation_checklist.md` must declare `display_item_plan_check: pass` when display items are present.",
                )
            )

    display_explanations_path = latest / "display_item_explanations.md"
    if bool(quality_settings["require_display_item_explanations"]):
        if not nonempty_file(display_explanations_path):
            findings.append(
                Finding(
                    "major",
                    "presentation_gate",
                    subject,
                    rel(display_explanations_path, root),
                    "`display_item_explanations.md` is required and must explain every figure and table.",
                )
            )
        else:
            explanation_text = display_explanations_path.read_text(encoding="utf-8", errors="replace")
            normalized_explanation = explanation_text.lower()
            missing_display_items = []
            for path in display_paths:
                rel_path = rel(path, latest).lower()
                candidates = {rel_path, path.name.lower(), path.stem.lower()}
                if not any(candidate in normalized_explanation for candidate in candidates):
                    missing_display_items.append(rel(path, latest))
            if missing_display_items:
                findings.append(
                    Finding(
                        "major",
                        "presentation_gate",
                        subject,
                        rel(display_explanations_path, root),
                        "`display_item_explanations.md` does not mention every submitted display item: "
                        + ", ".join(missing_display_items[:8])
                        + ("." if len(missing_display_items) <= 8 else ", ..."),
                    )
                )
            required_explanation_terms = [
                "purpose",
                "reader orientation",
                "raw label translation",
                "summary conclusion",
                "caveat",
            ]
            missing_terms = [term for term in required_explanation_terms if term not in normalized_explanation]
            if missing_terms:
                findings.append(
                    Finding(
                        "major",
                        "presentation_gate",
                        subject,
                        rel(display_explanations_path, root),
                        "`display_item_explanations.md` is missing required explanation heading(s): "
                        + ", ".join(missing_terms)
                        + ".",
                    )
                )
            raw_labels = raw_identifier_candidates(explanation_text + "\n" + figure_table_section)
            if raw_labels:
                findings.append(
                    Finding(
                        "minor",
                        "presentation_gate",
                        subject,
                        rel(display_explanations_path, root),
                        "Potential raw/internal labels still need human-readable translation or replacement: "
                        + ", ".join(raw_labels[:12])
                        + ("." if len(raw_labels) <= 12 else ", ..."),
                    )
                )

            article_pdf_exists = (latest / "article" / "article.pdf").is_file()
            if article_pdf_exists:
                explanation_entries = parse_display_item_explanation_entries(explanation_text)
                figure_suffixes = {".pdf", ".svg", ".png", ".jpg", ".jpeg", ".tif", ".tiff"}
                figure_paths = [path for path in display_paths if path.parent.name == "figures" and path.suffix.lower() in figure_suffixes]
                figure_groups: dict[str, list[tuple[Path, dict[str, str]]]] = {}
                missing_grouping_decisions: list[str] = []
                missing_grouping_rationales: list[str] = []
                missing_panel_labels: list[str] = []
                standalone_values = {"", "none", "na", "n/a", "no", "false", "standalone", "single"}

                def substantive(value: str) -> bool:
                    stripped = value.strip()
                    return bool(stripped) and not (stripped.startswith("<") and stripped.endswith(">"))

                for path in figure_paths:
                    fields = display_item_entry_for_path(path, latest, explanation_entries)
                    if not fields:
                        continue
                    group_value = (
                        fields.get("article_group")
                        or fields.get("article_figure_group")
                        or fields.get("figure_group")
                        or fields.get("composite_group")
                        or ""
                    ).strip()
                    normalized_group = re.sub(r"\s+", " ", group_value.lower())
                    rationale = fields.get("article_grouping_rationale", "").strip()
                    if not substantive(group_value):
                        missing_grouping_decisions.append(rel(path, latest))
                        continue
                    if not substantive(rationale):
                        missing_grouping_rationales.append(rel(path, latest))
                    if normalized_group not in standalone_values:
                        group_key = re.sub(r"[^a-z0-9]+", "-", normalized_group).strip("-")
                        figure_groups.setdefault(group_key, []).append((path, fields))
                        panel_value = (fields.get("panel_label") or fields.get("article_panel_label") or "").strip()
                        if not substantive(panel_value):
                            missing_panel_labels.append(rel(path, latest))

                if missing_grouping_decisions:
                    findings.append(
                        Finding(
                            "major",
                            "presentation_gate",
                            subject,
                            rel(display_explanations_path, root),
                            "Integrated article figures require an explicit `Article group` decision for each figure: "
                            + ", ".join(missing_grouping_decisions[:8])
                            + ("." if len(missing_grouping_decisions) <= 8 else ", ..."),
                        )
                    )
                if missing_grouping_rationales:
                    findings.append(
                        Finding(
                            "major",
                            "presentation_gate",
                            subject,
                            rel(display_explanations_path, root),
                            "Integrated article figures require an `Article grouping rationale` explaining why the figure is grouped or standalone: "
                            + ", ".join(missing_grouping_rationales[:8])
                            + ("." if len(missing_grouping_rationales) <= 8 else ", ..."),
                        )
                    )
                if missing_panel_labels:
                    findings.append(
                        Finding(
                            "major",
                            "presentation_gate",
                            subject,
                            rel(display_explanations_path, root),
                            "Grouped article figures require explicit `Panel label` values: "
                            + ", ".join(missing_panel_labels[:8])
                            + ("." if len(missing_panel_labels) <= 8 else ", ..."),
                        )
                    )
                for group_key, members in sorted(figure_groups.items()):
                    if len(members) < 2:
                        findings.append(
                            Finding(
                                "minor",
                                "presentation_gate",
                                subject,
                                rel(display_explanations_path, root),
                                f"Article figure group `{group_key}` has only one member; mark it `standalone` or add the missing related panel.",
                            )
                        )
                        continue
                    has_title = any(
                        substantive(fields.get("article_group_title", "") or fields.get("group_title", "") or fields.get("composite_title", ""))
                        for _, fields in members
                    )
                    has_explanation = any(
                        substantive(
                            fields.get("article_group_explanation", "")
                            or fields.get("group_explanation", "")
                            or fields.get("composite_explanation", "")
                        )
                        for _, fields in members
                    )
                    if not has_title or not has_explanation:
                        findings.append(
                            Finding(
                                "major",
                                "presentation_gate",
                                subject,
                                rel(display_explanations_path, root),
                                f"Article figure group `{group_key}` needs an `Article group title` and `Article group explanation` on at least one member.",
                            )
                        )

    manuscript_pdf = latest / "manuscript.pdf"
    pdf_renderer = style_values.get("pdf_renderer", "").strip().lower()
    math_rendering_pass = style_values.get("math_rendering_check", "").strip().lower() == "pass"
    if (
        nonempty_file(manuscript_pdf)
        and not bool(quality_settings["allow_raw_markdown_pdf"])
        and b"Matplotlib" in manuscript_pdf.read_bytes()
        and not (pdf_renderer == "research-arena-matplotlib-mathtext" and math_rendering_pass)
    ):
        findings.append(
            Finding(
                "major",
                "presentation_gate",
                subject,
                rel(manuscript_pdf, root),
                "Manuscript PDF appears to be Matplotlib-rendered; inspect for raw Markdown dump formatting.",
            )
        )
    raw_math_patterns = pdf_raw_math_markup_patterns(manuscript_pdf)
    if (
        nonempty_file(manuscript_pdf)
        and bool(quality_settings["require_rendered_math"])
        and raw_math_patterns
        and not (pdf_renderer == "research-arena-matplotlib-mathtext" and math_rendering_pass)
    ):
        findings.append(
            Finding(
                "major",
                "presentation_gate",
                subject,
                rel(manuscript_pdf, root),
                "Manuscript PDF appears to contain raw/unrendered LaTeX math markup: "
                + ", ".join(raw_math_patterns[:5])
                + ".",
            )
        )
    if (
        nonempty_file(manuscript_pdf)
        and bool(quality_settings["require_preferred_sans_fonts"])
        and not pdf_mentions_preferred_font(manuscript_pdf)
    ):
        findings.append(
                Finding(
                    "major",
                    "presentation_gate",
                    subject,
                    rel(manuscript_pdf, root),
                    "Manuscript PDF does not appear to mention an accepted open-source sans-serif font family.",
                )
            )

    if bool(quality_settings["require_human_readable_output"]):
        findings.extend(
            audit_human_readable_output(
                root,
                run_id,
                subject,
                latest,
                require_article_pdf=bool(quality_settings.get("require_integrated_article_pdf", True)),
            )
        )

    if bool(quality_settings["require_preferred_sans_fonts"]):
        figures_dir = latest / "figures"
        if figures_dir.is_dir():
            for svg_path in sorted(figures_dir.glob("*.svg")):
                font_values = svg_font_values(svg_path)
                if font_values and not any(uses_preferred_sans_font(value) for value in font_values):
                    findings.append(
                        Finding(
                            "major",
                            "presentation_gate",
                            subject,
                            rel(svg_path, root),
                            "SVG figure text does not use an accepted open-source sans-serif font family.",
                        )
                    )

    analysis_path = latest / "analysis.py"
    if nonempty_file(analysis_path):
        text = analysis_path.read_text(encoding="utf-8", errors="replace")
        matched = [pattern for pattern in WRAPPER_PATTERNS if re.search(pattern, text)]
        if matched:
            findings.append(
                Finding(
                    "major",
                    "independence",
                    subject,
                    rel(analysis_path, root),
                    "Submission analysis looks like a wrapper around a central generator or hidden engine.",
                )
            )

    researcher_match = re.search(r"submission_\d+_(.+)$", subject)
    researcher_id = researcher_match.group(1) if researcher_match else subject
    workspace = root / "agents" / researcher_id / "workspace" / run_id
    if not workspace.is_dir():
        findings.append(
            Finding(
                "major",
                "independence",
                subject,
                rel(workspace, root),
                "Researcher workspace is missing; independence before initial submission is not documented.",
            )
        )

    board_workspace = root / "agents" / "study_design_board" / "workspace" / run_id
    if not board_workspace.is_dir():
        findings.append(
            Finding(
                "major",
                "proposal_gate",
                subject,
                rel(board_workspace, root),
                "Study Design Board workspace is missing; proposal-gate review is not documented.",
            )
        )
    elif not any(board_workspace.glob(f"*{subject}*.md")):
        findings.append(
            Finding(
                "major",
                "proposal_gate",
                subject,
                rel(board_workspace, root),
                "No Study Design Board review file appears to reference this submission.",
            )
        )

    return findings


def write_csv(path: Path, rows: list[Finding]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["severity", "category", "subject", "path", "message"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Research Arena research-depth and presentation-gate artifacts.")
    parser.add_argument("run_id", help="Run id under runs/<run_id> and submissions/<run_id>.")
    parser.add_argument("--root", default=".", help="Research Arena repository root.")
    parser.add_argument("--output-json", help="Optional JSON output path.")
    parser.add_argument("--output-csv", help="Optional CSV output path.")
    parser.add_argument(
        "--write-default",
        action="store_true",
        help="Write runs/<run_id>/research_depth_audit.json and .csv.",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    findings = audit_run_contracts(root, args.run_id)
    quality_settings, quality_findings = read_quality_contract(root, args.run_id)
    findings.extend(quality_findings)
    findings.extend(audit_render_toolchain_report(root, args.run_id, quality_settings))
    compute_settings, compute_findings = read_compute_budget_contract(root, args.run_id)
    findings.extend(compute_findings)
    article_type = read_selected_article_type(root, args.run_id)
    if not bool(quality_settings.get("require_integrated_article_pdf", True)) and not is_demo_article_type(article_type):
        findings.append(
            Finding(
                "major",
                "manuscript_quality_contract",
                args.run_id,
                rel(root / "runs" / args.run_id / "manuscript_quality_contract.md", root),
                "`require_integrated_article_pdf: false` is only acceptable for explicitly compact/demo/internal runs; serious-pilot and full-research runs must build `article/article.pdf` for every revision.",
            )
        )
    submissions_root = root / "submissions" / args.run_id
    submission_dirs = sorted(p for p in submissions_root.glob("submission_*") if p.is_dir())
    if not submission_dirs:
        findings.append(
            Finding(
                "blocking",
                "submission",
                args.run_id,
                rel(submissions_root, root),
                "No submission_* folders found for run.",
            )
        )
    for submission_dir in submission_dirs:
        findings.extend(audit_submission(root, args.run_id, submission_dir, quality_settings, compute_settings, article_type))

    blocking_or_major = [row for row in findings if row.severity in {"blocking", "major"}]
    payload = {
        "run_id": args.run_id,
        "clerk_type": "structural_depth_presentation_independence",
        "scientific_judgment": "not_evaluated",
        "status": "flagged" if blocking_or_major else "pass",
        "finding_count": len(findings),
        "blocking_or_major_count": len(blocking_or_major),
        "notes": [
            "This deterministic clerk checks required artifacts, presentation structure, and independence signals, not scientific truth.",
            "A pass here is not an acceptance signal and does not mean the research is deep enough.",
            "Editors should combine this output with LLM-backed scientific-depth, display-program-independence, and article-fit judgment.",
            "Structured compute-budget settings are checked when present; missing structured settings are flagged so Editors can avoid accepting under-specified budgets.",
            "Manuscript style checks look for declared line numbers, numbered and rendered display equations, rendered inline math spans, style manifests, accepted sans-serif manuscript/figure text signals, and a declared math rendering policy; visual PDF review is still required.",
        ],
        "findings": [asdict(row) for row in findings],
    }

    output_json = Path(args.output_json) if args.output_json else None
    output_csv = Path(args.output_csv) if args.output_csv else None
    if args.write_default:
        output_json = root / "runs" / args.run_id / "research_depth_audit.json"
        output_csv = root / "runs" / args.run_id / "research_depth_audit.csv"

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
