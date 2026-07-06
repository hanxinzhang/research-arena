#!/usr/bin/env python3
"""Build a PLOS-like integrated article PDF for a Research Arena revision.

This creates a second publication-style artifact, `article/article.pdf`. It does not
replace `manuscript.pdf`, which remains the line-numbered review manuscript.
Figures and tables also remain separately inspectable in their original folders.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BUNDLED_FONT_DIR = Path("assets") / "fonts" / "inter"
BUNDLED_FONT_FILES = [
    "Inter-Regular.ttf",
    "Inter-Bold.ttf",
    "Inter-Italic.ttf",
    "Inter-BoldItalic.ttf",
    "LICENSE.txt",
]
BRAND_LOGO_ID = "research_arena_logo_evidence_gain"
BRAND_LOGO_PDF = f"{BRAND_LOGO_ID}.pdf"
BRAND_LOGO_TEX = f"{BRAND_LOGO_ID}.tex"
FIGURE_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
TABLE_EXTENSIONS = {".csv", ".tsv"}
MAX_MAIN_TABLE_ROWS = 35
MAX_MAIN_TABLE_COLUMNS = 8
PDF_POINTS_PER_INCH = 72.0
ARTICLE_TEXT_WIDTH_IN = 8.5 - (0.72 * 2)
TARGET_ARTICLE_FIGURE_TEXT_SIZE_PT = 8.0
FRAMEWORK_SOURCE_FIGURE_TEXT_SIZE_PT = 8.5
MIN_ARTICLE_FIGURE_TEXT_SIZE_PT = 7.4
MAX_ARTICLE_FIGURE_TEXT_SIZE_PT = 8.8
MAX_ARTICLE_FIGURE_WIDTH_IN = 6.05
MAX_ARTICLE_FIGURE_HEIGHT_IN = 4.35
MAX_COMPOSITE_PANEL_HEIGHT_IN = 2.65
FALLBACK_ARTICLE_FIGURE_WIDTH_IN = 3.75
FALLBACK_ARTICLE_FIGURE_HEIGHT_IN = 2.80
STANDALONE_GROUP_VALUES = {"", "none", "na", "n/a", "no", "false", "standalone", "single"}
PANEL_LABELS = "abcdefghijklmnopqrstuvwxyz"
INLINE_CODE_PATTERN = re.compile(r"(?<!\\)`([^`\n]+)`")
LATEX_TEXT_MATH_COMMAND_PATTERN = re.compile(
    r"\\(?P<command>operatornamewithlimits|operatorname|mathrm|textrm|textnormal|text)\{(?P<content>[^{}]+)\}"
)
PDF_MEDIABOX_PATTERN = re.compile(
    rb"/MediaBox\s*\[\s*[-+0-9.]+\s+[-+0-9.]+\s+(?P<width>[-+0-9.]+)\s+(?P<height>[-+0-9.]+)\s*\]"
)


@dataclass
class ManuscriptSection:
    level: int
    title: str
    body: str


@dataclass
class DisplayItem:
    label: str
    title: str
    artifact_path: str
    display_type: str
    fields: dict[str, str]


@dataclass
class ArticleBuildRecord:
    status: str
    article_layout_style: str
    renderer: str
    source_revision: str
    article_markdown: str
    article_pdf: str
    article_build_report: str
    brand_logo: str
    included_figures: list[dict[str, Any]]
    included_tables: list[dict[str, str | int]]
    supplemental_items: list[dict[str, str]]
    omitted_items: list[dict[str, str]]
    missing_article_explanation_count: int
    figure_presentation_flag_count: int
    publication_type: str
    author_name: str
    publication_date: str
    journal_volume: str
    journal_date: str
    page_count: int | None
    path_prefixes_added: list[str]
    created_at_utc: str


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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def slugify(value: str, fallback: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", value.lower()).strip("-")
    return slug[:70] or fallback


def normalize_inline_code(text: str) -> str:
    def replace_code_span(match: re.Match[str]) -> str:
        content = match.group(1).replace(r"\`", "`")
        return r"\texttt{" + latex_escape(content) + "}"

    return INLINE_CODE_PATTERN.sub(replace_code_span, text)


def normalize_latex_math_text_command_spaces(text: str) -> str:
    def replace_command(match: re.Match[str]) -> str:
        command = match.group("command")
        content = match.group("content")
        if command in {"operatorname", "operatornamewithlimits", "mathrm"}:
            content = re.sub(r"\s+", r"\\,", content.strip())
        return rf"\{command}{{{content}}}"

    return LATEX_TEXT_MATH_COMMAND_PATTERN.sub(replace_command, text)


def latex_escape(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in value)


ARTICLE_TABLE_HEADER_LABELS = {
    "brier": "Brier",
    "ci_2_5": "2.5% CI",
    "ci_97_5": "97.5% CI",
    "coefficient": "coef.",
    "folds": "folds",
    "mean_average_precision": "mean AP",
    "mean_auroc": "mean AUROC",
    "mean_brier": "mean Brier",
    "mean_predicted_probability": "mean predicted",
    "metric": "metric",
    "model": "model",
    "observed_prevalence": "observed prevalence",
    "observed_sparse_ap": "observed AP",
    "observed_sparse_auroc": "observed AUROC",
    "odds_ratio": "odds ratio",
    "permutation_ap": "permutation AP",
    "permutation_auroc": "permutation AUROC",
    "positive_rows": "positive rows",
    "sd_average_precision": "SD AP",
    "sd_auroc": "SD AUROC",
    "sd_brier": "SD Brier",
    "target": "target",
}


ARTICLE_TABLE_VALUE_LABELS = {
    "average_precision": "average precision",
    "cognitive_morphometry": "cognitive morphometry",
    "cognitive_morphometry_sparse_cdr_ge_1": "sparse CDR >= 1 model",
    "m/f_m": "male sex",
    "morphometry_age": "morphometry age",
    "no_mmse_sensitivity": "no-MMSE sensitivity",
    "observed_sparse_vs_permutation": "observed sparse endpoint vs permutation",
    "prevalence_baseline": "prevalence baseline",
    "target_sensitivity_cdr_gt_0": "target sensitivity CDR > 0",
    "permutation_negative_control": "permutation control",
}


def article_table_header(value: str) -> str:
    key = value.strip()
    return ARTICLE_TABLE_HEADER_LABELS.get(key, key.replace("_", " "))


def article_table_cell(value: str) -> str:
    text = value.strip()
    if not text:
        return ""
    key = text.lower()
    if key in ARTICLE_TABLE_VALUE_LABELS:
        return ARTICLE_TABLE_VALUE_LABELS[key]
    try:
        number = float(text)
    except ValueError:
        return text.replace("_", " ") if "_" in text and re.fullmatch(r"[A-Za-z0-9_./><= -]+", text) else text
    if number.is_integer() and abs(number) < 1000:
        return str(int(number))
    return f"{number:.3f}"


def split_markdown_pipe_row(line: str) -> list[str]:
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return [cell.strip() for cell in stripped.split("|")]


def is_markdown_pipe_separator(line: str) -> bool:
    cells = split_markdown_pipe_row(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)


def markdown_pipe_row(cells: list[str]) -> str:
    return "|" + "|".join(cells) + "|"


def normalize_markdown_pipe_tables(text: str) -> str:
    lines = text.splitlines()
    output: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if "|" not in line or index + 1 >= len(lines) or not is_markdown_pipe_separator(lines[index + 1]):
            output.append(line)
            index += 1
            continue

        header = split_markdown_pipe_row(line)
        output.append(markdown_pipe_row([article_table_header(cell) for cell in header]))
        output.append(markdown_pipe_row(["---"] * len(header)))
        index += 2
        while index < len(lines) and "|" in lines[index] and lines[index].strip():
            row = split_markdown_pipe_row(lines[index])
            padded = [*row, *[""] * (len(header) - len(row))]
            output.append(markdown_pipe_row([article_table_cell(cell) for cell in padded[: len(header)]]))
            index += 1
    return "\n".join(output)


def compact_text(value: str, limit: int = 850) -> str:
    text = re.sub(r"\s+", " ", value).strip()
    if len(text) <= limit:
        return text
    cut = text.rfind(". ", 0, limit)
    if cut < max(120, limit // 2):
        cut = limit
    return text[:cut].rstrip(" ,.;") + "."


def sanitize_report_paths(value: object, root: Path) -> object:
    if isinstance(value, dict):
        return {key: sanitize_report_paths(item, root) for key, item in value.items()}
    if isinstance(value, list):
        return [sanitize_report_paths(item, root) for item in value]
    if not isinstance(value, str):
        return value

    replacements = [
        ((root.parent / "required tools").resolve().as_posix(), "<required_tools>"),
        (root.resolve().as_posix(), "<research_arena_root>"),
        (Path.home().resolve().as_posix(), "<home>"),
    ]
    text = value
    for source, replacement in sorted(set(replacements), key=lambda item: len(item[0]), reverse=True):
        if source:
            text = text.replace(source, replacement)
    text = re.sub(r"/private/var/folders/[^\s\"']+", "<local_temp>", text)
    text = re.sub(r"/var/folders/[^\s\"']+", "<local_temp>", text)
    text = re.sub(r"/private/tmp/[^\s\"']+", "<local_temp>", text)
    text = re.sub(r"/tmp/[^\s\"']+", "<local_temp>", text)
    return text


def today_display_date() -> str:
    today = datetime.now().astimezone().date()
    return f"{today.strftime('%B')} {today.day}, {today.year}"


def infer_author_name(revision_dir: Path) -> str:
    submission = revision_dir.parent.name
    match = re.search(r"researcher[_-]*(\d+)", submission, flags=re.IGNORECASE)
    if match:
        return f"Researcher {match.group(1)}"
    if submission.startswith("submission_"):
        submission = submission.removeprefix("submission_")
    return submission.replace("_", " ").replace("-", " ").title() or "Research Arena Researcher"


def parse_manuscript(markdown: str) -> tuple[str, list[ManuscriptSection]]:
    title = "Untitled Research Arena article"
    sections: list[ManuscriptSection] = []
    current_title: str | None = None
    current_level = 2
    current_lines: list[str] = []

    def flush() -> None:
        nonlocal current_title, current_lines, current_level
        if current_title is not None:
            sections.append(
                ManuscriptSection(
                    level=current_level,
                    title=current_title.strip(),
                    body="\n".join(current_lines).strip(),
                )
            )
        current_title = None
        current_lines = []

    for line in markdown.splitlines():
        heading = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if heading:
            level = len(heading.group(1))
            text = heading.group(2).strip()
            if level == 1 and not sections and current_title is None:
                title = text
                continue
            if level <= 2:
                flush()
                current_title = text
                current_level = level
                current_lines = []
                continue
        if current_title is not None:
            current_lines.append(line)
    flush()
    return title, sections


def field_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


def parse_display_item_explanations(path: Path) -> list[DisplayItem]:
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    matches = list(re.finditer(r"^##\s+(.+?)\s*$", text, flags=re.MULTILINE))
    items: list[DisplayItem] = []
    for index, match in enumerate(matches):
        heading = match.group(1).strip()
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
                active_key = field_key(heading_match.group(1))
                fields.setdefault(active_key, "")
                continue
            field_match = None if in_subsection else re.match(r"^([A-Za-z][A-Za-z /-]+):\s*(.*)$", line)
            if field_match:
                active_key = field_key(field_match.group(1))
                fields[active_key] = field_match.group(2).strip()
                continue
            if active_key and line.strip():
                line_text = re.sub(r"^[-*]\s*", "", line.strip())
                fields[active_key] = (fields[active_key] + " " + line_text).strip()

        display_type = "table" if heading.lower().startswith("table") else "figure"
        title = heading.split(":", 1)[1].strip() if ":" in heading else heading
        artifact_path = fields.get("artifact_path", "")
        if not artifact_path:
            continue
        items.append(
            DisplayItem(
                label=heading,
                title=title,
                artifact_path=artifact_path.strip("` "),
                display_type=fields.get("display_type", display_type).strip().lower(),
                fields=fields,
            )
        )
    return items


def fallback_display_item(path: Path, revision_dir: Path, display_type: str) -> DisplayItem:
    rel_path = path.relative_to(revision_dir).as_posix()
    title = path.stem.replace("_", " ").replace("-", " ").title()
    return DisplayItem(
        label=title,
        title=title,
        artifact_path=rel_path,
        display_type=display_type,
        fields={
            "missing_article_explanation": "true",
            "caveat": "A dedicated display-item explanation was not provided.",
        },
    )


def display_item_caption(item: DisplayItem) -> str:
    parts = [item.title]
    for key in ["purpose", "display_details", "reader_orientation", "raw_label_translation", "summary_conclusion", "caveat"]:
        value = item.fields.get(key, "").strip()
        if value:
            prefix = "Caveat: " if key == "caveat" and not value.lower().startswith("caveat") else ""
            parts.append(prefix + value)
    return compact_text(" ".join(parts))


def display_item_explanation(item: DisplayItem) -> str:
    for key in ["article_explanation", "article_caption", "short_explanation"]:
        value = item.fields.get(key, "").strip()
        if value:
            return compact_text(value, limit=560)
    return ""


def first_field(item: DisplayItem, keys: list[str]) -> str:
    for key in keys:
        value = item.fields.get(key, "").strip()
        if value:
            return value
    return ""


def article_group_key(item: DisplayItem) -> str | None:
    value = first_field(item, ["article_group", "article_figure_group", "figure_group", "composite_group"])
    normalized = re.sub(r"\s+", " ", value.strip()).lower()
    if normalized in STANDALONE_GROUP_VALUES:
        return None
    return slugify(value, "figure-group")


def panel_order(item: DisplayItem, fallback: int) -> tuple[int, str]:
    value = first_field(item, ["panel_order", "article_panel_order"])
    try:
        return (int(value), item.artifact_path)
    except ValueError:
        return (fallback, item.artifact_path)


def panel_label(item: DisplayItem, index: int) -> str:
    value = first_field(item, ["panel_label", "article_panel_label"])
    if value:
        return value.strip().rstrip(".")
    return PANEL_LABELS[index] if index < len(PANEL_LABELS) else str(index + 1)


def panel_title(item: DisplayItem) -> str:
    return first_field(item, ["panel_title", "article_panel_title"]) or item.title


def group_title(group_key: str, items: list[DisplayItem]) -> str:
    for item in items:
        value = first_field(item, ["article_group_title", "group_title", "composite_title"])
        if value:
            return value
    return items[0].title if items else group_key.replace("-", " ").title()


def group_explanation(group_key: str, items: list[DisplayItem]) -> str:
    for item in items:
        value = first_field(item, ["article_group_explanation", "group_explanation", "composite_explanation"])
        if value:
            return compact_text(value, limit=560)
    explanations = [display_item_explanation(item) for item in items if display_item_explanation(item)]
    return compact_text(" ".join(explanations), limit=560)


def group_columns(group_key: str, items: list[DisplayItem]) -> int:
    for item in items:
        value = first_field(item, ["article_group_columns", "panel_columns", "composite_columns"])
        try:
            columns = int(value)
        except ValueError:
            continue
        if 1 <= columns <= 3:
            return columns
    return 2 if len(items) <= 4 else 3


def display_item_title_tex(kind: str, number: int, item: DisplayItem) -> str:
    label = "Fig." if kind == "figure" else "Table"
    return rf"\RADisplayItemTitle{{{label}}}{{{number}}}{{{latex_escape(item.title)}}}"


def display_item_explanation_tex(item: DisplayItem) -> str:
    explanation = display_item_explanation(item)
    if not explanation:
        return ""
    return rf"\RADisplayItemDek{{{latex_escape(explanation)}}}"


def pdf_page_size_inches(path: Path) -> tuple[float, float] | None:
    if path.suffix.lower() != ".pdf":
        return None
    try:
        data = path.read_bytes()[:65536]
    except OSError:
        return None
    match = PDF_MEDIABOX_PATTERN.search(data)
    if not match:
        return None
    try:
        width = float(match.group("width")) / PDF_POINTS_PER_INCH
        height = float(match.group("height")) / PDF_POINTS_PER_INCH
    except ValueError:
        return None
    if width <= 0 or height <= 0:
        return None
    return width, height


def article_figure_dimensions(
    path: Path,
    max_width_in: float = MAX_ARTICLE_FIGURE_WIDTH_IN,
    max_height_in: float = MAX_ARTICLE_FIGURE_HEIGHT_IN,
) -> tuple[float, float, float | None, float | None, float | None, float | None, str]:
    native_size = pdf_page_size_inches(path)
    if native_size is None:
        return (
            FALLBACK_ARTICLE_FIGURE_WIDTH_IN,
            FALLBACK_ARTICLE_FIGURE_HEIGHT_IN,
            None,
            None,
            None,
            None,
            "unknown_native_size",
        )

    native_width, native_height = native_size
    target_scale = TARGET_ARTICLE_FIGURE_TEXT_SIZE_PT / FRAMEWORK_SOURCE_FIGURE_TEXT_SIZE_PT
    scale = min(target_scale, max_width_in / native_width, max_height_in / native_height)
    display_width = native_width * scale
    display_height = native_height * scale
    effective_text_size = FRAMEWORK_SOURCE_FIGURE_TEXT_SIZE_PT * scale
    if effective_text_size < MIN_ARTICLE_FIGURE_TEXT_SIZE_PT:
        status = "too_small_after_article_scaling"
    elif effective_text_size > MAX_ARTICLE_FIGURE_TEXT_SIZE_PT:
        status = "too_large_after_article_scaling"
    else:
        status = "pass"
    return display_width, display_height, native_width, native_height, scale, effective_text_size, status


def article_figure_record_fields(
    display_width: float,
    display_height: float,
    native_width: float | None,
    native_height: float | None,
    scale: float | None,
    effective_text_size: float | None,
    text_size_status: str,
) -> dict[str, str]:
    return {
        "display_width_in": f"{display_width:.2f}",
        "display_height_in": f"{display_height:.2f}",
        "native_width_in": "" if native_width is None else f"{native_width:.2f}",
        "native_height_in": "" if native_height is None else f"{native_height:.2f}",
        "article_scale_factor": "" if scale is None else f"{scale:.3f}",
        "source_text_size_pt": f"{FRAMEWORK_SOURCE_FIGURE_TEXT_SIZE_PT:.1f}",
        "target_article_text_size_pt": f"{TARGET_ARTICLE_FIGURE_TEXT_SIZE_PT:.1f}",
        "effective_article_text_size_pt": "" if effective_text_size is None else f"{effective_text_size:.1f}",
        "figure_text_size_status": text_size_status,
    }


def figure_text_flag_count(records: list[dict[str, Any]]) -> int:
    count = 0
    for record in records:
        if record.get("figure_text_size_status") not in {None, "pass"}:
            count += 1
        for panel in record.get("panels", []) if isinstance(record.get("panels"), list) else []:
            if panel.get("figure_text_size_status") not in {None, "pass"}:
                count += 1
    return count


def copy_bundled_fonts(root: Path, article_dir: Path) -> None:
    source_dir = root / BUNDLED_FONT_DIR
    target_dir = article_dir / BUNDLED_FONT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    for filename in BUNDLED_FONT_FILES:
        source = source_dir / filename
        if source.is_file():
            shutil.copy2(source, target_dir / filename)


def brand_logo_pdf_source() -> str:
    return r"""
