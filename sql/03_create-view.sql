-- sql/03_create-view.sql

-- Drop the existing view if it exists
DROP VIEW IF EXISTS api.events_view;

-- Recreate the unified, source-filtered view
CREATE OR REPLACE VIEW api.events_view AS
SELECT
  *,
  -- pull out a single user_id field
  COALESCE(
    event->>'subject',
    event->>'user_id'
  ) AS user_id,

  -- pull out a single event_type field
  COALESCE(
    event->>'action',
    event->>'event_type'
  ) AS event_type,

  -- LTT first, then explicit version, else legacy
  CASE
    WHEN event->>'source_system' = 'LTT' THEN 'ltt'
    WHEN event->>'version' IS NOT NULL        THEN event->>'version'
    ELSE 'legacy'
  END AS schema_version,

  -- coalesce all timestamp flavors
  COALESCE(
    (event->>'event_time')::timestamptz,
    TO_TIMESTAMP( (event->>'timestamp')::bigint / 1000 ),
    TO_TIMESTAMP( event->>'created_at', 'YYYY-MM-DD HH24:MI:SS' ),
    TO_TIMESTAMP( event->>'asctime',     'YYYY-MM-DD HH24:MI:SS,MS' )
  ) AS occurred_at

FROM api.events

-- only include these source types:
WHERE event->'source'->>'type' IN (
  'dhair2/inform',
  'shl-ltt-server',
  'shl-ltt',
  'external-client'
);
