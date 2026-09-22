"""Student management routes (admin only for write operations)."""
import re
import sqlite3

from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash

from database.database import get_db_connection
from routes.decorators import admin_required

students_bp = Blueprint("students", __name__, url_prefix="/api/students")

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _serialize(row):
    """Convert a student DB row to a dict, never exposing the password."""
    return {
        "id": row["id"],
        "name": row["name"],
        "register_number": row["register_number"],
        "email": row["email"],
        "department": row["department"],
        "year": row["year"],
        "semester": row["semester"],
    }


def _validate_student(data, require_password=True):
    """Return an error message string, or None if the data is valid."""
    if not (data.get("name") or "").strip():
        return "Student name is required"
    if not (data.get("register_number") or "").strip():
        return "Register number is required"
    email = (data.get("email") or "").strip()
    if not email or not EMAIL_REGEX.match(email):
        return "A valid email address is required"
    try:
        year = int(data.get("year"))
        if year < 1 or year > 6:
            return "Year must be between 1 and 6"
    except (TypeError, ValueError):
        return "A valid year is required"
    try:
        semester = int(data.get("semester"))
        if semester < 1 or semester > 12:
            return "Semester must be between 1 and 12"
    except (TypeError, ValueError):
        return "A valid semester is required"
    if not (data.get("department") or "").strip():
        return "Department is required"
    if require_password and not (data.get("password") or "").strip():
        return "Password is required"
    return None


@students_bp.route("", methods=["GET"])
@admin_required
def get_students():
    department = request.args.get("department")
    year = request.args.get("year")
    semester = request.args.get("semester")
    search = request.args.get("search")

    query = "SELECT * FROM students WHERE 1=1"
    params = []

    if department:
        query += " AND department = ?"
        params.append(department)
    if year:
        query += " AND year = ?"
        params.append(year)
    if semester:
        query += " AND semester = ?"
        params.append(semester)
    if search:
        query += " AND (name LIKE ? OR register_number LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    query += " ORDER BY name"

    conn = get_db_connection()
    rows = conn.execute(query, params).fetchall()
    conn.close()

    return jsonify([_serialize(r) for r in rows]), 200


@students_bp.route("/<int:student_id>", methods=["GET"])
@admin_required
def get_student(student_id):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    conn.close()

    if row is None:
        return jsonify({"error": "Student not found"}), 404
    return jsonify(_serialize(row)), 200


@students_bp.route("", methods=["POST"])
@admin_required
def create_student():
    data = request.get_json(silent=True) or {}
    error = _validate_student(data, require_password=True)
    if error:
        return jsonify({"error": error}), 400

    conn = get_db_connection()
    try:
        conn.execute(
            """INSERT INTO students
               (name, register_number, email, department, year, semester, password)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                data["name"].strip(),
                data["register_number"].strip(),
                data["email"].strip(),
                data["department"].strip(),
                int(data["year"]),
                int(data["semester"]),
                generate_password_hash(data["password"]),
            ),
        )
        conn.commit()
        new_id = conn.execute(
            "SELECT id FROM students WHERE register_number = ?",
            (data["register_number"].strip(),),
        ).fetchone()["id"]
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Register number already exists"}), 400
    conn.close()

    return jsonify({"message": "Student created successfully", "id": new_id}), 201


@students_bp.route("/<int:student_id>", methods=["PUT"])
@admin_required
def update_student(student_id):
    data = request.get_json(silent=True) or {}
    error = _validate_student(data, require_password=False)
    if error:
        return jsonify({"error": error}), 400

    conn = get_db_connection()
    existing = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    if existing is None:
        conn.close()
        return jsonify({"error": "Student not found"}), 404

    password_value = existing["password"]
    if (data.get("password") or "").strip():
        password_value = generate_password_hash(data["password"].strip())

    try:
        conn.execute(
            """UPDATE students SET
               name = ?, register_number = ?, email = ?, department = ?,
               year = ?, semester = ?, password = ?
               WHERE id = ?""",
            (
                data["name"].strip(),
                data["register_number"].strip(),
                data["email"].strip(),
                data["department"].strip(),
                int(data["year"]),
                int(data["semester"]),
                password_value,
                student_id,
            ),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Register number already exists"}), 400
    conn.close()

    return jsonify({"message": "Student updated successfully"}), 200


@students_bp.route("/<int:student_id>", methods=["DELETE"])
@admin_required
def delete_student(student_id):
    conn = get_db_connection()
    existing = conn.execute("SELECT id FROM students WHERE id = ?", (student_id,)).fetchone()
    if existing is None:
        conn.close()
        return jsonify({"error": "Student not found"}), 404

    conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Student deleted successfully"}), 200
