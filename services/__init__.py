"""
Services package initialization.
Exports StudentService, CourseService, AnalyticsService, and AcademicRiskPredictor.
"""

from services.student_service import StudentService
from services.course_service import CourseService
from services.analytics_service import AnalyticsService
from services.prediction_service import AcademicRiskPredictor

__all__ = [
    "StudentService",
    "CourseService",
    "AnalyticsService",
    "AcademicRiskPredictor"
]
