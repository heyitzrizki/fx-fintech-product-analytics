-- List all tables
SELECT name
FROM sqlite_master
WHERE type = 'table'
ORDER BY name;

-- Validate row counts
SELECT 'users' AS table_name, COUNT(*) AS row_count FROM users
UNION ALL
SELECT 'events', COUNT(*) FROM events
UNION ALL
SELECT 'transactions', COUNT(*) FROM transactions
UNION ALL
SELECT 'fx_rates_hourly', COUNT(*) FROM fx_rates_hourly
UNION ALL
SELECT 'marketing_spend', COUNT(*) FROM marketing_spend
UNION ALL
SELECT 'support_tickets', COUNT(*) FROM support_tickets
UNION ALL
SELECT 'modeling_user_month_snapshots', COUNT(*) FROM modeling_user_month_snapshots;