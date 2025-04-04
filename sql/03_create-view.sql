CREATE OR REPLACE VIEW api.events_view AS
SELECT
    id,

    -- Schema detection (identify unique markers)
    CASE
        WHEN event->>'source_system' = 'LTT' THEN 'ltt'
        WHEN event->>'legacy_id' IS NOT NULL THEN 'legacy'
        ELSE 'unknown'
    END AS schema_version,

    -- Unified timestamp handling
    CASE
        WHEN event->>'source_system' = 'LTT' THEN
            (event->>'event_time')::TIMESTAMPTZ
        WHEN event->>'legacy_id' IS NOT NULL THEN
            TO_TIMESTAMP(event->>'created_at', 'YYYY-MM-DD HH24:MI:SS')
        ELSE NULL
    END AS occurred_at,

    -- User ID unification
    COALESCE(
        event->>'user_id',         -- LTT format
        event->>'subject',         -- Legacy format
        event->'actor'->>'id'      -- Keycloak-style
    ) AS user_id,

    -- Event type with format-specific fallbacks
    CASE
        WHEN event->>'source_system' = 'LTT' THEN
            event->>'event_type'
        ELSE
            COALESCE(
                event->>'action',
                event->>'operation'
            )
    END AS event_type,

    -- Add other fields following same pattern...

    event
FROM api.events;
ALTER VIEW api.events_view ADD COLUMN schema_version VARCHAR GENERATED ALWAYS AS (
    CASE
        WHEN event->>'loggerName' IS NOT NULL THEN 'ltt'
        WHEN event->>'asctime' IS NOT NULL THEN 'legacy'
        ELSE 'unknown'
    END
) STORED;
CREATE MATERIALIZED VIEW api.events_processed AS
SELECT * FROM api.events_view
WHERE schema_version IS NOT NULL;
