# Test Harness Architecture

This document describes the structure and usage of the test harness used for validating the `api.events_view` materialized view. It includes directory layout, helper functions, testing patterns, and data filtering techniques via SQL and PostgREST.

---

## Directory Structure

```
tests/
├── data/                        # JSON fixtures used for test inputs
│   ├── legacy_sample.json
│   ├── ltt_sample.json
│   ├── isacc_sample.json
│   ├── cosri_v1_sample.json
│   ├── cosri_v2_sample.json
│   ├── dhair2_inform_sample.json
│   └── ...                      # Additional schema-specific test data
├── expected/                    # (Optional) CSVs or structured data for test expectations
│   ├── legacy_expected.csv
│   ├── ltt_expected.csv
│   └── ...
└── test_views.py                # Main pytest suite for testing the events view
```

---

## Overview of `test_views.py`

This module contains fixtures and functions for end-to-end validation of the `api.events_view`. It ensures that normalized results match expectations defined per schema version.

### Core Functions

- **`insert_mock_data(cur, data_list)`**  
  Truncates `api.events` and inserts the provided list of JSON event records.

- **`query_events_view(cur)`**  
  Executes the following SQL query:

  ```sql
  SELECT schema_version, occurred_at, user_id, event_type
    FROM api.events_view
   ORDER BY occurred_at;
  ```

  Returns the raw output from the view for further normalization and assertion.

- **`normalize_results(rows)`**  
  Converts Python datetime values into UTC ISO-like strings:  
  `YYYY-MM-DD HH:MM:SS+00` for versioned schemas, and omits `+00` for legacy schemas.

- **`run_test(data_list, expected_rows)`**  
  A high-level helper that combines the above three steps and asserts that results match expected output.

### Fixtures

- Test fixtures load input data from `tests/data/`, using:

  ```python
  json.load(open("tests/data/<schema>_sample.json"))
  ```

- Expected results are either defined inline in test functions or loaded from CSV using a `load_expected()` helper (for schemas like `legacy`, `ltt`).

---

## Writing a New Test Case

To test a new schema:

1. **Add a JSON fixture** under `tests/data/`, using only required keys:
   - version
   - Timestamps: `event_time`, `occurred`, or `asctime`
   - Identity: `subject`, `user_id`, or nested user objects
   - Action descriptors: `action`, `tags`, `message`, etc.
   - Nested metadata: `source`, `context`, etc. (as required by your view)

2. **Create a test function** in `test_views.py`:

   ```python
   def test_view_with_new_schema(db_cursor):
       data = json.load(open("tests/data/new_schema_sample.json"))
       expected = [
           ("vX", "YYYY-MM-DD HH:MM:SS+00", "userID", "eventType")
       ]
       insert_mock_data(db_cursor, data)
       rows = normalize_results(query_events_view(db_cursor))
       assert rows == expected
   ```

3. **Commit your changes and push.** Continuous Integration (CI) will automatically execute the test suite.

---

## Filtering Events in `api.events_view`

### Using SQL

- **Legacy schema only:**

  ```sql
  SELECT * FROM api.events_view
   WHERE schema_version = 'legacy';
  ```

- **LTT schema only:**

  ```sql
  SELECT * FROM api.events_view
   WHERE schema_version = 'ltt'
   ORDER BY occurred_at;
  ```

- **All versioned schemas (non-legacy):**

  ```sql
  SELECT * FROM api.events_view
   WHERE schema_version NOT IN ('legacy', 'ltt')
   ORDER BY occurred_at;
  ```

### Using PostgREST HTTP API

- **Legacy events:**

  ```bash
  curl "http://localhost:3000/events_view?schema_version=eq.legacy"
  ```

- **LTT events:**

  ```bash
  curl "http://localhost:3000/events_view?schema_version=eq.ltt"
  ```

- **All versioned events:**

  ```bash
  curl "http://localhost:3000/events_view?schema_version=not.in.(legacy,ltt)"
  ```

---

## Filtering Raw Event JSON (Optional)

These filters help debug the raw event JSONs in the `api.events` table before transformation by the view.

### Using SQL

- **By `source.type`:**

  ```sql
  SELECT event->'source'->>'type' AS src_type, COUNT(*)
    FROM api.events
   GROUP BY src_type;
  ```

- **By `version` key:**

  ```sql
  SELECT event
    FROM api.events
   WHERE event->>'version' = '3.0';
  ```

### Using PostgREST

- **Filter by version (e.g., 3.0):**

  ```bash
  curl "http://localhost:3000/events?select=event&event->>version=eq.3.0"
  ```

---

## Notes

- This harness is **schema-agnostic** and supports heterogeneous input formats by focusing only on fields actually queried in `api.events_view`.
- **Timestamps and schema versions** are normalized at query-time to standardize assertion logic across schemas.
- To test **additional fields** or changes in view logic, extend `query_events_view` and `normalize_results` accordingly.
