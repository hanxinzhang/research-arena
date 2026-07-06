# Display Program Independence Rubric

Use this rubric for an LLM-backed judgment when a run has multiple Researchers,
when display programs look similar across submissions, or when a Referee,
Integrity Checker, or Editor raises concern that the figure/table sequence is
template-driven. This is not a deterministic filename or AST-similarity test. It
is a scientific and process judgment about whether the displays were chosen from
each Researcher's own question and evidence.

## Inputs To Read

- each relevant `display_item_plan.md`;
- each relevant `display_item_explanations.md`;
- the latest and prior `manuscript.md`, `article/article.md`, and rendered PDFs
  when present;
- figure and table artifact filenames, titles, captions, grouping decisions, and
  visual content;
- plotting sections of each `analysis.py`, especially functions that create
  figures or tables;
- `research_dossier.md`, `analysis_plan.md`, `results.json`, `stable_results.json`
  when available, `revision_plan.md`, `material_research_delta.md`, and
  `revision_response.md`;
- `runs/<run-id>/agent_independence_plan.md`, `scripted_generation_audit.json`,
  and relevant Referee, Integrity Checker, or Editor comments;
- `agents/templates/figure_style.py` and any copied style helper used by the
  submission.

## Judgment Questions

1. Are the display concepts claim-led, evidence-led, and specific to the
   Researcher's study, or do they look like a generic framework checklist?
2. Does `display_item_plan.md` explain why each display exists, what alternative
   forms were considered, and what claim role the item has?
3. Are similarities across Researchers limited to shared style helpers, field
   conventions, or necessary replication, or do they include the same figure
   sequence, filenames, titles, plot grammar, and `write_figures()` structure?
4. If different research questions produced the same display sequence, is there a
   scientific reason in the research record, or only a process convenience?
5. Did revisions materially change the display program when the evidence,
   reviewer issues, or manuscript claims changed?
6. Are the displays selected because the manuscript needs them, not because the
   contract asks for a minimum number of display items?
7. Does the use of `figure_style.py` stay inside typography, human-readable label,
   and saving utilities rather than becoming a shared figure-concept template?
8. Are any replicated figure forms explicitly justified as robustness checks,
   benchmark conventions, or direct answers to an issue?

## Required Output

```json
{
  "judgment_type": "display_program_independence",
  "status": "independent | partly_template_driven | overconverged | cannot_judge",
  "shared_style_only": false,
  "fixed_figure_program_detected": false,
  "researcher_specific_display_logic": "strong | adequate | weak | absent",
  "overlapping_display_concepts": [
    {
      "researchers_or_submissions": [],
      "items": [],
      "overlap_kind": "style_only | standard_field_convention | replicated_with_rationale | template_like_sequence | copied_plot_code | unclear",
      "judgment": "<why the overlap is acceptable, concerning, or blocking>"
    }
  ],
  "display_plan_findings": [
    {
      "submission": "<submission id>",
      "status": "pass | revise | missing | cannot_judge",
      "finding": "<claim-led display logic, weakness, or missing evidence>"
    }
  ],
  "style_helper_boundary": "<assessment of whether figure_style.py or similar helpers stayed within visual styling>",
  "required_next_action": "continue | revise_display_plan | request_researcher_specific_figures | accept_style_similarity | downgrade_process_confidence | reject_or_downgrade",
  "confidence": 0.0,
  "evidence_paths": []
}
```

## Decision Guidance

- `independent`: overlap is limited to shared style, standard field convention, or
  well-justified replication, and each Researcher has claim-specific display
  logic.
- `partly_template_driven`: some figures or code structure look inherited from a
  template, but the issue is fixable by revising the display plan and adding or
  changing displays tied to each study's evidence.
- `overconverged`: multiple Researchers share a figure sequence, filenames,
  titles, or plotting structure without a study-specific reason. Treat this as a
  process-risk blocker for acceptance unless the Editor documents an explicit
  downgrade or override.
- `cannot_judge`: required plans, artifacts, or plotting code are missing.
