# Data Familiarization

Researcher: `researcher_1`

The OASIS table contains demographics, cognitive score, morphometric
measures, and Clinical Dementia Rating. The observed-label subset has
235 rows. The selected study avoids row identifiers and treats missing
CDR labels as outside the supervised analysis set.

Key variables:

- `Age`, `M/F`, `Educ`, and `SES` describe demographics.
- `MMSE` is a cognitive score.
- `eTIV`, `nWBV`, and `ASF` are morphometric or scaling measures.
- `CDR` is the outcome family used for `whether age and morphometry discriminate CDR > 0 in observed-label rows`.
