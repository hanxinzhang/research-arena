# Research Arena Agent Instructions

This repository is an LLM-native research community protocol. This file is named
`AGENTS.md` for compatibility with agentic coding tools that read it automatically;
Codex, Claude, or another file-aware LLM agent can follow the same protocol.

When a user asks to run Research Arena:

1. Read `program.md` first.
2. Read each participating agent folder under `agents/`:
   - `config.json`
   - `profile.md`
   - `rules.md`
   Include all Researchers and Referees explicitly named by the user. The default
   pre-analysis gatekeeper is `study_design_board`, and the default reviewer set is
   `referee_1`, `referee_2`, `referee_3`, and `referee_4`.
3. Treat the dataset as a shared resource, not as a shared target. Researchers may
   study different bounded questions from the same data.
4. Declare the run's venue/article-type contract, study-design contract,
   research-depth contract, manuscript-quality contract, compute budget,
   agent-independence plan, and editor-gate plan before Researchers begin.
   Use `agents/templates/compute_budget.md` or an equivalent JSON schema so the
   budget includes parseable `minimum_cpu_core_hours_per_researcher`,
   `target_cpu_core_hours_per_researcher`, and
   `minimum_experiment_rows_per_researcher` fields.
   Also run `python tools/check_render_toolchain.py --run-id <run-id>
   --write-default` before manuscript acceptance whenever the manuscript-quality
   contract has `require_rendering_toolchain: true`.
5. Create run artifacts under `runs/<run-id>/`, `submissions/<run-id>/`,
   `human_readable_outputs/<run-id>/`, `work_packets/<run-id>/` when prompt packets
   are used, `agents/<agent-id>/workspace/<run-id>/`, and the final clean handoff
   under `outputs/<run-id>/` after post-decision verification. Initialize
   `runs/<run-id>/event_log.jsonl` and append an entry whenever an agent writes a
   proposal, analysis, review, audit, revision response, or editorial decision.
6. Do not require an API key, package install, or Python command to start the
   protocol. The user starts the protocol by prompting their chosen LLM agent in
   this repository.
7. Use Python or Anaconda only as a local analysis/artifact tool when needed.
8. Use Python for generated analysis code by default, unless the user explicitly
   requests another language.
9. Keep manuscript PDFs visually readable as line-numbered manuscripts. Text-only
   PDFs are allowed, but raw Markdown dumps with visible markup or monospace-only
   formatting fail the presentation gate unless the run is explicitly a compact
   non-publication demo and the manuscript-quality contract allows it. Use clear
   section/subsection hierarchy, numbered and visibly rendered LaTeX display
   equations when relevant, rendered inline math spans, open-source
   sans-serif typography for manuscript text, and LaTeX-like serif math. Prefer
   Pandoc/XeLaTeX for serious-pilot and full runs; fallback rendering is allowed
   only when the run contract explicitly sets `allow_fallback_renderer: true` and
   the limitation is disclosed in `known_style_limits`. Use the bundled Inter
   family in `assets/fonts/inter/` by default; TeX Gyre Heros, Nimbus Sans,
   Liberation Sans, Noto Sans, Source Sans 3, or Source Sans Pro are acceptable
   deliberate alternatives. Put figures and tables in separate artifact folders,
   and use PDF figure files with the same readable font policy. Figure typography
   must be article-native: titles, subtitles, axis labels, tick labels, legends,
   annotations, and colorbar labels should use one shared text size close to the
   article body text, with marks, bars, dots, lines, and error bars scaled for the
   same final article size. Avoid per-element `fontsize` overrides unless they
   preserve that one-size policy and are disclosed in the presentation checklist.
   SVG is optional.
   Manuscripts must include a figure/table guide explaining the purpose, labels,
   legends, annotations, conclusions, and caveats for every submitted display item.
   For serious-pilot and full-research runs, each revision must include an
   integrated journal-style PDF at `article/article.pdf` unless the contract
   explicitly opts out for a compact/demo/internal run. Each included figure and
   table must visibly pair its title with a short explanatory paragraph written as
   ordinary article prose. Build it with `tools/build_article_pdf.py`; do not
   replace `manuscript.pdf`, and keep the standalone `figures/` and `tables/`
   artifacts.
   Manuscript prose must read as a standalone article, not as a response memo,
   changelog, or direct answer to reviewer/gatekeeper questions. Put issue-by-issue
   answers in `revision_response.md`; integrate review-driven changes into the
   article's Methods, Results, Discussion, Limitations, or reproducibility prose.
10. Count figure concepts, not duplicate formats. If a figure is exported in
   multiple formats, it is still one display item.
11. Agents may use the internet for recent relevant literature, methods, and style
   references when the user permits browsing or when the LLM agent has browsing
   available. Cite sources with enough information for a human to find them.
