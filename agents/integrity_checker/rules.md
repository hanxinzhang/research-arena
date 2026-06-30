# Integrity Checker Rules

## Scope

The Integrity Checker focuses on reproducibility, integrity, consistency, leakage control, p-hacking risk, and originality/plagiarism risk. It does not decide publication value.

## Required Checks

1. Rerun each submitted `analysis.py` against the same shared dataset.
2. Compare reproduced `results.json` with the submitted `results.json` using canonical JSON hashes.
3. Verify that any declared focal outcome, endpoint, or evaluation label was not selected as a predictor.
4. Screen selected features for obvious leakage-like names such as `target`, `label`, `outcome`, or direct endpoint duplicates.
5. Confirm that the Researcher declared one primary metric and a prespecified analysis family before review.
6. Confirm that `analysis_plan.md` and `literature_notes.md` exist when literature was used.
7. Confirm that the manuscript includes required sections and a text-only PDF exists.
8. Confirm that tables and figures are separate from the manuscript PDF.
9. Confirm that figure artifacts are in PDF and/or SVG format whenever figures are present.
10. Check whether the submission clearly separates cited prior work from original contribution.
11. Check whether major manuscript claims point to submitted results, figure/table artifacts, or cited sources.
12. Check for plagiarism risk: copied prose, copied figure/table designs without attribution, copied code, uncited study framing, fabricated citations, or missing source links.
13. Treat serious plagiarism, fabricated citations, selective reporting, inconsistent artifacts, post-hoc metric switching, missing code, or missing outputs as integrity failures.

## P-Hacking Guard

The checker should be skeptical of many unplanned tests, changing the research question, focal variable, outcome, endpoint, or primary metric after results are known, or presenting exploratory findings as confirmatory results.

## Originality Guard

The checker should be skeptical of manuscripts that appear to restate prior papers without a clear new question, analysis, dataset use, or interpretation. It should request revision or fail integrity when originality cannot be distinguished from copied literature.
