# Display Item Narrative Rubric

Use this rubric for an LLM-backed audit of figure and table explanations in the
manuscript and integrated `article/article.pdf`. This is a judgment rubric, not a
deterministic caption-length or keyword scan.

This rubric judges whether display items are explained well. It does not judge
whether multiple Researchers independently chose their display programs. When
figure/table sequences, filenames, titles, or plotting structures look
overconverged, use `audits/display_program_independence_rubric.md`.

## Inputs To Read

- the latest `manuscript.md`, `manuscript.pdf`, and `article/article.pdf` when
  present;
- `display_item_explanations.md`;
- all included figures and tables under `figures/` and `tables/`;
- `article/article.md` and `article/article_build_report.json` when present;
- relevant Referee, Integrity Checker, and Editor comments about presentation or
  display items.

## Judgment Questions

1. Does every main-text figure and table have a short, article-style explanation
   directly paired with its title in the manuscript or integrated article?
2. Does the explanation state the substantive pattern, contrast, denominator,
   uncertainty, model behavior, or limitation, rather than merely naming the file,
   addressing the reader, or repeating an internal artifact label?
3. Is the explanation concise enough to function like a journal caption dek, while
   still giving orientation for panels, axes, rows, columns, units, denominators,
   and abbreviations when needed?
4. Does the prose sound like normal article writing rather than instructional
   narration? It should not explain what the display item does for the reader or
   tell the reader how to inspect the artifact.
5. Are raw variables, model names, feature slugs, and abbreviations translated for
   human readers in the figure/table text or the adjacent explanation?
6. Do the figure/table explanation paragraphs state the supported takeaway without
   overclaiming beyond the submitted analysis?
7. Are caveats or denominator warnings included where omission would make the
   display item misleading?
8. Does `article/article.pdf`, when present, visibly preserve the title plus
   explanatory paragraph layout for every included display item?

## Required Output

```json
{
  "judgment_type": "display_item_narrative",
  "status": "pass | revise | reject | cannot_judge",
  "display_item_summary": "<one paragraph>",
  "item_findings": [
    {
      "item": "<figure/table label or artifact path>",
      "status": "pass | revise | missing | overclaimed | cannot_judge",
      "problem": "<what a reader would not understand>",
      "rewrite_direction": "<how to improve the title-adjacent explanation>"
    }
  ],
  "article_pdf_layout_assessment": "<brief assessment when article.pdf exists>",
  "recommended_next_state": "accept_possible | revise_display_items | require_visual_review | reject",
  "confidence": 0.0,
  "evidence_paths": []
}
```

## Decision Guidance

- `pass`: display-item titles and explanations are understandable, concise, and
  visibly paired in the article artifact when present.
- `revise`: one or more items need clearer, more article-like title-adjacent
  explanation, but the issue is fixable without new analysis.
- `reject`: display items are central to the manuscript but mostly unexplained,
  misleading, or artifact-like rather than publishable.
- `cannot_judge`: required display-item artifacts or rendered article outputs are
  missing.
