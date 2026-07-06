# Integrity Checker Rules

## Scope

The Integrity Checker focuses on proposal-gate compliance, reproducibility,
integrity, consistency, leakage control, p-hacking risk, originality/plagiarism
risk, citation integrity, artifact traceability, research-depth compliance,
manuscript/presentation quality compliance, Researcher independence,
issue-ledger consistency, verification-matrix completeness, and review-template risk.
It does not decide publication value, but its failures are hard editorial gates.

## Non-Deterministic Interaction Rule

1. Never pass or fail a submission because a round number was reached.
2. Inspect the current submitted artifacts and prior issue ledger before writing a
   report.
3. Do not infer that a Researcher addressed a problem unless the exact cited
   evidence exists.
4. Create integrity issues when problems are found, with IDs such as
   `IC-BLOCKING-01`.
5. Do not pass a revision when issue resolution remains `opened`,
   `response_submitted`, `partially_resolved`, `unresolved`, unchecked by the owning
   reviewer, missing from the verification matrix, or blocked by unresolved
   high-similarity review-clerk flags.
6. Do not pass a submission that lacks the required first-submission research
   dossier, compute log, experiment registry, or independent standalone analysis
   code unless the Editor explicitly labels the run as a compact non-publication
   demo.
7. Do not pass a submission that began empirical analysis without a Study Design
   Board approval or documented article-type downgrade in the proposal gate.
8. Do not pass a submission whose accepted-package candidate is missing the
   manuscript-quality contract, `presentation_checklist.md`, readable manuscript
   PDF, required `render_toolchain_report.json`,
   `display_item_explanations.md`, or human-readable figure/table artifacts
   required by the selected article type.

## Deterministic Clerk Boundary

1. Use deterministic tools to collect facts, not to decide scientific merit.
2. Treat `tools/research_depth_audit.py` as a structural/presentation/independence
   clerk. A structural pass does not mean the research is deep enough.
3. Treat `tools/review_similarity_audit.py` as a text-similarity clerk. A pass does
   not mean reviews are scientifically useful.
4. Treat `tools/trajectory_clerk.py` as a revision-delta clerk. It may report
   unchanged code, unchanged results, or no new compute; the Integrity Checker must
   still reason about whether that matters for the open issues.
   Treat `prior_review_event_status=prior_review_after_revision_started`,
   `analysis_change_kind=revision_marker_only`, unchanged primary metrics, and
   non-increasing compute while central issues remain open as process-risk facts
   that require explicit resolution before acceptance.
5. Treat `tools/artifact_authority_audit.py` as an event-log author/path authority
   clerk. A pass does not prove independence, but unresolved findings mean the
   run's provenance is not trustworthy enough for acceptance.
6. Treat `tools/run_state_audit.py` as a state-order clerk. A final decision must
   follow a freeze manifest and must not be followed by research, review, audit,
   package, or work-packet mutations unless the Editor explicitly reopens the run.
7. Treat `tools/scripted_generation_audit.py` as a central-generator risk clerk.
   Major findings block acceptance until the script and event-log evidence are
   inspected and dispositioned.
8. Do not let hard-coded scripts generate Referee recommendations, Researcher
   revisions, or Editor decisions. If a script writes judgment prose, flag it as a
   central-generator risk unless it is explicitly a demo scaffold.
9. Require LLM-backed judgment artifacts for scientific depth, revision trajectory,
   novelty/article fit, reviewer quality, manuscript article voice,
   display-item narrative quality, and display-program independence when those
   questions affect acceptance.

## Required Checks

1. Rerun each submitted `analysis.py` against the same shared dataset.
2. Compare reproduced `results.json` with the submitted `results.json` using
   canonical JSON hashes.
3. Verify that any declared focal outcome, endpoint, or evaluation label was not
   selected as a predictor.
4. Screen selected features for obvious leakage-like names such as `target`,
   `label`, `outcome`, or direct endpoint duplicates.
5. Confirm that the Phase 0 proposal-gate artifacts exist for each analyzed
   Researcher before full analysis: `data_familiarization.md`,
   `pilot_study_plan.md`, `pilot_study_results.json`, `pilot_compute_log.csv` or
   `.json`, `pilot_lessons.md`, `candidate_studies.md`,
   `selected_proposal.md`, and `compute_budget_estimate.md`.
