"""
Course Data Access and Business Logic Service.

Encapsulates complete CRUD operations for the 'courses' collection using PyMongo.
Demonstrates PyMongo methods: insert_one, find, find_one, update_one, delete_one,
count_documents, distinct, and cross-collection reference validation.
"""

from datetime import datetime, timezone
import logging
from pymongo.errors import DuplicateKeyError, PyMongoError
from database.connection import get_database
from database.validators import validate_course_payload

logger = logging.getLogger(__name__)


class CourseService:
    """Service handling all course-related database operations."""

    def __init__(self, db=None):
        self._db = db

    @property
    def db(self):
        return self._db if self._db is not None else get_database()

    @property
    def collection(self):
        return self.db["courses"]

    # ==========================================
    # CREATE Operations
    # ==========================================

    def create_course(self, data):
        """
        Create a new course document.
        Validates payload, prevents duplicate course code (_id), sets BSON timestamp.
        """
        is_valid, errors, cleaned = validate_course_payload(data, is_update=False)
        if not is_valid:
            return {"success": False, "errors": errors, "status_code": 400}

        cleaned["created_at"] = datetime.now(timezone.utc)

        try:
            # PyMongo insert_one()
            result = self.collection.insert_one(cleaned)
            logger.info("Inserted new course with _id: %s", result.inserted_id)
            return {
                "success": True,
                "course_id": result.inserted_id,
                "course": cleaned,
                "status_code": 201
            }
        except DuplicateKeyError:
            return {
                "success": False,
                "errors": {"_id": f"Course code '{cleaned.get('_id')}' already exists."},
                "status_code": 409
            }
        except PyMongoError as exc:
            logger.error("Database error inserting course: %s", exc)
            return {
                "success": False,
                "errors": {"database": str(exc)},
                "status_code": 500
            }

    # ==========================================
    # READ Operations
    # ==========================================

    def get_course_by_id(self, course_id):
        """
        Retrieve a single course by string ID (e.g. 'CSE494') using find_one().
        """
        if not course_id:
            return None
        code = str(course_id).strip().upper()
        # PyMongo find_one()
        return self.collection.find_one({"_id": code})

    def get_courses(self, department=None, search=None):
        """
        Retrieve all courses with optional department and text filtering.
        """
        filter_doc = {}
        if department and str(department).strip():
            filter_doc["department"] = str(department).strip().upper()

        if search and str(search).strip():
            term = str(search).strip()
            filter_doc["$or"] = [
                {"_id": {"$regex": term, "$options": "i"}},
                {"course_name": {"$regex": term, "$options": "i"}},
                {"description": {"$regex": term, "$options": "i"}}
            ]

        # PyMongo find() with sort
        courses = list(self.collection.find(filter_doc).sort("_id", 1))
        return courses

    def count_courses(self, filter_doc=None):
        """Return total course count matching filter using count_documents()."""
        return self.collection.count_documents(filter_doc or {})

    def get_distinct_departments(self):
        """Return distinct department codes using distinct()."""
        return sorted(self.collection.distinct("department"))

    # ==========================================
    # UPDATE Operations
    # ==========================================

    def update_course(self, course_id, data):
        """
        Update course details using update_one() with $set.
        """
        if not course_id:
            return {"success": False, "errors": {"_id": "Course code required."}, "status_code": 400}

        code = str(course_id).strip().upper()
        existing = self.collection.find_one({"_id": code})
        if not existing:
            return {"success": False, "errors": {"_id": f"Course '{code}' not found."}, "status_code": 404}

        is_valid, errors, cleaned = validate_course_payload(data, is_update=True)
        if not is_valid:
            return {"success": False, "errors": errors, "status_code": 400}

        set_fields = {}
        for key in ["course_name", "credits", "department", "description"]:
            if key in cleaned:
                set_fields[key] = cleaned[key]

        set_fields["updated_at"] = datetime.now(timezone.utc)

        try:
            # PyMongo update_one()
            res = self.collection.update_one({"_id": code}, {"$set": set_fields})
            updated_doc = self.collection.find_one({"_id": code})
            return {
                "success": True,
                "modified_count": res.modified_count,
                "course": updated_doc,
                "status_code": 200
            }
        except PyMongoError as exc:
            logger.error("Error updating course %s: %s", code, exc)
            return {"success": False, "errors": {"database": str(exc)}, "status_code": 500}

    # ==========================================
    # DELETE Operations
    # ==========================================

    def delete_course(self, course_id):
        """
        Delete a course by course code using delete_one().
        Checks if any students currently have marks recorded for this course.
        """
        if not course_id:
            return {"success": False, "message": "Course code required.", "status_code": 400}

        code = str(course_id).strip().upper()
        existing = self.collection.find_one({"_id": code})
        if not existing:
            return {"success": False, "message": f"Course '{code}' not found.", "status_code": 404}

        # Check if any students reference this course in their embedded marks document
        enrolled_count = self.db["students"].count_documents({f"marks.{code}": {"$exists": True}})
        if enrolled_count > 0:
            return {
                "success": False,
                "message": f"Cannot delete course '{code}' because {enrolled_count} student(s) have marks recorded for it.",
                "enrolled_students": enrolled_count,
                "status_code": 400
            }

        # PyMongo delete_one()
        res = self.collection.delete_one({"_id": code})
        return {
            "success": True,
            "message": f"Course '{code}' deleted successfully.",
            "status_code": 200
        }
