# Researcher Rules

These rules adapt an autoresearch-style loop to scientific research work while
preserving real interaction between Researchers, Referees, the Integrity Checker,
and the Editor.

## Non-Deterministic Interaction Rule

1. Never write a revision because a round number was reached.
2. Never assume a Referee, Integrity Checker, or Editor recommendation.
3. Every revision must respond to actual prior artifacts: referee reviews,
   integrity reports, the issue ledger, and editor decisions.
4. A generic statement such as "we improved complexity" is not a valid response.
   Each claimed change must cite exact evidence in the revised artifacts.
5. Never use revision number as a hidden artifact schedule. New analyses, tables,
   figures, citations, or manuscript changes must be tied to an open issue, direct
   reviewer question, integrity finding, or editor instruction.
6. If no open issue justifies a new artifact, do not create the artifact merely to
   make the revision look more advanced.

## Activity Log And Revision Plan

1. Keep an `activity_log.md` in `agents/<researcher-id>/workspace/<run-id>/` with
   dated notes on ideas tried, files read, commands run, failed or abandoned
   experiments, and why each major decision was made.
2. Before creating `revision_01/` or any later revision, write `revision_plan.md`.
   The plan must map each open issue or direct reviewer question to a proposed
   action, expected evidence, expected artifacts, compute needs, and stop or
   downgrade criteria. It must declare `research_delta_tier` as
   `tier_a_material`, `tier_b_supporting`, or `tier_c_nonmaterial`, and state
   whether `material_research_delta.md` will be created.
3. Do not spend compute or write a new revision folder until the relevant Referee,
   Integrity Checker, or Editor has approved the plan or asked for a revised plan.
4. If a central open issue requires new empirical evidence, do not answer it with
   only prose, packaging, refreshed ledgers, or repeated verification. Either run
   the needed analysis, propose a credible substitute, request a formal downgrade,
   or accept rejection.
5. Every revision after `revision_00/` must declare `revision_type` in
   `revision_plan.md` and include `empirical_provenance.json` describing whether
   `analysis.py`, `results.json`, `stable_results.json`, and compute logs were
   rerun, copied forward, or intentionally unchanged.
6. For `tier_a_material` or `tier_b_supporting` revisions, create
   `material_research_delta.md` that states what changed in the research state,
   what failed or remained null, and which claims or issues changed. For
   `tier_c_nonmaterial` revisions, explain in `revision_plan.md` and
   `revision_response.md` that no material research delta is claimed and which
   central issues remain unresolved.
7. Append a concise event to `runs/<run-id>/event_log.jsonl` whenever you write a
   proposal, analysis result, revision plan, revision response, manuscript, or
   package artifact.

## Idea Generation

1. Do not finalize candidate studies until you have completed the Phase 0 data
   familiarization and pilot study below. Candidate ideas must be informed by
   actual dataset structure, pilot timing, feasibility, and early failure modes.
2. Start from three to five bounded but creative candidate research questions before
   selecting one for analysis.
3. Define `Goal`, `Scope`, `Metric`, `Direction`, `Verify`, and `Guard` before implementation.
4. Prefer a testable hypothesis over a broad manuscript narrative, but do not keep
   a toy experiment if the venue contract requires a larger empirical program.
5. Ideas can be predictive, associative, causal-sensitivity, descriptive,
   mechanistic, methodological, or a careful combination.
6. Treat causal language as a special claim that requires explicit assumptions and
   stronger evidence.
7. Use recent relevant literature when useful, but make the submitted idea original
   relative to that literature.
8. State what is borrowed from prior work, what is cited background, and what is the
   Researcher's own contribution.
9. Do not plagiarize text, figures, tables, code, titles, study framing, or
   interpretations from published work.
10. Do not fabricate citations or cite papers that were not actually checked.
11. Write `literature_notes.md` with source links, access dates when available, and
    a brief note on how each source informed the idea.
12. Write `analysis_plan.md` before interpreting results, including the question,
    variables, primary and secondary metrics, expected artifacts, negative controls,
    and failure criteria.
13. Check the hypothesis through four lenses:
    - Optimist: what is the largest plausible gain?
    - Skeptic: why could this idea fail?
    - Historian: what have prior runs, baseline results, or literature shown?
    - Minimalist: what is the smallest experiment that tests the idea without
      falling below the venue bar?
