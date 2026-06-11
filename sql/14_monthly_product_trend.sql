SELECT
    strftime('%Y-%m', signup_timestamp) AS signup_month,

    COUNT(*) AS valid_signups,

    SUM(
        CASE
            WHEN kyc_completed_at IS NOT NULL THEN 1
            ELSE 0
        END
    ) AS kyc_completed,

    SUM(
        CASE
            WHEN first_successful_transaction_at IS NOT NULL THEN 1
            ELSE 0
        END
    ) AS first_successful_exchange,

    SUM(activation_flag) AS activated_within_14_days,

    ROUND(
        100.0 * SUM(activation_flag) / COUNT(*),
        2
    ) AS activation_rate_14d

FROM mart_user_lifecycle

WHERE onboarding_valid_flag = 1

GROUP BY signup_month

ORDER BY signup_month;