\documentclass{article}
\usepackage[papersize={560bp,260bp},margin=0bp]{geometry}
\usepackage{fontspec}
\usepackage{xcolor}
\pagestyle{empty}
\setlength{\parindent}{0pt}
\setlength{\unitlength}{1bp}
\setmainfont{Inter}[
  Path=assets/fonts/inter/,
  UprightFont=Inter-Bold.ttf,
  BoldFont=Inter-Bold.ttf
]
\definecolor{RAAccent}{HTML}{2C7FB8}
\definecolor{RADark}{HTML}{1F2937}
\definecolor{RAMuted}{HTML}{4B5563}
\definecolor{RALogoDivider}{HTML}{D7E3EC}
\begin{document}
\noindent\begin{picture}(560,260)
\put(28,122){{\fontsize{82bp}{82bp}\selectfont\textcolor{RADark}{\char"0394\kern-4bp E}}}
\put(162,46){\textcolor{RALogoDivider}{\rule{3bp}{180bp}}}
\put(198,178){{\fontsize{66bp}{66bp}\selectfont\textcolor{RADark}{Research}}}
\put(198,103){{\fontsize{66bp}{66bp}\selectfont\textcolor{RAAccent}{Arena}}}
\put(201,46){{\fontsize{21bp}{21bp}\selectfont\textcolor{RAMuted}{E\kern3.2bp V\kern3.2bp I\kern3.2bp D\kern3.2bp E\kern3.2bp N\kern3.2bp C\kern3.2bp E\kern3.2bp \space\kern3.2bp G\kern3.2bp A\kern3.2bp I\kern3.2bp N}}}
\end{picture}
\end{document}
"""


def prepare_brand_logo_asset(root: Path, article_dir: Path, conda_env: str | None) -> str | None:
    """Render the canonical SVG logo layout as a vector PDF asset."""
    font_dir = root / BUNDLED_FONT_DIR
    if not (font_dir / "Inter-Bold.ttf").is_file():
        return None

    env, _ = toolchain_env(root, conda_env)
    xelatex = shutil.which("xelatex", path=env.get("PATH"))
    if not xelatex:
        return None

    target_dir = article_dir / "assets" / "brand"
    target_dir.mkdir(parents=True, exist_ok=True)
    source = target_dir / BRAND_LOGO_TEX
    source.write_text(brand_logo_pdf_source(), encoding="utf-8")
    command = [
        xelatex,
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-output-directory",
        target_dir.relative_to(article_dir).as_posix(),
        source.relative_to(article_dir).as_posix(),
    ]
    completed = subprocess.run(
        command,
        cwd=article_dir,
        env=env,
        text=True,
        capture_output=True,
        timeout=60,
        check=False,
    )
    for suffix in [".aux", ".log", ".out"]:
        generated = target_dir / f"{BRAND_LOGO_ID}{suffix}"
        if generated.exists():
            generated.unlink()
    target = target_dir / BRAND_LOGO_PDF
    if completed.returncode != 0 or not target.is_file():
        failure_log = target_dir / f"{BRAND_LOGO_ID}_render_error.log"
        failure_log.write_text(
            "Command: " + " ".join(command) + "\n\nstdout:\n" + completed.stdout + "\n\nstderr:\n" + completed.stderr,
            encoding="utf-8",
        )
        return None
    return target.relative_to(article_dir).as_posix()


def article_header_tex(journal_label: str, publication_type: str, journal_volume: str, journal_date: str) -> str:
    footer_text = " | ".join(part for part in [journal_label, journal_volume, journal_date] if part.strip())
    return rf"""
\usepackage{{amsmath,amssymb,mathtools}}
\usepackage{{booktabs}}
\usepackage{{caption}}
\usepackage{{fancyhdr}}
\usepackage{{float}}
\usepackage{{fontspec}}
\usepackage{{graphicx}}
\usepackage{{hyperref}}
\usepackage{{microtype}}
\usepackage{{titlesec}}
\usepackage{{xcolor}}

\IfFileExists{{assets/fonts/inter/Inter-Regular.ttf}}{{
  \setsansfont{{Inter}}[
    Path=assets/fonts/inter/,
    UprightFont=Inter-Regular.ttf,
    BoldFont=Inter-Bold.ttf,
    ItalicFont=Inter-Italic.ttf,
    BoldItalicFont=Inter-BoldItalic.ttf
  ]
}}{{}}
\renewcommand{{\familydefault}}{{\sfdefault}}
\let\ResearchArenaOriginalText\text
\renewcommand{{\text}}[1]{{\ResearchArenaOriginalText{{\normalfont\rmfamily #1}}}}

\definecolor{{RAAccent}}{{HTML}}{{2C7FB8}}
\definecolor{{RAGreen}}{{HTML}}{{2A9D8F}}
\definecolor{{RADark}}{{HTML}}{{1F2937}}
\definecolor{{RAMuted}}{{HTML}}{{4B5563}}
\definecolor{{RALogoDivider}}{{HTML}}{{D7E3EC}}
\definecolor{{RALight}}{{HTML}}{{E5EEF4}}
\hypersetup{{colorlinks=true, linkcolor=RAAccent, citecolor=RAAccent, urlcolor=RAAccent}}
\setcounter{{secnumdepth}}{{0}}
\setlength{{\parindent}}{{0pt}}
\setlength{{\parskip}}{{0.52em}}
\setlength{{\leftmargini}}{{1.25em}}
\setlength{{\leftmarginii}}{{1.55em}}
\setlength{{\labelsep}}{{0.42em}}
\makeatletter
\renewcommand{{\@listi}}{{%
  \leftmargin\leftmargini
  \parsep 0pt
  \topsep 0.18em
  \itemsep 0.16em
}}
\let\@listI\@listi
\renewcommand{{\@listii}}{{%
  \leftmargin\leftmarginii
  \parsep 0pt
  \topsep 0.12em
  \itemsep 0.10em
}}
\makeatother
\linespread{{1.04}}

\newenvironment{{RAAbstractBox}}{{
  \par\vspace{{0.7em}}\noindent
  \begin{{minipage}}{{\linewidth}}
  {{\sffamily\bfseries\color{{RAAccent}} Abstract}}\par\vspace{{0.25em}}\small
  \setlength{{\leftskip}}{{0.7em}}
  \setlength{{\rightskip}}{{0.7em}}
}}{{%
  \end{{minipage}}
  \par\vspace{{1.1em}}
}}

\titleformat{{\section}}
  {{\Large\bfseries\sffamily\color{{RADark}}}}
  {{}}{{0pt}}{{}}
\titleformat{{\subsection}}
  {{\large\bfseries\sffamily\color{{RADark}}}}
  {{}}{{0pt}}{{}}
\titleformat{{\subsubsection}}
  {{\normalsize\bfseries\sffamily\color{{RADark}}}}
  {{}}{{0pt}}{{}}
\titlespacing*{{\section}}{{0pt}}{{1.4em}}{{0.45em}}
\titlespacing*{{\subsection}}{{0pt}}{{1.0em}}{{0.35em}}

	\captionsetup{{
	  font={{small,sf}},
	  labelfont={{bf}},
	  margin=0.04\linewidth,
	  skip=0.45em
	}}
	\newcommand{{\RADisplayItemTitle}}[3]{{%
	  \par\vspace{{0.35em}}\noindent{{\small\sffamily\bfseries #1~#2 \textbar{{}} #3}}\par
	}}
	\newcommand{{\RADisplayItemDek}}[1]{{%
	  \vspace{{0.12em}}\noindent{{\small\sffamily #1}}\par\vspace{{0.55em}}
	}}
	\pagestyle{{fancy}}
	\fancyhf{{}}
\fancyhead[L]{{\small\bfseries {latex_escape(journal_label)}}}
\fancyhead[R]{{\small {latex_escape(publication_type)}}}
\fancyfoot[L]{{\small {latex_escape(footer_text)}}}
\fancyfoot[R]{{\small \thepage}}
\renewcommand{{\headrulewidth}}{{0.4pt}}
\renewcommand{{\footrulewidth}}{{0.4pt}}
"""


def brand_logo_tex(journal_label: str, logo_asset_path: str | None = None) -> str:
    if logo_asset_path:
        return rf"""
\noindent\includegraphics[width=3.10in]{{{logo_asset_path}}}
\par\vspace{{0.45em}}
"""

    words = journal_label.split()
    if len(words) >= 2:
        first_line = " ".join(words[:-1])
        second_line = words[-1]
    else:
        first_line = journal_label
        second_line = ""

    first_line_tex = latex_escape(first_line)
    second_line_tex = latex_escape(second_line)
    second_line_block = (
        rf"{{\sffamily\bfseries\fontsize{{42}}{{46}}\selectfont\color{{RAAccent}} {second_line_tex}}}\\[0.78em]"
        if second_line_tex
        else ""
    )
    return rf"""
\noindent
\begin{{minipage}}[c]{{1.12in}}
{{\sffamily\bfseries\fontsize{{60}}{{63}}\selectfont \char"0394\kern-0.06em E}}
\end{{minipage}}
\hspace{{0.02in}}
\begin{{minipage}}[c]{{0.02in}}
\textcolor{{RALogoDivider}}{{\rule{{1.1pt}}{{1.45in}}}}
\end{{minipage}}
\hspace{{0.23in}}
\begin{{minipage}}[c]{{4.35in}}
{{\sffamily\bfseries\fontsize{{42}}{{46}}\selectfont\color{{RADark}} {first_line_tex}}}\\[0.28em]
{second_line_block}
{{\sffamily\bfseries\fontsize{{13.2}}{{15.5}}\selectfont\color{{RAMuted}}\addfontfeatures{{LetterSpace=10.0}} EVIDENCE GAIN}}
\end{{minipage}}
\par\vspace{{0.85em}}
"""


def title_block(
    title: str,
    revision_dir: Path,
    root: Path,
    journal_label: str,
    publication_type: str,
    author_name: str,
    publication_date: str,
    logo_asset_path: str | None,
) -> str:
    escaped_title = latex_escape(title)
    escaped_type = latex_escape(publication_type)
    escaped_author = latex_escape(author_name)
    escaped_date = latex_escape(publication_date)
    logo = brand_logo_tex(journal_label, logo_asset_path)
    return rf"""
\begin{{flushleft}}
{logo}
{{\sffamily\bfseries\fontsize{{22}}{{26}}\selectfont {escaped_title}}}\\[0.7em]
{{\sffamily\normalsize {escaped_author}}}\\[0.25em]
{{\sffamily\small\color{{RAMuted}} {escaped_type} \textbar{{}} Published {escaped_date}}}\\[0.8em]
\textcolor{{RAAccent}}{{\rule{{\linewidth}}{{1.2pt}}}}
\end{{flushleft}}
"""


def abstract_block(body: str) -> str:
    return "\\begin{RAAbstractBox}\n" + body.strip() + "\n\\end{RAAbstractBox}"


def clean_section_body(body: str) -> str:
    paragraphs = re.split(r"\n\s*\n", body)
    paragraphs = [
        paragraph
        for paragraph in paragraphs
        if not re.search(r"`?(?:figures|tables)/[A-Za-z0-9_.\-/]+`?", paragraph)
    ]
    text = normalize_markdown_pipe_tables("\n\n".join(paragraphs))
    text = normalize_latex_math_text_command_spaces(normalize_inline_code(text))
    return text.strip()


def table_rows(path: Path) -> list[list[str]]:
    delimiter = "\t" if path.suffix.lower() == ".tsv" else ","
    with path.open(newline="", encoding="utf-8-sig", errors="replace") as handle:
        return [row for row in csv.reader(handle, delimiter=delimiter)]


def table_tex(item: DisplayItem, table_path: Path, table_number: int) -> tuple[str | None, dict[str, str | int] | None, dict[str, str] | None]:
    rows = table_rows(table_path)
    if not rows:
        return None, None, {"artifact": str(table_path), "reason": "empty table"}
    header = rows[0]
    data_rows = rows[1:]
    if len(header) > MAX_MAIN_TABLE_COLUMNS or len(data_rows) > MAX_MAIN_TABLE_ROWS:
        return (
            None,
            None,
            {
                "artifact": str(table_path),
                "reason": f"table is too large for main article ({len(data_rows)} rows, {len(header)} columns)",
            },
        )
    column_spec = "l" + "r" * max(0, len(header) - 1)
    label = f"tab:{slugify(item.title, f'table-{table_number}')}"
    font_size = r"\scriptsize" if len(header) > 6 else r"\small"
    tabcolsep = "2pt" if len(header) > 6 else "6pt"
    fit_to_width = False
    lines = [
        r"\begin{table}[H]",
        display_item_title_tex("table", table_number, item),
        display_item_explanation_tex(item),
        rf"\label{{{label}}}",
        r"\centering",
        r"\begin{center}",
        font_size,
        rf"\setlength{{\tabcolsep}}{{{tabcolsep}}}",
    ]
    if fit_to_width:
        lines.append(r"\resizebox{\linewidth}{!}{%")
    lines.extend(
        [
        rf"\begin{{tabular}}{{{column_spec}}}",
        r"\toprule",
        " & ".join(latex_escape(article_table_header(cell)) for cell in header) + r" \\",
        r"\midrule",
        ]
    )
    for row in data_rows:
        padded = [*row, *[""] * (len(header) - len(row))]
        lines.append(" & ".join(latex_escape(article_table_cell(cell)) for cell in padded[: len(header)]) + r" \\")
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"}" if fit_to_width else "",
            r"\end{center}",
            r"\end{table}",
        ]
    )
    return (
        "\n".join(lines),
        {
            "artifact": item.artifact_path,
            "label": label,
            "title": item.title,
            "article_explanation": display_item_explanation(item),
            "article_explanation_status": "provided" if display_item_explanation(item) else "missing",
            "rows": len(data_rows),
            "columns": len(header),
        },
        None,
    )


def figure_tex(item: DisplayItem, source: Path, article_dir: Path, figure_number: int) -> tuple[str, dict[str, str]]:
    slug = slugify(item.title, f"figure-{figure_number}")
    target = article_dir / "assets" / "figures" / f"figure_{figure_number:02d}_{slug}{source.suffix.lower()}"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    label = f"fig:{slug}"
    display_width, display_height, native_width, native_height, scale, effective_text_size, text_size_status = article_figure_dimensions(source)
    tex = "\n".join(
        [
            r"\begin{figure}[H]",
            r"\begin{center}",
            rf"\includegraphics[width={display_width:.2f}in,height={display_height:.2f}in,keepaspectratio]{{{target.relative_to(article_dir).as_posix()}}}",
            r"\end{center}",
            display_item_title_tex("figure", figure_number, item),
            display_item_explanation_tex(item),
            rf"\label{{{label}}}",
            r"\end{figure}",
        ]
    )
    return tex, {
        "artifact": item.artifact_path,
        "copied_to": target.relative_to(article_dir).as_posix(),
        "label": label,
        "title": item.title,
        "article_explanation": display_item_explanation(item),
        "article_explanation_status": "provided" if display_item_explanation(item) else "missing",
        **article_figure_record_fields(
            display_width,
            display_height,
            native_width,
            native_height,
            scale,
            effective_text_size,
            text_size_status,
        ),
        "article_group": "standalone",
        "kind": "figure",
    }


def composite_columns_that_preserve_text(entries: list[tuple[Path, DisplayItem]], requested_columns: int) -> int:
    requested = max(1, min(requested_columns, len(entries), 3))
    for columns in range(requested, 0, -1):
        panel_width_in = ARTICLE_TEXT_WIDTH_IN * (0.98 / columns)
        statuses: list[str] = []
        for source, _item in entries:
            _display_width, _display_height, _native_width, _native_height, _scale, _effective, status = article_figure_dimensions(
                source,
                max_width_in=panel_width_in,
                max_height_in=MAX_COMPOSITE_PANEL_HEIGHT_IN,
            )
            statuses.append(status)
        if all(status != "too_small_after_article_scaling" for status in statuses):
            return columns
    return 1


def composite_figure_tex(
    group_key: str,
    entries: list[tuple[Path, DisplayItem]],
    article_dir: Path,
    figure_number: int,
) -> tuple[str, dict[str, Any]]:
    ordered = sorted(enumerate(entries), key=lambda pair: panel_order(pair[1][1], pair[0]))
    paths = [entry for _, entry in ordered]
    items = [item for _, item in paths]
    title = group_title(group_key, items)
    explanation = group_explanation(group_key, items)
    requested_columns = group_columns(group_key, items)
    columns = composite_columns_that_preserve_text(paths, requested_columns)
    panel_width = 0.98 / columns
    panel_width_in = ARTICLE_TEXT_WIDTH_IN * panel_width
    label = f"fig:{slugify(title, f'figure-{figure_number}')}"

    lines = [
        r"\begin{figure}[H]",
        r"\centering",
    ]
    panel_records: list[dict[str, str]] = []
    for index, (source, item) in enumerate(paths):
        slug = slugify(panel_title(item), f"panel-{index + 1}")
        target = article_dir / "assets" / "figures" / f"figure_{figure_number:02d}{panel_label(item, index)}_{slug}{source.suffix.lower()}"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        display_width, display_height, native_width, native_height, scale, effective_text_size, text_size_status = article_figure_dimensions(
            source,
            max_width_in=panel_width_in,
            max_height_in=MAX_COMPOSITE_PANEL_HEIGHT_IN,
        )
        panel = panel_label(item, index)
        lines.extend(
            [
                rf"\begin{{minipage}}[t]{{{panel_width:.3f}\linewidth}}",
                r"\centering",
                rf"{{\footnotesize\sffamily\bfseries {latex_escape(panel)} \quad {latex_escape(panel_title(item))}}}\par\vspace{{0.16em}}",
                rf"\includegraphics[width={display_width:.2f}in,height={display_height:.2f}in,keepaspectratio]{{{target.relative_to(article_dir).as_posix()}}}",
                r"\end{minipage}%",
            ]
        )
        if (index + 1) % columns == 0 and index + 1 < len(paths):
            lines.append(r"\par\vspace{0.55em}")
        elif index + 1 < len(paths):
            lines.append(r"\hfill")
        panel_records.append(
            {
                "artifact": item.artifact_path,
                "copied_to": target.relative_to(article_dir).as_posix(),
                "panel_label": panel,
                "panel_title": panel_title(item),
                **article_figure_record_fields(
                    display_width,
                    display_height,
                    native_width,
                    native_height,
                    scale,
                    effective_text_size,
                    text_size_status,
                ),
            }
        )

    group_item = DisplayItem(
        label=title,
        title=title,
        artifact_path="; ".join(item.artifact_path for item in items),
        display_type="figure",
        fields={"article_explanation": explanation},
    )
    lines.extend(
        [
            display_item_title_tex("figure", figure_number, group_item),
            display_item_explanation_tex(group_item),
            rf"\label{{{label}}}",
            r"\end{figure}",
        ]
    )
    return "\n".join(lines), {
        "kind": "composite_figure",
        "article_group": group_key,
        "label": label,
        "title": title,
        "article_explanation": explanation,
        "article_explanation_status": "provided" if explanation else "missing",
        "panel_count": len(panel_records),
        "panel_columns": columns,
        "requested_panel_columns": requested_columns,
        "panel_column_status": "preserved_requested_columns" if columns == requested_columns else "reduced_columns_to_preserve_text_size",
        "panels": panel_records,
    }


def actual_display_items(revision_dir: Path) -> list[Path]:
    paths: list[Path] = []
    figures_dir = revision_dir / "figures"
    if figures_dir.is_dir():
        figure_candidates = [path for path in figures_dir.iterdir() if path.is_file() and path.suffix.lower() in FIGURE_EXTENSIONS]
        figure_preference = {".pdf": 0, ".png": 1, ".jpg": 2, ".jpeg": 2, ".svg": 3}
        by_stem: dict[str, Path] = {}
        for path in sorted(figure_candidates):
            current = by_stem.get(path.stem)
            if current is None or figure_preference.get(path.suffix.lower(), 99) < figure_preference.get(current.suffix.lower(), 99):
                by_stem[path.stem] = path
        paths.extend(by_stem[stem] for stem in sorted(by_stem))
    tables_dir = revision_dir / "tables"
    if tables_dir.is_dir():
        paths.extend(sorted(path for path in tables_dir.iterdir() if path.is_file() and path.suffix.lower() in TABLE_EXTENSIONS))
    return paths


def display_item_map(revision_dir: Path) -> dict[str, DisplayItem]:
    items = parse_display_item_explanations(revision_dir / "display_item_explanations.md")
    mapping: dict[str, DisplayItem] = {}
    for item in items:
        normalized = item.artifact_path.strip("` ")
        mapping[normalized.lower()] = item
        mapping[Path(normalized).name.lower()] = item
    return mapping


def item_for_path(path: Path, revision_dir: Path, mapping: dict[str, DisplayItem]) -> DisplayItem:
    rel_path = path.relative_to(revision_dir).as_posix()
    return mapping.get(rel_path.lower()) or mapping.get(path.name.lower()) or fallback_display_item(
        path,
        revision_dir,
        "table" if path.suffix.lower() in TABLE_EXTENSIONS else "figure",
    )


def build_display_item_tex(revision_dir: Path, article_dir: Path) -> tuple[str, list[dict[str, Any]], list[dict[str, str | int]], list[dict[str, str]], list[dict[str, str]]]:
    mapping = display_item_map(revision_dir)
    figure_snippets: list[str] = []
    table_snippets: list[str] = []
    included_figures: list[dict[str, Any]] = []
    included_tables: list[dict[str, str | int]] = []
    supplemental_items: list[dict[str, str]] = []
    omitted_items: list[dict[str, str]] = []
    figure_number = 1
    table_number = 1
    standalone_figures: dict[str, tuple[Path, DisplayItem]] = {}
    figure_groups: dict[str, list[tuple[Path, DisplayItem]]] = {}
    figure_unit_order: list[tuple[str, str]] = []
    tables: list[tuple[Path, DisplayItem]] = []

    for path in actual_display_items(revision_dir):
        item = item_for_path(path, revision_dir, mapping)
        suffix = path.suffix.lower()
        if suffix in FIGURE_EXTENSIONS:
            group_key = article_group_key(item)
            if group_key:
                if group_key not in figure_groups:
                    figure_groups[group_key] = []
                    figure_unit_order.append(("group", group_key))
                figure_groups[group_key].append((path, item))
            else:
                standalone_key = f"standalone-{len(standalone_figures) + 1}"
                standalone_figures[standalone_key] = (path, item)
                figure_unit_order.append(("standalone", standalone_key))
        elif suffix in TABLE_EXTENSIONS:
            tables.append((path, item))
        else:
            omitted_items.append({"artifact": path.relative_to(revision_dir).as_posix(), "reason": "unsupported display-item format"})

    for unit_kind, unit_key in figure_unit_order:
        if unit_kind == "standalone":
            path, item = standalone_figures[unit_key]
            snippet, record = figure_tex(item, path, article_dir, figure_number)
            figure_snippets.append(snippet)
            included_figures.append(record)
            figure_number += 1
            continue
        entries = figure_groups[unit_key]
        if len(entries) <= 1:
            path, item = entries[0]
            snippet, record = figure_tex(item, path, article_dir, figure_number)
            record["article_group"] = unit_key
            record["grouping_status"] = "single_item_group_rendered_standalone"
            figure_snippets.append(snippet)
            included_figures.append(record)
            figure_number += 1
            continue
        snippet, record = composite_figure_tex(unit_key, entries, article_dir, figure_number)
        figure_snippets.append(snippet)
        included_figures.append(record)
        figure_number += 1

    for path, item in tables:
        snippet, record, supplemental = table_tex(item, path, table_number)
        if snippet and record:
            table_snippets.append(snippet)
            included_tables.append(record)
            table_number += 1
        elif supplemental:
            supplemental_items.append(
                {
                    "artifact": path.relative_to(revision_dir).as_posix(),
                    "reason": supplemental["reason"],
                }
            )

    if not figure_snippets and not table_snippets:
        return "", included_figures, included_tables, supplemental_items, omitted_items

    blocks = ["## Key Figures And Tables", "The following display items summarize the main visual and tabular evidence."]
    blocks.extend(figure_snippets)
    blocks.extend(table_snippets)
    if supplemental_items:
        blocks.append("### Supplementary Display Items")
        for item in supplemental_items:
            blocks.append(f"- {item['artifact']}: {item['reason']}.")
    return "\n\n".join(blocks), included_figures, included_tables, supplemental_items, omitted_items


def build_article_markdown(
    revision_dir: Path,
    article_dir: Path,
    root: Path,
    journal_label: str,
    publication_type: str,
    author_name: str,
    publication_date: str,
    logo_asset_path: str | None,
) -> tuple[str, list[dict[str, Any]], list[dict[str, str | int]], list[dict[str, str]], list[dict[str, str]]]:
    manuscript_path = revision_dir / "manuscript.md"
    if not manuscript_path.is_file():
        raise SystemExit(f"Missing manuscript source: {rel(manuscript_path, root)}")
    markdown = manuscript_path.read_text(encoding="utf-8", errors="replace")
    title, sections = parse_manuscript(markdown)
    display_tex, included_figures, included_tables, supplemental_items, omitted_items = build_display_item_tex(revision_dir, article_dir)

    article_blocks: list[str] = [
        title_block(
            title,
            revision_dir,
            root,
            journal_label,
            publication_type,
            author_name,
            publication_date,
            logo_asset_path,
        )
    ]
    inserted_display_items = False
    references_block: ManuscriptSection | None = None
    abstract_body: str | None = None

    for section in sections:
        if section.title.strip().lower() == "abstract":
            abstract_body = clean_section_body(section.body)
            break
    if abstract_body:
        article_blocks.append(abstract_block(abstract_body))

    for section in sections:
        normalized_title = section.title.strip().lower()
        if normalized_title == "abstract":
            continue
        if "figure" in normalized_title and "table" in normalized_title:
            continue
        if normalized_title == "references":
            references_block = section
            continue
        body = clean_section_body(section.body)
        if not body:
            continue
        article_blocks.append(f"## {section.title}\n\n{body}")
        if not inserted_display_items and re.search(r"result|finding", normalized_title):
            if display_tex:
                article_blocks.append(display_tex)
                inserted_display_items = True

    if display_tex and not inserted_display_items:
        article_blocks.append(display_tex)
    if references_block and references_block.body.strip():
        article_blocks.append(f"## {references_block.title}\n\n{clean_section_body(references_block.body)}")

    article_markdown = "\n\n".join(article_blocks).strip() + "\n"
    article_markdown = normalize_latex_math_text_command_spaces(normalize_inline_code(article_markdown))
    return article_markdown, included_figures, included_tables, supplemental_items, omitted_items


def toolchain_env(repo_root: Path, conda_env: str | None) -> tuple[dict[str, str], list[str]]:
    sys.path.insert(0, str(repo_root))
    from tools.check_render_toolchain import augmented_env

    return augmented_env(repo_root, conda_env)


def pdf_page_count(pdf_path: Path, env: dict[str, str]) -> int | None:
    pdfinfo = shutil.which("pdfinfo", path=env.get("PATH"))
    if not pdfinfo:
        return None
    completed = subprocess.run(
        [pdfinfo, str(pdf_path)],
        env=env,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )
    if completed.returncode != 0:
        return None
    match = re.search(r"^Pages:\s+(\d+)\s*$", completed.stdout, flags=re.MULTILINE)
    return int(match.group(1)) if match else None


def render_article(
    article_dir: Path,
    root: Path,
    conda_env: str | None,
    journal_label: str,
    publication_type: str,
    journal_volume: str,
    journal_date: str,
) -> tuple[int | None, list[str]]:
    env, path_prefixes = toolchain_env(root, conda_env)
    pandoc = shutil.which("pandoc", path=env.get("PATH"))
    xelatex = shutil.which("xelatex", path=env.get("PATH"))
    if not pandoc or not xelatex:
        missing = ", ".join(name for name, path in [("pandoc", pandoc), ("xelatex", xelatex)] if not path)
        raise SystemExit(f"Missing required article render tool(s): {missing}")

    header_path = article_dir / "article_header.tex"
    header_path.write_text(article_header_tex(journal_label, publication_type, journal_volume, journal_date), encoding="utf-8")
    article_md = article_dir / "article.md"
    article_pdf = article_dir / "article.pdf"
    command = [
        pandoc,
        str(article_md.name),
        "--from",
        "markdown+tex_math_dollars+tex_math_single_backslash+raw_tex+pipe_tables",
        "--standalone",
        "--pdf-engine=xelatex",
        "--include-in-header",
        str(header_path.name),
        "--metadata",
        "documentclass=article",
        "--metadata",
        "classoption=11pt",
        "--metadata",
        "geometry=margin=0.72in",
        "--output",
        str(article_pdf.name),
    ]
    completed = subprocess.run(
        command,
        cwd=article_dir,
        env=env,
        text=True,
        capture_output=True,
        timeout=180,
        check=False,
    )
    if completed.returncode != 0:
        failure_log = article_dir / "article_render_error.log"
        failure_log.write_text(
            "Command: " + " ".join(command) + "\n\nstdout:\n" + completed.stdout + "\n\nstderr:\n" + completed.stderr,
            encoding="utf-8",
        )
        raise SystemExit(f"Pandoc/XeLaTeX article render failed. See {failure_log}.")
    return pdf_page_count(article_pdf, env), path_prefixes


def resolve_revision_dir(root: Path, args: argparse.Namespace) -> Path:
    if args.revision_dir:
        return Path(args.revision_dir).resolve()
    if not args.run_id or not args.submission:
        raise SystemExit("Provide either a revision_dir argument or --run-id plus --submission.")
    submission_dir = root / "submissions" / args.run_id / args.submission
    if not submission_dir.is_dir():
        raise SystemExit(f"Missing submission folder: {rel(submission_dir, root)}")
    if args.revision == "latest":
        revisions = sorted(
            (path for path in submission_dir.glob("revision_*") if path.is_dir()),
            key=lambda path: (int(path.name.removeprefix("revision_")) if path.name.removeprefix("revision_").isdigit() else -1, path.name),
        )
        if not revisions:
            raise SystemExit(f"No revision folders found under {rel(submission_dir, root)}")
        return revisions[-1].resolve()
    return (submission_dir / args.revision).resolve()


def build_article(
    revision_dir: Path,
    root: Path,
    output_dir: Path,
    conda_env: str | None,
    replace: bool,
    journal_label: str,
    publication_type: str,
    author_name: str | None,
    publication_date: str,
    journal_volume: str,
    journal_date: str,
) -> ArticleBuildRecord:
    if not revision_dir.is_dir():
        raise SystemExit(f"Missing revision folder: {revision_dir}")
    if output_dir.exists():
        if not replace:
            raise SystemExit(f"{rel(output_dir, root)} already exists; pass --replace to rebuild the generated article.")
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    copy_bundled_fonts(root, output_dir)
    logo_asset_path = prepare_brand_logo_asset(root, output_dir, conda_env)
    resolved_author_name = author_name or infer_author_name(revision_dir)

    article_markdown, included_figures, included_tables, supplemental_items, omitted_items = build_article_markdown(
        revision_dir,
        output_dir,
        root,
        journal_label,
        publication_type,
        resolved_author_name,
        publication_date,
        logo_asset_path,
    )
    article_md = output_dir / "article.md"
    article_md.write_text(article_markdown, encoding="utf-8")
    page_count, path_prefixes = render_article(
        output_dir,
        root,
        conda_env,
        journal_label,
        publication_type,
        journal_volume,
        journal_date,
    )
    report_path = output_dir / "article_build_report.json"
    missing_article_explanations = sum(
        1
        for item in [*included_figures, *included_tables]
        if item.get("article_explanation_status") == "missing"
    )
    figure_flags = figure_text_flag_count(included_figures)
    record = ArticleBuildRecord(
        status="flagged" if missing_article_explanations or figure_flags else "pass",
        article_layout_style="plos_like_single_column",
        renderer="pandoc-xelatex",
        source_revision=rel(revision_dir, root),
        article_markdown=rel(article_md, root),
        article_pdf=rel(output_dir / "article.pdf", root),
        article_build_report=rel(report_path, root),
        brand_logo=BRAND_LOGO_ID,
        included_figures=included_figures,
        included_tables=included_tables,
        supplemental_items=supplemental_items,
        omitted_items=omitted_items,
        missing_article_explanation_count=missing_article_explanations,
        figure_presentation_flag_count=figure_flags,
        publication_type=publication_type,
        author_name=resolved_author_name,
        publication_date=publication_date,
        journal_volume=journal_volume,
        journal_date=journal_date,
        page_count=page_count,
        path_prefixes_added=path_prefixes,
        created_at_utc=datetime.now(timezone.utc).isoformat(),
    )
    report = sanitize_report_paths(asdict(record), root)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a PLOS-like integrated Research Arena article PDF.")
    parser.add_argument("revision_dir", nargs="?", help="Revision folder containing manuscript.md, figures/, and tables/.")
    parser.add_argument("--root", default=".", help="Research Arena repository root.")
    parser.add_argument("--run-id", help="Run id under submissions/<run-id> when revision_dir is omitted.")
    parser.add_argument("--submission", help="Submission folder name when revision_dir is omitted.")
    parser.add_argument("--revision", default="latest", help="Revision folder name or `latest` when revision_dir is omitted.")
    parser.add_argument("--output-dir", help="Output directory. Defaults to <revision_dir>/article.")
    parser.add_argument("--conda-env", help="Optional conda environment name for toolchain path augmentation, e.g. `ag`.")
    parser.add_argument("--replace", action="store_true", help="Replace an existing generated article output directory.")
    parser.add_argument("--journal-label", default="Research Arena", help="Journal name shown in the article header and title block.")
    parser.add_argument("--publication-type", default="Article", help="Publication type shown in the upper-right running header, e.g. Article, Review, Editorial.")
    parser.add_argument("--author-name", help="Author line for the title block. Defaults to an inferred Researcher name.")
    parser.add_argument("--publication-date", default=today_display_date(), help="Publication date shown in the title block.")
    parser.add_argument("--journal-volume", default="Volume 1", help="Journal volume text shown in the footer.")
    parser.add_argument("--journal-date", help="Journal date text shown in the footer. Defaults to --publication-date.")
    args = parser.parse_args()

    root = repo_root_from(Path(args.root))
    revision_dir = resolve_revision_dir(root, args)
    output_dir = Path(args.output_dir).resolve() if args.output_dir else revision_dir / "article"
    journal_date = args.journal_date or args.publication_date
    record = build_article(
        revision_dir,
        root,
        output_dir,
        args.conda_env,
        args.replace,
        args.journal_label,
        args.publication_type,
        args.author_name,
        args.publication_date,
        args.journal_volume,
        journal_date,
    )
    print(f"Built article PDF: {record.article_pdf}")
    print(f"Build report: {record.article_build_report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
