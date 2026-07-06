# Referee Rules

Use `agents/referee_1/rules.md`, `agents/referee_2/rules.md`,
`agents/referee_3/rules.md`, or `agents/referee_4/rules.md` as the base rule
contract.

When creating a new Referee, keep:

1. the non-deterministic interaction rule;
2. the structured review schema;
3. issue IDs with severity, required evidence, evidence that would change the
   Referee's judgment, acceptance criteria, and lifecycle status (`opened`,
   `response_submitted`, `verified_resolved`,
   `partially_resolved`, `unresolved`, `editorial_risk_accepted`, or
   `superseded`);
4. follow-up verification of Researcher evidence;
5. integrity, citation, originality, artifact, and safety expectations;
6. the gate that no recommendation may be based on round number or scripted
   thresholds.
7. review of the first-submission research dossier, EDA report, experiment
   registry, compute log, method cards, and standalone analysis code;
8. issue ownership: the new Referee owns only its own prefix, such as `R5-*`;
9. artifact-specific major concerns with exact missing evidence;
10. `what_changed_since_previous_revision`;
11. direct questions to Researchers and assessment of their answers;
12. verification-matrix updates and canonical issue-ledger lifecycle updates for
    the Referee's owned issues;
13. anti-template discipline: the Referee must provide a distinct specialty lens
    and not copy another Referee's review text;
14. manuscript-quality and presentation-gate review, including
    `presentation_checklist.md`, `display_item_plan.md`,
    `display_item_explanations.md`,
    `manuscript_style_manifest.md`, readable line-numbered manuscript PDFs,
    organized section/subsection hierarchy, numbered and visibly rendered LaTeX
    display equations, rendered inline math spans, `render_toolchain_report.json`
    when required, bundled Inter-first manuscript and figure fonts plus LaTeX-like serif math,
    human-readable figures/tables, a human-readable output package, raw-label
    translation, manuscript figure/table explanations, title-adjacent figure/table
    narrative paragraphs in integrated `article/article.pdf` for serious-pilot and
    full-research runs, and Methods/background depth appropriate to the selected article
    type, plus whether the manuscript reads as a standalone article rather than a
    revision response or audit memo;
15. revision-plan review before follow-up rounds, including whether
    `research_delta_tier` and proposed actions are adequate for the Referee's
    owned issues;
16. the rule that empirical, novelty, or article-fit blockers need new evidence,
    credible substitutes, formal downgrade, or rejection rather than packaging-only
    responses;
17. the deterministic-clerk boundary: scripts may summarize hashes, compute, paths,
    and textual similarity, but the Referee must write an independent LLM-backed
    judgment;
18. the requirement to address trajectory-clerk process-risk fields such as
    `analysis_change_kind=revision_marker_only`, unchanged primary metrics,
    event-order warnings, and flat compute when judging whether a revision actually
    improved the evidence.
19. display-program independence review: distinguish shared visual style helpers
    from shared figure/table concepts, filenames, order, or plotting structure;
    route disputed overconvergence to
    `audits/display_program_independence_rubric.md` rather than relying on a
    deterministic filename or similarity rule.

Change only the specialty, review emphasis, and examples so the new Referee
contributes a distinct perspective.
