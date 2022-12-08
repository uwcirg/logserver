# NB Version 0, didn't include a "version" attribute.

# Smart On Fire /launch event:
```json
{
    "name": "sof_wrapper",
    "tags": ["launch"],
    "asctime": "2021-09-14 17:52:31,516",
    "message": "launch",
    "subject": "Patient/1",
    "levelname": "INFO"
}
```

# PDMP event: patient lookup success
```json
{
    "name": "patientsearch",
    "tags": ["search"],
    "user": {
        "DEA": "testDEAvalue",
	"username": "test"
    },
    "asctime": "2021-09-14 18:01:50,224",
    "message": "PDMP found match",
    "patient": {
        "subject.id": "2",
	"subject:Patient.birthdate": "eq1974-09-01",
	"subject:Patient.name.given": "Harry",
	"subject:Patient.name.family": "Osborn"
    },
    "levelname": "INFO"
}
```

# PDMP event: medication requests found
```json
{
    "name": "sof_wrapper",
    "user": {"DEA": "testDEAvalue", "username": "test"},
    "asctime": "2021-09-14 17:58:53,930",
    "message": "PDMP returned 3 MedicationRequest/Orders",
    "subject": "Patient/1",
    "levelname": "INFO"
}
```

# FEMR (patientsearch) initiated logout
```json
{
    "name": "patientsearch",
    "tags": ["logout"],
    "user": {
        "DEA": "testDEAvalue",
	"username": "test"
    },
    "asctime": "2021-09-17 00:04:08,187",
    "message": "logout on request",
    "levelname": "INFO"
}
```
