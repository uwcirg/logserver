import os
import json
import csv
import datetime
import psycopg2
import pytest
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL',
    'postgres://app_user:secret@localhost:5432/app_db'
)

# Path helper
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def insert_mock_data(cursor, data):
    cursor.execute("DELETE FROM api.events;")
    for record in data:
        cursor.execute(
            "INSERT INTO api.events (event) VALUES (%s);",
            (json.dumps(record),)
        )

def query_events_view(cursor):
    cursor.execute("""
        SELECT schema_version, occurred_at, user_id, event_type
          FROM api.events_view
      ORDER BY occurred_at;
    """)
    return cursor.fetchall()

def load_expected(path):
    """Return list of tuples (schema_version, occurred_at_str, user_id, event_type)."""
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            rows.append((
                row['schema_version'],
                row['occurred_at'],
                row['user_id'],
                row['event_type'],
            ))
    return rows

def format_timestamp(dt):
    """Render a datetime as 'YYYY-MM-DD HH:MM:SS' (no tz offset)."""
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def normalize_results(rows):
    """
    Given an iterable of (schema, datetime, user_id, event_type),
    return a list of tuples where the datetime is formatted as
    'YYYY-MM-DD HH:MM:SS' plus '+00' only for 'ltt' rows.
    """
    out = []
    for schema, dt, user, ev in rows:
        ts = dt.strftime('%Y-%m-%d %H:%M:%S')
        if schema !== 'legacy':
            ts += '+00'
        out.append((schema, ts, user, ev))
    return out

def run_test(mock_data, expected_rows):
    """Wipe, insert mock_data, run view, normalize & assert against expected_rows."""
    with psycopg2.connect(DATABASE_URL) as conn, conn.cursor() as cur:
        insert_mock_data(cur, mock_data)
        conn.commit()
        raw = query_events_view(cur)
    actual = normalize_results(raw)
    assert actual == expected_rows

@pytest.fixture
def isacc_data():
    path = os.path.join(DATA_DIR, "isacc_sample.json")
    with open(path, 'r') as f:
        return json.load(f)

@pytest.fixture
def isacc_expected():
    return [
        (
            "3.0",                             # version → schema_version
            "2025-04-23 14:22:10+00",          # occurred_at
            "Practitioner/ABC-123",            # user_id (from subject)
            "login"                            # event_type
        )
    ]

@pytest.fixture
def dhair2_data():
    path = os.path.join(DATA_DIR, "dhair2_inform_sample.json")
    return json.load(open(path))

@pytest.fixture
def dhair2_expected():
    return [
        (
            "3.0",                      # version field
            "2025-01-31 00:44:18+00",   # parsed from occurred
            "patients/607",             # first item from subject array
            "create"                    # action
        )
    ]

@pytest.fixture
def cosri_v2_data():
    path = os.path.join(DATA_DIR, "cosri_v2_sample.json")
    return json.load(open(path))

@pytest.fixture
def cosri_v2_expected():
    return [
        # first event: launch
        (
            "1",                            # version
            "2021-09-14 17:52:31+00",       # occurred_at (zoned)
            "Patient/1",                    # user_id
            "launch"                        # event_type (from tags[0] or message)
        ),
        # second event: logout
        (
            "1",
            "2021-09-17 00:04:08+00",
            "Patient/1",
            "logout"                        # tags[0] = "logout"
        )
    ]

@pytest.fixture(scope="module")
def legacy_data():
    return json.load(open('tests/data/legacy_sample.json'))

@pytest.fixture(scope="module")
def ltt_data():
    return json.load(open('tests/data/ltt_sample.json'))

@pytest.fixture(scope="module")
def legacy_expected():
    return load_expected('tests/expected_results/legacy_expected.csv')

@pytest.fixture(scope="module")
def ltt_expected():
    return load_expected('tests/expected_results/ltt_expected.csv')


def test_view_with_legacy_data(legacy_data, legacy_expected):
    run_test(legacy_data, legacy_expected)

def test_view_with_ltt_data(ltt_data, ltt_expected):
    run_test(ltt_data, ltt_expected)

def test_view_with_mixed_data(legacy_data, ltt_data,
                              legacy_expected, ltt_expected):
    # just concatenate the two known samples
    run_test(legacy_data + ltt_data,
             legacy_expected + ltt_expected)

def test_view_with_empty_data():
    run_test([], [])

def test_view_with_single_event(legacy_data, legacy_expected):
    # pick the first legacy record
    run_test([legacy_data[0]], [legacy_expected[0]])

def test_view_with_isacc_data(isacc_data, isacc_expected):
    run_test(isacc_data, isacc_expected)

def test_view_with_dhair2_data(dhair2_data, dhair2_expected):
    run_test(dhair2_data, dhair2_expected)

def test_view_with_cosri_v2_data(cosri_v2_data, cosri_v2_expected):
    run_test(cosri_v2_data, cosri_v2_expected)
