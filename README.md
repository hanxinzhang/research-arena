# Research Arena

Research Arena is a research community framework for agent-based research
workflows.

Instead of running one lone "research agent," it models a miniature scholarly
community: Researchers propose candidate studies, a Study Design Board reviews
those proposals before analysis, an Integrity Checker audits reproducibility,
specialized Referees create evidence-linked issues, and an Editor/Publisher makes a
gate-based decision about what gets accepted.

Research Arena is designed to reward evidence and clear scientific presentation, not
polished paperwork. Current framework rules require each run to declare a
study-design contract, data-agnostic rigor contract, manuscript-quality contract,
compute budget, and independence plan before initial submissions. Each Researcher
must first complete dataset familiarization and a small pilot study before writing
candidate proposals. The pilot grounds the selected idea and compute estimate in
actual data structure, loading cost, early baseline behavior, leakage risks, and
local resources. Only after Study Design Board approval does the Researcher produce
a first-submission dossier, EDA report, experiment registry, compute log, method
cards, standalone analysis code, and a presentation checklist so that the first
pass can be judged as real research rather than a quick LLM-generated narrative.

The current version is LLM-native: the protocol is written in Markdown, and the
user starts it by prompting an LLM coding/research agent inside this repository.
Codex, Claude, or another file-aware LLM agent can serve as the runtime. This follows the spirit of
[`karpathy/autoresearch`](https://github.com/karpathy/autoresearch): the repo stores
the program and rules; the chosen LLM agent executes the research loop.

The current framework schematic is available as a PDF:
[`assets/research_arena_workflow.pdf`](assets/research_arena_workflow.pdf).

## What it is

Research Arena is not a claim that agents can produce valid science on their own.
It is a testbed for asking a narrower question:

> Can we make agentic research workflows behave more like a research community,
> with competition, peer review, reproducibility checks, revision, and editorial
> selection?

Researchers share the same dataset access and governance rules, but they are not
required to optimize the same metric, use the same focal variable, or study the same
scientific question. A run may provide a focal variable as context for a demo or
benchmark, but the protocol allows creative predictive, associative, descriptive,
causal-sensitivity, or methodological ideas.

Agents may use the internet to find recent relevant research when browsing is
available. Published work can inform background, citations, and methods, but
Researchers must produce original ideas and original prose. Integrity Checker and
Referees explicitly screen for plagiarism, fabricated citations, weak originality,
poor citation practice, unsupported claims, and unresolved issue-ledger items.

## How this differs from autoresearch

Research Arena is inspired by
[`karpathy/autoresearch`](https://github.com/karpathy/autoresearch), especially the
idea that a repository can store a lightweight research "program" for an LLM agent
to follow.

The difference is the social structure. `autoresearch` is organized around an agent
iterating on research ideas, code, and experiments. Research Arena models a small
research community: multiple Researchers compete using the same shared resources,
an Integrity Checker audits reproducibility and originality, specialized Referees
request evidence-linked revisions, and an Editor/Publisher accepts at most one
manuscript only when acceptance gates are met.

In other words, `autoresearch` is closer to an autonomous research loop, while
Research Arena is a peer-review and publication protocol for agent-based research
workflows.

## Requirements

Install only the things needed to let an LLM agent work in a local research repository:

- An LLM coding/research agent, such as Codex, Claude, or another tool that can read
  and write local files
- Python 3.10 or newer, or Anaconda
- A local folder containing this repository

That is enough to start the protocol. You do not need to install a Research Arena
package, run a Research Arena command, configure a project API key, or start a
separate server.

Python/Anaconda is used only when the LLM agent needs to inspect data, run a submitted
analysis script, or create local artifacts. The protocol itself is started with
natural language.

Publication-quality manuscript rendering has an additional free/open-source
toolchain:

- Pandoc.
- XeLaTeX through TeX Live, BasicTeX, or MacTeX.
- `latexmk`.
- Poppler tools: `pdfinfo`, `pdftoppm`, and `pdftotext`.
- `qpdf`.
- `fontconfig` (`fc-match`).

For user-facing setup, run the dependency doctor. It distinguishes tools staged
beside the repo, tools installed on the machine, and tools visible to the runtime
that Research Arena will actually use:

```bash
python tools/doctor.py --fix
```

By default the doctor checks the `ag` conda environment, because many local runs
use `conda run -n ag`. Use `--conda-env none` to check only the current shell, or
`--conda-env <name>` for another runtime. `--fix` prints a concrete fix plan; add
`--apply` only when you want the doctor to run installer commands such as
`brew install`, `sudo installer`, or `sudo tlmgr install`.

The shell shortcut is equivalent:

```bash
bash tools/setup_rendering_tools.sh
```

For deterministic gate evidence, use the lower-level checker:

```bash
python tools/check_render_toolchain.py --text
```

To write the run-level report required by the presentation gate:

```bash
python tools/check_render_toolchain.py --run-id <run_id> --write-default
```

For serious-pilot and full-research runs, every revision should build
`article/article.pdf`. When a revision includes figures in `article.pdf`, run the
figure presentation audit before the final presentation gate:

```bash
python tools/figure_presentation_audit.py <revision-dir> --write
```

This checks that source PDF figures use article-normalized typography, consistent
open-source figure fonts, and readable article-effective text size after panel
insertion. It is designed to catch oversized or undersized axis labels, legends,
titles, tick labels, bars, lines, and dots before the final PDF is packaged.

If this repository sits beside a folder named `required tools`, the checker will
automatically add the staged local Pandoc binary and BasicTeX install path to its
search path. The BasicTeX package in `required tools` is staged only until it is
installed. On macOS, the remaining non-TeX QA tools usually come from Homebrew:

```bash
brew install poppler qpdf fontconfig
```

## Quickstart

1. Open this repository in your preferred LLM agent.
2. Ask the agent to read `program.md`.
3. If you want to run the OASIS demo, follow [`data/README.md`](data/README.md) to
   create a local `data/OASIS_cross_tbl_df.csv`.
4. Run `python tools/doctor.py --fix` if you want paper-level PDF rendering
   rather than a compact-demo fallback.
5. Paste a start prompt.

A good Research Arena prompt should be short. Give the framework the facts that
are specific to your run, then let `AGENTS.md`, `program.md`, and the agent rules
provide the default protocol.

Minimal example prompt:

```text
Please run Research Arena.

Dataset: data/OASIS_cross_tbl_df.csv
Run id: oasis_demo
Agents: 2 Researchers, 1 Study Design Board, 1 Integrity Checker, 4 Referees, 1 Editor
Research ambition: compact demo
Compute budget: target 0.25 CPU-core hours per Researcher; minimum 3 experiment rows per Researcher
Revision budget: revision_00 plus 1 evidence-linked revision
Research scope: Researchers may choose different questions; no shared target required
Pilot requirement: each Researcher must inspect the data and run a small Phase 0 pilot before proposing candidate studies

Use the framework defaults in AGENTS.md, program.md, and agents/ for all protocol
details, gates, artifacts, audits, and final editorial decision rules.
```

Reusable prompts are in [`prompts/`](prompts/):

- [`prompts/start_oasis_demo.md`](prompts/start_oasis_demo.md)
- [`prompts/continue_revision.md`](prompts/continue_revision.md)
- [`prompts/audit_run.md`](prompts/audit_run.md)

## Prompt Knobs

Most prompts only need these user-customized fields:

- `Dataset`: local data path or data folder.
- `Run id`: folder name under `runs/`, `submissions/`, and agent workspaces.
- `Agents`: how many Researchers, Referees, and whether to use extra named agents.
- `Research ambition`: demo, serious pilot, or full research attempt.
- `Compute budget`: target CPU/GPU/backend budget and minimum experiment rows.
- `Revision budget`: how many evidence-linked revision rounds to allow before the
  Editor must stop, downgrade, or reject.
- `Research scope`: shared target, free-form questions, required methods, excluded
  claims, or any domain constraints.

Avoid copying the full protocol into the prompt. If a rule is general, put it in
the framework files. If it is specific to this run, put it in the prompt.

## Choosing Run Realism And Compute Budget

Before starting a run, decide how real you want the work to be. The article type,
proposal gate, compute budget, and final editorial standard should all match that
choice.

### Demo Test

Use this when you are testing whether the framework works.

- Article type: compact demo or workshop-style note.
- Goal: exercise the workflow, not produce publishable science.
- Typical budget: minutes to about one hour per Researcher.
- Evidence: small EDA, one or two baselines, one robustness or leakage check, simple
  tables/figures.
- Presentation: still require readable labels, figure/table explanations, a
  readable manuscript/PDF, and an explicit demo-level
  `manuscript_quality_contract.md`. A demo may waive line numbers or
  equation-count expectations only when the waiver is explicit. If the demo uses
  the fallback renderer, set `allow_fallback_renderer: true` and disclose the
  limitation.
- Editorial rule: do not call the output a full research article.

### Serious Pilot

Use this when you want a credible exploratory analysis and to learn whether a larger
study is worth running.

- Article type: pilot analysis, benchmark note, methods note, or reusability report.
- Goal: produce a useful research artifact with honest limitations.
- Typical budget: one to four wall-clock hours per Researcher, more if the dataset is
  large.
- Evidence: proposal gate, meaningful EDA, baseline suite, ablation or contribution
  check, uncertainty, leakage checks, error analysis, and literature context.
- Presentation: a clear line-numbered manuscript with background, rationale,
  detailed Methods, numbered and visibly rendered LaTeX display equations when
  relevant, rendered inline math spans in the same LaTeX-like serif style, limitations,
  a dedicated figure/table guide, and human-readable
  display items. Run `tools/check_render_toolchain.py --run-id <run-id>
  --write-default` and resolve missing tools before acceptance. A pilot can be
  shorter than a full article, but it should not read like an extended abstract.
- Editorial rule: claims should be local unless validation and comparison support
  broader claims.

### Full Research Attempt

Use this when you actually want the arena to attempt a publishable research run.

- Article type: full Article or Analysis.
- Goal: field-relevant contribution, not only a local model result.
- Typical budget: several hours to days per Researcher, depending on data modality,
  baseline cost, literature review, external validation, and number of revisions.
- Evidence: strong proposal gate, recent literature grounding, strong baselines,
  contribution tests, paired statistical comparisons, calibration or uncertainty,
  subgroup/shift/robustness analysis, error analysis, reproducibility artifacts,
  publication-grade figures, and external validation when feasible.
- Presentation: substantial paper-level writing, formal method/model definitions
  with numbered LaTeX equations when relevant, line-numbered PDF rendering,
  polished annotated multi-panel figures where appropriate, comparison tables, a
  manuscript figure/table guide, and enough references for a real reader to
  understand the field position. Pandoc/XeLaTeX rendering and Poppler/qpdf/font
  QA are required unless the Editor explicitly downgrades the article type.
- Editorial rule: the Editor should reject all if the evidence does not meet the
  declared article type, even when the manuscript is polished.

Compute budget should be allocated to evidence, not to filling time. Prefer spending
compute on stronger baselines, ablations, validation, robustness checks, and
reproducibility reruns. Do not count repeated loops as meaningful compute unless they
answer a scientific stability or uncertainty question.
For Serious Pilot and Full Research Attempt runs, reserve a meaningful share of
the empirical budget for post-review challenge experiments. A run that spends all
compute on `revision_00` will tend to answer gatekeeper criticism with prose
rather than new evidence.

Proposal-stage compute estimates must be auditable arithmetic, not rough prose.
Each non-zero component in `compute_budget_estimate.md` should derive from pilot
timing or a separate timing probe. Components above 20% of the expected estimate
or 10% of the run target need measured timing support. For full Article/Analysis
runs, an expected estimate below 80% of the target, or a high estimate below the
target, should trigger a stronger empirical plan, article-type downgrade, or
run-budget revision before `revision_00/` begins.

## Example output

A completed demo can be regenerated from a local copy of
`data/OASIS_cross_tbl_df.csv` by following the quickstart prompt above. The raw
CSV and generated demo outputs are intentionally not committed to this repository
by default. A current generated example should contain:

- a compact current-framework community summary;
- proposal-gate artifacts and Study Design Board review;
- an integrity report;
- four specialized Referee reviews;
- an issue ledger and verification matrix;
- manuscript style and presentation checks;
- a final editorial decision;
- a tiny reproducible analysis script;
- a compact accepted manuscript PDF;
- separate PDF figure artifacts and a small result table.

Keep regenerated examples compact when packaging them for inspection. Real runs
can write larger artifacts to `runs/`, `submissions/`, `human_readable_outputs/`,
`work_packets/`, agent workspace folders, and final clean bundles under
`outputs/`, which are ignored by git by default.

## How it works

The protocol surface is plain text:

```text
AGENTS.md          agent instructions for compatible LLM tools
program.md         full Research Arena protocol
agents/
  README.md
  researcher_1/
    config.json
    profile.md
    rules.md
  researcher_2/
  study_design_board/
    config.json
    profile.md
    rules.md
  integrity_checker/
  referee_1/
  referee_2/
  referee_3/
  referee_4/
  editor_publisher/
  templates/
prompts/
  reusable natural-language prompts
examples/
  oasis_demo/
    optional local regenerated demo bundle, usually containing outputs/oasis_demo/
```

When you ask an LLM agent to run the arena, it should:

1. Read `program.md`.
2. Read all participating agent folders.
3. Profile the shared dataset.
4. Act as each named Researcher to perform Phase 0 data familiarization and a small
   pilot study, then generate multiple candidate studies and a selected
   pre-analysis proposal with a pilot-grounded compute estimate.
5. Act as the Study Design Board to approve, revise, downgrade, or stop each
   selected proposal before full analysis begins.
6. Act as each approved Researcher to generate analyses, results, and
   manuscripts.
7. Act as the Integrity Checker to audit proposal-gate compliance, reproducibility,
   consistency, leakage,
   p-hacking risk, originality, citation integrity, plagiarism risk, stale artifacts,
   research-depth compliance, Researcher independence, issue-ledger traceability,
   verification-matrix completeness, and templated-review risk.
8. Act as each named Referee to produce structured reviews with key claims, major
   concerns, required experiments, statistical concerns, novelty concerns,
   presentation-gate concerns, figure/table concerns, literature gaps, issue-status
   verification, and concrete acceptance criteria. Each Referee owns only its own
   issue prefix and must include `what_changed_since_previous_revision`, direct
   questions, and assessment of prior answers.
9. Run deterministic clerk checks, or manually reproduce their facts:
   structural-depth/presentation/independence, review similarity, revision
   trajectory when more than one revision exists, artifact authority, run-state
   order, archive hygiene, and scripted-generation risk. These checks summarize
   evidence; they do not decide scientific merit.
10. Act as LLM-backed scientific auditors using the rubrics under `audits/` for
   scientific depth, revision trajectory, novelty/article fit, reviewer quality,
   manuscript article voice, display-item narrative quality, and display-program
   independence when those judgments affect the decision.
11. Freeze the run evidence with
   `python tools/freeze_run.py <run-id> --stage pre-decision` immediately before
   final editorial decision.
12. Act as the Editor/Publisher to accept at most one manuscript only through
   gate-based review. The final decision must cite
   `pre_decision_freeze_manifest.json`. Then create and verify a post-decision
   archive with `python tools/freeze_run.py <run-id> --stage post-decision`. If no
   submission satisfies the proposal-gate, depth, presentation,
   artifact-authority, state-order, scripted-generation, independence,
   reproducibility, novelty, issue-resolution, and article-type gates, publish no
   manuscript.

There is no Research Arena Python package in this repository. The LLM agent may
still write and run Python analysis scripts as part of a submission, but the
protocol itself is stored in Markdown and agent rule files. Generated examples are
local artifacts by default and are ignored by git unless a maintainer deliberately
curates a shareable snapshot.

## Adding agents

The default protocol starts with two Researchers, one Study Design Board, and four
specialized Referees, but the protocol is folder-based. To add more:

1. Copy an existing folder, for example `agents/researcher_2/` to
   `agents/researcher_3/`, or `agents/referee_4/` to `agents/referee_5/`.
2. Edit `config.json` so `id` matches the folder name and the display/profile fields
   describe the new agent.
3. Edit `profile.md` and `rules.md` to give the new agent a distinct research or
   review style.
4. Name the extra agents in the run prompt.

The LLM agent should include every explicitly named Researcher and Referee in the
same community run. Researchers compete using the same shared dataset and governance
rules; the Study Design Board reviews proposals before analysis; Referees review all
submissions unless the user asks for a different review assignment.

Every Referee request should create or update an issue ID owned by that Referee,
such as `R1-MAJOR-02` for Referee 1. Referees should not resolve or summarize
other Referees' issues as their own. Researcher revision responses must cite exact
files, tables, figures, or lines that address each issue and answer direct reviewer
questions. Follow-up Referees must verify the evidence in
`verification_matrix.csv` or `verification_matrix.json` before marking issues
resolved.

Researcher revisions must be issue-driven. Do not add artifacts because a revision
number was reached; add them because an open issue, reviewer question, integrity
finding, or editor instruction requires them. The Editor and Integrity Checker
should run deterministic clerk checks for structural depth, presentation,
independence, review similarity, revision trajectory, artifact authority, state
order, and scripted-generation risk before final acceptance. Those checks are
evidence summaries; LLM-backed auditors must still judge scientific depth,
novelty/article fit, revision trajectory, reviewer quality, manuscript article
voice, display-item narrative quality, and display-program independence with the
rubrics under `audits/`.

If a run is orchestrated with automation, use explicit work packets under
`work_packets/<run-id>/` as role inputs. Work packets must list allowed inputs and
outputs, but they must not prewrite a Researcher's findings, a Referee's concerns,
an Integrity Checker report, LLM-backed judgments, or the Editor's decision.

Before any revision after `revision_00/`, the Researcher should write
`revision_plan.md` and receive approval, plan revision, downgrade, or rejection
from the relevant Referee, Integrity Checker, or Editor. A run should not continue
with packaging-only revisions when central open issues require new empirical
evidence.
The plan must declare `research_delta_tier`:

- `tier_a_material`: a design, data, endpoint, method, benchmark, leakage,
  validation, or generalization change that could alter the central claim or
  article-type fit.
- `tier_b_supporting`: ablations, stronger baselines, uncertainty, calibration,
  subgroup/shift/robustness checks, negative controls, error taxonomy, or
  sensitivity analysis.
- `tier_c_nonmaterial`: prose, formatting, rerendering, provenance, packaging,
  verification matrices, copied-forward results, or claim-boundary clarification
  without new empirical support.

Central empirical, novelty, or article-fit blockers cannot be resolved by
`tier_c_nonmaterial`. Material or supporting revisions should include
`material_research_delta.md`; nonmaterial revisions should say which central
issues remain unresolved and whether downgrade or rejection is the honest next
state.

## Outputs

The LLM agent should write run artifacts to:

```text
runs/<run-id>/
  dataset_profile.md
  event_log.jsonl
  article_type_contract.md
  study_design_contract.md
  proposal_gate_summary.md
  research_depth_contract.md
  manuscript_quality_contract.md
  compute_budget.md or compute_budget.json
  agent_independence_plan.md
  editor_gate_plan.md
  research_depth_audit.json
  review_similarity_audit.json
  trajectory_clerk.json
  artifact_authority_audit.json
  run_state_audit.json
  scripted_generation_audit.json
  archive_hygiene_audit.json
  pre_decision_freeze_manifest.json
  pre_decision_freeze_verification.json
  post_decision_archive_manifest.json
  post_decision_archive_verification.json
  scientific_depth_review.md
  revision_trajectory_review.md
  novelty_article_fit_review.md
  reviewer_quality_review.md
  manuscript_article_voice_review.md
  display_item_narrative_review.md
  display_program_independence_review.md
  summary.md
  final_decision.md

submissions/<run-id>/
  submission_001_<researcher-id>/
    proposal_gate/
      data_familiarization.md
      pilot_study_plan.md
      pilot_study_results.json
      pilot_compute_log.csv or pilot_compute_log.json
      pilot_lessons.md
      candidate_studies.md
      selected_proposal.md
      compute_budget_estimate.md
      proposal_response.md
    revision_00/
      proposal.md
      research_dossier.md
      eda_report.md or eda_report.ipynb
      literature_notes.md
      analysis_plan.md
      model_or_method_cards.md
      experiment_registry.csv or experiment_registry.json
      compute_log.csv or compute_log.json
      compute_reconciliation.md or compute_reconciliation.json when triggered
      analysis.py
      results.json
      stable_results.json when available
      empirical_provenance.json when revision_00 needs an explicit baseline; required after revision_00
      artifact_manifest.json
      issue_ledger.md
      issue_ledger.json
      verification_matrix.csv
      revision_response.md
      manuscript.md
      manuscript.pdf
      display_item_plan.md
      display_item_explanations.md
      manuscript_style_manifest.md
      presentation_checklist.md
      tables/
      figures/
    revision_01/
      revision_plan.md
      material_research_delta.md when research_delta_tier is tier_a_material or tier_b_supporting
      ...
  submission_002_<researcher-id>/
    revision_00/
      ...

human_readable_outputs/<run-id>/
  submission_001_<researcher-id>/
    revision_00/
      README.md
      manuscript.pdf
      figures/
      tables/
      source_code/
      human_readable_package_manifest.json

work_packets/<run-id>/
  proposal_gate.md
  integrity_round_00.md
  referee_1_round_00.md
  referee_2_round_00.md
  referee_3_round_00.md
  referee_4_round_00.md
  scientific-depth_audit.md
  revision-trajectory_audit.md
  novelty-article-fit_audit.md
  reviewer-quality_audit.md
  manuscript-article-voice_audit.md
  display-item-narrative_audit.md
  editor_final_decision.md

agents/<agent-id>/workspace/<run-id>/
  Study Design Board proposal reviews
  independent Researcher scratch work and experiment logs
  integrity reports
  referee reviews
  issue-status notes
  editorial records

outputs/<run-id>/
  README.md
  human_readable_outputs/
    run_overview/
      final_decision.md
      summary.md
    <submission>/<revision>/
      article.pdf
      manuscript.pdf
      figures/
      tables/
      source_code/
  diagnosis_process_files/
    run_records/
    submitted_revisions/
    work_packets/
    agent_workspaces/
  final_output_manifest.json
  final_output_verification.json
```

The active workflow may use several generated roots while the run is still being
generated, reviewed, audited, and decided. After the final decision, use
`outputs/<run-id>/` as the clean handoff folder. It separates normal reading
artifacts from diagnosis and process files. For completed runs, remove the
run-specific source roots after the final output bundle verifies so the project
does not keep duplicate `runs/`, `submissions/`, `human_readable_outputs/`, or
`work_packets/` copies.

The manuscript PDF should be visually readable line-numbered text/math/expression,
not a raw Markdown dump, unless the run is explicitly a compact non-publication
demo and the manuscript-quality contract allows it. Display equations should be
numbered LaTeX and visibly rendered in `manuscript.pdf`, and inline math such as
`$x_i$` or `\(p_i\)` should render as math rather than raw delimiters or code
spans. Manuscript text and figure text should use the bundled open-source Inter
family in `assets/fonts/inter/` by default. TeX Gyre Heros, Nimbus Sans,
Liberation Sans, Noto Sans, Source Sans 3, or Source Sans Pro are acceptable
deliberate alternatives for text. Mathematical expressions should render in
LaTeX-like serif math: italic serif variables and upright serif operator/text
labels. Put figures and tables in separate folders, preferably as PDF, with SVG
only as an optional extra, and use readable labels, legends, ticks, panel marks,
and annotations. Each latest revision with main-text display items must include
`display_item_plan.md` and `display_item_explanations.md`, and the manuscript must
summarize every figure and table: purpose, label/legend meaning, raw-label
translations, conclusion, and caveat. When `article/article.pdf` is required, each included figure and table
should show a short article-style explanatory paragraph directly paired with its
title. It should state the substantive pattern, contrast, estimate, uncertainty,
model behavior, or limitation, not tell the reader how to read. Each figure must
also declare an `Article group` decision in `display_item_explanations.md`:
`standalone` with a rationale, or a shared group id with panel labels, a group
title, and a group-level explanation. Grouping is an author/editor judgment about
related evidence, not a filename or count heuristic.

Each latest revision with main-text display items should also include
`display_item_plan.md` using `agents/templates/display_item_plan.md`. This file
states why the Researcher chose those figures or tables, what alternatives were
considered, and whether any item resembles another Researcher's display program.
Shared visual style is acceptable: `agents/templates/figure_style.py` may
standardize fonts, label humanization, line widths, marker sizes, grids, and save
behavior. It must not become a default figure sequence, filename list, or shared
`write_figures()` program. Use
`runs/<run-id>/display_item_narrative_review.md` with
`audits/display_item_narrative_rubric.md` when this title-adjacent explanation
needs judgment. Use `runs/<run-id>/display_item_grouping_review.md` with
`audits/display_item_grouping_rubric.md` when figure grouping or standalone
rationales need LLM/editor review. Use
`runs/<run-id>/display_program_independence_review.md` with
`audits/display_program_independence_rubric.md` when multiple Researchers'
display programs look overconverged or the style/program boundary is disputed.

Each manuscript revision should read as a standalone final article rather than a
response memo, changelog, or direct answer to reviewer/gatekeeper questions. Keep
issue-by-issue answers in `revision_response.md` and integrate review-driven
changes into ordinary Methods, Results, Discussion, Limitations, or reproducibility
prose. When article voice is uncertain, write
`runs/<run-id>/manuscript_article_voice_review.md` using
`audits/manuscript_article_voice_rubric.md` before acceptance.

Use `agents/templates/render_manuscript_pdf.py` as the standard Markdown
manuscript renderer. Its default `--engine auto` path prefers Pandoc/XeLaTeX,
reuses the staged toolchain paths checked by `tools/check_render_toolchain.py`,
and writes a render report beside the PDF. Keep
`agents/templates/manuscript_template.tex` as the LaTeX style reference for
serious-pilot and full runs, and write
`runs/<run-id>/render_toolchain_report.json` before acceptance when the
manuscript-quality contract requires it. If a run environment lacks
Pandoc/XeLaTeX, `agents/templates/render_manuscript_pdf.py --engine matplotlib`
may be used only for explicitly downgraded compact demos or internal review
artifacts; disclose the fallback in `known_style_limits`.

For serious-pilot and full-research runs, keep `manuscript.pdf` as the
line-numbered review manuscript and build a second integrated article output for
every revision:

```bash
python tools/build_article_pdf.py <revision-dir> --conda-env ag
```

This writes `article/article.pdf`, `article/article.md`, and
`article/article_build_report.json` using the same Pandoc/XeLaTeX toolchain. The
default layout is a robust PLOS-like single-column article that integrates
manuscript text, reasonably sized figures, and reasonably sized tables while
leaving the original `figures/` and `tables/` folders inspectable. It renders each
included figure and table with a bold title line followed by a short explanatory
paragraph from `display_item_explanations.md`. When multiple figure entries share
the same declared `Article group`, the builder renders them as labeled panels in
one condensed article figure while keeping the original standalone files
inspectable. The running
header uses a real publication type such as `Article`, `Review`, or `Editorial`
rather than the internal artifact label. Set article metadata explicitly when
needed:

```bash
python tools/build_article_pdf.py <revision-dir> --conda-env ag \
  --publication-type Article \
  --author-name "Researcher 1" \
  --publication-date "July 5, 2026" \
  --journal-volume "Volume 1" \
  --journal-date "July 2026"
```

When `--author-name` is omitted, the builder infers a readable Researcher name
from the submission folder when possible. The title block shows author,
publication type, and publication date; the footer shows the journal label,
volume, and journal date. The abstract is pulled into a distinct pre-main-text
block for emphasis. The title block begins with the Research Arena `Delta E /
Evidence Gain` logo masthead using the bundled open-source Inter font.

Before acceptance, build a human-readable output folder for every revision:

```bash
python tools/package_human_readable_outputs.py --run-id <run-id> --replace
```

This creates `human_readable_outputs/<run-id>/<submission>/<revision>/` with
the line-numbered `manuscript.pdf`, integrated `article.pdf`, standalone
`figures/`, standalone `tables/`, `source_code/`, a README, and a package
manifest. Use `--latest-only` only for explicitly scoped internal checks. This
intermediate package is copied into `outputs/<run-id>/` during finalization and
can be removed afterward.

After the final decision, post-decision archive manifest, and post-decision
verification are complete, build the clean one-folder handoff:

```bash
python tools/finalize_run_outputs.py <run-id> --replace --cleanup-source-roots
python tools/finalize_run_outputs.py <run-id> --verify
```

This creates `outputs/<run-id>/` with `human_readable_outputs/` for final reading
and `diagnosis_process_files/` for run records, submitted revisions, work packets,
and agent workspaces. It copies source workflow folders, verifies the copied
bundle, skips transient/cache/editor-generated files, omits package-manifest JSON
from the reader-facing area, and then removes the run-specific source workflow
folders when `--cleanup-source-roots` is used. The JSON files that remain in
`diagnosis_process_files/` are machine-readable audit records, freeze manifests,
and verification receipts; they should be kept when provenance matters, but they
are intentionally separated from normal reading artifacts.

## Data

The quickstart expects a local `data/OASIS_cross_tbl_df.csv`, a small public/demo
table described in [`data/README.md`](data/README.md). The raw CSV is intentionally
not committed. The prompt-run workflow uses this human-readable CSV file after the
user downloads or exports it locally.

Before redistributing this repository, publishing derived datasets, or adding other
datasets, check the source dataset's license, citation requirements, consent terms,
and redistribution rules.

## Safety model

Research Arena is exploratory only.

- Not clinical advice or medical advice
- Not a diagnostic system
- Not causal discovery
- Not proof of valid science
- Human review required before using any output for scientific, clinical, policy, or
  operational decisions

Generated analysis scripts are untrusted code until inspected. The LLM agent should
avoid network calls, secrets, private paths, shell-based destructive operations,
hidden external files, and unsupported clinical or causal claims. Toolchain and
render reports sanitize local repository, home-directory, staged-tool, and temporary
paths before writing shareable JSON reports, but generated diagnosis files should
still be reviewed before redistribution. See [`SECURITY.md`](SECURITY.md).

## Roadmap

- More Researcher profiles and strategies
- Stronger statistics and benchmark datasets
- Better reproducibility audits and artifact manifests
- More article-type presets and venue-specific review contracts
- Optional prompt templates for common dataset types
- Multi-dataset examples
- Stronger automated checks for research depth, compute effort, and Researcher
  independence across data modalities

## License

Research Arena is released under the MIT License. See [`LICENSE`](LICENSE).
