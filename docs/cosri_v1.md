
# Smart On Fire /launch event:
```json
{
    "version": "1",
    "name": "sof_wrapper",
    "tags": ["launch"],
    "asctime": "2021-09-14 17:52:31,516+00:00",
    "clinical-site": "Demo",
    "deployment": "demo",
    "system-name": "http://backend.cosri-demo.cirg.washington.edu/",
    "message": "launch",
    "subject": "Patient/1",
    "levelname": "INFO"
}
```

# PDMP event: patient lookup success
```json
{
    "version": "1",
    "name": "patientsearch",
    "tags": ["search"],
    "user": {
        "DEA": "testDEAvalue",
	"username": "test"
    },
    "asctime": "2021-09-14 18:01:50,224+00:00",
    "clinical-site": "Demo",
    "deployment": "demo",
    "system-name": "http://pdmp.cosri-demo.cirg.washington.edu/",
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
    "version": "1",
    "name": "sof_wrapper",
    "user": {
        "DEA": "testDEAvalue",
	"username": "test"
    },
    "asctime": "2021-09-14 17:58:53,930+00:00",
    "clinical-site": "Demo",
    "deployment": "demo",
    "system-name": "http://backend.cosri-demo.cirg.washington.edu/",
    "message": "PDMP returned 3 MedicationRequest/Orders",
    "subject": "Patient/1",
    "levelname": "INFO"
}
```

# FEMR (patientsearch) initiated logout
```json
{
    "version": "1",
    "name": "patientsearch",
    "tags": ["logout"],
    "user": {
        "DEA": "testDEAvalue",
	"username": "test"
    },
    "asctime": "2021-09-17 00:04:08,187+00:00",
    "clinical-site": "Demo",
    "deployment": "demo",
    "system-name": "http://dashboard.cosri-demo.cirg.washington.edu/",
    "message": "logout on request",
    "levelname": "INFO"
}
```
