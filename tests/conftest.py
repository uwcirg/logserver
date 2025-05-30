import os
import psycopg2
import pytest

@pytest.fixture(scope="module")
def db_conn():
    """
    Provides a psycopg2 connection for tests needing direct SQL access.
    """
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    yield conn
    conn.close()
