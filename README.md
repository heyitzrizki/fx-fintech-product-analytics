# FX Fintech Product Analytics

This case study examines onboarding, activation, retention, feature adoption, acquisition quality, campaign targeting, and operating readiness for a synthetic FX fintech product. It is designed around product decisions rather than model complexity.

## Business context

The core question is whether acquired users reach a first successful exchange, return, and adopt useful product features. The analysis asks:

- Where does the onboarding funnel lose users?
- Which channels produce activation and repeat behavior, not only signups?
- How do rate alerts and target-rate orders relate to retention?
- Which users should enter controlled lifecycle tests?
- Can recent FX volatility support operational preparation?

## Dataset and assumptions

`data/fx_fintech_product_analytics.db` contains synthetic users, events, transactions, support tickets, marketing spend, and monthly modeling snapshots. These product results are illustrative and do not represent any real company performance.

The volatility model uses external historical daily FX data downloaded from Yahoo Finance for USD/KRW, JPY/KRW, EUR/KRW, and SGD/KRW. The fixed snapshot is cached at `data/external/yahoo_fx_daily.csv` for reproducibility. The database also contains a legacy simulated `fx_rates_hourly` table; it is not used to train the volatility model.

Repeat prediction uses a trailing 90-day observation window through each `observation_date`; `target_repeat_30d` covers the following 30 days. D30 product retention is a separate metric: another successful exchange within 30 days after the first exchange. The model split is chronological. Campaign uplift and fee rates are explicit scenario assumptions.

The experiment section is a simulated experiment analysis to demonstrate A/B testing logic. Both assignment and outcomes are generated because no production experiment table exists, so the reported uplift is not production causal evidence.

## Analysis workflow

The main workbook is [notebooks/00_fx_fintech_product_analytics_workbook.ipynb](notebooks/00_fx_fintech_product_analytics_workbook.ipynb). It:

1. builds the clean event and user lifecycle marts;
2. checks data quality and target leakage;
3. exports funnel, cohort, feature, and channel metrics;
4. compares repeat-prediction models and creates a targeting table;
5. creates an FX volatility readiness signal;
6. evaluates a simulated onboarding experiment;
7. exports campaign scenarios and dashboard files.

The repeat-model comparison includes Logistic Regression, Random Forest, XGBoost, LightGBM, and CatBoost. Logistic Regression is retained when more complex models improve validation performance only marginally.

## Key findings

The product findings below come from synthetic behavior and demonstrate analysis and decision logic rather than actual company performance.

### Funnel and activation

- Of 44,974 valid signups, 74.28% complete KYC, 65.07% link a bank account, 57.35% complete a first exchange, and 21.45% activate within 14 days.
- Only 37.41% of first-exchange users satisfy the complete 14-day activation definition. The main opportunity is therefore activation speed, not only reaching a first exchange.
- Monthly 14-day activation rises from 9.08% for the January 2024 signup cohort to 55.18% for December 2025. This strong trend should be validated in real data because it may partly reflect the synthetic data-generation process.

### Retention and acquisition quality

- Overall D30 repeat is 52.22%, defined as another successful exchange within 30 days after the first exchange.
- Weighted monthly cohort retention declines from 49.86% in month 1 to 40.87% in month 6, indicating gradual post-exchange attrition rather than a single sharp drop.
- Referral has the highest 14-day activation rate at 23.89%, while paid social has the lowest at 19.77%.
- D30 repeat varies only from 51.15% to 53.06% across channels. Channel differences are therefore more visible before activation than after a user completes the first exchange.
- Paid social has the lowest activation but the highest D30 repeat among activated users. A practical decision is to improve paid-social onboarding before changing downstream retention messaging.

### Feature adoption and customer value

- Rate-alert adoption is 30.70%, and target-rate adoption is 34.68%.
- Rate-alert users show 65.20% D30 repeat versus 37.34% for non-users, a 27.86 percentage-point descriptive gap.
- Target-rate users show 63.51% D30 repeat versus 34.95% for manual-only users, a 28.56-point gap.
- Users adopting both features show 69.81% D30 repeat versus 29.85% for users adopting neither feature.
- The highest-volume quartile averages 22.19 successful transactions and 94.31% target-rate adoption, compared with 2.14 transactions and 26.40% adoption in the lowest quartile.
- These feature and value relationships are observational. Higher-intent users may be more likely both to adopt features and to repeat, so the gaps are hypotheses for experimentation rather than causal effects.

### Support behavior

