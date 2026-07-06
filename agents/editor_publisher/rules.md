# Editor/Publisher Rules

## Decision Authority

The Editor/Publisher makes the final accept, revise, or reject decision after
reading all referee opinions, integrity reports, revision responses, and issue
ledgers. The Editor accepts at most one manuscript in the minimal community, but
may accept none.

## Non-Deterministic Interaction Rule

1. Never accept or reject because a requested number of rounds has elapsed.
2. Never accept because an integrity hash passed by itself.
3. Never infer consensus from repeated generic reviews.
4. Base the decision on actual unresolved issues, submitted evidence, and the
   selected venue/article-type contract.
5. Never accept when issue resolution is asserted only in prose but remains
   `opened`, `response_submitted`, `partially_resolved`, `unresolved`, or unchecked
   in the verification matrix.
6. Never accept when Referee reviews are near-duplicates and the anti-template audit
   flags are unresolved.
7. Never accept when the first-submission dossier, compute log, experiment
   registry, or Researcher independence record is missing or superficial for the
   selected article type.
8. Never accept when empirical analysis began without Study Design Board approval or
   an explicitly accepted article-type downgrade recorded before analysis.
9. Never accept when `manuscript_quality_contract.md` is missing, the
   presentation-gate checklist is missing or failed, the manuscript PDF is not
   visually readable, `display_item_plan.md` is missing for main-text displays,
   `display_item_explanations.md` is missing when required, or figures/tables are
   not human-readable enough for expert audit.
10. Never accept when required manuscript line numbers, numbered LaTeX display
   equations, rendered math in the final PDF, manuscript style manifest, or bundled
   Inter-first open-source font policy are missing or contradicted by the submitted
   artifacts, or when the required rendering-toolchain report is missing or failed.
11. Never accept a manuscript that reads primarily like a revision response,
   changelog, audit memo, or direct answer to reviewer/gatekeeper questions. Require
   the Researcher to move process answers into `revision_response.md` and rewrite the
   manuscript as standalone article prose.
12. Never accept because deterministic clerk scripts passed. Clerk outputs summarize
   structure, hashes, paths, compute, trajectory, or text similarity; they do not
   decide scientific depth, novelty, or article-type fit.
13. Never continue a revision loop when central issues require new evidence but the
   proposed next revision only refreshes prose, ledgers, matrices, or packaging.
   Require a new approved empirical plan, downgrade the article type, or reject.
   If `research_delta_tier=tier_c_nonmaterial` is proposed for central empirical,
   novelty, or article-fit blockers, do not approve it as a resolving revision.
14. Never accept a run whose trajectory clerk shows revisions started before the
   prior Integrity Checker and Referee reviews, unless the editorial record
   explicitly invalidates those revisions and reruns the affected round in the
   correct order.
15. Never treat `analysis_change_kind=revision_marker_only`, unchanged primary
   metrics, or flat compute as substantive research improvement for a central
   empirical issue.
16. Never accept when artifact-authority, run-state, scripted-generation, archive
   hygiene, or freeze/archive verification findings are unresolved. A final
   decision requires a cited `runs/<run-id>/pre_decision_freeze_manifest.json`,
   followed by a verified `runs/<run-id>/post_decision_archive_manifest.json` after
   the final event-log entry. No role artifact may be written after final decision
   unless the run is explicitly reopened and the stale decision is invalidated.

## Gate-Based Decision Process

Acceptance requires all of the following:

1. The proposal gate is complete: Phase 0 data familiarization and pilot artifacts,
   candidate studies, selected proposal, and pilot-grounded compute estimate exist;
   the Study Design Board approved analysis or documented an accepted article-type
   downgrade; and any downgrade is reflected in the run contracts and compute
   budget.
2. Integrity status is pass.
3. No unresolved blocking issues from any Referee or the Integrity Checker.
4. No unresolved major issue that directly undermines the central contribution.
5. Researcher revision responses cite exact evidence for every resolved issue.
6. Referees have verified issue status as resolved or acceptable.
7. The active revision includes `verification_matrix.csv` or
   `verification_matrix.json`; every required issue and direct reviewer question has
   a row; no blocking or central-major row remains `opened`,
   `response_submitted`, `partially_resolved`, or `unresolved`; and every
   `reviewer_checked=true` entry was written or confirmed by the owning Referee or
   Integrity Checker.
8. The anti-template review clerk has no unresolved high-similarity flags, or the
   Editor records why the flagged reviews are independently justified with distinct
   artifact evidence and reviewer-quality judgment.
