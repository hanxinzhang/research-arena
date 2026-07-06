# Research Arena Program

Research Arena is a prompt-run research community. The protocol is executed by
starting a file-aware LLM agent in this repository and asking it to follow these
rules.

There is no Python command that "runs the agents." The chosen LLM agent is the
runtime: it reads the rule files, plays the roles, creates artifacts, runs only the
local analysis code needed for a submission, and iterates through review and
revision.

## Core Principle

Each revision must be based on actual interactions between agents. Researcher
changes, Referee recommendations, Integrity Checker findings, and Editor decisions
must be grounded in submitted artifacts and issue-ledger status. No agent may use
round number, scripted thresholds, prewritten praise, or deterministic acceptance
logic as a substitute for review.

Revision artifacts must be issue-driven. A Researcher may add a table, figure,
analysis, control, citation update, or manuscript change only because an open issue,
reviewer question, integrity finding, or editor instruction requests it. Do not use
the revision number as a hidden schedule, such as "revision 2 always adds
calibration" or "revision 5 always adds a manifest."

## No Central Role Generator

Research Arena may use scripts to package files, compute hashes, rerun analyses,
compare text, and summarize objective facts. It must not use a central script,
notebook, or prompt template to generate the Researcher submissions, Referee
reviews, Integrity Checker reports, LLM-backed judgments, and Editor decisions as a
single deterministic batch.

Each role turn needs its own visible input context and output authority. A
Researcher may write only its own submission artifacts. A Referee may write only
its own review. The Integrity Checker may write integrity and rerun evidence. The
Study Design Board may write proposal-gate decisions. The Editor may write the
final decision. If a coordinator creates prompt packets, those packets are inputs
under `work_packets/<run-id>/`; they must not prewrite the role's conclusions.

After Referee review, any non-Researcher cleanup of submitted manuscripts, PDFs,
display-item plans, display-item explanations, package manifests, or presentation
checklists must
either trigger reviewer re-review or create a
`runs/<run-id>/non_scientific_change_record*.json|md` with before/after hashes,
the exact reason for the cleanup, and a declaration that scientific claims,
metrics, and empirical results did not change.

When automation is used, prefer `tools/create_work_packets.py` to create explicit
role inputs, then run the LLM-backed role turns separately. If a run contains a
script that writes artifacts for multiple scientific roles, the Integrity Checker
must treat it as central-generator risk until the script is inspected and the
Editor resolves the risk in writing.

## Research Depth Principle

Research Arena must evaluate evidence, not only artifact completeness. A run should
look less like a manuscript generator and more like a small research operating
system: Researchers propose several possible studies, a Study Design Board rejects
or sharpens weak designs before compute is spent, Researchers spend declared effort
exploring data and models, Referees audit the actual evidence, the Integrity Checker
reruns and inspects code, and the Editor defaults to no publication unless the
selected article type is genuinely satisfied.

The framework is data agnostic. It does not require one fixed model family, metric,
or data modality. It does require each run to declare a data/claim-specific rigor
contract before research begins and to enforce that contract consistently. The
contract should be appropriate to the dataset and claim, whether the data are
tabular, text, image, audio, signal, graph, simulation, multimodal, qualitative, or
another form.

## Deterministic Clerk, LLM Judge Boundary

Research Arena should use deterministic code as a clerk, not as the scientific
judge. Helper scripts may collect facts that are objectively checkable: artifact
existence, hashes, changed files, rerun status, metric equality, compute totals,
evidence-path validity, stale files, cache files, and legal state transitions.
Those scripts must not decide novelty, scientific depth, article-type adequacy, or
what experiment should be done next.

Scientific judgments belong to LLM-backed agents using explicit rubrics. The
Integrity Checker, Referees, Scientific Depth Auditor, and Editor may use
deterministic clerk outputs as evidence, but they must write their own reasoning
against the submitted artifacts. A structural pass from a script is never an
acceptance signal by itself.

Recommended clerk outputs are:

- `runs/<run-id>/research_depth_audit.json`: structural/presentation/independence
  facts only.
- `runs/<run-id>/review_similarity_audit.json`: text-similarity facts only.
- `runs/<run-id>/trajectory_clerk.json`: revision-to-revision artifact deltas,
  hashes, compute totals, and unresolved-issue signals only.
- `runs/<run-id>/artifact_authority_audit.json`: event-log author/path authority
  facts only.
- `runs/<run-id>/run_state_audit.json`: final-decision order, freeze citation,
  and self-certification facts only.
- `runs/<run-id>/scripted_generation_audit.json`: central scripted-generation
  process-risk facts only.
- `runs/<run-id>/archive_hygiene_audit.json`: transient-file archive hygiene facts
  only.
- `runs/<run-id>/pre_decision_freeze_manifest.json`: frozen evidence hashes
  immediately before the Editor writes a final decision.
- `runs/<run-id>/post_decision_archive_manifest.json`: complete post-decision
  archive hashes after the final decision and final event-log entry are written.

Recommended LLM judgment outputs are:

- `runs/<run-id>/scientific_depth_review.md` or `.json`.
- `runs/<run-id>/revision_trajectory_review.md` or `.json`.
- `runs/<run-id>/novelty_article_fit_review.md` or `.json`.
- `runs/<run-id>/reviewer_quality_review.md` or `.json`.
- `runs/<run-id>/manuscript_article_voice_review.md` or `.json` when manuscript
  prose risks reading like a revision response, changelog, or audit memo.
- `runs/<run-id>/display_item_narrative_review.md` or `.json` when figure/table
  explanations or integrated article display-item captions need article-style
  prose judgment.
- `runs/<run-id>/display_program_independence_review.md` or `.json` when multiple
  Researchers' figure/table programs appear similar or the boundary between
  shared visual style and shared display logic needs judgment.

The deterministic files provide the table of evidence. The LLM-backed reviews make
the research judgment.

## Event Log And Provenance

Each run should maintain an append-only event log at `runs/<run-id>/event_log.jsonl`.
Every agent action that changes a submission, review, audit, or decision should add
one JSON object with:

```json
{
  "time": "<ISO-8601 timestamp or explicit unknown>",
  "agent": "<agent id>",
  "role": "<orchestrator | researcher | study_design_board | integrity_checker | referee | editor | auditor>",
  "action": "<short verb phrase>",
  "input_artifacts": ["<paths read>"],
  "output_artifacts": ["<paths written>"],
  "decision": "<decision if any>",
  "reason": "<one or two sentence rationale>",
  "issue_ids": ["<issue ids touched>"]
}
```

The event log is not a substitute for reviews or manuscripts. Its purpose is to let
later auditors reconstruct the trajectory without inferring agent interactions from
final files alone.

The final editorial decision should be the last research-mutating event in the
run. Before writing `final_decision.md`, create
`runs/<run-id>/pre_decision_freeze_manifest.json` with
`python tools/freeze_run.py <run-id> --stage pre-decision`; the final decision
event must cite that manifest as an input. After the final decision and its event
log entry are written, create `runs/<run-id>/post_decision_archive_manifest.json`
with `python tools/freeze_run.py <run-id> --stage post-decision` and verify it.
If new research, review, audit, package, or work-packet artifacts are needed
afterward, the Editor must explicitly reopen the run and invalidate the stale final
decision before proceeding.

