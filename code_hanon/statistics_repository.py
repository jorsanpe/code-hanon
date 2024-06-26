import sqlite3


DATABASE_FILENAME = ".statistics.db"


def migrate():
    connection = sqlite3.connect(DATABASE_FILENAME)
    cursor = connection.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS ngrams("
        " ngram TEXT,"
        " total INTEGER DEFAULT 0,"
        " mistakes INTEGER DEFAULT 0,"
        " PRIMARY KEY(ngram)"
        ")"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS expressions("
        " expression TEXT,"
        " total INTEGER DEFAULT 0,"
        " mistakes INTEGER DEFAULT 0,"
        " PRIMARY KEY(expression)"
        ")"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS latencies("
        " ngram TEXT,"
        " latency INTEGER DEFAULT 0"
        ")"
    )


def update_statistics(statistics):
    connection = sqlite3.connect(DATABASE_FILENAME)
    cursor = connection.cursor()
    for ngram in statistics.failed_3grams.most_common():
        _fail(cursor, ngram, "ngram")
    for expression in statistics.failed_expressions.most_common():
        _fail(cursor, expression, "expression")
    for ngram in statistics.valid_3grams.most_common():
        _valid(cursor, ngram, "ngram")
    for expression in statistics.valid_expressions.most_common():
        _valid(cursor, expression, "expression")
    for latency in statistics.latency_3grams.most_common():
        _latency(cursor, latency)
    connection.commit()
    connection.close()


def _fail(cursor, element, root):
    expression_id = "".join(element[0])
    if expression_id.startswith("$$"):
        return
    row = cursor.execute(f"SELECT * FROM {root}s WHERE {root} = ?", [expression_id]).fetchone()
    if row:
        cursor.execute(
            f"UPDATE {root}s SET total = ?, mistakes = ? WHERE {root} = ?",
            [int(row[1]) + element[1], int(row[2]) + element[1], expression_id]
        )
    else:
        cursor.execute(
            f"INSERT INTO {root}s ({root}, total, mistakes) VALUES (?, ?, ?)",
            [expression_id, element[1], element[1]]
        )


def _valid(cursor, element, root):
    expression_id = "".join(element[0])
    if expression_id.startswith("$$"):
        return
    row = cursor.execute(f"SELECT * FROM {root}s WHERE {root} = ?", [expression_id]).fetchone()
    if row:
        cursor.execute(
            f"UPDATE {root}s SET total = ? WHERE {root} = ?",
            [int(row[1]) + element[1], expression_id]
        )
    else:
        cursor.execute(
            f"INSERT INTO {root}s ({root}, total) VALUES (?, ?)",
            [expression_id, element[1]]
        )


def _latency(cursor, latency):
    ngram_id = "".join(latency[0])
    if ngram_id.startswith("$$"):
        return
    cursor.execute(
        f"INSERT INTO latencies (ngram, latency) VALUES (?, ?)",
        [ngram_id, latency[1]]
    )
