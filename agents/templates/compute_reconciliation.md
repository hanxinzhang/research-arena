# Compute Reconciliation

Submission: `<submission_id>`

Revision: `<revision_id>`

## Structured Fields

compute_outcome: `<compute_target_met | compute_under_target_with_approved_efficiency_override | compute_under_target_requires_downgrade | compute_under_target_blocks_acceptance>`
proposed_expected_cpu_core_hours: `<float>`
actual_cpu_core_hours: `<float>`
target_cpu_core_hours: `<float>`
planned_experiment_families: `<semicolon-separated planned families>`
completed_experiment_families: `<semicolon-separated completed families>`
actual_to_expected_ratio: `<float>`
actual_to_target_ratio: `<float>`

## Reconciliation

- Proposal estimate source: `proposal_gate/compute_budget_estimate.md`
- Latest compute log: `revision_<NN>/compute_log.csv` or `.json`
- If the compute log contains component rows and an explicit `total_*` row, use
  the total row for actual compute and do not sum the total row with components.
- Explanation for difference between proposed and actual compute:
- Evidence families completed as planned:
- Evidence families omitted, reduced, or replaced:
- Why omitted or reduced compute does or does not change article-type fit:

## Editorial Consequence

State whether the submission can proceed at the current article type, requires a
formal downgrade, requires new empirical work, or must be blocked from acceptance.
