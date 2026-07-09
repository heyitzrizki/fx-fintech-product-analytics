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

`data/fx_fintech_product_analytics.db` contains synthetic users, events, transactions, support tickets, marketing spend, and monthly modeling snapshots. These product results are illustrative and are not Switchwon performance.

The volatility model uses external historical daily FX data downloaded from Yahoo Finance for USD/KRW, JPY/KRW, EUR/KRW, and SGD/KRW. The fixed snapshot is cached at `data/external/yahoo_fx_daily.csv` for reproducibility. The database also contains a legacy simulated `fx_rates_hourly` table; it is not used to train the volatility model.

Repeat prediction uses a trailing 90-day observation window through each `observation_date`; `target_repeat_30d` covers the following 30 days. The validation split is chronological. Campaign uplift and fee rates are explicit scenario assumptions. The A/B test assignment and outcomes are simulated because no production experiment table exists.

## Analysis workflow

The main workbook is [notebooks/00_fx_fintech_product_analytics_workbook.ipynb](notebooks/00_fx_fintech_product_analytics_workbook.ipynb). It:

1. builds the clean event and user lifecycle marts;
2. checks data quality and target leakage;
3. exports funnel, cohort, feature, and channel metrics;
4. compares repeat-prediction models and creates a targeting table;
5. creates an FX volatility readiness signal;
6. evaluates a simulated onboarding experiment;
7. exports campaign scenarios and dashboard files.

Key descriptive findings in the supplied synthetic data:

- 9,649 of 44,974 valid signups activate within 14 days (21.45%).
- Feature users have higher observed D30 repeat rates, but the relationship is not causal.
- High-volatility periods have a lower transaction success rate than low-volatility periods.
- Channel quality should be assessed with activation and repeat rate together.

## Dashboard

The six pages are Executive Summary, Funnel and Retention, Feature Adoption and A/B Test, Prediction and Targeting, FX Market Readiness, and Data Quality and Methodology. Each page states the metric, decision, and caveat.

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