12. Researchers must generate original ideas and writing. They may cite and build
   on published work, but they must not plagiarize text, figures, tables, code, or
   research framing.
13. Do not paste private/local data into internet searches or third-party websites.
14. Researchers should keep a source/literature note and a pre-results analysis plan
   for each submission.
15. Before `revision_00/`, Researchers must create a `proposal_gate/` folder with
    Phase 0 data familiarization and pilot artifacts:
    `data_familiarization.md`, `pilot_study_plan.md`,
    `pilot_study_results.json`, `pilot_compute_log.csv` or `.json`,
    `pilot_lessons.md`, then `candidate_studies.md`, `selected_proposal.md`, and
    `compute_budget_estimate.md`. Candidate studies must be written after the
    pilot, not before it. The Study Design Board must review the selected proposal
    and write `runs/<run-id>/proposal_gate_summary.md`. No Researcher may write
    full `analysis.py`, run full empirical analysis, create `results.json`, or
    draft a manuscript until the active proposal is approved for analysis or
    explicitly downgraded with updated run contracts.
    Compute estimates must show measured arithmetic from pilot timing; large
    unmeasured components and full-run proposals below 80% of the compute target
    require proposal revision, article-type downgrade, or run-budget revision
    before analysis.
16. Researchers must create a first-submission dossier in `revision_00/` after
    proposal-gate approval:
    `research_dossier.md`, `eda_report.md` or `eda_report.ipynb`,
    `model_or_method_cards.md`, an experiment registry, a compute log, and
    standalone analysis code.
17. Researchers must include `presentation_checklist.md` in each latest revision,
    with manuscript and Methods word counts, display-item count, PDF visual check,
    figure-label check, table-readability check, math/method-detail check,
    display-item plan check, display-item explanation check, raw-label translation check, line-number check,
    equation-numbering check, math-rendering check, human-readable output package
    check, manuscript typography check, figure typography check, render-toolchain
    check, and known presentation limits.
    Latest revisions must also
    include `display_item_plan.md`, `display_item_explanations.md`, and
    `manuscript_style_manifest.md` when
    required by the contract. `display_item_plan.md` must explain why each
    main-text display item was selected, what alternatives were considered, and
    whether similarities with other Researchers' display programs are style-only,
    standard convention, justified replication, or possible overconvergence.
    `display_item_explanations.md` must map every figure and table to the
    manuscript discussion, translate raw labels, and summarize the conclusion and
    caveat. Use
    `agents/templates/presentation_checklist.md`,
    `agents/templates/display_item_plan.md`,
    `agents/templates/display_item_explanations.md`,
    `agents/templates/manuscript_style_manifest.md`,
    `agents/templates/manuscript_template.tex`, and
    `agents/templates/render_manuscript_pdf.py`, and
    `agents/templates/figure_style.py` as backend defaults when useful. The figure
    style helper may standardize typography, label humanization, line widths,
    marker sizes, grids, and saving; it must not supply a default figure concept
    list, filename pattern, panel order, or shared `write_figures()` program. Run
    `tools/figure_presentation_audit.py` on each revision when figures are
    included in `article.pdf`; a passing figure presentation audit is required
    before the article presentation gate can pass. Use
    `tools/package_human_readable_outputs.py` before acceptance to create
    `human_readable_outputs/<run-id>/<submission>/<revision>/` packages with
    `manuscript.pdf`, `figures/`, `tables/`, and `source_code/`.
18. Each Researcher must work in its own workspace before initial submission.
    Shared utilities must be declared, and publication submissions must not rely on
    thin wrappers around a hidden central generator.
    Do not use a central script, notebook, or prompt template to generate multiple
    roles' scientific artifacts. If orchestration is useful, generate role-specific
    inputs with `python tools/create_work_packets.py <run-id> --phase all`, then
    run each LLM-backed role turn from its own packet and allowed artifacts.
    Shared visual styling alone is not an independence violation, but shared
    figure concepts, filenames, order, or plotting structure without
    researcher-specific rationale are process-risk evidence. Resolve disputed
    cases with `audits/display_program_independence_rubric.md`.
19. Treat generated analysis scripts as untrusted until inspected. Do not put
    network calls, secrets, private paths, shell-based destructive operations, or
    hidden external dependencies in generated research code.
20. Keep all claims exploratory unless a stronger claim is explicitly justified by
    the submitted evidence and the integrity check.
21. Do not use revision number as an artifact schedule. New analyses, tables,
    figures, citations, or manuscript changes must be justified by open issues,
    reviewer questions, integrity findings, or editor guidance.
22. Before creating any `revision_01/` or later folder, require a
    `revision_plan.md` that maps open issues to proposed evidence, expected
    artifacts, compute needs, `revision_type`, empirical provenance, and
    stop/downgrade criteria. The plan must also declare `research_delta_tier`
    as `tier_a_material`, `tier_b_supporting`, or `tier_c_nonmaterial` and state
    whether `material_research_delta.md` will be created. Do not continue a
    revision whose plan only repackages unchanged evidence while central empirical
    issues remain open.
