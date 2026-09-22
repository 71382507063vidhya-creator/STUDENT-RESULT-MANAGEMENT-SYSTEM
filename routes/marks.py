"""Marks management routes (admin only)."""
import sqlite3

from flask import Blueprint, request, jsonify

from config import Config
from database.database import get_db_connection
from routes.decorators import admin_required

marks_bp = Blueprint("marks", __name__, url_prefix="/api/marks")


def _serialize(row):
    return {
        "id": row["id"],
        "student_id": row["student_id"],
        "student_name": row["student_name"],
        "register_number": row["register_number"],
        "subject_id": row["subject_id"],
        "subject_code": row["subject_code"],
        "subject_name": row["subject_name"],
        "marks": row["marks"],
    }


def _validate_marks(data):
    if not data.get("student_id"):
        return "Student is required"
    if not data.get("subject_id"):
        return "Subject is required"
    try:
        marks = int(data.get("marks"))
    except (TypeError, ValueError):
        return "Marks must be a valid number"
    if marks < Config.MIN_MARK or marks > Config.MAX_MARK:
        return f"Marks must be between {Config.MIN_MARK} and {Config.MAX_MARK}"
    return None


MARKS_QUERY = """
    SELECT marks.id AS id, marks.student_id AS student_id, marks.subject_id AS subject_id,
           marks.marks AS marks, students.name AS student_name,
           students.register_number AS register_number,
           subjects.subject_code AS subject_code, subjects.subject_name AS subject_name
    FROM marks
    JOIN students ON marks.student_id = students.id
    JOIN subjects ON marks.subject_id = subjects.id
"""


@marks_bp.route("", methods=["GET"])
@admin_required
def get_marks():
    student_id = request.args.get("student_id")
    subject_id = request.args.get("subject_id")

    query = MARKS_QUERY + " WHERE 1=1"
    params = []
    if student_id:
        query += " AND marks.student_id = ?"
        params.append(student_id)
    if subject_id:
        query += " AND marks.subject_id = ?"
        params.append(subject_id)
    query += " ORDER BY students.name, subjects.subject_code"

    conn = get_db_connection()
    rows = conn.execute(query, params).fetchall()
    conn.close()

    return jsonify([_serialize(r) for r in rows]), 200


@marks_bp.route("", methods=["POST"])
@admin_required
def create_marks():
    data = request.get_json(silent=True) or {}
    error = _validate_marks(data)
    if error:
        return jsonify({"error": error}), 400

    conn = get_db_connection()

    student = conn.execute("SELECT id FROM students WHERE id = ?", (data["student_id"],)).fetchone()
    if student is None:
        conn.close()
        return jsonify({"error": "Student not found"}), 404

    subject = conn.execute("SELECT id FROM subjects WHERE id = ?", (data["subject_id"],)).fetchone()
    if subject is None:
        conn.close()
        return jsonify({"error": "Subject not found"}), 404

    try:
        conn.execute(
            "INSERT INTO marks (student_id, subject_id, marks) VALUES (?, ?, ?)",
            (data["student_id"], data["subject_id"], int(data["marks"])),
        )
        conn.commit()
        new_id = conn.execute(
            "SELECT id FROM marks WHERE student_id = ? AND subject_id = ?",
            (data["student_id"], data["subject_id"]),
        ).fetchone()["id"]
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Marks for this student and subject already exist"}), 400
    conn.close()

    return jsonify({"message": "Marks added successfully", "id": new_id}), 201


@marks_bp.route("/<int:mark_id>", methods=["PUT"])
@admin_required
def update_marks(mark_id):
    data = request.get_json(silent=True) or {}
    try:
        marks_value = int(data.get("marks"))
    except (TypeError, ValueError):
        return jsonify({"error": "Marks must be a valid number"}), 400
    if marks_value < Config.MIN_MARK or marks_value > Config.MAX_MARK:
        return jsonify({"error": f"Marks must be between {Config.MIN_MARK} and {Config.MAX_MARK}"}), 400

    conn = get_db_connection()
    existing = conn.execute("SELECT id FROM marks WHERE id = ?", (mark_id,)).fetchone()
    if existing is None:
        conn.close()
        return jsonify({"error": "Marks record not found"}), 404

    conn.execute("UPDATE marks SET marks = ? WHERE id = ?", (marks_value, mark_id))
    conn.commit()
    conn.close()

    return jsonify({"message": "Marks updated successfully"}), 200


@marks_bp.route("/<int:mark_id>", methods=["DELETE"])
@admin_required
def delete_marks(mark_id):
    conn = get_db_connection()
    existing = conn.execute("SELECT id FROM marks WHERE id = ?", (mark_id,)).fetchone()
    if existing is None:
        conn.close()
        return jsonify({"error": "Marks record not found"}), 404

    conn.execute("DELETE FROM marks WHERE id = ?", (mark_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Marks deleted successfully"}), 200
