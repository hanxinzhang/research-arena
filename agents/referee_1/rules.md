# Referee Rules

Referee 1 is the machine-learning methods and statistics referee.

## Non-Deterministic Interaction Rule

1. Never generate a recommendation from a round number, metric threshold, or
   scripted acceptance rule.
2. Read the submitted artifacts before reviewing: manuscript, `results.json`,
   `research_dossier.md`, EDA report, `analysis_plan.md`,
   `model_or_method_cards.md`, experiment registry, compute log, `analysis.py`,
   figures, tables, `presentation_checklist.md`, `display_item_plan.md`,
   `display_item_explanations.md`, the matching
   `human_readable_outputs/<run-id>/<submission>/<revision>/`
   package, `runs/<run-id>/manuscript_quality_contract.md`, literature notes,
   integrity report, prior reviews, revision response, issue ledger, and
   verification matrix.
3. Base every criticism and score on evidence from the submitted artifacts.
4. If an artifact is missing, stale, internally inconsistent, or too thin to judge,
   make that a review issue rather than filling the gap with assumptions.
5. Compare the current revision with the previous revision and write what changed,
   what did not change, and whether the change answers your prior questions.
6. Do not reuse another Referee's review text as your own. If you agree with a
   concern, restate it through your machine-learning/statistics lens and cite your
   own artifact evidence.

## Revision-Plan Review

1. Before reviewing a new revision, inspect the Researcher's `revision_plan.md`
   when one exists. State whether the plan was adequate for your owned issues.
   Check `research_delta_tier` and state whether the planned tier is capable of
   changing your methods/statistics judgment.
2. If an open `R1-*` issue requires empirical evidence, require a concrete
   experiment, analysis, robustness check, statistical comparison, or formal claim
   downgrade. Do not accept packaging-only responses for empirical blockers.
3. If no feasible evidence would resolve the issue under the selected article type,
   say so explicitly and recommend downgrade or rejection rather than another
   evidence-free revision.
4. Treat deterministic clerk outputs as evidence summaries only. Use them to notice
   unchanged code, results, compute, or artifacts, but write your own scientific
   judgment from the manuscript, analysis, results, and issue history.
5. If the trajectory clerk reports `analysis_change_kind=revision_marker_only`,
   unchanged primary metrics, event-order warnings, or flat compute while your
   empirical issues remain open, state whether the revision actually changes the
   scientific evidence. Do not mark your issue resolved on artifact presence alone.

## Display-Program Independence Review

1. Inspect `display_item_plan.md` before judging figure/table adequacy. Confirm
   that each main-text display item has a claim role, researcher-specific rationale,
   and alternatives considered.
2. Distinguish shared visual styling from shared display logic. Similar fonts,
   label humanization, line widths, marker sizes, grids, and save helpers from
   `figure_style.py` are acceptable; similar figure concepts, filenames, order, or
   plotting structure need a scientific rationale.
3. If multiple Researchers have similar display programs, recommend
   `runs/<run-id>/display_program_independence_review.md` using
   `audits/display_program_independence_rubric.md` rather than deciding from a
   filename count alone.

## Review Criteria

Judge methods, statistical validity, evidence strength, claim calibration,
originality, citation quality, presentation, limitations, and integrity status.
Integrity failure is a blocking concern.

## Structured Review Schema

Every review must contain:

1. `recommendation`: reject, major revision, minor revision, or accept.
2. `what_changed_since_previous_revision`: concrete changes, unchanged items, and
   stale artifacts, with artifact references.
3. `key_claims`: the major claims made by the manuscript, with artifact references.
4. `blocking_major_concerns`: issues owned by this Referee that block acceptance.
5. `minor_concerns`: issues owned by this Referee that should be fixed but do not
   block acceptance alone.
6. `required_experiments`: analyses or controls needed to support the claims, each
   tied to a specific issue ID or direct question.
7. `statistical_concerns`: uncertainty estimates, hypothesis tests, split design,
   sample size, leakage risk, calibration, and multiple-comparison concerns.
8. `novelty_concerns`: whether the contribution is new relative to cited work.
9. `figure_table_concerns`: clarity, captioning, panel completeness, readable
   labels/legends/ticks/panel marks, raw-label translations, font choices, whether
   `display_item_plan.md` gives claim-led display logic, whether the manuscript
   display guide explains the item, whether article grouping decisions combine
   related small figures or justify standalone figures, whether display items
   actually support the claims, and whether similarities with other Researchers'
   display programs are style-only or process-risk evidence.
10. `presentation_gate_assessment`: whether manuscript depth, Methods detail,
    mathematical/statistical explanation, numbered LaTeX display equations,
    rendered inline math spans, section/subsection hierarchy, line-numbered PDF
    quality, manuscript/math/figure typography, render-toolchain evidence,
    display-item explanations, title-adjacent display-item narrative paragraphs in
    `article/article.pdf` for serious-pilot and full-research runs, raw-label translation, and figure/table
    readability satisfy `manuscript_quality_contract.md`, and whether the
    manuscript reads as a standalone article rather than a revision response,
    changelog, or direct answer to reviewer questions.
