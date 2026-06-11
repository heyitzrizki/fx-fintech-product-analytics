SELECT
    acquisition_channel,

    COUNT(*) AS valid_signups,

    SUM(
        CASE
            WHEN kyc_completed_at IS NOT NULL THEN 1
            ELSE 0
        END
    ) AS kyc_completed,

    ROUND(
        100.0 * SUM(
            CASE
                WHEN kyc_completed_at IS NOT NULL THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS kyc_completion_rate,

    SUM(
        CASE
            WHEN bank_account_linked_at IS NOT NULL THEN 1
            ELSE 0
        END
    ) AS bank_linked,

    ROUND(
        100.0 * SUM(
            CASE
                WHEN bank_account_linked_at IS NOT NULL THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS bank_link_rate,

    SUM(
        CASE
            WHEN first_successful_transaction_at IS NOT NULL THEN 1
            ELSE 0
        END
    ) AS first_successful_exchange,

    ROUND(
        100.0 * SUM(
            CASE
                WHEN first_successful_transaction_at IS NOT NULL THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS first_exchange_rate,

    SUM(activation_flag) AS activated_within_14_days,

    ROUND(
        100.0 * SUM(activation_flag) / COUNT(*),
        2
    ) AS activation_rate_14d

FROM mart_user_lifecycle

WHERE onboarding_valid_flag = 1

GROUP BY acquisition_channel

ORDER BY activation_rate_14d DESC;









