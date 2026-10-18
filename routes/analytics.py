"""
Analytics Routes and REST API Endpoints.
Exposes MongoDB Aggregation Framework pipelines and machine learning predictions.
"""

from flask import Blueprint, render_template, request, jsonify
from services.analytics_service import AnalyticsService
from services.student_service import StudentService
from services.prediction_service import AcademicRiskPredictor
from routes import serialize_doc

analytics_bp = Blueprint("analytics", __name__)


# ==============================================================
# WEB UI ROUTE
# ==============================================================

@analytics_bp.route("/analytics")
def analytics_view():
    """Render comprehensive analytics dashboard with real-time MongoDB aggregations."""
    analytics_service = AnalyticsService()
    predictor = AcademicRiskPredictor()

    # Pre-fetch MongoDB Aggregation Framework outputs
    dept_stats = analytics_service.get_department_performance()
    toppers = analytics_service.get_topper_ranking(limit=10)
    course_stats = analytics_service.get_course_statistics()
    at_risk = analytics_service.get_at_risk_students()
    skills = analytics_service.get_skill_distribution(limit=12)
    categories = analytics_service.get_performance_categories()
    semester_stats = analytics_service.get_semester_analytics()
    kpis = analytics_service.get_overview_kpis()

    # Train / fetch ML model evaluation status
    ml_train_result = predictor.train_model()

    return render_template(
        "analytics.html",
        dept_stats=dept_stats,
        toppers=toppers,
        course_stats=course_stats,
        at_risk=at_risk,
        skills=skills,
        categories=categories,
        semester_stats=semester_stats,
        kpis=kpis,
        ml_metrics=predictor.metrics or {}
    )


# ==============================================================
# REST API ENDPOINTS
# ==============================================================

@analytics_bp.route("/api/analytics/overview", methods=["GET"])
def api_analytics_overview():
    """GET /api/analytics/overview - Overall system KPIs via $facet."""
    service = AnalyticsService()
    return jsonify(serialize_doc(service.get_overview_kpis())), 200


@analytics_bp.route("/api/analytics/topper-ranking", methods=["GET"])
def api_topper_ranking():
    """GET /api/analytics/topper-ranking - Ranked student leaderboard."""
    service = AnalyticsService()
    limit = request.args.get("limit", 10)
    dept = request.args.get("department")
    results = service.get_topper_ranking(limit=limit, department=dept)
    return jsonify(serialize_doc(results)), 200


@analytics_bp.route("/api/analytics/departments", methods=["GET"])
def api_department_analytics():
    """GET /api/analytics/departments - Department performance via $group."""
    service = AnalyticsService()
    return jsonify(serialize_doc(service.get_department_performance())), 200


@analytics_bp.route("/api/analytics/course-statistics", methods=["GET"])
def api_course_statistics():
    """GET /api/analytics/course-statistics - Course performance with $lookup."""
    service = AnalyticsService()
    return jsonify(serialize_doc(service.get_course_statistics())), 200


@analytics_bp.route("/api/analytics/at-risk", methods=["GET"])
def api_at_risk_students():
    """GET /api/analytics/at-risk - Configurable threshold risk detection."""
    service = AnalyticsService()
    att_thresh = request.args.get("attendance_threshold", 75.0)
    marks_thresh = request.args.get("marks_threshold", 40.0)
    results = service.get_at_risk_students(
        attendance_threshold=float(att_thresh),
        marks_threshold=float(marks_thresh)
    )
    return jsonify(serialize_doc(results)), 200


@analytics_bp.route("/api/analytics/skills", methods=["GET"])
def api_skill_distribution():
    """GET /api/analytics/skills - Technical skill frequency via $unwind."""
    service = AnalyticsService()
    limit = request.args.get("limit", 15)
    return jsonify(serialize_doc(service.get_skill_distribution(limit=limit))), 200


@analytics_bp.route("/api/analytics/performance-categories", methods=["GET"])
def api_performance_categories():
    """GET /api/analytics/performance-categories - Academic tiers via $switch."""
    service = AnalyticsService()
    return jsonify(serialize_doc(service.get_performance_categories())), 200


@analytics_bp.route("/api/analytics/semester-analytics", methods=["GET"])
def api_semester_analytics():
    """GET /api/analytics/semester-analytics - Semester & department cross-grouping."""
    service = AnalyticsService()
    return jsonify(serialize_doc(service.get_semester_analytics())), 200


@analytics_bp.route("/api/analytics/ml-model-info", methods=["GET"])
def api_ml_model_info():
    """GET /api/analytics/ml-model-info - Scikit-learn model evaluation metrics."""
    predictor = AcademicRiskPredictor()
    if not predictor.is_trained:
        predictor.train_model()
    return jsonify(serialize_doc(predictor.metrics)), 200


@analytics_bp.route("/api/analytics/predict-risk/<student_id>", methods=["GET"])
def api_predict_student_risk(student_id):
    """GET /api/analytics/predict-risk/<student_id> - Rule-based + ML prediction."""
    student_service = StudentService()
    predictor = AcademicRiskPredictor()

    student = student_service.get_student_by_id(student_id)
    if not student:
        return jsonify({"error": f"Student with ID '{student_id}' not found."}), 404

    prediction = predictor.predict_for_student(student)
    return jsonify(serialize_doc(prediction)), 200
