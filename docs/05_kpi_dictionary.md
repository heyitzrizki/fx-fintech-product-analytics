# KPI Dictionary

## Overview

This document defines the key metrics used in the FX Fintech Product Analytics Case Study. The purpose is to ensure that all funnel, activation, retention, feature adoption, FX regime, and customer value metrics are calculated consistently.

## 1. Valid Signup

### Definition

A valid signup is a user included in onboarding and activation analysis after excluding invalid onboarding sequences.

### SQL Logic

```sql
onboarding_valid_flag = 1
```

### Final Count

```text
Valid signups = 44,974
```

### Business Meaning

Valid signups represent the user base used for reliable funnel and activation measurement.

## 2. KYC Completed

### Definition

A user is considered KYC completed if the user has a non-null KYC completion timestamp.

### SQL Logic

```sql
kyc_completed_at IS NOT NULL
```

### Final Count

```text
KYC completed = 33,406
```

### Business Meaning

This measures how many valid users completed the identity verification step.

## 3. Bank Linked

### Definition

A user is considered bank linked if the user has a non-null bank account linking timestamp.

### SQL Logic

```sql
bank_account_linked_at IS NOT NULL
```

### Final Count

```text
Bank linked = 29,264
```

### Business Meaning

This measures how many valid users completed the required financial account connection step before exchange activity.

## 4. First Successful Exchange

### Definition

A user is counted as having a first successful exchange if the user has at least one completed exchange transaction.

### SQL Logic

```sql
transaction_type = 'exchange'
AND transaction_status = 'completed'
```

At the user level:

```sql
MIN(transaction_timestamp) AS first_successful_transaction_at
```

### Final Count

```text
First successful exchange users = 25,791
```

### Business Meaning

This is the key product activation milestone showing that a user moved from onboarding into actual exchange behavior.

## 5. Activation Within 14 Days

### Definition

A user is activated within 14 days if the user:

1. completed KYC,
2. linked a bank account,
3. completed at least one successful exchange, and
4. completed the first successful exchange within 14 days after signup.

### SQL Logic

```sql
CASE
    WHEN kyc_completed_at IS NOT NULL
     AND bank_account_linked_at IS NOT NULL
     AND first_successful_transaction_at IS NOT NULL
     AND datetime(first_successful_transaction_at)
         <= datetime(signup_timestamp, '+14 days')
    THEN 1
    ELSE 0
END AS activation_flag
```

### Final Count

```text
Activated within 14 days = 9,649
```

### Final Rate

```text
14-day activation rate = 21.45%
```

### Business Meaning

This measures how quickly users reach meaningful product value after signup.

## 6. Funnel Conversion Rate

### Definition

Funnel conversion rate measures the percentage of valid signups reaching each onboarding stage.

### Formula

```text
Stage conversion rate = users at stage / valid signups
```

### Final Funnel

| Stage | Users | Conversion from Valid Signup |
|---|---:|---:|
| Valid signups | 44,974 | 100.00% |
| KYC completed | 33,406 | 74.28% |
| Bank linked | 29,264 | 65.07% |
| First successful exchange | 25,791 | 57.35% |
| Activated within 14 days | 9,649 | 21.45% |

### Business Meaning

This identifies where users drop off during onboarding and activation.

## 7. Previous-Step Conversion Rate

### Definition

Previous-step conversion measures the percentage of users moving from one funnel stage to the next.

### Formula

```text
Previous-step conversion = users at current stage / users at previous stage
```

### Final Rates

| Transition | Conversion Rate |
|---|---:|
| Signup to KYC | 74.28% |
| KYC to bank linked | 87.60% |
| Bank linked to first exchange | 88.13% |
| First exchange to 14-day activation | 37.41% |

### Business Meaning

This shows that the largest bottleneck occurs in fast activation after the first successful exchange.

## 8. D30 Repeat User

### Definition

A D30 repeat user is a user who completes another successful exchange around one month after the first successful exchange.

### SQL Logic

```sql
datetime(transaction_timestamp) > datetime(first_transaction_at, '+21 days')
AND datetime(transaction_timestamp) <= datetime(first_transaction_at, '+45 days')
```

### Business Meaning

FX transactions may not happen every day, so a 21-to-45-day window is used instead of requiring activity on exactly day 30.

## 9. D30 Repeat Rate

### Definition

D30 repeat rate is the percentage of first-exchange users who complete another successful exchange within the D30 repeat window.

### Formula

```text
D30 repeat rate = D30 repeat users / first-exchange users
```

### Business Meaning

This measures whether users return to the product after their first successful transaction.

## 10. Target-Rate User

### Definition

A target-rate user is a user who has used at least one target-rate exchange order.

### SQL Logic

```sql
MAX(
    CASE
        WHEN order_type = 'target_rate' THEN 1
        ELSE 0
    END
) AS target_rate_user_flag
```

### Result

| Group | First-Exchange Users | D30 Repeat Rate |
|---|---:|---:|
| Manual-only users | 10,196 | 26.02% |
| Target-rate users | 15,595 | 52.00% |

### Business Meaning

Target-rate adoption is a strong behavioral signal associated with repeat exchange activity.

### Caveat

This is an observational association and should not be interpreted as causal without controlled testing.

## 11. Rate-Alert User

### Definition

