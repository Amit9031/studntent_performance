"""
Integration tests for course CRUD operations and cross-collection integrity.
"""

import pytest


def test_create_and_get_course(course_service):
    """Test creating a new course and retrieving by code."""
    course_data = {
        "_id": "CSE480",
        "course_name": "Cloud Computing Architecture",
        "credits": 3,
        "department": "CSE",
        "description": "AWS, GCP, Virtualization, and Kubernetes."
    }
    course_service.delete_course("CSE480")

    # CREATE
    res = course_service.create_course(course_data)
    assert res["success"] is True
    assert res["course_id"] == "CSE480"

    # READ
    fetched = course_service.get_course_by_id("CSE480")
    assert fetched is not None
    assert fetched["course_name"] == "Cloud Computing Architecture"
    assert fetched["credits"] == 3


def test_duplicate_course_prevention(course_service):
    """Test that creating a course with an existing _id is rejected with 409."""
    course_data = {
        "_id": "CSE481",
        "course_name": "Quantum Computing",
        "credits": 4,
        "department": "CSE"
    }
    course_service.delete_course("CSE481")
    course_service.create_course(course_data)

    # Duplicate insertion
    res = course_service.create_course(course_data)
    assert res["success"] is False
    assert res["status_code"] == 409


def test_update_course(course_service):
    """Test updating course attributes."""
    course_id = "CSE482"
    course_service.delete_course(course_id)
    course_service.create_course({
        "_id": course_id,
        "course_name": "Original Course Title",
        "credits": 3,
        "department": "IT"
    })

    res = course_service.update_course(course_id, {
        "course_name": "Updated Advanced Course Title",
        "credits": 4
    })
    assert res["success"] is True

    updated = course_service.get_course_by_id(course_id)
    assert updated["course_name"] == "Updated Advanced Course Title"
    assert updated["credits"] == 4


def test_delete_course_with_enrolled_students(course_service, student_service):
    """
    Test integrity rule: Courses with enrolled students / recorded marks
    cannot be deleted.
    """
    # Create test course and enroll a student
    course_id = "CSE483"
    student_id = 550

    course_service.delete_course(course_id)
    course_service.create_course({
        "_id": course_id,
        "course_name": "Data Mining",
        "credits": 3,
        "department": "CSE"
    })

    student_service.delete_student(student_id)
    student_service.create_student({
        "_id": student_id,
        "name": "Enrolled Student",
        "email": "enrolled550@test.edu",
        "department": "CSE",
        "semester": 6,
        "attendance": 90.0,
        "marks": {course_id: 88.0}
    })

    # Attempt to delete course
    del_res = course_service.delete_course(course_id)
    assert del_res["success"] is False
    assert del_res["status_code"] == 400
    assert "Cannot delete course" in del_res["message"]

    # Now unenroll student and test successful deletion
    student_service.delete_student(student_id)
    del_res_2 = course_service.delete_course(course_id)
    assert del_res_2["success"] is True
