"""
Database connection and initialization for the Student Result Management System.

Uses plain sqlite3 (no ORM) so the project stays easy to read for beginners.
"""
import sqlite3
from werkzeug.security import generate_password_hash

from config import Config


def get_db_connection():
    """Return a new SQLite connection with row access by column name."""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all tables (if they do not already exist) and seed demo data."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            register_number TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL,
            department TEXT NOT NULL,
            year INTEGER NOT NULL,
            semester INTEGER NOT NULL,
            password TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_code TEXT NOT NULL UNIQUE,
            subject_name TEXT NOT NULL,
            department TEXT NOT NULL,
            semester INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS marks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject_id INTEGER NOT NULL,
            marks INTEGER NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
            FOREIGN KEY (subject_id) REFERENCES subjects (id) ON DELETE CASCADE,
            UNIQUE (student_id, subject_id)
        );
        """
    )
    conn.commit()

    _seed_admin(conn)
    _seed_subjects(conn)
    _seed_students(conn)
    _seed_marks(conn)

    conn.close()


def _seed_admin(conn):
    """Create a default demo admin account if none exists."""
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS count FROM admins")
    if cur.fetchone()["count"] == 0:
        cur.execute(
            "INSERT INTO admins (username, password) VALUES (?, ?)",
            ("admin", generate_password_hash("admin123")),
        )
        conn.commit()


def _seed_subjects(conn):
    """Insert a handful of demo subjects if the table is empty."""
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS count FROM subjects")
    if cur.fetchone()["count"] > 0:
        return

    subjects = [
        ("CS101", "Programming in C", "Computer Science", 5),
        ("CS102", "Python Programming", "Computer Science", 5),
        ("CS103", "Database Management Systems", "Computer Science", 5),
        ("CS104", "Computer Networks", "Computer Science", 5),
        ("CS105", "Software Engineering", "Computer Science", 5),
    ]
    cur.executemany(
        "INSERT INTO subjects (subject_code, subject_name, department, semester) "
        "VALUES (?, ?, ?, ?)",
        subjects,
    )
    conn.commit()


def _seed_students(conn):
    """Insert demo students if the table is empty."""
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS count FROM students")
    if cur.fetchone()["count"] > 0:
        return

    # Password for every demo student is "pass123"
    hashed = generate_password_hash("pass123")
    students = [
        ("Arun Kumar", "23CS101", "arun@example.com", "Computer Science", 3, 5, hashed),
        ("Priya Sharma", "23CS102", "priya@example.com", "Computer Science", 3, 5, hashed),
        ("Rahul Verma", "23CS103", "rahul@example.com", "Computer Science", 3, 5, hashed),
        ("Divya Nair", "23CS104", "divya@example.com", "Computer Science", 3, 5, hashed),
        ("Karthik Raj", "23CS105", "karthik@example.com", "Computer Science", 3, 5, hashed),
    ]
    cur.executemany(
        """INSERT INTO students
           (name, register_number, email, department, year, semester, password)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        students,
    )
    conn.commit()


def _seed_marks(conn):
    """
    Insert demo marks so the application can be demonstrated immediately.

    Rahul is deliberately given one subject below the 35-mark passing
    threshold so both the PASS (chocolate shower) and FAIL paths can be
    demonstrated straight after setup.
    """
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS count FROM marks")
    if cur.fetchone()["count"] > 0:
        return

    students = cur.execute("SELECT id, register_number FROM students").fetchall()
    subjects = cur.execute("SELECT id, subject_code FROM subjects ORDER BY id").fetchall()
    student_by_reg = {s["register_number"]: s["id"] for s in students}
    subject_ids = [s["id"] for s in subjects]

    demo_marks = {
        "23CS101": [85, 78, 92, 88, 80],   # Arun   -> PASS
        "23CS102": [90, 88, 76, 95, 84],   # Priya  -> PASS
        "23CS103": [85, 30, 90, 75, 88],   # Rahul  -> FAIL (DBMS below 35)
        "23CS104": [70, 65, 72, 68, 74],   # Divya  -> PASS
        "23CS105": [55, 40, 60, 58, 50],   # Karthik -> PASS (borderline)
    }

    rows = []
    for reg_number, mark_list in demo_marks.items():
        student_id = student_by_reg[reg_number]
        for subject_id, mark in zip(subject_ids, mark_list):
            rows.append((student_id, subject_id, mark))

    cur.executemany(
        "INSERT INTO marks (student_id, subject_id, marks) VALUES (?, ?, ?)",
        rows,
    )
    conn.commit()
