# referee_2 Round 00 Packet

- Run id: `oasis_demo`
- Packet type: prompt input
- Created at UTC: `2026-07-05T20:32:51.669064+00:00`

This packet is an instruction artifact. It must not prewrite the role's
conclusions, issue resolutions, acceptance decision, or scientific
judgment. The receiving agent must inspect the cited inputs and write only
the allowed outputs for its own role.

## Allowed Role

- Agent: `referee_2`
- Role: `referee`

## Required Inputs

- `runs/oasis_demo/article_type_contract.md`
- `runs/oasis_demo/manuscript_quality_contract.md`
- `runs/oasis_demo/proposal_gate_summary.md`
- latest `human_readable_outputs/oasis_demo/submission_*/revision_00/`
- latest submission artifacts under `submissions/oasis_demo/submission_*/revision_00/`
- prior `referee_2` reviews and Researcher responses when `round_id` is not `00`
- current Integrity Checker report when available

## Allowed Outputs

- `agents/referee_2/workspace/oasis_demo/review_round_00.md`
- one append-only event in `runs/oasis_demo/event_log.jsonl`

## Required Work

Write evidence-linked review comments only after reading the artifacts.
Use issue IDs beginning with `R2-`. Every major or blocking
issue must cite an exact path and state required evidence plus acceptance
criterion. Include what changed since the previous revision and direct
questions for the Researcher. Do not write another Referee's review,
integrity report, or editorial decision.