## Revision-Plan Gate

Before any `revision_01/` or later submission folder is created, the Researcher
must write a `revision_plan.md` in the current or proposed revision folder. The plan
must state:

1. open issue IDs and direct reviewer questions being addressed;
2. whether each issue needs new empirical evidence, manuscript-only clarification,
   additional provenance, or formal downgrade/rejection;
3. proposed actions and expected artifacts;
4. expected compute and analysis commands, if empirical work is proposed;
5. evidence that would convince the owning Referee, Integrity Checker, or Editor
   to change judgment, not only evidence that a file exists;
6. a parseable `research_delta_tier` field:
   `tier_a_material`, `tier_b_supporting`, or `tier_c_nonmaterial`;
7. a parseable `revision_type` field:
   `empirical_revision`, `interpretive_revision`, `packaging_revision`, or
   `mixed_revision`;
8. how `empirical_provenance.json` will declare whether `analysis.py`, results,
   compute logs, and stable scientific outputs are rerun, copied forward, or
   intentionally unchanged;
9. whether the revision will produce `material_research_delta.md`, what central
   claim may change, and which open central issues will remain unresolved even if
   the plan succeeds;
10. stop or downgrade criteria if the needed evidence is infeasible.

Use these research-delta tiers consistently:

- `tier_a_material`: new or changed study design, endpoint, data/split, method,
  benchmark program, leakage repair, external/generalization evidence, or other
  evidence that can plausibly change the central claim or article-type fit.
- `tier_b_supporting`: ablations, stronger baselines, paired uncertainty,
  calibration, subgroup/shift/robustness checks, negative controls, error
  taxonomy, sensitivity analysis, or other support that strengthens an existing
  claim without redesigning the study.
- `tier_c_nonmaterial`: prose, formatting, rerendering, provenance, packaging,
  verification matrices, copied-forward results, or claim-boundary clarification
  without new empirical support.

The owning Referee, Integrity Checker, or Editor should approve, revise, or reject
the plan before the Researcher spends more compute. If open central issues require
new empirical evidence and the plan proposes only packaging, prose, or repeated
verification, the correct next state is usually `revise_plan`, `downgrade_article_type`,
or `reject`, not another manuscript-shaped revision.
Central empirical, novelty, or article-fit blockers cannot be resolved by
`tier_c_nonmaterial`; they require `tier_a_material`, a strong and explicitly
adequate set of `tier_b_supporting` evidence, formal downgrade, or rejection.
For Serious Pilot and Full Research Attempt runs, reserve part of the empirical
budget for post-review challenge experiments so Researchers can answer central
reviewer issues with new evidence instead of only prose.

## Stop, Downgrade, Or Continue Rule

Research Arena should not create unlimited evidence-free revision rounds. If two
consecutive revisions do not change the scientific state while central issues
remain open, the Editor must choose one of:

1. request a new approved empirical revision plan;
2. formally downgrade the article type and update contracts;
3. reject the submission or reject all;
4. record an explicit override explaining why another non-empirical revision is
   scientifically necessary.

This rule should be judged by LLM-backed agents using the revision trajectory and
submitted artifacts. Deterministic scripts may summarize that the empirical
artifacts did not change, but they do not decide whether the change matters.

## Anti-Simulated-Trajectory Checks

When `tools/trajectory_clerk.py` is available, the Editor and Integrity Checker
should inspect its process-risk fields before continuing or accepting a run:

1. `prior_review_event_status`: later revisions should start only after the prior
   Integrity Checker and Referee reviews are present in the event log. A value such
   as `prior_review_after_revision_started` means the run recorded the revision
   before the review it claims to answer.
2. `analysis_change_kind`: a value of `revision_marker_only` means `analysis.py`
   changed only in a recognized revision-number marker after normalization. Treat
   this as staged artifact release unless the Researcher also provides a
   scientifically substantive change in design, data, model, evaluation, or
   interpretation.
3. `primary_metrics_change_kind`: a value of `unchanged` means the primary metric
   block in `stable_results.json` or `results.json` did not change from the prior
   revision. This is not automatically bad, but it cannot be cited as stronger
   empirical support without additional evidence.
4. `compute_delta_from_previous_cpu_core_hours`: if central empirical issues remain
   open and compute does not materially increase, the revision should normally
   stop, downgrade, or receive a new approved empirical plan rather than proceed as
   a manuscript-shaped revision.
5. `research_delta_tier`: a `tier_c_nonmaterial` revision can resolve
   claim-boundary, presentation, or provenance issues, but it must not resolve
   central empirical, novelty, or article-fit blockers unless the Editor formally
   downgrades or rejects. A `tier_a_material` or `tier_b_supporting` claim should
   be backed by `material_research_delta.md` and actual artifact changes.
6. `revision_type` and `empirical_provenance_status`: interpretive or packaging
   revisions can resolve claim-boundary, presentation, or provenance issues, but
   they must not be treated as new empirical support. Copied-forward results must
   be declared in `empirical_provenance.json`.

These checks are still clerk facts, not scientific judgments. Their purpose is to
force the LLM-backed trajectory review and final Editor decision to explain whether
researchers actually improved the research over revisions.

## Research Operating-System Contracts

Each run must include these contracts before final acceptance:

1. `article_type_contract.md`: selected article type, venue bar, required sections,
   required evidence, and publication threshold.
2. `study_design_contract.md`: proposal-gate rules, required candidate-study
   artifacts, Study Design Board decision schema, and the conditions under which a
   Researcher may begin analysis.
3. `research_depth_contract.md`: data modality, scientific question class, minimal
   first-submission dossier, expected rigor checks, and rejection criteria for
   shallow work.
4. `manuscript_quality_contract.md`: hard presentation gate, article-type-specific
   manuscript length/depth targets, required manuscript sections, figure/table
   readability requirements, and PDF quality rules.
5. `compute_budget.md` or `compute_budget.json`: intended wall-clock effort,
   CPU/GPU/backend assumptions, planned model/analysis families, minimum experiment
   count, and stopping criteria. Markdown budgets should use
   `agents/templates/compute_budget.md` and include parseable
   `minimum_cpu_core_hours_per_researcher`,
   `target_cpu_core_hours_per_researcher`, and
   `minimum_experiment_rows_per_researcher` fields so deterministic clerks can
   compare the latest artifacts with the declared evidence budget. The budget may
   be small for a demo, but it must be explicit and acceptance must respect it.
   If actual compute is below target or materially different from the proposal
   estimate, the active revision must include `compute_reconciliation.md` or
   `.json` with one of these parseable outcomes:
   `compute_target_met`,
   `compute_under_target_with_approved_efficiency_override`,
   `compute_under_target_requires_downgrade`, or
   `compute_under_target_blocks_acceptance`.
6. `agent_independence_plan.md`: participating Researchers, their isolated working
   folders, allowed shared resources, and what cannot be shared before initial
   submissions.
7. `editor_gate_plan.md`: acceptance gates, including proposal-gate approval, depth,
   presentation quality, independence, reproducibility, issue resolution, novelty,
   and article-type compliance.

If a run intentionally uses a compact demo contract, the Editor must label it as a
demo and must not accept it as a full research article.