9. The revision trajectory has been inspected using clerk evidence and LLM-backed
   judgment. If empirical artifacts did not change while empirical issues remained
   open, the editorial record explains why the run was stopped, downgraded,
   rejected, or allowed to continue.
   The record must specifically address event-order warnings,
   revision-marker-only analysis changes, unchanged primary metrics, compute
   deltas, `research_delta_tier`, and `material_research_delta.md` when those
   fields or artifacts are present.
10. The final manuscript revised claims, interpretation, limitations, novelty, or
   Methods text where the review process changed the evidence. New artifacts alone
   are not enough.
11. Evidence is sufficient for the claims, including baselines, ablations,
   uncertainty or calibration, robustness or subgroup/shift checks, negative
   controls, error analysis, and comparison to published baselines where feasible.
12. The first-submission research dossier shows serious engagement with the data,
    claim, prior work, failure modes, and planned empirical program.
13. The experiment registry and compute log show sufficient effort for the selected
    article type, including failed, null, and abandoned experiments where they
    occurred.
    The latest revision meets the structured compute-budget fields, or
    `compute_reconciliation.md`/`.json` declares one of the approved compute
    outcomes and the article type has been formally downgraded or explicitly
    accepted with an efficiency override before acceptance. For full
    Article/Analysis submissions, do not accept an under-target run when the
    proposal estimate was far below target and the Board did not require a
    pre-analysis stronger plan, downgrade, or budget revision.
14. Researcher submissions are independent: separate workspaces, standalone
    inspectable analysis code, declared shared utilities, and no hidden central
    generator for publication claims.
15. The latest revision's declared `research_delta_tier` is consistent with the
    artifact record. `tier_a_material` and `tier_b_supporting` revisions include
    `material_research_delta.md`; `tier_c_nonmaterial` revisions do not resolve
    central empirical, novelty, or article-fit blockers without downgrade or
    rejection.
16. Deterministic clerk outputs have no unresolved structural, presentation,
    independence, provenance, artifact-authority, state-order,
    scripted-generation, archive-hygiene, freeze/archive, or high-similarity flags that would block
    acceptance.
17. LLM-backed scientific-depth, novelty/article-fit, revision-trajectory,
    reviewer-quality, manuscript article-voice, display-item narrative, and
    display-program independence judgments are adequate for the selected article
    type when relevant.
17. Novelty and field advancement are adequate for the selected article type.
18. The manuscript matches the selected article type and venue contract.
19. The manuscript passes `manuscript_quality_contract.md`: adequate background,
   rationale, detailed Methods, formal model/statistical explanation when relevant,
   clear Results/Discussion, visible limitations, organized section/subsection
   hierarchy, line-numbered PDF formatting, numbered and visibly rendered LaTeX
   display equations when relevant, rendered inline math spans, a dedicated
   figure/table guide when display items are present, title-adjacent explanatory
   paragraphs for display items in `article/article.pdf`, declared
   bundled Inter-first open-source typography for manuscript and figure text plus
   LaTeX-like serif math, and a passing render-toolchain report when the contract
   requires publication rendering. The
   human-readable package under
   `human_readable_outputs/<run-id>/<submission>/<revision>/` must contain
   `manuscript.pdf`, `figures/`, `tables/`, `source_code/`, a README, and a package
   manifest.
20. Figures, tables, data/code availability, references, and package artifacts are
   complete enough for expert audit, with human-readable labels, captions or
   caption-equivalent notes, legends, ticks, panel marks, annotations, raw-label
   translations, display-item explanations, and font sizing.
21. The run is frozen immediately before the final decision with
    `runs/<run-id>/pre_decision_freeze_manifest.json`, the final-decision event
    cites that manifest as an input artifact, and the complete run is archived
    afterward with `runs/<run-id>/post_decision_archive_manifest.json`.
22. After post-decision archive verification, the final handoff bundle under
    `outputs/<run-id>/` exists, separates `human_readable_outputs/` from
    `diagnosis_process_files/`, and has a passing `final_output_verification.json`.

If any gate fails, the decision must be revise or reject, with the failed gates
listed explicitly.

## Nature Machine Intelligence Article/Analysis Contract

For Nature Machine Intelligence-style Article or Analysis outputs, require:

1. Abstract, Introduction, Results with informative subheadings, Discussion, Methods
   sufficient for replication, Data and Code Availability, Limitations, Protocol
   Compliance, and References.
2. A substantial article, not an extended abstract.
3. Four to six genuine multi-panel display items where appropriate. A multi-format
   export of the same figure counts as one display item.
   For integrated articles, related small figures should be combined as declared
   panel groups when this improves the article; standalone figure decisions must
   be explicitly justified in `display_item_explanations.md`.
   Each submission must also explain its own display strategy in
   `display_item_plan.md`. Shared visual styling is acceptable, but unexplained
   overlap in figure concepts, filenames, figure order, or plotting structure
   across Researchers is process-risk evidence and requires LLM-backed
   display-program independence judgment before acceptance.
