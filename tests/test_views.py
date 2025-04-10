import os
import json
import psycopg2
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'postgres://app_user:secret@localhost:5432/app_db')

def insert_mock_data(cursor, data):
    cursor.execute("DELETE FROM api.events;")
    for record in data:
        cursor.execute("INSERT INTO api.events (event) VALUES (%s);", (json.dumps(record),))

def query_events_view(cursor):
    cursor.execute("SELECT schema_version, occurred_at, user_id, event_type FROM api.events_view ORDER BY occurred_at;")
    return cursor.fetchall()

def test_view_with_legacy_data():
    with open('tests/data/legacy_sample.json') as f:
        mock_data = json.load(f)
    expected_df = pd.read_csv('tests/expected_results/legacy_expected.csv')

    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cursor:
            insert_mock_data(cursor, mock_data)
            conn.commit()

            results = query_events_view(cursor)
            results_df = pd.DataFrame(results, columns=expected_df.columns)

            pd.testing.assert_frame_equal(results_df.reset_index(drop=True), expected_df)

def test_view_with_ltt_data():
    with open('tests/data/ltt_sample.json') as f:
        mock_data = json.load(f)
    expected_df = pd.read_csv('tests/expected_results/ltt_expected.csv')

    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cursor:
            insert_mock_data(cursor, mock_data)
            conn.commit()

            results = query_events_view(cursor)
            results_df = pd.DataFrame(results, columns=expected_df.columns)

            pd.testing.assert_frame_equal(results_df.reset_index(drop=True), expected_df)
