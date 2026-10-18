"""
Integration tests for student CRUD operations and PyMongo update operators.
"""

import pytest


def test_create_and_get_student(student_service):
    """Test creating a new student and retrieving by ID."""
    student_data = {
        "_id": 501,
        "name": "Integration Test Student",
        "email": "integration.student@university.edu",
        "department": "CSE",
        "semester": 6,
        "attendance": 88.0,
        "marks": {"CSE494": 89.0, "CSE401": 91.0},
        "skills": ["Python", "PyMongo", "Testing"]
    }
    # Ensure not present before test
    student_service.delete_student(501)

    # CREATE
    res = student_service.create_student(student_data)
    assert res["success"] is True
    assert res["student_id"] == 501

    # READ
    fetched = student_service.get_student_by_id(501)
    assert fetched is not None
    assert fetched["name"] == "Integration Test Student"
    assert fetched["email"] == "integration.student@university.edu"
    assert fetched["marks"]["CSE494"] == 89.0


def test_duplicate_student_id_prevention(student_service):
    """Test that creating a student with an existing _id is rejected with 409."""
    student_data = {
        "_id": 502,
        "name": "Original Student",
        "email": "orig.student502@university.edu",
        "department": "IT",
        "semester": 4,
        "attendance": 82.0,
        "marks": {"IT301": 80.0}
    }
    student_service.delete_student(502)
    student_service.create_student(student_data)

    # Attempt to insert duplicate ID with different email
    dup_data = {
        "_id": 502,
        "name": "Duplicate Student",
        "email": "different.email@university.edu",
        "department": "IT",
        "semester": 4,
        "attendance": 75.0,
        "marks": {"IT301": 70.0}
    }
    res = student_service.create_student(dup_data)
    assert res["success"] is False
    assert res["status_code"] == 409
    assert "_id" in res["errors"]


def test_duplicate_email_prevention(student_service):
    """Test that creating a student with an existing email violates unique index."""
    student_data = {
        "_id": 503,
        "name": "Unique Email Student",
        "email": "shared.email@university.edu",
        "department": "ECE",
        "semester": 5,
        "attendance": 90.0,
        "marks": {"ECE204": 85.0}
    }
    student_service.delete_student(503)
    student_service.delete_student(504)
    student_service.create_student(student_data)

    # Attempt to insert different ID with same email
    dup_email_data = {
        "_id": 504,
        "name": "Second Student",
        "email": "shared.email@university.edu",
        "department": "ME",
        "semester": 3,
        "attendance": 85.0,
        "marks": {"CSE401": 75.0}
    }
    res = student_service.create_student(dup_email_data)
    assert res["success"] is False
    assert res["status_code"] == 409
    assert "email" in res["errors"]


def test_update_student_details(student_service):
    """Test updating student details using update_one and $set."""
    student_id = 505
    student_service.delete_student(student_id)
    student_service.create_student({
        "_id": student_id,
        "name": "Pre-Update Name",
        "email": "update.student@university.edu",
        "department": "CSE",
        "semester": 2,
        "attendance": 70.0,
        "marks": {"CSE401": 65.0}
    })

    # UPDATE
    update_res = student_service.update_student(student_id, {
        "name": "Post-Update Name",
        "semester": 3,
        "attendance": 85.5
    })
    assert update_res["success"] is True

    # Verify updated doc
    updated = student_service.get_student_by_id(student_id)
    assert updated["name"] == "Post-Update Name"
    assert updated["semester"] == 3
    assert updated["attendance"] == 85.5


def test_add_or_update_course_mark(student_service):
    """Test updating embedded document field marks.<course_code>."""
    student_id = 506
    student_service.delete_student(student_id)
    student_service.create_student({
        "_id": student_id,
        "name": "Marks Test Student",
        "email": "marks.test@university.edu",
        "department": "CSE",
        "semester": 7,
        "attendance": 92.0,
        "marks": {"CSE494": 85.0}
    })

    # Add a new course score into embedded marks
    res = student_service.add_or_update_course_mark(student_id, "CSE405", 94.5)
    assert res["success"] is True

    updated = student_service.get_student_by_id(student_id)
    assert updated["marks"]["CSE494"] == 85.0
    assert updated["marks"]["CSE405"] == 94.5


def test_add_skills_array_addToSet(student_service):
    """Test adding skills using array operator $addToSet (no duplicates)."""
    student_id = 507
    student_service.delete_student(student_id)
    student_service.create_student({
        "_id": student_id,
        "name": "Skills Test Student",
        "email": "skills.test@university.edu",
        "department": "AIDS",
        "semester": 5,
        "attendance": 88.0,
        "skills": ["Python", "SQL"]
    })

    # Add new and duplicate skills
    student_service.add_skills(student_id, ["Python", "TensorFlow", "PyTorch"])

    updated = student_service.get_student_by_id(student_id)
    # Python should only appear once
    assert updated["skills"].count("Python") == 1
    assert "TensorFlow" in updated["skills"]
    assert "PyTorch" in updated["skills"]


def test_delete_student(student_service):
    """Test deleting student and verifying 404 on subsequent read."""
    student_id = 508
    student_service.create_student({
        "_id": student_id,
        "name": "To Be Deleted",
        "email": "tobedeleted@university.edu",
        "department": "ME",
        "semester": 1,
        "attendance": 75.0
    })

    del_res = student_service.delete_student(student_id)
    assert del_res["success"] is True

    # Confirm non-existence
    assert student_service.get_student_by_id(student_id) is None

    # Deleting again returns 404
    second_del = student_service.delete_student(student_id)
    assert second_del["success"] is False
    assert second_del["status_code"] == 404


def test_pagination_and_filters(student_service):
    """Test filtering by department, semester, and attendance bounds."""
    # Query CSE department
    result = student_service.get_students(department="CSE", page=1, page_size=5)
    assert "students" in result
    assert result["total"] > 0
    for s in result["students"]:
        assert s["department"] == "CSE"

    # Query with attendance range [80, 95]
    att_res = student_service.get_students(min_attendance=80, max_attendance=95)
    for s in att_res["students"]:
        assert 80 <= s["attendance"] <= 95
