# Revision Plan

Submission: `<submission_id>`

Proposed revision: `revision_<NN>`

Authoring Researcher: `<researcher_id>`

revision_type: `<empirical_revision | interpretive_revision | packaging_revision | mixed_revision>`

research_delta_tier: `<tier_a_material | tier_b_supporting | tier_c_nonmaterial>`

material_research_delta_required: `<yes | no>`

post_review_compute_reserve_to_use: `<CPU-core hours, GPU-hours, or none>`

## Research Delta Classification

Choose the highest tier this revision is designed to achieve:

- `tier_a_material`: a change to study design, data/split, endpoint, method,
  benchmark suite, leakage repair, external/generalization evidence, or other
  evidence that can plausibly change the central claim or article-type fit.
- `tier_b_supporting`: ablations, stronger baselines, paired uncertainty,
  calibration, subgroup/shift/robustness checks, negative controls, error
  taxonomy, sensitivity analysis, or other support that strengthens an existing
  claim but does not redesign the study.
- `tier_c_nonmaterial`: prose, formatting, rerendering, provenance, packaging,
  verification matrices, copied-forward results, or claim-boundary clarification
  without new empirical support.

Central empirical, novelty, or article-fit blockers cannot be resolved by
`tier_c_nonmaterial`. They usually require `tier_a_material`, a strong
combination of `tier_b_supporting` evidence, formal downgrade, or rejection.

If this revision is `tier_a_material` or `tier_b_supporting`, create
`material_research_delta.md` in the revision folder. If this revision is
`tier_c_nonmaterial`, explain why no material research delta is being claimed and
which open central issues remain unresolved.

## Open Issues And Questions

| Issue ID | Owner | Current status | What evidence is required? | Evidence that would change the reviewer/editor judgment | Planned delta tier |
|---|---|---|---|---|---|
| `<issue_id>` | `<agent_id>` | `<open/partial>` | `<specific evidence>` | `<what result or artifact would change the decision>` | `<tier_a_material/tier_b_supporting/tier_c_nonmaterial>` |

## Proposed Actions

| Issue ID | Action type | Planned action | Expected artifact(s) | Empirical work required? | Claim that may change |
|---|---|---|---|---|---|
| `<issue_id>` | `<analysis/provenance/manuscript/downgrade/reject>` | `<action>` | `<paths>` | `<yes/no>` | `<central/secondary/none>` |

## Predicted Research-State Change

- Current central claim:
- Current weakest central evidence:
- New experiment, analysis, or design change:
- Result that would strengthen the submission:
- Result that would force downgrade or rejection:
- Central issues that will remain unresolved even if the plan succeeds:
- Whether `material_research_delta.md` will be created:

## Compute And Commands

- Expected wall-clock:
- Expected CPU/GPU/backend:
- Expected CPU-core hours:
- Expected experiment-registry rows added or updated:
- Planned commands:
- Seeds or reproducibility controls:
- Empirical provenance update: `empirical_provenance.json` will declare whether
  code, results, compute logs, and stable results are rerun, copied forward, or
  intentionally unchanged.

State whether the expected compute and experiment rows are sufficient to move the
run toward the structured compute-budget fields in `runs/<run-id>/compute_budget.*`.
If not, request downgrade or rejection instead of another packaging-only revision.

## Stop Or Downgrade Criteria

State the condition under which this revision should stop, downgrade article type,
or accept rejection instead of producing another packaging-only revision.

## Requested Approval

Requested decision: `<approve_plan | revise_plan | downgrade_article_type | reject>`

Reviewer/Integrity/Editor approval:

- decision:
- approving agent:
- rationale:
- date:
