"""
Application configuration.
"""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration for the Student Result Management System."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    DATABASE_PATH = os.path.join(BASE_DIR, "database", "database.db")
    PASSING_MARK = 35          # Minimum marks required in a subject to pass it
    MAX_MARK = 100
    MIN_MARK = 0
    DEBUG = True
