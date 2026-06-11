WITH user_value AS (
    SELECT
        m.user_id,
        m.acquisition_channel,
        m.target_rate_user_flag,
        m.rate_alert_user_flag,
        COUNT(t.transaction_id) AS successful_transactions,
        SUM(t.transaction_amount_krw) AS total_volume_krw,
        SUM(t.fee_amount_krw) AS total_fee_krw
    FROM mart_user_lifecycle m
    JOIN transactions t
        ON m.user_id = t.user_id
    WHERE m.onboarding_valid_flag = 1
      AND t.transaction_type = 'exchange'
      AND t.transaction_status = 'completed'
    GROUP BY
        m.user_id,
        m.acquisition_channel,
        m.target_rate_user_flag,
        m.rate_alert_user_flag
),

ranked_users AS (
    SELECT
        *,
        NTILE(4) OVER (
            ORDER BY total_volume_krw
        ) AS value_quartile
    FROM user_value
)

SELECT
    CASE value_quartile
        WHEN 1 THEN 'Q1 lowest volume'
        WHEN 2 THEN 'Q2'
        WHEN 3 THEN 'Q3'
        WHEN 4 THEN 'Q4 highest volume'
    END AS value_segment,

    COUNT(*) AS users,

    ROUND(AVG(successful_transactions), 2) AS avg_successful_transactions,
    ROUND(AVG(total_volume_krw), 0) AS avg_total_volume_krw,
    ROUND(AVG(total_fee_krw), 0) AS avg_total_fee_krw,

    ROUND(
        100.0 * AVG(target_rate_user_flag),
        2
    ) AS target_rate_adoption_rate,

    ROUND(
        100.0 * AVG(rate_alert_user_flag),
        2
    ) AS rate_alert_adoption_rate

FROM ranked_users

GROUP BY value_quartile

ORDER BY value_quartile;









