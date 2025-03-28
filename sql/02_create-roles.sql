
-- create web user w/ read only auth
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'web_anon') THEN
    create role web_anon nologin;
  END IF;
END $$;

grant usage on schema api to web_anon;
grant select on api.events to web_anon;

-- create privileged user to write events
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'event_logger') THEN
    create role event_logger nologin;
  END IF;
END $$;

grant usage on schema api to event_logger;
grant all on api.events to event_logger;
grant usage, select on sequence api.events_id_seq to event_logger;

