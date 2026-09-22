"""
Authentication routes: admin login, student login, logout.

Uses Flask session-based authentication with hashed passwords
(never stores or returns plain-text passwords).
"""
from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash

from database.database import get_db_connection

auth_bp = Blueprint("auth", __name__, url_prefix="/api")


@auth_bp.route("/admin/login", methods=["POST"])
def admin_login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    conn = get_db_connection()
    admin = conn.execute(
        "SELECT * FROM admins WHERE username = ?", (username,)
    ).fetchone()
    conn.close()

    if admin is None or not check_password_hash(admin["password"], password):
        return jsonify({"error": "Invalid username or password"}), 401

    session.clear()
    session["role"] = "admin"
    session["admin_id"] = admin["id"]
    session["username"] = admin["username"]

    return jsonify({"message": "Login successful", "role": "admin", "username": admin["username"]}), 200


@auth_bp.route("/student/login", methods=["POST"])
def student_login():
    data = request.get_json(silent=True) or {}
    register_number = (data.get("register_number") or "").strip()
    password = data.get("password") or ""

    if not register_number or not password:
        return jsonify({"error": "Register number and password are required"}), 400

    conn = get_db_connection()
    student = conn.execute(
        "SELECT * FROM students WHERE register_number = ?", (register_number,)
    ).fetchone()
    conn.close()

    if student is None or not check_password_hash(student["password"], password):
        return jsonify({"error": "Invalid register number or password"}), 401

    session.clear()
    session["role"] = "student"
    session["student_id"] = student["id"]
    session["register_number"] = student["register_number"]
    session["name"] = student["name"]

    return jsonify({
        "message": "Login successful",
        "role": "student",
        "student_id": student["id"],
        "name": student["name"],
    }), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200


@auth_bp.route("/session", methods=["GET"])
def session_info():
    """Let the frontend check who (if anyone) is currently logged in."""
    if session.get("role") == "admin":
        return jsonify({"role": "admin", "username": session.get("username")}), 200
    if session.get("role") == "student":
        return jsonify({
            "role": "student",
            "student_id": session.get("student_id"),
            "name": session.get("name"),
            "register_number": session.get("register_number"),
        }), 200
    return jsonify({"role": None}), 200
