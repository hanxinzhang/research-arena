# Analysis Plan

The analysis estimates cross-validated logistic regression models for
`CDR >= 1.0` using the observed-label OASIS rows. Numeric
predictors are median-imputed and standardized. Sex is mode-imputed and
one-hot encoded. Class weights are balanced because the endpoint
prevalence is uneven.

The minimum experiment rows are a baseline model, a richer model, and
an issue-linked robustness or sensitivity check. The plan records ROC
AUC, average precision, Brier score, model coefficients, figures, and
CSV tables for reproducibility.
