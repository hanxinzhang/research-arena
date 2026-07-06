# Manuscript Quality Contract

Run id: `<run-id>`

Selected article type: `<demo | serious pilot | benchmark note | methods note | full Article/Analysis>`

## Hard Presentation Gate

Acceptance requires both credible evidence and clear, paper-level presentation.
A small analysis may justify a smaller manuscript, but it does not justify unclear
writing, unexplained methods, raw variable-name figures, or a raw Markdown PDF.

The Editor must reject or request revision if the accepted package fails this
contract, even when integrity, reproducibility, and issue-resolution gates pass.

## Machine-Readable Audit Settings

Set these values before initial submissions. Demos may use lower values, but the
lower bar must be explicit and the final decision must label the output as a demo.

```text
minimum_manuscript_words: 2500
minimum_methods_words: 500
minimum_display_items: 3
minimum_subsection_count: 3
minimum_numbered_equations: 1
allow_raw_markdown_pdf: false
allow_fallback_renderer: false
require_line_numbers: true
require_numbered_equations: true
require_rendered_math: true
require_display_item_explanations: true
require_human_readable_output: true
require_manuscript_style_manifest: true
require_preferred_sans_fonts: true
require_rendering_toolchain: true
require_integrated_article_pdf: true
```

## Manuscript Requirements

Every candidate accepted manuscript must include:

1. Abstract.
2. Introduction or Background with the motivation, prior-work context, and research
   rationale.
3. Results or Findings with informative subheadings and clear links to tables,
   figures, and `results.json`.
4. A Figure And Table Guide, Display Item Interpretation, or equivalent section
   explaining every submitted figure and table in article-ready scientific prose.
5. Discussion or Interpretation explaining what the evidence means, what it does
   not mean, and how null or weak findings affect the central claim.
6. Methods with enough detail for an expert reader to audit data construction,
   preprocessing, model/statistical formulation, losses or estimands, inference,
   uncertainty, validation, and evaluation.
7. Data and Code Availability.
8. Limitations.
9. Protocol Compliance.
10. References.

For modeling or quantitative submissions, Methods must include mathematical or
formal definitions where appropriate: variables, targets, feature maps,
objectives/losses, fitted models, evaluation estimands, resampling/statistical
tests, and calibration or uncertainty definitions.

The manuscript must use visibly organized section and subsection hierarchy.
Results and Methods should have informative subheadings rather than one long block
of text.

Every revision's manuscript must read as a standalone final article, not as a
response letter, changelog, or audit memo. Reviewer questions, issue IDs,
verification-matrix status, and direct answers to gatekeepers belong in
`revision_response.md`, issue ledgers, and verification matrices. The manuscript
should integrate any review-driven changes as ordinary article prose about the
methods, results, interpretation, limitations, or reproducibility of the study.
When article voice is uncertain, use
`audits/manuscript_article_voice_rubric.md` for an LLM-backed judgment before
acceptance.

Every displayed mathematical expression must be valid LaTeX and numbered. Prefer
`\begin{equation}...\label{eq:name}\end{equation}` or
`\begin{align}...\label{eq:name}\end{align}`. Bare `$$ ... $$` or `\[ ... \]`
display math fails the presentation gate unless it renders with a visible equation
number and the numbering policy is documented.

The final `manuscript.pdf` must render mathematical notation visually, including
both displayed equations and inline math spans. Inline definitions should use
math delimiters such as `$x_i$` or `\(x_i\)`, not code spans such as `` `x_i` ``.
Raw strings such as `\begin{equation}`, `\hat{p}`, `\frac{...}{...}`, `$x_i$`,
`\(...\)`, `$$`, or `\[...\]` must not appear as ordinary text in the PDF body.
The default publication-quality route is Pandoc plus XeLaTeX. Each run must create
`runs/<run-id>/render_toolchain_report.json` with
`tools/check_render_toolchain.py` before acceptance when
`require_rendering_toolchain: true`.

The standard Markdown manuscript wrapper is
`agents/templates/render_manuscript_pdf.py`. Its default `--engine auto` path must
prefer Pandoc/XeLaTeX. The explicit Matplotlib fallback
`agents/templates/render_manuscript_pdf.py --engine matplotlib` may be used for
internal review or explicitly downgraded compact demos only when
`allow_fallback_renderer: true`. A fallback-rendered manuscript cannot declare
`known_style_limits: none`; the style manifest must state the fallback limitation
and the Editor must not treat it as publication-grade rendering.

