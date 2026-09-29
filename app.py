"""
Student Result Management System
Main Flask application entry point.
"""

from flask import Flask, render_template, session, redirect, url_for

from config import Config
from database.database import init_db
from routes.auth import auth_bp
from routes.students import students_bp
from routes.subjects import subjects_bp
from routes.marks import marks_bp
from routes.results import results_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register REST API blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(subjects_bp)
    app.register_blueprint(marks_bp)
    app.register_blueprint(results_bp)

    # ---------------- Page (HTML) routes ----------------

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/about")
    def about():
        return render_template("about.html")

    @app.route("/login")
    def login_page():
        return render_template("login.html")

    @app.route("/admin/dashboard")
    def admin_dashboard():
        if session.get("role") != "admin":
            return redirect(url_for("login_page"))
        return render_template(
            "admin_dashboard.html",
            username=session.get("username")
        )

    @app.route("/admin/students")
    def students_page():
        if session.get("role") != "admin":
            return redirect(url_for("login_page"))
        return render_template("students.html")

    @app.route("/admin/subjects")
    def subjects_page():
        if session.get("role") != "admin":
            return redirect(url_for("login_page"))
        return render_template("subjects.html")

    @app.route("/admin/marks")
    def marks_page():
        if session.get("role") != "admin":
            return redirect(url_for("login_page"))
        return render_template("marks.html")

    @app.route("/admin/results")
    def results_page():
        if session.get("role") != "admin":
            return redirect(url_for("login_page"))
        return render_template("results.html")

    @app.route("/admin/result/<int:student_id>")
    def admin_view_result(student_id):
        if session.get("role") != "admin":
            return redirect(url_for("login_page"))
        return render_template(
            "result.html",
            student_id=student_id,
            viewer="admin"
        )

    @app.route("/student/dashboard")
    def student_dashboard():
        if session.get("role") != "student":
            return redirect(url_for("login_page"))
        return render_template(
            "student_dashboard.html",
            name=session.get("name")
        )

    @app.route("/student/result")
    def student_result():
        if session.get("role") != "student":
            return redirect(url_for("login_page"))
        return render_template(
            "result.html",
            student_id=session.get("student_id"),
            viewer="student"
        )

    # ---------------- Error handlers ----------------

    @app.errorhandler(404)
    def not_found(error):
        return render_template("index.html"), 404

    @app.errorhandler(500)
    def server_error(error):
        return {"error": "Internal server error"}, 500

    return app


# Create Flask application
app = create_app()

# Initialize database when the application starts
init_db()


# Local development
if __name__ == "__main__":
    app.run(debug=True)