## Phase 0 Data Familiarization And Pilot

Before the proposal gate, each Researcher must learn the user-provided dataset and
local compute resources through a small, bounded pilot. This phase is not a full
analysis and must not produce a manuscript, full `analysis.py`, `results.json`, or
article-level claims. Its purpose is to make the later proposal data-informed
rather than invented from the schema.

Each Researcher must create these `proposal_gate/` artifacts before writing
`candidate_studies.md`:

```text
data_familiarization.md
pilot_study_plan.md
pilot_study_results.json
pilot_compute_log.csv or pilot_compute_log.json
pilot_lessons.md
```

`data_familiarization.md` should describe file formats, row/sample counts,
variables, labels or outcomes, missingness, splits, modalities, governance
constraints, loading and memory observations, likely leakage or confounding paths,
and surprising dataset characteristics.

`pilot_study_plan.md` should define the small pilot question, subset size, timing
probes, resource measurements, baseline or preprocessing smoke tests, success
criteria, and limits on what the pilot can conclude.

`pilot_study_results.json` should record machine-readable pilot outputs, including
sample sizes, rough baseline metrics or descriptive results, failures, warnings,
and leakage or resource signals. `pilot_compute_log.csv` or `.json` should include
parseable timing and compute rows with wall seconds, backend, effective core count,
estimated CPU-core hours, optional GPU hours, commands or scripts used, and notes.

`pilot_lessons.md` must explain how the pilot changed the Researcher's proposed
direction, which ideas became infeasible, which leakage or data-quality risks were
found, which baselines look necessary, and what compute bottlenecks shape the full
plan. A pilot that only says the data loaded successfully is insufficient for a
full Article/Analysis proposal.

## Pre-Analysis Proposal Gate

The proposal gate happens before any Researcher writes `analysis.py`, runs model
fitting, writes results, or drafts a manuscript. Its job is to prevent weak,
unoriginal, infeasible, or mismatched studies from consuming compute and then being
polished into a manuscript-shaped artifact.

Each Researcher must create a `proposal_gate/` folder under its submission folder
before `revision_00/`:

```text
submissions/<run-id>/submission_<n>_<researcher-id>/proposal_gate/
  data_familiarization.md
  pilot_study_plan.md
  pilot_study_results.json
  pilot_compute_log.csv or pilot_compute_log.json
  pilot_lessons.md
  candidate_studies.md
  selected_proposal.md
  compute_budget_estimate.md
  proposal_response.md   optional, required after proposal revision
```

`candidate_studies.md` must contain three to five candidate studies written after
Phase 0. Each candidate should include the question, claim class, expected
contribution, plausible baselines, minimum evidence, likely failure modes,
pilot-informed feasibility, and rough compute cost.

`selected_proposal.md` must include:

1. Goal, Scope, Metric or estimand, Direction, Verify, and Guard.
2. Article type and whether the run is demo, pilot, benchmark, or full research.
3. Prior-work gap and what is new relative to literature or prior runs.
4. Planned baseline suite, including trivial, simple, strong standard, and relevant
   domain or published baselines when feasible.
5. Planned ablations or contribution tests.
6. Planned uncertainty, calibration, paired comparison, sensitivity, or statistical
   support.
7. Planned leakage, confounding, robustness, subgroup, shift, external-validation,
   error, or case analyses where appropriate.
8. Minimum publishable result and explicit failure criteria.
9. Compute budget needed for the planned evidence.
10. Safety, privacy, licensing, and domain-use constraints.

`compute_budget_estimate.md` must be grounded in the pilot compute log and should
include a component table with pilot size, pilot seconds, scale factor,
repeats/folds/seeds, effective core count, risk multiplier, estimated compute,
and evidence role. Every non-zero row should show the formula
`pilot_seconds * scale_factor * planned_repeats * effective_cpu_cores *
risk_multiplier / 3600`. Components above 20% of expected compute or 10% of the
run target need their own pilot timing probe or separately timed smoke test. It
must include parseable low/expected/high CPU-core-hour fields:
`estimated_cpu_core_hours_low`, `estimated_cpu_core_hours_expected`, and
`estimated_cpu_core_hours_high`. GPU-hour fields may be added when relevant.

If the selected article type has a compute target and the Researcher's expected
compute estimate falls below 80% of it, or the high estimate does not reach it,
the Researcher must add meaningful experiments, choose a stronger feasible model,
request article-type downgrade, or request a run-budget revision before
`revision_00/`. A later efficiency override is not a substitute for this
pre-analysis gate in a full Article/Analysis run.

The `study_design_board` must review each selected proposal before analysis begins.
It writes per-proposal reviews under
`agents/study_design_board/workspace/<run-id>/` and a run-level
`runs/<run-id>/proposal_gate_summary.md`.

Allowed Study Design Board decisions are:

1. `approve_for_analysis`: the Researcher may begin `revision_00/` analysis.
2. `revise_before_analysis`: the Researcher must revise `proposal_gate/` artifacts
   before analysis starts.
3. `downgrade_article_type`: the Researcher may proceed only after the run contracts
   and compute budget are updated to a lower bar, such as demo, methods note, or
   benchmark/reusability report.
4. `stop_before_analysis`: the proposal should not consume compute under the current
   run.

No Researcher may start `revision_00/` analysis until the active proposal has an
`approve_for_analysis` decision or an explicitly accepted `downgrade_article_type`
decision reflected in the run contracts. The Integrity Checker and Editor must treat
missing proposal-gate artifacts or unapproved analysis as blocking.

## First-Submission Research Dossier

The initial submission is the baseline for judging each Researcher. Revision rounds
must not be used to hide a shallow first pass. Each Researcher must include, in
`revision_00/`, after proposal-gate approval, a first-submission dossier with:

1. `research_dossier.md`: question, claim class, prior-work gap, rationale, expected
   failure modes, data risks, and why the study is worth running.
2. `eda_report.md` or `eda_report.ipynb`: data profile, missingness, target/outcome
   construction when applicable, split rationale, possible leakage paths, and
   exploratory observations. The form is data agnostic; use the medium that best
   fits the dataset.
3. `analysis_plan.md`: prespecified primary question, primary metric or estimand,
   secondary checks, failure criteria, planned comparisons, and stopping criteria.
4. `experiment_registry.csv` or `experiment_registry.json`: planned and executed
   experiments, including failed or null experiments.
5. `compute_log.csv` or `compute_log.json`: wall-clock time, CPU/GPU/backend use,
   number of model fits or analysis runs, seeds, major commands, and whether the
   declared budget was met. If the log includes both component rows and a
   `total_*` row, deterministic clerks use the total row for actual compute and do
   not add it to the component rows.
6. `model_or_method_cards.md`: model, statistical, qualitative, or analytic method
   families considered, what was selected, and why alternatives were rejected.
7. `results.json`, tables, figures, and manuscript draft only after the above
   planning and execution artifacts exist.

Referees should treat a missing or superficial first-submission dossier as a major
or blocking issue even if later revisions add polished outputs.

## Independence And Workspace Contract

Researchers must be operationally independent before their initial submissions:

1. Each Researcher works in an isolated folder such as
   `agents/<researcher-id>/workspace/<run-id>/` and writes a standalone submission
   under `submissions/<run-id>/submission_<n>_<researcher-id>/`.
