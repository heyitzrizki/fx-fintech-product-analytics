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
),

support_summary AS (
    SELECT
        user_id,
        COUNT(*) AS ticket_count,
        AVG(resolution_time_hours) AS avg_resolution_time_hours,
        AVG(satisfaction_score) AS avg_satisfaction_score
    FROM support_tickets
    GROUP BY user_id
)

SELECT
    CASE
        WHEN ss.user_id IS NULL
            THEN 'No support ticket'
        WHEN ss.ticket_count = 1
            THEN 'One support ticket'
        ELSE 'Multiple support tickets'
    END AS support_group,

    COUNT(*) AS first_exchange_users,
    SUM(r.d30_repeat_flag) AS d30_repeat_users,

    ROUND(
        100.0 * SUM(r.d30_repeat_flag) / COUNT(*),
        2
    ) AS d30_repeat_rate,

    ROUND(AVG(ss.avg_resolution_time_hours), 2) AS avg_resolution_time_hours,
    ROUND(AVG(ss.avg_satisfaction_score), 2) AS avg_satisfaction_score

FROM mart_user_lifecycle m

JOIN repeat_users r
    ON m.user_id = r.user_id

LEFT JOIN support_summary ss
    ON m.user_id = ss.user_id

WHERE m.onboarding_valid_flag = 1
  AND m.first_successful_transaction_at IS NOT NULL

GROUP BY support_group

ORDER BY
    CASE support_group
        WHEN 'No support ticket' THEN 1
        WHEN 'One support ticket' THEN 2
        WHEN 'Multiple support tickets' THEN 3
    END;