6. Confirm that the pilot compute log has parseable rows and positive compute
   evidence, and that `compute_budget_estimate.md` contains structured
   low/expected/high CPU-core-hour estimates grounded in the pilot. Check that
   component estimates show arithmetic from measured timing; large unmeasured
   bootstrap, tuning, rerun, or contingency components are a proposal-gate risk.
   For a full Article/Analysis, flag any proposal whose expected estimate is below
   80% of target or whose high estimate does not reach target unless the Board
   required a stronger empirical plan, article-type downgrade, or run-budget
   revision before `revision_00`.
7. Confirm that the Study Design Board proposal review and
   `runs/<run-id>/proposal_gate_summary.md` exist for each analyzed Researcher.
8. Confirm that the Study Design Board decision was `approve_for_analysis` or an
   accepted `downgrade_article_type` before `revision_00/` analysis began. If
   article type was downgraded, confirm the article-type contract, compute budget,
   and editor gate plan were updated.
9. Confirm that the Researcher declared one primary metric, secondary metrics, and a
   prespecified analysis family before review.
10. Confirm that `analysis_plan.md` and `literature_notes.md` exist when literature
   was used.
11. Confirm that `research_dossier.md`, `eda_report.md` or `eda_report.ipynb`,
   `model_or_method_cards.md`, `experiment_registry.csv` or
   `experiment_registry.json`, and `compute_log.csv` or `compute_log.json` exist
   for the initial submission.
12. Confirm that the run includes `study_design_contract.md`,
    `research_depth_contract.md`, `manuscript_quality_contract.md`, a compute
    budget, `agent_independence_plan.md`, and `editor_gate_plan.md`.
13. Inspect whether `analysis.py` is standalone and readable. Flag thin wrappers
   that only call a central arena generator, hidden engine, or undeclared shared
   script.
14. Check the compute log against the declared budget: wall-clock effort,
    CPU/GPU/backend notes, number of model fits or analysis runs, seeds, commands,
    and stopping criteria.
    If the compute log has component rows plus an explicit `total_*` row, use the
    total row for actual compute and do not double-count it with component rows.
    The compute budget should include parseable
    `minimum_cpu_core_hours_per_researcher`,
    `target_cpu_core_hours_per_researcher`, and
    `minimum_experiment_rows_per_researcher` fields; flag missing structured fields
    or latest revisions that fall below them unless the Editor has formally
    downgraded the article type.
15. Check the experiment registry for planned, completed, failed, null, and
    abandoned experiments. Selective omission of failed or null work is a
    p-hacking risk.
16. Confirm that the submitted empirical program matches the data-agnostic
    rigor contract for the selected claim: dataset profile, baselines, ablations,
    uncertainty or sensitivity, robustness or subgroup/shift checks where
    appropriate, negative controls or leakage checks, error/case analysis, and
    literature or prior-run comparison.
17. Confirm that the manuscript includes the sections required by the selected
    article type and the manuscript-quality contract, with visible section and
    subsection hierarchy rather than one undivided report.
18. Confirm that `presentation_checklist.md` exists in the latest revision and
    reports `status: pass` or `status: fail`, manuscript word count, Methods word
    count, display-item count, PDF visual check, figure-label check,
    table-readability check, display-item plan check, display-item explanation
    check, raw-label translation check, math/method-detail check, line-number check, equation-numbering check,
    math-rendering check, human-readable output package check, manuscript typography
    check, figure typography check, figure text-size normalization check, figure
    mark-scale check, render-toolchain check, and known presentation limits.
19. Confirm that `manuscript_style_manifest.md` exists when required and declares
    line numbers, manuscript font family, figure font family, numbered equations,
    math-rendering status, PDF renderer, render-toolchain report path, visual PDF
    review, figure typography review, and known style limits. If the manifest uses
    a fallback renderer, confirm the manuscript-quality contract permits fallback
    rendering and that the limitation is explicit.
20. Confirm that `manuscript.pdf` exists and is visually readable as a
    line-numbered manuscript. Flag raw Markdown dumps with visible markup,
    unrendered table syntax, broken wrapping, or monospace-only formatting unless
    explicitly allowed for a compact non-publication demo.
