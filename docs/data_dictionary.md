# Data Dictionary

The most important reading rule is the grain: confirm what one row represents before joining tables or calculating a rate. Product behavior comes from the synthetic SQLite database; the FX prediction section uses the separate Yahoo Finance cache.

| Table | Grain | Important fields | Use |
|---|---|---|---|
| `users` | One row per user | signup, KYC, bank link, channel | Onboarding funnel |
| `events` | One row per raw event | user, session, timestamp, event name | Feature and behavior analysis |
| `clean_events` | One row per deduplicated event key | same as events | Analysis event source |
| `transactions` | One row per transaction attempt | amount, status, order type, regime | Activation, repeat, reliability |
| `support_tickets` | One row per ticket | issue, resolution, satisfaction | Guardrail context |
| `marketing_spend` | Campaign, date, channel, market | spend, impressions, clicks | Acquisition context |
| `fx_rates_hourly` | Currency pair and hour | OHLC, return, volatility, regime | Legacy simulated regime context; not used to train the FX model |
| `data/external/yahoo_fx_daily.csv` | Currency pair and market date | Yahoo Finance OHLC observations | FX volatility model |
| `modeling_user_month_snapshots` | User and observation month | trailing behavior, future target | Repeat prediction |
| `mart_user_lifecycle` | One row per user | first exchange, activation, feature flags | Product metrics |

The SQLite product database is synthetic. The cached Yahoo Finance file contains external historical market data and is not synthetic. Timestamp coverage differs by source, so analyses use explicit event and prediction windows.
