# MongoDB Aggregation Framework Documentation

## Course: CSE494 Intelligent NoSQL Databases
**System:** Student Performance Analytics System  
**Driver:** PyMongo 4.8  

The MongoDB Aggregation Framework processes data through a multi-stage pipeline where the output of each stage acts as the input to the next. In this system, all analytical calculations are executed directly inside the MongoDB engine, ensuring zero reliance on client-side Python loops.

---

### Pipeline 1: Student Performance Summary
**Purpose:** Calculates statistical summaries (average mark, highest score, lowest score, and total enrolled subjects) for each student. Handles the embedded `marks` document dynamically.

#### MongoDB Aggregation Pipeline:
```python
pipeline = [
    {
        # Stage 1: Convert embedded document 'marks' into key-value array
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
        # Stage 2: Compute statistical expressions on the values
        "$project": {
            "_id": 1,
            "name": 1,
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
    # Stage 3: Sort by average score descending
    {"$sort": {"average_marks": -1, "_id": 1}}
]
```

#### Expected Sample Output:
```json
{
  "_id": 101,
  "name": "Amit Ranjan",
  "department": "CSE",
  "semester": 7,
  "attendance": 94.5,
  "total_subjects": 4,
  "average_marks": 93.25,
  "highest_mark": 96.0,
  "lowest_mark": 90.0
}
```

---

### Pipeline 2: Topper Ranking Leaderboard
**Purpose:** Ranks students based on computed average marks in descending order. Demonstrates `$limit` for leaderboard extraction.

#### MongoDB Aggregation Pipeline:
```python
pipeline = [
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
    {"$limit": 10}
]
```

#### Expected Sample Output:
```json
[
  {
    "_id": 102,
    "name": "Priya Sharma",
    "department": "CSE",
    "semester": 7,
    "attendance": 98.0,
    "average_marks": 94.75,
    "rank": 1
  },
  {
    "_id": 104,
    "name": "Ananya Gupta",
    "department": "AIDS",
    "semester": 5,
    "attendance": 96.0,
    "average_marks": 93.67,
    "rank": 2
  }
]
```

---

### Pipeline 3: Department-wise Performance
**Purpose:** Uses `$group` to aggregate department cohorts, calculating total students, cohort average marks, department highest marks, and average attendance.

#### MongoDB Aggregation Pipeline:
```python
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
```

#### Expected Sample Output:
```json
{
  "department": "CSE",
  "total_students": 12,
  "avg_marks": 78.42,
  "highest_marks": 94.75,
  "avg_attendance": 84.17
}
```

---

### Pipeline 4: At-Risk Students Detection
**Purpose:** Identifies students requiring academic interventions based on configurable threshold rules: attendance `< 75%` OR average marks `< 40`. Uses `$match` with `$or` and `$addFields` with `$concatArrays`.

#### MongoDB Aggregation Pipeline:
```python
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
        # Stage 2: Filter at-risk conditions
        "$match": {
            "$or": [
                {"attendance": {"$lt": 75.0}},
                {"average_marks": {"$lt": 40.0}}
            ]
        }
    },
    {
        # Stage 3: Dynamically generate specific risk reason descriptions
        "$addFields": {
            "risk_reasons": {
                "$concatArrays": [
                    {
                        "$cond": [
                            {"$lt": ["$attendance", 75.0]},
                            ["Low Attendance (<75%)"],
                            []
                        ]
                    },
                    {
                        "$cond": [
                            {"$lt": ["$average_marks", 40.0]},
                            ["Low Academic Marks (<40)"],
                            []
                        ]
                    }
                ]
            }
        }
    },
    {"$sort": {"attendance": 1, "average_marks": 1}}
]
```

#### Expected Sample Output:
```json
{
  "_id": 127,
  "name": "Sunil Varma",
  "department": "IT",
  "semester": 5,
  "attendance": 48.5,
  "average_marks": 40.0,
  "risk_reasons": [
    "Low Attendance (<75%)"
  ]
}
```

---

### Pipeline 5: Course-wise Statistics with `$lookup`
**Purpose:** Normalizes embedded student marks across all courses using `$objectToArray` and `$unwind`, groups by course code to compute statistics, and performs a `$lookup` join with the `courses` collection.

#### MongoDB Aggregation Pipeline:
```python
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
        # Left outer join with 'courses' collection
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
```

#### Expected Sample Output:
```json
{
  "course_id": "CSE494",
  "course_name": "Intelligent NoSQL Databases",
  "department": "CSE",
  "credits": 4,
  "student_count": 8,
  "avg_marks": 83.38,
  "min_marks": 55.0,
  "max_marks": 98.0
}
```

---

### Pipeline 6: Skill Distribution
**Purpose:** Deconstructs the BSON `skills` array using `$unwind` and groups by skill name to determine technical competencies across the student body.

#### MongoDB Aggregation Pipeline:
```python
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
    {"$limit": 15}
]
```

#### Expected Sample Output:
```json
[
  { "skill": "Python", "student_count": 16 },
  { "skill": "MongoDB", "student_count": 8 },
  { "skill": "Machine Learning", "student_count": 5 },
  { "skill": "SQL", "student_count": 4 }
]
```

---

### Pipeline 7: Performance Categories via `$switch`
**Purpose:** Evaluates conditional grading branches using `$switch` and groups students into performance brackets.

#### MongoDB Aggregation Pipeline:
```python
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
            "student_count": {"$sum": 1}
        }
    },
    {
        "$project": {
            "category": "$_id",
            "student_count": 1
        }
    },
    {"$sort": {"student_count": -1}}
]
```

#### Expected Sample Output:
```json
[
  { "category": "Good (75-89%)", "student_count": 13 },
  { "category": "Average (60-74%)", "student_count": 11 },
  { "category": "Needs Improvement (<60%)", "student_count": 6 },
  { "category": "Excellent (>=90%)", "student_count": 5 }
]
```

---

### Pipeline 8: Semester-wise Analytics
**Purpose:** Groups students by composite key `{semester, department}` to evaluate progress across academic cohorts.

#### MongoDB Aggregation Pipeline:
```python
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
```

---

### Pipeline 9: System Overview KPI Multi-Faceting (`$facet`)
**Purpose:** Executes multiple independent sub-pipelines simultaneously in a single round-trip query to populate executive dashboard metric cards.

#### MongoDB Aggregation Pipeline:
```python
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
```
