import os
import json
import csv
import psycopg2
import pytest

# 1) Autouse fixture for dotenv
@pytest.fixture(scope="session", autouse=True)
def load_env():
    from dotenv import load_dotenv
    load_dotenv()

DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgres://app_user:secret@localhost:5432/app_db'
)
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
EXPECTED_DIR = os.path.join(os.path.dirname(__file__), "expected_results")

# 2) Cursor fixture + reset hook
@pytest.fixture
def db_cursor():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    yield cur
    conn.rollback()
    conn.close()

@pytest.fixture(autouse=True)
def reset_table(db_cursor):
    db_cursor.execute("TRUNCATE api.events;")
    db_cursor.connection.commit()

def insert_events(cur, data):
    for e in data:
        cur.execute("INSERT INTO api.events (event) VALUES (%s)", (json.dumps(e),))
    cur.connection.commit()

def query_view(cur):
    cur.execute("""
        SELECT schema_version, occurred_at, user_id, event_type
          FROM api.events_view
      ORDER BY occurred_at;
    """)
    return cur.fetchall()

def normalize(rows):
    out = []
    for schema, dt, user, ev in rows:
        ts = dt.strftime('%Y-%m-%d %H:%M:%S')
        if schema != 'legacy':
            ts += '+00'
        out.append((schema, ts, user, ev))
    return out

# 3) CSV loader helper
def load_expected(name):
    path = os.path.join(EXPECTED_DIR, name + ".csv")
    with open(path, newline='') as f:
        return [ (r['schema_version'], r['occurred_at'], r['user_id'], r['event_type'])
                 for r in csv.DictReader(f) ]

# 4) Tests now inline their asserts

def test_view_with_legacy_data(db_cursor):
    data = json.load(open(os.path.join(DATA_DIR, "legacy_sample.json")))
    expected = load_expected("legacy_expected")
    insert_events(db_cursor, data)
    actual = normalize(query_view(db_cursor))
    assert actual == expected


def test_view_with_ltt_data(db_cursor):
    data = json.load(open(os.path.join(DATA_DIR, "ltt_sample.json")))
    expected = load_expected("ltt_expected")
    insert_events(db_cursor, data)
    actual = normalize(query_view(db_cursor))
    assert actual == expected


def test_view_with_mixed_data(db_cursor):
    legacy = json.load(open(os.path.join(DATA_DIR, "legacy_sample.json")))
    ltt    = json.load(open(os.path.join(DATA_DIR, "ltt_sample.json")))
    expected = load_expected("legacy_expected") + load_expected("ltt_expected")
    insert_events(db_cursor, legacy + ltt)
    actual = normalize(query_view(db_cursor))
    assert actual == expected


def test_view_with_empty_data(db_cursor):
    insert_events(db_cursor, [])
    actual = normalize(query_view(db_cursor))
    assert actual == []


def test_view_with_single_event(db_cursor):
    legacy = json.load(open(os.path.join(DATA_DIR, "legacy_sample.json")))
    expected = load_expected("legacy_expected")[0:1]
    insert_events(db_cursor, [legacy[0]])
    actual = normalize(query_view(db_cursor))
    assert actual == expected


def test_view_with_isacc_data(db_cursor):
    data = json.load(open(os.path.join(DATA_DIR, "isacc_sample.json")))
    expected = [("3.0", "2025-04-23 14:22:10+00", "Practitioner/ABC-123", "login")]
    insert_events(db_cursor, data)
    actual = normalize(query_view(db_cursor))
    assert actual == expected


def test_view_with_dhair2_data(db_cursor):
    data = json.load(open(os.path.join(DATA_DIR, "dhair2_inform_sample.json")))
    expected = [("3.0", "2025-01-31 00:44:18+00", "patients/607", "create")]
    insert_events(db_cursor, data)
    actual = normalize(query_view(db_cursor))
    assert actual == expected


def test_view_with_cosri_v2_data(db_cursor):
    data = json.load(open(os.path.join(DATA_DIR, "cosri_v2_sample.json")))
    expected = [
        ("1", "2021-09-14 17:52:31+00", "Patient/1", "launch"),
        ("1", "2021-09-17 00:04:08+00", "Patient/1", "logout"),
    ]
    insert_events(db_cursor, data)
    actual = normalize(query_view(db_cursor))
    assert actual == expected
