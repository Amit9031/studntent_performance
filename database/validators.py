"""
MongoDB JSON Schema Validators and Python-level validation utilities.

Implements database-level schema validation using MongoDB's $jsonSchema validator
and application-level payload validation for student and course records.
"""

import re
import logging
from pymongo.errors import OperationFailure

logger = logging.getLogger(__name__)

# Email validation regex
EMAIL_REGEX = re.compile(r"^[\w\.-]+@([\w\.-]+\.)+[a-zA-Z]{2,10}$")

# MongoDB JSON Schema for 'students' collection
STUDENT_JSON_SCHEMA = {
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
                "description": "Student full name - string between 2 and 100 characters"
            },
            "email": {
                "bsonType": "string",
                "pattern": "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$",
                "description": "Valid email address format - required and unique"
            },
            "department": {
                "bsonType": "string",
                "enum": ["CSE", "IT", "ECE", "ME", "EE", "CE", "AIDS", "AIML"],
                "description": "Department code - must be one of the permitted departments"
            },
            "semester": {
                "bsonType": ["int", "long"],
                "minimum": 1,
                "maximum": 12,
                "description": "Semester number between 1 and 12"
            },
            "attendance": {
                "bsonType": ["double", "int", "long"],
                "minimum": 0,
                "maximum": 100,
                "description": "Attendance percentage between 0 and 100"
            },
            "marks": {
                "bsonType": "object",
                "description": "Dictionary mapping course code to numeric mark (0-100)",
                "additionalProperties": {
                    "bsonType": ["double", "int", "long"],
                    "minimum": 0,
                    "maximum": 100
                }
            },
            "skills": {
                "bsonType": "array",
                "items": {
                    "bsonType": "string"
                },
                "description": "List of student skills"
            },
            "created_at": {
                "bsonType": ["date", "timestamp"],
                "description": "BSON datetime stamp when the student record was created"
            },
            "updated_at": {
                "bsonType": ["date", "timestamp"],
                "description": "BSON datetime stamp of last record modification"
            }
        }
    }
}

# MongoDB JSON Schema for 'courses' collection
COURSE_JSON_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["_id", "course_name", "credits", "department"],
        "properties": {
            "_id": {
                "bsonType": "string",
                "minLength": 3,
                "maxLength": 20,
                "description": "Course code string (e.g., 'CSE494') - required and unique"
            },
            "course_name": {
                "bsonType": "string",
                "minLength": 2,
                "maxLength": 150,
                "description": "Descriptive course title"
            },
            "credits": {
                "bsonType": ["int", "long"],
                "minimum": 1,
                "maximum": 10,
                "description": "Course credits between 1 and 10"
            },
            "department": {
                "bsonType": "string",
                "description": "Offering academic department"
            },
            "description": {
                "bsonType": "string",
                "description": "Syllabus summary or course description"
            },
            "created_at": {
                "bsonType": ["date", "timestamp"],
                "description": "BSON datetime stamp"
            }
        }
    }
}


def apply_collection_validators(db):
    """
    Apply MongoDB database-level JSON schema validation to 'students' and 'courses' collections.
    Creates collections if they do not exist, or updates schema via collMod command.
    """
    existing_collections = db.list_collection_names()
    results = {}

    # Setup students collection validator
    if "students" not in existing_collections:
        try:
            db.create_collection("students", validator=STUDENT_JSON_SCHEMA, validationLevel="moderate")
            results["students"] = "Created collection with JSON Schema validator"
        except OperationFailure as exc:
            logger.warning("Could not create students with validator: %s", exc)
            results["students"] = f"Warning: {exc}"
    else:
        try:
            db.command({
                "collMod": "students",
                "validator": STUDENT_JSON_SCHEMA,
                "validationLevel": "moderate"
            })
            results["students"] = "Updated existing collection with JSON Schema validator"
        except OperationFailure as exc:
            logger.warning("Could not modify students validator: %s", exc)
            results["students"] = f"Warning: {exc}"

    # Setup courses collection validator
    if "courses" not in existing_collections:
        try:
            db.create_collection("courses", validator=COURSE_JSON_SCHEMA, validationLevel="moderate")
            results["courses"] = "Created collection with JSON Schema validator"
        except OperationFailure as exc:
            logger.warning("Could not create courses with validator: %s", exc)
            results["courses"] = f"Warning: {exc}"
    else:
        try:
            db.command({
                "collMod": "courses",
                "validator": COURSE_JSON_SCHEMA,
                "validationLevel": "moderate"
            })
            results["courses"] = "Updated existing collection with JSON Schema validator"
        except OperationFailure as exc:
            logger.warning("Could not modify courses validator: %s", exc)
            results["courses"] = f"Warning: {exc}"

    return results


