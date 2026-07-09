WITH first_exchange AS (
    SELECT
        user_id,
        date(MIN(transaction_timestamp), 'start of month') AS cohort_month
    FROM transactions
    WHERE transaction_type = 'exchange' AND transaction_status = 'completed'
    GROUP BY user_id
),
activity AS (
    SELECT DISTINCT
        t.user_id,
        f.cohort_month,
        date(t.transaction_timestamp, 'start of month') AS activity_month
    FROM transactions t
    JOIN first_exchange f USING (user_id)
    WHERE t.transaction_type = 'exchange' AND t.transaction_status = 'completed'
),
cohort_size AS (
    SELECT cohort_month, COUNT(*) AS cohort_users
    FROM first_exchange
    GROUP BY cohort_month
)
SELECT
    a.cohort_month,
    (CAST(strftime('%Y', a.activity_month) AS INTEGER) - CAST(strftime('%Y', a.cohort_month) AS INTEGER)) * 12
      + CAST(strftime('%m', a.activity_month) AS INTEGER) - CAST(strftime('%m', a.cohort_month) AS INTEGER)
      AS months_since_first_transaction,
    c.cohort_users,
    COUNT(DISTINCT a.user_id) AS retained_users,
    ROUND(100.0 * COUNT(DISTINCT a.user_id) / c.cohort_users, 2) AS retention_rate
FROM activity a
JOIN cohort_size c USING (cohort_month)
GROUP BY a.cohort_month, months_since_first_transaction, c.cohort_users
ORDER BY a.cohort_month, months_since_first_transaction;
