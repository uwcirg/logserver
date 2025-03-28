-- create schema used for API
create schema api;

-- create table used for log events
create table api.events (
	id serial primary key,
	event jsonb not null
);

