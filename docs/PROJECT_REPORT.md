# PROJECT REPORT

## STUDENT PERFORMANCE ANALYTICS SYSTEM USING MONGODB AND PYMONGO
**Course Code:** CSE494: Intelligent NoSQL Databases  
**Academic Degree:** Bachelor of Technology in Computer Science & Engineering  
**Primary Database:** MongoDB Community Edition v8.0  
**Backend Framework:** Python 3.12 / Flask 3.0 / PyMongo 4.8  

---

## 1. ABSTRACT
Modern educational institutions face increasing challenges in tracking diverse, multi-dimensional student performance metrics across evolving curriculums. Traditional relational databases (RDBMS) struggle with dynamic course offerings, varying elective sets, and rapid multi-attribute analytics without extensive schema alterations and computationally expensive multi-table joins. This project develops the **Student Performance Analytics System**, an intelligent, scalable academic management platform built with MongoDB, PyMongo, Flask, and Scikit-Learn. The system demonstrates core NoSQL paradigms, utilizing BSON document modeling with embedded course marks, cross-collection referencing with the MongoDB Aggregation Framework, database-level schema constraints, query optimization via compound and unique B-Tree indexes, and a dual-tier academic risk prediction engine combining rule-based heuristics with machine learning. Empirical benchmarks demonstrate a reduction in documents examined from 10,000 to 474 using compound indexes, and an automated test suite achieves 100% pass across 36 comprehensive test cases.

---

## 2. INTRODUCTION
In academic institutions, students accumulate data spanning enrollment details, semester progression, attendance logs, course-specific marks, and co-curricular skills. Relational database management systems (RDBMS) model these requirements using normalized tables, requiring foreign keys, junction tables, and complex SQL joins that degrade under heavy analytical loads. 

Document-oriented NoSQL databases, specifically MongoDB, present a modern alternative. MongoDB represents data using Binary JSON (BSON), permitting nested sub-documents, dynamic key-value attributes, and polymorphic arrays within a single record. By leveraging MongoDB and PyMongo directly, this project provides a full-stack, enterprise-grade academic analytics portal that demonstrates database design, native server-side aggregations, query execution optimization, and transparent intelligent intervention alerts.

---

## 3. PROBLEM STATEMENT
Educational administrators and course coordinators lack real-time visibility into academic risk factors. Existing university software suffers from:
1. **Rigid Schemas:** Adding or modifying elective courses often requires database migrations across several relational tables.
2. **Performance Bottlenecks:** Aggregating cohort averages, department percentiles, and attendance correlations using standard relational queries incurs high latency when scanning millions of historical records.
3. **Late Academic Interventions:** Students falling below attendance minimums (75%) or failing thresholds (40%) are typically identified only at the conclusion of a semester rather than proactively.

---

## 4. OBJECTIVES
1. Implement a complete, production-ready full-stack application using **Python 3.12**, **MongoDB 8.0**, and **PyMongo 4.8** without Object-Document Mappers (ODMs).
2. Model academic data using both **embedding** (course marks embedded inside student records) and **referencing** (courses stored in an independent collection).
3. Enforce database-level data integrity using MongoDB **`$jsonSchema`** validators.
4. Build **nine native aggregation pipelines** executing calculations entirely within MongoDB.
5. Implement, benchmark, and evaluate **single-field, compound, unique, and text indexes** using `explain("executionStats")`.
6. Integrate a dual-tier academic risk analytics engine incorporating deterministic business rules and a Scikit-Learn predictive model.
7. Expose all functionalities via a responsive web dashboard and documented REST API endpoints.

---

## 5. EXISTING SYSTEM VS. PROPOSED SYSTEM

| Parameter | Existing System (Traditional RDBMS) | Proposed System (MongoDB & PyMongo) |
| :--- | :--- | :--- |
| **Data Model** | Rigid relational tables with strict foreign keys | Dynamic, self-describing BSON documents |
| **Course Marks Storage** | Separate junction table (`Student_Courses_Marks`) | Embedded sub-document with instant atomic reads |
| **Analytical Calculations** | Multi-table SQL `JOIN` statements and client loops | MongoDB Aggregation Framework executed on server |
| **Schema Evolution** | Requires database migration scripts and downtime | Flexible schema with optional `$jsonSchema` validation |
| **Query Optimization** | B-Tree indexes on relational columns | Compound, Unique, and Text indexes with `explain()` |
| **Risk Prediction** | Manual post-semester review | Real-time rule-based assessment and ML classification |

