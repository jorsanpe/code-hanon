# Copyright (C) Jordi Sánchez 2024
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sqlite3
import time

DATABASE_FILENAME = "statistics.db"
FAILED = "KO"
VALID = "OK"
DATABASE_TABLES = [
    {
        'name': 'ngrams',
        'columns': {
            'ngram': 'TEXT',
            'pattern': 'TEXT',
            'status': 'TEXT',
            'value': 'INTEGER DEFAULT 0',
            'timestamp': 'INTEGER',
        }
    },
    {
        'name': 'latencies',
        'columns': {
            'ngram': 'TEXT',
            'pattern': 'TEXT',
            'value': 'INTEGER DEFAULT 0',
            'timestamp': 'INTEGER',
        }
    },
]


def prepare():
    with sqlite3.connect(DATABASE_FILENAME) as connection:
        cursor = connection.cursor()

        for table in DATABASE_TABLES:
            cursor.execute(
                f"CREATE TABLE IF NOT EXISTS {table['name']}("
                f"{','.join(f'{col} {typ}' for col, typ in table['columns'].items())}"
                f")"
            )
            for col, typ in table['columns'].items():
                _add_column_if_not_exists(cursor, 'ngrams', col, typ)


def _add_column_if_not_exists(cursor, table_name, column_name, column_type):
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    if not cursor.fetchone():
        return

    cursor.execute(f"PRAGMA table_info('{table_name}')")
    existing_columns = [column[1] for column in cursor.fetchall()]
    if column_name in existing_columns:
        return

    cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")


def update_statistics(statistics):
    connection = sqlite3.connect(DATABASE_FILENAME)
    cursor = connection.cursor()
    for ngram in statistics.failed_3grams.most_common():
        _insert(cursor, ngram, FAILED)
    for ngram in statistics.valid_3grams.most_common():
        _insert(cursor, ngram, VALID)
    for latency in statistics.latency_3grams:
        _insert_latency(cursor, latency)
    connection.commit()
    connection.close()


def _insert(cursor, element, status):
    ngram_id = "".join(element[0][0])
    if ngram_id.startswith("$$"):
        return
    pattern = element[0][1]
    value = element[1]
    timestamp = int(time.time())
    cursor.execute(
        f"INSERT INTO ngrams (ngram, pattern, status, value, timestamp) VALUES (?, ?, ?, ?, ?)",
        [ngram_id, pattern, status, value, timestamp]
    )


def _insert_latency(cursor, latency):
    ngram_id = "".join(latency[0][0])
    if ngram_id.startswith("$$"):
        return
    pattern = latency[0][1]
    value = latency[1]
    timestamp = int(time.time())
    if ngram_id.startswith("$$"):
        return
    cursor.execute(
        f"INSERT INTO latencies (ngram, pattern, value, timestamp) VALUES (?, ?, ?, ?)",
        [ngram_id, pattern, value, timestamp]
    )


def all_statistics():
    connection = sqlite3.connect(DATABASE_FILENAME)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    rows = cursor.execute(
        f'SELECT ngram, pattern, value, status, timestamp FROM ngrams ORDER BY timestamp ASC'
    ).fetchall()
    ngrams = [{
        'ngram': row['ngram'],
        'pattern': row['pattern'],
        'value': row['value'],
        'status': row['status'],
        'timestamp': row['timestamp']
    } for row in rows]

    rows = cursor.execute(
        f'SELECT ngram, pattern, value, timestamp FROM latencies ORDER BY timestamp ASC'
    ).fetchall()
    latencies = [{
        'ngram': row['ngram'],
        'pattern': row['pattern'],
        'value': row['value'],
        'timestamp': row['timestamp']
    } for row in rows]

    return [ngrams, latencies]
