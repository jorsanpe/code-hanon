import sqlite3
import time

DATABASE_FILENAME = "statistics.db"
FAILED = "KO"
VALID = "OK"


def migrate():
    connection = sqlite3.connect(DATABASE_FILENAME)
    cursor = connection.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS ngrams("
        " ngram TEXT,"
        " expression TEXT,"
        " status TEXT,"
        " value INTEGER DEFAULT 0,"
        " timestamp INTEGER"
        ")"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS latencies("
        " ngram TEXT,"
        " expression TEXT,"
        " value INTEGER DEFAULT 0,"
        " timestamp INTEGER"
        ")"
    )


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
    expression = element[0][1]
    value = element[1]
    timestamp = int(time.time())
    cursor.execute(
        f"INSERT INTO ngrams (ngram, expression, status, value, timestamp) VALUES (?, ?, ?, ?, ?)",
        [ngram_id, expression, status, value, timestamp]
    )


def _insert_latency(cursor, latency):
    ngram_id = "".join(latency[0][0])
    if ngram_id.startswith("$$"):
        return
    expression = latency[0][1]
    value = latency[1]
    timestamp = int(time.time())
    if ngram_id.startswith("$$"):
        return
    cursor.execute(
        f"INSERT INTO latencies (ngram, expression, value, timestamp) VALUES (?, ?, ?, ?)",
        [ngram_id, expression, value, timestamp]
    )


def all_statistics():
    connection = sqlite3.connect(DATABASE_FILENAME)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    rows = cursor.execute(
        f'SELECT ngram, expression, value, status, timestamp FROM ngrams ORDER BY timestamp ASC'
    ).fetchall()
    ngrams = [{
        'ngram': row['ngram'],
        'expression': row['expression'],
        'value': row['value'],
        'status': row['status'],
        'timestamp': row['timestamp']
    } for row in rows]

    rows = cursor.execute(
        f'SELECT ngram, expression, value, timestamp FROM latencies ORDER BY timestamp ASC'
    ).fetchall()
    latencies = [{
        'ngram': row['ngram'],
        'expression': row['expression'],
        'value': row['value'],
        'timestamp': row['timestamp']
    } for row in rows]

    return [ngrams, latencies]
