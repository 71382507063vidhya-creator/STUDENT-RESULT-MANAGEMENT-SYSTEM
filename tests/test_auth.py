"""Tests for admin and student authentication."""


def test_admin_login_success(client):
    response = client.post(
        "/api/admin/login", json={"username": "admin", "password": "admin123"}
    )
    assert response.status_code == 200
    assert response.get_json()["role"] == "admin"


def test_admin_login_failure_wrong_password(client):
    response = client.post(
        "/api/admin/login", json={"username": "admin", "password": "wrongpass"}
    )
    assert response.status_code == 401
    assert "error" in response.get_json()


def test_admin_login_failure_missing_fields(client):
    response = client.post("/api/admin/login", json={"username": "admin"})
    assert response.status_code == 400


def test_student_login_success(client):
    response = client.post(
        "/api/student/login",
        json={"register_number": "23CS101", "password": "pass123"},
    )
    assert response.status_code == 200
    assert response.get_json()["role"] == "student"


def test_student_login_failure(client):
    response = client.post(
        "/api/student/login",
        json={"register_number": "23CS101", "password": "wrongpass"},
    )
    assert response.status_code == 401


def test_logout_clears_session(admin_client):
    response = admin_client.post("/api/logout")
    assert response.status_code == 200

    # After logout, an admin-only endpoint should be unauthorized.
    protected = admin_client.get("/api/students")
    assert protected.status_code == 401


def test_unauthenticated_access_is_blocked(client):
    response = client.get("/api/students")
    assert response.status_code == 401
