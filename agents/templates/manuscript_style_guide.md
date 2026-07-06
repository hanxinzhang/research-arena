# Manuscript Style Guide

Use this guide for every candidate accepted manuscript unless the run-level
`manuscript_quality_contract.md` explicitly downgrades the article type for a
compact non-publication demo.

## Required Manuscript Structure

The manuscript must read like a paper, not a raw report. Use a clear hierarchy:

1. Title.
2. Abstract.
3. Introduction or Background.
4. Results or Findings, with informative subsections.
5. Figure And Table Guide, Display Item Interpretation, or equivalent.
6. Discussion or Interpretation.
7. Methods, with informative subsections.
8. Data and Code Availability.
9. Limitations.
10. Protocol Compliance.
11. References.

Use Markdown headings or LaTeX section commands that render as visually distinct
titles and subtitles. Avoid long undivided sections.

## Article Voice

Each revision's manuscript must be written as the final article a human reader
would see, not as a response memo to Referees, the Integrity Checker, or the
Editor. Put point-by-point answers, issue status, verification claims, and
review-process details in `revision_response.md`, issue ledgers, and verification
matrices.

When a review causes new analysis or clarification, integrate the result into the
article's Methods, Results, Discussion, Limitations, Data and Code Availability, or
Protocol Compliance sections. Do not narrate manuscript changes as revision
mechanics. A reader should understand the evidence without knowing which reviewer
asked for it or which revision added it.

Before acceptance, an LLM-backed reviewer or Editor should apply
`audits/manuscript_article_voice_rubric.md` whenever manuscript prose appears to
answer the review process directly.

## Figure And Table Narrative

For journal-style article PDFs, every included main-text figure and table should
read like a publishable display item. Place a short explanatory paragraph directly
with the figure/table title. The paragraph should state the substantive pattern,
contrast, estimate, uncertainty, model behavior, or limitation shown by the item,
plus any denominator or caveat needed to avoid overclaiming. It should sound like
normal article prose, not instructions to the reader. Use the `Article Explanation` field in
`display_item_explanations.md` as the source. When display-item narrative quality
is uncertain, apply `audits/display_item_narrative_rubric.md`.

## Line Numbers And PDF Rendering

`manuscript.pdf` must include visible line numbers for review unless the run is an
explicit compact demo and the manuscript-quality contract waives the requirement.
For LaTeX renders, use the `lineno` package and enable `\linenumbers`.

Preferred render path:

```text
manuscript.md or manuscript.tex -> XeLaTeX/Pandoc XeLaTeX -> manuscript.pdf
```

Serious-pilot and full runs should use the preferred path and write a passing
`runs/<run-id>/render_toolchain_report.json` with
`tools/check_render_toolchain.py`. The standard Markdown manuscript wrapper is
`agents/templates/render_manuscript_pdf.py`; its default `--engine auto` path
prefers Pandoc/XeLaTeX and reuses the staged toolchain paths checked by the
toolchain report. If Pandoc or XeLaTeX is unavailable, another renderer is
acceptable only for an explicitly downgraded compact demo or internal review
artifact whose manuscript-quality contract sets `allow_fallback_renderer: true`.
The PDF must still show line numbers, clear section hierarchy, readable spacing,
page numbers, rendered mathematical notation, and non-monospace manuscript
typography. Do not use a renderer that prints raw LaTeX or Markdown math syntax
in the PDF body. The explicit Matplotlib fallback
`agents/templates/render_manuscript_pdf.py --engine matplotlib` renders
line-numbered PDFs with bundled Inter typography and Matplotlib mathtext display
equations; its use must be disclosed in `known_style_limits`.

## Fonts

Use open-source sans-serif fonts for manuscript and figure text. Research Arena
bundles Inter at `assets/fonts/inter/` so every user has a known
redistributable default without relying on system fonts. Use the bundled font
unless the run deliberately chooses another accepted open-source family.

Accepted families, in order:

1. Inter from `assets/fonts/inter/`.
2. TeX Gyre Heros.
3. Nimbus Sans.
4. Liberation Sans.
5. Noto Sans.
6. Source Sans 3 or Source Sans Pro.

Do not rely on PDF base Helvetica or Arial as the declared manuscript font. If none
of the accepted families is available, record the fallback and reason in
`manuscript_style_manifest.md`; the Editor should treat the fallback as a
presentation limitation.

## Mathematical Expressions

Every displayed mathematical expression must be valid LaTeX and numbered. Prefer
`equation`, `align`, `gather`, or `multline` environments with labels:

```latex
\begin{equation}
\hat{p}_i = f_{\theta}(x_i), \qquad y_i \in \{0,1\}.
\label{eq:prediction-model}
\end{equation}
```