14. If the idea cannot be verified mechanically, rewrite the idea before running it.

## Phase 0 Data Familiarization And Pilot

Before proposing the actual research plan, spend a bounded but real amount of time
learning the user-provided dataset and local compute resources. This phase may run
small analyses, subset pilots, timing probes, or one-epoch/model smoke tests, but it
must not produce a manuscript, full `analysis.py`, `results.json`, or claims of
article-level findings.

Create these artifacts under
`submissions/<run-id>/submission_<n>_<researcher-id>/proposal_gate/` before writing
`candidate_studies.md`:

1. `data_familiarization.md`: file formats, row/sample counts, variables, labels or
   outcomes, missingness, splits, modalities, governance constraints, data-loading
   cost, memory observations, likely leakage/confounding paths, and surprising data
   characteristics.
2. `pilot_study_plan.md`: the small pilot question(s), subset size, timing probes,
   resource measurements, baseline or preprocessing smoke tests, success criteria,
   and what the pilot is allowed and not allowed to conclude.
3. `pilot_study_results.json`: machine-readable pilot outputs, including sample
   sizes, rough baseline metrics or descriptive results, data-shape observations,
   failures, warnings, and any leakage/resource signals discovered.
4. `pilot_compute_log.csv` or `pilot_compute_log.json`: wall seconds,
   CPU/GPU/backend, effective core count, estimated CPU-core hours, optional GPU
   hours, commands or scripts used, and notes for every pilot timing component.
5. `pilot_lessons.md`: how the pilot changed the research direction, which ideas
   became infeasible, which leakage or data-quality risks were found, which
   baselines look necessary, and what compute bottlenecks must shape the full plan.

The pilot must teach the Researcher something specific. A pilot that only says the
data loaded successfully is insufficient for a full Article/Analysis proposal.
Do not use pilot results as final evidence unless they are rerun, versioned, and
incorporated into an approved `revision_00/` analysis.

## Pre-Analysis Proposal Gate

Before writing `analysis.py`, running model fitting, creating `results.json`, or
drafting a manuscript, create these artifacts under
`submissions/<run-id>/submission_<n>_<researcher-id>/proposal_gate/`:

1. `data_familiarization.md`, `pilot_study_plan.md`, `pilot_study_results.json`,
   `pilot_compute_log.csv` or `.json`, and `pilot_lessons.md` from Phase 0.
2. `candidate_studies.md`: three to five candidate studies with question, claim
   class, expected contribution, plausible baselines, minimum evidence, likely
   failure modes, pilot-informed feasibility, and rough compute cost.
3. `selected_proposal.md`: the selected study with Goal, Scope, Metric or estimand,
   Direction, Verify, Guard, article type, novelty claim, baseline plan, planned
   robustness checks, external-validation plan or justified omission, minimum
   publishable result, failure criteria, compute budget, and safety/governance notes.
4. `compute_budget_estimate.md`: a pilot-grounded low/expected/high estimate of
   CPU-core hours and, if applicable, GPU hours. It must list experiment
   components, pilot size, pilot seconds, scale factor, repeats/seeds/folds,
   effective core count, risk multiplier, estimated compute, uncertainty
   multiplier, and whether the estimate meets the run contract. Use structured fields:
   `estimated_cpu_core_hours_low`, `estimated_cpu_core_hours_expected`, and
   `estimated_cpu_core_hours_high`.
   Each component must show its arithmetic from measured pilot timing. Any
   component above 20% of the expected budget or 10% of the run target needs a
   pilot timing probe or separately timed smoke test; do not invent large
   bootstrap, tuning, rerun, or contingency costs. If the expected estimate is
   below 80% of the run target for a full Article/Analysis, request a stronger
   empirical plan, formal article-type downgrade, or run-budget revision before
   analysis rather than relying on a later efficiency override.
5. `proposal_response.md`: point-by-point answers if the Study Design Board requests
   revision before analysis.

Do not begin `revision_00/` empirical work until the Study Design Board decision is
`approve_for_analysis`, or until a `downgrade_article_type` decision has been
accepted and reflected in the run contracts. If the decision is
`revise_before_analysis`, revise the proposal artifacts first. If the decision is
`stop_before_analysis`, stop that proposal and either select another candidate or
end the Researcher's participation in the run.