A rate-alert user is a user who created at least one rate alert event.

### SQL Logic

```sql
event_name = 'rate_alert_created'
```

At the user level:

```sql
rate_alert_user_flag = 1
```

### Result

| Group | First-Exchange Users | D30 Repeat Rate |
|---|---:|---:|
| Non-rate-alert users | 12,014 | 26.70% |
| Rate-alert users | 13,777 | 54.84% |

### Business Meaning

Rate-alert adoption is a strong behavioral signal associated with repeat exchange activity.

### Caveat

This is observational and may reflect higher user intent or monitoring behavior.

## 12. Combined Feature Adoption

### Definition

Users are grouped based on whether they adopted target-rate orders and/or rate-alert features.

### Groups

```text
Both target-rate and rate-alert
Rate-alert only
Target-rate only
Neither feature
```

### Result

| Feature Group | First-Exchange Users | D30 Repeat Rate |
|---|---:|---:|
| Both target-rate and rate-alert | 10,884 | 59.04% |
| Rate-alert only | 2,893 | 39.03% |
| Target-rate only | 4,711 | 35.75% |
| Neither feature | 7,303 | 20.87% |

### Business Meaning

Combined feature adoption is the strongest observed retention signal in the analysis.

### Caveat

The relationship is observational and should be validated through experimentation.

## 13. Transaction Success Rate

### Definition

Transaction success rate measures the share of exchange attempts that were completed successfully.

### Formula

```text
Transaction success rate = completed exchange transactions / total exchange attempts
```

### FX Regime Result

| FX Regime | Success Rate |
|---|---:|
| Low volatility | 92.98% |
| Normal volatility | 91.84% |
| High volatility | 90.34% |

### Business Meaning

Transaction success rate indicates execution reliability across market conditions.

## 14. FX Market Regime

### Definition

FX market regime classifies market conditions based on simulated FX volatility.

### Regime Values

```text
low
normal
high
```

### Business Meaning

FX regimes are used to compare user transaction behavior and success rate under different market volatility conditions.

## 15. Attempts per Regime Hour

### Definition

Attempts per regime hour normalizes raw transaction attempts by the number of available FX regime hours.

### Formula

```text
Attempts per regime hour = transaction attempts in regime / number of FX hourly rows in regime
```

### Result

| Regime | Attempts per Regime Hour |
|---|---:|
| Low | 3.72 |
| Normal | 3.61 |
| High | 3.85 |

### Business Meaning

This avoids overinterpreting raw transaction counts when some regimes occur more often than others.

## 16. Failure Reason Share

### Definition

Failure reason share measures the distribution of failed exchange reasons within each FX regime.

### Formula

```text
Failure reason share = failed transactions for reason / total failed transactions in regime
```

### Main Finding

Across all regimes, the top failure reasons were:

```text
1. insufficient_balance
2. rate_changed
3. bank_timeout
```

### Business Meaning

The decline in success rate during high-volatility regimes is not driven by a dramatically different failure mix.

## 17. Customer Value Segment

### Definition

Customer value segments are quartiles based on each user's total completed exchange volume.

### SQL Logic

```sql
NTILE(4) OVER (
    ORDER BY total_volume_krw
) AS value_quartile
```

### Segments

```text
Q1 lowest volume
Q2
Q3
Q4 highest volume
```

### Result

| Segment | Avg Transactions | Avg Volume KRW | Target-Rate Adoption | Rate-Alert Adoption |
|---|---:|---:|---:|---:|
| Q1 lowest volume | 2.14 | 1,699,953 | 26.40% | 22.35% |
| Q2 | 4.80 | 6,016,026 | 49.72% | 42.70% |
| Q3 | 7.92 | 14,725,808 | 71.45% | 61.54% |
| Q4 highest volume | 22.19 | 61,286,989 | 94.31% | 87.09% |

### Business Meaning

High-value users are more frequent, higher-volume, and more feature-engaged users.

## 18. Support Ticket Group

### Definition

Users are grouped based on the number of support tickets.

### Groups

```text
No support ticket
One support ticket
Multiple support tickets
```

### Result

| Support Group | First-Exchange Users | D30 Repeat Rate |
|---|---:|---:|
| No support ticket | 15,153 | 41.06% |
| One support ticket | 8,042 | 41.98% |
| Multiple support tickets | 2,596 | 44.88% |

### Business Meaning

Support tickets did not correspond to lower repeat behavior in this synthetic dataset. Ticket volume may partly reflect higher engagement rather than dissatisfaction alone.

## 19. Modeling Target

### Definition

The modeling target is `target_repeat_30d`, which indicates whether a user repeats within the prediction window.

### Modeling Table Summary

| Metric | Value |
|---|---:|
| Snapshot rows | 206,376 |
| Distinct users | 23,387 |
| Observation date range | 2024-06-30 to 2025-11-30 |
| Positive targets | 84,459 |
| Positive target rate | 40.92% |
| Average recency days | 63.51 |
| Average transactions 90d | 2.28 |
| Average failed ratio 90d | 0.0526 |

### Business Meaning

The modeling table is ready for predictive modeling of repeat transaction behavior using user-level monthly snapshots.

## Final Note

All KPIs are calculated from a synthetic dataset. The results are intended for portfolio demonstration and analytical storytelling, not as actual company performance.
