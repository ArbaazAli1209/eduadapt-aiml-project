"""SQLite storage (free, serverless). Two tables: students and attempts."""
import sqlite3
from contextlib import contextmanager
from datetime import datetime

import pandas as pd

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS students(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE COLLATE NOCASE,
    grade INTEGER DEFAULT 8,
    lang TEXT DEFAULT 'English',
    is_demo INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS attempts(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL REFERENCES students(id),
    topic TEXT NOT NULL,
    difficulty TEXT,
    question_id TEXT,
    correct INTEGER NOT NULL,
    ts TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_attempts_student ON attempts(student_id, ts);
"""


@contextmanager
def connect():
    conn = sqlite3.connect(str(config.DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def get_or_create_student(name, grade=8, lang="English", is_demo=0):
    name = name.strip()
    with connect() as c:
        row = c.execute("SELECT id FROM students WHERE name = ?", (name,)).fetchone()
        if row:
            c.execute("UPDATE students SET lang = ? WHERE id = ?", (lang, row["id"]))
            return int(row["id"])
        cur = c.execute("INSERT INTO students(name, grade, lang, is_demo) VALUES (?,?,?,?)",
                        (name, grade, lang, is_demo))
        return int(cur.lastrowid)


def log_attempt(student_id, topic, difficulty, question_id, correct, ts=None):
    ts = (ts or datetime.now()).isoformat(timespec="seconds")
    with connect() as c:
        c.execute("INSERT INTO attempts(student_id, topic, difficulty, question_id, correct, ts) VALUES (?,?,?,?,?,?)",
                  (student_id, topic, difficulty, question_id, int(correct), ts))


def bulk_insert_attempts(rows):
    """rows: iterable of (student_id, topic, difficulty, question_id, correct, ts_datetime)."""
    data = [(sid, t, d, q, int(c), ts.isoformat(timespec="seconds")) for sid, t, d, q, c, ts in rows]
    with connect() as c:
        c.executemany("INSERT INTO attempts(student_id, topic, difficulty, question_id, correct, ts) VALUES (?,?,?,?,?,?)", data)


def attempts_df(student_id=None):
    query = "SELECT student_id, topic, difficulty, question_id, correct, ts FROM attempts"
    params = ()
    if student_id is not None:
        query += " WHERE student_id = ?"
        params = (student_id,)
    query += " ORDER BY ts, id"
    with connect() as c:
        df = pd.read_sql_query(query, c, params=params)
    df["ts"] = pd.to_datetime(df["ts"])
    return df


def students_df():
    with connect() as c:
        return pd.read_sql_query("SELECT id, name, grade, lang, is_demo FROM students ORDER BY id", c)


def seen_question_ids(student_id):
    with connect() as c:
        rows = c.execute("SELECT DISTINCT question_id FROM attempts WHERE student_id = ? AND question_id IS NOT NULL",
                         (student_id,)).fetchall()
    return {r["question_id"] for r in rows}


def clear_demo():
    with connect() as c:
        c.execute("DELETE FROM attempts WHERE student_id IN (SELECT id FROM students WHERE is_demo = 1)")
        c.execute("DELETE FROM students WHERE is_demo = 1")
