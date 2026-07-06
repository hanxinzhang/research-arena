# Revision Trajectory Audit Packet

- Run id: `oasis_demo`
- Packet type: prompt input
- Created at UTC: `2026-07-05T20:32:51.669203+00:00`

This packet is an instruction artifact. It must not prewrite the role's
conclusions, issue resolutions, acceptance decision, or scientific
judgment. The receiving agent must inspect the cited inputs and write only
the allowed outputs for its own role.

## Allowed Role

- Agent: `auditor`
- Role: `auditor`

## Required Inputs

- relevant rubric under `audits/`
- `runs/oasis_demo/event_log.jsonl`
- `runs/oasis_demo/research_depth_audit.json`
- `runs/oasis_demo/review_similarity_audit.json` when available
- `runs/oasis_demo/trajectory_clerk.json` when available
- all relevant Referee reviews, Integrity Checker reports, submissions,
  verification matrices, and human-readable packages

## Allowed Outputs

- `runs/oasis_demo/revision_trajectory_review.md`
- one append-only event in `runs/oasis_demo/event_log.jsonl`

## Required Work

Make a judgment from the rubric and cited artifacts. Deterministic clerk
outputs are evidence tables only. Do not prewrite acceptance or rejection;
give the Editor a concise judgment, unresolved risks, and exact artifact
citations.
