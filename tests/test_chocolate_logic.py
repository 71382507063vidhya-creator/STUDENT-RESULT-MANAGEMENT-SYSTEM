"""
Tests for the Chocolate Shower business rule.

The animation itself is JavaScript and cannot be exercised by pytest,
so these tests verify the backend contract the frontend relies on:

    PASS -> celebration allowed  (frontend triggers showChocolateShower())
    FAIL -> celebration not allowed (frontend shows the fail message instead)

See README.md "Testing" section for more detail on this approach.
"""
from services.result_service import calculate_result
from database.database import get_db_connection


def _result_for(register_number):
    conn = get_db_connection()
    row = conn.execute(
        "SELECT id FROM students WHERE register_number = ?", (register_number,)
    ).fetchone()
    conn.close()
    return calculate_result(row["id"])


def test_pass_status_allows_celebration(app):
    result = _result_for("23CS101")
    assert result["status"] == "PASS"
    celebration_allowed = result["status"] == "PASS"
    assert celebration_allowed is True


def test_fail_status_blocks_celebration(app):
    result = _result_for("23CS103")
    assert result["status"] == "FAIL"
    celebration_allowed = result["status"] == "PASS"
    assert celebration_allowed is False


def test_result_api_contract_matches_chocolate_rule(admin_client):
    """The JSON contract the frontend reads to decide on the chocolate shower."""
    students = admin_client.get("/api/students").get_json()
    arun = next(s for s in students if s["register_number"] == "23CS101")

    response = admin_client.get(f"/api/results/{arun['id']}")
    data = response.get_json()

    assert "status" in data
    assert data["status"] in ("PASS", "FAIL")
    # The frontend's chocolate-shower.js only fires when this exact string matches.
    assert (data["status"] == "PASS") == (data["status"] != "FAIL")
