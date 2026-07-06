# Presentation Checklist

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

## Evidence Paths

- Manuscript source: `<path/to/manuscript.md or manuscript.tex>`
- Manuscript PDF: `<path/to/manuscript.pdf>`
- Style manifest: `<path/to/manuscript_style_manifest.md>`
- Display item plan: `<path/to/display_item_plan.md>`
- Display item explanations: `<path/to/display_item_explanations.md>`
- Figure folder: `<path/to/figures/>`
- Table folder: `<path/to/tables/>`
- Results file: `<path/to/results.json>`
- Rendering toolchain report: `runs/<run-id>/render_toolchain_report.json`
- Figure presentation audit: `<path/to/figure_presentation_audit.json or not required>`
- Integrated article PDF: `<path/to/article/article.pdf or explicit compact/demo opt-out>`
- Integrated article build report: `<path/to/article/article_build_report.json or explicit compact/demo opt-out>`
- Human-readable output folder: `human_readable_outputs/<run-id>/<submission-id>/<revision-id>/`

## Reviewer Notes

Explain any failed or borderline item. A Researcher-authored `status: pass` is a
claim for Referees, the Integrity Checker, and the Editor to verify, not an
acceptance decision.
