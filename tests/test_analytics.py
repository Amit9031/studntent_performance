"""
Integration tests for all MongoDB Aggregation Framework pipelines.
Verifies calculations are performed directly by MongoDB without Python loops.
"""

import pytest


def test_pipeline_1_student_performance_summary(analytics_service):
    """
    Test Pipeline 1: Student Performance Summary.
    Verifies that MongoDB calculates average, highest, lowest marks, and subject count.
    """
    results = analytics_service.get_student_performance_summary()
    assert len(results) > 0

    first = results[0]
    assert "average_marks" in first
    assert "highest_mark" in first
    assert "lowest_mark" in first
    assert "total_subjects" in first
    # Check that highest mark is >= lowest mark
    assert first["highest_mark"] >= first["lowest_mark"]
    # Check that average is within [lowest, highest]
    assert first["lowest_mark"] <= first["average_marks"] <= first["highest_mark"]


def test_pipeline_2_topper_ranking(analytics_service):
    """
    Test Pipeline 2: Topper Ranking.
    Verifies that students are strictly ordered by average marks descending.
    """
    toppers = analytics_service.get_topper_ranking(limit=10)
    assert len(toppers) > 0
    assert len(toppers) <= 10

    # Verify descending sort order
    for i in range(len(toppers) - 1):
        assert toppers[i]["average_marks"] >= toppers[i + 1]["average_marks"]


def test_pipeline_3_department_performance(analytics_service):
    """
    Test Pipeline 3: Department-wise Performance.
    Verifies $group aggregation produces counts and averages for all departments.
    """
    depts = analytics_service.get_department_performance()
    assert len(depts) > 0

    dept_names = [d["department"] for d in depts]
    assert "CSE" in dept_names

    for d in depts:
        assert d["total_students"] > 0
        assert 0 <= d["avg_marks"] <= 100
        assert 0 <= d["avg_attendance"] <= 100


def test_pipeline_4_at_risk_students(analytics_service):
    """
    Test Pipeline 4: At-Risk Students.
    Verifies detection of students with attendance < 75% or average marks < 40.
    """
    at_risk = analytics_service.get_at_risk_students(attendance_threshold=75.0, marks_threshold=40.0)
    assert len(at_risk) > 0

    for student in at_risk:
        # At least one condition must be true
        assert student["attendance"] < 75.0 or student["average_marks"] < 40.0
        assert len(student["risk_reasons"]) > 0


def test_pipeline_5_course_statistics_lookup(analytics_service):
    """
    Test Pipeline 5: Course-wise Statistics with $lookup.
    Verifies $unwind, $group, and $lookup join with the courses collection.
    """
    stats = analytics_service.get_course_statistics()
    assert len(stats) > 0

    course_codes = [c["course_id"] for c in stats]
    assert "CSE494" in course_codes

    for c in stats:
        assert "course_name" in c
        assert "avg_marks" in c
        assert "min_marks" in c
        assert "max_marks" in c
        assert c["student_count"] > 0
        assert c["min_marks"] <= c["avg_marks"] <= c["max_marks"]


def test_pipeline_6_skill_distribution(analytics_service):
    """
    Test Pipeline 6: Skill Distribution.
    Verifies $unwind on skills array and $group counts.
    """
    skills = analytics_service.get_skill_distribution(limit=10)
    assert len(skills) > 0

    skill_names = [s["skill"] for s in skills]
    assert "Python" in skill_names

    for s in skills:
        assert s["student_count"] >= 1


def test_pipeline_7_performance_categories_switch(analytics_service):
    """
    Test Pipeline 7: Performance Categories.
    Verifies $project with $switch assigns students to appropriate academic tiers.
    """
    categories = analytics_service.get_performance_categories()
    assert len(categories) > 0

    cat_labels = [c["category"] for c in categories]
    # Check that categories exist
    valid_tiers = ["Excellent (>=90%)", "Good (75-89%)", "Average (60-74%)", "Needs Improvement (<60%)"]
    for cl in cat_labels:
        assert cl in valid_tiers


def test_pipeline_8_semester_analytics(analytics_service):
    """
    Test Pipeline 8: Semester-wise Analytics.
    Verifies grouping by composite key {semester, department}.
    """
    semester_stats = analytics_service.get_semester_analytics()
    assert len(semester_stats) > 0

    for item in semester_stats:
        assert 1 <= item["semester"] <= 12
        assert item["student_count"] > 0
        assert 0 <= item["avg_marks"] <= 100


def test_pipeline_9_overview_kpis_facet(analytics_service):
    """
    Test Pipeline 9: Overview KPIs with $facet.
    Verifies single-query aggregation of multi-dimensional summary cards.
    """
    kpis = analytics_service.get_overview_kpis()
    assert kpis["total_students"] > 0
    assert kpis["total_courses"] > 0
    assert 0 <= kpis["overall_avg_marks"] <= 100
    assert 0 <= kpis["overall_avg_attendance"] <= 100
    assert kpis["at_risk_count"] >= 0
