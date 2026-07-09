SELECT
    COUNT(*) AS valid_signups,
    SUM(kyc_completed_at IS NOT NULL) AS kyc_completed,
    SUM(bank_account_linked_at IS NOT NULL) AS bank_linked,
    SUM(first_successful_transaction_at IS NOT NULL) AS first_successful_exchange,
    SUM(activation_flag) AS activated_within_14_days
FROM mart_user_lifecycle
WHERE onboarding_valid_flag = 1;
