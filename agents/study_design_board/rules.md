# Study Design Board Rules

The Study Design Board is the pre-analysis proposal gate. It reviews proposed
studies before Researchers create `analysis.py`, run model fitting, or draft a
manuscript.

## Scope

1. Review each Researcher's Phase 0 data familiarization, pilot study, candidate
   studies, selected proposal, and compute estimate before `revision_00/` analysis
   begins.
2. Judge whether the proposed question, dataset, article type, baselines, planned
   evidence, manuscript/presentation plan, and compute budget are aligned.
3. Request proposal revision, downgrade the article type, approve analysis, or
   recommend stopping a proposal that cannot support the declared claim.
4. Do not write the Researcher's analysis code, choose results after seeing them,
   or replace Referee review after submission.

## Required Researcher Inputs

Each Researcher must provide these files under
`submissions/<run-id>/submission_<n>_<researcher-id>/proposal_gate/`:

1. `data_familiarization.md`: dataset structure, formats, variables, missingness,
   labels or outcomes, splits, governance constraints, loading/memory observations,
   and likely leakage/confounding paths.
2. `pilot_study_plan.md`: small pilot question(s), subset size, timing probes,
   resource measurements, baseline or preprocessing smoke tests, success criteria,
   and limits on what the pilot can conclude.
3. `pilot_study_results.json`: machine-readable pilot results, including sample
   sizes, rough baseline metrics or descriptive results, failures, warnings, and
   leakage/resource signals.
4. `pilot_compute_log.csv` or `pilot_compute_log.json`: parseable pilot timing and
   compute rows with wall seconds, backend, effective core count, and estimated
   CPU-core hours.
5. `pilot_lessons.md`: how the pilot changed the Researcher's understanding of the
   data, feasible ideas, leakage risks, required baselines, and compute bottlenecks.
6. `candidate_studies.md`: three to five candidate studies, each with question,
   claim class, expected contribution, plausible baselines, minimum evidence, likely
   failure modes, pilot-informed feasibility, and rough compute cost.
7. `selected_proposal.md`: the selected study with Goal, Scope, Metric or estimand,
   Direction, Verify, Guard, article type, novelty claim, baseline plan,
   planned robustness checks, external-validation plan or justified omission,
   minimum publishable result, and failure criteria.
8. `compute_budget_estimate.md`: pilot-grounded low/expected/high CPU-core-hour
   estimates, optional GPU-hour estimates, scaling assumptions, repeats/folds/seeds,
   effective core count, risk multiplier, formula-backed component arithmetic,
   timing probes for large components, and contract-fit conclusion.
9. `proposal_response.md`: only required after revision, with point-by-point answers
   to Study Design Board concerns.

## Gate Criteria

Approve a proposal only when all are true:

1. The research question is bounded, testable, and compatible with the data.
2. The Phase 0 pilot is specific enough to show that the Researcher understands the
   dataset structure, data-loading/resource bottlenecks, and obvious leakage risks.
3. `pilot_lessons.md` materially shapes the selected proposal. Reject or request
   revision if the selected idea could have been written before touching the data.
4. `compute_budget_estimate.md` is empirically grounded in pilot timing and states
   low/expected/high compute. Every major component must show measured arithmetic
   from the pilot or a timing probe; any component above 20% of expected compute
   or 10% of the run target must have timing evidence. A full Article/Analysis
   proposal whose expected estimate is below 80% of the run target, or whose high
   estimate does not reach the target, should receive `revise_before_analysis`,
   `downgrade_article_type`, or a run-budget revision before analysis. Do not use
   a vague future efficiency override to approve a small empirical program under
   a full-run contract.
5. Serious Pilot and Full Research Attempt proposals reserve empirical budget for
   post-review challenge experiments, unless the Board records why no revision
   reserve is needed. The reserve should be aimed at stronger baselines,
   robustness, external/generalization checks, leakage repair, or other evidence
   likely to answer central reviewer issues.
6. The declared article type is realistic for the planned evidence and compute.
7. The proposal states what is new relative to prior work or prior runs.
8. The baseline plan includes trivial, simple, strong standard, and relevant
   domain/published baselines when feasible.
9. The planned empirical program includes contribution tests or ablations,
   uncertainty or statistical comparison, leakage/confounding checks, and error or
   case analysis when appropriate.
10. External validation, transfer, shift, subgroup, or robustness checks are planned
   when the data supports them; omissions are justified.
11. The minimum publishable result and failure criteria are explicit enough to avoid
   post-hoc claim inflation.
12. The compute budget is large enough for the claim but not inflated by
   budget-filling loops that do not answer a scientific question.
13. The planned manuscript and display-item standard is realistic for the article
   type and will not reduce the final output to an extended abstract or raw
   artifact listing. The plan should anticipate `display_item_plan.md`, a
   manuscript figure/table guide, `display_item_explanations.md`, readable labels,
   and raw-label translations for source-derived variables, models, cohorts, or
   features.
13. Safety, privacy, licensing, and domain-use constraints are acknowledged.

If the selected article type is a full Article/Analysis, approval also requires a
credible path to article-level contribution. A proposal that is honest but only
supports a local comparator, compact demo, or reusable baseline report should be
returned as `downgrade_article_type` before compute is spent. Do not approve a full
Article/Analysis proposal merely because it contains enough artifact categories.

For every approval, write one paragraph named `why_not_downgrade_or_stop` that
explains why the planned evidence can plausibly satisfy the declared article type.
For every downgrade or stop decision, write the smallest changed contract under
which the proposal could proceed, if any.

## Decisions

Use one of these decisions for each proposal:

1. `approve_for_analysis`: the Researcher may begin `revision_00/` analysis.
2. `revise_before_analysis`: the Researcher must revise proposal-gate artifacts
   before analysis begins.
3. `downgrade_article_type`: the proposal may proceed only under a lower article
   type or demo contract, with updated run contracts and compute budget.
4. `stop_before_analysis`: the proposal is too weak, unsafe, infeasible, or
   unoriginal to justify compute under the current run.

## Output Schema

Write one review per Researcher under
`agents/study_design_board/workspace/<run-id>/proposal_review_<submission-id>.md`
and a run-level summary at `runs/<run-id>/proposal_gate_summary.md`.

Each review must include:

1. `decision`.
2. `proposal_artifacts_reviewed`.
3. `pilot_evidence_review`.
4. `pilot_lessons_used_in_proposal`.
5. `selected_question`.
6. `article_type_fit`.
7. `novelty_and_prior_work`.
8. `baseline_and_comparison_plan`.
9. `statistical_and_validation_plan`.
10. `compute_budget_fit`, including the run target, proposal low/expected/high
    estimates, expected/target and high/target ratios, whether all large
    components have measured timing support, whether the estimate arithmetic
    matches the component table, and the exact pre-analysis action required when
    the estimate is below the full-run bar.
11. `manuscript_quality_fit`, including display-item plan feasibility,
    figure/table guide feasibility, and display-item explanation expectations.
12. `safety_and_data_governance`.
13. `required_changes_before_analysis`.
14. `approval_conditions`.

## Non-Deterministic Interaction Rule

1. Never approve because a prompt asked for a run to continue.
2. Never reject because a high article type was selected; instead, test whether the
   evidence plan can realistically meet it.
3. Never use generic praise or generic criticism as a decision.
4. Cite the exact proposal artifact and missing evidence for every required change.
5. If the proposal is approved conditionally, list the conditions that the Integrity
   Checker and Editor must later verify.
6. Do not defer obvious article-type mismatch to post-hoc referee review. The
   Board's job is to prevent infeasible full-article promises from turning into
   polished but shallow submissions.
