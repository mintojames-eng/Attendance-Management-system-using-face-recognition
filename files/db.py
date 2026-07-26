"""
db.py — Shared SQLite storage layer for the attendance system.

Replaces:
  - StudentDetails/studentdetails.csv
  - Attendance/<Subject>/<Subject>_<date>_<time>.csv

Usage:
    from db import init_db, add_student, mark_attendance, get_attendance_report

    init_db()  # call once at app startup (attendance.py already does this)
"""

import sqlite3
import os
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "attendance.db")


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """Create tables if they don't exist. Safe to call every startup."""
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                enrollment TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                enrollment TEXT NOT NULL REFERENCES students(enrollment),
                subject TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                UNIQUE(enrollment, subject, date)
            )
            """
        )


# ---------- Students (write path used by takeImage.py) ----------

def add_student(enrollment, name):
    """Insert a student. Raises sqlite3.IntegrityError if enrollment already exists."""
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO students (enrollment, name) VALUES (?, ?)",
            (enrollment, name),
        )


def student_exists(enrollment):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT 1 FROM students WHERE enrollment = ?", (enrollment,)
        ).fetchone()
        return row is not None


def get_student_name(enrollment):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT name FROM students WHERE enrollment = ?", (enrollment,)
        ).fetchone()
        return row[0] if row else None


# ---------- Attendance (write path used by automaticAttedance.py) ----------

def mark_attendance(enrollment, subject, date, time_str):
    """
    Insert one attendance record. Duplicate (enrollment, subject, date)
    is silently ignored — this replaces the old drop_duplicates() logic.
    """
    with get_conn() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO attendance (enrollment, subject, date, time)
            VALUES (?, ?, ?, ?)
            """,
            (enrollment, subject, date, time_str),
        )


def get_session_attendance(subject, date):
    """Rows for a single day's session — used to show the popup after filling attendance."""
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT a.enrollment, s.name, a.time
            FROM attendance a
            JOIN students s ON s.enrollment = a.enrollment
            WHERE a.subject = ? AND a.date = ?
            ORDER BY a.time
            """,
            (subject, date),
        ).fetchall()
        return rows


# ---------- Reporting (read path used by show_attendance.py) ----------

def get_attendance_report(subject):
    """
    Returns rows of (enrollment, name, sessions_attended, total_sessions, pct)
    for a subject — replaces the CSV merge/fillna/mean logic entirely.
    """
    with get_conn() as conn:
        total_sessions_row = conn.execute(
            "SELECT COUNT(DISTINCT date) FROM attendance WHERE subject = ?",
            (subject,),
        ).fetchone()
        total_sessions = total_sessions_row[0] or 0

        rows = conn.execute(
            """
            SELECT s.enrollment, s.name, COUNT(DISTINCT a.date) AS attended
            FROM students s
            JOIN attendance a ON a.enrollment = s.enrollment
            WHERE a.subject = ?
            GROUP BY s.enrollment, s.name
            ORDER BY s.enrollment
            """,
            (subject,),
        ).fetchall()

        report = []
        for enrollment, name, attended in rows:
            pct = round(100 * attended / total_sessions) if total_sessions else 0
            report.append((enrollment, name, attended, total_sessions, f"{pct}%"))
        return report