2. Shared resources are limited to the dataset, run contracts, public literature
   notes that are explicitly declared as shared, and framework rules.
3. Researcher-specific ideas, code, experiment registries, and manuscripts should
   not be copied between Researchers before the first review cycle.
4. Submitted `analysis.py` must be inspectable and runnable as the Researcher's own
   code. Thin wrappers that only call a central run generator or hidden engine fail
   the independence check unless the wrapper is explicitly a demo scaffold and the
   Editor labels the output as non-publication demo.
5. Common utilities may be imported only when they are general-purpose and declared
   in `artifact_manifest.json`; the Researcher's own modeling, analysis, and
   interpretation logic must remain visible in the submission.

## Data-Agnostic Rigor Contract

The empirical program must match the claim. Researchers and Referees should choose
checks from the following generic menu and justify omissions:

1. Dataset profile and governance: provenance, sampling frame, missingness, quality
   limits, use constraints, and split or sampling design.
2. Baselines: trivial, simple, strong standard, and relevant published or domain
   baselines where feasible.
3. Ablations and contribution tests: remove or alter the claimed contribution and
   show whether the claim still holds.
4. Uncertainty and statistical support: confidence intervals, resampling, paired
   tests, sensitivity analysis, power or sample-size reasoning, or other methods
   appropriate to the claim.
5. Calibration, robustness, shift, subgroup, perturbation, external-validity, or
   negative-control checks when they fit the data and question.
6. Error or case analysis: representative failures, edge cases, qualitative audit,
   or residual analysis.
7. Leakage, confounding, and alternative-explanation analysis.
8. Comparison to relevant literature, prior runs, or known baselines with clear
   caveats when direct comparison is infeasible.
9. Null, weak, failed, and abandoned experiments remain visible in the experiment
   registry and manuscript limitations.

No single checklist item is mandatory for every dataset. What is mandatory is a
declared, justified, and referee-audited match between the claim and the evidence.

## Manuscript And Presentation Quality Gate

Research Arena must not treat a small analysis as permission for weak presentation.
Every run must create `runs/<run-id>/manuscript_quality_contract.md` before initial
submissions. That contract is a hard acceptance gate, separate from empirical
integrity and issue resolution.

The contract must state article-type-specific thresholds and use these
machine-readable settings so `tools/research_depth_audit.py` can enforce basic
structural checks:

```text
minimum_manuscript_words: <integer>
minimum_methods_words: <integer>
minimum_display_items: <integer>
minimum_subsection_count: <integer>
minimum_numbered_equations: <integer>
allow_raw_markdown_pdf: <true | false>
allow_fallback_renderer: <true | false>
require_line_numbers: <true | false>
require_numbered_equations: <true | false>
require_rendered_math: <true | false>
require_display_item_explanations: <true | false>
require_manuscript_style_manifest: <true | false>
require_preferred_sans_fonts: <true | false>
require_rendering_toolchain: <true | false>
require_integrated_article_pdf: <true | false>
```

The presentation gate requires:

1. Background or Introduction that explains motivation, prior work, research gap,
   and the thought process behind the study.
2. Results or Findings that read like an argument, not only a list of generated
   artifacts. Use informative subsections for distinct result families.
3. Methods with enough detail for expert audit, including formal or mathematical
   definitions of variables, targets, feature maps, model objectives/losses,
   inference, evaluation estimands, resampling/statistical tests, and calibration or
   uncertainty measures when relevant. Displayed mathematical expressions must use
   valid LaTeX, visible equation numbering when the contract requires numbered
   equations, and visibly rendered notation in the final `manuscript.pdf`.
4. Discussion that explains the meaning, limitations, alternative explanations, and
   implications of both positive and negative findings.
5. Human-readable figures and tables with clear labels, captions or
   caption-equivalent notes, units or denominators where relevant, and names that do
   not require reading source code to understand. Figure labels, legends, tick text,
   panel marks, and annotations must be readable in exported files. Raw internal
   identifiers must be transformed into human-readable labels whenever possible.
   For normal serious-pilot and full-research runs, every revision must include
   `article/article.pdf` as a journal-style integrated article unless the
   manuscript-quality contract explicitly declares a compact/demo/internal
   downgrade with `require_integrated_article_pdf: false`. Every included main-text figure and
   table must visibly pair its title with a short explanatory paragraph written as
   ordinary article prose rather than reader-directed instructions. Every figure
   must also carry an explicit article grouping decision in
   `display_item_explanations.md`: `standalone` with a rationale, or a shared
   group id with panel labels, a group title, and a group-level explanation. This
   is a scientific/editorial judgment by the Researcher and reviewers, not a
   deterministic filename grouping rule. Figure text and visual marks must be
   normalized for the final article scale: titles, subtitles, labels, legends,
   ticks, colorbars, annotations, bars, dots, lines, and error bars should look as
   though they belong to the same article text system rather than a pasted poster
   or debugging plot. Use `tools/figure_presentation_audit.py` for figure-bearing
   integrated articles.
6. A visually readable, line-numbered `manuscript.pdf`. A text-only PDF is
   acceptable, but a raw Markdown dump with visible markup, unrendered table syntax,
   broken wrapping, or monospace-only formatting fails unless the run is explicitly a
   compact non-publication demo and the contract allows it.
7. A run-level `runs/<run-id>/render_toolchain_report.json` created with
   `tools/check_render_toolchain.py` when `require_rendering_toolchain: true`.
   Serious-pilot and full runs must resolve missing Pandoc, XeLaTeX, Poppler,
   qpdf, and fontconfig tools before acceptance unless the Editor downgrades the
   article type.
   For user-facing setup, first run `tools/doctor.py --fix`; it distinguishes
   tools staged in the sibling `required tools` folder, tools installed on the
   machine, and tools visible to the configured runtime.
8. A latest-revision `presentation_checklist.md` declaring `status: pass` or
   `status: fail`, manuscript and Methods word counts, display-item count, PDF visual
   check, figure-label check, table-readability check, display-item plan check,
   display-item explanation check, raw-label translation check, math/method-detail check, line-number check,
   equation-numbering check, math-rendering check, inline-math rendering check,
   human-readable output package check, manuscript typography check, figure
   typography check, render-toolchain check, and known presentation limits.

The manuscript must include a dedicated `Figure And Table Guide`, `Display Item
Interpretation`, or equivalent section. For every figure and table, explain what
the item does, what axes/rows/columns/labels/legends/colors/panels/annotations
mean, what the summary conclusion is, and what caveat prevents overreading. Latest
revisions with main-text display items must include `display_item_plan.md` and
`display_item_explanations.md` using the templates under `agents/templates/`.
When integrated articles are
required, that file must declare whether related figures should be combined into
multi-panel article figures or kept standalone, with a rationale for either
choice. When this judgment is uncertain or disputed, write
`runs/<run-id>/display_item_grouping_review.md` using
`audits/display_item_grouping_rubric.md`.