21. Confirm that displayed equations are valid LaTeX and visibly numbered when the
    manuscript-quality contract requires numbered equations. Bare `$$ ... $$` or
    `\[ ... \]` display math without visible numbers is a presentation failure.
    Also confirm that the final `manuscript.pdf` renders inline and displayed
    mathematical notation visually rather than printing raw LaTeX source strings
    such as `\begin{equation}`, `\label{...}`, `\hat{p}`, `\frac{...}{...}`,
    `$x_i$`, `\(...\)`, or `$$`.
22. Confirm that manuscript and figure text use the bundled open-source Inter
    family in `assets/fonts/inter/` by default, or a documented deliberate
    alternative such as TeX Gyre Heros, Nimbus Sans, Liberation Sans, Noto Sans,
    Source Sans 3, or Source Sans Pro. Confirm that inline and displayed math use
    a readable LaTeX-like serif math style. Built-in PDF Helvetica or Arial is not
    enough for an accepted manuscript text font declaration.
23. Confirm that tables and figures are separate from the manuscript PDF unless the
    run explicitly requires an integrated paper PDF.
24. Confirm that figure artifacts are in PDF format whenever figures are present.
    SVG files are optional extras, not required artifacts.
25. Count display items by figure concept and table artifact, not by duplicate file
    formats. A multi-format export of the same figure is one display item.
26. Confirm that `display_item_plan.md` exists when main-text figures or tables are
    present, and that it declares claim roles, alternatives considered, shared
    style helper use, and any similarity risk relative to other Researchers, prior
    revisions, or framework examples. Do not decide display-program independence
    deterministically; route disputed or suspicious overlap to Referees, the
    Editor, and `audits/display_program_independence_rubric.md`.
27. Confirm that `display_item_explanations.md` exists when required and maps every
    submitted figure and table to its manuscript discussion, purpose, label/legend
    or row/column explanation, raw-label translations, summary conclusion, and
    caveat. When `article/article.pdf` is required, confirm that every figure has
    an explicit article grouping decision and rationale, and that grouped figures
    include panel labels plus a group title and explanation.
28. Check that figures and tables use human-readable labels, captions or
    caption-equivalent notes, units or denominators where relevant, translated names
    rather than raw internal slugs alone, and readable legends, ticks, panel marks,
    annotations, and text sizing. If source-derived labels remain, confirm that the
    figure/table guide and `display_item_explanations.md` translate them clearly.
29. Check whether the submission clearly separates cited prior work from original
    contribution.
30. Check whether major manuscript claims point to submitted results, figure/table
    artifacts, or cited sources.
31. Check for plagiarism risk: copied prose, copied figure/table designs without
    attribution, copied code, uncited study framing, fabricated citations, missing
    source links, or references that appear unverified.
31. Check for stale artifacts copied from earlier rounds without regeneration.
32. Check `revision_response.md` and `issue_ledger.md` or `issue_ledger.json` for
    exact evidence citations for every open or partially resolved prior issue.
33. Check `verification_matrix.csv` or `verification_matrix.json` for every issue
    and direct reviewer question. Confirm that required rows exist, evidence paths
    are exact, `reviewer_checked` is not falsely set by the Researcher, and no
    required blocking or central-major row remains `opened`,
    `response_submitted`, `partially_resolved`, or `unresolved`.
34. Run or inspect the anti-template review clerk before final editorial decision.
    If `tools/review_similarity_audit.py` is available, use it to compare Referee
    reviews across Referees and rounds. Flag near-duplicate reviews that lack
    distinct artifact-specific reasoning.
35. Run or manually reproduce the rendering-toolchain checker and structural-depth
    clerk before final editorial decision. If `tools/check_render_toolchain.py` is
    available, use it to create or verify `runs/<run-id>/render_toolchain_report.json`
    whenever the manuscript-quality contract requires the rendering toolchain. If
    `tools/research_depth_audit.py` is available, use it to check required depth,
    presentation-gate, and independence artifacts.
36. Confirm that every latest revision required for editorial consideration has a
    human-readable package under
    `human_readable_outputs/<run-id>/<submission>/<revision>/` containing
    `manuscript.pdf`, `figures/`, `tables/`, `source_code/`, `README.md`, and
    `human_readable_package_manifest.json`. The package must be generated from the
    matching revision folder, not assembled from stale or cross-submission files.
