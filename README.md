# Student Performance Analytics System Using MongoDB and PyMongo

[![Python Version](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![MongoDB Version](https://img.shields.io/badge/MongoDB-8.0_Community-green.svg)](https://www.mongodb.com/)
[![PyMongo Version](https://img.shields.io/badge/PyMongo-4.8.0-brightgreen.svg)](https://pymongo.readthedocs.io/)
[![Flask Version](https://img.shields.io/badge/Flask-3.0.3-orange.svg)](https://flask.palletsprojects.com/)
[![Tests Passed](https://img.shields.io/badge/Pytest-36%20Passed-success.svg)](https://docs.pytest.org/)
[![Course](https://img.shields.io/badge/Course-CSE494%3A%20Intelligent%20NoSQL%20Databases-purple.svg)]()

> A full-stack, enterprise-grade academic analytics system developed for **CSE494: Intelligent NoSQL Databases** course project. Built directly with **Python 3.12**, **MongoDB Community Edition 8.0**, **PyMongo**, **Flask**, and **Scikit-Learn** without Object-Document Mappers (ODMs).

---

## 📌 Table of Contents
1. [Project Overview & Features](#-project-overview--features)
2. [Course Outcome (CO) Mapping](#-course-outcome-co-mapping)
3. [System Architecture & Technology Stack](#-system-architecture--technology-stack)
4. [Prerequisites & Environment Setup](#-prerequisites--environment-setup)
5. [Step-by-Step Installation & Running Guide](#-step-by-step-installation--running-guide)
6. [Database Initialization & Sample Seeding](#-database-initialization--sample-seeding)
7. [Running Index Optimization Benchmarks](#-running-index-optimization-benchmarks)
8. [Running Automated Tests](#-running-automated-tests)
9. [MongoDB Aggregation Framework Highlights](#-mongodb-aggregation-framework-highlights)
10. [REST API Endpoint Reference](#-rest-api-endpoint-reference)
11. [Troubleshooting & FAQs](#-troubleshooting--faqs)

---

## 🚀 Project Overview & Features

- **Document-Oriented Data Modeling:** Demonstrates both **document embedding** (coursework marks embedded inside student records for instant atomic retrieval) and **collection referencing** (`courses` collection referenced via `$lookup`).
- **Database-Level JSON Schema Validation:** Enforces data integrity using MongoDB's `$jsonSchema` engine at the database layer (attendance $[0, 100]$, marks $[0, 100]$, positive numeric IDs, regex email patterns).
- **Comprehensive CRUD Operations:** Complete create, read, update, and delete functionality implemented using native PyMongo methods (`insert_one`, `insert_many`, `find`, `find_one`, `update_one`, `update_many`, `delete_one`, `delete_many`, `count_documents`, `distinct`).
- **9 Native MongoDB Aggregation Pipelines:** Multi-stage pipelines executed directly on the MongoDB server using `$objectToArray`, `$project`, `$group`, `$sort`, `$limit`, `$unwind`, `$lookup`, `$facet`, `$switch`, and `$addFields`. Zero reliance on client-side Python loops for calculations.
- **Query Optimization & Explain Benchmarking:** Implements single-field, compound, unique, and text indexes. Includes a 10,000-record benchmark comparing `COLLSCAN` vs `IXSCAN` using `explain("executionStats")`.
- **Intelligent Risk Prediction Engine:** Dual-tier evaluation:
  1. *Transparent rule-based heuristics* detecting attendance shortage ($< 75\%$) or academic failure ($< 40\%$).
  2. *Supervised machine learning model* (`RandomForestClassifier` from Scikit-Learn) with reproducible train/test split.
- **Modern Responsive Web Dashboard:** Built with Flask, Bootstrap 5, and Chart.js 4 for interactive visual charts and student management.
- **Complete REST API:** Clean JSON endpoints for programmatic integration.

---

## 🎯 Course Outcome (CO) Mapping

| Outcome Code | Description | Demonstrated Feature in Project |
| :--- | :--- | :--- |
| **CO1** | Discuss NoSQL concepts and differentiate NoSQL from RDBMS | Detailed documentation in `docs/PROJECT_REPORT.md` and 45 viva Q&As in `docs/VIVA_QUESTIONS.md` covering CAP theorem, BSON vs. JSON, and horizontal scaling. |
| **CO2** | Apply CRUD operations, indexing, and query optimization | Complete CRUD in `StudentService` and `CourseService`. Single, compound, unique, and text indexes in `database/indexes.py`. |
| **CO3** | Analyze data modeling strategies (embedding vs. referencing) | Embedded marks (`marks` document) vs. referenced `courses` collection with `$lookup` and enrolled deletion safety rules. |
| **CO4** | Evaluate performance impact of indexes and aggregation pipelines | Standalone benchmark (`scripts/benchmark_queries.py`) examining 10,000 documents with `explain("executionStats")` and 9 native aggregation pipelines. |
| **CO5** | Develop applications integrating MongoDB with Python and PyMongo | Reusable thread-safe `MongoClient` connection pool in `database/connection.py`, Flask blueprints, safe BSON serialization, and 36 automated pytest tests. |
| **CO6** | Create a functional mini-project with intelligent analytics | Full interactive web dashboard and dual-tier academic risk analytics (rule-based + Scikit-Learn ML). |

---

## 🛠 System Architecture & Technology Stack

```
student-performance-analytics/
├── app.py                     # Flask Application Factory & Server Entrypoint
├── config.py                  # Environment-specific configuration manager
├── requirements.txt           # Project dependencies
├── .env.example               # Configuration template
├── .env                       # Local active environment variables
├── .gitignore                 # Git ignore rules
├── README.md                  # Comprehensive project documentation
│
├── database/                  # Database Layer
│   ├── connection.py          # Thread-safe MongoClient connection manager & ping
│   ├── validators.py          # MongoDB $jsonSchema definitions & Python validators
│   ├── indexes.py             # Single, compound, unique, and text index creators
│   └── seed.py                # Deterministic realistic sample data generator
│
├── services/                  # Business Logic & Data Access Layer
│   ├── student_service.py     # Student CRUD, pagination, filtering, array operators
│   ├── course_service.py      # Course CRUD and cross-collection reference integrity
│   ├── analytics_service.py   # 9 Native MongoDB Aggregation Pipelines
│   └── prediction_service.py  # Rule-based evaluation & Scikit-Learn ML risk model
│
├── routes/                    # Presentation / Controller Layer (Flask Blueprints)
│   ├── dashboard.py           # Overview page views
│   ├── students.py            # Student catalog views & /api/students REST routes
│   ├── courses.py             # Course catalog views & /api/courses REST routes
│   └── analytics.py           # Analytics dashboard views & /api/analytics REST routes
│
├── templates/                 # Jinja2 HTML Templates
│   ├── base.html              # Core layout, sidebar, header, flash alerts
│   ├── dashboard.html         # Executive overview with metric cards and previews
│   ├── students.html          # Student directory, advanced search & filter bar
│   ├── student_form.html      # Create / Edit student with dynamic marks
│   ├── student_details.html   # Student profile, transcript, AI risk prediction
│   ├── courses.html           # Course catalog with add/edit/delete modals
│   └── analytics.html         # Chart.js visualizations, topper tables, ML stats
│
├── static/                    # Frontend Assets
│   ├── css/style.css          # Modern academic UI design & responsiveness
│   └── js/
│       ├── dashboard.js       # Tooltips and quick interaction helpers
│       └── analytics.js       # Chart.js rendering using MongoDB aggregation feeds
│
├── tests/                     # Automated Test Suite (Pytest)
│   ├── conftest.py            # Test database fixture (student_analytics_test)
│   ├── test_validation.py     # Schema validation and bounds testing
│   ├── test_students.py       # Student CRUD and update operator tests
│   ├── test_courses.py        # Course CRUD and referential integrity tests
│   ├── test_analytics.py      # Aggregation pipeline calculation tests
│   └── test_api.py            # Flask REST API endpoint tests
│
├── scripts/                   # Standalone CLI Utilities
│   ├── create_indexes.py      # Standalone index builder and reporter
│   ├── benchmark_queries.py   # 10,000-doc COLLSCAN vs IXSCAN benchmark
│   └── reset_demo_data.py     # Safe database reset to deterministic demo data
│
└── docs/                      # Coursework Academic Documentation
    ├── PROJECT_REPORT.md      # Full 22-section academic project report
    ├── DATABASE_DESIGN.md     # BSON vs JSON, data modeling, schemas, indexes
    ├── AGGREGATION_EXAMPLES.md# All 9 pipelines with code, stages, sample outputs
    ├── VIVA_QUESTIONS.md      # 45 Viva questions and answers for practical exam
    └── API_DOCUMENTATION.md   # Complete REST API reference with curl examples
```

---

## 💻 Prerequisites & Environment Setup

### 1. MongoDB Installation (macOS via Homebrew)
If MongoDB Community Edition is not yet installed or started:
```bash
# Install MongoDB Community Edition 8.0
brew tap mongodb/brew
brew install mongodb-community@8.0

# Start MongoDB background service
brew services start mongodb-community@8.0

# Verify MongoDB is running
mongosh --eval "db.adminCommand('ping')"
```

---

## ⚡ Step-by-Step Installation & Running Guide

### Step 1: Navigate to Project Directory
```bash
cd /Users/amitranjan/.gemini/antigravity/scratch/student-performance-analytics
```

### Step 2: Create and Activate Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy the template to `.env` (already pre-configured for local testing):
```bash
cp .env.example .env
```
Default `.env` settings:
```ini
MONGODB_URI=mongodb://localhost:27017/
DATABASE_NAME=student_analytics
TEST_DATABASE_NAME=student_analytics_test
PORT=5001
HOST=127.0.0.1
FLASK_DEBUG=1
```

---

## 🗄 Database Initialization & Sample Seeding

To create collections, register `$jsonSchema` validators, build all B-Tree indexes, and insert 35 realistic student records across 7 engineering courses:
```bash
python scripts/reset_demo_data.py
```

To create/rebuild indexes at any time:
```bash
python scripts/create_indexes.py
```

---

## 📊 Running Index Optimization Benchmarks

To execute the 10,000-document empirical benchmark comparing `COLLSCAN` vs `IXSCAN` using `explain("executionStats")`:
```bash
python scripts/benchmark_queries.py
```

### Actual Benchmark Output:
```
================================================================================
BENCHMARK COMPARISON SUMMARY (10,000 Documents)
================================================================================
╒═══════════════════════╤════════════════════╤═══════════════════╤═════════════════╤═════════════════╤═════════════════╤═════════════╕
│ Query Scenario        │ Index State        │ Execution Stage   │   Docs Examined │   Keys Examined │   Docs Returned │ Exec Time   │
╞═══════════════════════╪════════════════════╪═══════════════════╪═════════════════╪═════════════════╪═════════════════╪═════════════╡
│ Q1: Dept + Attendance │ Unindexed          │ SORT -> COLLSCAN  │           10000 │               0 │             474 │ 4 ms        │
├───────────────────────┼────────────────────┼───────────────────┼─────────────────┼─────────────────┼─────────────────┼─────────────┤
│ Q1: Dept + Attendance │ Indexed (Compound) │ FETCH -> IXSCAN   │             474 │             474 │             474 │ 2 ms        │
├───────────────────────┼────────────────────┼───────────────────┼─────────────────┼─────────────────┼─────────────────┼─────────────┤
│ Q2: Email Lookup      │ Unindexed          │ COLLSCAN          │           10000 │               0 │               1 │ 1 ms        │
├───────────────────────┼────────────────────┼───────────────────┼─────────────────┼─────────────────┼─────────────────┼─────────────┤
│ Q2: Email Lookup      │ Indexed (Unique)   │ EXPRESS_IXSCAN    │               1 │               1 │               1 │ 1 ms        │
╘═══════════════════════╧════════════════════╧═══════════════════╧═════════════════╧═════════════════╧═════════════════╧═════════════╛
```

---

## 🧪 Running Automated Tests

Run the full pytest suite (36 tests) against the isolated `student_analytics_test` database:
```bash
pytest tests/ -v
```

### Actual Test Results:
```
tests/test_analytics.py::test_pipeline_1_student_performance_summary PASSED
tests/test_analytics.py::test_pipeline_2_topper_ranking PASSED
tests/test_analytics.py::test_pipeline_3_department_performance PASSED
tests/test_analytics.py::test_pipeline_4_at_risk_students PASSED
tests/test_analytics.py::test_pipeline_5_course_statistics_lookup PASSED
tests/test_analytics.py::test_pipeline_6_skill_distribution PASSED
tests/test_analytics.py::test_pipeline_7_performance_categories_switch PASSED
tests/test_analytics.py::test_pipeline_8_semester_analytics PASSED
tests/test_analytics.py::test_pipeline_9_overview_kpis_facet PASSED
tests/test_api.py::test_api_get_students PASSED
tests/test_api.py::test_api_get_student_by_id PASSED
tests/test_api.py::test_api_create_student_lifecycle PASSED
tests/test_api.py::test_api_invalid_content_type PASSED
tests/test_api.py::test_api_courses_endpoints PASSED
tests/test_api.py::test_api_analytics_endpoints PASSED
tests/test_api.py::test_api_predict_risk_endpoint PASSED
tests/test_courses.py::test_create_and_get_course PASSED
tests/test_courses.py::test_duplicate_course_prevention PASSED
tests/test_courses.py::test_update_course PASSED
tests/test_courses.py::test_delete_course_with_enrolled_students PASSED
tests/test_students.py::test_create_and_get_student PASSED
tests/test_students.py::test_duplicate_student_id_prevention PASSED
tests/test_students.py::test_duplicate_email_prevention PASSED
tests/test_students.py::test_update_student_details PASSED
tests/test_students.py::test_add_or_update_course_mark PASSED
tests/test_students.py::test_add_skills_array_addToSet PASSED
tests/test_students.py::test_delete_student PASSED
tests/test_students.py::test_pagination_and_filters PASSED
tests/test_validation.py::test_valid_student_payload PASSED
tests/test_validation.py::test_invalid_student_id PASSED
tests/test_validation.py::test_invalid_email_format PASSED
tests/test_validation.py::test_invalid_attendance_range PASSED
tests/test_validation.py::test_invalid_marks_range PASSED
tests/test_validation.py::test_invalid_department PASSED
tests/test_validation.py::test_valid_course_payload PASSED
tests/test_validation.py::test_invalid_course_payload PASSED

============================== 36 passed in 0.42s ==============================
```

---

## 🌐 Starting the Web Application

Launch the Flask development server:
```bash
python app.py
```
Open your web browser and navigate to:
```
http://127.0.0.1:5001
```

---

## 📈 MongoDB Aggregation Framework Highlights

1. **Pipeline 1 (Student Performance Summary):** Extracts dynamic course marks using `$objectToArray` and calculates each student's average, highest, lowest marks, and subject count.
2. **Pipeline 2 (Topper Leaderboard):** Ranks students by average marks in descending order with `$limit`.
3. **Pipeline 3 (Department Performance):** Uses `$group` by department to calculate student counts, average scores, and average attendance.
4. **Pipeline 4 (At-Risk Detection):** Identifies students with attendance $< 75\%$ or marks $< 40$, dynamically constructing intervention reasons using `$concatArrays`.
5. **Pipeline 5 (Course-wise Statistics with `$lookup`):** `$unwind`s embedded marks and performs an index-backed left outer join with the `courses` collection.
6. **Pipeline 6 (Skill Distribution):** Deconstructs the `skills` array via `$unwind` and groups to compute frequency of competencies.
7. **Pipeline 7 (Performance Categories):** Classifies students into grade tiers ("Excellent", "Good", "Average", "Needs Improvement") using `$project` and `$switch`.
8. **Pipeline 8 (Semester-wise Analytics):** Groups by composite key `{semester, department}`.
9. **Pipeline 9 (System Overview KPIs):** Evaluates multi-metric dashboard statistics simultaneously using `$facet`.

---

## 🔌 REST API Endpoint Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/students` | Get paginated students with search and filters |
| `GET` | `/api/students/<id>` | Get single student details |
| `POST` | `/api/students` | Register new student document |
| `PUT` | `/api/students/<id>` | Update student details and embedded marks |
| `DELETE` | `/api/students/<id>` | Delete student document |
| `GET` | `/api/courses` | Get course catalog |
| `GET` | `/api/courses/<id>` | Get single course details |
| `POST` | `/api/courses` | Add new course to catalog |
| `PUT` | `/api/courses/<id>` | Modify course details |
| `DELETE` | `/api/courses/<id>` | Delete course (prevents deletion if students enrolled) |
| `GET` | `/api/analytics/overview` | Overall dashboard KPIs via `$facet` |
| `GET` | `/api/analytics/topper-ranking` | Top performing students ranked by marks |
| `GET` | `/api/analytics/departments` | Department-wise summary statistics via `$group` |
| `GET` | `/api/analytics/course-statistics` | Course score statistics with `$lookup` join |
| `GET` | `/api/analytics/at-risk` | Filter at-risk students by configurable thresholds |
| `GET` | `/api/analytics/skills` | Technical skill distribution via `$unwind` |
| `GET` | `/api/analytics/performance-categories`| Grade tiers via `$switch` |
| `GET` | `/api/analytics/semester-analytics`| Semester cohort distribution |
| `GET` | `/api/analytics/ml-model-info` | Scikit-Learn model evaluation metrics |
| `GET` | `/api/analytics/predict-risk/<id>` | Risk assessment for specific student |

---

## 📚 Coursework Documentation Files

The `docs/` folder contains extensive documentation for examination review:
- **`docs/PROJECT_REPORT.md`**: Complete 22-section academic project report with Course Outcome (CO1–CO6) mapping.
- **`docs/DATABASE_DESIGN.md`**: Deep dive into BSON vs. JSON, embedding vs. referencing, schemas, and indexes.
- **`docs/AGGREGATION_EXAMPLES.md`**: Complete code and output examples for all 9 aggregation pipelines.
- **`docs/VIVA_QUESTIONS.md`**: 45 questions and answers for viva voce preparation.
- **`docs/API_DOCUMENTATION.md`**: REST API documentation with curl commands and request/response samples.

---

## 🛠 Troubleshooting & FAQs

#### Q: How do I verify MongoDB is running?
Run `mongosh --eval "db.adminCommand('ping')"` in your terminal. It should return `{ ok: 1 }`. If not, start it using `brew services start mongodb-community@8.0`.

#### Q: Can I change the MongoDB connection port or host?
Yes! Simply update `MONGODB_URI` in `.env` (e.g. `MONGODB_URI=mongodb://127.0.0.1:27017/`).

#### Q: Does running the tests delete my sample data?
No! Tests run against a dedicated, isolated test database named `student_analytics_test` configured in `tests/conftest.py`. Your primary `student_analytics` data remains untouched.

---

## 👨‍💻 Project Developer & Academic Coursework
- **Course:** CSE494: Intelligent NoSQL Databases
- **Degree:** B.Tech in Computer Science & Engineering
- **Institution:** Department of Computer Science & Engineering
