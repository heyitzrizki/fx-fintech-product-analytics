SELECT
    COUNT(*) AS valid_signups,

    SUM(
        CASE
            WHEN kyc_completed_at IS NOT NULL THEN 1
            ELSE 0
        END
    ) AS kyc_completed,

    SUM(
        CASE
            WHEN bank_account_linked_at IS NOT NULL THEN 1
            ELSE 0
        END
    ) AS bank_linked,

    SUM(
        CASE
            WHEN first_successful_transaction_at IS NOT NULL THEN 1
            ELSE 0
        END
    ) AS first_successful_exchange,

    SUM(activation_flag) AS activated_within_14_days

FROM mart_user_lifecycle
WHERE onboarding_valid_flag = 1;