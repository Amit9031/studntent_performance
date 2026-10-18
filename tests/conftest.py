"""
Pytest configuration and fixtures.
Configures isolated test database 'student_analytics_test' to ensure test runs
never modify or delete production or demo application data.
"""

import os
import pytest
from database.connection import get_database, get_mongo_client
from database.validators import apply_collection_validators
from database.indexes import create_all_indexes
from database.seed import seed_database
from services.student_service import StudentService
from services.course_service import CourseService
from services.analytics_service import AnalyticsService
from app import create_app

TEST_DB_NAME = "student_analytics_test"


@pytest.fixture(scope="session")
def test_db():
    """
    Session-level fixture that connects to isolated test database,
    sets up validators and indexes, seeds deterministic sample data,
    and drops test collections on teardown.
    """
    client = get_mongo_client()
    db = client[TEST_DB_NAME]

    # Initialize test database schema and deterministic seed
    seed_database(db, drop_existing=True)

    yield db

    # Teardown: Clean up test collections after test suite completes
    db["students"].delete_many({})
    db["courses"].delete_many({})
    # Drop test database
    client.drop_database(TEST_DB_NAME)


@pytest.fixture
def student_service(test_db):
    """Fixture providing StudentService backed by the isolated test database."""
    return StudentService(db=test_db)


@pytest.fixture
def course_service(test_db):
    """Fixture providing CourseService backed by the isolated test database."""
    return CourseService(db=test_db)


@pytest.fixture
def analytics_service(test_db):
    """Fixture providing AnalyticsService backed by the isolated test database."""
    return AnalyticsService(db=test_db)


@pytest.fixture
def client(test_db):
    """Flask test client configured for the testing environment."""
    os.environ["DATABASE_NAME"] = TEST_DB_NAME
    app = create_app("testing")
    app.config["DATABASE_NAME"] = TEST_DB_NAME
    with app.test_client() as test_client:
        yield test_client
