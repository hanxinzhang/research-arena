# Editor Final-Decision Packet

- Run id: `oasis_demo`
- Packet type: prompt input
- Created at UTC: `2026-07-05T20:32:51.669380+00:00`

This packet is an instruction artifact. It must not prewrite the role's
conclusions, issue resolutions, acceptance decision, or scientific
judgment. The receiving agent must inspect the cited inputs and write only
the allowed outputs for its own role.

## Allowed Role

- Agent: `editor_publisher`
- Role: `editor`

## Required Inputs

- `runs/oasis_demo/pre_decision_freeze_manifest.json`
- `runs/oasis_demo/pre_decision_freeze_verification.json` when verifying an existing pre-decision freeze
- `runs/oasis_demo/artifact_authority_audit.json`
- `runs/oasis_demo/run_state_audit.json`
- `runs/oasis_demo/scripted_generation_audit.json`
- `runs/oasis_demo/archive_hygiene_audit.json`
- `runs/oasis_demo/research_depth_audit.json`
- `runs/oasis_demo/review_similarity_audit.json`
- `runs/oasis_demo/trajectory_clerk.json` when applicable
- all LLM-backed judgment outputs
- latest Referee reviews, Integrity Checker reports, verification
  matrices, and proposal-gate summary

## Allowed Outputs

- `runs/oasis_demo/final_decision.md`
- `runs/oasis_demo/final_decision.json` when useful
- `runs/oasis_demo/summary.md` when useful
- one final-decision event in `runs/oasis_demo/event_log.jsonl`

## Required Work

Decide by gates, not by round count. The decision must cite
`runs/oasis_demo/pre_decision_freeze_manifest.json` as a frozen evidence input and
address unresolved proposal-gate, artifact-authority, state-order,
scripted-generation, presentation, reproducibility, review-quality,
novelty, and article-type risks. Do not write new research, review, audit,
or package artifacts after the final decision unless the run is explicitly
reopened and the stale decision is invalidated. After the final decision
event is appended, create and verify
`runs/oasis_demo/post_decision_archive_manifest.json`.