Use inline math only for short symbols or definitions, but render those symbols as
math with `$...$` or `\(...\)`, not as code spans such as `` `x_i` ``. Inline and
displayed math must use a consistent LaTeX-like serif math style. The
Pandoc/XeLaTeX path leaves equations in the standard serif math family. The
explicit fallback renderer normalizes `$...$` and `\(...\)` spans and draws them
with STIX/Computer-Modern-style Matplotlib mathtext. Text inside equations, such
as `\operatorname{macro AUROC}`, `\mathrm{OR}`, or `\text{calibrated risk}`, must
render as regular upright serif text, while variables such as `x_i`, `\theta`, and
`\hat{p}` remain italic serif math. Do not leave display math in bare `$$ ... $$`
or `\[ ... \]` blocks unless a renderer-specific tag produces a visible equation
number.

For compact-demo fallback PDFs, displayed equations must be visually display-mode
math: centered on the page, larger than inline math, and with legible large
operators and fraction contents. The fallback renderer therefore promotes
displayed `\frac{...}{...}` expressions to `\dfrac{...}{...}` before rendering.
Inline fractions are not promoted.

The final `manuscript.pdf` must be inspected for rendered math. Raw source strings
such as `\begin{equation}`, `\label{eq:...}`, `\hat{p}`, `\frac{...}{...}`, `$x_i$`,
`\(...\)`, `$$`, or `\[...\]` must not appear as ordinary text in the PDF body.
Set `math_rendering_check: pass` and `inline_math_rendering_check: pass` only when
displayed equations and inline mathematical spans are visibly typeset in the
serif math style in the PDF, including upright regular serif operator/text labels
and italic serif variables.

## Figure Typography

Figures must use the same open-source sans-serif family as the manuscript when
possible. For Matplotlib, import `agents/templates/figure_style.py` and call
`apply_research_arena_figure_style()` before creating figures. The helper
registers the bundled Inter font and embeds TrueType fonts in PDFs. If an optional
SVG is generated, text remains editable.

The helper is not a figure-concept template. Use it for typography, label
translation, mark scale, grids, and save behavior, while documenting the
Researcher's own display choices in `display_item_plan.md`.

Figure labels must be understandable without reading source code:

1. Translate internal model names, feature slugs, and column names.
2. Include units, denominators, sample sizes, or cohort definitions where relevant.
3. Use readable legend labels and avoid clipped or overlapping text.
4. Export vector figure artifacts as PDF. SVG is optional.

## Figure And Table Explanation

The manuscript must include a dedicated section such as `Figure And Table Guide`,
`Display Item Interpretation`, or `Figure And Table Annotations`. This section must
explain each figure and table in article-ready scientific prose:

1. what the display item is for;
2. what each axis, row, column, label, legend, color, line, marker, panel, and
   annotation means;
3. any units, denominators, thresholds, sample sizes, cohorts, or split definitions;
4. translations for raw variable, model, feature, or file-derived labels;
5. the summary conclusion supported by the item;
6. the main caveat or common misreading.

Each latest revision must also include `display_item_explanations.md` using
`agents/templates/display_item_explanations.md`. The manuscript section should
summarize this artifact rather than leave readers to decode raw figure/table files.
Use `humanize_label()` from `agents/templates/figure_style.py` or a documented
translation map when plotting source-derived variable, feature, model, cohort, or
metric names. For integrated articles, `display_item_explanations.md` is also the
source of figure grouping decisions: related figures may share an `Article group`
and panel labels, while standalone figures need a rationale.

Each latest revision with main-text display items should also include
`display_item_plan.md` using `agents/templates/display_item_plan.md`. That plan
should explain why the selected display forms, filenames, grouping, and order fit
the Researcher's specific claim rather than a framework-default figure sequence.

## Required Style Manifest

Each latest revision must include `manuscript_style_manifest.md`:

```text
line_numbers: true
manuscript_font_family: <preferred open-source sans-serif family>
figure_font_family: <preferred open-source sans-serif family>
math_font_family: <LaTeX-like serif math family or renderer policy>
numbered_equations: true
math_rendering_check: pass
inline_math_rendering_check: pass
pdf_renderer: <xelatex | pandoc-xelatex | research-arena-matplotlib-mathtext | other>
render_toolchain_report: runs/<run-id>/render_toolchain_report.json
visual_pdf_review: pass
figure_typography_review: pass
figure_presentation_audit: <path/to/figure_presentation_audit.json or not required>
known_style_limits: <none or explicit limitations>
```

The style manifest is evidence for the presentation gate. It does not replace
visual review by Referees, the Integrity Checker, and the Editor.
