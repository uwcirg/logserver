# logserver
API and storage for logging, event and audit messages, persisted in JSON
within a PostgreSQL db, with a thin frontend provided by
[PostgREST](http://postgrest.org/en/v7.0.0/index.html)

## Event Schema
*logserver* is agnostic to format of events, provided it's valid JSON.  The
following suggestions enable common query syntax and expectations:

A distinction is made between "top level" attributes, and those nested under
"message".  The "message" may be a simple text string, or any level of valid
JSON data, intended to capture the intent of the event, such a "patient/12 deleted" or "search for {...} found 0 matches".

Tags is a list of strings defining general event types, with the intent to
make filtering or searching easy.

All other top level attributes are generally consistent on any given system,
defining the source, user, system type, time of event, etc.

```json
{
"version": "1", // the event schema version, not the application version
"asctime": "", // ISO-8601 format including time-zone offset, preferably in UTC

```

1. Top level attributes, such as "version" and "asctime", are typically
consistent across all event types.  For example, "user" is generally the
authenticated user, and available on most all events.
2. "message", itself a top level attribute, captures the unique nature of
the event being logged.  Examples might include "session created" or "question 1.1 skipped" and may also include any number of nested fields.
3. "tags", itself a top level attribute, captures single term identifiers,
useful in filtering.  Examples include "search", "logout", "patient", etc.
4. "name", often derrived from the code module executing, not easily controlled.
5. "clinical-site", unique name when appropriate to define jurisdiction, institution or clinic, such as "UW Harborview"
6. "deployment", one of ["dev", "test", "demo", "stage", "prod"]
7. "system-type", such as "remote" or "kiosk"
8. "system-name", system identifier URL

Project - Version examples for formatting `events`

* [COSRI - version 0](./docs/cosri_v0.md)
* [COSRI - version 1](./docs/cosri_v1.md)

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

See [PostgREST API](http://postgrest.org/en/v7.0.0/api.html) documentation
for additional options