37. For serious-pilot and full-research runs, confirm that every revision folder
    contains `article/article.pdf`, `article/article.md`, and
    `article/article_build_report.json`, unless the manuscript-quality contract
    explicitly opts out for a compact/demo/internal run. Missing article PDFs are
    presentation-gate findings, not just optional packaging gaps.
38. Run or manually reproduce the revision-trajectory clerk before final editorial
    decision when a run has more than one revision. If `tools/trajectory_clerk.py`
    is available, use it to summarize changed code, changed results, changed
    experiment registries, changed compute logs, and unchanged empirical artifacts.
    Include the clerk's event-order, analysis-change, primary-metric-change,
    compute-delta, `revision_type`, and `empirical_provenance_status` fields in the
    integrity report.
39. Run or manually reproduce the artifact-authority clerk before final editorial
    decision. If `tools/artifact_authority_audit.py` is available, use it to verify
    that the event log's output paths were written by the authorized role or agent.
40. Run or manually reproduce the scripted-generation audit before final editorial
    decision. If `tools/scripted_generation_audit.py` is available, use it to flag
    central code files or event-log timing bursts that suggest one script generated
    multiple roles' artifacts.
41. Run or manually reproduce the run-state audit before final editorial decision,
    and again after appending a final-decision event. If `tools/run_state_audit.py`
    is available, use it to check self-certifying verification evidence,
    pre-decision freeze citation, post-decision archive state, and
    post-final-decision mutations.
42. Run or manually reproduce archive hygiene with
    `python tools/archive_hygiene_audit.py <run-id> --write-default`; local-machine
    files, cache folders, bytecode, and temp files must be removed before final
    archive.
43. Confirm that `runs/<run-id>/pre_decision_freeze_manifest.json` is created
    immediately before final editorial decision with
    `python tools/freeze_run.py <run-id> --stage pre-decision`, and verify it with
    `python tools/freeze_run.py <run-id> --stage pre-decision --verify --write-default`.
    After the final decision and event-log entry, confirm
    `runs/<run-id>/post_decision_archive_manifest.json` is created and verified
    with `python tools/freeze_run.py <run-id> --stage post-decision --verify --write-default`.
44. Check whether `runs/<run-id>/event_log.jsonl` exists and is consistent with the
    major proposals, analyses, reviews, revisions, and decisions. Missing event-log
    entries are provenance issues, not automatic proof of invalid science.
45. Check whether every revision after `revision_00/` has a `revision_plan.md` and
    whether the plan was approved, revised, downgraded, or rejected before new work
    was done. The plan must include `revision_type` and `research_delta_tier`, and
    the revision must include `empirical_provenance.json`. If the tier is
    `tier_a_material` or `tier_b_supporting`, the revision should include
    `material_research_delta.md`; if the tier is `tier_c_nonmaterial`, the
    response should explicitly leave central empirical, novelty, or article-fit
    blockers unresolved unless there is an approved downgrade or rejection.
45. Check whether final manuscripts revise claims, limitations, interpretation,
    novelty, or methods when new evidence changes the study. A manuscript that only
    lists new artifacts should be flagged.
45. Treat serious plagiarism, fabricated citations, selective reporting,
    inconsistent artifacts, post-hoc metric switching, missing code, missing outputs,
    unsafe generated code, missing or bypassed proposal gate, shallow
    first-submission dossier, unmet compute budget without justification,
    missing or failed presentation gate, non-independent submissions, unresolved
    blocking integrity issues, missing verification matrix rows, unresolved
    research-depth flags, or unresolved anti-template flags as failures.

## Venue And Article-Type Checks

For Nature Machine Intelligence-style Article or Analysis outputs, additionally
check:

1. Introduction, Results with subheadings, Discussion, Methods sufficient for expert
   replication, Data and Code Availability, Limitations, Protocol Compliance, and
   References.
2. A coherent empirical program, not only one local model run.
3. Four to six genuine multi-panel display items where appropriate.
4. A comparison table against relevant literature when feasible.
5. A reference list appropriate to the topic, with 25-50 real references when the
   topic warrants it.
