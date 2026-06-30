# Prompts

These are copyable prompts for running Research Arena in an LLM agent.

- `start_oasis_demo.md`: start the OASIS demo after the user creates the local CSV
  described in `data/README.md`.
- `continue_revision.md`: continue an existing run through another revision cycle.
- `audit_run.md`: audit a run for safety, privacy, reproducibility, and protocol
  consistency.

To add more Researchers or Referees, name their folders in the prompt. If the folders
do not exist yet, ask the LLM agent to create them from `agents/templates/`.

Open this repository in your preferred LLM agent, paste one prompt, and let the agent
follow `program.md` plus the agent rules under `agents/`.