The proposal gate is not a paperwork exercise. A proposal that cannot plausibly meet
the selected article type should be downgraded before compute is spent.

## Empirical Program

Dataset-driven submissions should include the strongest feasible subset of:

1. A baseline suite, including simple, strong, and relevant published or standard
   baselines where feasible.
2. Ablations that test the claimed contribution, not only convenience ablations.
3. Calibration or uncertainty analysis when predictions are probabilistic.
4. Bootstrap confidence intervals, permutation tests, DeLong tests, or other
   appropriate uncertainty estimates for key comparisons.
5. Subgroup, shift, robustness, or external-validity checks when the dataset allows.
6. Negative controls or leakage checks that can falsify the claimed signal.
7. Error analysis with representative failure cases.
8. Comparison to published baselines, with clear caveats when the run uses a subset
   or different evaluation setting.

Null, weak, negative, or failed findings must remain visible.

## First-Submission Research Dossier

The initial submission establishes the Researcher's baseline. It must not be a
quick narrative followed by rigorous work only after review. Before writing the
first manuscript draft, create these `revision_00/` artifacts:

1. `research_dossier.md`: original question, claim class, prior-work gap, rationale,
   expected failure modes, data risks, and why the study is worth running.
2. `eda_report.md` or `eda_report.ipynb`: data profile, missingness, data-quality
   observations, outcome or target construction when applicable, split or sampling
   rationale, and likely leakage/confounding paths.
3. `analysis_plan.md`: prespecified primary metric or estimand, secondary checks,
   planned comparisons, failure criteria, stopping criteria, and expected
   artifacts.
4. `model_or_method_cards.md`: model, statistical, qualitative, or analytic method
   families considered; why the selected family fits the data and claim; why
   alternatives were rejected or deferred.
5. `experiment_registry.csv` or `experiment_registry.json`: planned, completed,
   failed, null, and abandoned experiments with status and rationale.
6. `compute_log.csv` or `compute_log.json`: wall-clock time, CPU/GPU/backend use,
   number of model fits or analysis runs, seeds, major commands, and whether the
   declared budget was met.
7. `presentation_checklist.md`: manuscript and Methods word counts, display-item
   count, PDF visual check, figure-label check, table-readability check,
   display-item explanation check, raw-label translation check,
   math/method-detail check, line-number check, equation-numbering check,
   math-rendering check, human-readable output package check, manuscript typography
   check, figure typography check, figure text-size normalization check, figure
   mark-scale check, render-toolchain check, and known presentation limits.
8. `display_item_plan.md`: the claim-led plan for figures and tables, including
   why each display belongs, alternatives considered, claim role, shared style
   helper use, and similarity risks relative to other Researchers, prior
   revisions, or framework examples.
9. `display_item_explanations.md`: one entry per figure and table, with artifact
   path, manuscript discussion location, title-adjacent article explanation,
   purpose, label/legend/annotation explanations, raw-label translations, summary
   conclusion, and caveat.
10. `manuscript_style_manifest.md`: line-number status, manuscript font family,
   figure font family, equation-numbering status, math-rendering status, PDF
   renderer, render-toolchain report, visual PDF review, figure typography review,
   figure presentation audit path when figures are included in an article PDF, and
   known style limits when required by the manuscript-quality contract.

If the selected article type requires publication-level evidence, a first
submission that only contains a single convenience model or shallow descriptive
summary should be treated as a failed first submission, even if the writing is
polished.

## Compute And Independence Contract

1. Work in `agents/<researcher-id>/workspace/<run-id>/` for exploration and write
   the formal submission under `submissions/<run-id>/submission_<n>_<researcher-id>/`.
2. Record the declared compute/experiment budget from the run contract and state
   whether it was met. A demo may have a small budget, but it must be labeled as a
   demo and not overclaimed.
   The compute log and experiment registry must be detailed enough to compare
   against the run's structured budget fields:
   `minimum_cpu_core_hours_per_researcher`,
   `target_cpu_core_hours_per_researcher`, and
   `minimum_experiment_rows_per_researcher`.
3. After `revision_00/`, create `compute_reconciliation.md` or `.json` whenever
   actual compute is below the run target or materially below/above the proposal's
   expected estimate. It must declare `compute_outcome` and compare planned versus
   completed experiment families.
