# Integrity Checker Round 00 Packet

- Run id: `oasis_demo`
- Packet type: prompt input
- Created at UTC: `2026-07-05T20:32:51.668987+00:00`

This packet is an instruction artifact. It must not prewrite the role's
conclusions, issue resolutions, acceptance decision, or scientific
judgment. The receiving agent must inspect the cited inputs and write only
the allowed outputs for its own role.

## Allowed Role

- Agent: `integrity_checker`
- Role: `integrity_checker`

## Required Inputs

- `runs/oasis_demo/event_log.jsonl`
- `runs/oasis_demo/proposal_gate_summary.md`
- all latest `submissions/oasis_demo/submission_*/revision_00/artifact_manifest.json`
- all latest `submissions/oasis_demo/submission_*/revision_00/compute_log.*`
- all latest `submissions/oasis_demo/submission_*/revision_00/verification_matrix.*`
- all latest `human_readable_outputs/oasis_demo/submission_*/revision_00/`
- `runs/oasis_demo/research_depth_audit.json` when available
- `runs/oasis_demo/artifact_authority_audit.json` when available
- `runs/oasis_demo/run_state_audit.json` when available
- `runs/oasis_demo/scripted_generation_audit.json` when available

## Allowed Outputs

- `agents/integrity_checker/workspace/oasis_demo/integrity_report_round_00.md`
- rerun logs under `agents/integrity_checker/workspace/oasis_demo/`
- one append-only event in `runs/oasis_demo/event_log.jsonl`

## Required Work

Rerun or inspect each submitted analysis, verify manifests and hashes,
check proposal-gate order, check the human-readable package, and identify
issue IDs with severity, required evidence, acceptance criteria, and
status. Do not resolve Referee-owned issues unless you verified the cited
evidence directly.
