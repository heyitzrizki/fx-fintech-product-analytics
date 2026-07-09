DROP VIEW IF EXISTS clean_events;

CREATE VIEW clean_events AS
WITH ranked_events AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY user_id, session_id, event_timestamp, event_name
            ORDER BY event_id
        ) AS row_num
    FROM events
)
SELECT
    event_id, user_id, session_id, event_timestamp, event_name,
    screen_name, device_os, currency_pair, campaign_id
FROM ranked_events
WHERE row_num = 1;

DROP VIEW IF EXISTS mart_user_lifecycle;
DROP TABLE IF EXISTS analysis_mart_user_lifecycle;

CREATE TABLE analysis_mart_user_lifecycle AS
WITH successful_transactions AS (
    SELECT
        user_id,
        MIN(transaction_timestamp) AS first_successful_transaction_at,
        MAX(transaction_timestamp) AS last_successful_transaction_at,
        COUNT(*) AS successful_transaction_count,
        SUM(transaction_amount_krw) AS successful_transaction_volume,
        MAX(CASE WHEN order_type = 'target_rate' THEN 1 ELSE 0 END) AS target_rate_user_flag
    FROM transactions
    WHERE transaction_type = 'exchange' AND transaction_status = 'completed'
    GROUP BY user_id
),
rate_alert_users AS (
    SELECT user_id, 1 AS rate_alert_user_flag
    FROM events
    WHERE event_name = 'rate_alert_created'
    GROUP BY user_id
)
SELECT
    u.user_id,
    u.signup_timestamp,
    u.acquisition_channel,
    u.kyc_completed_at,
    u.bank_account_linked_at,
    st.first_successful_transaction_at,
    st.last_successful_transaction_at,
    ROUND(julianday(u.kyc_completed_at) - julianday(u.signup_timestamp), 2) AS days_to_kyc,
    ROUND(julianday(st.first_successful_transaction_at) - julianday(u.signup_timestamp), 2) AS activation_days_exact,
    ROUND((julianday(st.first_successful_transaction_at) - julianday(u.signup_timestamp)) * 24, 2) AS activation_hours,
    COALESCE(st.successful_transaction_count, 0) AS successful_transaction_count,
    COALESCE(st.successful_transaction_volume, 0) AS successful_transaction_volume,
    COALESCE(st.target_rate_user_flag, 0) AS target_rate_user_flag,
    COALESCE(ra.rate_alert_user_flag, 0) AS rate_alert_user_flag,
    CASE WHEN st.first_successful_transaction_at IS NOT NULL AND u.kyc_completed_at IS NULL THEN 0 ELSE 1 END AS onboarding_valid_flag,
    CASE
        WHEN u.kyc_completed_at IS NOT NULL
         AND u.bank_account_linked_at IS NOT NULL
         AND st.first_successful_transaction_at IS NOT NULL
         AND datetime(st.first_successful_transaction_at) <= datetime(u.signup_timestamp, '+14 days')
        THEN 1 ELSE 0
    END AS activation_flag
FROM users u
LEFT JOIN successful_transactions st ON u.user_id = st.user_id
LEFT JOIN rate_alert_users ra ON u.user_id = ra.user_id;

CREATE UNIQUE INDEX IF NOT EXISTS idx_analysis_mart_user
    ON analysis_mart_user_lifecycle(user_id);

CREATE VIEW mart_user_lifecycle AS
SELECT * FROM analysis_mart_user_lifecycle;
