# Model Card: User Repeat

## Purpose

Rank users by likelihood of repeating an exchange in the 30 days after a monthly observation date. The score supports CRM test prioritization and service-recovery review.

## Data and split

- Unit: user-month snapshot.
- Features: recency, transaction count, transaction volume, and failed-attempt ratio from the trailing 90 days.
- Target: `target_repeat_30d` in the following 30 days.
- Validation: last 20% of observation dates; no random split.

Logistic Regression, Random Forest, XGBoost, LightGBM, and CatBoost are attempted. Optional libraries are skipped when unavailable. Selection balances ROC-AUC, PR-AUC, F1, interpretability, and reliability. The fitted artifact stores the feature list, decision threshold, and windows.

## Intended use

Use the ranking to define controlled lifecycle tests or manual service workflows. Do not deny service, set prices, or infer customer value from the score.

## Risks and monitoring

The data is synthetic. Repeated snapshots, changing channel mix, probability calibration, class balance, and feature drift require monitoring. Feature importance is not causal. Production use would require calibration, fairness review, holdout validation, and a clear contact policy.
