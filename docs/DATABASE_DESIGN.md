# Database Design & Architecture Specification

## Project: Student Performance Analytics System
**Course:** CSE494: Intelligent NoSQL Databases  
**Database Engine:** MongoDB Community Edition 8.0  
**Database Driver:** PyMongo 4.8  
**Primary Database:** `student_analytics`  
**Isolated Test Database:** `student_analytics_test`  

---

## 1. Why MongoDB and BSON?

### 1.1 JSON vs. BSON
MongoDB represents documents internally using **BSON (Binary JSON)**, an optimized binary serialization format designed for speed, traversability, and extended data typing.

| Feature / Metric | Standard JSON (JavaScript Object Notation) | BSON (Binary JSON) |
| :--- | :--- | :--- |
| **Storage Format** | Human-readable text format (UTF-8) | Binary encoded format with length prefixes |
| **Parsing Speed** | Requires parsing byte-by-byte text characters | Extremely fast; field lengths allow skipping unread fields |
| **Supported Data Types** | Only 6 basic types: `string`, `number`, `boolean`, `null`, `array`, `object` | Extended types: `int32`, `int64`, `double`, `decimal128`, `date` (BSON datetime), `ObjectId`, `binData`, `regex`, `timestamp` |
| **Date / Time Handling**| Must be serialized as ISO-8601 strings or epoch integers | Native 64-bit integer tracking milliseconds since Unix epoch UTC |
| **Space Efficiency** | Smaller for trivial payloads | Slightly larger overhead due to length headers, but drastically faster for indexing and traversal |

In this project, dates like `created_at` and `updated_at` are stored as native **BSON Datetime** objects (`datetime.now(timezone.utc)`), preventing timezone ambiguities and enabling native range queries (`$gte`, `$lte`).

---

## 2. Data Modeling Strategy: Embedding vs. Referencing

### 2.1 Embedding Strategy (`marks` in `students`)
Each student document contains an embedded document named `marks`:
```json
"marks": {
    "CSE494": 96.0,
    "CSE401": 92.0,
    "CSE402": 90.0,
    "CSE405": 95.0
}
```

#### Why Embedding is Optimal for Marks:
1. **Atomic Reads & Writes:** In 95% of use cases, when an instructor, student, or analytics module accesses a student profile, their coursework marks are required together. Embedding ensures a single disk seek and zero joins.
2. **ACID Document Guarantee:** MongoDB provides ACID atomicity at the single-document level. Updating a student's marks and recalculating their status occurs atomically without distributed transaction overhead.
3. **Bounded Growth:** The number of courses a student undertakes in a degree program is strictly bounded (typically 30–50 courses across 8 semesters), avoiding document bloating and respecting MongoDB's 16MB document limit.

### 2.2 Referencing Strategy (`courses` Collection)
Course metadata (course name, credits, department, syllabus description) is stored in a separate collection named `courses`:
```json
{
    "_id": "CSE494",
    "course_name": "Intelligent NoSQL Databases",
    "credits": 4,
    "department": "CSE",
    "description": "MongoDB Architecture, Aggregation Framework, Indexing, and Document Modeling."
}
```

#### Why Referencing is Appropriate for Courses:
1. **Data Redundancy Prevention:** Multiple students (hundreds to thousands) enroll in course `CSE494`. If course details (credits, title, syllabus) were embedded in every student document, any change in course title or credits would require updating thousands of student documents.
2. **Referential Joins via `$lookup`:** When analytical reports require enriched course metadata, MongoDB's `$lookup` aggregation stage performs an efficient index-backed left outer join between `students.marks` and `courses._id`.

---

## 3. Collection Schemas & Database-Level Validation

MongoDB enforces structural integrity using `$jsonSchema` validators registered via `db.create_collection()` and `collMod`.

### 3.1 `students` Collection Schema
```json
{
  "$jsonSchema": {
    "bsonType": "object",
    "required": ["_id", "name", "email", "department", "semester", "attendance", "marks"],
    "properties": {
      "_id": {
        "bsonType": ["int", "long", "double"],
        "description": "Numeric student ID - required and unique"
      },
      "name": {
        "bsonType": "string",
        "minLength": 2,
        "maxLength": 100,
        "description": "Student full name"
      },
      "email": {
        "bsonType": "string",
        "pattern": "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$",
        "description": "Valid email address format - unique index enforced"
      },
      "department": {
        "bsonType": "string",
        "enum": ["CSE", "IT", "ECE", "ME", "EE", "CE", "AIDS", "AIML"],
        "description": "Department code"
      },
      "semester": {
        "bsonType": ["int", "long"],
        "minimum": 1,
        "maximum": 12,
        "description": "Semester number"
      },
      "attendance": {
        "bsonType": ["double", "int", "long"],
        "minimum": 0,
        "maximum": 100,
        "description": "Attendance percentage"
      },
      "marks": {
        "bsonType": "object",
        "description": "Key-value mapping of course codes to scores",
        "additionalProperties": {
          "bsonType": ["double", "int", "long"],
          "minimum": 0,
          "maximum": 100
        }
      },
      "skills": {
        "bsonType": "array",
        "items": { "bsonType": "string" },
        "description": "List of student technical competencies"
      },
      "created_at": {
        "bsonType": ["date", "timestamp"],
        "description": "BSON datetime stamp"
      },
      "updated_at": {
        "bsonType": ["date", "timestamp"],
        "description": "BSON datetime stamp"
      }
    }
  }
}
```

### 3.2 `courses` Collection Schema
```json
{
  "$jsonSchema": {
    "bsonType": "object",
    "required": ["_id", "course_name", "credits", "department"],
    "properties": {
      "_id": {
        "bsonType": "string",
        "minLength": 3,
        "maxLength": 20,
        "description": "Course code string (e.g., 'CSE494')"
      },
      "course_name": {
        "bsonType": "string",
        "minLength": 2,
        "maxLength": 150
      },
      "credits": {
        "bsonType": ["int", "long"],
        "minimum": 1,
        "maximum": 10
      },
      "department": { "bsonType": "string" },
      "description": { "bsonType": "string" },
      "created_at": { "bsonType": ["date", "timestamp"] }
    }
  }
}
```

---

## 4. Index Architecture & Query Optimization

| Collection | Index Name | Indexed Fields | Index Type | Purpose / Query Optimized |
| :--- | :--- | :--- | :--- | :--- |
| `students` | `_id_` | `{"_id": 1}` | Default Primary Key | Unique point lookups by numeric student ID |
| `students` | `uniq_idx_email` | `{"email": 1}` | Unique Single-Field | Enforces unique email constraint at engine level; converts full scan to `IXSCAN` |
| `students` | `idx_department` | `{"department": 1}` | Single-Field | Accelerates department filtering and `$group` pipeline stages |
| `students` | `idx_semester` | `{"semester": 1}` | Single-Field | Optimizes semester cohort aggregations |
| `students` | `idx_dept_attendance` | `{"department": 1, "attendance": -1}` | Compound Index | Optimizes department queries sorted by attendance (e.g. at-risk queries) without in-memory sort |
| `students` | `text_idx_name_email` | `{"name": "text", "email": "text"}` | Full-Text Index | Powers text search queries across student catalog |
| `courses` | `_id_` | `{"_id": 1}` | Default Primary Key | Fast course code lookups and foreign field joins in `$lookup` |
| `courses` | `idx_course_dept` | `{"department": 1}` | Single-Field | Accelerates course catalog department filtering |
