"""Reusable authentication/authorization decorators for API routes."""
from functools import wraps
from flask import session, jsonify


def admin_required(view_func):
    """Only allow access to logged-in admins."""
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if session.get("role") != "admin":
            return jsonify({"error": "Unauthorized: admin login required"}), 401
        return view_func(*args, **kwargs)
    return wrapper


def student_or_admin_required(view_func):
    """Allow access to any logged-in user (admin or student)."""
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if session.get("role") not in ("admin", "student"):
            return jsonify({"error": "Unauthorized: please log in"}), 401
        return view_func(*args, **kwargs)
    return wrapper
