WITH first_transactions AS (
    SELECT
        user_id,
        MIN(transaction_timestamp) AS first_transaction_at
    FROM transactions
    WHERE transaction_type = 'exchange'
      AND transaction_status = 'completed'
    GROUP BY user_id
),

repeat_users AS (
    SELECT
        ft.user_id,
        MAX(
            CASE
                WHEN datetime(t.transaction_timestamp)
                     > datetime(ft.first_transaction_at, '+21 days')
                 AND datetime(t.transaction_timestamp)
                     <= datetime(ft.first_transaction_at, '+45 days')
                THEN 1
                ELSE 0
            END
        ) AS d30_repeat_flag
    FROM first_transactions ft
    LEFT JOIN transactions t
        ON ft.user_id = t.user_id
       AND t.transaction_type = 'exchange'
       AND t.transaction_status = 'completed'
    GROUP BY ft.user_id
)

SELECT
    m.acquisition_channel,
    COUNT(*) AS first_exchange_users,
    SUM(r.d30_repeat_flag) AS d30_repeat_users,
    ROUND(
        100.0 * SUM(r.d30_repeat_flag) / COUNT(*),
        2
    ) AS d30_repeat_rate
FROM mart_user_lifecycle m
JOIN repeat_users r
    ON m.user_id = r.user_id
WHERE m.onboarding_valid_flag = 1
  AND m.first_successful_transaction_at IS NOT NULL
GROUP BY m.acquisition_channel
ORDER BY d30_repeat_rate DESC;









