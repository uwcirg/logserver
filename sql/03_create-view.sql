-- sql/03_create-view.sql

DROP VIEW IF EXISTS api.events_view;
CREATE OR REPLACE VIEW api.events_view AS
SELECT
  *,  
  -- flatten user_id: pick first array element, then scalar field, then fallback
  COALESCE(
    event->'subject'->>0,    -- dhair2-style array
    event->>'subject',       -- simple string
    event->>'user_id'        -- legacy key
  ) AS user_id,

  -- flatten event_type: use explicit action first, then event_type, then tags, then message
  COALESCE(
    event->>'action',
    event->>'event_type',
    event->'tags'->>0,
    event->>'message'
  ) AS event_type,

  -- schema_version: LTT first, then version, else legacy
  CASE
    WHEN event->>'source_system' = 'LTT'   THEN 'ltt'
    WHEN event->>'version'       IS NOT NULL THEN event->>'version'
    ELSE 'legacy'
  END AS schema_version,

  -- coalesce all timestamp sources, normalizing commas to dots for asctime
  COALESCE(
    (event->>'event_time')::timestamptz,                                   -- ISO-8601
    (event->>'occurred')   ::timestamptz,                                   -- dhair2
    TO_TIMESTAMP(event->>'created_at', 'YYYY-MM-DD HH24:MI:SS'),           -- legacy
    REPLACE(event->>'asctime', ',', '.')::timestamptz,                     -- Python asctime w/ ms or zone
    TO_TIMESTAMP((event->>'timestamp')::bigint / 1000)                     -- epoch-ms
  ) AS occurred_at

FROM api.events;
