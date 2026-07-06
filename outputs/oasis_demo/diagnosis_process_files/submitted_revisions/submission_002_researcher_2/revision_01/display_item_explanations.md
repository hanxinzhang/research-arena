# Display Item Explanations

## Figure 1: Sparse severity ROC curves

Artifact path: `figures/figure_1_roc_curves.pdf`
Display type: figure
Where discussed in manuscript: Display Item Guide
Article group: sparse endpoint diagnostics
Article group title: Sparse endpoint diagnostics
Article group explanation: The paired panels summarize internal discrimination and a label-permutation control for the sparse Clinical Dementia Rating endpoint. Together they show the observed model contrast and the null reference used to judge whether the signal exceeds randomized labels.
Article grouping rationale: The ROC and permutation-control figures answer the same question about whether sparse severity discrimination rises above a chance-like reference.
Panel label: a
Panel title: Discrimination
Panel order: 1
Panel columns: 2
Figure typography: article-normalized Inter
Figure mark scale: article-normalized

### Article Explanation

The ROC curves compare age, morphometry, cognitive plus morphometry, and no-MMSE sensitivity models for detecting Clinical Dementia Rating at least 1.0. The cognitive plus morphometry model has the highest internal ROC AUC.

### Purpose

Compares candidate model families for the sparse severity endpoint.

### Reader Orientation

Read the axes and legend as the primary mapping from model output to article claim; the figure does not encode unreported subgroups or hidden thresholds.

### Display Details

- The x-axis is the false-positive rate, the y-axis is the true-positive rate, and the legend reports cross-validated ROC AUC.
- Color, line, and marker styles separate model families or reference quantities.
- The cohort is the observed-label OASIS subset.

### Raw Label Translation

- CDR -> Clinical Dementia Rating.
- MMSE -> Mini-Mental State Examination.
- ROC AUC -> area under the receiver operating characteristic curve.

### Summary Conclusion

MMSE combined with morphometry gives the strongest sparse-endpoint discrimination in the demo.

### Caveat

MMSE is clinically close to the outcome construct, so the finding is not a standalone imaging discovery.

## Figure 2: Sparse-endpoint coefficient profile

Artifact path: `figures/figure_2_coefficient_profile.pdf`
Display type: figure
Where discussed in manuscript: Display Item Guide
Article group: standalone
Article grouping rationale: The coefficient profile is interpretive rather than a performance diagnostic, so it remains a standalone figure.
Panel label: 
Panel title: 
Panel order: 1
Panel columns: 2
Figure typography: article-normalized Inter
Figure mark scale: article-normalized

### Article Explanation

The coefficient profile ranks the largest standardized log-odds coefficients in the sparse-endpoint model. It shows that cognitive and morphometric features both contribute to the fitted model.

### Purpose

Shows the direction and relative size of fitted predictors for the selected sparse endpoint model.

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

The fitted model is dominated by interpretable cognitive and morphometric terms.

### Caveat

Coefficient values are descriptive and can shift under resampling or external cohorts.

## Figure 3: Negative-control comparison

Artifact path: `figures/figure_3_negative_control.pdf`
Display type: figure
Where discussed in manuscript: Display Item Guide
Article group: sparse endpoint diagnostics
Article group title: Sparse endpoint diagnostics
Article group explanation: The paired panels summarize internal discrimination and a label-permutation control for the sparse Clinical Dementia Rating endpoint. Together they show the observed model contrast and the null reference used to judge whether the signal exceeds randomized labels.
Article grouping rationale: The negative-control bar plot is grouped with the ROC curves because it provides the null context for the same primary performance claim.
Panel label: b
Panel title: Permutation control
Panel order: 2
Panel columns: 2
Figure typography: article-normalized Inter
Figure mark scale: article-normalized

### Article Explanation

The negative-control panel compares the observed sparse-endpoint ROC AUC with the mean ROC AUC from label permutations. The permutation reference is near chance and below the observed model.

### Purpose

Checks whether the observed discrimination is larger than a randomized-label reference.

### Reader Orientation

Read the axes and legend as the primary mapping from model output to article claim; the figure does not encode unreported subgroups or hidden thresholds.

### Display Details

- The y-axis reports mean ROC AUC; the permutation bar includes its standard deviation across draws.
- Color, line, and marker styles separate model families or reference quantities.
- The cohort is the observed-label OASIS subset.

### Raw Label Translation

- CDR -> Clinical Dementia Rating.
- MMSE -> Mini-Mental State Examination.
- ROC AUC -> area under the receiver operating characteristic curve.

### Summary Conclusion

The observed sparse-endpoint performance exceeds the randomized-label control.

### Caveat

Thirty permutations provide a compact-demo check rather than a definitive randomization test.

## Table 1: Model metric summary

Artifact path: `tables/model_metric_summary.csv`
Display type: table
Where discussed in manuscript: Results and Display Item Guide

### Article Explanation

Compares ROC AUC, average precision, and Brier score across sparse-endpoint models.

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

The cognitive plus morphometry model is the primary row.

### Caveat

The table supports internal compact-demo interpretation only.

## Table 2: Permutation control

Artifact path: `tables/permutation_control.csv`
Display type: table
Where discussed in manuscript: Results and Display Item Guide

### Article Explanation

Reports the observed sparse-endpoint ROC AUC and the randomized-label reference distribution.

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

The p-value is a compact permutation estimate.

### Caveat

The table supports internal compact-demo interpretation only.

## Table 3: Target sensitivity

Artifact path: `tables/target_sensitivity.csv`
Display type: table
Where discussed in manuscript: Results and Display Item Guide

### Article Explanation

Contrasts the sparse endpoint with the broader nonzero CDR endpoint.

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

The sensitivity analysis checks whether the signal depends entirely on the sparse threshold.

### Caveat

The table supports internal compact-demo interpretation only.

## Table 4: Coefficient table

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
