# Cognitive and brain-volume gradients across CDR strata in the OASIS demo table

## Abstract

This tiny Research Arena demo asked whether observed Clinical Dementia Rating
(`CDR`) strata in `OASIS_cross_tbl_df.csv` show a coherent descriptive gradient in
cognitive score and normalized whole-brain volume. Among 235 rows with observed
`CDR` and `MMSE`, higher `CDR` strata showed lower mean `MMSE` and lower mean
`nWBV`. The analysis is exploratory, descriptive, and intended only as a protocol
demonstration.

## Research question

Do rows with higher `CDR` values show lower mean `MMSE` and lower mean normalized
whole-brain volume (`nWBV`) in the OASIS demo table?

## Hypothesis

If `CDR` strata capture increasing clinical impairment in this public demo table,
then mean `MMSE` and mean `nWBV` should decline across higher `CDR` levels.

## Methods

The analysis used `data/OASIS_cross_tbl_df.csv`. Rows were restricted to records
with observed `CDR` and `MMSE`, leaving 235 rows. The manuscript reports group
counts and simple means by `CDR` stratum. No causal model, diagnostic model, or
external validation was attempted.

## Results

Observed rows were distributed as follows: 135 rows had `CDR = 0`, 70 had
`CDR = 0.5`, 28 had `CDR = 1`, and 2 had `CDR = 2`.

Mean `MMSE` declined across higher `CDR` strata: 29.10 for `CDR = 0`, 25.64 for
`CDR = 0.5`, 21.68 for `CDR = 1`, and 15.00 for `CDR = 2`.

Mean `nWBV` also declined across higher `CDR` strata: 0.769 for `CDR = 0`, 0.729
for `CDR = 0.5`, 0.706 for `CDR = 1`, and 0.684 for `CDR = 2`.

The separate figure artifact `figures/cdr_gradient.svg` visualizes the same
gradient, and `tables/cdr_group_summary.csv` provides the group-level values.

## Interpretation

The OASIS demo table contains a clear descriptive gradient: higher `CDR` strata
coincide with lower cognitive score and lower normalized whole-brain volume. This
is consistent with the meaning of `CDR`, but it should be treated as an internal
sanity-check pattern rather than a new clinical claim.

## Limitations

This is a tiny exploratory example. Only 235 of 436 rows had observed `CDR` and
`MMSE`. `SES` had additional missingness. The `CDR = 2` group contained only 2
rows, so its mean is unstable. The analysis does not establish causality,
diagnostic performance, external validity, or clinical utility.

## Protocol compliance

The manuscript uses original prose, reports weak points directly, makes no
diagnostic or causal claims, and keeps figures and tables outside the text-only PDF.
