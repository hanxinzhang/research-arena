"""Render a line-numbered manuscript PDF with checked math rendering.

By default this helper uses Pandoc/XeLaTeX so displayed equations are true TeX
display math and inline equations use the same LaTeX-style serif math family.
The Matplotlib mathtext renderer remains available only as an explicit compact
demo/internal-review fallback when TeX tools are unavailable.

Example:
    python agents/templates/render_manuscript_pdf.py manuscript.md manuscript.pdf \
        --repo-root .
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


BUNDLED_FONT_FAMILY = "Inter"
BUNDLED_FONT_DIR = Path("assets") / "fonts" / "inter"
BUNDLED_FONT_FILES = [
    "Inter-Regular.ttf",
    "Inter-Bold.ttf",
    "Inter-Italic.ttf",
    "Inter-BoldItalic.ttf",
]
INLINE_MATH_PATTERN = re.compile(r"(?<!\\)\$(?!\$)(.+?)(?<!\\)\$(?!\$)")
PAREN_INLINE_MATH_PATTERN = re.compile(r"\\\((.+?)\\\)")
INLINE_CODE_PATTERN = re.compile(r"(?<!\\)`([^`\n]+)`")
TEXT_MATH_COMMAND_PATTERN = re.compile(
    r"\\(?:operatorname|operatornamewithlimits|text|textrm|textnormal|mathrm)\{([^{}]+)\}"
)
LATEX_TEXT_MATH_COMMAND_PATTERN = re.compile(
    r"\\(?P<command>operatornamewithlimits|operatorname|mathrm|textrm|textnormal|text)\{(?P<content>[^{}]+)\}"
)
DISPLAY_MATH_FONT_SIZE = 16.5
DISPLAY_MATH_LINE_HEIGHT = 0.072
DISPLAY_MATH_TOP_PADDING = 0.010
DISPLAY_MATH_BOTTOM_PADDING = 0.014
DISPLAY_MATH_X = 0.50
DISPLAY_EQUATION_NUMBER_X = 0.92


@dataclass
class Block:
    kind: str
    text: str
    level: int = 0
    equation_number: int | None = None


def find_repo_root(start: Path) -> Path:
    for parent in [start.resolve(), *start.resolve().parents]:
        if (parent / BUNDLED_FONT_DIR / "Inter-Regular.ttf").is_file():
            return parent
    raise SystemExit(
        "Could not find assets/fonts/inter/Inter-Regular.ttf. "
        "Pass --repo-root pointing to the research-arena folder."
    )


def register_fonts(repo_root: Path) -> None:
    import matplotlib as mpl
    import matplotlib.font_manager as font_manager

    font_dir = repo_root / BUNDLED_FONT_DIR
    for filename in BUNDLED_FONT_FILES:
        font_manager.fontManager.addfont(str(font_dir / filename))
    params = {
        "font.family": "sans-serif",
        "font.sans-serif": [BUNDLED_FONT_FAMILY],
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "mathtext.fontset": "stix",
        "mathtext.default": "it",
        "text.parse_math": True,
    }
    if "mathtext.fallback" in mpl.rcParams:
        params["mathtext.fallback"] = "cm"
    mpl.rcParams.update(params)


def starts_display_math(line: str) -> tuple[str, str] | None:
    stripped = line.strip()
    env_match = re.match(r"\\begin\{(equation\*?|align\*?|gather\*?|multline\*?)\}", stripped)
    if env_match:
        env = env_match.group(1)
        return (f"\\end{{{env}}}", stripped)
    if stripped.startswith("$$"):
        return ("$$", stripped[2:].strip())
    if stripped.startswith(r"\["):
        return (r"\]", stripped[2:].strip())
    return None


def parse_markdown(markdown: str) -> list[Block]:
    blocks: list[Block] = []
    paragraph: list[str] = []
    lines = markdown.splitlines()
    i = 0
    equation_number = 1

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            blocks.append(Block("paragraph", " ".join(part.strip() for part in paragraph if part.strip())))
            paragraph = []

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        math_start = starts_display_math(line)
        if math_start:
            flush_paragraph()
            end_marker, first = math_start
            math_lines: list[str] = []
            if end_marker in {"$$", r"\]"} and first.endswith(end_marker):
                math_lines.append(first[: -len(end_marker)].strip())
                i += 1
                blocks.append(Block("equation", "\n".join(math_lines), equation_number=equation_number))
                equation_number += 1
                continue
            if end_marker not in {"$$", r"\]"} and end_marker in stripped:
                math_lines.append(line)
                i += 1
                blocks.append(Block("equation", "\n".join(math_lines), equation_number=equation_number))
                equation_number += 1
                continue
            if end_marker in {"$$", r"\]"} and first:
                math_lines.append(first)
            else:
                math_lines.append(line)
            i += 1
            while i < len(lines):
                current = lines[i]
                if current.strip().endswith(end_marker):
                    tail = current.strip()
                    if end_marker in {"$$", r"\]"}:
                        tail = tail[: -len(end_marker)].strip()
                    if tail:
                        math_lines.append(tail)
                    else:
                        math_lines.append(current)
                    i += 1
                    break
                math_lines.append(current)
                i += 1
            blocks.append(Block("equation", "\n".join(math_lines), equation_number=equation_number))
            equation_number += 1
            continue

        heading = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if heading:
            flush_paragraph()
            blocks.append(Block("heading", heading.group(2).strip(), level=len(heading.group(1))))
            i += 1
            continue

        if not stripped:
            flush_paragraph()
            blocks.append(Block("blank", ""))
            i += 1
            continue

        paragraph.append(line)
        i += 1

    flush_paragraph()
    return blocks


def clean_math_fragment(source: str) -> str:
    text = source.strip()
    text = re.sub(r"\\begin\{(?:equation\*?|align\*?|gather\*?|multline\*?)\}", "", text)
    text = re.sub(r"\\end\{(?:equation\*?|align\*?|gather\*?|multline\*?)\}", "", text)
    text = re.sub(r"\\label\{[^}]+\}", "", text)
    text = re.sub(r"\\tag\{[^}]+\}", "", text)
    text = text.replace("$$", "").replace(r"\[", "").replace(r"\]", "")
    text = text.replace("&", "")
    text = TEXT_MATH_COMMAND_PATTERN.sub(lambda match: serif_regular_math_text(match.group(1)), text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def serif_regular_math_text(source: str) -> str:
    content = re.sub(r"\s+", r"\\;", source.strip())
    return rf"\mathrm{{{content}}}"


def clean_equation(source: str) -> list[str]:
    text = clean_math_fragment(source)
    text = text.replace(r"\frac", r"\dfrac")
    parts = [part.strip() for part in re.split(r"\\\\|\\qquad", text) if part.strip()]
    return parts or [text.strip()]


def normalize_inline_math(text: str) -> str:
    return PAREN_INLINE_MATH_PATTERN.sub(lambda match: f"${match.group(1).strip()}$", text)


def normalize_inline_code(text: str) -> str:
    def replace_code_span(match: re.Match[str]) -> str:
        content = match.group(1).replace(r"\`", "`")
        return content.replace("$", r"\$")

    return INLINE_CODE_PATTERN.sub(replace_code_span, text)


def normalize_latex_math_text_command_spaces(text: str) -> str:
    def replace_command(match: re.Match[str]) -> str:
        command = match.group("command")
        content = match.group("content")
        if command in {"operatorname", "operatornamewithlimits", "mathrm"}:
            content = re.sub(r"\s+", r"\\,", content.strip())
        return rf"\{command}{{{content}}}"

    return LATEX_TEXT_MATH_COMMAND_PATTERN.sub(replace_command, text)


def sanitize_inline_math(text: str) -> str:
    normalized = normalize_inline_math(normalize_inline_code(text))
    return INLINE_MATH_PATTERN.sub(lambda match: f"${clean_math_fragment(match.group(1))}$", normalized)


def inline_math_expressions(text: str) -> list[str]:
    normalized = sanitize_inline_math(text)
    return [
        clean_math_fragment(match.group(1))
        for match in INLINE_MATH_PATTERN.finditer(normalized)
        if clean_math_fragment(match.group(1))
    ]


def validate_math(expressions: list[str]) -> None:
    from matplotlib.mathtext import MathTextParser

    parser = MathTextParser("path")
    for expression in expressions:
        if not expression:
            continue
        try:
            parser.parse(f"${expression}$", dpi=120)
        except Exception as exc:
            raise SystemExit(
                "Math rendering failed for expression:\n"
                f"{expression}\n\n"
                "Use simpler mathtext-compatible LaTeX in the fallback renderer, "
                "or render the manuscript with Pandoc/XeLaTeX.\n"
                f"Original error: {exc}"
            ) from exc


def wrapped_lines(text: str, width: int = 92) -> tuple[list[str], int]:
    normalized = sanitize_inline_math(text)
    expressions = inline_math_expressions(normalized)
    validate_math(expressions)
    tokens = re.findall(r"\$[^$]+\$[.,;:]?|\S+", normalized)
    if not tokens:
        return [""], len(expressions)
    lines: list[str] = []
    current = ""
    for token in tokens:
        candidate = token if not current else f"{current} {token}"
        if len(candidate) <= width:
            current = candidate
            continue
        if current:
            lines.append(current)
        current = token
    if current:
        lines.append(current)
    return lines or [""], len(expressions)


def toolchain_env(repo_root: Path, conda_env: str | None = None) -> tuple[dict[str, str], list[str]]:
    sys.path.insert(0, str(repo_root))
    try:
        from tools.check_render_toolchain import augmented_env

        return augmented_env(repo_root, conda_env)
    except Exception:
        env = os.environ.copy()
        required_tools = repo_root.parent / "required tools"
        extra_paths = [
            required_tools / "pandoc-3.10-arm64" / "bin",
            Path("/usr/local/texlive/2026basic/bin/universal-darwin"),
            Path("/Library/TeX/texbin"),
            Path("/opt/homebrew/bin"),
            Path("/usr/local/bin"),
        ]
        prefixes = [str(path) for path in extra_paths if path.is_dir()]
        current_path = env.get("PATH", "")
        env["PATH"] = os.pathsep.join([*prefixes, current_path]) if prefixes else current_path
        return env, prefixes


def sanitize_report_paths(value: object, repo_root: Path) -> object:
    if isinstance(value, dict):
        return {key: sanitize_report_paths(item, repo_root) for key, item in value.items()}
    if isinstance(value, list):
        return [sanitize_report_paths(item, repo_root) for item in value]
    if not isinstance(value, str):
        return value

    replacements = [
        ((repo_root.parent / "required tools").resolve().as_posix(), "<required_tools>"),
        (repo_root.resolve().as_posix(), "<research_arena_root>"),
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


def pandoc_xelatex_available(env: dict[str, str]) -> bool:
    return bool(shutil.which("pandoc", path=env.get("PATH")) and shutil.which("xelatex", path=env.get("PATH")))


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


def pandoc_header() -> str:
    return r"""
