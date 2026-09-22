"""Shared pytest fixtures for the test suite."""
import os
import tempfile

import pytest

from config import Config


@pytest.fixture
def app():
    """Create a Flask app configured to use a temporary SQLite database."""
    db_fd, db_path = tempfile.mkstemp()
    Config.DATABASE_PATH = db_path

    # Import after patching the DB path so init_db() uses the temp file.
    from app import create_app
    from database.database import init_db

    flask_app = create_app()
    flask_app.config.update({"TESTING": True})

    init_db()

    yield flask_app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def admin_client(client):
    """A test client already logged in as the demo admin."""
    client.post("/api/admin/login", json={"username": "admin", "password": "admin123"})
    return client


@pytest.fixture
def student_client(client):
    """A test client already logged in as a demo student (23CS101 - a PASS student)."""
    client.post(
        "/api/student/login",
        json={"register_number": "23CS101", "password": "pass123"},
    )
    return client
