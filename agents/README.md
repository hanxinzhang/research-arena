# Agents

Each agent is a folder with three files:

- `config.json`
- `profile.md`
- `rules.md`

The minimal community includes:

- `researcher_1`
- `researcher_2`
- `integrity_checker`
- `referee_1`
- `referee_2`
- `editor_publisher`

To add more Researchers or Referees:

1. Copy `agents/templates/researcher/` to `agents/researcher_3/`, or copy
   `agents/templates/referee/` to `agents/referee_3/`.
2. Replace `researcher_N` or `referee_N` in `config.json` with the new folder name.
3. Edit `profile.md` and `rules.md` so the new agent has a distinct perspective.
4. Name the new agent in the run prompt.

The LLM agent should include all explicitly named Researchers and Referees in the run.
Researchers compete using the same shared dataset and governance rules. Referees
review all Researcher submissions unless the user specifies a different assignment.
