SELECT
    'rate_alert' AS feature,
    SUM(rate_alert_user_flag) AS adopted_users,
    COUNT(*) AS eligible_users,
    ROUND(100.0 * SUM(rate_alert_user_flag) / COUNT(*), 2) AS adoption_rate
FROM mart_user_lifecycle
WHERE onboarding_valid_flag = 1
UNION ALL
SELECT
    'target_rate_order',
    SUM(target_rate_user_flag),
    COUNT(*),
    ROUND(100.0 * SUM(target_rate_user_flag) / COUNT(*), 2)
FROM mart_user_lifecycle
WHERE onboarding_valid_flag = 1;
