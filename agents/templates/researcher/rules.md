# Researcher Rules

Use `agents/researcher_1/rules.md` as the base rule contract.

When creating a new Researcher, keep:

1. the non-deterministic interaction rule;
2. the pre-results analysis plan requirement;
3. the pre-analysis proposal gate requirement, including multiple candidate studies,
   a selected proposal, and Study Design Board approval before implementation;
4. the Phase 0 data-familiarization and pilot requirement before candidate studies:
   `data_familiarization.md`, `pilot_study_plan.md`, `pilot_study_results.json`,
   `pilot_compute_log.csv` or `.json`, `pilot_lessons.md`, and a pilot-grounded
   `compute_budget_estimate.md` with measured component arithmetic, timing probes
   for large components, and an explicit strengthen/downgrade/budget-revision
   choice when expected compute falls below a full Article/Analysis target;
5. the first-submission research dossier requirement;
6. the compute budget, experiment registry, and compute log requirements,
   including enough detail to audit `minimum_cpu_core_hours_per_researcher`,
   `target_cpu_core_hours_per_researcher`, and
   `minimum_experiment_rows_per_researcher`;
7. the independent workspace and standalone submission-code requirements;
8. the data-agnostic rigor-matching requirements;
9. the empirical-program requirements;
10. issue-ledger and evidence-linked revision responses;
11. integrity, citation, originality, artifact, and safety rules;
12. the rule that no revision may be generic or based only on round number;
13. an `activity_log.md` in the independent workspace, with ideas tried, commands
   run, failed or abandoned experiments, and decision rationale;
14. a `revision_plan.md` gate before `revision_01/` or any later revision, with
    open issues, proposed evidence, expected artifacts, compute needs, and
   stop/downgrade criteria, including parseable `revision_type` and
   `research_delta_tier`;
15. the rule that empirical blockers require empirical evidence, credible
    substitutes, article-type downgrade, or rejection rather than packaging-only
    revisions;
16. the `material_research_delta.md` requirement for `tier_a_material` and
    `tier_b_supporting` revisions, plus the requirement that
    `tier_c_nonmaterial` revisions explicitly say which central issues remain
    unresolved;
17. the issue-driven artifact rule: every new analysis, table, figure, citation
    update, or manuscript change must map to an open issue, reviewer question,
    integrity finding, or editor instruction;
18. the verification-matrix requirement;
19. `empirical_provenance.json` for every revision after `revision_00/`, and
    `compute_reconciliation.md` or `.json` whenever actual compute is below target
    or materially different from the proposal estimate;
20. the requirement that final manuscripts revise claims, limitations,
    interpretation, novelty, or methods, not only list new artifacts;
21. the article-voice boundary: `revision_response.md` answers Referees,
    Integrity Checker, and Editor questions, while `manuscript.md` must read as a
    standalone final article rather than a memo about what a revision added or how
    reviewer issues were answered;
22. the hard manuscript-quality contract and `presentation_checklist.md`
   requirement, including line-numbered readable manuscript PDFs, organized section
   and subsection hierarchy, numbered and visibly rendered LaTeX display
   equations, rendered inline math spans, bundled Inter-first open-source
   sans-serif typography for manuscript text, LaTeX-like serif math, a
   run-level rendering toolchain report when required, a human-readable output
   package, human-readable figure/table labels, manuscript figure/table
   explanations, raw-label translation, and formal method/model detail when
   relevant; for serious-pilot and full-research runs, build an integrated
   `article/article.pdf` in every revision as a second journal-style artifact
   without replacing `manuscript.pdf` or deleting standalone figures/tables,
   unless the contract explicitly opts out for a compact/demo/internal run;
23. the `display_item_plan.md` requirement for latest revisions with main-text
   display items, including a claim-led display strategy, alternatives considered,
   claim role for each item, shared style helper boundary, and similarity-risk
   rationale when figure concepts, filenames, ordering, or plotting structure
   resemble another Researcher, a prior revision, or a framework example;
24. the `display_item_explanations.md` requirement when the run contract requires
   it, including one entry per figure and table with artifact path, manuscript
   discussion location, title-adjacent article explanation,
   label/legend/annotation explanation, raw-label translation, summary conclusion,
   and caveat;
25. the `manuscript_style_manifest.md` requirement when the run contract requires
   it, including manuscript font, figure font, equation numbering, math-rendering
   status, PDF renderer, render-toolchain report, visual PDF review, and known
   style limits.

Change only the research style, preferred analysis families, and creative emphasis
so the new Researcher contributes a distinct perspective.