def validate_student_payload(data, is_update=False):
    """
    Application-level validation for incoming student data.
    Returns (is_valid, errors_dict, cleaned_data).
    """
    errors = {}
    cleaned = {}

    # Student ID (_id)
    if not is_update:
        if "_id" not in data or data["_id"] is None or str(data["_id"]).strip() == "":
            errors["_id"] = "Student ID (_id) is required."
        else:
            try:
                cleaned["_id"] = int(data["_id"])
                if cleaned["_id"] <= 0:
                    errors["_id"] = "Student ID must be a positive integer."
            except (ValueError, TypeError):
                errors["_id"] = "Student ID must be a valid integer."
    elif "_id" in data:
        try:
            cleaned["_id"] = int(data["_id"])
        except (ValueError, TypeError):
            errors["_id"] = "Student ID must be a valid integer."

    # Name
    if "name" in data or not is_update:
        name = str(data.get("name", "")).strip()
        if not name or len(name) < 2:
            errors["name"] = "Name must be at least 2 characters long."
        else:
            cleaned["name"] = name

    # Email
    if "email" in data or not is_update:
        email = str(data.get("email", "")).strip().lower()
        if not email or not EMAIL_REGEX.match(email):
            errors["email"] = "A valid email address is required (e.g., student@example.com)."
        else:
            cleaned["email"] = email

    # Department
    valid_departments = ["CSE", "IT", "ECE", "ME", "EE", "CE", "AIDS", "AIML"]
    if "department" in data or not is_update:
        dept = str(data.get("department", "")).strip().upper()
        if dept not in valid_departments:
            errors["department"] = f"Department must be one of: {', '.join(valid_departments)}."
        else:
            cleaned["department"] = dept

    # Semester
    if "semester" in data or not is_update:
        try:
            sem = int(data.get("semester", 0))
            if sem < 1 or sem > 12:
                errors["semester"] = "Semester must be an integer between 1 and 12."
            else:
                cleaned["semester"] = sem
        except (ValueError, TypeError):
            errors["semester"] = "Semester must be a valid integer."

    # Attendance
    if "attendance" in data or not is_update:
        try:
            att = float(data.get("attendance", -1))
            if att < 0 or att > 100:
                errors["attendance"] = "Attendance must be between 0 and 100."
            else:
                cleaned["attendance"] = round(att, 2)
        except (ValueError, TypeError):
            errors["attendance"] = "Attendance must be a valid number between 0 and 100."

    # Marks (embedded document)
    if "marks" in data or not is_update:
        raw_marks = data.get("marks", {})
        if not isinstance(raw_marks, dict):
            errors["marks"] = "Marks must be an object/dictionary mapping course code to score."
        else:
            cleaned_marks = {}
            for course_code, score in raw_marks.items():
                code = str(course_code).strip().upper()
                if not code:
                    continue
                try:
                    num_score = float(score)
                    if num_score < 0 or num_score > 100:
                        errors[f"marks.{code}"] = f"Mark for {code} must be between 0 and 100."
                    else:
                        cleaned_marks[code] = round(num_score, 2)
                except (ValueError, TypeError):
                    errors[f"marks.{code}"] = f"Mark for {code} must be a numeric score."
            cleaned["marks"] = cleaned_marks

    # Skills (array of strings)
    if "skills" in data:
        raw_skills = data.get("skills", [])
        if isinstance(raw_skills, str):
            # Support comma-separated strings from HTML forms
            cleaned["skills"] = [s.strip() for s in raw_skills.split(",") if s.strip()]
        elif isinstance(raw_skills, list):
            cleaned["skills"] = [str(s).strip() for s in raw_skills if str(s).strip()]
        else:
            cleaned["skills"] = []
    elif not is_update:
        cleaned["skills"] = []

    is_valid = len(errors) == 0
    return is_valid, errors, cleaned


def validate_course_payload(data, is_update=False):
    """
    Application-level validation for incoming course data.
    Returns (is_valid, errors_dict, cleaned_data).
    """
    errors = {}
    cleaned = {}

    # Course ID / Code (_id)
    if not is_update:
        code = str(data.get("_id", "")).strip().upper()
        if not code or len(code) < 3:
            errors["_id"] = "Course code (_id) is required (e.g., 'CSE494')."
        else:
            cleaned["_id"] = code
    elif "_id" in data:
        cleaned["_id"] = str(data.get("_id", "")).strip().upper()

    # Course Name
    if "course_name" in data or not is_update:
        name = str(data.get("course_name", "")).strip()
        if not name or len(name) < 2:
            errors["course_name"] = "Course name must be at least 2 characters long."
        else:
            cleaned["course_name"] = name

    # Credits
    if "credits" in data or not is_update:
        try:
            creds = int(data.get("credits", 0))
            if creds < 1 or creds > 10:
                errors["credits"] = "Credits must be an integer between 1 and 10."
            else:
                cleaned["credits"] = creds
        except (ValueError, TypeError):
            errors["credits"] = "Credits must be a valid integer."

    # Department
    if "department" in data or not is_update:
        dept = str(data.get("department", "")).strip().upper()
        if not dept:
            errors["department"] = "Department is required."
        else:
            cleaned["department"] = dept

    # Description (optional)
    if "description" in data:
        cleaned["description"] = str(data.get("description", "")).strip()
    elif not is_update:
        cleaned["description"] = ""

    is_valid = len(errors) == 0
    return is_valid, errors, cleaned
