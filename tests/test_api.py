"""
REST API endpoint tests.
Tests HTTP status codes, JSON response serialization, error responses, and CRUD endpoints.
"""

import json


def test_api_get_students(client):
    """Test GET /api/students returns 200 and list of students."""
    response = client.get("/api/students")
    assert response.status_code == 200
    data = response.get_json()
    assert "students" in data
    assert "total" in data
    assert len(data["students"]) > 0


def test_api_get_student_by_id(client):
    """Test GET /api/students/<id> for existing and non-existing students."""
    # Existing
    res = client.get("/api/students/101")
    assert res.status_code == 200
    student = res.get_json()
    assert student["_id"] == 101
    assert "marks" in student

    # Non-existing
    res_404 = client.get("/api/students/999999")
    assert res_404.status_code == 404
    assert "error" in res_404.get_json()


def test_api_create_student_lifecycle(client):
    """Test POST, PUT, and DELETE /api/students/<id>."""
    student_payload = {
        "_id": 777,
        "name": "REST API Test Student",
        "email": "rest.student777@university.edu",
        "department": "CSE",
        "semester": 5,
        "attendance": 84.0,
        "marks": {"CSE494": 90.0},
        "skills": ["Flask", "REST API", "PyMongo"]
    }

    # 1. CREATE (POST)
    res_post = client.post(
        "/api/students",
        data=json.dumps(student_payload),
        content_type="application/json"
    )
    assert res_post.status_code == 201
    post_data = res_post.get_json()
    assert post_data["success"] is True

    # 2. UPDATE (PUT)
    update_payload = {
        "name": "Updated REST Student",
        "attendance": 89.0
    }
    res_put = client.put(
        "/api/students/777",
        data=json.dumps(update_payload),
        content_type="application/json"
    )
    assert res_put.status_code == 200
    put_data = res_put.get_json()
    assert put_data["student"]["name"] == "Updated REST Student"

    # 3. DELETE
    res_del = client.delete("/api/students/777")
    assert res_del.status_code == 200

    # 4. Confirm Deletion
    res_get = client.get("/api/students/777")
    assert res_get.status_code == 404


def test_api_invalid_content_type(client):
    """Test that POST /api/students without application/json returns 415."""
    res = client.post("/api/students", data="not json")
    assert res.status_code == 415


def test_api_courses_endpoints(client):
    """Test GET, POST, and DELETE /api/courses."""
    # GET catalog
    res_list = client.get("/api/courses")
    assert res_list.status_code == 200
    courses = res_list.get_json()
    assert len(courses) > 0

    # POST new course
    course_payload = {
        "_id": "CSE777",
        "course_name": "API Testing Principles",
        "credits": 3,
        "department": "CSE",
        "description": "Integration testing REST endpoints."
    }
    res_post = client.post(
        "/api/courses",
        data=json.dumps(course_payload),
        content_type="application/json"
    )
    assert res_post.status_code == 201

    # GET single course
    res_get = client.get("/api/courses/CSE777")
    assert res_get.status_code == 200
    assert res_get.get_json()["course_name"] == "API Testing Principles"

    # DELETE course
    res_del = client.delete("/api/courses/CSE777")
    assert res_del.status_code == 200


def test_api_analytics_endpoints(client):
    """Test all /api/analytics/* endpoints return 200 and expected structures."""
    endpoints = [
        "/api/analytics/overview",
        "/api/analytics/topper-ranking",
        "/api/analytics/departments",
        "/api/analytics/course-statistics",
        "/api/analytics/at-risk",
        "/api/analytics/skills",
        "/api/analytics/performance-categories",
        "/api/analytics/semester-analytics",
        "/api/analytics/ml-model-info"
    ]
    for ep in endpoints:
        res = client.get(ep)
        assert res.status_code == 200, f"Endpoint {ep} failed with status {res.status_code}"


def test_api_predict_risk_endpoint(client):
    """Test GET /api/analytics/predict-risk/<id>."""
    res = client.get("/api/analytics/predict-risk/101")
    assert res.status_code == 200
    data = res.get_json()
    assert "rule_evaluation" in data
    assert "risk_level" in data["rule_evaluation"]
    assert "ml_prediction" in data
