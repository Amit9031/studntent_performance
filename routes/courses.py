"""
Course Management Routes and REST API Endpoints.
Handles Web UI views and JSON API endpoints for course CRUD operations.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from services.course_service import CourseService
from routes import serialize_doc

courses_bp = Blueprint("courses", __name__)


# ==============================================================
# WEB UI ROUTES
# ==============================================================

@courses_bp.route("/courses")
def list_courses():
    """Display course catalog with department filter and enrollment metrics."""
    course_service = CourseService()
    dept = request.args.get("department", "").strip()
    search = request.args.get("q", "").strip()

    courses = course_service.get_courses(department=dept, search=search)
    departments = course_service.get_distinct_departments()

    return render_template(
        "courses.html",
        courses=courses,
        departments=departments,
        selected_dept=dept,
        selected_search=search
    )


@courses_bp.route("/courses/new", methods=["POST"])
def add_course_view():
    """Handle course creation from web modal."""
    course_service = CourseService()
    data = {
        "_id": request.form.get("_id"),
        "course_name": request.form.get("course_name"),
        "credits": request.form.get("credits"),
        "department": request.form.get("department"),
        "description": request.form.get("description", "")
    }

    res = course_service.create_course(data)
    if res["success"]:
        flash(f"Course '{data['_id']}' added successfully!", "success")
    else:
        err_msg = list(res.get("errors", {}).values())[0] if res.get("errors") else "Course creation failed."
        flash(f"Error: {err_msg}", "danger")

    return redirect(url_for("courses.list_courses"))


@courses_bp.route("/courses/<course_id>/edit", methods=["POST"])
def edit_course_view(course_id):
    """Handle course update from web modal."""
    course_service = CourseService()
    data = {
        "course_name": request.form.get("course_name"),
        "credits": request.form.get("credits"),
        "department": request.form.get("department"),
        "description": request.form.get("description", "")
    }

    res = course_service.update_course(course_id, data)
    if res["success"]:
        flash(f"Course '{course_id}' updated successfully!", "success")
    else:
        err_msg = list(res.get("errors", {}).values())[0] if res.get("errors") else "Update failed."
        flash(f"Error: {err_msg}", "danger")

    return redirect(url_for("courses.list_courses"))


@courses_bp.route("/courses/<course_id>/delete", methods=["POST"])
def delete_course_view(course_id):
    """Handle course deletion from web interface."""
    course_service = CourseService()
    res = course_service.delete_course(course_id)
    if res["success"]:
        flash(res["message"], "success")
    else:
        flash(res["message"], "danger")

    return redirect(url_for("courses.list_courses"))


# ==============================================================
# REST API ENDPOINTS
# ==============================================================

@courses_bp.route("/api/courses", methods=["GET"])
def api_get_courses():
    """
    GET /api/courses
    Retrieve course catalog with optional department and search query filters.
    """
    course_service = CourseService()
    dept = request.args.get("department")
    search = request.args.get("q")
    courses = course_service.get_courses(department=dept, search=search)
    return jsonify(serialize_doc(courses)), 200


@courses_bp.route("/api/courses/<course_id>", methods=["GET"])
def api_get_course_by_id(course_id):
    """
    GET /api/courses/<course_id>
    Retrieve single course details by course code.
    """
    course_service = CourseService()
    course = course_service.get_course_by_id(course_id)
    if not course:
        return jsonify({"error": f"Course '{course_id}' not found."}), 404
    return jsonify(serialize_doc(course)), 200


@courses_bp.route("/api/courses", methods=["POST"])
def api_create_course():
    """
    POST /api/courses
    Register a new course. Request body must be valid JSON matching course schema.
    """
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json."}), 415

    data = request.get_json()
    course_service = CourseService()
    result = course_service.create_course(data)

    if result["success"]:
        return jsonify(serialize_doc(result)), 201
    return jsonify(serialize_doc(result)), result.get("status_code", 400)


@courses_bp.route("/api/courses/<course_id>", methods=["PUT"])
def api_update_course(course_id):
    """
    PUT /api/courses/<course_id>
    Update course details.
    """
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json."}), 415

    data = request.get_json()
    course_service = CourseService()
    result = course_service.update_course(course_id, data)

    if result["success"]:
        return jsonify(serialize_doc(result)), 200
    return jsonify(serialize_doc(result)), result.get("status_code", 400)


@courses_bp.route("/api/courses/<course_id>", methods=["DELETE"])
def api_delete_course(course_id):
    """
    DELETE /api/courses/<course_id>
    Delete course by course code (prevents deletion if students enrolled).
    """
    course_service = CourseService()
    result = course_service.delete_course(course_id)
    return jsonify(serialize_doc(result)), result.get("status_code", 200)
