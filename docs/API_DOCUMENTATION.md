# REST API Specification & Endpoint Documentation

## Student Performance Analytics System (CSE494)
**Base URL:** `http://127.0.0.1:5001`  
**Content-Type:** `application/json`  
**Authentication:** Optional for college coursework demonstration  

---

## 1. Student Management Endpoints

### 1.1 List Students (with Filtering & Pagination)
* **Endpoint:** `GET /api/students`
* **Query Parameters:**
  * `q` (string, optional): Search keyword matching numeric ID, name, or email.
  * `department` (string, optional): Department filter (e.g. `CSE`, `IT`, `ECE`).
  * `semester` (integer, optional): Semester number (1–12).
  * `min_attendance` (float, optional): Lower attendance percentage threshold.
  * `max_attendance` (float, optional): Upper attendance percentage threshold.
  * `page` (integer, default: 1): Page index.
  * `page_size` (integer, default: 10, max: 100): Records per page.
* **Curl Example:**
```bash
curl -X GET "http://127.0.0.1:5001/api/students?department=CSE&page=1&page_size=5"
```
* **Success Response (200 OK):**
```json
{
  "students": [
    {
      "_id": 101,
      "name": "Amit Ranjan",
      "email": "amit.ranjan@example.com",
      "department": "CSE",
      "semester": 7,
      "attendance": 94.5,
      "marks": { "CSE494": 96.0, "CSE401": 92.0, "CSE402": 90.0, "CSE405": 95.0 },
      "skills": ["Python", "MongoDB", "Machine Learning", "System Design"],
      "created_at": "2025-08-15T10:00:00+00:00",
      "updated_at": "2025-08-15T10:00:00+00:00"
    }
  ],
  "total": 12,
  "page": 1,
  "page_size": 5,
  "total_pages": 3
}
```

---

### 1.2 Get Single Student by ID
* **Endpoint:** `GET /api/students/<student_id>`
* **Curl Example:**
```bash
curl -X GET "http://127.0.0.1:5001/api/students/101"
```
* **Success Response (200 OK):**
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
  "created_at": "2025-08-15T10:00:00+00:00",
  "updated_at": "2025-08-15T10:00:00+00:00"
}
```
* **Error Response (404 Not Found):**
```json
{ "error": "Student with ID '999' not found." }
```

---

### 1.3 Register New Student
* **Endpoint:** `POST /api/students`
* **Curl Example:**
```bash
curl -X POST "http://127.0.0.1:5001/api/students" \
  -H "Content-Type: application/json" \
  -d '{
    "_id": 160,
    "name": "Neha Sharma",
    "email": "neha.sharma@example.com",
    "department": "CSE",
    "semester": 6,
    "attendance": 88.0,
    "marks": { "CSE494": 91.0, "CSE401": 85.0 },
    "skills": ["Python", "Docker"]
  }'
```
* **Success Response (201 Created):**
```json
{
  "success": true,
  "student_id": 160,
  "status_code": 201
}
```
* **Error Response (409 Conflict):**
```json
{
  "success": false,
  "errors": { "email": "Email 'neha.sharma@example.com' is already registered to another student." },
  "status_code": 409
}
```

---

### 1.4 Update Student Record
* **Endpoint:** `PUT /api/students/<student_id>`
* **Curl Example:**
```bash
curl -X PUT "http://127.0.0.1:5001/api/students/160" \
  -H "Content-Type: application/json" \
  -d '{
    "attendance": 92.5,
    "marks": { "CSE494": 95.0 }
  }'
```
* **Success Response (200 OK):**
```json
{
  "success": true,
  "modified_count": 1,
  "status_code": 200
}
```

---

### 1.5 Delete Student
* **Endpoint:** `DELETE /api/students/<student_id>`
* **Curl Example:**
```bash
curl -X DELETE "http://127.0.0.1:5001/api/students/160"
```
* **Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Student 160 deleted successfully.",
  "status_code": 200
}
```

