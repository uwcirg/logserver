-- sql/03_create-view.sql

-- Drop existing view if it exists
DROP VIEW IF EXISTS api.events_view;

-- Create a single, unified view
CREATE OR REPLACE VIEW api.events_view AS
SELECT *,

  -- Use the explicit 'version' field when present, else mark as 'legacy'
  -- Reducing the number of CASE statements
  CASE
    WHEN event->>'version' IS NOT NULL THEN event->>'version'
    ELSE 'legacy'
  END AS schema_version,

  -- Coalesce all possible timestamp sources into one timestamptz
  COALESCE(
    -- New-standard field
    (event->>'event_time')::timestamptz,
    -- Keycloak’s epoch‐ms timestamp
    TO_TIMESTAMP( (event->>'timestamp')::bigint / 1000 ),
    -- Older created_at string
    TO_TIMESTAMP( event->>'created_at', 'YYYY-MM-DD HH24:MI:SS' ),
    -- Python asctime format (with milliseconds)
    TO_TIMESTAMP( event->>'asctime', 'YYYY-MM-DD HH24:MI:SS,MS' )
  ) AS occurred_at

FROM api.events;
