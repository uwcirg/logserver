-- sql/03_create-view.sql

-- Drop the existing view if it exists
DROP VIEW IF EXISTS api.events_view;

-- Recreate the unified view, exposing user_id and event_type for testing
CREATE OR REPLACE VIEW api.events_view AS
SELECT
  *,
  -- Extract user_id and event_type from the JSON
  event->>'subject' AS user_id,
  event->>'action'  AS event_type,

  -- Determine schema version: use explicit 'version' field when present
  CASE
    WHEN event->>'version' IS NOT NULL THEN event->>'version'
    ELSE 'legacy'
  END AS schema_version,

  -- Consolidate all timestamp formats into one timestamptz
  COALESCE(
    -- new schema field
    (event->>'event_time')::timestamptz,
    -- Keycloak timestamp (ms since epoch)
    TO_TIMESTAMP((event->>'timestamp')::bigint / 1000),
    -- legacy created_at string
    TO_TIMESTAMP(event->>'created_at', 'YYYY-MM-DD HH24:MI:SS'),
    -- Python asctime format (with milliseconds)
    TO_TIMESTAMP(event->>'asctime', 'YYYY-MM-DD HH24:MI:SS,MS')
  ) AS occurred_at

FROM api.events;