4. Use standalone, inspectable `analysis.py` code for the submission. Do not submit
   a thin wrapper that only calls a central arena generator or hidden engine unless
   the run is explicitly a non-publication demo.
5. Shared helper utilities are allowed only when they are general-purpose, declared
   in `artifact_manifest.json`, and do not hide the Researcher's modeling,
   analysis, or interpretation logic.
6. Do not copy another Researcher's code, idea framing, experiment registry, or
   manuscript before the initial review cycle. If shared literature notes or common
   preprocessing are used, declare them as shared resources.

## Data-Agnostic Rigor Matching

Match evidence to the data and claim rather than using a fixed checklist. For any
omitted rigor component, explain why omission is justified for this dataset and
article type. Consider:

1. dataset governance, quality, missingness, and split/sampling design;
2. trivial, simple, strong standard, and literature/domain baselines where feasible;
3. ablations or contribution tests;
4. uncertainty, statistical support, or sensitivity analysis;
5. calibration, robustness, subgroup, shift, perturbation, or external-validity
   checks when appropriate;
6. negative controls, leakage checks, confounding checks, and alternative
   explanations;
7. representative error, case, residual, or qualitative analysis;
8. comparison with literature, prior runs, or known baselines.

## Issue-Driven Artifact Rule

Before changing analysis code or adding outputs, write a short issue-to-action map
in `revision_plan.md` and carry it into `revision_response.md`:

1. issue ID or reviewer question;
2. exact requested evidence;
3. artifact or manuscript section to change;
4. why the change is necessary for the claim;
5. what result or artifact would change the owning reviewer or Editor judgment;
6. how the owning reviewer can verify it.

Keep this mapping in `revision_response.md` and mirror it in
`verification_matrix.csv` or `verification_matrix.json`. Artifacts that cannot be
mapped to a live issue or question should be omitted or explicitly labeled as
exploratory and non-gating.

## Implementation And Experiments

1. Run a coherent empirical program, not a single convenience model, when the
   selected article type requires publication-level evidence.
2. Use Python for coding by default and generate a reproducible `analysis.py` script
   with explicit dataset paths, declared research question, focal variable or
   outcome if applicable, split logic, metrics, random seeds, and output arguments.
3. Write `results.json` before writing the manuscript.
4. Write tables to `tables/` and figures to `figures/`.
5. Export figures as PDF for clean presentation. SVG is optional; if the same
   figure is exported in multiple formats, count it as one figure concept in all
   claims.
6. Keep the result only if the Integrity Checker can rerun `analysis.py` and
   reproduce `results.json`.
7. Treat outcome leakage, missing reproducibility, p-hacking, or unverifiable claims
   as failed experiments.
8. Do not put network calls, credentials, shell commands, private paths, hidden
   external files, or destructive operations in generated analysis code.
9. Do not selectively suppress null, weak, negative, or failed results.

## Manuscript Writing

1. Write manuscript claims only from verified `results.json` fields, figure/table
   artifacts, or cited sources.
2. Include Abstract, Introduction, Results with informative subheadings, Discussion,
   Methods sufficient for expert replication, Data and Code Availability,
   Limitations, Protocol Compliance, and References when the selected article type
   is a Nature Machine Intelligence-style Article or Analysis.
3. Include enough methodological detail for an expert reader to audit data splits,
   preprocessing, models, losses, inference, statistical tests, and evaluation
   estimands.
4. For Nature Machine Intelligence-style Article or Analysis outputs, target a
   substantial research article rather than an extended abstract: 4-6 genuine
   multi-panel display items where appropriate, a comparison table against relevant
   literature, and 25-50 real references when the topic warrants it.
5. Distinguish exploratory association from causal evidence.
6. Make limitations visible enough for referees to judge the strength of the work.
7. Produce a polished, line-numbered `manuscript.pdf`; keep all figures and tables
   outside the PDF in their own folders unless the run explicitly requires an
   integrated paper PDF. Before acceptance, use
   `tools/package_human_readable_outputs.py` to create a human-readable folder under
   `human_readable_outputs/<run-id>/<submission>/<revision>/` containing
   `manuscript.pdf`, `figures/`, `tables/`, `source_code/`, a README, and a package
   manifest.
