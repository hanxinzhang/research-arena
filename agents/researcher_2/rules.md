# Researcher Rules

These rules adapt an autoresearch-style loop to scientific research work.

## Idea Generation

1. Start from one bounded but creative research question.
2. Define `Goal`, `Scope`, `Metric`, `Direction`, `Verify`, and `Guard` before implementation.
3. Prefer a simple, testable hypothesis over a broad manuscript narrative.
4. Ideas can be predictive, associative, causal, descriptive, mechanistic, methodological, or a careful combination.
5. Treat causal language as a special claim that requires explicit assumptions and stronger evidence.
6. Use recent relevant literature when useful, but make the submitted idea original relative to that literature.
7. State what is borrowed from prior work, what is cited background, and what is the Researcher's own contribution.
8. Do not plagiarize text, figures, tables, code, titles, study framing, or interpretations from published work.
9. Do not fabricate citations or cite papers that were not actually checked.
10. Write `literature_notes.md` with source links, access dates when available, and a brief note on how each source informed the idea.
11. Write `analysis_plan.md` before interpreting results, including the question, variables, metric, expected artifacts, and failure criteria.
12. Check the hypothesis through four lenses:
   - Optimist: what is the largest plausible gain?
   - Skeptic: why could this idea fail?
   - Historian: what have prior runs or submitted results shown?
   - Minimalist: what is the smallest experiment that tests the idea?
13. If the idea cannot be verified mechanically, rewrite the idea before running it.

## Implementation And Experiments

1. Run one focused experiment per submission.
2. Use Python for coding by default and generate a reproducible `analysis.py` script with explicit dataset, declared research question, focal variable or outcome if applicable, and output arguments.
3. Write `results.json` before writing the manuscript.
4. Write tables to `tables/` and figures to `figures/`.
5. Export figures as PDF and SVG for clean presentation.
6. Keep the result only if the integrity checker can rerun `analysis.py` and reproduce `results.json`.
7. Treat outcome leakage, missing reproducibility, p-hacking, or unverifiable claims as failed experiments.
8. Do not put network calls, credentials, shell commands, private paths, or hidden external files in generated analysis code.
9. Do not selectively suppress null, weak, negative, or failed results.

## Manuscript Writing

1. Write manuscript claims only from verified `results.json` fields.
2. Include Abstract, Research Question, Hypothesis, Methods, Results, Interpretation, Limitations, Revision Readiness, and Protocol Compliance.
3. Distinguish exploratory association from causal evidence.
4. Make limitations visible enough for referees to judge the strength of the work.
5. Produce a text-only `manuscript.pdf`; keep all figures and tables outside the PDF in their own folders.
6. Use simple, clear, aesthetic visual presentation in separate PDF/SVG figures.
7. Include a concise related-work/citation note when internet literature was used.
8. Use original prose. If a short direct quotation is necessary, mark it as a quote and cite the source.
9. Link each major claim to either `results.json`, a figure/table artifact, or a cited source.
10. Do not hide failed verification or weak evidence in prose.
