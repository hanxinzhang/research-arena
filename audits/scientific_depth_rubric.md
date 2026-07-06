# Scientific Depth Rubric

Use this rubric for an LLM-backed scientific-depth judgment. Deterministic clerk
outputs may be provided as evidence, but they do not decide the result.

## Inputs To Read

- run contracts, especially article type, research depth, compute, and editor gate;
- proposal gate artifacts and Study Design Board decisions;
- first-submission dossier, EDA, analysis plan, method cards, registry, compute log;
- current `analysis.py`, `results.json`, tables, figures, manuscript,
  `display_item_explanations.md`, and checklist;
- issue ledger, verification matrix, integrity reports, and referee reviews;
- deterministic clerk outputs, if available.

## Judgment Questions

1. Does the empirical program match the declared article type and claim?
2. Is the first submission serious research rather than a manuscript-shaped demo?
3. Are baselines, ablations, uncertainty, robustness, negative controls, and error
   analysis adequate for this data modality and claim?
4. Are omissions justified, or are they hidden weaknesses?
5. Does the compute and experiment registry support the claimed depth?
6. Are null, weak, failed, or abandoned experiments visible?
7. Are central claims supported by actual results rather than prose?
8. Do figures and tables explain the evidence clearly enough that an expert can
   understand labels, legends, annotations, conclusions, and caveats without
   reverse-engineering the code?
9. Would another expert know what additional evidence is needed?

## Required Output

Return or write a structured judgment with:

```json
{
  "judgment_type": "scientific_depth",
  "status": "adequate | inadequate | mixed | cannot_judge",
  "article_type_fit": "adequate | too_shallow | overclaimed | downgrade_recommended",
  "central_strengths": [],
  "central_blockers": [],
  "required_next_evidence": [],
  "recommended_next_state": "continue | revise_plan | downgrade_article_type | reject | accept_possible",
  "confidence": 0.0,
  "evidence_paths": []
}
```

Do not mark `accept_possible` unless the evidence, not only artifact completeness,
supports the selected article type.
