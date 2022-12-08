# logserver
API and storage for logging event and audit messages, persisted in JSON
within a PostgreSQL db, with a thin frontend provided by
[PostgREST](http://postgrest.org/en/v7.0.0/index.html)

## Event Schema
**logserver** is agnostic to the format of events, provided it's valid JSON.
The following suggestions enable common query syntax and meet expectations.

A distinction is made between "top level" attributes, and those nested under
"message".  The "message" may be a simple text string, or any level of valid
JSON data, intended to capture the intent of the event, such as "new consent
signed" or "search for <...> found 0 matches".

Tags is a list of strings defining general event types, with the intent to
make filtering or searching easy.

All other top level attributes are generally consistent on any given system,
defining the source, user, system type, time of event, etc.

The following should be common to all events and are generally built in:
```json
{
    "version": "1", // the event schema version, not the application version
    "asctime": "", // ISO-8601 format including time-zone offset, preferably in UTC
    "name": "", // Application code package name, often built in to the logging system and difficult to manipulate
    "level": "INFO", // Built in to the logging package, typical values include DEBUG, WARN, ERROR
```

System identifiers to uniquely specify the source of the event. 
```json
    "clinical-site": "", // unique name when appropriate to define jurisdiction, institution or clinic, such as "UW Harborview",
    "deployment": "", // one of ["dev", "test", "demo", "stage", "prod"]
    "system-type": "", // such as "remote" or "kiosk"
    "system-name": "", // system identifier URL
```

If acting on an identifiable entity "subject", such as "Patient/12"
```json
    "subject": "Patient/12
```

List of topics useful for filtering
```json
    "tags": ["patient", "launch", "logout", "search"], // one or more
```

And finally, and details in the message itself, that aren't captured above,
nesting any valid JSON within message if appropriate.  The details captured
in the "message" often come from deep in the application stack, where all of
the above isn't so easily obtained.
```json
    "message": "Description of action" // replace string with nested JSON when applicable 
}
```

### Example event schemas in use for the respective projects:

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
