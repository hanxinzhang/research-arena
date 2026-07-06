# Revision Trajectory Rubric

Use this rubric to judge whether revisions changed the scientific state. Use
`tools/trajectory_clerk.py` if available, but do not let the clerk output decide
the judgment by itself.

## Inputs To Read

- all revision folders for each submission;
- `revision_plan.md`, `revision_response.md`, issue ledgers, and verification
  matrices for each revision;
- `material_research_delta.md` for material or supporting revisions, and any
  explicit explanation for nonmaterial revisions;
- referee and integrity reports before and after each revision;
- trajectory clerk output, if available;
- final or current editor decision.

## Judgment Questions

1. What changed between revisions: code, data, model, metrics, figures, tables,
   manuscript interpretation, claims, or only packaging?
2. Did the changes address the open issues that motivated the revision?
3. Were new experiments or analyses performed when empirical issues required them?
4. Did reviewers ask new actionable questions, verify evidence, or merely repeat a
   recommendation?
5. Did the revision loop stop, downgrade, or reject when the needed evidence was
   infeasible?
6. Are there two or more consecutive revisions with no scientific-state change
   while central issues remain open?
7. Did any revision start before the prior Integrity Checker and Referee reviews
   were present in the event log?
8. Did `analysis.py` change only through a revision-number marker while new outputs
   appeared?
9. Did primary metrics remain unchanged while the revision claimed empirical
   progress?
10. Did compute effort materially increase when central empirical issues required
   new evidence?
11. Did the declared `research_delta_tier` match the actual artifact changes?
12. Did material or supporting revisions record failed, null, or abandoned
   experiments instead of hiding them?
13. Did nonmaterial revisions explicitly leave central empirical, novelty, or
   article-fit blockers unresolved unless a downgrade or rejection was approved?

## Required Output

```json
{
  "judgment_type": "revision_trajectory",
  "status": "productive | stagnant | mixed | cannot_judge",
  "scientific_state_changed": true,
  "empirical_evidence_added": true,
  "packaging_only_revisions": [],
  "process_order_warnings": [],
  "revision_marker_only_revisions": [],
  "unchanged_primary_metric_revisions": [],
  "compute_budget_concerns": [],
  "research_delta_tier_concerns": [],
  "material_research_delta_paths": [],
  "unanswered_central_issues": [],
  "reviewer_interaction_quality": "strong | adequate | weak | templated",
  "recommended_next_state": "continue | revise_plan | downgrade_article_type | reject | accept_possible",
  "confidence": 0.0,
  "evidence_paths": []
}
```

A polished folder sequence is not a productive trajectory unless the scientific
state or the justified article type actually changes.
