# Integrity report

Scope: tiny OASIS demo example.

## Checks

- Reproducibility: pass. The reported statistics are deterministic summaries from
  `data/OASIS_cross_tbl_df.csv`.
- Data leakage: pass. Researcher 1 used `CDR` as a grouping variable, not as a
  predictor in a model. Researcher 2 used `CDR > 0` as the label and `MMSE` as the
  predictor; this is not file-level leakage, but it has conceptual overlap and must
  be stated as a limitation.
- P-hacking risk: low for Researcher 1, moderate for Researcher 2 because multiple
  possible thresholds could be tried. The example reports the selected threshold as
  a baseline and does not claim it was optimized for external validity.
- Selective reporting: acceptable. Weaknesses and missingness are stated.
- Originality/plagiarism risk: pass. No external prose, figures, tables, or study
  framing were copied. No literature citations were used in this tiny demo.
- Safety: pass. No clinical, diagnostic, or causal claims are made.

## Required limitations

- Only 235 of 436 rows had observed `CDR` and `MMSE`.
- `SES` had additional missingness.
- The `CDR = 2` group had only 2 observed rows.
- Results are descriptive and exploratory.
