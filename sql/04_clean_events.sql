DROP VIEW IF EXISTS clean_events;

CREATE VIEW clean_events AS

WITH ranked_events AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY
                user_id,
                session_id,
                event_timestamp,
                event_name
            ORDER BY event_id
        ) AS row_num
    FROM events
)

SELECT
    event_id,
    user_id,
    session_id,
    event_timestamp,
    event_name,
    screen_name,
    device_os,
    currency_pair,
    campaign_id

FROM ranked_events

WHERE row_num = 1;


SELECT
    (SELECT COUNT(*) FROM events) AS raw_events,
    (SELECT COUNT(*) FROM clean_events) AS clean_events,
    (SELECT COUNT(*) FROM events)
    -
    (SELECT COUNT(*) FROM clean_events) AS removed_duplicates;