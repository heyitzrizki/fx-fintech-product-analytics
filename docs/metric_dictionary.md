# Metric Dictionary

| Metric | Definition | Denominator or window |
|---|---|---|
| Valid signup | User without an invalid onboarding sequence | Eligible users |
| KYC completion rate | Users with `kyc_completed_at` | Valid signups |
| Bank-link rate | Users with `bank_account_linked_at` | Valid signups |
| First exchange rate | Users with a completed exchange | Valid signups |
| 14-day activation rate | KYC, bank link, and first completed exchange within 14 days of signup | Valid signups |
| D30 repeat rate | Users with another completed exchange 21–45 days after first exchange | First-exchange users |
| Rate-alert adoption | Users with `rate_alert_created` | Eligible users |
| Target-rate adoption | Users with a completed or attempted target-rate order | Eligible users |
| Cohort retention | Users active in month N after first-exchange month | First-exchange cohort |
| Transaction success rate | Completed exchange attempts | All exchange attempts |
| Repeat prediction target | At least one repeat in the next 30 days | Monthly user snapshots |
| Feature adoption experiment metric | Rate-alert or target-rate adoption within 7 days | Randomized users |
| Guardrail event rate | Failed transaction or support ticket within 30 days | Randomized users |

Feature comparisons are descriptive. Experiment metrics require randomized production instrumentation for causal interpretation.