Each latest revision with main-text figures or tables must also include
`display_item_plan.md` using `agents/templates/display_item_plan.md`. The plan is
the Researcher's claim-led rationale for the display program: why each figure or
table exists, what alternative form was considered, what claim role it has, and
whether it resembles another Researcher's display item, a prior revision, or a
framework example. Shared visual styling is allowed; shared figure programs are a
process risk. `agents/templates/figure_style.py` may be used for fonts,
human-readable labels, mark scale, line widths, grids, and saving, but it must not
be used as a default list of figure concepts, filenames, plot types, or panel
order. When display-program similarity is alleged or visible, write
`runs/<run-id>/display_program_independence_review.md` using
`audits/display_program_independence_rubric.md` and treat unresolved
overconvergence as an independence risk.

The default manuscript typography is the bundled open-source Inter family in
`assets/fonts/inter/`. TeX Gyre Heros, Nimbus Sans, Liberation Sans, Noto Sans,
Source Sans 3, and Source Sans Pro are acceptable deliberate alternatives. Use
Pandoc/XeLaTeX rendering for serious-pilot and full runs. If Pandoc/XeLaTeX is
unavailable, use `agents/templates/render_manuscript_pdf.py` or another renderer
only for explicitly downgraded compact demos or internal review artifacts, and
record the limitation in `manuscript_style_manifest.md`. Use
`agents/templates/figure_style.py` or equivalent Matplotlib settings for figure
text. Built-in PDF Helvetica or Arial must not be the declared font family for
accepted manuscripts.

Researchers may draft `presentation_checklist.md`, but Referees, the Integrity
Checker, and the Editor must verify it. A self-declared pass is not enough for
acceptance. If the presentation gate fails, the Editor must request revision or
reject even when all analysis artifacts reproduce.

## Executable Audit Contract

Before final editorial decision, the Integrity Checker or Editor should run:

1. `python tools/create_work_packets.py <run-id> --phase all` when the run uses an
   orchestrated workflow and explicit prompt packets are needed for independent
   role turns. Work packets are inputs only, not judgments.
2. `tools/doctor.py --fix` when local rendering dependencies are uncertain.
   This is a setup convenience, not the run-level evidence artifact.
3. `tools/review_similarity_audit.py` or an equivalent anti-template clerk.
4. `tools/check_render_toolchain.py --run-id <run-id> --write-default` when the
   manuscript-quality contract requires the rendering toolchain.
5. `tools/research_depth_audit.py` or an equivalent structural depth and
   presentation clerk.
6. `tools/trajectory_clerk.py` or an equivalent revision-trajectory clerk when the
   run has more than one revision.
7. `python tools/artifact_authority_audit.py <run-id> --write-default` or an
   equivalent event-log author/path authority clerk.
8. `python tools/scripted_generation_audit.py <run-id> --write-default` or an
   equivalent central-generator risk clerk.
9. `python tools/run_state_audit.py <run-id> --write-default` before freezing, then
   again after final decision if the decision event was just appended.
10. A rerun of each submitted `analysis.py` or an explicitly documented reason why
   rerun is infeasible.
11. A proposal-gate compliance check confirming that every analyzed submission had
   Study Design Board approval or a documented article-type downgrade before
   analysis began.
12. LLM-backed scientific and manuscript judgment using the relevant rubrics under
    `audits/`, including `audits/manuscript_article_voice_rubric.md` when the
    manuscript may be answering reviewers rather than reading as a final article
    and `audits/display_item_narrative_rubric.md` when figure/table title-adjacent
    explanations need judgment, plus
    `audits/display_program_independence_rubric.md` when multiple Researchers'
    display programs appear overconverged or style/program boundaries are disputed.
13. `python tools/archive_hygiene_audit.py <run-id> --write-default` before final
    archive.
14. `python tools/freeze_run.py <run-id> --stage pre-decision` immediately before
    the final editorial decision. The decision must cite the resulting
    `pre_decision_freeze_manifest.json` as an input.
15. `python tools/freeze_run.py <run-id> --stage post-decision` after the final
    decision and final event-log entry, followed by verification.
16. `python tools/finalize_run_outputs.py <run-id> --replace --cleanup-source-roots`, followed by
    `python tools/finalize_run_outputs.py <run-id> --verify`, to create the clean
    final handoff folder under `outputs/<run-id>/` and remove duplicate
    run-specific workflow roots after successful bundle verification.

Unresolved proposal-gate, presentation-gate, artifact-authority, state-order,
scripted-generation, independence, reproducibility, or anti-template findings block
acceptance. Structural clerk outputs do not decide scientific depth; the Editor
must combine clerk evidence with LLM-backed scientific depth, trajectory,
novelty/article-fit, reviewer-quality, manuscript article-voice, display-item
narrative, and display-program independence judgments where relevant.

## Shared Resources

- Dataset: local `data/OASIS_cross_tbl_df.csv` for the quickstart after the user
  downloads or exports it following `data/README.md`.
- Dataset notes: `data/README.md`.
- Agent folders: `agents/`.
- Proposal gate agent: `agents/study_design_board/`.
- Agent extension guide and templates: `agents/README.md` and `agents/templates/`.
- Workflow figure: `assets/research_arena_workflow.pdf`.

All Researchers receive the same dataset and the same governance rules. They do not
need to share the same target, focal variable, metric, or research question.

## Agents

Default community:

- `researcher_1`: conservative, interpretable, methodical Researcher.
- `researcher_2`: comparative Researcher willing to combine simple signals.
- `study_design_board`: pre-analysis Research Mentor that reviews candidate studies,
  article-type fit, evidence plans, and compute realism before analysis begins.
- `integrity_checker`: reproducibility and integrity auditor.
- `referee_1`: machine-learning methods and statistics Referee.
- `referee_2`: domain and scientific-interpretation Referee.
- `referee_3`: reproducibility and software-artifact Referee.
- `referee_4`: novelty, literature, and field-advancement Referee.
- `editor_publisher`: final gate-based decision maker and publisher.

The community can be expanded without changing code. To add more Researchers or
Referees, create another agent folder such as `agents/researcher_3/` or
`agents/referee_5/` with the same three files: `config.json`, `profile.md`, and
`rules.md`. Then name the extra agents in the user's run prompt. The LLM agent
should include all explicitly named Researchers and Referees in the run.

Each agent folder contains:

- `config.json`: machine-readable role settings.
- `profile.md`: role/personality description.
- `rules.md`: behavioral rules for the LLM agent to follow while acting as that
  agent.

## Venue And Article-Type Contract

Each run must declare a target article type. For a Nature Machine
Intelligence-style Article or Analysis, require:

1. Abstract, Introduction, Results with informative subheadings, Discussion,
   Methods sufficient for expert replication, Data and Code Availability,
   Limitations, Protocol Compliance, and References.
2. A substantial research article rather than an extended abstract.
3. Four to six genuine multi-panel display items where appropriate. If a figure is
   exported in multiple formats, it counts as one display item.
4. A comparison table against relevant literature.
5. A reference list appropriate to the topic, often 25-50 real references for a full
   Article or Analysis.
6. A field-advancement argument grounded in evidence.
7. A coherent empirical program: baseline suite, ablations, calibration or
   uncertainty, bootstrap confidence intervals or other appropriate statistical
   tests, subgroup/shift checks, negative controls, error analysis, external
   validation when feasible, and published-baseline comparison.

For smaller demos, the user may declare a demo or workshop article type with a lower
bar, but agents must state that lower bar in the run summary and editorial record.

