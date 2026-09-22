"""
Result calculation service.

This module is the SINGLE SOURCE OF TRUTH for result calculations.
The frontend never decides PASS/FAIL on its own - it only displays
whatever this service returns.
"""
from config import Config
from database.database import get_db_connection


def get_grade(average):
    """Convert a numeric average into a letter grade."""
    if average >= 90:
        return "A+"
    if average >= 80:
        return "A"
    if average >= 70:
        return "B"
    if average >= 60:
        return "C"
    if average >= 50:
        return "D"
    return "F"


def calculate_result(student_id):
    """
    Calculate the full result for a single student.

    Returns a dictionary with subject-wise marks, total, average, grade
    and PASS/FAIL status, or None if the student has no marks recorded.
    """
    conn = get_db_connection()
    student = conn.execute(
        "SELECT * FROM students WHERE id = ?", (student_id,)
    ).fetchone()

    if student is None:
        conn.close()
        return None

    rows = conn.execute(
        """
        SELECT marks.marks AS marks,
               subjects.subject_code AS subject_code,
               subjects.subject_name AS subject_name
        FROM marks
        JOIN subjects ON marks.subject_id = subjects.id
        WHERE marks.student_id = ?
        ORDER BY subjects.subject_code
        """,
        (student_id,),
    ).fetchall()
    conn.close()

    if len(rows) == 0:
        return {
            "student_id": student["id"],
            "name": student["name"],
            "register_number": student["register_number"],
            "department": student["department"],
            "year": student["year"],
            "semester": student["semester"],
            "subjects": [],
            "total": 0,
            "average": 0,
            "grade": "N/A",
            "status": "NO_RESULT",
        }

    subjects = [
        {
            "subject_code": row["subject_code"],
            "subject_name": row["subject_name"],
            "marks": row["marks"],
        }
        for row in rows
    ]

    total = sum(subject["marks"] for subject in subjects)
    average = round(total / len(subjects), 2)
    grade = get_grade(average)

    # A student passes ONLY if every subject mark is >= the passing threshold.
    status = "PASS" if all(s["marks"] >= Config.PASSING_MARK for s in subjects) else "FAIL"

    return {
        "student_id": student["id"],
        "name": student["name"],
        "register_number": student["register_number"],
        "department": student["department"],
        "year": student["year"],
        "semester": student["semester"],
        "subjects": subjects,
        "total": total,
        "average": average,
        "grade": grade,
        "status": status,
    }


def calculate_all_results():
    """Calculate results for every student in the database."""
    conn = get_db_connection()
    student_ids = [row["id"] for row in conn.execute("SELECT id FROM students").fetchall()]
    conn.close()
    return [calculate_result(sid) for sid in student_ids]


def get_dashboard_stats():
    """Aggregate statistics used by the admin dashboard cards and chart."""
    conn = get_db_connection()
    total_students = conn.execute("SELECT COUNT(*) AS c FROM students").fetchone()["c"]
    total_subjects = conn.execute("SELECT COUNT(*) AS c FROM subjects").fetchone()["c"]
    total_results = conn.execute(
        "SELECT COUNT(DISTINCT student_id) AS c FROM marks"
    ).fetchone()["c"]
    conn.close()

    results = [r for r in calculate_all_results() if r["status"] in ("PASS", "FAIL")]
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    pass_percentage = round((passed / total_results) * 100, 2) if total_results else 0

    department_stats = {}
    for r in results:
        dept = r["department"]
        department_stats.setdefault(dept, {"passed": 0, "failed": 0})
        if r["status"] == "PASS":
            department_stats[dept]["passed"] += 1
        else:
            department_stats[dept]["failed"] += 1

    return {
        "total_students": total_students,
        "total_subjects": total_subjects,
        "total_results": total_results,
        "passed_students": passed,
        "failed_students": failed,
        "pass_percentage": pass_percentage,
        "department_stats": department_stats,
        "recent_results": results[-5:],
    }