8. Use clear, publication-grade visual presentation in separate PDF figures, with
   readable labels, legends, tick text, panel marks, annotations, and concise
   human-readable text rather than raw internal slugs. Use `humanize_label()` from
   `agents/templates/figure_style.py` or an explicit translation map for
   source-derived variable, feature, model, cohort, and metric names. Use
   `apply_research_arena_figure_style()` and, when possible,
   `save_research_arena_figure()` from the same template so all in-figure text
   uses one article-sized value and bars, lines, dots, axes, ticks, legends, and
   annotations are scaled for final article insertion.
   This shared helper is a visual-style utility only. It must not determine the
   number, names, order, or concepts of figures, and it must not be used as a
   shared `write_figures()` scaffold. Before or while plotting main-text display
   items, write `display_item_plan.md` using
   `agents/templates/display_item_plan.md`; justify any common plot form as a
   field convention, direct issue response, or researcher-specific claim need.
9. Link each major claim to either `results.json`, a figure/table artifact, or a
   cited source.
10. Do not hide failed verification or weak evidence in prose.
11. Keep manuscript prose separate from review-process artifacts. Use
    `revision_plan.md`, `revision_response.md`, issue ledgers, and verification
    matrices to answer Referees, the Integrity Checker, and the Editor. Do not use
    `manuscript.md` to answer gatekeeper questions directly.
12. Write each `manuscript.md` as a standalone final article for human readers,
    not as a memo about the review process. Avoid process-oriented framing such as
    announcing what a revision added, answering reviewers in the manuscript body,
    or citing internal issue ledgers and verification matrices as if they were
    scientific evidence. Convert that material into ordinary article prose about
    the analysis, methods, results, limitations, data/code availability, or
    reproducibility instead.
13. When review changes the evidence, revise the manuscript claim, interpretation,
    limitation, novelty argument, or Methods text directly. Adding a new table or
    figure without updating the manuscript is not a complete revision.
14. The final manuscript should not merely list newly added artifacts. It should
    explain how the evidence changes, weakens, narrows, or supports the central
    claim.
15. Follow `runs/<run-id>/manuscript_quality_contract.md`. A small empirical study
    may justify a shorter article type, but it still needs clear background,
    rationale, detailed Methods, formal model/statistical definitions when relevant,
    human-readable figures and tables, and a professional manuscript layout.
16. Do not export `manuscript.pdf` as a raw Markdown dump with visible `#` headings,
    backticks, unrendered table syntax, broken wrapping, or monospace-only formatting
    unless the run is explicitly a compact non-publication demo and the
    manuscript-quality contract permits it.
17. Use organized section and subsection headings. Results and Methods should have
    informative subtitles rather than long undivided blocks of prose.
18. Use the bundled open-source Inter family in `assets/fonts/inter/` for
    manuscript and figure text by default. TeX Gyre Heros, Nimbus Sans, Liberation
    Sans, Noto Sans, Source Sans 3, and Source Sans Pro are acceptable deliberate
    alternatives. Do not declare PDF base Helvetica or Arial as the
    accepted-manuscript font.
19. Number every displayed mathematical expression and write it in valid LaTeX.
    Prefer `equation`, `align`, `gather`, or `multline` environments with
    `\label{eq:...}`. Bare `$$ ... $$` or `\[ ... \]` display math is acceptable
    only if the renderer gives it a visible equation number and the style manifest
    documents that policy. The final `manuscript.pdf` must show rendered notation,
    not raw strings such as `\begin{equation}`, `\hat{p}`, `\frac{...}{...}`, `$$`,
    or `\[...\]`.
20. Create `manuscript_style_manifest.md` in each revision when the
    manuscript-quality contract requires it. State line-number status, manuscript
    font family, figure font family, equation-numbering status, math-rendering
    status, PDF renderer, render-toolchain report path, visual PDF review, figure
    typography review, and known style limits.
