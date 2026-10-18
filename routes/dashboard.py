"""
Dashboard Blueprint for overview page rendering.
"""

from flask import Blueprint, render_template
from services.analytics_service import AnalyticsService
from services.student_service import StudentService
from services.course_service import CourseService

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def index():
    """Render main overview dashboard with real MongoDB analytics metrics."""
    analytics_service = AnalyticsService()
    student_service = StudentService()
    course_service = CourseService()

    # Fetch aggregated KPIs
    kpis = analytics_service.get_overview_kpis()
    toppers = analytics_service.get_topper_ranking(limit=5)
    departments = analytics_service.get_department_performance()
    at_risk_list = analytics_service.get_at_risk_students()

    # Get recent students
    recent_students = student_service.get_students(page=1, page_size=5, sort_by="created_at", sort_order=-1)

    return render_template(
        "dashboard.html",
        kpis=kpis,
        toppers=toppers,
        departments=departments,
        at_risk_count=len(at_risk_list),
        at_risk_list=at_risk_list[:5],
        recent_students=recent_students["students"]
    )
