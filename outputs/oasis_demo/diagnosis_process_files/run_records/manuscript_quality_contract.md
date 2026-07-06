# Manuscript Quality Contract

Selected article type: compact demo article.

minimum_manuscript_words: 1200
minimum_methods_words: 250
minimum_display_items: 4
minimum_subsection_count: 6
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

Each latest revision must include `manuscript.md`, `manuscript.pdf`,
`manuscript_style_manifest.md`, `display_item_explanations.md`,
`presentation_checklist.md`, standalone PDF figures, readable tables, and
`article/article.pdf`.

Manuscripts must read as final article prose rather than reviewer
response memos. Math must render as LaTeX-like serif math. Manuscript and
figure text must use bundled Inter or an approved open-source sans-serif
fallback. Article figure text and marks must be normalized to the final
article scale and pass `tools/figure_presentation_audit.py`.
