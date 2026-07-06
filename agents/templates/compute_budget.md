# Compute Budget

Run id: `<run_id>`

Selected article type: `<demo | pilot | benchmark note | methods note | full Article/Analysis>`

## Structured Settings

These fields are parsed by `tools/research_depth_audit.py`.

minimum_cpu_core_hours_per_researcher: `<float>`
target_cpu_core_hours_per_researcher: `<float>`
minimum_experiment_rows_per_researcher: `<integer>`
allowed_compute_outcomes: `compute_target_met; compute_under_target_with_approved_efficiency_override; compute_under_target_requires_downgrade; compute_under_target_blocks_acceptance`

## Backend Assumptions

- CPU/GPU/backend:
- Environment:
- Expected wall-clock range:
- Expected rerun cost:
- Whether target is a minimum acceptance bar or an upper evidence budget:

## Planned Evidence Families

List the experiment families that justify the budget. Examples include:

- trivial or negative-control baseline;
- simple interpretable baseline;
- strong standard or literature baseline;
- claimed contribution or ablation test;
- uncertainty, calibration, or statistical comparison;
- subgroup, robustness, shift, or external-validity check;
- error, case, residual, or qualitative analysis;
- reproducibility rerun.

## Budget Interpretation

The budget is an evidence budget, not a time-filling target. Compute counts only
when it supports a scientific question, robustness check, comparison, or rerun.
Repeated loops that do not change evidence should not be counted as meaningful
progress.

Each Researcher must also create
`proposal_gate/compute_budget_estimate.md` after Phase 0 pilot timing. The Study
Design Board should compare the Researcher's low/expected/high estimate with this
run-level budget before allowing `revision_00/` analysis.

For full Article/Analysis attempts, a proposal whose expected CPU-core hours are
below 80% of the run target, or whose high estimate does not reach the target,
should not receive plain `approve_for_analysis`. The Board should require a
stronger empirical plan, a formal article-type downgrade, or an explicit
run-budget revision before `revision_00/` begins. Efficiency is welcome, but an
efficient analysis that is two orders of magnitude below the declared full-run
budget is evidence for a smaller article type unless the scientific evidence
plan is strengthened.

Large estimated components must be measured. Any component above 20% of the
proposal's expected compute or 10% of the run target needs a pilot timing probe
or a separately timed smoke test. Hand-estimated bootstrap, tuning, or rerun
allowances are not enough for proposal approval.

After `revision_00/`, each Researcher must reconcile actual compute with both the
run target and the proposal estimate whenever actual compute is below target or
differs materially from the expected proposal estimate. Use
`revision_<NN>/compute_reconciliation.md` or `.json` with a parseable
`compute_outcome` value. An efficient under-target run can proceed only when the
Study Design Board, Integrity Checker, and Editor can verify the completed
evidence families and the selected article type still match.

## Stop, Downgrade, Or Reject Criteria

State when the run should stop, downgrade article type, or reject instead of
continuing with packaging-only revisions.