## Run Loop

1. Create a run id, usually `YYYYMMDD_<short_name>`.
2. Declare `article_type_contract.md`, `study_design_contract.md`,
   `research_depth_contract.md`, `manuscript_quality_contract.md`,
   `compute_budget.md` or `compute_budget.json`, `agent_independence_plan.md`, and
   `editor_gate_plan.md` for the run. Initialize `runs/<run-id>/event_log.jsonl`.
3. Profile the shared dataset enough to understand columns, row count, missingness,
   plausible variable types, data provenance, and safe-use constraints.
4. Researchers may use the internet to find recent relevant literature, but must
   cite sources, distinguish prior work from their own contribution, and avoid
   plagiarism.
5. Each participating Researcher works in an isolated workspace and completes
   Phase 0 data familiarization and pilot artifacts before candidate generation.
6. Each participating Researcher creates `proposal_gate/candidate_studies.md`,
   `proposal_gate/selected_proposal.md`, and
   `proposal_gate/compute_budget_estimate.md` before implementation.
7. The `study_design_board` reviews every selected proposal, writes per-Researcher
   proposal reviews, and writes `runs/<run-id>/proposal_gate_summary.md`.
8. Researchers with `revise_before_analysis` decisions revise proposal artifacts
   and receive another Study Design Board decision before analysis. Researchers with
   `stop_before_analysis` decisions do not proceed. Researchers with
   `downgrade_article_type` decisions proceed only after affected run contracts and
   compute budgets are updated.
9. Only after proposal-gate approval, each participating Researcher writes the
   first-submission research dossier, implements a reproducible empirical program,
   logs compute/experiments, writes `results.json`, creates tables and PDF
   figures, writes a manuscript and visually readable manuscript PDF, writes
   `presentation_checklist.md`, and initializes an issue ledger.
10. Researchers compete from the same shared resource but are free to choose
   different questions, methods, variables, and metrics.
11. The Integrity Checker audits each submission for proposal-gate compliance,
   reproducibility, leakage,
   consistency, missing artifacts, p-hacking risk, plagiarism/originality concerns,
   citation integrity, article-type compliance, research-depth compliance,
   researcher independence, issue-ledger traceability, verification-matrix
   completeness, and stale or templated review behavior.
12. Each participating Referee reviews each submission using the structured review
   schema in that Referee's rules.
13. Every Referee request must create or update an issue owned by that Referee, with
   an ID, severity, triggering artifact, required evidence, acceptance criterion,
   direct reviewer question when useful, and lifecycle status. Referee 1 owns `R1-*` issues,
   Referee 2 owns `R2-*` issues, and so on. A Referee may mention another
   Referee's issue as context, but must not resolve, rename, merge, or use it as
   the main basis for that Referee's recommendation.
14. Before any revision folder after `revision_00/` is created, each Researcher
    writes `revision_plan.md` and receives plan approval, plan revision, downgrade,
    or rejection from the owning reviewer, Integrity Checker, or Editor.
15. Researchers revise only in response to actual open issues, integrity findings,
    approved revision plans, and editor guidance. Revision plans must declare
    `research_delta_tier`; material or supporting revisions must include
    `material_research_delta.md`, while nonmaterial revisions must say which
    central issues remain unresolved. `revision_response.md` must cite exact files,
    tables, figures, or lines that address each issue and must answer every direct
    reviewer question.
16. Follow-up Referees verify issue status as `verified_resolved`,
    `partially_resolved`, `unresolved`, `editorial_risk_accepted`, or `superseded`
    based on the cited evidence. Verification must be written into
    `verification_matrix.csv` or `verification_matrix.json`; `opened`,
    `response_submitted`, unchecked, or unresolved blocking/central-major rows block
    acceptance.
17. The Integrity Checker or Editor runs deterministic clerk tools and then asks
    LLM-backed auditors to judge scientific depth, revision trajectory,
    novelty/article fit, reviewer quality, manuscript article voice,
    display-item narrative quality, and display-program independence where those
    questions are relevant.
18. The Editor/Publisher makes a gate-based decision. Acceptance requires proposal
    gate compliance, integrity pass, zero unresolved blocking issues, adequate
    novelty, sufficient evidence, verified issue resolution, no unchecked or
    unresolved blocking/central-major verification-matrix rows, no unresolved anti-template audit flags, no unresolved
    presentation-gate or independence flags, adequate LLM-backed scientific
    judgment, and article-type compliance.
19. If no submission passes the gates, publish no manuscript.

## Structured Review Contract

Every Referee review must include:

- recommendation;
- what changed since the previous revision, with concrete artifact references;
- key claims;
- blocking major concerns;
- minor concerns;
- required experiments;
- statistical concerns;
- novelty concerns;
- figure/table concerns;
- literature gaps;
- issue-status review for that Referee's own prior issues;
- direct questions for the Researcher to answer;
- assessment of the Researcher's answers from the prior round;
- what would change the recommendation;
- scores tied to the Referee's specialty.

Every major or blocking concern must cite the triggering artifact path and, when
possible, a table row, figure panel, metric name, manuscript section, or line
number. It must state the exact missing evidence. Generic concerns such as
"improve rigor" or "add more analysis" are not valid unless they are translated
into concrete acceptance criteria.

Referee reviews must be distinct. Reusing the same concern text across Referees or
rounds is allowed only when the same artifact problem is independently justified
with the Referee's own specialty lens. The Integrity Checker or Editor should run
the review-similarity clerk and flag near-duplicate reviews before acceptance.
The clerk output is evidence for follow-up judgment; it is not a substitute for
Referee-specific reasoning or Editor review.

## Issue Ledger Contract

Each submission revision should include:

```text
issue_ledger.md
issue_ledger.json   optional but preferred
revision_response.md
```

Every issue must include:

- issue ID, such as `R1-MAJOR-02` or `IC-BLOCKING-01`;
- source agent;
- severity: blocking, major, minor, or advisory;
- triggering artifact location;
- required evidence;
- acceptance criterion;
- reviewer question, if the issue asks the author to explain or justify something;
- status: `opened`, `response_submitted`, `verified_resolved`,
  `partially_resolved`, `unresolved`, `editorial_risk_accepted`, or `superseded`;
- reviewer verification note;
- verification-matrix row ID.

Issue status in `issue_ledger.md` or `issue_ledger.json` is not enough for
acceptance. The active revision must also include a verification matrix with one row
per `opened`, `response_submitted`, `verified_resolved`, `partially_resolved`,
`unresolved`, `editorial_risk_accepted`, or `superseded` issue.

## Verification Matrix Contract

Each revised submission must include `verification_matrix.csv` or
`verification_matrix.json`. Preferred CSV columns:

```text
issue_id,source_agent,owning_reviewer,author_claim,evidence_path,reviewer_checked,verification_status,verification_note,question_answered,remaining_action
```

Allowed `verification_status` values are `opened`, `response_submitted`,
`verified_resolved`, `partially_resolved`, `unresolved`,
`editorial_risk_accepted`, or `superseded`.
`reviewer_checked` must be `true` only after the owning Referee or Integrity
Checker has inspected the exact cited evidence. The Editor must fail the acceptance
gate if any required row is missing, any `reviewer_checked` value is false, or any
blocking/central-major issue remains `opened`, `response_submitted`,
`partially_resolved`, or `unresolved`.