## Figure And Table Requirements

Figures and tables must be presentation artifacts, not merely debugging outputs.
They must use human-readable labels, captions or caption-equivalent notes, units
where applicable, sample sizes or denominators where relevant, and names that a
reader can understand without reading the code.

The manuscript must include a dedicated figure/table explanation section. For each
figure and table, this section must explain:

1. what the item is for;
2. what each axis, row, column, label, legend, color, marker, line, panel mark,
   threshold, and annotation means;
3. units, denominators, sample sizes, cohorts, folds, or split definitions;
4. the summary conclusion supported by the item;
5. the main caveat or common misreading.

When `article/article.pdf` is required, every included figure and table must also
have a title-adjacent explanatory paragraph. It should be short, simple, and
written as ordinary article prose: one paragraph stating the substantive pattern,
contrast, estimate, uncertainty, model behavior, or limitation shown by the item.
Do not merely name the artifact file, and avoid meta-commentary about instructing
or orienting the reader. The preferred source is the `Article Explanation` field
in `display_item_explanations.md`.

Figure text must use the bundled open-source Inter family in `assets/fonts/inter/`
by default. TeX Gyre Heros, Nimbus Sans, Liberation Sans, Noto Sans, Source Sans 3,
or Source Sans Pro are acceptable deliberate alternatives. Use
`agents/templates/figure_style.py` or equivalent Matplotlib settings for generated
figures. Use `humanize_label()` from that template or an explicit translation map
when source columns, features, models, or cohorts have code-style names. Labels,
legends, tick text, panel marks, annotations, and captions must be large enough to
read in the exported artifact. For article PDFs, figure typography must be
article-normalized rather than merely readable: titles, subtitles, axis labels,
tick labels, legends, annotations, and colorbar labels should use one shared text
size near the article body text, and bars, lines, dots, boxplot elements, axes, and
error bars should be scaled for that same final size. Do not shrink oversized
source figures as a substitute for article-native plotting. Run
`tools/figure_presentation_audit.py <revision-dir> --write` when figures are
included in `article.pdf`.

`agents/templates/figure_style.py` is a style helper, not a figure-program
template. It may standardize typography, label translation, line widths, marker
sizes, grids, and saving, but it must not determine which figures exist, what
they are called, or what sequence they follow.

Each latest revision with main-text display items must include
`display_item_plan.md` using `agents/templates/display_item_plan.md`. The plan
records the Researcher's own visual/table strategy, claim role for each item,
alternative display forms considered, and any similarity risk relative to other
Researchers, prior revisions, or framework examples. If multiple Researchers
produce highly similar figure sequences, or if the boundary between shared style
and shared display program is disputed, write
`runs/<run-id>/display_program_independence_review.md` using
`audits/display_program_independence_rubric.md`.

Raw internal identifiers such as `model_v3`, `ecg_plus_metadata_random_forest`,
feature slugs, or column names may appear in supplements or tables only when they
are also translated for human readers. Avoid underscore-heavy labels in figures and
tables whenever possible; use title case, spaces, concise units, and legends that a
domain reader can understand without opening `analysis.py`.

Display items should be organized as coherent figure concepts. A multi-format
export of the same figure counts as one display item.

Each latest revision must include `display_item_explanations.md` using
`agents/templates/display_item_explanations.md`. It must map each figure and table
artifact to its manuscript discussion, label/legend/annotation explanations, raw
label translations, title-adjacent article explanation, summary conclusion, and
caveat. When `article/article.pdf` is required, each figure must also declare an
article grouping decision: `standalone` with a rationale, or a shared group id
with panel labels, group title, and group explanation.

## PDF Requirements

`manuscript.pdf` must be visually readable as a line-numbered manuscript. It may be
text-only, but it must not be a raw Markdown dump with visible `#` headings,
backticks, unrendered table syntax, broken wrapping, or monospace-only formatting
unless the run is explicitly a compact non-publication demo and
`allow_raw_markdown_pdf` is set to `true`.

Use the bundled open-source Inter family for manuscript rendering by default. The
default LaTeX route is Pandoc/XeLaTeX with the `lineno` package enabled and
standard LaTeX-style serif math for all inline and displayed mathematical
expressions. Equation variables should render as italic serif math, while
operator/text labels such as `\operatorname{macro AUROC}`, `\mathrm{OR}`, or
`\text{calibrated risk}` should render as upright regular serif text inside the
math expression. If another renderer is used, it must still produce line numbers,
page numbers, clear section hierarchy, readable inline and displayed math, and
embedded or declared fonts.

