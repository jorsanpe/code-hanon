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
        " status TEXT,"
        " value INTEGER DEFAULT 0,"
        " timestamp INTEGER"
        ")"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS expressions("
        " expression TEXT,"
        " status TEXT,"
        " value INTEGER DEFAULT 0,"
        " timestamp INTEGER"
        ")"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS latencies("
        " ngram TEXT,"
        " value INTEGER DEFAULT 0,"
        " timestamp INTEGER"
        ")"
    )


def update_statistics(statistics):
    connection = sqlite3.connect(DATABASE_FILENAME)
    cursor = connection.cursor()
    for ngram in statistics.failed_3grams.most_common():
        _insert(cursor, ngram, "ngram", FAILED)
    for expression in statistics.failed_expressions.most_common():
        _insert(cursor, expression, "expression", FAILED)
    for ngram in statistics.valid_3grams.most_common():
        _insert(cursor, ngram, "ngram", VALID)
    for expression in statistics.valid_expressions.most_common():
        _insert(cursor, expression, "expression", VALID)
    for latency in statistics.latency_3grams:
        _insert_latency(cursor, latency)
    connection.commit()
    connection.close()


def _insert(cursor, element, root, status):
    timestamp = int(time.time())
    expression_id = "".join(element[0])
    if expression_id.startswith("$$"):
        return
    cursor.execute(
        f"INSERT INTO {root}s ({root}, status, value, timestamp) VALUES (?, ?, ?, ?)",
        [expression_id, status, element[1], timestamp]
    )


def _insert_latency(cursor, latency):
    ngram_id = "".join(latency[0])
    timestamp = int(time.time())
    if ngram_id.startswith("$$"):
        return
    cursor.execute(
        f"INSERT INTO latencies (ngram, value, timestamp) VALUES (?, ?, ?)",
        [ngram_id, latency[1], timestamp]
    )


def all_statistics():
    connection = sqlite3.connect(DATABASE_FILENAME)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    rows = cursor.execute(
        f'SELECT ngram, value, status, timestamp FROM ngrams ORDER BY timestamp ASC'
    ).fetchall()
    ngrams = [{
        'ngram': row['ngram'],
        'value': row['value'],
        'status': row['status'],
        'timestamp': row['timestamp']
    } for row in rows]

    rows = cursor.execute(
        f'SELECT expression, value, status, timestamp FROM expressions ORDER BY timestamp ASC'
    ).fetchall()
    expressions = [{
        'expression': row['expression'],
        'value': row['value'],
        'status': row['status'],
        'timestamp': row['timestamp']
    } for row in rows]

    rows = cursor.execute(
        f'SELECT ngram, value, timestamp FROM latencies ORDER BY timestamp ASC'
    ).fetchall()
    latencies = [{
        'ngram': row['ngram'],
        'value': row['value'],
        'timestamp': row['timestamp']
    } for row in rows]

    return [ngrams, expressions, latencies]