\usepackage{amsmath,amssymb,mathtools}
\usepackage{booktabs}
\usepackage{caption}
\usepackage{fontspec}
\usepackage{lineno}
\usepackage{microtype}
\usepackage{titlesec}
\usepackage{xcolor}

\IfFileExists{assets/fonts/inter/Inter-Regular.ttf}{
  \setsansfont{Inter}[
    Path=assets/fonts/inter/,
    UprightFont=Inter-Regular.ttf,
    BoldFont=Inter-Bold.ttf,
    ItalicFont=Inter-Italic.ttf,
    BoldItalicFont=Inter-BoldItalic.ttf
  ]
}{}
\renewcommand{\familydefault}{\sfdefault}
\let\ResearchArenaOriginalText\text
\renewcommand{\text}[1]{\ResearchArenaOriginalText{\normalfont\rmfamily #1}}

\definecolor{headingcolor}{HTML}{1F2937}
\definecolor{subheadingcolor}{HTML}{374151}
\titleformat{\section}
  {\Large\bfseries\color{headingcolor}}
  {\thesection}{0.75em}{}
\titleformat{\subsection}
  {\large\bfseries\color{subheadingcolor}}
  {\thesubsection}{0.75em}{}
\titleformat{\subsubsection}
  {\normalsize\bfseries\color{subheadingcolor}}
  {\thesubsubsection}{0.75em}{}

\captionsetup{
  font=small,
  labelfont=bf,
  margin=0.5in
}

\AtBeginDocument{
  \linenumbers
  \modulolinenumbers[1]
}
"""


def render_pdf_pandoc_xelatex(source: Path, output_pdf: Path, repo_root: Path, conda_env: str | None = None) -> dict[str, object]:
    env, path_prefixes = toolchain_env(repo_root, conda_env)
    if not pandoc_xelatex_available(env):
        missing = [
            name
            for name in ["pandoc", "xelatex"]
            if not shutil.which(name, path=env.get("PATH"))
        ]
        raise RuntimeError("Missing Pandoc/XeLaTeX tool(s): " + ", ".join(missing))

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="research_arena_xelatex_") as temp_name:
        temp_dir = Path(temp_name)
        header = temp_dir / "research_arena_header.tex"
        staged_source = temp_dir / "manuscript.md"
        header.write_text(pandoc_header(), encoding="utf-8")
        staged_markdown = normalize_latex_math_text_command_spaces(
            normalize_inline_code(source.read_text(encoding="utf-8", errors="replace"))
        )
        staged_source.write_text(staged_markdown, encoding="utf-8")

        command = [
            shutil.which("pandoc", path=env.get("PATH")) or "pandoc",
            str(staged_source),
            "--from",
            "markdown+tex_math_dollars+tex_math_single_backslash",
            "--standalone",
            "--pdf-engine=xelatex",
            "--include-in-header",
            str(header),
            "--resource-path",
            os.pathsep.join([str(repo_root), str(source.parent)]),
            "--metadata",
            "documentclass=article",
            "--metadata",
            "classoption=11pt",
            "--metadata",
            "geometry=margin=1in",
            "--output",
            str(output_pdf),
        ]
        completed = subprocess.run(
            command,
            cwd=repo_root,
            env=env,
            text=True,
            capture_output=True,
            timeout=120,
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                "Pandoc/XeLaTeX manuscript rendering failed.\n\n"
                f"Command: {' '.join(command)}\n\n"
                f"stdout:\n{completed.stdout}\n\nstderr:\n{completed.stderr}"
            )

    markdown = source.read_text(encoding="utf-8", errors="replace")
    blocks = parse_markdown(markdown)
    display_equations = sum(1 for block in blocks if block.kind == "equation")
    inline_math = sum(len(inline_math_expressions(block.text)) for block in blocks if block.kind == "paragraph")
    return {
        "pdf_renderer": "pandoc-xelatex",
        "math_rendering_check": "pass",
        "line_numbers": True,
        "font_family": BUNDLED_FONT_FAMILY,
        "math_font_policy": "LaTeX/XeLaTeX serif math: variables italic serif, operator/text labels regular serif.",
        "math_text_commands_normalized": True,
        "markdown_code_spans_normalized": True,
        "display_equations_rendered": display_equations,
        "inline_math_spans_rendered": inline_math,
        "path_prefixes_added": path_prefixes,
        "renderer_command": "pandoc --pdf-engine=xelatex",
        "page_count": pdf_page_count(output_pdf, env),
    }


def render_pdf_matplotlib(blocks: list[Block], output_pdf: Path) -> dict[str, object]:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    rendered_equations = 0
    page_count = 0
    line_number = 1
    index = 0
    rendered_inline_math = 0

    with PdfPages(output_pdf) as pdf:
        while index < len(blocks):
            fig = plt.figure(figsize=(8.27, 11.69))
            ax = fig.add_axes([0, 0, 1, 1])
            ax.axis("off")
            y = 0.955
            page_count += 1
            ax.text(0.5, 0.985, f"Page {page_count}", ha="center", va="top", fontsize=8, color="#6b7280")

            while index < len(blocks) and y > 0.065:
                block = blocks[index]
                if block.kind == "blank":
                    y -= 0.016
                    index += 1
                    continue

                if block.kind == "heading":
                    size = 15 if block.level == 1 else 12 if block.level == 2 else 10.5
                    gap = 0.034 if block.level == 1 else 0.028
                    heading_width = 68 if block.level == 1 else 82
                    heading_lines, _ = wrapped_lines(block.text, width=heading_width)
                    needed = 0.024 * len(heading_lines) + gap - 0.020
                    if y - needed < 0.06:
                        break
                    for heading_line in heading_lines:
                        ax.text(0.045, y, f"{line_number:>4}", ha="right", va="top", fontsize=6.8, color="#6b7280")
                        ax.text(0.075, y, heading_line, ha="left", va="top", fontsize=size, fontweight="bold", color="#111827", parse_math=True)
                        y -= 0.024
                        line_number += 1
                    y -= gap - 0.024
                    index += 1
                    continue

                if block.kind == "equation":
                    expressions = clean_equation(block.text)
                    validate_math(expressions)
                    needed = (
                        DISPLAY_MATH_TOP_PADDING
                        + DISPLAY_MATH_LINE_HEIGHT * len(expressions)
                        + DISPLAY_MATH_BOTTOM_PADDING
                    )
                    if y - needed < 0.06:
                        break
                    block_top = y
                    y -= DISPLAY_MATH_TOP_PADDING
                    for expression in expressions:
                        center_y = y - DISPLAY_MATH_LINE_HEIGHT / 2
                        ax.text(0.045, center_y, f"{line_number:>4}", ha="right", va="center", fontsize=6.8, color="#6b7280")
                        ax.text(
                            DISPLAY_MATH_X,
                            center_y,
                            f"${expression}$",
                            ha="center",
                            va="center",
                            fontsize=DISPLAY_MATH_FONT_SIZE,
                            color="#111827",
                        )
                        y -= DISPLAY_MATH_LINE_HEIGHT
                        line_number += 1
                    block_center = block_top - (needed - DISPLAY_MATH_BOTTOM_PADDING) / 2
                    ax.text(
                        DISPLAY_EQUATION_NUMBER_X,
                        block_center,
                        f"({block.equation_number})",
                        ha="right",
                        va="center",
                        fontsize=9.5,
                        color="#111827",
                    )
                    rendered_equations += 1
                    y -= DISPLAY_MATH_BOTTOM_PADDING
                    index += 1
                    continue

                lines, inline_math_count = wrapped_lines(block.text)
                for line in lines:
                    if y < 0.065:
                        break
                    ax.text(0.045, y, f"{line_number:>4}", ha="right", va="top", fontsize=6.8, color="#6b7280")
                    ax.text(0.075, y, line, ha="left", va="top", fontsize=9.4, color="#111827", parse_math=True)
                    y -= 0.020
                    line_number += 1
                else:
                    rendered_inline_math += inline_math_count
                    index += 1
                    continue
                break

            pdf.savefig(fig)
            plt.close(fig)

    return {
        "pdf_renderer": "research-arena-matplotlib-mathtext",
        "math_rendering_check": "pass",
        "line_numbers": True,
        "font_family": BUNDLED_FONT_FAMILY,
        "math_font_policy": "LaTeX-like serif mathtext: variables italic serif, operator/text labels regular serif.",
        "display_math_alignment": "centered",
        "display_math_font_size": DISPLAY_MATH_FONT_SIZE,
        "display_math_line_height": DISPLAY_MATH_LINE_HEIGHT,
        "display_fraction_style": "display fractions promoted from \\frac to \\dfrac",
        "math_text_commands_normalized": True,
        "markdown_code_spans_normalized": True,
        "display_equations_rendered": rendered_equations,
        "inline_math_spans_rendered": rendered_inline_math,
        "page_count": page_count,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a Research Arena manuscript PDF with checked math rendering.")
    parser.add_argument("source", help="Input manuscript.md file.")
    parser.add_argument("output_pdf", help="Output manuscript.pdf file.")
    parser.add_argument("--repo-root", help="Path to the research-arena folder. Auto-detected when omitted.")
    parser.add_argument("--report", help="Optional render report JSON path. Defaults to manuscript_render_report.json beside the PDF.")
    parser.add_argument(
        "--engine",
        choices=["auto", "pandoc-xelatex", "matplotlib"],
        default="auto",
        help="Renderer backend. `auto` prefers Pandoc/XeLaTeX and falls back to Matplotlib only when TeX tools are unavailable.",
    )
    parser.add_argument("--conda-env", help="Optional conda environment name for toolchain path augmentation, e.g. `ag`.")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    output_pdf = Path(args.output_pdf).resolve()
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root(Path(__file__))

    report: dict[str, object]
    if args.engine in {"auto", "pandoc-xelatex"}:
        try:
            report = render_pdf_pandoc_xelatex(source, output_pdf, repo_root, args.conda_env)
        except Exception as exc:
            if args.engine == "pandoc-xelatex":
                raise SystemExit(str(exc)) from exc
            register_fonts(repo_root)
            blocks = parse_markdown(source.read_text(encoding="utf-8", errors="replace"))
            report = render_pdf_matplotlib(blocks, output_pdf)
            report["pandoc_xelatex_unavailable"] = str(exc)
    else:
        register_fonts(repo_root)
        blocks = parse_markdown(source.read_text(encoding="utf-8", errors="replace"))
        report = render_pdf_matplotlib(blocks, output_pdf)
    report.update({"source": str(source), "output_pdf": str(output_pdf)})
    report = sanitize_report_paths(report, repo_root)  # type: ignore[assignment]

    report_path = Path(args.report).resolve() if args.report else output_pdf.with_name("manuscript_render_report.json")
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
