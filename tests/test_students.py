"""Tests for student CRUD operations, subjects, and marks validation."""


def _create_student(admin_client, register_number="23CS999"):
    return admin_client.post(
        "/api/students",
        json={
            "name": "Test Student",
            "register_number": register_number,
            "email": "test.student@example.com",
            "department": "Computer Science",
            "year": 2,
            "semester": 3,
            "password": "secret123",
        },
    )


def test_create_student(admin_client):
    response = _create_student(admin_client)
    assert response.status_code == 201
    assert "id" in response.get_json()


def test_retrieve_student(admin_client):
    create_res = _create_student(admin_client, "23CS888")
    student_id = create_res.get_json()["id"]

    response = admin_client.get(f"/api/students/{student_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["register_number"] == "23CS888"
    assert "password" not in data  # password must never be exposed


def test_update_student(admin_client):
    create_res = _create_student(admin_client, "23CS777")
    student_id = create_res.get_json()["id"]

    response = admin_client.put(
        f"/api/students/{student_id}",
        json={
            "name": "Updated Name",
            "register_number": "23CS777",
            "email": "updated@example.com",
            "department": "Computer Science",
            "year": 3,
            "semester": 5,
        },
    )
    assert response.status_code == 200

    fetched = admin_client.get(f"/api/students/{student_id}").get_json()
    assert fetched["name"] == "Updated Name"
    assert fetched["year"] == 3


def test_delete_student(admin_client):
    create_res = _create_student(admin_client, "23CS666")
    student_id = create_res.get_json()["id"]

    response = admin_client.delete(f"/api/students/{student_id}")
    assert response.status_code == 200

    fetched = admin_client.get(f"/api/students/{student_id}")
    assert fetched.status_code == 404


def test_duplicate_register_number_rejected(admin_client):
    _create_student(admin_client, "23CS555")
    duplicate = _create_student(admin_client, "23CS555")
    assert duplicate.status_code == 400


def test_invalid_email_rejected(admin_client):
    response = admin_client.post(
        "/api/students",
        json={
            "name": "Bad Email",
            "register_number": "23CS444",
            "email": "not-an-email",
            "department": "Computer Science",
            "year": 1,
            "semester": 1,
            "password": "secret123",
        },
    )
    assert response.status_code == 400


def test_marks_valid(admin_client):
    students = admin_client.get("/api/students").get_json()
    subjects = admin_client.get("/api/subjects").get_json()
    student_id = students[0]["id"]
    subject_id = subjects[0]["id"]

    # Remove any existing mark first (demo data may already have one).
    existing = admin_client.get(
        f"/api/marks?student_id={student_id}&subject_id={subject_id}"
    ).get_json()
    for m in existing:
        admin_client.delete(f"/api/marks/{m['id']}")

    response = admin_client.post(
        "/api/marks", json={"student_id": student_id, "subject_id": subject_id, "marks": 75}
    )
    assert response.status_code == 201


def test_marks_below_zero_rejected(admin_client):
    students = admin_client.get("/api/students").get_json()
    subjects = admin_client.get("/api/subjects").get_json()
    response = admin_client.post(
        "/api/marks",
        json={"student_id": students[0]["id"], "subject_id": subjects[1]["id"], "marks": -5},
    )
    assert response.status_code == 400


def test_marks_above_hundred_rejected(admin_client):
    students = admin_client.get("/api/students").get_json()
    subjects = admin_client.get("/api/subjects").get_json()
    response = admin_client.post(
        "/api/marks",
        json={"student_id": students[0]["id"], "subject_id": subjects[2]["id"], "marks": 150},
    )
    assert response.status_code == 400


def test_duplicate_marks_rejected(admin_client):
    students = admin_client.get("/api/students").get_json()
    subjects = admin_client.get("/api/subjects").get_json()
    student_id = students[1]["id"]
    subject_id = subjects[3]["id"]

    existing = admin_client.get(
        f"/api/marks?student_id={student_id}&subject_id={subject_id}"
    ).get_json()
    for m in existing:
        admin_client.delete(f"/api/marks/{m['id']}")

    first = admin_client.post(
        "/api/marks", json={"student_id": student_id, "subject_id": subject_id, "marks": 60}
    )
    assert first.status_code == 201

    duplicate = admin_client.post(
        "/api/marks", json={"student_id": student_id, "subject_id": subject_id, "marks": 65}
    )
    assert duplicate.status_code == 400
