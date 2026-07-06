# Reviewer Quality Rubric

Use this rubric for an LLM-backed audit of referee and integrity-review behavior.
The text-similarity clerk may identify near-duplicates, but this rubric judges
whether reviews were scientifically useful.

## Inputs To Read

- all referee reviews and integrity reports;
- issue ledgers and verification matrices;
- revision responses and revision plans;
- review-similarity clerk output, if available.

## Judgment Questions

1. Did each reviewer read and cite concrete artifacts?
2. Did each major issue state required evidence and acceptance criteria?
3. Did reviewers ask direct questions when explanation was needed?
4. Did reviewers inspect figure/table readability, manuscript display-item
   explanations, title-adjacent article-PDF display-item narratives, and raw-label
   translations instead of accepting checklist claims?
5. Did reviewers notice when manuscript prose read like a revision response,
   changelog, or audit memo instead of a standalone article?
6. Did follow-up reviews verify cited evidence before marking issues resolved?
7. Did reviewer recommendations evolve because artifacts changed?
8. Did reviewers avoid owning, resolving, or summarizing another reviewer's issues?
9. Did reviews force useful research decisions, or only produce procedural prose?

## Required Output

```json
{
  "judgment_type": "reviewer_quality",
  "status": "strong | adequate | weak | templated | cannot_judge",
  "useful_reviews": [],
  "weak_reviews": [],
  "missing_questions_or_criteria": [],
  "issue_ownership_problems": [],
  "recommended_next_state": "continue | require_review_rewrite | downgrade_article_type | reject | accept_possible",
  "confidence": 0.0,
  "evidence_paths": []
}
```

Reviews can be textually distinct and still be scientifically weak. Judge whether
they changed the research process.
