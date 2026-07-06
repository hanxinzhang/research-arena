# Novelty And Article-Fit Rubric

Use this rubric for an LLM-backed novelty and article-type judgment.

## Inputs To Read

- article-type contract and editor-gate plan;
- selected proposals, literature notes, manuscript introduction/discussion, and
  references;
- model/method cards, comparison tables, figures, and display-item explanations;
- reviewer 4 or novelty/literature reviews;
- scientific-depth and trajectory judgments when available.

## Judgment Questions

1. What is the claimed contribution?
2. Is the contribution new relative to cited literature, prior runs, or standard
   baselines?
3. Does the work provide field advancement, reusable evidence, a credible negative
   result, strong validation, or a methodological insight?
4. Do the figures and comparison tables communicate the contribution with
   human-readable labels, explained legends/annotations, and clear conclusions?
5. Is the article type too ambitious for the actual evidence?
6. Would a lower article type be more honest?
7. What exact evidence would change the novelty/article-fit judgment?

## Required Output

```json
{
  "judgment_type": "novelty_article_fit",
  "status": "fits_declared_article_type | downgrade_recommended | reject | cannot_judge",
  "claimed_contribution": "",
  "actual_contribution": "",
  "main_gap": "",
  "required_next_evidence": [],
  "recommended_article_type": "",
  "confidence": 0.0,
  "evidence_paths": []
}
```

Do not accept rhetorical novelty. The novelty claim must be grounded in submitted
evidence and checked literature.