---

## 2. Course Management Endpoints

### 2.1 Get All Courses
* **Endpoint:** `GET /api/courses`
* **Curl Example:**
```bash
curl -X GET "http://127.0.0.1:5001/api/courses"
```
* **Success Response (200 OK):**
```json
[
  {
    "_id": "CSE494",
    "course_name": "Intelligent NoSQL Databases",
    "credits": 4,
    "department": "CSE",
    "description": "MongoDB Architecture, Aggregation Framework, Indexing, and Document Modeling."
  }
]
```

### 2.2 Create Course
* **Endpoint:** `POST /api/courses`
* **Curl Example:**
```bash
curl -X POST "http://127.0.0.1:5001/api/courses" \
  -H "Content-Type: application/json" \
  -d '{
    "_id": "CSE490",
    "course_name": "Blockchain Technologies",
    "credits": 3,
    "department": "CSE",
    "description": "Smart contracts and decentralized ledgers."
  }'
```

### 2.3 Delete Course
* **Endpoint:** `DELETE /api/courses/<course_id>`
* **Safety Feature:** Returns 400 Bad Request if any students have recorded marks for this course.

---

## 3. Analytics & Machine Learning Endpoints

### 3.1 Overall KPIs (`$facet`)
* **Endpoint:** `GET /api/analytics/overview`
* **Response (200 OK):**
```json
{
  "total_students": 35,
  "total_courses": 7,
  "overall_avg_marks": 73.18,
  "overall_avg_attendance": 80.24,
  "at_risk_count": 10
}
```

### 3.2 Topper Rankings
* **Endpoint:** `GET /api/analytics/topper-ranking?limit=5`
* **Response (200 OK):**
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
  }
]
```

### 3.3 Department Analytics (`$group`)
* **Endpoint:** `GET /api/analytics/departments`
* **Response (200 OK):**
```json
[
  {
    "department": "CSE",
    "total_students": 12,
    "avg_marks": 78.42,
    "highest_marks": 94.75,
    "avg_attendance": 84.17
  }
]
```

### 3.4 Course Statistics (`$lookup`)
* **Endpoint:** `GET /api/analytics/course-statistics`
* **Response (200 OK):**
```json
[
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
]
```

### 3.5 At-Risk Students
* **Endpoint:** `GET /api/analytics/at-risk?attendance_threshold=75&marks_threshold=40`

### 3.6 Skill Distribution (`$unwind`)
* **Endpoint:** `GET /api/analytics/skills?limit=10`

### 3.7 Scikit-Learn Predictive Model Evaluation
* **Endpoint:** `GET /api/analytics/ml-model-info`
* **Response (200 OK):**
```json
{
  "algorithm": "RandomForestClassifier",
  "accuracy": 1.0,
  "precision": 1.0,
  "recall": 1.0,
  "f1_score": 1.0,
  "training_samples": 26,
  "testing_samples": 9,
  "feature_importances": {
    "attendance": 0.442,
    "avg_marks": 0.381,
    "semester": 0.082,
    "num_courses": 0.051,
    "num_skills": 0.044
  }
}
```

### 3.8 Predict Risk for Individual Student
* **Endpoint:** `GET /api/analytics/predict-risk/127`
* **Response (200 OK):**
```json
{
  "student_id": 127,
  "name": "Sunil Varma",
  "attendance": 48.5,
  "avg_marks": 40.0,
  "rule_evaluation": {
    "risk_level": "High Risk",
    "is_at_risk": true,
    "reasons": [
      "Critical attendance shortage (<60%)",
      "Below-average academic standing (<55%)"
    ],
    "recommendation": "Immediate faculty mentoring and academic counseling required."
  },
  "ml_prediction": {
    "predicted_label": "At Risk",
    "risk_probability": 0.88,
    "confidence_score": 88.0
  }
}
```