- D30 repeat is 51.71% for users without a support ticket, 52.70% for users with one ticket, and 53.70% for users with multiple tickets.
- Support exposure is not associated with lower repeat behavior in this synthetic dataset. Ticket volume may reflect higher product activity rather than dissatisfaction alone.

### Repeat prediction and targeting

- Logistic Regression is selected with test ROC-AUC 0.777, PR-AUC 0.755, and F1 0.681.
- CatBoost records a slightly higher test ROC-AUC of 0.779 and F1 of 0.683, but the gain is too small to outweigh the simpler explanation and deployment of Logistic Regression.
- Recent transaction count is the strongest model signal, followed by recency, failed-transaction ratio, and recent volume. Importance describes model dependence, not causal effect.
- The latest targeting table contains 5,978 users with no recent transaction, 2,261 with a high failed-transaction ratio, and 104 high-value users with below-threshold repeat likelihood.

### A/B test findings (simulated)

This is a simulated experiment analysis to demonstrate A/B testing logic. Assignment and outcomes are generated because the project does not contain production experiment data.

| Metric | Control | Treatment | Absolute uplift | 95% confidence interval | P-value | Interpretation |
|---|---:|---:|---:|---:|---:|---|
| Feature adoption within 7 days | 21.64% | 26.40% | +4.76 pp | +3.98 to +5.55 pp | <0.001 | Statistically and practically significant in the simulation |
| First exchange within 14 days | 21.05% | 22.31% | +1.26 pp | +0.50 to +2.03 pp | 0.001 | Statistically significant simulated secondary effect |
| Failed transaction or support guardrail | 7.33% | 7.08% | −0.24 pp | −0.72 to +0.23 pp | 0.316 | No statistically significant simulated change |

The generated treatment group therefore shows higher feature adoption and first exchange without a detectable guardrail change. These figures demonstrate the evaluation workflow and must not be presented as evidence that an onboarding prompt would produce the same uplift in production.

### Campaign sensitivity

- The scenario audience contains 18,994 users.
- Under the explicitly assumed base case of five-point uplift, the simulator estimates approximately 950 incremental repeat users and KRW 2.27 billion of incremental volume proxy.
- Applying the base 0.025% fee proxy produces approximately KRW 567 thousand of value impact. These are directional sensitivity outputs, not revenue forecasts or causal estimates.

### Data quality

- The audit identifies 4,400 duplicated event-key rows; the `clean_events` view retains one row per event key.
- It also flags 1,675 nonpositive transaction amounts for correction and 7,337 high-volume records above the conservative KRW 8.77 million outlier threshold for review.
- Missing values are concentrated in conditionally optional fields such as campaign ID, executed rate for failed transactions, and failure reason for completed transactions. They are documented rather than automatically treated as defects.
- No selected repeat-model feature overlaps with the future target fields.

### FX market readiness

- In the synthetic product transactions, success rate declines from 92.98% in low-volatility regimes to 90.34% in high-volatility regimes, while attempts per regime hour are highest in the high regime at 3.85.
- Using historical Yahoo Finance data, the selected Random Forest with KMeans volatility regimes reaches macro F1 0.541 and balanced accuracy 0.600 on the chronological holdout.
- The moderate predictive performance supports using the model only as a readiness signal for staffing, monitoring, and messaging. It is not accurate enough to frame as an exchange-rate or trading forecast.

## Dashboard

The six pages are Executive Summary, Funnel and Retention, Feature Adoption and Simulated A/B Test, Prediction and Targeting, FX Market Readiness, and Data Quality and Methodology. Each page states the metric, decision, and caveat.

## Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Open the workbook from the repository root and run all cells:

```bash
jupyter lab notebooks/00_fx_fintech_product_analytics_workbook.ipynb
```

Run the dashboard after the notebook has produced the CSV exports:

```bash
streamlit run dashboard/app.py
```

## Documentation

- [Metric dictionary](docs/metric_dictionary.md)
- [Data dictionary](docs/data_dictionary.md)
- [Repeat model card](docs/model_card_user_repeat.md)
- [FX model card](docs/model_card_fx_volatility.md)
- [Decision log](docs/decision_log.md)
- [Limitations](docs/limitations.md)

## Limitations

Product behavior is synthetic, feature-retention comparisons are observational, experiment results are simulated, model probabilities are not production-calibrated, and campaign value is a fee proxy rather than revenue. Yahoo Finance provides real historical market observations, but the FX model has not been validated against production operating outcomes.
