"""
Unit tests for data validation logic.
Tests validation of student payloads, course payloads, invalid attendance, and invalid marks.
"""

from database.validators import validate_student_payload, validate_course_payload


def test_valid_student_payload():
    """Test that a well-formed student payload passes validation."""
    data = {
        "_id": 999,
        "name": "Validation Student",
        "email": "validation@test.edu",
        "department": "CSE",
        "semester": 4,
        "attendance": 88.5,
        "marks": {"CSE494": 92.0, "CSE401": 85.0},
        "skills": ["Python", "MongoDB"]
    }
    is_valid, errors, cleaned = validate_student_payload(data)
    assert is_valid is True
    assert len(errors) == 0
    assert cleaned["_id"] == 999
    assert cleaned["department"] == "CSE"
    assert cleaned["attendance"] == 88.5


def test_invalid_student_id():
    """Test rejection of non-positive or non-integer student IDs."""
    # Negative ID
    is_valid, errors, _ = validate_student_payload({
        "_id": -5,
        "name": "Test",
        "email": "test@test.edu",
        "department": "CSE",
        "semester": 1,
        "attendance": 80.0
    })
    assert is_valid is False
    assert "_id" in errors

    # Missing ID on create
    is_valid, errors, _ = validate_student_payload({
        "name": "Test",
        "email": "test@test.edu",
        "department": "CSE",
        "semester": 1,
        "attendance": 80.0
    })
    assert is_valid is False
    assert "_id" in errors


def test_invalid_email_format():
    """Test rejection of malformed email addresses."""
    invalid_emails = ["notanemail", "user@", "@domain.com", "user@domain", "user space@domain.com"]
    for bad_email in invalid_emails:
        is_valid, errors, _ = validate_student_payload({
            "_id": 998,
            "name": "Test Student",
            "email": bad_email,
            "department": "CSE",
            "semester": 1,
            "attendance": 80.0
        })
        assert is_valid is False
        assert "email" in errors


def test_invalid_attendance_range():
    """Test that attendance below 0% or above 100% is rejected."""
    # Over 100%
    is_valid, errors, _ = validate_student_payload({
        "_id": 997,
        "name": "Over Attend",
        "email": "over@test.edu",
        "department": "IT",
        "semester": 2,
        "attendance": 105.0
    })
    assert is_valid is False
    assert "attendance" in errors

    # Under 0%
    is_valid, errors, _ = validate_student_payload({
        "_id": 996,
        "name": "Under Attend",
        "email": "under@test.edu",
        "department": "IT",
        "semester": 2,
        "attendance": -10.0
    })
    assert is_valid is False
    assert "attendance" in errors


def test_invalid_marks_range():
    """Test that course marks below 0 or above 100 are rejected."""
    # Score > 100
    is_valid, errors, _ = validate_student_payload({
        "_id": 995,
        "name": "High Mark",
        "email": "highmark@test.edu",
        "department": "ECE",
        "semester": 3,
        "attendance": 85.0,
        "marks": {"CSE494": 150.0}
    })
    assert is_valid is False
    assert "marks.CSE494" in errors

    # Negative Score
    is_valid, errors, _ = validate_student_payload({
        "_id": 994,
        "name": "Low Mark",
        "email": "lowmark@test.edu",
        "department": "ECE",
        "semester": 3,
        "attendance": 85.0,
        "marks": {"CSE494": -5.0}
    })
    assert is_valid is False
    assert "marks.CSE494" in errors


def test_invalid_department():
    """Test rejection of non-permitted academic departments."""
    is_valid, errors, _ = validate_student_payload({
        "_id": 993,
        "name": "Invalid Dept",
        "email": "dept@test.edu",
        "department": "ASTRONOMY",
        "semester": 1,
        "attendance": 80.0
    })
    assert is_valid is False
    assert "department" in errors


def test_valid_course_payload():
    """Test valid course creation payload."""
    data = {
        "_id": "CSE599",
        "course_name": "Distributed Systems",
        "credits": 4,
        "department": "CSE",
        "description": "CAP Theorem, Paxos, Consensus, and Vector Clocks."
    }
    is_valid, errors, cleaned = validate_course_payload(data)
    assert is_valid is True
    assert cleaned["_id"] == "CSE599"
    assert cleaned["credits"] == 4


def test_invalid_course_payload():
    """Test rejection of invalid course credits or empty code."""
    # Invalid credits (> 10)
    is_valid, errors, _ = validate_course_payload({
        "_id": "CSE999",
        "course_name": "Too Many Credits",
        "credits": 20,
        "department": "CSE"
    })
    assert is_valid is False
    assert "credits" in errors

    # Missing course code
    is_valid, errors, _ = validate_course_payload({
        "_id": "",
        "course_name": "No Code",
        "credits": 3,
        "department": "IT"
    })
    assert is_valid is False
    assert "_id" in errors
