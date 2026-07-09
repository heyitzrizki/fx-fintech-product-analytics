# Limitations

- Product behavior in the SQLite database is synthetic and cannot establish actual company performance.
- Feature adoption and retention associations are vulnerable to self-selection and user-intent confounding.
- The A/B test assignment and outcomes are simulated; results demonstrate analysis code only.
- The repeat model is validated on synthetic monthly snapshots and is not calibrated for production decisions.
- The campaign simulator assumes uplift, recent volume, and fee proxies. It is not a revenue forecast.
- FX regime prediction uses historical Yahoo Finance observations, but it has not been linked to measured operational benefit.
- D30 repeat counts another successful exchange after the first exchange and no later than day 30.
- Missing fields may be conditionally optional. A nonzero missing count is not automatically an error.
- Transaction volume outliers are flagged using Q3 plus three IQRs and retained unless domain review finds invalid records.

Recommended next steps are production metric validation, experiment instrumentation, calibrated holdout evaluation, contact-policy guardrails, and drift monitoring.
