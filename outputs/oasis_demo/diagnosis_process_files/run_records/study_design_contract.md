# Study Design Contract

Dataset: `data/OASIS_cross_tbl_df.csv`

Researchers may choose different questions. No shared target is required.
Before analysis, each Researcher must inspect the data, run a small pilot,
write candidate studies, choose one proposal, and submit it to the Study
Design Board.

Leakage guardrails:

- do not use row identifiers as predictors;
- disclose missing Clinical Dementia Rating labels;
- keep claims internal to this table;
- use cross-validation or resampling for performance estimates;
- include at least one robustness, sensitivity, calibration, bootstrap, or
  negative-control check by revision_01.