---

## 6. HARDWARE AND SOFTWARE REQUIREMENTS

### 6.1 Software Requirements
- **Operating System:** macOS (Apple Silicon ARM64)
- **Database Server:** MongoDB Community Edition v8.0.28
- **MongoDB Shell:** mongosh v2.9.2
- **Runtime Environment:** Python 3.12.15
- **Database Driver:** PyMongo 4.8.0
- **Web Framework:** Flask 3.0.3, Jinja2 3.1.6
- **Machine Learning Library:** Scikit-Learn 1.5.2, NumPy 2.1.2
- **Testing Framework:** Pytest 8.3.3
- **Frontend Assets:** HTML5, CSS3, JavaScript (ES6), Bootstrap 5.3.3, Chart.js 4.4

### 6.2 Hardware Specifications (Tested Platform)
- **Architecture:** ARM64 (Apple M-series)
- **Primary Memory (RAM):** 8 GB or higher
- **Disk Storage:** SSD with WiredTiger storage engine

---

## 7. SYSTEM ARCHITECTURE

```
+-------------------------------------------------------------------------+
|                              CLIENT TIER                                |
|   Responsive Web Dashboard (Chart.js / Bootstrap) & REST API Clients    |
+------------------------------------+------------------------------------+
                                     | HTTP Requests (JSON / HTML)
                                     v
+-------------------------------------------------------------------------+
|                        APPLICATION BACKEND TIER                         |
|   Flask Application Factory (app.py) & Blueprints (routes/)            |
|   - dashboard_bp | students_bp | courses_bp | analytics_bp              |
+------------------------------------+------------------------------------+
                                     | Python Service Calls
                                     v
+-------------------------------------------------------------------------+
|                          BUSINESS LOGIC TIER                            |
|   - StudentService: CRUD, Filtering, Pagination, Array Operators        |
|   - CourseService: Catalog Management, Referential Integrity Checks    |
|   - AnalyticsService: 9 Server-Side Aggregation Pipelines               |
|   - AcademicRiskPredictor: Rule Engine & Scikit-Learn Random Forest     |
+------------------------------------+------------------------------------+
                                     | PyMongo 4.8 Connection Pool
                                     v
+-------------------------------------------------------------------------+
|                            DATABASE TIER                                |
|   MongoDB Community Edition 8.0 (WiredTiger Storage Engine)             |
|   - Database: student_analytics / student_analytics_test               |
|   - Collections: students, courses                                      |
|   - Constraints: $jsonSchema Validators, B-Tree Indexes                 |
+-------------------------------------------------------------------------+
```

---

## 8. DATABASE DESIGN

The system uses a document-oriented database named `student_analytics`.
Data modeling balances **document embedding** for frequently coupled data (student coursework marks) and **collection referencing** for shared, normalized metadata (academic courses).

### 8.1 Why BSON?
MongoDB represents documents in Binary JSON (BSON). BSON extends JSON by adding support for non-textual data types, including native 64-bit BSON Datetime (`datetime.now(timezone.utc)`), 64-bit integers (`int64`), and floating-point doubles. Length prefixes allow WiredTiger to traverse documents rapidly without parsing character-by-character.

---

## 9. COLLECTION SCHEMAS & VALIDATION

Database-level validation is configured using MongoDB's `$jsonSchema` engine.

### 9.1 `students` Collection Document
```json
{
  "_id": 101,
  "name": "Amit Ranjan",
  "email": "amit.ranjan@example.com",
  "department": "CSE",
  "semester": 7,
  "attendance": 94.5,
  "marks": {
    "CSE494": 96.0,
    "CSE401": 92.0,
    "CSE402": 90.0,
    "CSE405": 95.0
  },
  "skills": ["Python", "MongoDB", "Machine Learning", "System Design"],
  "created_at": "2025-08-15T10:00:00Z",
  "updated_at": "2025-08-15T10:00:00Z"
}
```

### 9.2 `courses` Collection Document
```json
{
  "_id": "CSE494",
  "course_name": "Intelligent NoSQL Databases",
  "credits": 4,
  "department": "CSE",
  "description": "MongoDB Architecture, Aggregation Framework, Indexing, and Document Modeling.",
  "created_at": "2025-08-01T09:00:00Z"
}
```