## Question-Answer Contract

Referees should ask direct questions when a concern requires explanation rather
than only a new artifact. Researcher responses must answer each question in
`revision_response.md`, cite evidence, and state whether the answer changes the
manuscript claim, limitation, method, or result. Follow-up Referees must judge the
answer as adequate, partially adequate, or inadequate in the next review and in the
verification matrix.

## Manuscript Revision Contract

Researchers must revise the manuscript itself when review changes the study's
claim, interpretation, limitation, novelty argument, method description, or
evidence weight. Adding new files is not sufficient. Final manuscripts should show
changed claims, calibrated limitations, and revised interpretation rather than only
a list of newly generated artifacts.

## Presentation Checklist Contract

Each revision must include `presentation_checklist.md`. It must report:

```text
status: pass | fail
manuscript_word_count: <integer>
methods_word_count: <integer>
display_item_count: <integer>
pdf_visual_check: pass | fail
figure_label_check: pass | fail
figure_text_size_normalization_check: pass | fail
figure_mark_scale_check: pass | fail
table_readability_check: pass | fail
display_item_plan_check: pass | fail | not_required
display_item_explanation_check: pass | fail
raw_label_translation_check: pass | fail
math_or_method_detail_check: pass | fail
line_number_check: pass | fail
equation_numbering_check: pass | fail
math_rendering_check: pass | fail
inline_math_rendering_check: pass | fail
human_readable_output_check: pass | fail
manuscript_typography_check: pass | fail
figure_typography_check: pass | fail
render_toolchain_check: pass | fail | waived
article_pdf_check: pass | fail | not_required only when contract explicitly opts out
known_presentation_limits: <none or explicit limitations>
```

The checklist must cite the manuscript, figure, table, method-detail, and
rendering-toolchain evidence used for each pass/fail judgment. The Editor must
treat missing, stale, or unverified checklist rows as presentation-gate failures.

## Anti-Template Review Audit

Runs should include an anti-template clerk check before final editorial decision.
The check compares Referee reviews across Referees and rounds, normalizes trivial
identity labels, and flags high-similarity reviews that may lack distinct
artifact-specific reasoning. A helper script is provided at
`tools/review_similarity_audit.py`. The audit output should be stored under
`runs/<run-id>/review_similarity_audit.json` and, when useful,
`runs/<run-id>/review_similarity_audit.csv`. Unresolved high-similarity flags block
acceptance until the responsible LLM-backed reviewer-quality judgment explains
whether the reviews are genuinely independent, evidence-linked, and adequate.

## Artifact Contract

Use this folder shape:

```text
runs/<run-id>/
  dataset_profile.md
  event_log.jsonl
  article_type_contract.md
  study_design_contract.md
  proposal_gate_summary.md
  research_depth_contract.md
  manuscript_quality_contract.md
  compute_budget.md or compute_budget.json
  agent_independence_plan.md
  editor_gate_plan.md
  research_depth_audit.json
  review_similarity_audit.json
  trajectory_clerk.json
  artifact_authority_audit.json
  run_state_audit.json
  scripted_generation_audit.json
  archive_hygiene_audit.json
  pre_decision_freeze_manifest.json
  pre_decision_freeze_verification.json
  post_decision_archive_manifest.json
  post_decision_archive_verification.json
  scientific_depth_review.md
  revision_trajectory_review.md
  novelty_article_fit_review.md
  reviewer_quality_review.md
  manuscript_article_voice_review.md
  display_item_narrative_review.md
  display_program_independence_review.md
  summary.md
  final_decision.md

submissions/<run-id>/
  submission_001_<researcher-id>/
    proposal_gate/
      data_familiarization.md
      pilot_study_plan.md
      pilot_study_results.json
      pilot_compute_log.csv or pilot_compute_log.json
      pilot_lessons.md
      candidate_studies.md
      selected_proposal.md
      compute_budget_estimate.md
      proposal_response.md
    revision_00/
      proposal.md
      research_dossier.md
      eda_report.md or eda_report.ipynb
      literature_notes.md
      analysis_plan.md
      model_or_method_cards.md
      experiment_registry.csv or experiment_registry.json
      compute_log.csv or compute_log.json
      compute_reconciliation.md or compute_reconciliation.json when triggered
      analysis.py
      results.json
      stable_results.json when available
      empirical_provenance.json when revision_00 needs an explicit baseline; required after revision_00
      artifact_manifest.json
      issue_ledger.md
      issue_ledger.json
      verification_matrix.csv
      revision_response.md
      manuscript.md
      manuscript.pdf
      article/
        article.md
        article.pdf
        article_build_report.json
      display_item_plan.md
      display_item_explanations.md
      manuscript_style_manifest.md
      presentation_checklist.md
      tables/
      figures/
    revision_01/
      revision_plan.md
      material_research_delta.md when research_delta_tier is tier_a_material or tier_b_supporting
      ...

human_readable_outputs/<run-id>/
  submission_001_<researcher-id>/
    revision_00/
      README.md
      manuscript.pdf
      figures/
      tables/
      source_code/
      human_readable_package_manifest.json

work_packets/<run-id>/
  proposal_gate.md
  integrity_round_00.md
  referee_1_round_00.md
  referee_2_round_00.md
  referee_3_round_00.md
  referee_4_round_00.md
  scientific-depth_audit.md
  revision-trajectory_audit.md
  novelty-article-fit_audit.md
  reviewer-quality_audit.md
  manuscript-article-voice_audit.md
  display-item-narrative_audit.md
  editor_final_decision.md

agents/<agent-id>/workspace/<run-id>/
  study design board proposal reviews
  researcher scratch notes, experiment logs, and independent drafts
  integrity reports
  referee reviews
  issue-status notes
  editorial records

outputs/<run-id>/
  README.md
  human_readable_outputs/
  diagnosis_process_files/
  final_output_manifest.json
  final_output_verification.json

runs/<run-id>/
  research_depth_audit.json
  research_depth_audit.csv
  review_similarity_audit.json
  review_similarity_audit.csv
  trajectory_clerk.json
  trajectory_clerk.csv
  scientific_depth_review.md
  revision_trajectory_review.md
  novelty_article_fit_review.md
  reviewer_quality_review.md
  manuscript_article_voice_review.md
  display_item_narrative_review.md
  display_program_independence_review.md
```

Use Python for analysis code by default. Manuscript PDFs should be visually readable
line-numbered text/math/expression artifacts, not raw Markdown dumps, unless the run
is explicitly a compact non-publication demo and the manuscript-quality contract
allows it. Put figures and tables in separate folders. Use PDF figure files by
default, with SVG only as an optional extra, and keep labels readable with bundled
Inter-first open-source sans-serif typography. Inline math spans and displayed
equations must render as LaTeX-style serif math, while ordinary manuscript and
figure text use the preferred open-source sans-serif typography. Serious-pilot
and full runs should produce a passing `render_toolchain_report.json` before
manuscript acceptance.

## Safety Rules

- Do not treat outputs as clinical advice, diagnostic evidence, causal discovery, or
  validated science.
