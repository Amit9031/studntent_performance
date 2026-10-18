"""
Student Management Routes and REST API Endpoints.
Handles Web UI views and JSON API endpoints for student CRUD operations.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from services.student_service import StudentService
from services.course_service import CourseService
from services.prediction_service import AcademicRiskPredictor
from routes import serialize_doc

students_bp = Blueprint("students", __name__)


# ==============================================================
# WEB UI ROUTES
# ==============================================================

@students_bp.route("/students")
def list_students():
    """Display paginated list of students with search and filter capabilities."""
    student_service = StudentService()
    course_service = CourseService()

    query = request.args.get("q", "").strip()
    department = request.args.get("department", "").strip()
    semester = request.args.get("semester", "").strip()
    min_att = request.args.get("min_attendance", "").strip()
    max_att = request.args.get("max_attendance", "").strip()
    page = request.args.get("page", 1)

    result = student_service.get_students(
        query=query,
        department=department,
        semester=semester,
        min_attendance=min_att,
        max_attendance=max_att,
        page=page,
        page_size=10
    )

    departments = student_service.get_distinct_departments()
    semesters = student_service.get_distinct_semesters()

    return render_template(
        "students.html",
        students=result["students"],
        total=result["total"],
        page=result["page"],
        total_pages=result["total_pages"],
        departments=departments,
        semesters=semesters,
        selected_dept=department,
        selected_sem=semester,
        selected_query=query,
        selected_min_att=min_att,
        selected_max_att=max_att
    )


@students_bp.route("/students/new", methods=["GET", "POST"])
def add_student():
    """Render and process student creation form."""
    student_service = StudentService()
    course_service = CourseService()
    courses = course_service.get_courses()

    if request.method == "POST":
        # Extract form inputs
        data = {
            "_id": request.form.get("_id"),
            "name": request.form.get("name"),
            "email": request.form.get("email"),
            "department": request.form.get("department"),
            "semester": request.form.get("semester"),
            "attendance": request.form.get("attendance"),
            "skills": request.form.get("skills", "")
        }

        # Build marks dictionary from dynamic course inputs
        marks = {}
        for course in courses:
            mark_val = request.form.get(f"mark_{course['_id']}")
            if mark_val is not None and mark_val.strip() != "":
                marks[course["_id"]] = mark_val
        data["marks"] = marks

        result = student_service.create_student(data)
        if result["success"]:
            flash(f"Student '{data['name']}' (ID: {data['_id']}) registered successfully!", "success")
            return redirect(url_for("students.student_detail", student_id=data["_id"]))
        else:
            flash(f"Error: {list(result.get('errors', {}).values())[0]}", "danger")
            return render_template("student_form.html", mode="create", courses=courses, form_data=data, errors=result.get("errors", {}))

    return render_template("student_form.html", mode="create", courses=courses, form_data={}, errors={})


@students_bp.route("/students/<student_id>")
def student_detail(student_id):
    """View detailed student academic profile and intelligent risk evaluation."""
    student_service = StudentService()
    course_service = CourseService()
    predictor = AcademicRiskPredictor()

    student = student_service.get_student_by_id(student_id)
    if not student:
        flash(f"Student ID '{student_id}' does not exist.", "warning")
        return redirect(url_for("students.list_students"))

    # Compute risk prediction
    risk_report = predictor.predict_for_student(student)
    courses_map = {c["_id"]: c for c in course_service.get_courses()}

    return render_template(
        "student_details.html",
        student=student,
        risk_report=risk_report,
        courses_map=courses_map
    )


@students_bp.route("/students/<student_id>/edit", methods=["GET", "POST"])
def edit_student(student_id):
    """Render and process student update form."""
    student_service = StudentService()
    course_service = CourseService()
    courses = course_service.get_courses()

    student = student_service.get_student_by_id(student_id)
    if not student:
        flash(f"Student ID '{student_id}' not found.", "warning")
        return redirect(url_for("students.list_students"))

    if request.method == "POST":
        data = {
            "name": request.form.get("name"),
            "email": request.form.get("email"),
            "department": request.form.get("department"),
            "semester": request.form.get("semester"),
            "attendance": request.form.get("attendance"),
            "skills": request.form.get("skills", "")
        }

        marks = {}
        for course in courses:
            mark_val = request.form.get(f"mark_{course['_id']}")
            if mark_val is not None and mark_val.strip() != "":
                marks[course["_id"]] = mark_val
        data["marks"] = marks

        result = student_service.update_student(student_id, data)
        if result["success"]:
            flash(f"Student '{student_id}' updated successfully!", "success")
            return redirect(url_for("students.student_detail", student_id=student_id))
        else:
            flash(f"Update failed: {list(result.get('errors', {}).values())[0]}", "danger")
            return render_template("student_form.html", mode="edit", student=student, courses=courses, form_data=data, errors=result.get("errors", {}))

    return render_template("student_form.html", mode="edit", student=student, courses=courses, form_data=student, errors={})


@students_bp.route("/students/<student_id>/delete", methods=["POST"])
def delete_student_view(student_id):
    """Handle student deletion from web interface."""
    student_service = StudentService()
    res = student_service.delete_student(student_id)
    if res["success"]:
        flash(res["message"], "success")
    else:
        flash(res["message"], "danger")
    return redirect(url_for("students.list_students"))


# ==============================================================
# REST API ENDPOINTS
# ==============================================================

@students_bp.route("/api/students", methods=["GET"])
def api_get_students():
    """
    GET /api/students
    Query parameters: q, department, semester, min_attendance, max_attendance, page, page_size
    """
    student_service = StudentService()
    q = request.args.get("q")
    dept = request.args.get("department")
    sem = request.args.get("semester")
    min_att = request.args.get("min_attendance")
    max_att = request.args.get("max_attendance")
    page = request.args.get("page", 1)
    page_size = request.args.get("page_size", 10)

    result = student_service.get_students(
        query=q,
        department=dept,
        semester=sem,
        min_attendance=min_att,
        max_attendance=max_att,
        page=page,
        page_size=page_size
    )
    return jsonify(serialize_doc(result)), 200


@students_bp.route("/api/students/<student_id>", methods=["GET"])
def api_get_student_by_id(student_id):
    """
    GET /api/students/<student_id>
    Retrieve single student record by numeric ID.
    """
    student_service = StudentService()
    student = student_service.get_student_by_id(student_id)
    if not student:
        return jsonify({"error": f"Student with ID '{student_id}' not found."}), 404
    return jsonify(serialize_doc(student)), 200


@students_bp.route("/api/students", methods=["POST"])
def api_create_student():
    """
    POST /api/students
    Register a new student. Request body must be valid JSON matching student schema.
    """
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json."}), 415

    data = request.get_json()
    student_service = StudentService()
    result = student_service.create_student(data)

    if result["success"]:
        return jsonify(serialize_doc(result)), 201
    return jsonify(serialize_doc(result)), result.get("status_code", 400)


@students_bp.route("/api/students/<student_id>", methods=["PUT"])
def api_update_student(student_id):
    """
    PUT /api/students/<student_id>
    Update an existing student record.
    """
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json."}), 415

    data = request.get_json()
    student_service = StudentService()
    result = student_service.update_student(student_id, data)

    if result["success"]:
        return jsonify(serialize_doc(result)), 200
    return jsonify(serialize_doc(result)), result.get("status_code", 400)


@students_bp.route("/api/students/<student_id>", methods=["DELETE"])
def api_delete_student(student_id):
    """
    DELETE /api/students/<student_id>
    Remove a student record.
    """
    student_service = StudentService()
    result = student_service.delete_student(student_id)
    return jsonify(serialize_doc(result)), result.get("status_code", 200)
