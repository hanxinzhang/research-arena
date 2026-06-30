# Research Arena Agent Instructions

This repository is an LLM-native research community protocol. This file is named
`AGENTS.md` for compatibility with agentic coding tools that read it automatically;
Codex, Claude, or another file-aware LLM agent can follow the same protocol.

When a user asks to run Research Arena:

1. Read `program.md` first.
2. Read each participating agent folder under `agents/`:
   - `config.json`
   - `profile.md`
   - `rules.md`
   Include all Researchers and Referees explicitly named by the user. If the user
   asks to add agents, create new folders such as `agents/researcher_3/` or
   `agents/referee_3/` using the existing folder pattern.
3. Treat the dataset as a shared resource, not as a shared target. Researchers may
   study different bounded questions from the same data.
4. Create run artifacts under `runs/<run-id>/`, `submissions/<run-id>/`, and
   `agents/<agent-id>/workspace/<run-id>/`.
5. Do not require an API key, package install, or Python command to start the protocol.
   The user starts the protocol by prompting their chosen LLM agent in this repository.
6. Use Python or Anaconda only as a local analysis/artifact tool when needed.
7. Use Python for generated analysis code by default, unless the user explicitly
   requests another language.
8. Keep manuscript PDFs text-only. Put figures and tables in separate artifact
   folders, and prefer PDF/SVG figure files for presentation quality.
9. Agents may use the internet for recent relevant literature, methods, and style
   references when the user permits browsing or when the LLM agent has browsing available.
   Cite sources with enough information for a human to find them.
10. Researchers must generate original ideas and writing. They may cite and build on
   published work, but they must not plagiarize text, figures, tables, code, or
   research framing.
11. Do not paste private/local data into internet searches or third-party websites.
12. Researchers should keep a source/literature note and a pre-results analysis plan
    for each submission.
13. Treat generated analysis scripts as untrusted until inspected. Do not put network
   calls, secrets, private paths, or shell-based destructive operations in generated
   research code.
14. Keep all claims exploratory unless a stronger claim is explicitly justified by the
   submitted evidence and the integrity check.