---

## 10. CRUD IMPLEMENTATION
All CRUD operations are implemented directly in PyMongo without an ODM:
- **`insert_one()` / `insert_many()`:** Inserts validated student and course documents.
- **`find()` / `find_one()`:** Parameterized queries supporting text searches, attendance ranges, and department filtering.
- **`update_one()`:** Demonstrates atomic MongoDB operators:
  - `$set`: Updates demographics and embedded marks using dot notation (`marks.CSE494: 95.0`).
  - `$addToSet` with `$each`: Appends technical skills to the BSON array without duplicates.
- **`update_many()`:** Demonstrates bulk updates using `$inc` to award attendance bonuses across a department.
- **`delete_one()` / `delete_many()`:** Deletes records with safety checks preventing the deletion of courses with active student marks.

---

## 11. AGGREGATION PIPELINES (THE 9 PIPELINES)

1. **Pipeline 1: Student Performance Summary:** Uses `$objectToArray`, `$avg`, `$max`, `$min`, and `$size` to compute student-level summary statistics.
2. **Pipeline 2: Topper Ranking:** Sorts students by calculated average marks descending and applies `$limit`.
3. **Pipeline 3: Department-wise Performance:** Groups by `$department` to calculate student counts, average marks, and average attendance.
4. **Pipeline 4: At-Risk Students:** Uses `$match` to filter students with attendance `< 75%` or marks `< 40`, adding formatted reason strings with `$concatArrays`.
5. **Pipeline 5: Course-wise Statistics with `$lookup`:** Unwinds marks and performs a left outer join with the `courses` collection.
6. **Pipeline 6: Skill Distribution:** Deconstructs the `skills` array via `$unwind` and counts occurrences via `$group`.
7. **Pipeline 7: Performance Categories:** Classifies students into academic categories using `$project` and `$switch`.
8. **Pipeline 8: Semester-wise Analytics:** Aggregates by composite grouping key `{semester, department}`.
9. **Pipeline 9: System Overview KPIs (`$facet`):** Computes total counts, averages, and at-risk counts in a single database pass.

---

## 12. INDEXING AND PERFORMANCE ANALYSIS

### Empirical Benchmark Results (10,000 Synthetic Student Documents)
Collected via `scripts/benchmark_queries.py` using `explain("executionStats")`:

| Query Scenario | Index Configuration | Execution Stage | Docs Examined | Keys Examined | Docs Returned | Execution Time |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Q1: Dept + Attendance Range** | Unindexed | `SORT -> COLLSCAN` | **10,000** | 0 | 474 | **4 ms** |
| **Q1: Dept + Attendance Range** | Compound (`department`, `attendance`) | `FETCH -> IXSCAN` | **474** | 474 | 474 | **2 ms** |
| **Q2: Email Point Lookup** | Unindexed | `COLLSCAN` | **10,000** | 0 | 1 | **1 ms** |
| **Q2: Email Point Lookup** | Unique Index (`email`) | `EXPRESS_IXSCAN` | **1** | 1 | 1 | **1 ms** |

**Evaluation:**
- In Q1, the compound index transformed an exhaustive collection scan (`COLLSCAN`) of 10,000 documents into an index scan (`IXSCAN`) examining only the 474 matching documents.
- In Q2, the unique index located the single document via B-Tree traversal in $O(\log N)$ time, examining exactly 1 key and 1 document.

---

## 13. EMBEDDING VS. REFERENCING
- **Marks Embedded in Students:** Read latency is prioritized. Student marks are accessed together with student records. Because each student enrolls in a bounded number of courses, embedding avoids document bloat while providing ACID guarantees at the document level.
- **Courses Stored as References:** Prevents data duplication. If course metadata (title, credits, syllabus) were embedded in thousands of student records, updating course details would cause massive write amplification and anomalies.

---

## 14. VALIDATION AND CONSTRAINTS
- **Database-Level Validation:** Configured via `$jsonSchema` in `database/validators.py`. Rejects documents with attendance outside $[0, 100]$, marks outside $[0, 100]$, or invalid email regex patterns.
- **Application-Level Validation:** Python functions (`validate_student_payload`) validate input before dispatching queries to MongoDB, providing informative error messages for client interfaces.

