#!/usr/bin/env python3
"""Render the current Research Arena architecture schematic as a PDF."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


INCH = 72
PAGE_WIDTH = 17 * INCH
PAGE_HEIGHT = 11 * INCH

PALETTE = {
    "paper": "#FFFFFF",
    "panel": "#FFFFFF",
    "ink": "#19242B",
    "muted": "#58656E",
    "line": "#CBD2D6",
    "arrow": "#52606A",
    "blue": "#DCEAF7",
    "green": "#DFF0E7",
    "amber": "#F6E3BE",
    "rose": "#F3DAD5",
    "violet": "#E5DDF4",
    "teal": "#D8EEF0",
    "slate": "#253746",
}


def c(hex_value: str) -> colors.Color:
    return colors.HexColor(hex_value)


def register_fonts(root: Path) -> tuple[str, str]:
    font_dir = root / "assets" / "fonts" / "inter"
    regular = font_dir / "Inter-Regular.ttf"
    bold = font_dir / "Inter-Bold.ttf"
    if regular.exists() and bold.exists():
        pdfmetrics.registerFont(TTFont("Inter", regular.as_posix()))
        pdfmetrics.registerFont(TTFont("Inter-Bold", bold.as_posix()))
        return "Inter", "Inter-Bold"
    return "Helvetica", "Helvetica-Bold"


def set_text(canv: canvas.Canvas, font: str, size: float, color: str) -> None:
    canv.setFont(font, size)
    canv.setFillColor(c(color))


def draw_wrapped(
    canv: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    width: float,
    font: str,
    size: float,
    color: str,
    leading: float | None = None,
    align: str = "left",
) -> float:
    leading = leading or size * 1.32
    set_text(canv, font, size, color)
    current_y = y
    for paragraph in text.split("\n"):
        lines = simpleSplit(paragraph, font, size, width)
        if not lines:
            current_y -= leading
            continue
        for line in lines:
            if align == "center":
                canv.drawCentredString(x + width / 2, current_y, line)
            elif align == "right":
                canv.drawRightString(x + width, current_y, line)
            else:
                canv.drawString(x, current_y, line)
            current_y -= leading
    return current_y


def round_box(
    canv: canvas.Canvas,
    x: float,
    y: float,
    width: float,
    height: float,
    fill: str,
    stroke: str = "line",
    radius: float = 10,
    stroke_width: float = 1.1,
) -> None:
    canv.setFillColor(c(PALETTE[fill]))
    canv.setStrokeColor(c(PALETTE[stroke]))
    canv.setLineWidth(stroke_width)
    canv.roundRect(x, y, width, height, radius, stroke=1, fill=1)


def section_label(canv: canvas.Canvas, text: str, x: float, y: float, width: float, bold_font: str) -> None:
    set_text(canv, bold_font, 10.4, PALETTE["muted"])
    canv.drawCentredString(x + width / 2, y, text.upper())
    canv.setStrokeColor(c(PALETTE["line"]))
    canv.setLineWidth(0.8)
    canv.line(x, y - 8, x + width, y - 8)


def stage_box(
    canv: canvas.Canvas,
    x: float,
    y: float,
    width: float,
    height: float,
    step: str,
    title: str,
    body: str,
    fill: str,
    regular: str,
    bold: str,
) -> None:
    round_box(canv, x, y, width, height, fill)
    canv.setFillColor(c(PALETTE["slate"]))
    canv.circle(x + 20, y + height - 25, 14, stroke=0, fill=1)
    set_text(canv, bold, 9.6, "#FFFFFF")
    canv.drawCentredString(x + 20, y + height - 28, step)
    set_text(canv, bold, 13.8, PALETTE["ink"])
    canv.drawString(x + 42, y + height - 29, title)
    draw_wrapped(canv, body, x + 16, y + height - 61, width - 32, regular, 10.4, PALETTE["muted"], 13.5)


def info_box(
    canv: canvas.Canvas,
    x: float,
    y: float,
    width: float,
    height: float,
    title: str,
    body: str,
    fill: str,
    regular: str,
    bold: str,
    title_size: float = 11.6,
    body_size: float = 8.4,
) -> None:
    round_box(canv, x, y, width, height, fill)
    set_text(canv, bold, title_size, PALETTE["ink"])
    canv.drawString(x + 16, y + height - 27, title)
    draw_wrapped(canv, body, x + 16, y + height - 57, width - 32, regular, body_size, PALETTE["muted"], body_size * 1.35)


def draw_logo(canv: canvas.Canvas, x: float, y: float, regular: str, bold: str) -> None:
    """Draw the Research Arena Evidence Gain logo from the brand SVG."""
    set_text(canv, bold, 31, "#1F2937")
    canv.drawString(x, y + 34, "\u0394E")
    canv.setStrokeColor(c("#D7E3EC"))
    canv.setLineWidth(1.4)
    canv.line(x + 70, y + 16, x + 70, y + 86)
    set_text(canv, bold, 24, "#1F2937")
    canv.drawString(x + 90, y + 62, "Research")
    set_text(canv, bold, 24, "#2C7FB8")
    canv.drawString(x + 90, y + 34, "Arena")
    set_text(canv, bold, 7.8, "#4B5563")
    canv.drawString(x + 91, y + 14, "EVIDENCE GAIN")


def arrow_head(canv: canvas.Canvas, tip_x: float, tip_y: float, angle: float, color: str, size: float = 7) -> None:
    left = angle + math.pi * 0.82
    right = angle - math.pi * 0.82
    points = [
        tip_x,
        tip_y,
        tip_x + size * math.cos(left),
        tip_y + size * math.sin(left),
        tip_x + size * math.cos(angle + math.pi),
        tip_y + size * math.sin(angle + math.pi),
        tip_x + size * math.cos(right),
        tip_y + size * math.sin(right),
    ]
    canv.setFillColor(c(color))
    path = canv.beginPath()
    path.moveTo(points[0], points[1])
    path.lineTo(points[2], points[3])
    path.lineTo(points[4], points[5])
    path.lineTo(points[6], points[7])
    path.close()
    canv.drawPath(path, stroke=0, fill=1)


def poly_arrow(
    canv: canvas.Canvas,
    points: list[tuple[float, float]],
    color: str | None = None,
    width: float = 1.4,
    dashed: bool = False,
) -> None:
    color = color or PALETTE["arrow"]
    canv.setStrokeColor(c(color))
    canv.setLineWidth(width)
    canv.setDash(4, 3) if dashed else canv.setDash()
    for start, end in zip(points, points[1:]):
        canv.line(start[0], start[1], end[0], end[1])
    canv.setDash()
    x1, y1 = points[-2]
    x2, y2 = points[-1]
    arrow_head(canv, x2, y2, math.atan2(y2 - y1, x2 - x1), color)


def render(output: Path, root: Path) -> None:
    regular, bold = register_fonts(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    canv = canvas.Canvas(output.as_posix(), pagesize=(PAGE_WIDTH, PAGE_HEIGHT))
    canv.setTitle("What Research Arena Provides")
    canv.setAuthor("Research Arena")
    canv.setSubject("Simple overview of the Research Arena workflow")

    canv.setFillColor(c(PALETTE["paper"]))
    canv.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)

    draw_logo(canv, PAGE_WIDTH - 285, 667, regular, bold)

    set_text(canv, bold, 31, PALETTE["ink"])
    canv.drawString(56, 742, "What Research Arena Provides")
    draw_wrapped(
        canv,
        "A structured way to run agent-based research: set the rules, test ideas, build evidence, review it, and deliver a verified output.",
        56,
        718,
        810,
        regular,
        12.2,
        PALETTE["muted"],
        15.5,
    )
    section_label(canv, "Research workflow", 56, 676, 1112, bold)
    pipeline_y = 430
    box_w = 190
    gap = 42
    xs = [50 + i * (box_w + gap) for i in range(5)]
    pipeline = [
        (
            "01",
            "Set the rules",
            "Define the dataset, study scope, compute budget, success bar, and who is responsible for each part.",
            "blue",
        ),
        (
            "02",
            "Test ideas early",
            "Researcher agents inspect the data, run small pilots, and propose studies before larger analysis starts.",
            "amber",
        ),
        (
            "03",
            "Run studies",
            "Each Researcher creates its own analysis, results, figures, manuscript draft, and reading package.",
            "green",
        ),
        (
            "04",
            "Review and improve",
            "Integrity checks and Referees ask concrete questions tied to files, results, and missing evidence.",
            "rose",
        ),
        (
            "05",
            "Ship a decision",
            "The Editor compares the evidence, freezes the record, and accepts, downgrades, or rejects the output.",
            "violet",
        ),
    ]
    for x, (step, title, body, fill) in zip(xs, pipeline):
        stage_box(canv, x, pipeline_y, box_w, 138, step, title, body, fill, regular, bold)
    for i in range(4):
        poly_arrow(canv, [(xs[i] + box_w + 14, pipeline_y + 69), (xs[i + 1] - 14, pipeline_y + 69)])

    poly_arrow(
        canv,
        [
            (xs[3] + box_w / 2, pipeline_y - 10),
            (xs[3] + box_w / 2, pipeline_y - 52),
            (xs[2] + box_w / 2, pipeline_y - 52),
            (xs[2] + box_w / 2, pipeline_y - 10),
        ],
        dashed=True,
    )
    set_text(canv, regular, 10.0, PALETTE["muted"])
    canv.drawCentredString((xs[2] + xs[3] + box_w) / 2, pipeline_y - 42, "review questions drive revisions")

    canv.setFillColor(c(PALETTE["slate"]))
    canv.roundRect(116, 330, 992, 34, 8, stroke=0, fill=1)
    set_text(canv, bold, 11.2, "#FFFFFF")
    canv.drawCentredString(
        612,
        342,
        "No hidden master script: researchers, reviewers, auditors, and editor each leave their own visible record.",
    )

    section_label(canv, "Quality controls", 116, 288, 992, bold)
    bottom_y = 134
    bottom_h = 120
    bottom_specs = [
        (
            116,
            280,
            "Automatic checks",
            "Scripts verify files, hashes, reruns, package contents, and whether the run happened in the right order.",
            "blue",
        ),
        (
            472,
            280,
            "Expert-style review",
            "LLM agents judge whether the study is meaningful, original enough, well reviewed, and honest about limits.",
            "green",
        ),
        (
            828,
            280,
            "Verified handoff",
            "A freeze record locks the evidence before the Editor decides; the final package is ready to read and audit.",
            "violet",
        ),
    ]
    for x, width, title, body, fill in bottom_specs:
        info_box(canv, x, bottom_y, width, bottom_h, title, body, fill, regular, bold, title_size=14.4, body_size=10.4)
    poly_arrow(canv, [(420, bottom_y + 60), (448, bottom_y + 60)])
    poly_arrow(canv, [(776, bottom_y + 60), (804, bottom_y + 60)])

    canv.showPage()
    canv.save()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render the Research Arena architecture schematic PDF.")
    parser.add_argument(
        "--output",
        default="assets/research_arena_workflow.pdf",
        help="Output PDF path relative to the Research Arena root.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parents[1]
    output = Path(args.output)
    if not output.is_absolute():
        output = root / output
    render(output, root)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
