# Agents

Each agent is a folder with three files:

- `config.json`
- `profile.md`
- `rules.md`

The default community includes:

- `researcher_1`
- `researcher_2`
- `study_design_board`: pre-analysis proposal gate and research mentor
- `integrity_checker`
- `referee_1`: machine-learning methods and statistics
- `referee_2`: domain and scientific interpretation
- `referee_3`: reproducibility and software artifacts
- `referee_4`: novelty, literature, and field advancement
- `editor_publisher`

To add more Researchers or Referees:

1. Copy `agents/templates/researcher/` to `agents/researcher_3/`, or copy
   `agents/templates/referee/` to `agents/referee_5/`.
2. Replace `researcher_N` or `referee_N` in `config.json` with the new folder name.
3. Edit `profile.md` and `rules.md` so the new agent has a distinct perspective.
4. Keep the non-deterministic interaction rule, structured review schema, issue
   ledger requirements, citation/originality rules, and safety expectations.
5. Name the new agent in the run prompt.

The LLM agent should include all explicitly named Researchers and Referees in the
run. Researchers compete using the same shared dataset and governance rules.
Referees review all Researcher submissions unless the user specifies a different
assignment.

## Shared Review Contract

Every Referee must:

- read the actual current artifacts before reviewing;
- create or update only that Referee's owned issue IDs for every actionable
  request, such as `R1-*` for `referee_1`;
- specify severity, required evidence, and acceptance criteria;
- cite the triggering artifact path and exact missing evidence for every major or
  blocking concern;
- include `what_changed_since_previous_revision`;
- ask direct questions when explanation is needed, and later assess whether the
  Researcher answered them;
- verify Researcher evidence in the verification matrix before marking issues
  resolved;
- avoid recommendations driven by round number, scripted thresholds, or generic
  praise;
- avoid templated review text that duplicates other Referees without a distinct
  specialty-specific rationale.

Every Researcher must:

- work in an independent `agents/<researcher-id>/workspace/<run-id>/` folder before
  the first submission;
- complete Phase 0 data familiarization and pilot artifacts before candidate
  generation: `proposal_gate/data_familiarization.md`,
  `proposal_gate/pilot_study_plan.md`, `proposal_gate/pilot_study_results.json`,
  `proposal_gate/pilot_compute_log.csv` or `.json`, and
  `proposal_gate/pilot_lessons.md`;
- create `proposal_gate/candidate_studies.md`,
  `proposal_gate/selected_proposal.md`, and
  `proposal_gate/compute_budget_estimate.md` with measured component arithmetic
  before analysis;
- wait for `study_design_board` approval or an explicitly accepted article-type
  downgrade before writing `analysis.py`, fitting models, writing results, or
  drafting a manuscript;
- include a first-submission research dossier, EDA report, method cards,
  experiment registry, compute log, and standalone `analysis.py` in `revision_00/`;
- declare shared utilities and avoid thin wrappers around a hidden central
  generator for publication claims;
- when orchestration is needed, use explicit prompt packets under
  `work_packets/<run-id>/` as role inputs; packets must not prewrite scientific
  conclusions, reviews, integrity findings, or editorial decisions;
- add analyses, tables, figures, citations, and manuscript changes only in response
  to open issues, direct reviewer questions, integrity findings, or editor
  instructions;
- include `presentation_checklist.md` in each revision, satisfy the run-level
  `manuscript_quality_contract.md`, include `display_item_plan.md`, include
  `display_item_explanations.md`, and include `manuscript_style_manifest.md` when
  the contract requires it;
- build `article/article.pdf` for every revision in serious-pilot and
  full-research runs unless the contract explicitly opts out for a
  compact/demo/internal run;
- render manuscripts with clear sections/subsections, line numbers, numbered and
  visibly rendered LaTeX display equations, rendered inline math spans, bundled
  Inter-first open-source sans-serif typography for manuscript text and figures,
  LaTeX-like serif math, and a passing `render_toolchain_report.json` when the manuscript-quality
  contract requires the publication renderer;
- create a human-readable package under
  `human_readable_outputs/<run-id>/<submission>/<revision>/` with
  `manuscript.pdf`, `article.pdf`, `figures/`, `tables/`, `source_code/`,
  `README.md`, and a package manifest before editorial acceptance;
- style figure labels, legends, ticks, panel marks, and annotations so they are
  human-readable in exported PDF artifacts. SVG is optional. Shared style helpers
  such as `agents/templates/figure_style.py` are allowed for typography and label
  translation, but they must not become shared figure-concept or `write_figures()`
  templates;
- include a manuscript figure/table guide that explains each display item's
  purpose, axes or rows/columns, labels, legends, annotations, summary conclusion,
  and caveat, with raw internal labels translated into human-readable text;
- maintain `verification_matrix.csv` or `verification_matrix.json` alongside the
  issue ledger;
- answer each direct reviewer question in `revision_response.md`;
- write `revision_plan.md` before creating any revision after `revision_00/` and
  map open issue IDs to planned evidence, compute, verification criteria,
  `revision_type`, `research_delta_tier`, empirical provenance status,
  `material_research_delta.md` expectations, and stop/downgrade criteria;
- include `material_research_delta.md` for `tier_a_material` and
  `tier_b_supporting` revisions, and explicitly leave central empirical, novelty,
  or article-fit blockers unresolved when a revision is `tier_c_nonmaterial`;
- include `compute_reconciliation.md` or `.json` when actual compute is below
  target or materially different from the proposal estimate;
- include `empirical_provenance.json` in every revision after `revision_00/`;
- revise manuscript claims, limitations, interpretation, novelty, or methods when
  the evidence changes, rather than only listing newly added artifacts.

The Editor and Integrity Checker should use deterministic clerk tools or equivalent
manual fact collection before final acceptance:
`tools/review_similarity_audit.py`, `tools/research_depth_audit.py`,
`tools/trajectory_clerk.py` for multi-revision runs,
`tools/artifact_authority_audit.py`, `tools/run_state_audit.py`,
`tools/archive_hygiene_audit.py`, and
`tools/scripted_generation_audit.py`. These clerks report evidence about text
similarity, artifact presence, presentation checks, independence, compute records,
revision deltas, author/path authority, final-decision order, archive hygiene, and
central-generation risk. They do not decide scientific depth, novelty,
article-type fit, reviewer quality, display-program independence, or acceptance.
Those judgments require agent reasoning using the rubrics under `audits/`.
Unresolved proposal-gate,
structural-depth, presentation-gate, independence, high-similarity, stagnant
revision-trajectory, artifact-authority, state-order, scripted-generation, freeze,
or missing-judgment evidence blocks publication. The Editor must create and cite
`runs/<run-id>/pre_decision_freeze_manifest.json` immediately before final
decision, then create and verify `runs/<run-id>/post_decision_archive_manifest.json`
after the final event-log entry.

## Study Design Board

The `study_design_board` is a pre-analysis agent. It reviews proposed studies before
Researchers spend meaningful compute. For each Researcher, it should inspect:

- multiple candidate studies;
- the selected proposal;
- article-type fit;
- novelty and prior-work gap;
- baseline and validation plan;
- compute-budget realism;
- manuscript-quality and presentation-gate realism;
- safety and data-governance constraints.

Its decision must be one of `approve_for_analysis`, `revise_before_analysis`,
`downgrade_article_type`, or `stop_before_analysis`. The decision is written to the
Study Design Board workspace and summarized in `runs/<run-id>/proposal_gate_summary.md`.
