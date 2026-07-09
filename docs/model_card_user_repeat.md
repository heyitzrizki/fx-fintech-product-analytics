# Model Card: User Repeat

## Purpose

Rank users by likelihood of repeating an exchange in the 30 days after a monthly observation date. The score supports CRM test prioritization and service-recovery review.

## Data and split

- Unit: user-month snapshot.
- Features: recency, transaction count, transaction volume, and failed-attempt ratio from the trailing 90 days.
- Target: `target_repeat_30d` in the following 30 days.
- Split: first 70% of observation dates for training, next 15% for threshold and model selection, and final 15% for chronological testing.

Logistic Regression, Random Forest, XGBoost, LightGBM, and CatBoost are included in the reproducible model comparison. CatBoost is selected as the performance winner using validation ROC-AUC, with validation PR-AUC as the tie-breaker. Logistic Regression remains the interpretability baseline. The fitted artifact stores the feature list, decision threshold, and windows.

## Intended use

Use the ranking to define controlled lifecycle tests or manual service workflows. Do not deny service, set prices, or infer customer value from the score.

## Risks and monitoring

The data is synthetic. Repeated snapshots, changing channel mix, probability calibration, class balance, and feature drift require monitoring. Feature importance is not causal. Production use would require calibration, fairness review, holdout validation, and a clear contact policy.
