# Study Design Board Proposal-Gate Packet

- Run id: `oasis_demo`
- Packet type: prompt input
- Created at UTC: `2026-07-05T20:32:51.668843+00:00`

This packet is an instruction artifact. It must not prewrite the role's
conclusions, issue resolutions, acceptance decision, or scientific
judgment. The receiving agent must inspect the cited inputs and write only
the allowed outputs for its own role.

## Allowed Role

- Agent: `study_design_board`
- Role: `study_design_board`

## Required Inputs

- `runs/oasis_demo/article_type_contract.md`
- `runs/oasis_demo/study_design_contract.md`
- `runs/oasis_demo/research_depth_contract.md`
- `runs/oasis_demo/compute_budget.md` or `.json`
- `submissions/oasis_demo/submission_*_*/proposal_gate/data_familiarization.md`
- `submissions/oasis_demo/submission_*_*/proposal_gate/pilot_study_plan.md`
- `submissions/oasis_demo/submission_*_*/proposal_gate/pilot_study_results.json`
- `submissions/oasis_demo/submission_*_*/proposal_gate/pilot_compute_log.csv` or `.json`
- `submissions/oasis_demo/submission_*_*/proposal_gate/pilot_lessons.md`
- `submissions/oasis_demo/submission_*_*/proposal_gate/candidate_studies.md`
- `submissions/oasis_demo/submission_*_*/proposal_gate/selected_proposal.md`
- `submissions/oasis_demo/submission_*_*/proposal_gate/compute_budget_estimate.md`

## Allowed Outputs

- `agents/study_design_board/workspace/oasis_demo/proposal_review_<submission-id>.md`
- `runs/oasis_demo/proposal_gate_summary.md`
- one append-only event in `runs/oasis_demo/event_log.jsonl`

## Required Decision Shape

Use one of: `approve_for_analysis`, `revise_before_analysis`,
`downgrade_article_type`, or `stop_before_analysis`.

For every selected proposal, cite the exact artifacts read, state the
article-type fit, compute realism, expected evidence, and blocking design
risks. Do not write analysis code or manuscript text for Researchers.
