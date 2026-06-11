SELECT
    COUNT(*) AS duplicate_event_records
FROM (
    SELECT
        user_id,
        session_id,
        event_timestamp,
        event_name
    FROM events
    GROUP BY
        user_id,
        session_id,
        event_timestamp,
        event_name
    HAVING COUNT(*) > 1
);