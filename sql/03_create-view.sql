-- Create standardized event view with legacy support
CREATE OR REPLACE VIEW api.events_view AS
SELECT
    id,
    CASE
        WHEN (event->>'timestamp') ~ '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d+Z$'
            THEN (event->>'timestamp')::TIMESTAMPTZ
        WHEN (event->>'asctime') IS NOT NULL
            THEN TO_TIMESTAMP(event->>'asctime', 'YYYY-MM-DD HH24:MI:SS.MS')::TIMESTAMPTZ
        ELSE NULL
    END AS occurred_at,
    COALESCE(
        event->>'event_type',
        event->>'type',
        event->>'name'
    ) AS event_type,
    COALESCE(
        event->>'user_id',
        event->>'sub',
        event->>'user'
    ) AS user_id,
    COALESCE(
        event->>'client_id',
        event->>'client'
    ) AS client_id,
    COALESCE(
        event->>'severity',
        event->>'level'
    ) AS severity,
    CASE
        WHEN event->>'duration_ms' ~ '^\d+$' 
            THEN (event->>'duration_ms')::INTEGER
        ELSE NULL
    END AS duration_ms,
    COALESCE(
        event->>'status',
        event->>'result'
    ) AS status,
    event
FROM api.events;

