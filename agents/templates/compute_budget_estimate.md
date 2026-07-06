# Compute Budget Estimate

Run id: `<run-id>`
Researcher: `<researcher-id>`
Selected proposal: `<short-name>`

## Structured Estimate

estimated_cpu_core_hours_low: 0
estimated_cpu_core_hours_expected: 0
estimated_cpu_core_hours_high: 0
estimated_gpu_hours_low: 0
estimated_gpu_hours_expected: 0
estimated_gpu_hours_high: 0

## Pilot Basis

- Pilot compute log: `pilot_compute_log.csv`
- Pilot sample size:
- Full planned sample size:
- Effective CPU cores:
- GPU or accelerator:
- Main bottleneck:
- Risk multiplier:
- Pilot timing rows used for each component:
- Components without measured timing:

## Component Scaling

Every row with a non-zero estimate should be backed by a measured pilot row or a
clearly named conservative fallback. Use this formula:

`estimated_cpu_core_hours = pilot_seconds * scale_factor * planned_repeats * effective_cpu_cores * risk_multiplier / 3600`

| component | measured_timing_source | pilot_size | full_size | pilot_seconds | scale_factor | planned_repeats | effective_cpu_cores | risk_multiplier | estimated_cpu_core_hours | evidence_role |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| data_loading_or_feature_extraction | `pilot_compute_log.csv:<row>` | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 0 | preprocessing |
| baseline_suite | `pilot_compute_log.csv:<row>` | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 0 | comparison |
| main_model_or_analysis | `pilot_compute_log.csv:<row>` | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 0 | primary evidence |
| uncertainty_or_resampling | `timing_probe_required_if_large` | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 0 | statistical support |
| negative_controls_or_leakage_checks | `pilot_compute_log.csv:<row>` | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 0 | validity |
| integrity_rerun_allowance | `derived_from_analysis_total` | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 0 | reproducibility |

## Formula Check

- Sum of component estimates:
- Structured expected estimate:
- Difference between component sum and structured expected:
- Expected / run target ratio:
- High / run target ratio:
- Any component above 20% of the expected budget:
- Timing probe exists for every component above 20% of expected or 10% of target:

## Contract Fit

- Run minimum CPU-core hours per Researcher:
- Run target CPU-core hours per Researcher:
- Does expected estimate meet the target:
- If below target, choose one before `revision_00`: strengthen the empirical plan,
  request article-type downgrade, or request run-budget revision. Do not rely on a
  post-hoc efficiency override for a full Article/Analysis proposal.
- Reconciliation trigger: after `revision_00`, create `compute_reconciliation.md`
  if actual compute is below target or less than half/more than 150% of this
  expected estimate.

## Uncertainty And Risks

- Low estimate assumes:
- High estimate assumes:
- Failure modes that could increase compute:
- Failure modes that could make the estimate too high:
- Parts that should not be counted because they are budget-filling rather than evidence:
