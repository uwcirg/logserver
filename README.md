# logserver
API and storage for logging event and audit messages, persisted in JSON
within a PostgreSQL db, with a thin frontend provided by
[PostgREST](http://postgrest.org/en/v7.0.0/index.html)

The logserver serves as the **Audit Record Repository**, as detailed in the 
Basic Audit Log Patterns
[(BALP)](https://profiles.ihe.net/ITI/BALP/volume-1.html#1-52-basic-audit-log-patterns) 
implementation guide.

## Table of Contents
- [Event Schema](#event-schema-version-30)
  - [Project Specific Examples](#example-event-schemas-in-use-for-the-respective-projects)
- [Config](#config)
- [Roles](#roles)
- [Access via JWT](#access-via-jwt)
- [API use](#api-use)
- [Advanced Query Examples](#advanced-query-examples)
- [Direct DB access](#db-access)
- [Reporting tools](#reporting-tools-that-use-data-from-logserver)

## Event Schema (version 3.0)
**logserver** is agnostic to the format, provided it is valid JSON.  Any number
of database tables can be used, but only the single `events` table is built
in, containing a PostgreSQL JSONB column,  `event`.

It is desirable to generate log events compliant with the [FHIR audit event](
https://www.hl7.org/fhir/auditevent.html) resource.  To generate an AuditEvent
resource nested within each `event` is cumbersome, however the following field
parity is recommended:

NB: all fields are considered optional unless marked as **required**

- `severity`: **required** element.  Use built in log level rather than adding
  an additional `severity` field:
  - `critical`: Critical condition with application.  Include `emergency` and
    `alert` levels in this category.
  - `error`: Error condition with the application.
  - `warning`: Warning needing attention before escalation to error.
  - `info`: Normal operational messages not requiring action.  Include
    `notice` level in this category (normal but significant).
  - `debug`: Debug level messages, useful to application developers.
- `version`: **required** logserver schema version.
- `action`: **required** element to describe the type of operation performed.
  - `create`: creating a new resource, such as adding a patient.
  - `read`: read/view/search - data retrieved or viewed w/o modification.
  - `update`: indicates existing data was modified.
  - `delete`: indicates data was removed or deleted.
  - `execute`: system or application function such as, program execution or
    perform a query/search.
  - `login`: specific category for the log-in action
  - `logout`: specific category for the log-out action
- `occurred`: Date-Time of the event, including timestamp information.  This may
    duplicate the logging system timestamp (such as `asctime`) but will always
    capture the time the event took place, not when it hit the logging server.
- `subject`: the **subject** of the activity, i.e. `Patient/ab-123-ef`
- `agent`: actor involved in the event, generally the logged-in user:
  - `ip_address`:  end user or requesting system's IP Address
  - `type`: i.e. `system` or `user`
  - `who`: i.e. `Practitioner/123-abc`
- `source`: event reporter or system generating the audit event.
  - `observer`: base URL of the system generating the audit message
  - `type`: system type such as `dhair2` or other predefined project category.
  - `version`: version of the observer (in contrast to top level `version`)
- `entity`: data or objects used
  - `detail`: list of tagged value pairs for conveying additional information.
      example pair might include `url`: `<full_url>` in contrast to `source.observer`
  - `query`: query parameters for query-type entities
- `outcome`: details in event of a failure or warning.  use `severity` to capture
  level.

### Example event schemas in use for the respective projects:

* [dhair2 - version 3](./docs/dhair2_v3.md)
* [COSRI - version 1](./docs/cosri_v1.md)
* [COSRI - version 0](./docs/cosri_v0.md)

## Config
Copy ``default.env`` to ``.env`` and edit.  Don't quote strings!

## Roles
Role | Access
-----|-------
web_anon | read only access to the API
event_logger | read / write access to the API

## Access via JWT
For write access, generate a JWT at [jwt.io](https://jwt.io/#debugger-io)

* Replace ``secret`` with the *unquoted* value of ``PGRST_JWT_SECRET``
* Replace the ``PAYLOAD: DATA`` with the appropriate role

```javascript
{
  "role": "event_logger"
}
```  

* Do NOT check the ``secret base64 encoded`` checkbox
* Save the ``Encoded`` JWT for use, passing as a bearer token:

```bash
export TOKEN=<JWT>
curl https://FQDN/events -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"event": {
    "asctime": "2020-04-26 00:33:26,731",
    "name": "sof_wrapper",
    "levelname": "INFO",
    "tags": [
      "auth",
      "login"
    ],
    "subject": "Patient/41703",
    "user": "Practitioner/SMART-1234"
    }
  }'
```

## API use
All events posted are available at:
```http request
/events
```

Sample query to fetch all events including ``login`` in the list of ``tags``:
```http request
/events?event.tags=cs.{login}
```

Sample query to fetch all events where the ``patient`` field equals ``"marcus aurelius"``:
```http request
/events?select=event&event-%3E%3Epatient=eq.marcus%20aurelius
```

Sample query to fetch events for given patient AND tag:
```http request
/events?select=event&event.tags=cs.{mme-calc}&event-%3E%3Epatient=eq.marcus%20aurelius
```

Fetch events based on datetime:
```http request
/events?select=event->>asctime,event->>message&event->>asctime=gte.2023-04-01&limit=25
```

Fetch events based on datetime, and include a number of isacc-specific fields:
```http request
/events?select=event-%3E%3Easctime,event-%3E%3Ename,event-%3E%3Emessage,event-%3E%3Eversion,event-%3E%3Elevelname,event-%3E%3ETwilio%20messages,event-%3E%3ECommunicationRequest&event-%3E%3Easctime=gte.2023-04-18&limit=25
```

See [PostgREST API](http://postgrest.org/en/v7.0.0/api.html) documentation
for additional options

## Advanced Query Examples

Example to find `letstalktech` events filtered by source.  Using 
[direct database access](#direct-db-access), look up available source
from the development logserver `logs.inform.dev.cirg.uw.edu`:

```sql
select distinct(event->'source'->>'type') from events;
    ?column?
-----------------
 dhair2/inform
 shl-ltt-server
 shl-ltt
 external-client
```

Request all events of `source->type` = `shl-ltt-server`, from the dev `letstalktech` logserver:

[https://logs.inform.dev.cirg.uw.edu/events?select=event&event->source->>type=eq.shl-ltt-server](https://logs.inform.dev.cirg.uw.edu/events?select=event&event-%3Esource-%3E%3Etype=eq.shl-ltt-server)

or the first 10 with `source_type` = `shl-ltt-server` since Jan 30, 2025:

[https://logs.inform.dev.cirg.uw.edu/events?select=event&event->source->>type=eq.shl-ltt-server&event->>occurred=gte.2025-01-30&order=event->>occurred&limit=10](https://logs.inform.dev.cirg.uw.edu/events?select=event&event-%3Esource-%3E%3Etype=eq.shl-ltt-server&event-%3E%3Eoccurred=gte.2025-01-30&order=event-%3E%3Eoccurred&limit=10)

or only the `event->occurred` from the first 10 with `source_type` = `shl-ltt` since Jan 30, 2025:

[https://logs.inform.dev.cirg.uw.edu/events?select=event->occurred&event-%3Esource->>type=eq.shl-ltt&event->>occurred=gte.2025-01-30&order=event->>occurred&limit=10](https://logs.inform.dev.cirg.uw.edu/events?select=event-%3Eoccurred&event-%3Esource-%3E%3Etype=eq.shl-ltt&event-%3E%3Eoccurred=gte.2025-01-30&order=event-%3E%3Eoccurred&limit=10)


## Direct DB Access

To access the backing postgres database, invoke `docker compose` from the
deployed directory as follows:

```
docker compose exec postgres psql postgres://app_user:secret@postgres:5432/app_db -c '\dt api.*'
```

To simplify queries, set `api` as the search path, to make it the default schema:
```sql
SET search_path TO api;
```
## Reporting tools that use data from logserver
- https://github.com/uwcirg/gwen
- https://github.com/uwcirg/logserver-tabulator
