# Data

This directory is for local demo data used to exercise the Research Arena protocol.
Raw datasets are not committed to the public repository by default.

## OASIS_cross_tbl_df

Expected local file:

- `data/OASIS_cross_tbl_df.csv`

The quickstart and `examples/oasis_demo/analysis.py` expect this file to exist
locally, but the CSV itself is intentionally excluded from git. This avoids
redistributing a third-party dataset without rechecking its current license,
citation requirements, consent terms, and redistribution rules.

Source notes:

- Dataset name: `OASIS_cross_tbl_df`
- Upstream documentation: https://lightbluetitan.github.io/neurodatasets/
- Upstream source noted by NeuroDataSets: Kaggle

## How to obtain the local CSV

Use whichever route is allowed by the current upstream dataset terms.

1. Visit the upstream NeuroDataSets documentation.
2. Locate `OASIS_cross_tbl_df` and review its license/source notes.
3. Download or load the dataset according to the upstream instructions.
4. Export the table as `data/OASIS_cross_tbl_df.csv`.

If you are using R and have loaded the dataset object as `OASIS_cross_tbl_df`, one
possible export command is:

```r
write.csv(OASIS_cross_tbl_df, "data/OASIS_cross_tbl_df.csv", row.names = FALSE)
```

After export, you can run the quickstart prompt or reproduce the tiny demo:

```bash
python3 examples/oasis_demo/analysis.py
```

The prompt-run workflow uses CSV because it is human-readable and easy to audit.
Source metadata from the R documentation are summarized below.

The table has 436 observations and 12 variables:

- `ID`
- `M/F`
- `Hand`
- `Age`
- `Educ`
- `SES`
- `MMSE`
- `CDR`
- `eTIV`
- `nWBV`
- `ASF`
- `Delay`

The quickstart can pass `CDR` as optional focal-variable context. This is a demo
choice, not a Research Arena protocol requirement. Researchers may propose other
bounded questions from the same shared dataset.

## Dataset Licensing And Redistribution

Before publishing, redistributing, or using this repository with additional data,
check each source dataset's license, citation requirements, consent terms, and
redistribution rules. Do not assume that every public research dataset can be freely
redistributed or used for every purpose.

The OASIS table is a protocol demonstration input, not a clinical decision resource.
Outputs produced from it should not be interpreted as medical advice,
diagnostic evidence, causal discovery, or validated science.