---

## 15. PYMONGO INTEGRATION
- Implemented as a reusable singleton in `database/connection.py`.
- Thread-safe connection pool with configurable timeouts (`connectTimeoutMS=5000`, `serverSelectionTimeoutMS=5000`).
- Connectivity verification via `client.admin.command('ping')`.
- Safe serialization handles BSON types (`ObjectId`, `datetime`) for JSON API responses.

---

## 16. DASHBOARD IMPLEMENTATION
- Full-stack web dashboard built with Flask, HTML5, CSS3, Bootstrap 5, and Chart.js 4.4.
- Includes Overview, Students Directory, Student Details & Transcript, Course Catalog, and Analytics & ML pages.
- Chart.js charts render data directly from MongoDB aggregation pipelines.

---

## 17. COURSE OUTCOME (CO) MAPPING

| Course Outcome (CO) | Course Outcome Description | Specific Project Feature Demonstrating the Outcome |
| :--- | :--- | :--- |
| **CO1** | Discuss NoSQL concepts and differentiate NoSQL databases from relational databases. | Project report Section 5, Viva Questions 1–4, and documentation explaining CAP theorem, BSON vs. JSON, and schema flexibility. |
| **CO2** | Apply CRUD operations, indexing, and query optimization using MongoDB. | `StudentService` and `CourseService` implementing `insert_one`, `find`, `update_one`, `delete_one`, and compound/unique/text index definitions. |
| **CO3** | Analyze data modeling strategies, including embedding and referencing. | Embedding `marks` within `students` for atomic reads vs. referencing `courses` with cross-collection integrity checks. |
| **CO4** | Evaluate the performance impact of indexes and aggregation frameworks on queries. | Empirical 10,000-document benchmark in `benchmark_queries.py` comparing `COLLSCAN` vs. `IXSCAN` and 9 native aggregation pipelines. |
| **CO5** | Develop applications integrating MongoDB with Python and PyMongo. | Reusable `connection.py` connection pool, Flask REST API endpoints, safe BSON serialization, and 36 automated pytest tests. |
| **CO6** | Create a functional mini-project demonstrating MongoDB and intelligent analytics. | Complete web application featuring rule-based intervention evaluation and a Scikit-Learn predictive model. |

---

## 18. TESTING AND RESULTS
Automated testing was conducted using `pytest` against an isolated test database (`student_analytics_test`).
- **Total Tests Executed:** 36
- **Passed:** 36 (100%)
- **Failed:** 0
- **Execution Time:** 0.42 seconds
- **Modules Verified:** `test_analytics.py`, `test_api.py`, `test_courses.py`, `test_students.py`, `test_validation.py`.

---

## 19. LIMITATIONS
1. **Synthetic Training Data:** The Scikit-Learn predictive model is trained on a synthetic academic dataset designed for coursework demonstration; real-world deployment requires multi-year longitudinal cohorts.
2. **Sharding Not Implemented:** Designed for single-replica or replica set deployment; distributed sharding across multiple MongoDB shards is outside current project scope.

---

## 20. FUTURE SCOPE
1. Integration with University Learning Management Systems (LMS) via OAuth2 and LTI standards.
2. Time-series collection modeling for continuous biometric attendance tracking.
3. Automated student mentoring notification dispatch via Celery background tasks.

---

## 21. CONCLUSION
The Student Performance Analytics System demonstrates the practical application of MongoDB Community Edition and PyMongo in building intelligent academic information systems. By combining document embedding, cross-collection joins with `$lookup`, server-side aggregation pipelines, B-Tree index optimization, and machine learning, the project fulfills all objectives for course CSE494: Intelligent NoSQL Databases.

---

## 22. REFERENCES
1. Chodorow, K. (2013). *MongoDB: The Definitive Guide*. O'Reilly Media.
2. Banker, K., et al. (2016). *MongoDB in Action*. Manning Publications.
3. MongoDB Documentation. *Aggregation Pipeline Quick Reference*. https://www.mongodb.com/docs/manual/core/aggregation-pipeline/
4. PyMongo Documentation. *Tutorial & API Reference*. https://pymongo.readthedocs.io/
5. Scikit-Learn Documentation. *Random Forest Classifier*. https://scikit-learn.org/
