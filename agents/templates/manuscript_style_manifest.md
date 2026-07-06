# Manuscript Style Manifest

line_numbers: true
manuscript_font_family: Inter (bundled open-source font)
figure_font_family: Inter (bundled open-source font)
math_font_family: LaTeX-like serif math (standard XeLaTeX math or Matplotlib STIX/Computer-Modern-style mathtext)
numbered_equations: true
math_rendering_check: pass
inline_math_rendering_check: pass
pdf_renderer: pandoc-xelatex
render_toolchain_report: runs/<run-id>/render_toolchain_report.json
visual_pdf_review: pass
figure_typography_review: pass
figure_presentation_audit: <path/to/figure_presentation_audit.json or not required>
figure_style_boundary: style helper only; display concepts documented in display_item_plan.md
known_style_limits: none

## Evidence

- Manuscript PDF: `<path/to/manuscript.pdf>`
- Manuscript source: `<path/to/manuscript.md or manuscript.tex>`
- Figure artifacts checked: `<path/to/figures/>`
- Display item plan: `<path/to/display_item_plan.md>`
- Figure presentation audit: `<path/to/figure_presentation_audit.json or not required>`
- Renderer command or method: `<command or concise description>`
- Rendering toolchain report: `runs/<run-id>/render_toolchain_report.json`
- Font fallback, if any: `<none or explanation>`
- Bundled font evidence: `assets/fonts/inter/Inter-Regular.ttf` registered or used through `fontspec`
- Math rendering evidence: `<visual inspection, pdftotext/strings check, or manuscript_render_report.json path confirming inline and displayed math, including serif regular operator/text labels such as macro AUROC or OR>`

## Equation Numbering Policy

Every displayed mathematical expression uses a numbered LaTeX environment such as
`equation`, `align`, `gather`, or `multline`, with a stable `\label{eq:...}` when
the manuscript references it. The final `manuscript.pdf` must show rendered
mathematical notation and visible equation numbers, not raw LaTeX source text.
Inline mathematical symbols and short definitions must also render as LaTeX-like
serif math, not as code spans or raw `$...$` / `\(...\)` text.
Roman/operator/text labels inside equations must render in regular serif type;
variables and Greek/math symbols should render in the matching italic serif math
style.