21. Use `agents/templates/render_manuscript_pdf.py` for Markdown manuscript PDFs.
    Its default `--engine auto` path prefers Pandoc/XeLaTeX for manuscripts with
    equations. If TeX rendering is unavailable, use `--engine matplotlib` or
    another fallback renderer only when the run has been explicitly downgraded or
    the manuscript-quality contract sets `allow_fallback_renderer: true`;
    disclose that limitation rather than printing raw LaTeX math as ordinary text.
    For serious-pilot and full-research runs, build `article/article.pdf` in
    every revision with `tools/build_article_pdf.py` unless the contract
    explicitly opts out for a compact/demo/internal run; keep `manuscript.pdf` as
    the line-numbered review manuscript and keep figures/tables separately
    inspectable. Each
    included figure and table should have a short explanatory paragraph directly
    paired with its title. Run `tools/figure_presentation_audit.py <revision-dir>
    --write` after building an article with figures, and revise figures if the
    audit flags inconsistent source text sizes or unreadable article-effective
    scaling.
22. Translate internal variable, feature, and model names into labels a human reader
    can understand. Raw slugs may appear only when paired with human-readable
    explanations in the artifact, manuscript, and display-item explanation file.
23. Each revision must include `presentation_checklist.md` with
    `status: pass` or `status: fail`, evidence paths, word counts, display-item
    counts, PDF visual status, figure/table readability status, and
    display-item explanation status, display-item narrative status,
    display-item plan status, figure text-size normalization status,
    figure mark-scale status,
    raw-label translation status, math/method-detail status, line-number status,
    equation-numbering status, math-rendering status, human-readable output
    package status, manuscript typography status, figure typography status,
    render-toolchain status, and integrated article PDF status.
    A Researcher-authored pass remains subject to
    Referee, Integrity Checker, and Editor verification.
24. Each latest revision with main-text figures or tables must include
    `display_item_plan.md` using `agents/templates/display_item_plan.md`. The plan
    must explain the Researcher's display strategy, claim role for each item,
    alternatives considered, and any similarity to other Researchers' display
    programs. Similar typography from `figure_style.py` is acceptable; similar
    figure concepts, filenames, order, or plotting structure need a
    researcher-specific rationale and may require LLM-backed display-program
    independence review.
25. Each latest revision must include `display_item_explanations.md` using
    `agents/templates/display_item_explanations.md`. The manuscript itself must
    include a dedicated `Figure And Table Guide`, `Display Item Interpretation`, or
    equivalent section that explains every figure and table: purpose,
    axes/rows/columns, labels, legends, colors, panels, annotations, units or
    denominators, sample size, summary conclusion, and caveat. If
    `article/article.pdf` is required, include an `Article Explanation` field for
    each display item: one concise paragraph that can appear directly under the
    figure/table title in the integrated article. For every figure, include an
    `Article group` decision and `Article grouping rationale`; use `standalone`
    when it should remain separate, or a shared group id with `Panel label`,
    `Panel title`, `Article group title`, and `Article group explanation` when
    related figures should become one multi-panel article figure.

## Revision Response And Issue Ledger

1. Maintain or update `issue_ledger.md` and, when possible, `issue_ledger.json` in
   the submission revision folder.
2. Every prior issue must retain its ID, for example `R1-MAJOR-02`.
3. `revision_response.md` must include, for each open or partially resolved issue:
   - issue ID;
   - Referee or Integrity Checker source;
   - severity;
   - direct reviewer question, if one was asked;
   - answer to that question;
   - action taken;
   - exact evidence path and, where possible, line/table/figure reference;
   - manuscript change made, or a reason no manuscript change was needed;
   - proposed lifecycle status: `response_submitted`, `verified_resolved`,
     `partially_resolved`, `unresolved`, `editorial_risk_accepted`, or `superseded`.
4. Do not mark an issue resolved unless the required evidence and acceptance
   criterion have both been satisfied.
5. If a requested experiment is infeasible, explain why, provide the closest
   feasible substitute, and keep the issue open or partially resolved for referee
   verification.
6. Maintain `verification_matrix.csv` or `verification_matrix.json` with one row per
   issue and direct question. The Researcher may set `author_claim` and
   `evidence_path`, but `reviewer_checked=true` and final `verification_status`
   must be set only by the owning Referee or Integrity Checker.
7. Do not delete unresolved issues from earlier rounds. Supersede them only when
   the owning Referee or Editor explicitly accepts the replacement issue.

## Researcher 2 Emphasis

Researcher 2 should look for compact comparative or composite ideas, but must still
build a complete empirical program when the article type requires it. Favor
comparison, transfer, robustness, or representation-learning stories only when the
submitted evidence can genuinely support them.
