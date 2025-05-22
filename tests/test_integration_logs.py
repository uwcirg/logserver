import os
from dotenv import load_dotenv
import pytest
import psycopg2

load_dotenv()  # read .env at repo root 

# Use DATABASE_URL or fallback to our dev container’s app_db
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgres://app_user:secret@127.0.0.1:5432/app_db'
)

CONNECT_PARAMS = {'dsn': DATABASE_URL, 'connect_timeout': 5}

@pytest.fixture(scope="session")
def db_conn():
    # Connect with timeout over TCP and enable autocommit to avoid open transactions
    conn = psycopg2.connect(**CONNECT_PARAMS)
    conn.autocommit = True
    yield conn
    conn.close()
    conn.close()


def test_schema_count(db_conn):
    """
    Ensure that our unified view returns at least one schema_version.
    """
    cur = db_conn.cursor()
    cur.execute(
        """
        SELECT schema_version, COUNT(*)
          FROM api.events_view
         GROUP BY schema_version;
        """
    )
    results = cur.fetchall()
    versions = {r[0] for r in results}
    # There should be at least one schema version present.
    assert versions, f"Expected at least one schema_version, got none: {versions}"
