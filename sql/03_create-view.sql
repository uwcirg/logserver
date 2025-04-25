-- sql/03_create-view.sql

DROP VIEW IF EXISTS api.events_view;
CREATE OR REPLACE VIEW api.events_view AS
SELECT
  *,  
  -- flatten user_id 
  COALESCE(
    event->>'subject',
    event->>'user_id',
    event->'subject'->>0
  ) AS user_id,

  -- flatten event_type: action, event_type, message, or first tag
  COALESCE(
    event->>'action',
    event->>'event_type',
    event->>'message',
    event->'tags'->>0
  ) AS event_type,

  -- schema_version: LTT first, then version, else legacy
  CASE
    WHEN event->>'source_system' = 'LTT'   THEN 'ltt'
    WHEN event->>'version'       IS NOT NULL THEN event->>'version'
    ELSE 'legacy'
  END AS schema_version,

  -- coalesce all timestamp sources, normalizing commas to dots for asctime
  -- keep as text so '+00' isn’t lost by psycopg2
  (COALESCE(
    (event->>'event_time')::timestamptz,
    (event->>'occurred')    ::timestamptz,
    TO_TIMESTAMP(event->>'created_at', 'YYYY-MM-DD HH24:MI:SS'),
    REPLACE(event->>'asctime', ',', '.')::timestamptz,
    TO_TIMESTAMP((event->>'timestamp')::bigint / 1000)
  )::timestamptz)::text AS occurred_at

FROM api.events
WHERE
  event->>'version' IS NULL
  OR event->'source'->>'type' IN (
    'dhair2/inform',
    'shl-ltt-server',
    'shl-ltt',
    'external-client',
    'isacc-project',
    'other-approved'
  );
