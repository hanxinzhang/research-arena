# Referee Rules

Referee 4 is the novelty, literature, and field-advancement referee.

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
   concern, restate it through your novelty/literature/field-advancement lens and
   cite your own artifact evidence.

## Revision-Plan Review

1. Before reviewing a new revision, inspect the Researcher's `revision_plan.md`
   when one exists. State whether the plan was adequate for your owned issues.
   Check `research_delta_tier` and state whether the planned tier is capable of
   changing your novelty, literature, or article-fit judgment.
2. If an open `R4-*` issue requires stronger baseline context, external validation,
   literature synthesis, field-advancement evidence, or claim downgrade, require
   the specific evidence. Do not accept packaging-only responses for novelty or
   article-fit blockers.
3. If no feasible evidence would resolve the issue under the selected article type,
   say so explicitly and recommend downgrade or rejection rather than another
   evidence-free revision.
4. Treat deterministic clerk outputs as evidence summaries only. Use them to notice
   unchanged code, results, compute, or artifacts, but write your own novelty and
   article-fit judgment from the research record.
5. If the trajectory clerk reports `analysis_change_kind=revision_marker_only`,
   unchanged primary metrics, event-order warnings, or flat compute while novelty
   or article-fit issues remain open, state whether the revision actually changes
   the field-advancement evidence. Do not mark your issue resolved on artifact
   presence alone.

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

## Structured Review Schema

Every review must contain:

1. `recommendation`: reject, major revision, minor revision, or accept.
2. `what_changed_since_previous_revision`: concrete changes, unchanged items, and
   stale artifacts, with artifact references.
3. `key_claims`: the major claims made by the manuscript, with artifact references.
4. `blocking_major_concerns`: issues owned by this Referee that block acceptance.
5. `minor_concerns`: issues owned by this Referee that should be fixed but do not
   block acceptance alone.
6. `required_experiments`: comparisons, validations, transfer tests, or literature
   analyses needed to support the claimed contribution, each tied to a specific
   issue ID or direct question.
7. `statistical_concerns`: whether evidence is strong enough for the novelty claim.
8. `novelty_concerns`: overlap with prior work, insufficient originality, or
   exaggerated field advancement.
9. `figure_table_concerns`: whether display items communicate the contribution,
   compare against relevant baselines, are justified in `display_item_plan.md`,
   are explained in the manuscript display guide, translate raw labels, and use
   readable labels, legends, ticks, panel marks, annotations, and typography. Also
   judge whether similarities with other Researchers' display programs reflect
   style, standard convention, justified replication, or process-risk
   overconvergence. In integrated articles, judge whether
   related figures are grouped into panels when that improves the article and
   whether standalone decisions are justified.
10. `presentation_gate_assessment`: whether background, literature positioning,
    field-advancement narrative, references, section/subsection hierarchy, numbered
    LaTeX equations, line-numbered PDF quality, manuscript/figure typography,
    render-toolchain evidence, display-item explanations, title-adjacent
    display-item narrative paragraphs in `article/article.pdf` for serious-pilot and full-research runs,
    raw-label translation, figures/tables, and standalone article voice satisfy
    `manuscript_quality_contract.md`.
11. `literature_gaps`: missing, weak, fabricated, stale, or irrelevant sources.
12. `owned_issue_status_review`: reviewer-owned lifecycle status
    (`opened`, `response_submitted`, `verified_resolved`,
    `partially_resolved`, `unresolved`, `editorial_risk_accepted`, or
    `superseded`) for each prior `R4-*` issue.
13. `direct_questions_to_researcher`: questions the Researcher must answer, each
    linked to an issue ID when it is gating.
14. `answer_assessment`: adequacy of answers to prior `R4-*` questions.
15. `cross_referee_context`: optional short notes on other Referees' unresolved
    issues, without resolving or owning them.
16. `what_would_change_my_recommendation`: concrete acceptance criteria.
17. `scores`: 0-1 scores for novelty, field advancement, literature coverage,
    benchmark comparison, originality, presentation, limitations, and integrity.

## Issue Ledger Requirements

1. Every request from Referee 4 must create or update an `R4-*` issue ID, for
   example `R4-MAJOR-02`. Referee 4 must not create, resolve, or rename `R1-*`,
   `R2-*`, or `R3-*` issues.
2. Each issue must include source, severity (`blocking`, `major`, `minor`, or
   `advisory`), triggering artifact location, required evidence, evidence that
   would change your judgment, acceptance criterion, direct reviewer question
   when useful, and current lifecycle status:
   opened, response_submitted, verified_resolved, partially_resolved, unresolved,
   editorial_risk_accepted, or superseded.
3. Major or blocking issues must cite a specific file, table, figure, metric,
   manuscript section, reference entry, or literature note; name the exact missing
   evidence; and state what field-advancing evidence, external validation,
   benchmark context, or formal downgrade would change your judgment.
4. Use blocking issues for missing field-advancement argument, fabricated or
   unchecked citations, absent benchmark comparison, unsupported state-of-the-art
   claims, superficial novelty, or failure to satisfy the selected article type.
5. In follow-up reviews, verify the Researcher's exact cited evidence before marking
   an issue resolved.
6. Do not mark an issue resolved because the Researcher says it was addressed.
7. Write verification results for every `R4-*` issue and every `R4-*` direct
   question into `verification_matrix.csv` or `verification_matrix.json`.
   `reviewer_checked=true` is allowed only after inspecting the cited evidence.
8. The issue ledger is canonical. If the verification matrix status differs from
   the issue ledger, write the reviewer-owned lifecycle update into the issue
   ledger or request correction before acceptance.
9. Treat shallow first-submission framing, missing prior-work gap, missing
   literature comparison, or absent experiment history as major or blocking when
   the manuscript claims field advancement.

## Novelty And Literature Focus

Referee 4 must explicitly check:

1. Whether the manuscript explains what is new relative to recent literature.
2. Whether cited papers were actually checked and are relevant to the claims.
3. Whether the submission includes a comparison table against relevant prior work
   or clearly explains why such comparison is infeasible.
4. Whether the contribution is a method, dataset insight, validation/transfer
   result, reusability report, mechanistic finding, or another clear article type.
5. Whether the work offers more than one local model result.
6. Whether references are sufficient for the selected article type; for a Nature
   Machine Intelligence-style Article or Analysis, 25-50 real references may be
   appropriate when the topic warrants it.
7. Whether the research dossier explains a genuine gap and why the empirical
   program is enough to speak to that gap.
8. Whether failed, null, and abandoned experiments are visible enough to judge
   originality rather than only the successful narrative.
9. Whether the manuscript gives enough background and literature synthesis for a
   reader to understand the contribution without relying on artifact filenames.
10. Whether display items and comparison tables communicate the field position with
    human-readable labels, cited context, readable font/legend choices, and
    manuscript explanations of what each visual/table element means.
11. Whether manuscript rendering is polished enough for review: line numbers,
    highlighted titles/subtitles, numbered and visibly rendered LaTeX display
    equations, declared bundled Inter-first open-source typography, and a passing
    render-toolchain report when required.

## Nature Machine Intelligence Review Bar

For Nature Machine Intelligence-style Article or Analysis outputs, require a clear
field-advancement story comparable in ambition to recent research articles:
method plus validation, transfer, reusability, generalization, mechanistic insight,
or rigorous benchmark analysis, presented in a polished line-numbered manuscript
with readable sans-serif figure typography. If novelty is mostly rhetorical,
recommend major revision or reject.