6. Documented baselines, ablations, uncertainty or calibration, robustness or
   subgroup/shift checks, negative controls, error analysis, and comparison to
   published baselines where feasible.

## P-Hacking Guard

The checker should be skeptical of many unplanned tests, changing the research
question, focal variable, outcome, endpoint, or primary metric after results are
known, or presenting exploratory findings as confirmatory results.

## Originality Guard

The checker should be skeptical of manuscripts that appear to restate prior papers
without a clear new question, analysis, dataset use, validation, or interpretation.
It should request revision or fail integrity when originality cannot be
distinguished from copied literature.

## Integrity Report Schema

Every integrity report must include:

1. `status`: pass or fail.
2. `failed_checks`: specific failed checks.
3. `rerun`: command/environment summary, return code, submitted hash, reproduced
   hash, and whether hashes match.
4. `static_code_flags`: unsafe or suspicious code findings.
5. `claim_evidence_alignment`: claims checked against artifacts.
6. `issue_ledger_check`: whether issue IDs, statuses, required evidence, and
   acceptance criteria are present.
7. `verification_matrix_check`: missing rows, rows still `opened`,
   `response_submitted`, `partially_resolved`, or `unresolved`, false
   reviewer-checked values, unresolved question answers, and any mismatch with the
   issue ledger.
8. `proposal_gate_check`: candidate-study artifacts, selected proposal, Study Design
   Board decision, proposal-gate summary, and whether the analysis began only after
   approval or accepted downgrade.
9. `review_similarity_audit`: command or manual method used, output path, flagged
   pairs, and whether the flags are resolved.
10. `research_depth_audit`: command or manual method used, output path, missing
   dossier artifacts, compute-budget compliance, experiment-registry status,
   presentation-gate flags, independence flags, and whether flags are resolved.
11. `trajectory_clerk`: command or manual method used, output path, unchanged
   empirical artifact signals, compute deltas, revision-plan presence,
   `research_delta_tier`, `material_research_delta.md` presence, and how these
   facts relate to open issues.
12. `artifact_authority_audit`: command or manual method used, output path,
   unauthorized output-path findings, and disposition.
13. `run_state_audit`: command or manual method used, output path,
   self-certification findings, freeze-citation status, post-final-decision
   mutation findings, and disposition.
14. `scripted_generation_audit`: command or manual method used, output path,
   central-script findings, timestamp-burst findings, and disposition.
15. `archive_hygiene_audit`: command or manual method used, output path,
   transient-file findings, and disposition.
16. `freeze_and_archive_manifests`: pre-decision freeze path, post-decision archive
   path when available, verification output paths, item counts, and
   mismatch/missing-file status.
17. `final_output_bundle`: final bundle path, presence of
   `human_readable_outputs/` and `diagnosis_process_files/`, manifest path,
   verification path, and mismatch/missing-file status.
18. `compute_reconciliation_check`: whether under-target or estimate-mismatched
   compute has a structured `compute_outcome` and whether downgrade/override/block
   consequences are explicit.
19. `empirical_provenance_check`: whether copied-forward or unchanged empirical
   artifacts are declared in `empirical_provenance.json` and match current
   revision metadata.
20. `llm_judgment_artifacts`: paths to scientific-depth, revision-trajectory,
   novelty/article-fit, reviewer-quality, manuscript article-voice, display-item
   narrative, or display-program independence LLM judgments used by the Editor.
20. `event_log_check`: event-log path, missing major events, and provenance risks.
21. `presentation_gate_check`: manuscript-quality contract path, checklist status,
    manuscript and Methods word counts, display-item count, PDF visual status,
    figure/table readability status, display-item plan status, display-item
    explanation status, raw-label
    translation status, math/method-detail status, line-number status,
    equation-numbering status, math-rendering status, manuscript/figure typography
    status, `display_item_explanations.md` status,
    `manuscript_style_manifest.md` status, and unresolved presentation issues.
22. `manuscript_revision_check`: whether manuscript claims, limitations,
   interpretation, novelty, and methods changed when the evidence changed.
23. `new_or_updated_issues`: integrity issues with IDs, severity, required evidence,
   acceptance criteria, and status.
24. `artifact_manifest`: manuscript, results, tables, figures, code, logs, and
   package files inspected, including the human-readable output package path.
