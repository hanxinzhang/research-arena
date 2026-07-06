# Display Item Explanations

## Figure 1: Nonzero CDR ROC curves

Artifact path: `figures/figure_1_roc_curves.pdf`
Display type: figure
Where discussed in manuscript: Display Item Guide
Article group: nonzero cdr diagnostics
Article group title: Nonzero CDR model diagnostics
Article group explanation: The paired panels summarize discrimination and calibration for the nonzero Clinical Dementia Rating endpoint. The ROC panel compares age, morphometry, and the combined demographic model, while the calibration panel shows whether predicted probabilities track observed prevalence across probability bins.
Article grouping rationale: The ROC and calibration figures describe complementary performance properties for the same endpoint and are easier to compare as a two-panel article figure.
Panel label: a
Panel title: Discrimination
Panel order: 1
Panel columns: 2
Figure typography: article-normalized Inter
Figure mark scale: article-normalized

### Article Explanation

The ROC curves compare internal cross-validated discrimination for age alone, morphometry alone, and morphometry with demographics. The combined model is above the chance line and provides the strongest nonzero CDR signal in this compact analysis.

### Purpose

Compares the candidate model families for the primary nonzero CDR endpoint.

### Reader Orientation

Read the axes and legend as the primary mapping from model output to article claim; the figure does not encode unreported subgroups or hidden thresholds.

### Display Details

- The x-axis is the false-positive rate, the y-axis is the true-positive rate, and the legend reports cross-validated ROC AUC for each model.
- Color, line, and marker styles separate model families or reference quantities.
- The cohort is the observed-label OASIS subset.

### Raw Label Translation

- CDR -> Clinical Dementia Rating.
- MMSE -> Mini-Mental State Examination.
- ROC AUC -> area under the receiver operating characteristic curve.

### Summary Conclusion

Adding morphometry and demographic information improves discrimination relative to age alone.

### Caveat

The curves are internal cross-validation estimates from the observed-label subset, not external validation.

## Figure 2: Coefficient profile

Artifact path: `figures/figure_2_coefficient_profile.pdf`
Display type: figure
Where discussed in manuscript: Display Item Guide
Article group: standalone
Article grouping rationale: The coefficient profile is a model-interpretation display and is best read after the performance panels.
Panel label: 
Panel title: 
Panel order: 1
Panel columns: 2
Figure typography: article-normalized Inter
Figure mark scale: article-normalized

### Article Explanation

The coefficient profile shows the largest standardized log-odds coefficients in the combined nonzero CDR model. It identifies which scaled predictors drive the internal discrimination signal while preserving the exploratory scope of the compact demo.

### Purpose

Summarizes the direction and relative size of the strongest fitted coefficients.

### Reader Orientation

Read the axes and legend as the primary mapping from model output to article claim; the figure does not encode unreported subgroups or hidden thresholds.

### Display Details

- The x-axis is the fitted log-odds coefficient and the y-axis lists human-readable predictor names.
- Color, line, and marker styles separate model families or reference quantities.
- The cohort is the observed-label OASIS subset.

### Raw Label Translation

- CDR -> Clinical Dementia Rating.
- MMSE -> Mini-Mental State Examination.
- ROC AUC -> area under the receiver operating characteristic curve.

### Summary Conclusion

The strongest coefficients are compatible with an age and morphometry signal, but they remain descriptive.

### Caveat

Coefficient magnitude can be unstable in small, correlated tabular datasets.

## Figure 3: Calibration alignment

Artifact path: `figures/figure_3_calibration.pdf`
Display type: figure
Where discussed in manuscript: Display Item Guide
Article group: nonzero cdr diagnostics
Article group title: Nonzero CDR model diagnostics
Article group explanation: The paired panels summarize discrimination and calibration for the nonzero Clinical Dementia Rating endpoint. The ROC panel compares age, morphometry, and the combined demographic model, while the calibration panel shows whether predicted probabilities track observed prevalence across probability bins.
Article grouping rationale: The calibration figure belongs with the ROC figure because both evaluate the same primary model behavior from different angles.
Panel label: b
Panel title: Calibration
Panel order: 2
Panel columns: 2
Figure typography: article-normalized Inter
Figure mark scale: article-normalized

