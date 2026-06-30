---
name: research-arena
description: Use when the user wants to run or extend Research Arena, an LLM-native research community protocol with competing Researchers, an Integrity Checker, Referees, revision, and an Editor/Publisher decision. Trigger for agent-based research workflows, peer-review simulation, manuscript/revision rounds, OASIS demo runs, or adding new Researcher/Referee agents.
---

# Research Arena

Use this skill to run or extend the Research Arena protocol from this repository.
Research Arena is a repo-native workflow, not a Python package or command-line
runner. The LLM agent is the runtime: it reads the protocol files, plays the named
agent roles, creates artifacts, and coordinates review/revision.

## Core workflow

1. Read `program.md`.
2. Read `AGENTS.md`.
3. Read the participating agent folders under `agents/`.
4. If the user asks for the OASIS demo, read `data/README.md` first. The raw CSV is
   not committed; stop and ask the user to create it locally if missing.
5. Use prompts in `prompts/` when the user wants a ready-made start, continuation,
   or audit prompt.
6. Treat `examples/oasis_demo/` as illustrative output, not as raw source data.

## Operating rules

- Keep Research Arena LLM-agnostic; do not assume Codex is the only possible backend.
- Researchers compete using the same shared resources, but they do not need a shared
  target, focal variable, metric, or research question.
- Enforce the integrity gate before editorial acceptance.
- Do not treat outputs as clinical advice, diagnostic evidence, causal discovery, or
  validated science.
- Do not fetch, redistribute, or invent third-party datasets unless the user confirms
  the source and license/redistribution terms.
- Generated analysis code should avoid network calls, shell calls, credentials,
  private paths, hidden files, and destructive operations.

## Common tasks

- **Run a demo:** Start from `prompts/start_oasis_demo.md`.
- **Continue revisions:** Start from `prompts/continue_revision.md`.
- **Audit a run:** Start from `prompts/audit_run.md`.
- **Add agents:** Copy from `agents/templates/researcher/` or
  `agents/templates/referee/`, then update `config.json`, `profile.md`, and
  `rules.md`.
- **Inspect examples:** Use `examples/oasis_demo/summary.md`,
  `final_decision.md`, `integrity_report.md`, and `referee_reviews.md`.

## Artifact locations

Follow the artifact contract in `program.md`:

- `runs/<run-id>/`
- `submissions/<run-id>/`
- `agents/<agent-id>/workspace/<run-id>/`

Before publishing or sharing artifacts, audit for private data, raw data leakage,
unsafe generated code, unsupported claims, and stale outputs.
