# logserver
API and storage for logging event and audit messages, persisted in JSON
within a PostgreSQL db, with a thin frontend provided by
[PostgREST](http://postgrest.org/en/v7.0.0/index.html)

The logserver serves as the **Audit Record Repository**, as detailed in the 
Basic Audit Log Patterns
[(BALP)](https://profiles.ihe.net/ITI/BALP/volume-1.html#1-52-basic-audit-log-patterns) 
implementation guide.

## Event Schema
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
- `source`: event reporter or system generating the audit event including version
  - `observer`: base URL of the system generating the audit message
  - `type`: system type such as `dhair2` or other predefined project category.
  - `version`: version of the observer (in contrast to top level `version`)
- `entity`: data or objects used
  - `detail`: list of tagged value pairs for conveying additional information.
      example pair might include `url`: `<full_url>` in contrast to `source.observer`
  - `query`: query parameters for query-type entities
- `outcome`: details in event of a failure or warning.  use `severity` to capture
  level.

## Historical Schema Information Below

The following suggestions for the format of each "event" entry enable common
query syntax and meet expectations.

A distinction is made between "top level" attributes, and those nested under
"message".  The "message" may be a simple text string, or any level of valid
JSON data, intended to capture the intent of the event, such as "new consent
signed" or "search for <...> found 0 matches".  Message generally captures
the specific context from the code of the event being tracked, with all other
details collected by a routine that can collect and populate the other top
level attributes as specified below.  

Since we anticipate that events will undergo automated processing and there is only a single 'message' attribute, it seems likely that a message will have several json attributes, rather than be a simple string.  But, either is legal.

The following should be common to all events on a given system:
```json
{
    "event_version": "1", // the event schema version
    "asctime": "", // ISO-8601 format including time-zone offset
    "name": "", // Application code package name, often built in to the logging system and difficult to manipulate
    "level": "INFO", // Built in to the logging package, options also include DEBUG, WARN, ERROR
```

System identifiers to uniquely specify the source of the event:
```json
    "clinical-site": "", // unique name when appropriate to define jurisdiction, institution or clinic, such as "UW Harborview",
    "deployment": "", // one of ["dev", "test", "demo", "stage", "prod"]
    "system-type": "", // such as "remote" or "kiosk", if applicable
    "system-url": "", // system identifier URL
```

Authenticated user, or string identifier for system run jobs, etc.
```json
    "user": "User/1", // alternative nested JSON with attributes is fine; ideally consistent per application
```

If acting on an identifiable entity "subject":
```json
    "subject": "Patient/12",
```

List of topics (effectively a message "type" or "reason") useful for filtering:
```json
    "tags": ["patient", "launch", "logout", "search"], // one or more tags
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

## Reporting tools that use data from logserver
- https://github.com/uwcirg/gwen
- https://github.com/uwcirg/logserver-tabulator