### Article Explanation

The calibration panel compares average predicted probability with observed nonzero CDR prevalence across quantile bins. The fitted probabilities are not perfectly calibrated, but the bins generally follow the expected ordering.

### Purpose

Checks whether predicted risks are aligned with observed outcome frequency.

### Reader Orientation

Read the axes and legend as the primary mapping from model output to article claim; the figure does not encode unreported subgroups or hidden thresholds.

### Display Details

- The x-axis is mean predicted probability, the y-axis is observed prevalence, and the diagonal line marks ideal calibration.
- Color, line, and marker styles separate model families or reference quantities.
- The cohort is the observed-label OASIS subset.

### Raw Label Translation

- CDR -> Clinical Dementia Rating.
- MMSE -> Mini-Mental State Examination.
- ROC AUC -> area under the receiver operating characteristic curve.

### Summary Conclusion

The combined model shows useful ordering with imperfect calibration.

### Caveat

Only five bins were used, so calibration should be interpreted qualitatively.

## Table 1: Model metric summary

Artifact path: `tables/model_metric_summary.csv`
Display type: table
Where discussed in manuscript: Results and Display Item Guide

### Article Explanation

Compares ROC AUC, average precision, and Brier score across candidate nonzero CDR models.

### Purpose

Provides the numerical values supporting the manuscript text and figure interpretation.

### Reader Orientation

Rows should be read as reported model, endpoint, or coefficient summaries rather than independent external-validation records.

### Display Details

- Rows: model, endpoint, coefficient, or robustness quantities depending on the table.
- Columns: human-readable metrics, values, row counts, or feature names.
- Units: probabilities, ROC AUC, average precision, Brier score, or log-odds coefficients.
- Denominators: observed-label OASIS rows used by the current revision.

### Raw Label Translation

- CDR -> Clinical Dementia Rating.
- MMSE -> Mini-Mental State Examination.
- ROC AUC -> area under the receiver operating characteristic curve.

### Summary Conclusion

The combined morphometry and demographic model is the primary row.

### Caveat

The table supports internal compact-demo interpretation only.

## Table 2: Calibration bins

Artifact path: `tables/calibration_table.csv`
Display type: table
Where discussed in manuscript: Results and Display Item Guide

### Article Explanation

Reports mean predicted probability, observed prevalence, and row count for probability bins.

### Purpose

Provides the numerical values supporting the manuscript text and figure interpretation.

### Reader Orientation

Rows should be read as reported model, endpoint, or coefficient summaries rather than independent external-validation records.

### Display Details

- Rows: model, endpoint, coefficient, or robustness quantities depending on the table.
- Columns: human-readable metrics, values, row counts, or feature names.
- Units: probabilities, ROC AUC, average precision, Brier score, or log-odds coefficients.
- Denominators: observed-label OASIS rows used by the current revision.

### Raw Label Translation

- CDR -> Clinical Dementia Rating.
- MMSE -> Mini-Mental State Examination.
- ROC AUC -> area under the receiver operating characteristic curve.

### Summary Conclusion

The rows summarize calibration rather than independent validation.

### Caveat

The table supports internal compact-demo interpretation only.

## Table 3: Coefficient table

Artifact path: `tables/coefficient_table.csv`
Display type: table
Where discussed in manuscript: Results and Display Item Guide

### Article Explanation

Lists fitted log-odds coefficients with human-readable predictor names.

### Purpose

Provides the numerical values supporting the manuscript text and figure interpretation.

### Reader Orientation

Rows should be read as reported model, endpoint, or coefficient summaries rather than independent external-validation records.

### Display Details

- Rows: model, endpoint, coefficient, or robustness quantities depending on the table.
- Columns: human-readable metrics, values, row counts, or feature names.
- Units: probabilities, ROC AUC, average precision, Brier score, or log-odds coefficients.
- Denominators: observed-label OASIS rows used by the current revision.

### Raw Label Translation

- CDR -> Clinical Dementia Rating.
- MMSE -> Mini-Mental State Examination.
- ROC AUC -> area under the receiver operating characteristic curve.

### Summary Conclusion

The coefficients are descriptive summaries from a compact internal model.

### Caveat

The table supports internal compact-demo interpretation only.
