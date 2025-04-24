-- sql/03_create-view.sql

-- Drop old view
DROP VIEW IF EXISTS api.events_view;

-- Recreate the unified view
CREATE OR REPLACE VIEW api.events_view AS
SELECT
  *,  
  -- expose user_id & event_type
  COALESCE(event->>'subject',    event->>'user_id')    AS user_id,
  COALESCE(event->>'action',     event->>'event_type')  AS event_type,

  -- schema_version: LTT first, then any explicit version, else legacy
  CASE
    WHEN event->>'source_system' = 'LTT'   THEN 'ltt'
    WHEN event->>'version'       IS NOT NULL THEN event->>'version'
    ELSE 'legacy'
  END AS schema_version,

  -- coalesce all timestamp variants
  COALESCE(
    (event->>'event_time')::timestamptz,
    TO_TIMESTAMP((event->>'timestamp')::bigint/1000),
    TO_TIMESTAMP(event->>'created_at', 'YYYY-MM-DD HH24:MI:SS'),
    TO_TIMESTAMP(event->>'asctime',     'YYYY-MM-DD HH24:MI:SS,MS')
  ) AS occurred_at

FROM api.events

-- keep all legacy/LTT (no version field) plus only the known modern sources
WHERE
  event->>'version' IS NULL
  OR event->'source'->>'type' IN (
    'dhair2/inform',
    'shl-ltt-server',
    'shl-ltt',
    'external-client'
  );
