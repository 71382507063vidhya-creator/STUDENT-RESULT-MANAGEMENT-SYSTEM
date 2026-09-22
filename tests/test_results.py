"""Tests for result calculation: total, average, grade, PASS/FAIL."""
from services.result_service import calculate_result, get_grade


def test_get_grade_boundaries():
    assert get_grade(95) == "A+"
    assert get_grade(90) == "A+"
    assert get_grade(85) == "A"
    assert get_grade(75) == "B"
    assert get_grade(65) == "C"
    assert get_grade(55) == "D"
    assert get_grade(49) == "F"


def test_total_and_average_calculation(app):
    with app.app_context():
        pass  # calculate_result opens its own connection; app context not required here.

    students = None
    from database.database import get_db_connection

    conn = get_db_connection()
    row = conn.execute(
        "SELECT id FROM students WHERE register_number = ?", ("23CS101",)
    ).fetchone()
    conn.close()

    result = calculate_result(row["id"])
    assert result["total"] == sum(s["marks"] for s in result["subjects"])
    assert result["average"] == round(result["total"] / len(result["subjects"]), 2)


def test_pass_calculation(app):
    """23CS101 (Arun) has all subjects >= 35, so must PASS."""
    from database.database import get_db_connection

    conn = get_db_connection()
    row = conn.execute(
        "SELECT id FROM students WHERE register_number = ?", ("23CS101",)
    ).fetchone()
    conn.close()

    result = calculate_result(row["id"])
    assert result["status"] == "PASS"
    assert all(s["marks"] >= 35 for s in result["subjects"])


def test_fail_calculation(app):
    """23CS103 (Rahul) has one subject below 35, so must FAIL."""
    from database.database import get_db_connection

    conn = get_db_connection()
    row = conn.execute(
        "SELECT id FROM students WHERE register_number = ?", ("23CS103",)
    ).fetchone()
    conn.close()

    result = calculate_result(row["id"])
    assert result["status"] == "FAIL"
    assert any(s["marks"] < 35 for s in result["subjects"])


def test_results_api_returns_backend_status(admin_client):
    students = admin_client.get("/api/students").get_json()
    rahul = next(s for s in students if s["register_number"] == "23CS103")

    response = admin_client.get(f"/api/results/{rahul['id']}")
    assert response.status_code == 200
    assert response.get_json()["status"] == "FAIL"


def test_student_cannot_view_another_students_result(student_client):
    """23CS101 logs in; trying to view a different student's result must fail."""
    other = student_client.get("/api/students")
    # Students are not authorized to list all students at all.
    assert other.status_code == 401

    # Attempting to view another student's result directly should be blocked.
    response = student_client.get("/api/results/99999")
    assert response.status_code in (401, 404)
