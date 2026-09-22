"""Subject management routes (admin only for write operations)."""
import sqlite3

from flask import Blueprint, request, jsonify

from database.database import get_db_connection
from routes.decorators import admin_required

subjects_bp = Blueprint("subjects", __name__, url_prefix="/api/subjects")


def _serialize(row):
    return {
        "id": row["id"],
        "subject_code": row["subject_code"],
        "subject_name": row["subject_name"],
        "department": row["department"],
        "semester": row["semester"],
    }


def _validate_subject(data):
    if not (data.get("subject_code") or "").strip():
        return "Subject code is required"
    if not (data.get("subject_name") or "").strip():
        return "Subject name is required"
    if not (data.get("department") or "").strip():
        return "Department is required"
    try:
        semester = int(data.get("semester"))
        if semester < 1 or semester > 12:
            return "Semester must be between 1 and 12"
    except (TypeError, ValueError):
        return "A valid semester is required"
    return None


@subjects_bp.route("", methods=["GET"])
@admin_required
def get_subjects():
    department = request.args.get("department")
    semester = request.args.get("semester")
    search = request.args.get("search")

    query = "SELECT * FROM subjects WHERE 1=1"
    params = []
    if department:
        query += " AND department = ?"
        params.append(department)
    if semester:
        query += " AND semester = ?"
        params.append(semester)
    if search:
        query += " AND (subject_name LIKE ? OR subject_code LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    query += " ORDER BY subject_code"

    conn = get_db_connection()
    rows = conn.execute(query, params).fetchall()
    conn.close()

    return jsonify([_serialize(r) for r in rows]), 200


@subjects_bp.route("/<int:subject_id>", methods=["GET"])
@admin_required
def get_subject(subject_id):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM subjects WHERE id = ?", (subject_id,)).fetchone()
    conn.close()
    if row is None:
        return jsonify({"error": "Subject not found"}), 404
    return jsonify(_serialize(row)), 200


@subjects_bp.route("", methods=["POST"])
@admin_required
def create_subject():
    data = request.get_json(silent=True) or {}
    error = _validate_subject(data)
    if error:
        return jsonify({"error": error}), 400

    conn = get_db_connection()
    try:
        conn.execute(
            """INSERT INTO subjects (subject_code, subject_name, department, semester)
               VALUES (?, ?, ?, ?)""",
            (
                data["subject_code"].strip(),
                data["subject_name"].strip(),
                data["department"].strip(),
                int(data["semester"]),
            ),
        )
        conn.commit()
        new_id = conn.execute(
            "SELECT id FROM subjects WHERE subject_code = ?",
            (data["subject_code"].strip(),),
        ).fetchone()["id"]
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Subject code already exists"}), 400
    conn.close()

    return jsonify({"message": "Subject created successfully", "id": new_id}), 201


@subjects_bp.route("/<int:subject_id>", methods=["PUT"])
@admin_required
def update_subject(subject_id):
    data = request.get_json(silent=True) or {}
    error = _validate_subject(data)
    if error:
        return jsonify({"error": error}), 400

    conn = get_db_connection()
    existing = conn.execute("SELECT id FROM subjects WHERE id = ?", (subject_id,)).fetchone()
    if existing is None:
        conn.close()
        return jsonify({"error": "Subject not found"}), 404

    try:
        conn.execute(
            """UPDATE subjects SET subject_code = ?, subject_name = ?,
               department = ?, semester = ? WHERE id = ?""",
            (
                data["subject_code"].strip(),
                data["subject_name"].strip(),
                data["department"].strip(),
                int(data["semester"]),
                subject_id,
            ),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Subject code already exists"}), 400
    conn.close()

    return jsonify({"message": "Subject updated successfully"}), 200


@subjects_bp.route("/<int:subject_id>", methods=["DELETE"])
@admin_required
def delete_subject(subject_id):
    conn = get_db_connection()
    existing = conn.execute("SELECT id FROM subjects WHERE id = ?", (subject_id,)).fetchone()
    if existing is None:
        conn.close()
        return jsonify({"error": "Subject not found"}), 404

    conn.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Subject deleted successfully"}), 200
