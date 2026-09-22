"""
Result routes.

All PASS/FAIL, total, average, and grade calculations happen in
services/result_service.py. This file only handles HTTP concerns and
access control (a student may only view their own result).
"""
from flask import Blueprint, jsonify, session

from services.result_service import calculate_result, calculate_all_results, get_dashboard_stats
from routes.decorators import admin_required, student_or_admin_required

results_bp = Blueprint("results", __name__, url_prefix="/api")


@results_bp.route("/results", methods=["GET"])
@admin_required
def get_all_results():
    return jsonify(calculate_all_results()), 200


@results_bp.route("/results/<int:student_id>", methods=["GET"])
@student_or_admin_required
def get_student_result(student_id):
    # Students may only view their own result.
    if session.get("role") == "student" and session.get("student_id") != student_id:
        return jsonify({"error": "Unauthorized access to this result"}), 401

    result = calculate_result(student_id)
    if result is None:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(result), 200


@results_bp.route("/dashboard-stats", methods=["GET"])
@admin_required
def dashboard_stats():
    return jsonify(get_dashboard_stats()), 200
