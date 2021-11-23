-- create schema used for API
create schema api;

-- create table used for log events
create table api.events (
	id serial primary key,
	event jsonb not null
);

-- create web user w/ read only auth
create role web_anon nologin;
grant usage on schema api to web_anon;
grant select on api.events to web_anon;

-- create privileged user to write events
create role event_logger nologin;
grant usage on schema api to event_logger;
grant all on api.events to event_logger;
grant usage, select on sequence api.events_id_seq to event_logger;

