# Display Item Grouping Review Rubric

Use this rubric for `runs/<run-id>/display_item_grouping_review.md` when an
integrated article contains multiple figure artifacts or when a reviewer questions
whether related figures should be combined as panels.

This is an LLM/editor judgment rubric, not a filename rule. Do not infer grouping
from file order alone. Judge the evidence, article flow, and reader burden.

## Inputs

- `display_item_explanations.md`
- `article/article_build_report.json`
- `article/article.pdf`
- standalone files under `figures/`
- manuscript Results and Figure/Table Guide sections
- referee comments about figure/table presentation

## Required Review Fields

1. `status`: `pass`, `revise`, or `fail`.
2. `grouping_decision_summary`: each figure, its declared `Article group`, panel
   label if any, and whether the decision is editorially coherent.
3. `missed_grouping_opportunities`: related figures that should likely be combined,
   with a short reason grounded in the claims.
4. `over_grouping_risks`: panels that are too unrelated, too dense, or likely to
   obscure the claim.
5. `panel_readability`: whether panel labels, axis labels, legends, and text remain
   readable after article scaling.
6. `standalone_rationale_quality`: whether standalone figures have a substantive
   reason rather than a convenience rationale.
7. `required_changes`: issue-linked changes before acceptance.

## Pass Criteria

- Each figure has an explicit grouping or standalone judgment.
- Multi-panel figures combine genuinely related evidence.
- Standalone figures have a scientific or editorial rationale.
- Panel labels and panel-level titles are clear.
- The integrated article is more compact and readable than a sequence of loosely
  related single figures.
- The original standalone figure files remain inspectable.

## Failure Modes

- Figures are grouped only because filenames are adjacent.
- Related small figures are left standalone without a rationale.
- A group combines unrelated evidence and weakens the Results flow.
- Panel text becomes materially smaller than article text.
- `article.pdf` omits the title-adjacent explanation for the grouped figure.
