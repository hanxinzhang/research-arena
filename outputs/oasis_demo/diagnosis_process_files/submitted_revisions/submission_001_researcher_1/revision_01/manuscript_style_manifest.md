# Manuscript Style Manifest

line_numbers: true
manuscript_font_family: Inter (bundled open-source font)
figure_font_family: Inter (bundled open-source font)
math_font_family: LaTeX-like serif math (standard XeLaTeX math)
numbered_equations: true
math_rendering_check: pass
inline_math_rendering_check: pass
pdf_renderer: pandoc-xelatex
render_toolchain_report: runs/oasis_demo/render_toolchain_report.json
visual_pdf_review: pass
figure_typography_review: pass
figure_presentation_audit: submissions/oasis_demo/submission_001_researcher_1/revision_01/figure_presentation_audit.json
known_style_limits: none

## Evidence

- Manuscript PDF: `submissions/oasis_demo/submission_001_researcher_1/revision_01/manuscript.pdf`
- Manuscript source: `submissions/oasis_demo/submission_001_researcher_1/revision_01/manuscript.md`
- Figure artifacts checked: `submissions/oasis_demo/submission_001_researcher_1/revision_01/figures/`
- Figure presentation audit: `submissions/oasis_demo/submission_001_researcher_1/revision_01/figure_presentation_audit.json`
- Renderer command or method: `python agents/templates/render_manuscript_pdf.py <source> <output> --engine pandoc-xelatex --conda-env ag`
- Rendering toolchain report: `runs/oasis_demo/render_toolchain_report.json`
- Font fallback, if any: none
- Bundled font evidence: `assets/fonts/inter/Inter-Regular.ttf`
- Math rendering evidence: `manuscript_render_report.json` and visual PDF inspection confirm inline and displayed LaTeX-like serif math.