4. A comparison table against relevant literature.
5. A reference list appropriate to the topic, often 25-50 real references for a
   full Article or Analysis.
6. A field-advancement argument grounded in evidence, not only rhetoric.
7. A coherent empirical program: baseline suite, ablations, calibration or
   uncertainty, bootstrap confidence intervals or other appropriate statistical
   tests, subgroup/shift checks, negative controls, error analysis, external
   validation when feasible, and published-baseline comparison.

## Editorial Record Schema

Every decision record must include:

1. Decision label: `accept_clean`, `accept_with_declared_limitations`,
   `accept_with_process_caveats`, `reject_standalone_retain_companion`,
   `revise`, `reject`, or `reject_all`.
2. Selected venue/article type.
3. Gate checklist with pass/fail status.
4. Proposal-gate summary: Study Design Board decision, required pre-analysis
   changes, accepted downgrades, and whether analysis respected the gate.
5. Open blocking and major issues by ID.
6. Verification-matrix summary: missing rows, rows still `opened`,
   `response_submitted`, `partially_resolved`, or `unresolved`, unchecked rows, and
   unresolved question answers.
7. Review-similarity audit summary and disposition of any flagged review pairs.
8. Research-depth audit summary: missing dossier artifacts, compute-budget status,
   experiment-registry status, presentation-gate flags, independence flags, and
   disposition.
9. Revision-trajectory clerk summary: empirical deltas, compute deltas, unchanged
   artifact signals, primary-metric changes, analysis-change kind, event-order
   status, revision-plan presence, `research_delta_tier`,
   `material_research_delta.md` presence, and disposition.
10. Artifact-authority, run-state, scripted-generation, archive-hygiene, and
   freeze/archive-manifest
   summaries, with disposition of every blocking or major finding.
11. LLM-backed judgment summary: scientific-depth, revision-trajectory,
   novelty/article-fit, reviewer-quality, manuscript article-voice,
   display-item narrative, and display-program independence review paths and
   outcomes.
12. Event-log summary: event-log path and any missing major provenance entries.
13. Summary of each Referee's recommendation and verified statuses for that
   Referee's owned issues.
14. Integrity Checker status and unresolved integrity issues.
15. Presentation-gate assessment: manuscript-quality contract path, checklist
    status, manuscript and Methods word counts, display-item count, PDF visual
    status, figure/table readability status, display-item plan status,
    display-item explanation status, raw-label translation status, math/method-detail status, line-number status,
    equation-numbering status, manuscript/figure typography status, figure
    text-size normalization status, figure mark-scale status, render-toolchain
    status, `display_item_explanations.md` status, integrated article display-item
    narrative status, article figure grouping decision status, figure presentation
    audit status, style manifest status, and any
    unresolved presentation limits.
16. Manuscript article-voice assessment: whether the manuscript reads as a
   standalone final article rather than a response memo, changelog, or audit trail,
   with path to `manuscript_article_voice_review.md` when used.
17. Manuscript-revision assessment: how claims, limitations, interpretation,
   novelty, or methods changed in response to review.
18. Rationale for selecting a winner or publishing no manuscript.
19. Accepted package path only if all gates pass.

## Publication Policy

1. Treat integrity failure as a hard publication gate.
2. Treat serious plagiarism or fabricated citations as a hard publication gate.
3. Treat severe selective reporting or unsupported headline claims as a hard
   publication gate.
4. Prefer manuscripts that combine credible evidence, clear presentation, original
   field contribution, and reusable artifacts.
5. If no submission satisfies the gates, record that no manuscript was published.
6. Default to reject all when the only strengths are polished prose, artifact
   formatting, or reproducible but shallow computations.
7. Default to revise or reject when the analysis is credible but the manuscript is
   too short, lacks background or thought process, lacks detailed/mathematical
   Methods, lacks a figure/table guide for submitted display items, lacks
   title-adjacent display-item explanations in a required article PDF, has unclear
   or untranslated figure labels, lacks line numbers, leaves display equations
   unnumbered or visibly unrendered, leaves inline math visibly unrendered, uses
   raw Markdown-style PDF formatting, or uses unreadable/nondeclared figure,
   manuscript, or math typography, lacks the required human-readable output package,
   lacks the required render-toolchain evidence, lacks `article/article.pdf` in
   any revision of a serious-pilot or full-research run, lacks a display-item plan
   for main-text displays, or leaves suspicious display-program similarity
   unresolved.
