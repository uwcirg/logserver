# logserver
API and storage for logging, event and audit messages, persisted in JSON
within a PostgreSQL db, with a thin frontend provided by
[PostgREST](http://postgrest.org/en/v7.0.0/index.html)

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

Sample query to fetch all events where the ``patient`` field equals ``"marcus aurelius"``
```http request```
/events?select=event&event-%3E%3Epatient=eq.marcus%20aurelius

Sample query to fetch events where for given patient AND tag:
```http request
/events?select=event&event.tags=cs.{mme-calc}&event-%3E%3Epatient=eq.marcus%20aurelius
```

See [PostgREST API](http://postgrest.org/en/v7.0.0/api.html) documentation
for additional options
