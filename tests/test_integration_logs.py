import os
import pytest
from psycopg2 import connect

DATABASE_URL = os.getenv('DATABASE_URL', 'postgres://app_user:secret@localhost:5432/app_db')

@pytest.fixture(scope="session")
def db_conn():
    cn = connect(DATABASE_URL)
    yield cn
    cn.close()

def test_schema_count(db_conn):
    cur = db_conn.cursor()
    # no truncate, just query
    cur.execute("""
      SELECT schema_version, COUNT(*) 
        FROM api.events_view 
        GROUP BY schema_version;
    """)
    results = cur.fetchall()
    versions = {r[0] for r in results}
    assert '3.0'    in versions
    assert 'legacy' in versions
    versioned = versions - {'legacy'}
    assert versioned, f"Expected some non-legacy schema versions, got only {versions}"
