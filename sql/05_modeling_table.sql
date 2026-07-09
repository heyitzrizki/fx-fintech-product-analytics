-- Each row is a monthly user snapshot.
-- Features summarize the trailing 90 days through observation_date.
-- target_repeat_30d is measured in the following 30 days and is never used as a feature.
SELECT
    user_id,
    observation_date,
    recency_days,
    transactions_90d,
    total_volume_90d,
    failed_ratio_90d,
    target_repeat_30d
FROM modeling_user_month_snapshots;