Figures and tables should remain separate from the line-numbered `manuscript.pdf`.
For normal serious-pilot and full-research runs, build a second journal-style
artifact at `article/article.pdf` for every revision; do not replace the review
manuscript and do not remove the separate figure/table folders. Compact demos or
internal smoke tests may set `require_integrated_article_pdf: false`, but the
contract and final decision must state the downgrade explicitly.

## Integrated Article PDF

When `require_integrated_article_pdf: true`, every revision folder must include:

```text
article/
  article.md
  article.pdf
  article_build_report.json
```

Build it with the PLOS-like integrated article builder:

```bash
python tools/build_article_pdf.py <revision-dir> --conda-env ag
```

The builder must use Pandoc/XeLaTeX, the same render toolchain checked by
`tools/check_render_toolchain.py`, and the bundled Inter text font with
LaTeX-style serif math. The upper-right running header must show the publication
type, such as `Article`, `Review`, or `Editorial`, rather than the internal
artifact label. The title block must show the author, publication type,
and publication date; the footer must show journal label, volume, and journal
date. The abstract should appear as a distinct emphasized
block before the main text begins. The title block must begin with the Research
Arena `Delta E / Evidence Gain` logo masthead, and `article_build_report.json`
must declare `brand_logo: research_arena_logo_evidence_gain`.

It should integrate manuscript text, reasonably sized figures, and reasonably
sized tables into `article.pdf`; oversized tables or unsupported display formats
should be listed in `article_build_report.json` as supplemental or omitted,
while the original files remain separately inspectable. Each included figure and
table should show a bold title line followed immediately by the short explanation
from `display_item_explanations.md`.

## Human-Readable Output Package

Every revision should be copied into a human-readable output folder before
acceptance so the revision trajectory remains readable:

```text
human_readable_outputs/<run-id>/<submission-id>/<revision-id>/
  README.md
  manuscript.pdf
  article.pdf              # required unless the run contract explicitly opts out
  figures/
  tables/
  article/                 # article.md and article_build_report.json
  source_code/
  human_readable_package_manifest.json
```

The manuscript PDF in this folder is the line-numbered review manuscript.
`article.pdf` is the integrated journal-style article artifact unless the run is
explicitly a compact/demo/internal output. Figures and tables remain separate
folders so readers can inspect display items directly.
Source code must include the executable analysis source, usually
`source_code/analysis.py`.
Build or refresh the package with:

```bash
python tools/package_human_readable_outputs.py --run-id <run-id> --replace
```

Use `--latest-only` only for explicitly scoped internal checks. The full revision
folder remains the source of truth for issue ledgers, compute logs, verification
matrices, and review artifacts.

Each latest revision must also include `manuscript_style_manifest.md` with:

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
known_style_limits: <none or explicit limitations>
```

Use `agents/templates/manuscript_style_manifest.md` as the default template.

## Required Submission Artifact

Each latest revision must include `presentation_checklist.md` with:

```text
status: pass
manuscript_word_count: <integer>
methods_word_count: <integer>
display_item_count: <integer>
pdf_visual_check: <pass | fail>
figure_label_check: <pass | fail>
figure_text_size_normalization_check: <pass | fail>
figure_mark_scale_check: <pass | fail>
table_readability_check: <pass | fail>
display_item_explanation_check: <pass | fail>
display_item_narrative_check: <pass | fail | not_required>
display_item_plan_check: <pass | fail | not_required>
raw_label_translation_check: <pass | fail>
math_or_method_detail_check: <pass | fail>
line_number_check: <pass | fail>
equation_numbering_check: <pass | fail>
math_rendering_check: <pass | fail>
inline_math_rendering_check: <pass | fail>
human_readable_output_check: <pass | fail>
manuscript_typography_check: <pass | fail>
figure_typography_check: <pass | fail>
render_toolchain_check: <pass | fail | waived>
article_pdf_check: <pass | fail | not_required only when contract explicitly opts out>
known_presentation_limits: <none or explicit limitations>
```

Use `agents/templates/presentation_checklist.md` as the default template.

The Researcher may draft the checklist, but the owning Referees, Integrity
Checker, and Editor must verify it before acceptance. A self-declared pass is not
enough to publish.
