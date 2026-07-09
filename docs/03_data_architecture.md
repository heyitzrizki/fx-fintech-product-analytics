# Data Architecture

## Overview

This project uses a relational SQLite database designed to simulate a foreign exchange fintech product analytics environment. The database connects user onboarding, product events, exchange transactions, FX market conditions, acquisition data, customer support interactions, and modeling-ready user snapshots.

The analytical workflow follows this structure:

```text
Raw relational tables
→ data quality checks
→ cleaned event layer
→ user lifecycle mart
→ funnel, retention, feature, FX regime, and value analysis
→ dashboard and predictive modeling outputs
```

## Source Tables

### 1. users

The `users` table contains user profile and onboarding information.

Main fields:

- `user_id`
- `signup_timestamp`
- `country`
- `city_type`
- `age_group`
- `device_os`
- `acquisition_channel`
- `campaign_id`
- `preferred_currency_pair`
- `kyc_status`
- `kyc_completed_at`
- `bank_account_linked_at`

Analytical use:

- signup analysis
- onboarding funnel
- acquisition channel comparison
- activation measurement
- user-level mart construction

### 2. events

The `events` table contains product interaction logs.

Main fields:

- `event_id`
- `user_id`
- `session_id`
- `event_timestamp`
- `event_name`
- `screen_name`
- `device_os`
- `currency_pair`
- `campaign_id`

Analytical use:

- product behavior analysis
- rate-alert adoption
- event-level product engagement
- cleaned event layer construction

A cleaned analytical view named `clean_events` was created to remove duplicate event records.

### 3. transactions

The `transactions` table contains exchange transaction attempts and outcomes.

Main fields:

- `transaction_id`
- `user_id`
- `transaction_timestamp`
- `currency_pair`
- `transaction_type`
- `order_type`
- `transaction_amount_krw`
- `quoted_rate`
- `executed_rate`
- `fee_amount_krw`
- `cashback_krw`
- `transaction_status`
- `failure_reason`
- `processing_seconds`
- `market_regime_at_transaction`

Analytical use:

- first successful exchange
- activation analysis
- D30 repeat behavior
- transaction success rate
- failure reason analysis
- FX regime behavior
- customer value segmentation

### 4. fx_rates_hourly

The `fx_rates_hourly` table contains simulated hourly FX data used only for legacy descriptive regime joins and activity normalization. The volatility prediction model instead uses the cached Yahoo Finance daily snapshot in `data/external/yahoo_fx_daily.csv`.

Main fields:

- `timestamp`
- `currency_pair`
- `open_rate`
- `high_rate`
- `low_rate`
- `close_rate`
- `log_return`
- `rolling_volatility_24h`
- `market_regime`

Analytical use:

- FX market regime analysis
- volatility-based transaction behavior
- transaction intensity normalization by regime hour

### 5. marketing_spend

The `marketing_spend` table contains simulated campaign-level acquisition spend.

Main fields:

- `date`
- `campaign_id`
- `channel`
- `market`
- `spend_krw`
- `impressions`
- `clicks`

Analytical use:

- acquisition channel context
- campaign-level growth analysis
- potential CAC and marketing efficiency analysis

In this phase, acquisition channel quality was mainly analyzed through the `users` table and lifecycle outcomes.

### 6. support_tickets

The `support_tickets` table contains customer support interactions.

Main fields:

- `ticket_id`
- `user_id`
- `created_at`
- `issue_type`
- `resolution_time_hours`
- `resolved_flag`
- `satisfaction_score`

Analytical use:

- support interaction analysis
- support ticket impact on repeat behavior
- issue-type segmentation for future analysis

### 7. modeling_user_month_snapshots

The `modeling_user_month_snapshots` table contains monthly user-level features prepared for predictive modeling.

Main fields:

- `user_id`
- `observation_date`
- `recency_days`
- `transactions_90d`
- `transactions_all`
- `total_volume_90d`
- `failed_ratio_90d`
- `target_repeat_30d`

Analytical use:

- predictive modeling readiness check
- repeat transaction prediction
- user-level classification modeling

## Logical Relationships

The main user-level analytical relationships are:

```text
users.user_id
→ events.user_id
→ transactions.user_id
→ support_tickets.user_id
→ modeling_user_month_snapshots.user_id
```

Additional analytical joins:

```text
transactions.market_regime_at_transaction
→ fx_rates_hourly.market_regime
```

```text
users.acquisition_channel / campaign_id
→ marketing_spend.channel / campaign_id
```

The `users` table is the central entity for onboarding, activation, feature adoption, and retention analysis.

## Analytical Views and Marts

### clean_events

The `clean_events` view removes duplicated product event records based on:

- `user_id`
- `session_id`
- `event_timestamp`
- `event_name`

This view was created to avoid overstating product engagement metrics.

### mart_user_lifecycle

The `mart_user_lifecycle` view consolidates user-level onboarding, activation, transaction, and feature adoption metrics.

Main fields include:

- signup timestamp
- acquisition channel
- KYC completion timestamp
- bank account linking timestamp
- first successful transaction timestamp
- last successful transaction timestamp
- activation timing
- successful transaction count
- successful transaction volume
- target-rate user flag
- rate-alert user flag
- onboarding validity flag
- 14-day activation flag

This mart is the core analytical layer used for funnel, activation, acquisition channel, feature adoption, retention, and customer value analysis.

## Data Architecture Summary

The database supports the product analytics workflow:

```text
User acquisition
→ onboarding
→ first exchange
→ repeat transaction
→ feature adoption
→ customer value
→ support interaction
→ predictive modeling
```

This architecture allows the analysis to move beyond signup volume and evaluate deeper product quality, including activation, repeat behavior, feature engagement, and transaction reliability.