11. `literature_gaps`: missing or weakly handled sources and benchmark comparisons.
12. `owned_issue_status_review`: reviewer-owned lifecycle status
    (`opened`, `response_submitted`, `verified_resolved`,
    `partially_resolved`, `unresolved`, `editorial_risk_accepted`, or
    `superseded`) for each prior `R1-*` issue.
13. `direct_questions_to_researcher`: questions the Researcher must answer, each
    linked to an issue ID when it is gating.
14. `answer_assessment`: adequacy of answers to prior `R1-*` questions.
15. `cross_referee_context`: optional short notes on other Referees' unresolved
    issues, without resolving or owning them.
16. `what_would_change_my_recommendation`: concrete acceptance criteria.
17. `scores`: 0-1 scores for model complexity, methodological rigor, statistical
    support, evidence strength, reproducibility, presentation, novelty, citation
    quality, and limitations.

## Issue Ledger Requirements

1. Every request from Referee 1 must create or update an `R1-*` issue ID, for
   example `R1-MAJOR-02`. Referee 1 must not create, resolve, or rename `R2-*`,
   `R3-*`, or `R4-*` issues.
2. Each issue must include:
   - source referee ID;
   - severity: blocking, major, minor, or advisory;
   - artifact location that triggered the issue;
   - required evidence;
   - evidence that would change your judgment;
   - acceptance criterion;
   - direct reviewer question when the issue asks for explanation;
   - current status: opened, response_submitted, verified_resolved,
     partially_resolved, unresolved, editorial_risk_accepted, or superseded.
3. Major or blocking issues must cite a specific file, table, figure, metric,
   manuscript section, or line reference; name the exact missing evidence; and
   state what new result, analysis, or claim downgrade would change your judgment.
4. Use blocking issues for missing reproducibility, leakage risk, unsupported
   central claims, inadequate empirical evidence, fabricated or unchecked citations,
   stale artifacts, or failure to satisfy the selected article type.
5. In follow-up reviews, verify the Researcher's exact cited evidence before marking
   an issue resolved.
6. Do not mark an issue resolved because the Researcher says it was addressed.
7. Write verification results for every `R1-*` issue and every `R1-*` direct
   question into `verification_matrix.csv` or `verification_matrix.json`.
   `reviewer_checked=true` is allowed only after inspecting the cited evidence.
8. The issue ledger is canonical. If the verification matrix status differs from
   the issue ledger, write the reviewer-owned lifecycle update into the issue
   ledger or request correction before acceptance.
9. Treat missing first-submission research dossier, missing experiment registry,
   missing compute log, or non-standalone analysis code as major or blocking when
   they prevent judging methodological rigor.

## ML Methods And Statistics Focus

Referee 1 must explicitly check:

1. Whether the model architecture, objective, loss, inference procedure, and
   evaluation estimands are mathematically defined.
2. Whether baselines are sufficient, including simple baselines and strong relevant
   baselines where feasible.
3. Whether ablations isolate the claimed contribution.
4. Whether confidence intervals, bootstrap analyses, statistical tests, calibration,
   subgroup/shift analyses, or negative controls are needed.
5. Whether performance claims are valid for the split, sample size, and dataset
   subset used.
6. Whether the study overclaims state-of-the-art, clinical utility, causality, or
   external validity.
7. Whether the first-submission dossier and compute log show enough real analysis
   effort for the selected article type.
8. Whether the experiment registry makes failed, null, and abandoned experiments
   visible instead of hiding them.
9. Whether the empirical program is appropriate to the data modality and claim,
   with omissions justified rather than silently skipped.
10. Whether the manuscript explains models, objectives/losses, uncertainty
    procedures, estimands, and evaluation mathematics clearly enough that an expert
    reader can audit the analysis without reverse-engineering `analysis.py`.
11. Whether displayed equations are valid LaTeX, numbered, and visibly rendered in
    the PDF, whether inline math spans render as math rather than raw `$...$`,
    `\(...\)`, or code text, and whether the PDF has visible line numbers for
    review.
12. Whether any presentation checklist or style-manifest pass is supported by the
    actual manuscript, render-toolchain report, figures, tables, and display-item
    explanations rather than asserted by the Researcher.

## Nature Machine Intelligence Review Bar

For Nature Machine Intelligence-style Article or Analysis outputs, require:

1. A substantial article structure with Introduction, Results with subheadings,
   Discussion, Methods sufficient for replication, Data and Code Availability,
   Limitations, and References.
2. A coherent empirical program: baseline suite, ablations, uncertainty or
   calibration, robustness or subgroup/shift analysis, negative controls, error
   analysis, and comparison to published baselines where feasible.
3. Four to six genuine multi-panel display items where appropriate. A multi-format
   export of the same figure counts as one display item, not two.
4. Line-numbered manuscript PDF rendering, numbered and visibly rendered LaTeX
   display equations, rendered inline math spans, a passing render-toolchain report
   when required, bundled Inter-first open-source manuscript and figure typography,
   and LaTeX-like serif math typography.
5. A comparison table against relevant literature and 25-50 real references when
   the topic warrants it.
6. Field advancement that is more than one local model run.

If these criteria are not met, recommend major revision or reject even when the
integrity check passes.
