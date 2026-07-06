# Cognitive and morphometric signal for sparse dementia severity in a compact OASIS demo

## Abstract

Background: Research Arena is intended to make automated research runs
inspectable, revision-aware, and publication-shaped without hiding
process evidence. We tested that framework on a compact OASIS demo using
a local cross-sectional table and a bounded article bar. Methods: The
analysis used the 235 rows with observed Clinical Dementia Rating labels,
excluded row identifiers from predictors, and evaluated cross-validated
logistic regression models for CDR >= 1.0. Results: The primary
model, Cognitive plus morphometry, had ROC AUC 0.919, average precision
0.591, and Brier score 0.111. The observed sparse-endpoint ROC AUC was 0.919, whereas the permutation-control mean was 0.485 with standard deviation 0.067. The compact permutation p-value was 0.032. The broader CDR > 0 sensitivity endpoint had ROC AUC 0.910. Conclusions: The run
produced a coherent compact-demo article package with executable analysis,
figure/table explanations, and reviewable limitations. The claims are
internal to the demo data and do not establish clinical deployment
readiness.

## Introduction

Automated research systems can produce attractive prose while leaving
readers uncertain about what was actually computed, who made a judgment,
and whether revisions changed the evidence. This compact article uses the
OASIS table as a deliberately small test of a stricter workflow. The
scientific question is narrow: Does adding MMSE to morphometry improve detection of Clinical Dementia Rating at least 1.0? The workflow question is
broader: whether an end-to-end run can preserve proposal-gate reasoning,
executed analysis, reviewer issues, and final article presentation in a
package that a human reader can audit.

Clinical Dementia Rating, abbreviated CDR, is a coarse measure of dementia
severity. The table also includes age, MMSE, estimated total intracranial
volume, normalized whole-brain volume, atlas scaling factor, and basic
demographic fields. These variables make the dataset suitable for a
compact discrimination example because the expected signal is plausible,
but the table is not large or independent enough to justify broad medical
claims. The article therefore treats all performance estimates as internal
cross-validation results.

## Methods

The analysis began only after the Study Design Board approved a Phase 0
proposal for this Researcher. Rows without observed CDR were excluded from
modeling, leaving 235 rows. The endpoint was CDR >= 1.0, giving
30 rows with Clinical Dementia Rating at least 1.0 among 235 observed-label rows. The scripts used a logistic regression
pipeline with median imputation and standard scaling for numeric
predictors, mode imputation and one-hot encoding for sex, and balanced
class weights to reduce the effect of class imbalance. The cross-validated
probability estimates were produced with five stratified folds.

For row \(i\), the fitted probability model can be written as:

\begin{equation}
\widehat{\Pr}(Y_i = 1 \mid X_i) =
\operatorname{logit}^{-1}\left(\beta_0 + \sum_{j=1}^p X_{ij}\beta_j\right).
\label{eq:logistic-model}
\end{equation}

Here \(Y_i\) is the binary CDR endpoint and \(X_{ij}\) is a processed
predictor after imputation, scaling, and encoding. The primary
discrimination metrics were ROC AUC and average precision. The Brier score
summarized probability-scale error. Coefficients were fit once on the full
observed-label subset after cross-validated performance estimation so the
manuscript could describe predictor direction and relative magnitude
without using those coefficients as independent validation evidence.

The analysis scripts wrote stable results, CSV tables, PDF figures,
compute logs, and experiment registries. A revision-level empirical
provenance record declares that the latest empirical artifacts were rerun
in the current revision. The compute reconciliation records that the
compact analysis finished below the planning target because the approved
models were small; the Editor can accept that only as an efficiency
override, not as evidence of a larger study.

## Results

The primary analysis found that the cognitive plus morphometry model showed strong internal discrimination for the sparse severity endpoint the permutation-control distribution stayed near chance, supporting that the observed signal was not a label-order artifact a target-sensitivity analysis showed that the signal remained visible when the endpoint was broadened to nonzero CDR. Across model rows, Age only had ROC AUC 0.644, average precision 0.199, and Brier score 0.235; Morphometry plus age had ROC AUC 0.794, average precision 0.332, and Brier score 0.191; Cognitive plus morphometry had ROC AUC 0.919, average precision 0.591, and Brier score 0.111; No-MMSE sensitivity check had ROC AUC 0.797, average precision 0.344, and Brier score 0.187.
The primary model had ROC AUC 0.919, average precision 0.591, and
Brier score 0.111. The observed sparse-endpoint ROC AUC was 0.919, whereas the permutation-control mean was 0.485 with standard deviation 0.067. The compact permutation p-value was 0.032. The broader CDR > 0 sensitivity endpoint had ROC AUC 0.910.

The result is consistent with a strong internal cognitive and morphometric severity signal, but it is also clinically unsurprising because MMSE is close to the outcome construct. The acceptable claim is therefore not that an imaging-only biomarker has been discovered, but that the framework recovered a coherent and auditable tabular demonstration with an explicit null reference. These estimates should be read as a compact internal
benchmark. They show that the data and modeling path are coherent enough
for a demonstration article, and they also show why the article must not
overclaim. The endpoint distribution, missing CDR labels, and absence of
external validation all limit the strength of inference.

## Display Item Guide

Figure 1 reports discrimination for the candidate model families. The
axes use false-positive rate and true-positive rate, and the legend gives
ROC AUC values in article-readable labels. Figure 2 reports the coefficient
profile for the selected model, using standardized log-odds coefficients
and human-readable feature names rather than internal variable tokens.
Figure 3 provides the main robustness or calibration display for the same
endpoint. The tables give the numerical metric summary, supporting
robustness values, and fitted coefficients. Together, the display items
separate the performance claim, the interpretive coefficient claim, and
the caveat that this is an internal compact demo. The article PDF includes
short explanatory paragraphs directly under each display-item title, while
the standalone figure and table files remain inspectable in their folders.

## Discussion

This run demonstrates a bounded article workflow rather than a finished
clinical study. The most important scientific result is not the absolute
value of a single metric; it is the alignment between an approved question,
executable analysis, reviewer-visible robustness checks, and a final
manuscript that states only what the evidence supports. The model results
are plausible for the OASIS table and are presented with enough supporting
files to make the calculation traceable.

The analysis also shows the benefit of the framework's separation of
roles. The Researcher owns the analysis and manuscript. The Study Design
Board owns the pre-analysis gate. Referees and the Integrity Checker own
issue records. The Editor owns the final decision. That separation matters
because a polished article should not erase disagreement, limitations, or
process evidence.

## Limitations

The dataset is small, cross-sectional, and incomplete with respect to CDR.
The models are linear logistic regressions rather than a search over all
plausible clinical prediction strategies. The analysis does not use an
external validation cohort, does not assess calibration drift, and does
not make causal claims. MMSE is especially close to the outcome construct,
so any model using MMSE should be interpreted as a cognitive-severity
demonstration rather than a discovery of an independent biomarker. The
compact-demo compute budget also limits the number of resampling and
sensitivity analyses.

## Reproducibility

All analysis code is in `analysis.py` for the revision. Stable numerical
outputs are in `stable_results.json`, display tables are in `tables/`, and
standalone vector figures are in `figures/`. The rendered review
manuscript is `manuscript.pdf`; the integrated journal-style output is
`article/article.pdf`. The figure presentation audit checks that figure
text and marks are normalized to the article scale.

## References

1. OASIS project documentation for cross-sectional MRI and clinical table
variables.
2. Morris JC. The Clinical Dementia Rating scale and staging of dementia.
3. Harrell FE. Regression modeling strategies and internal validation
principles.
