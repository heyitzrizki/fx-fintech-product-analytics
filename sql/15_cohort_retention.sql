WITH user_first_transaction AS (
    SELECT
        user_id,
        MIN(transaction_timestamp) AS first_transaction_at
    FROM transactions
    WHERE transaction_type = 'exchange'
      AND transaction_status = 'completed'
    GROUP BY user_id
),

user_transactions AS (
    SELECT
        t.user_id,
        date(uft.first_transaction_at, 'start of month') AS cohort_month,
        date(t.transaction_timestamp, 'start of month') AS transaction_month,

        (
            CAST(strftime('%Y', t.transaction_timestamp) AS INTEGER)
            - CAST(strftime('%Y', uft.first_transaction_at) AS INTEGER)
        ) * 12
        +
        (
            CAST(strftime('%m', t.transaction_timestamp) AS INTEGER)
            - CAST(strftime('%m', uft.first_transaction_at) AS INTEGER)
        ) AS months_since_first_transaction

    FROM transactions t

    JOIN user_first_transaction uft
        ON t.user_id = uft.user_id

    JOIN mart_user_lifecycle m
        ON t.user_id = m.user_id

    WHERE t.transaction_type = 'exchange'
      AND t.transaction_status = 'completed'
      AND m.onboarding_valid_flag = 1
),

cohort_size AS (
    SELECT
        cohort_month,
        COUNT(DISTINCT user_id) AS cohort_users
    FROM user_transactions
    WHERE months_since_first_transaction = 0
    GROUP BY cohort_month
)

SELECT
    ut.cohort_month,
    ut.months_since_first_transaction,
    cs.cohort_users,
    COUNT(DISTINCT ut.user_id) AS retained_users,

    ROUND(
        100.0 * COUNT(DISTINCT ut.user_id) / cs.cohort_users,
        2
    ) AS retention_rate

FROM user_transactions ut

JOIN cohort_size cs
    ON ut.cohort_month = cs.cohort_month

WHERE ut.months_since_first_transaction BETWEEN 0 AND 6

GROUP BY
    ut.cohort_month,
    ut.months_since_first_transaction,
    cs.cohort_users

ORDER BY
    ut.cohort_month,
    ut.months_since_first_transaction;









