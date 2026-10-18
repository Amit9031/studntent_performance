"""
MongoDB Aggregation Framework Service.

Implements all required analytical aggregation pipelines executed directly in MongoDB:
1. Student Performance Summary (average, max, min, subject count)
2. Topper Ranking (ranked by average marks)
3. Department-wise Performance ($group for stats across departments)
4. At-Risk Students ($match for attendance < 75 OR marks < 40)
5. Course-wise Statistics ($objectToArray, $unwind, $group, and $lookup with courses)
6. Skill Distribution ($unwind and $group by skill)
7. Performance Categories ($project, $switch for grade tiers)
8. Semester-wise Analytics (group by semester and department)
9. System Overview KPI Metrics ($facet for multi-metric dashboard cards)
"""

import logging
from database.connection import get_database

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service providing data analytics computed entirely via MongoDB Aggregation Pipelines."""

    def __init__(self, db=None):
        self._db = db

    @property
    def db(self):
        return self._db if self._db is not None else get_database()

    @property
    def students_collection(self):
        return self.db["students"]

    # ==============================================================
    # PIPELINE 1: STUDENT PERFORMANCE SUMMARY
    # Calculates each student's average, max, min marks & subject count.
    # ==============================================================
    def get_student_performance_summary(self, student_id=None):
        """
        Calculates each student's average marks, highest mark, lowest mark,
        and number of enrolled subjects using $objectToArray, $avg, $max, $min, $size.
        """
        pipeline = []

        # Optional filter for single student
        if student_id is not None:
            try:
                pipeline.append({"$match": {"_id": int(student_id)}})
            except (ValueError, TypeError):
                pass

        pipeline.extend([
            {
                # Transform embedded 'marks' document into an array of key-value objects
                "$project": {
                    "_id": 1,
                    "name": 1,
                    "email": 1,
                    "department": 1,
                    "semester": 1,
                    "attendance": 1,
                    "marks_array": {"$objectToArray": "$marks"}
                }
            },
            {
                # Compute statistical aggregates across the marks array
                "$project": {
                    "_id": 1,
                    "name": 1,
                    "email": 1,
                    "department": 1,
                    "semester": 1,
                    "attendance": 1,
                    "total_subjects": {"$size": "$marks_array"},
                    "average_marks": {
                        "$cond": [
                            {"$gt": [{"$size": "$marks_array"}, 0]},
                            {"$round": [{"$avg": "$marks_array.v"}, 2]},
                            0.0
                        ]
                    },
                    "highest_mark": {
                        "$cond": [
                            {"$gt": [{"$size": "$marks_array"}, 0]},
                            {"$max": "$marks_array.v"},
                            0.0
                        ]
                    },
                    "lowest_mark": {
                        "$cond": [
                            {"$gt": [{"$size": "$marks_array"}, 0]},
                            {"$min": "$marks_array.v"},
                            0.0
                        ]
                    }
                }
            },
            {"$sort": {"average_marks": -1, "_id": 1}}
        ])

        return list(self.students_collection.aggregate(pipeline))

    # ==============================================================
    # PIPELINE 2: TOPPER RANKING
    # Ranks students in descending order of average marks.
    # ==============================================================
    def get_topper_ranking(self, limit=10, department=None):
        """
        Ranks top students by average marks in descending order.
        Includes student name, department, semester, and average mark.
        """
        pipeline = []

        if department and str(department).strip():
            pipeline.append({"$match": {"department": str(department).strip().upper()}})

        pipeline.extend([
            {
                "$project": {
                    "_id": 1,
                    "name": 1,
                    "department": 1,
                    "semester": 1,
                    "attendance": 1,
                    "marks_array": {"$objectToArray": "$marks"}
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "name": 1,
                    "department": 1,
                    "semester": 1,
                    "attendance": 1,
                    "average_marks": {
                        "$cond": [
                            {"$gt": [{"$size": "$marks_array"}, 0]},
                            {"$round": [{"$avg": "$marks_array.v"}, 2]},
                            0.0
                        ]
                    }
                }
            },
            {"$sort": {"average_marks": -1, "attendance": -1}},
            {"$limit": int(limit)}
        ])

        results = list(self.students_collection.aggregate(pipeline))
        # Add rank indicator
        for idx, item in enumerate(results, start=1):
            item["rank"] = idx
        return results

    # ==============================================================
    # PIPELINE 3: DEPARTMENT-WISE PERFORMANCE
    # Groups students by department to calculate comprehensive stats.
    # ==============================================================
    def get_department_performance(self):
        """
        Calculates:
        - Total students per department
        - Overall average marks
        - Highest average marks achieved by any student in the department
        - Average attendance
        """
        pipeline = [
            {
                "$project": {
                    "department": 1,
                    "attendance": 1,
                    "student_avg_mark": {
                        "$let": {
                            "vars": {"m_arr": {"$objectToArray": "$marks"}},
                            "in": {
                                "$cond": [
                                    {"$gt": [{"$size": "$$m_arr"}, 0]},
                                    {"$avg": "$$m_arr.v"},
                                    0.0
                                ]
                            }
                        }
                    }
                }
            },
            {
                "$group": {
                    "_id": "$department",
                    "total_students": {"$sum": 1},
                    "avg_marks": {"$avg": "$student_avg_mark"},
                    "highest_marks": {"$max": "$student_avg_mark"},
                    "avg_attendance": {"$avg": "$attendance"}
                }
            },
            {
                "$project": {
                    "department": "$_id",
                    "total_students": 1,
                    "avg_marks": {"$round": ["$avg_marks", 2]},
                    "highest_marks": {"$round": ["$highest_marks", 2]},
                    "avg_attendance": {"$round": ["$avg_attendance", 2]}
                }
            },
            {"$sort": {"avg_marks": -1}}
        ]

        return list(self.students_collection.aggregate(pipeline))

    # ==============================================================
    # PIPELINE 4: AT-RISK STUDENTS
    # Identifies students with attendance < 75% OR average marks < 40.
    # ==============================================================
    def get_at_risk_students(self, attendance_threshold=75.0, marks_threshold=40.0):
        """
        Identifies at-risk students using configurable thresholds:
        - Attendance < attendance_threshold (default: 75.0%) OR
        - Average Marks < marks_threshold (default: 40.0)
        """
        pipeline = [
            {
                "$project": {
                    "_id": 1,
                    "name": 1,
                    "email": 1,
                    "department": 1,
                    "semester": 1,
                    "attendance": 1,
                    "average_marks": {
                        "$let": {
                            "vars": {"m_arr": {"$objectToArray": "$marks"}},
                            "in": {
                                "$cond": [
                                    {"$gt": [{"$size": "$$m_arr"}, 0]},
                                    {"$round": [{"$avg": "$$m_arr.v"}, 2]},
                                    0.0
                                ]
                            }
                        }
                    }
                }
            },
            {
                "$match": {
                    "$or": [
                        {"attendance": {"$lt": float(attendance_threshold)}},
                        {"average_marks": {"$lt": float(marks_threshold)}}
                    ]
                }
            },
            {
                "$addFields": {
                    "low_attendance": {"$lt": ["$attendance", float(attendance_threshold)]},
                    "low_marks": {"$lt": ["$average_marks", float(marks_threshold)]},
                    "risk_reasons": {
                        "$concatArrays": [
                            {
                                "$cond": [
                                    {"$lt": ["$attendance", float(attendance_threshold)]},
                                    [f"Low Attendance (<{attendance_threshold}%)"],
                                    []
                                ]
                            },
                            {
                                "$cond": [
                                    {"$lt": ["$average_marks", float(marks_threshold)]},
                                    [f"Low Academic Marks (<{marks_threshold})"],
                                    []
                                ]
                            }
                        ]
                    }
                }
            },
            {"$sort": {"attendance": 1, "average_marks": 1}}
        ]

        return list(self.students_collection.aggregate(pipeline))

    # ==============================================================
    # PIPELINE 5: COURSE-WISE STATISTICS WITH $LOOKUP
    # Calculates statistics per course and joins course metadata.
    # ==============================================================
    def get_course_statistics(self):
        """
        Transforms embedded marks via $objectToArray, $unwinds them,
        groups by course code to compute avg, min, max, student count,
        and joins course details via $lookup.
        """
        pipeline = [
            {
                "$project": {
                    "_id": 1,
                    "marks_array": {"$objectToArray": "$marks"}
                }
            },
            {"$unwind": "$marks_array"},
            {
                "$group": {
                    "_id": "$marks_array.k",
                    "student_count": {"$sum": 1},
                    "avg_marks": {"$avg": "$marks_array.v"},
                    "min_marks": {"$min": "$marks_array.v"},
                    "max_marks": {"$max": "$marks_array.v"}
                }
            },
            {
                # Join with 'courses' collection
                "$lookup": {
                    "from": "courses",
                    "localField": "_id",
                    "foreignField": "_id",
                    "as": "course_info"
                }
            },
            {
                "$unwind": {
                    "path": "$course_info",
                    "preserveNullAndEmptyArrays": True
                }
            },
            {
                "$project": {
                    "course_id": "$_id",
                    "course_name": {"$ifNull": ["$course_info.course_name", "$_id"]},
                    "department": {"$ifNull": ["$course_info.department", "N/A"]},
                    "credits": {"$ifNull": ["$course_info.credits", 0]},
                    "student_count": 1,
                    "avg_marks": {"$round": ["$avg_marks", 2]},
                    "min_marks": {"$round": ["$min_marks", 2]},
                    "max_marks": {"$round": ["$max_marks", 2]}
                }
            },
            {"$sort": {"course_id": 1}}
        ]

        return list(self.students_collection.aggregate(pipeline))

    # ==============================================================
    # PIPELINE 6: SKILL DISTRIBUTION
    # Unwinds skills array and groups to find most common skills.
    # ==============================================================
    def get_skill_distribution(self, limit=15):
        """
        Computes frequency distribution of student technical skills using $unwind and $group.
        """
        pipeline = [
            {"$unwind": "$skills"},
            {
                "$group": {
                    "_id": "$skills",
                    "student_count": {"$sum": 1}
                }
            },
            {
                "$project": {
                    "skill": "$_id",
                    "student_count": 1
                }
            },
            {"$sort": {"student_count": -1, "skill": 1}},
            {"$limit": int(limit)}
        ]

        return list(self.students_collection.aggregate(pipeline))

    # ==============================================================
    # PIPELINE 7: PERFORMANCE CATEGORIES
    # Classifies students into categories using $switch and groups counts.
    # ==============================================================
    def get_performance_categories(self):
        """
        Classifies students into academic categories based on average marks:
        - Excellent: >= 90
        - Good: 75 to < 90
        - Average: 60 to < 75
        - Needs Improvement: < 60
        Uses $project with $switch and $group.
        """
        pipeline = [
            {
                "$project": {
                    "_id": 1,
                    "name": 1,
                    "department": 1,
                    "avg_marks": {
                        "$let": {
                            "vars": {"m_arr": {"$objectToArray": "$marks"}},
                            "in": {
                                "$cond": [
                                    {"$gt": [{"$size": "$$m_arr"}, 0]},
                                    {"$round": [{"$avg": "$$m_arr.v"}, 2]},
                                    0.0
                                ]
                            }
                        }
                    }
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "name": 1,
                    "department": 1,
                    "avg_marks": 1,
                    "category": {
                        "$switch": {
                            "branches": [
                                {"case": {"$gte": ["$avg_marks", 90.0]}, "then": "Excellent (>=90%)"},
                                {"case": {"$gte": ["$avg_marks", 75.0]}, "then": "Good (75-89%)"},
                                {"case": {"$gte": ["$avg_marks", 60.0]}, "then": "Average (60-74%)"}
                            ],
                            "default": "Needs Improvement (<60%)"
                        }
                    }
                }
            },
            {
                "$group": {
                    "_id": "$category",
                    "student_count": {"$sum": 1},
                    "students": {
                        "$push": {
                            "id": "$_id",
                            "name": "$name",
                            "department": "$department",
                            "avg_marks": "$avg_marks"
                        }
                    }
                }
            },
            {
                "$project": {
                    "category": "$_id",
                    "student_count": 1,
                    "students": 1
                }
            },
            {"$sort": {"student_count": -1}}
        ]

        return list(self.students_collection.aggregate(pipeline))

    # ==============================================================
    # PIPELINE 8: SEMESTER-WISE ANALYTICS
    # Groups students by semester and department for multi-dimensional metrics.
    # ==============================================================
    def get_semester_analytics(self):
        """
        Groups students by composite key {semester, department}.
        Computes student counts, average marks, and average attendance.
        """
        pipeline = [
            {
                "$project": {
                    "semester": 1,
                    "department": 1,
                    "attendance": 1,
                    "avg_marks": {
                        "$let": {
                            "vars": {"m_arr": {"$objectToArray": "$marks"}},
                            "in": {
                                "$cond": [
                                    {"$gt": [{"$size": "$$m_arr"}, 0]},
                                    {"$avg": "$$m_arr.v"},
                                    0.0
                                ]
                            }
                        }
                    }
                }
            },
            {
                "$group": {
                    "_id": {
                        "semester": "$semester",
                        "department": "$department"
                    },
                    "student_count": {"$sum": 1},
                    "avg_marks": {"$avg": "$avg_marks"},
                    "avg_attendance": {"$avg": "$attendance"}
                }
            },
            {
                "$project": {
                    "semester": "$_id.semester",
                    "department": "$_id.department",
                    "student_count": 1,
                    "avg_marks": {"$round": ["$avg_marks", 2]},
                    "avg_attendance": {"$round": ["$avg_attendance", 2]}
                }
            },
            {"$sort": {"semester": 1, "department": 1}}
        ]

        return list(self.students_collection.aggregate(pipeline))

    # ==============================================================
    # PIPELINE 9: SYSTEM OVERVIEW (FACET PIPELINE)
    # Computes overall dashboard KPIs in a single query execution.
    # ==============================================================
    def get_overview_kpis(self):
        """
        Uses $facet to compute total students, overall average marks,
        overall average attendance, and at-risk count in a single pass.
        """
        pipeline = [
            {
                "$project": {
                    "_id": 1,
                    "attendance": 1,
                    "avg_marks": {
                        "$let": {
                            "vars": {"m_arr": {"$objectToArray": "$marks"}},
                            "in": {
                                "$cond": [
                                    {"$gt": [{"$size": "$$m_arr"}, 0]},
                                    {"$avg": "$$m_arr.v"},
                                    0.0
                                ]
                            }
                        }
                    }
                }
            },
            {
                "$facet": {
                    "overall_stats": [
                        {
                            "$group": {
                                "_id": None,
                                "total_students": {"$sum": 1},
                                "overall_avg_marks": {"$avg": "$avg_marks"},
                                "overall_avg_attendance": {"$avg": "$attendance"}
                            }
                        }
                    ],
                    "at_risk_stats": [
                        {
                            "$match": {
                                "$or": [
                                    {"attendance": {"$lt": 75.0}},
                                    {"avg_marks": {"$lt": 40.0}}
                                ]
                            }
                        },
                        {"$count": "count"}
                    ]
                }
            }
        ]

        facet_result = list(self.students_collection.aggregate(pipeline))
        total_courses = self.db["courses"].count_documents({})

        if not facet_result or not facet_result[0]["overall_stats"]:
            return {
                "total_students": 0,
                "total_courses": total_courses,
                "overall_avg_marks": 0.0,
                "overall_avg_attendance": 0.0,
                "at_risk_count": 0
            }

        stats = facet_result[0]["overall_stats"][0]
        at_risk_count = facet_result[0]["at_risk_stats"][0]["count"] if facet_result[0]["at_risk_stats"] else 0

        return {
            "total_students": stats.get("total_students", 0),
            "total_courses": total_courses,
            "overall_avg_marks": round(stats.get("overall_avg_marks", 0.0), 2),
            "overall_avg_attendance": round(stats.get("overall_avg_attendance", 0.0), 2),
            "at_risk_count": at_risk_count
        }
