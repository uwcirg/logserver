# Example Audit Entries from dhair2

## Creating an answers record:
```json
{
	"level": "info",
	"version": "3.0",
	"source": {
		"observer": "https://ubu.mcjustin.dev.cirg.uw.edu",
		"type": "dhair2/inform"
	},
	"occurred": "2025-01-31T00:44:18Z",
	"agent": {
		"type": "user",
		"who": "607",
		"user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0",
		"ip_address": "10.102.17.250"
	},
	"subject": [
		"patients/607"
	],
	"entity": {
		"detail": {
			"controller": "Answer",
			"action": "afterSave created"
		},
		"query": "question_id = 2320; state = ; body_text = 6; option_id = 8040; value = ; iteration = 0; survey_session_id = 78900258;"
	},
	"action": "create"
}
```

## View survey page:
```json
{
	"level": "info",
	"version": "3.0",
	"source": {
		"observer": "https://ubu.mcjustin.dev.cirg.uw.edu",
		"type": "dhair2/inform"
	},
	"occurred": "2025-01-31T00:47:17Z",
	"agent": {
		"type": "user",
		"who": "607",
		"user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0",
		"ip_address": "10.102.17.250"
	},
	"subject": [
		"patients/607"
	],
	"entity": {
		"detail": {
			"controller": "surveys",
			"action": "show"
		},
		"query": "1680"
	},
	"action": "read"
}
```

## SurveySession copy:
("restart" for inform; I'll note that this also creates a ton of log entries for copying the session's answer records):
```json
{
	"level": "info",
	"version": "3.0",
	"source": {
		"observer": "https://ubu.mcjustin.dev.cirg.uw.edu",
		"type": "dhair2/inform"
	},
	"occurred": "2025-01-31T01:49:39Z",
	"agent": {
		"type": "user",
		"who": "607",
		"user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0",
		"ip_address": "10.102.17.250"
	},
	"subject": [
		"patients/607"
	],
	"entity": {
		"detail": {
			"controller": "SurveySession",
			"action": "afterSave created"
		},
		"query": "partial_finalization = ; finished = ; auto_finish = ; user_id = 607; project_id = 3; started = 2025-01-30 00:52:20; patient_id = 607; type = ELECTIVE; appointment_id = ; reportable_datetime = 2025-01-31 01:34:54; external_id = ; page_id_last_interaction = 1705;"
	},
	"action": "create"
}
```
