SELECT
    COUNT(*) AS snapshot_rows,

    COUNT(DISTINCT user_id) AS users,

    MIN(observation_date) AS min_observation_date,
    MAX(observation_date) AS max_observation_date,

    SUM(target_repeat_30d) AS positive_targets,

    ROUND(
        100.0 * SUM(target_repeat_30d) / COUNT(*),
        2
    ) AS positive_target_rate,

    ROUND(AVG(recency_days), 2) AS avg_recency_days,
    ROUND(AVG(transactions_90d), 2) AS avg_transactions_90d,
    ROUND(AVG(failed_ratio_90d), 4) AS avg_failed_ratio_90d

FROM modeling_user_month_snapshots;









