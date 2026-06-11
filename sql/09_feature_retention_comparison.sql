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
    'Target-rate adoption' AS comparison_type,

    CASE
        WHEN m.target_rate_user_flag = 1
            THEN 'Target-rate users'
        ELSE 'Manual-only users'
    END AS user_group,

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

GROUP BY user_group


UNION ALL


SELECT
    'Rate-alert adoption' AS comparison_type,

    CASE
        WHEN m.rate_alert_user_flag = 1
            THEN 'Rate-alert users'
        ELSE 'Non-rate-alert users'
    END AS user_group,

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

GROUP BY user_group

ORDER BY
    comparison_type,
    d30_repeat_rate DESC;