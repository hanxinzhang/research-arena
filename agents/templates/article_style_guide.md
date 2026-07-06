# Integrated Article Style Guide

Use this guide for every revision in serious-pilot and full-research runs. Compact
demos or internal smoke tests may opt out only when
`manuscript_quality_contract.md` explicitly sets
`require_integrated_article_pdf: false`.

## Artifact Split

`manuscript.pdf` remains the line-numbered review manuscript. It may be text-only
and must keep figures and tables separately inspectable.

`article/article.pdf` is the integrated journal-style article. It should combine
the manuscript narrative, central figures, and reasonably sized tables into a
single polished PDF. It is a second artifact, not a replacement for
`manuscript.pdf`.

## Default Layout

The default style is PLOS-like:

1. single-column body;
2. compact research-article title block using the Research Arena `Delta E /
   Evidence Gain` logo masthead;
3. running header with journal name on the left and publication type on the
   right, such as `Article`, `Review`, or `Editorial`;
4. author/date metadata beneath the title;
5. footer with journal, volume, and journal date;
6. emphasized abstract block before the main text begins;
7. clean header and footer;
8. integrated figures with full captions;
9. compact `booktabs` tables;
10. Inter for article text, the logo masthead, and other sans-serif article UI;
11. LaTeX-style serif math for equations.

The logo masthead must use open-source fonts only. Prefer the bundled Inter
family from `assets/fonts/inter/`; acceptable open-source fallbacks are Source
Sans 3, Noto Sans, and Liberation Sans.

Use the PLOS-like layout first because it is robust for arbitrary Research Arena
outputs. A denser Nature-like layout may be added later for accepted work that has
stable, manually curated display items.

## Build Command

```bash
python tools/build_article_pdf.py <revision-dir> --conda-env ag
```

Publication metadata can be set explicitly:

```bash
python tools/build_article_pdf.py <revision-dir> --conda-env ag \
  --publication-type Article \
  --author-name "Researcher 1" \
  --publication-date "July 5, 2026" \
  --journal-volume "Volume 1" \
  --journal-date "July 2026"
```

If `--author-name` is omitted, the builder infers a readable Researcher name
from the submission folder when possible. Use `--publication-type` for the real
publication category; do not use the internal artifact label `Integrated article`
as a running header.

The builder writes:

```text
article/
  article.md
  article.pdf
  article_build_report.json
```

Use `--replace` only to rebuild an existing generated `article/` folder.

## Fit Rules

Include in the main `article.pdf`:

1. manuscript sections from `manuscript.md`, except duplicate figure/table guide
   text that has become captions;
2. figures in `figures/` that are PDF, PNG, JPG, or JPEG;
3. tables in `tables/` that have at most 35 data rows and 8 columns.

Route to supplemental/omitted status in `article_build_report.json`:

1. oversized tables;
2. unsupported display formats;
3. display items that would become unreadable after scaling.

Never delete or move the original figure/table artifacts. The separate folders
remain the source for inspection and audit.

## Figure Normalization

Figures should be built for the article size rather than treated as large slides
that are shrunk after the fact. Use
`agents/templates/figure_style.py` before plotting. Its default contract is:

1. all in-figure text uses one shared size near the article body text, including
   titles, subtitles, axis labels, tick labels, legends, annotations, panel labels,
   and colorbar labels;
2. lines, bars, dots, boxplots, error bars, grid lines, and axes spines are scaled
   for that same final size;
3. source figures are exported as vector PDF with bundled Inter or an approved
   open-source sans-serif fallback;
4. related figures may be grouped into panels only when the article-effective text
   size remains readable.

Run the figure presentation audit before final article acceptance:

```bash
python tools/figure_presentation_audit.py <revision-dir> --write
```

The audit checks source PDF text-size consistency, obvious manual font-size
overrides in submitted analysis code, and article-effective figure text size from
`article/article_build_report.json`.

## Verification

Before treating `article.pdf` as passing, run:

1. Pandoc/XeLaTeX build through `tools/build_article_pdf.py`;
2. `qpdf --check` on the output;
3. `pdftotext` raw-markup scan for unrendered LaTeX or Markdown delimiters;
4. `pdffonts` to confirm embedded text/math fonts;
5. Poppler PNG rendering and visual inspection of at least the first page and
   each page containing a figure or table.
6. `tools/figure_presentation_audit.py` when figures are included in the article.

Set `article_pdf_check: pass` in `presentation_checklist.md` only after the
integrated PDF is visually readable, `article_build_report.json` declares
`status: pass`, and figure typography/scale checks pass or have explicit,
reviewer-accepted limitations.
