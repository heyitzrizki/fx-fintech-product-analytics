# Data Quality Log

## Overview

Data quality checks were performed before building the analytical marts. The objective was to ensure that key business metrics such as funnel conversion, activation, repeat behavior, and transaction success were not distorted by duplicated events, orphan records, inconsistent timestamps, or invalid onboarding sequences.

The raw data was preserved, while analytical flags and cleaned views were created for downstream analysis.

## Database Validation

The SQLite database was validated across seven tables.

| Table | Row Count |
|---|---:|
| users | 45,000 |
| events | 2,204,400 |
| transactions | 261,679 |
| fx_rates_hourly | 70,176 |
| marketing_spend | 9,238 |
| support_tickets | 18,000 |
| modeling_user_month_snapshots | 206,376 |

The database contains more than 2.8 million records across user, event, transaction, FX market, marketing, support, and modeling tables.

## Duplicate Event Check

Duplicate product event groups were checked using the following business keys:

- `user_id`
- `session_id`
- `event_timestamp`
- `event_name`

Result:

| Check | Issue Count |
|---|---:|
| duplicate event groups | 4,400 |

## Clean Events Layer

A cleaned analytical view named `clean_events` was created using `ROW_NUMBER()` to retain one record per duplicated event group.

| Layer | Row Count |
|---|---:|
| raw events | 2,204,400 |
| clean events | 2,200,000 |
| removed duplicates | 4,400 |

Action taken:

```text
Raw events were preserved.
Duplicate records were removed only in the clean_events analytical view.
```

This prevents duplicated events from overstating feature adoption and product engagement metrics.

## Referential Integrity Checks

### Orphan Events

Events were checked against the `users` table.

| Check | Issue Count |
|---|---:|
| orphan event records | 0 |

Result:

```text
No event records were found without a matching user_id.
```

### Transactions Before Signup

Transactions were checked to ensure that no transaction occurred before the user's signup timestamp.

| Check | Issue Count |
|---|---:|
| transactions before signup | 0 |

Result:

```text
No transactions occurred before signup.
```

## Transaction Consistency Checks

### Completed Exchange Without Executed Rate

Completed exchange transactions were checked for missing executed rates.

| Check | Issue Count |
|---|---:|
| completed exchanges without executed_rate | 0 |

Result:

```text
All completed exchange transactions had an executed rate.
```

### Failed Exchange With Executed Rate

Failed exchange transactions were checked to ensure they did not have executed rates.

| Check | Issue Count |
|---|---:|
| failed exchanges with executed_rate | 0 |

Result:

```text
No failed exchange transactions had an executed rate.
```

## Onboarding Sequence Validation

A user-level onboarding validity flag was created in `mart_user_lifecycle`.

Invalid onboarding sequence definition:

```text
A user has a successful exchange transaction, but no completed KYC timestamp.
```

Result:

| Onboarding Valid Flag | Users |
|---|---:|
| 0 - invalid onboarding sequence | 26 |
| 1 - valid onboarding sequence | 44,974 |

Further breakdown:

| Invalid User Timing | Users |
|---|---:|
| Successful exchange within 14 days | 15 |
| Successful exchange after 14 days | 11 |

Action taken:

```text
Invalid onboarding users were not deleted from the raw data.
They were flagged with onboarding_valid_flag = 0 and excluded from onboarding and activation KPI calculations.
```

## Final Data Quality Summary

| Check | Result |
|---|---:|
| Duplicate event groups | 4,400 |
| Orphan event records | 0 |
| Transactions before signup | 0 |
| Completed exchanges without executed rate | 0 |
| Failed exchanges with executed rate | 0 |
| Invalid onboarding sequence users | 26 |

## Analytical Decision

The project uses two layers:

```text
Raw data layer:
Preserves all original synthetic records.

Analytical layer:
Uses clean_events and mart_user_lifecycle to support reliable KPI calculations.
```

For funnel and activation metrics, only users with:

```sql
onboarding_valid_flag = 1
```

were included.

## Data Quality Interpretation

The dataset was generally consistent and suitable for product analytics. The main data quality issues were duplicated event records and a small number of invalid onboarding sequences. These issues were handled through an analytical cleaning layer rather than raw data deletion.

This approach preserves raw data integrity while ensuring that product metrics such as activation, feature adoption, and repeat behavior are calculated consistently.
