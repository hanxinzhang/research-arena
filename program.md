# Research Arena Program

Research Arena is a prompt-run research community. The protocol is executed by
starting a file-aware LLM agent in this repository and asking it to follow these rules.

There is no Python command that "runs the agents." The chosen LLM agent is the runtime:
it reads the rule files, plays the roles, creates artifacts, runs only the local
analysis code needed for a submission, and iterates through review and revision.

## Shared Resources

- Dataset: local `data/OASIS_cross_tbl_df.csv` for the quickstart after the user
  downloads or exports it following `data/README.md`.
- Dataset notes: `data/README.md`.
- Agent folders: `agents/`.
- Agent extension guide and templates: `agents/README.md` and `agents/templates/`.
- Workflow figure: `docs/assets/research_arena_workflow.svg`.

All Researchers receive the same dataset and the same governance rules. They do not
need to share the same target, focal variable, metric, or research question.

## Agents

Minimal community:

- `researcher_1`: conservative, interpretable, methodical Researcher.
- `researcher_2`: comparative Researcher willing to combine simple signals.
- `integrity_checker`: reproducibility and integrity auditor.
- `referee_1`: methods-first Referee.
- `referee_2`: clarity/publication-focused Referee.
- `editor_publisher`: final decision maker and publisher.

The community can be expanded without changing code. To add more Researchers or
Referees, create another agent folder such as `agents/researcher_3/` or
`agents/referee_3/` with the same three files: `config.json`, `profile.md`, and
`rules.md`. Then name the extra agents in the user's run prompt. The LLM agent should
include all explicitly named Researchers and Referees in the run.

Each agent folder contains:

- `config.json`: machine-readable role settings.
- `profile.md`: role/personality description.
- `rules.md`: behavioral rules for the LLM agent to follow while acting as that agent.

## Run Loop

1. Create a run id, usually `YYYYMMDD_<short_name>`.
2. Profile the shared dataset enough to understand columns, row count, missingness,
   and plausible variable types.
3. Researchers may use the internet to find recent relevant literature, but must
   cite sources, distinguish prior work from their own contribution, and avoid
   plagiarism.
4. Each participating Researcher generates one bounded original idea, writes Python
   analysis code in `analysis.py`, runs the analysis, writes `results.json`, creates
   simple PDF/SVG figures and tables, and writes a text-only manuscript PDF.
5. Researchers compete from the same shared resource but are free to choose different
   questions, methods, variables, and metrics.
6. Integrity Checker audits each submission for reproducibility, leakage,
   consistency, missing artifacts, p-hacking risk, and plagiarism/originality concerns.
7. Each participating Referee reviews each submission for creativity, originality,
   presentation, manuscript clarity, evidence strength, integrity, and limitations.
8. Researchers revise in response to referee and integrity feedback.
9. Repeat review/revision for the requested number of rounds.
10. Editor/Publisher synthesizes all reviews and integrity reports, accepts at most
   one manuscript, and writes a publication record.

## Artifact Contract

Use this folder shape:

```text
runs/<run-id>/
  dataset_profile.md
  summary.md
  final_decision.md

submissions/<run-id>/
  submission_001_<researcher-id>/
    revision_00/
      proposal.md
      literature_notes.md
      analysis_plan.md
      analysis.py
      results.json
      manuscript.md
      manuscript.pdf
      tables/
      figures/
    revision_01/
      ...
  submission_002_<researcher-id>/
    revision_00/
      ...

agents/<agent-id>/workspace/<run-id>/
  integrity reports, referee reviews, editorial records
```

Use Python for analysis code by default. Manuscript PDFs should be
text/math/expression only. Put figures and tables in separate folders. Prefer figure
files in PDF or SVG.

## Safety Rules

- Do not treat outputs as clinical advice, diagnostic evidence, causal discovery, or
  validated science.
- Do not use private data unless the user explicitly provides it and confirms that it
  may be used.
- Do not paste or write secrets into artifacts.
- Do not paste private/local data into search engines, external websites, or
  third-party literature tools.
- Do not copy text, figures, tables, code, or study framing from published work
  without clear attribution. Prefer paraphrase and synthesis over quotation.
- Do not fabricate citations, findings, related work, or source links.
- Do not selectively report only successful findings. Null, weak, and failed results
  should remain visible.
- Inspect generated analysis code before running it.
- Generated analysis code should use local files only, avoid network access, avoid
  shell calls, and avoid hidden external dependencies.
- Integrity failures block publication acceptance.

## Natural-Language Start Prompt

Use this prompt from the repository root:

```text
Please run Research Arena on data/OASIS_cross_tbl_df.csv.
If the CSV is missing, stop and tell me to follow data/README.md to create it locally.
Follow program.md and all agent rules under agents/.
Use two Researchers, one Integrity Checker, two Referees, and one Editor/Publisher.
Researchers may choose different research questions from the shared dataset; there is
no shared target requirement. Run one initial submission plus one revision round.
Write all artifacts under runs/oasis_demo and submissions/oasis_demo, then give me
the final editorial decision and the accepted manuscript path if any.
```

## Natural-Language Continuation Prompt

```text
Continue the existing Research Arena run in runs/oasis_demo.
Read the referee and integrity reports, revise each Researcher submission once, rerun
the integrity checks, collect new Referee recommendations, and update the final
editorial decision.
```

## Natural-Language Expanded-Community Prompt

```text
Please run Research Arena with researchers researcher_1, researcher_2, researcher_3
and referees referee_1, referee_2, referee_3. If researcher_3 or referee_3 folders do
not exist, create them from agents/templates/ and give each a distinct profile.
Follow program.md and all agent rules. Have every Referee review every Researcher
submission unless I specify a different review assignment.
```

## Natural-Language Audit Prompt

```text
Audit this Research Arena run for safety, privacy, reproducibility, and protocol
consistency. Check for private data leakage, unsafe generated code, data leakage,
p-hacking risk, unsupported claims, and stale artifacts. Summarize findings with file
paths and recommended fixes.
```
