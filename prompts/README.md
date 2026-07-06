# Prompts

These are copyable prompts for running Research Arena in an LLM agent.

Prompts should be short. Put only run-specific choices in the prompt: dataset,
run id, agent counts, ambition, compute budget, revision budget, and any domain
constraints. Keep general protocol behavior in `AGENTS.md`, `program.md`, agent
rules, audit rubrics, and deterministic tools.

- `start_oasis_demo.md`: start the OASIS demo with a compact configuration block.
- `continue_revision.md`: continue an existing run with a compact revision budget
  and stopping rule.
- `audit_run.md`: audit a run with a compact scope and focus list.

To add more Researchers or Referees, name their folders in the prompt. If the folders
do not exist yet, ask the LLM agent to create them from `agents/templates/`.

Open this repository in your preferred LLM agent, paste one prompt, and let the agent
follow `program.md` plus the agent rules under `agents/`.

Current prompts assume one Study Design Board plus four specialized Referees by
default: methods/statistics, domain interpretation, reproducibility/software, and
novelty/literature.

Backend defaults require Phase 0 data familiarization and pilot studies before
candidate proposals, proposal gates, contracts, verification matrices, presentation
checks, explicit work packets when orchestration is used, deterministic clerk
outputs, freeze manifests, LLM-backed scientific judgments including
display-program independence when relevant, and gate-based editorial decisions.
Do not copy those rules into every prompt.
