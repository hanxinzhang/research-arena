# Research Arena OASIS demo summary

Run id: `oasis_demo_tiny`

Dataset: `data/OASIS_cross_tbl_df.csv`

Community:

- `researcher_1`: descriptive association study.
- `researcher_2`: simple predictive baseline study.
- `integrity_checker`: reproducibility, leakage, p-hacking, and originality audit.
- `referee_1`: methods-first review.
- `referee_2`: clarity and presentation review.
- `editor_publisher`: final selection.

## Dataset profile

The CSV contains 436 rows and 12 columns: `ID`, `M/F`, `Hand`, `Age`, `Educ`,
`SES`, `MMSE`, `CDR`, `eTIV`, `nWBV`, `ASF`, and `Delay`.

The tiny demo restricted analysis to 235 rows with observed `CDR` and `MMSE`.
Missingness is important: `Educ`, `MMSE`, and `CDR` are missing in 201 rows, and
`SES` is missing in 220 rows.

## Researcher submissions

Researcher 1 asked whether clinical dementia rating strata show a coherent
gradient across cognitive score and normalized whole-brain volume. The analysis was
descriptive and did not make causal or diagnostic claims.

Researcher 2 asked whether a very simple `MMSE` threshold could separate rows with
`CDR > 0` from rows with `CDR = 0`. This was framed as a baseline rather than a
clinical classifier.

## Outcome

Both submissions passed the basic integrity gate. Referees preferred Researcher 1
because it gave a clearer, less overclaiming account of the shared dataset and made
the limitations more visible. Researcher 2 was considered useful as a baseline but
less original and more vulnerable to criterion-overlap concerns because `MMSE` is a
cognitive score closely related to the clinical construct summarized by `CDR`.

The Editor/Publisher accepted Researcher 1.