- Do not use private data unless the user explicitly provides it and confirms that
  it may be used.
- Do not paste or write secrets into artifacts.
- Do not paste private/local data into search engines, external websites, or
  third-party literature tools.
- Do not copy text, figures, tables, code, or study framing from published work
  without clear attribution. Prefer paraphrase and synthesis over quotation.
- Do not fabricate citations, findings, related work, or source links.
- Do not selectively report only successful findings. Null, weak, and failed
  results should remain visible.
- Inspect generated analysis code before running it.
- Generated analysis code should use local files only, avoid network access, avoid
  shell calls, and avoid hidden external dependencies.
- Integrity failures block publication acceptance.

## Natural-Language Start Prompt

Use this prompt from the repository root:

```text
Please run Research Arena on data/OASIS_cross_tbl_df.csv.
If the CSV is missing, stop and tell me to follow data/README.md to create it locally.
Follow program.md and all agent rules under agents/.
Use two Researchers, one Study Design Board, one Integrity Checker, four Referees,
and one Editor/Publisher.
Use referees referee_1, referee_2, referee_3, and referee_4.
If you orchestrate role turns, create explicit work packets under
`work_packets/oasis_demo/`; do not use a central script or prewritten template to
generate Researcher submissions, Referee reviews, integrity reports, LLM-backed
judgments, or the Editor decision.
Researchers may choose different research questions from the shared dataset; there is
no shared target requirement. Run one initial submission plus one evidence-linked
revision round. Each revision must respond to actual issue-ledger items, not round
number. Before any initial submission, create the article-type, study-design,
research-depth, manuscript-quality, compute-budget, independence, and editor-gate
contracts. Each Researcher must first complete Phase 0 data familiarization and a
small pilot study, then create `proposal_gate/candidate_studies.md`,
`proposal_gate/selected_proposal.md`, and
`proposal_gate/compute_budget_estimate.md`. The Study Design Board must review every
selected proposal and write `runs/oasis_demo/proposal_gate_summary.md`; no
Researcher may start `analysis.py`, model fitting, results, or manuscript drafting
until the active proposal is approved for analysis or explicitly downgraded with
updated contracts. Each approved Researcher must use an independent workspace and
include a first-submission dossier, EDA report, experiment registry, compute log,
and standalone analysis code. Each revision must include
`presentation_checklist.md`, `display_item_plan.md`, and
`display_item_explanations.md`, include
`manuscript_style_manifest.md` when required, and pass the manuscript-quality
contract, including a manuscript section explaining every figure/table, line
numbers, numbered LaTeX equations when relevant, readable open-source sans-serif
typography for text and figures, LaTeX-style serif math for inline and display
equations, an integrated `article/article.pdf` unless the contract explicitly
opts out for a compact/demo/internal run, plus a passing render-toolchain report
when required. Before editorial acceptance, run
`python tools/package_human_readable_outputs.py --run-id oasis_demo --replace`
or the corresponding run id so every revision has a human-readable package
under `human_readable_outputs/<run-id>/`. Run
the deterministic clerk checks before any final decision, including render
toolchain, structural depth, review similarity, revision trajectory when
multiple revisions exist, artifact authority, run-state order, and
scripted-generation risk. Then ask
LLM-backed auditors to judge scientific depth, revision trajectory,
novelty/article-type fit, reviewer quality, manuscript article voice,
display-item narrative quality, and display-program independence when relevant
using the rubrics under `audits/`.
Freeze the run with `python tools/freeze_run.py oasis_demo --stage pre-decision`
immediately before the final editorial decision, cite
`runs/oasis_demo/pre_decision_freeze_manifest.json` in the decision event, then
create and verify `runs/oasis_demo/post_decision_archive_manifest.json` after the
final event-log entry. Then run
`python tools/finalize_run_outputs.py oasis_demo --replace --cleanup-source-roots` and
`python tools/finalize_run_outputs.py oasis_demo --verify` so the final handoff is
under `outputs/oasis_demo/`, divided into human-readable outputs and
diagnosis/process files, without duplicate run-specific workflow roots remaining
in the project root. Give me the final editorial decision, the accepted manuscript
path if any, and the clean output bundle path.
```

## Natural-Language Continuation Prompt

```text
Continue the existing Research Arena run in runs/oasis_demo.
Read the proposal-gate summary, Study Design Board reviews, referee reviews,
integrity reports, issue ledgers, revision responses, study-design contract,
research-depth contract, manuscript-quality contract, compute budget,
agent-independence plan, event log, revision plans, experiment registries, compute
logs, display-item plans, presentation checklists, style manifests, prior deterministic clerk outputs,
and prior LLM-backed judgment artifacts.
Before creating any revision after revision_00, require a revision_plan.md that maps
open issues to planned evidence, compute, verification, manuscript changes,
`research_delta_tier`, `material_research_delta.md` expectations, and
stop/downgrade criteria. Revise each Researcher submission only in response to
actual open issues, rerun integrity checks including proposal-gate compliance, run
the deterministic clerks as evidence providers, including artifact authority,
state order, scripted-generation risk, and freeze verification, have every Referee
verify issue status, ask LLM-backed auditors to judge scientific depth, trajectory,
and display-program independence when relevant, and ask the Editor/Publisher to make a gate-based decision. Do not
continue a stopped or unapproved proposal, and do not accept a polished but
shallow, scientifically stagnant, poorly presented, centrally generated, or
non-independent submission.
```

## Natural-Language Expanded-Community Prompt

```text
Please run Research Arena with researchers researcher_1, researcher_2, researcher_3
and referees referee_1, referee_2, referee_3, referee_4, referee_5. If researcher_3
or referee_5 folders do not exist, create them from agents/templates/ and give each
a distinct profile. Follow program.md and all agent rules. Have every Referee review
every Researcher submission unless I specify a different review assignment.
```

## Natural-Language Audit Prompt

```text
Audit this Research Arena run for safety, privacy, reproducibility, protocol
consistency, issue-ledger traceability, and gate-based editorial compliance. Check
for private data leakage, unsafe generated code, data leakage, p-hacking risk,
missing proposal-gate artifacts, unapproved analysis starts, missing
first-submission dossiers, missing compute logs, missing experiment registries,
missing or failed presentation checklists, missing manuscript style manifests, raw
Markdown manuscript PDFs, missing line numbers, missing or failed render-toolchain
reports, unnumbered or visibly unrendered display equations, visibly unrendered
inline math spans, unreadable or poorly
typed figures or tables, non-standalone analysis wrappers, unresolved research-depth or
presentation-gate flags, unsupported claims, stale artifacts, unresolved blocking
issues, missing revision plans, missing display-item plans for main-text displays,
missing LLM-backed scientific judgments, artifact
authority violations, state-order violations, self-certifying verification rows,
missing freeze manifests, and deterministic review/acceptance patterns. Run
`tools/check_render_toolchain.py`, `tools/research_depth_audit.py`,
`tools/review_similarity_audit.py`, `tools/trajectory_clerk.py`,
`tools/artifact_authority_audit.py`, `tools/run_state_audit.py`, and
`tools/scripted_generation_audit.py` if available,
but treat them as fact collectors rather than final judges. Summarize findings with
file paths, scientific risks, and recommended fixes.
```