23. Require each revised submission to include a verification matrix
    (`verification_matrix.csv` or `verification_matrix.json`) covering every issue
    and direct reviewer question, plus a canonical issue ledger using reviewer-owned
    lifecycle statuses.
24. Before final editorial decision, run or manually reproduce the deterministic
    clerk checks described in `program.md`: research-depth structure,
    review-similarity, revision trajectory when applicable, artifact authority,
    run-state order, archive hygiene, and scripted-generation risk. Treat these
    outputs as evidence tables, not scientific judgments.
25. Use the LLM-backed rubrics under `audits/` for scientific depth,
    revision-trajectory, novelty/article-fit, reviewer-quality, manuscript
    article-voice, display-item narrative, and display-program independence
    judgments.
26. Treat trajectory-clerk process warnings as blocking process-risk evidence until
    the Editor resolves them in writing. In particular, a later revision with
    `prior_review_event_status=prior_review_after_revision_started` is not a true
    issue-linked revision, and `analysis_change_kind=revision_marker_only` is not
    by itself substantive empirical improvement. Unchanged primary metrics and flat
    compute while central issues remain open are also not evidence of a stronger
    study. These signals should usually require rerunning the round in the correct
    order, rewriting the revision plan after real reviews, downgrading the article
    type, or rejecting.
27. Before writing `runs/<run-id>/final_decision.md`, create
    `runs/<run-id>/pre_decision_freeze_manifest.json` with
    `python tools/freeze_run.py <run-id> --stage pre-decision`. The
    final-decision event must cite that manifest as an input. After the final
    decision and final event-log entry, create and verify
    `runs/<run-id>/post_decision_archive_manifest.json` with
    `python tools/freeze_run.py <run-id> --stage post-decision`. No research,
    review, audit, package, or work-packet artifact may be written after final
    decision unless the Editor explicitly reopens the run and invalidates the stale
    decision.
28. After post-decision archive verification, create and verify a clean final
    handoff bundle with
    `python tools/finalize_run_outputs.py <run-id> --replace --cleanup-source-roots`
    and `python tools/finalize_run_outputs.py <run-id> --verify`. The bundle under
    `outputs/<run-id>/` is the user-facing entry point: `human_readable_outputs/`
    contains final reading artifacts, and `diagnosis_process_files/` contains run
    records, submissions, work packets, and agent workspaces. Completed runs should
    not leave duplicate run-specific source folders in the project root after the
    bundle verifies.

## Interaction Rules

1. Every revision must be based on actual interactions between agents.
2. Do not create deterministic or prewritten recommendations between Researchers,
   Referees, the Integrity Checker, or the Editor.
3. Do not accept or reject because a round number was reached.
4. Referees must read the artifacts and produce structured, evidence-linked reviews.
5. Every Referee or Integrity Checker request must have an issue ID, severity,
   required evidence, acceptance criterion, and status.
6. Researchers must answer every open or partially resolved issue in
   `revision_response.md`, citing exact files, tables, figures, or lines.
7. Referees own only their own issue IDs (`R1-*` for `referee_1`, `R2-*` for
   `referee_2`, etc.). They may mention other issues as context but must not
   resolve or summarize them as their own concerns.
8. Every major or blocking concern must cite a concrete artifact path, the exact
   missing evidence, and the evidence that would change the Referee's or Editor's
   judgment. Generic criticism is not sufficient.
9. Every Referee review must include "what changed since the previous revision,"
   direct questions for the Researcher, and an assessment of prior answers when
   applicable.
10. Follow-up Referees must verify the cited evidence before marking an issue
   `verified_resolved` and must write the result into both the canonical issue
   ledger and verification matrix.
11. Manuscript revisions must update claims, limitations, interpretation, novelty,
    or method text when review changes the evidence, not only list new artifacts.
12. Central empirical, novelty, or article-fit blockers cannot be resolved by
    `tier_c_nonmaterial` revisions. They require material research-state change,
    a strong supporting-evidence package, formal article-type downgrade, or
    rejection.
13. Deterministic Python tools may summarize files, hashes, compute, paths, and
    textual similarity. They must not be treated as deciding novelty, scientific
    adequacy, or article-type fit.
14. The Editor/Publisher must make a gate-based decision using unresolved issues,
    verification-matrix status, proposal-gate status, integrity status,
    clerk evidence, artifact-authority status, state-order status, archive hygiene,
    scripted-generation status, LLM-backed scientific judgments,
    display-program independence judgment when relevant, novelty, evidence
    strength, presentation-gate status, independence, and article-type compliance.
