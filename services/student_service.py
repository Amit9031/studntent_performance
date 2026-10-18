"""
Student Data Access and Business Logic Service.

Encapsulates complete CRUD operations for the 'students' collection using PyMongo.
Demonstrates PyMongo methods: insert_one, insert_many, find, find_one,
update_one, update_many, delete_one, delete_many, count_documents, distinct.
"""

from datetime import datetime, timezone
import logging
from pymongo.errors import DuplicateKeyError, PyMongoError
from database.connection import get_database
from database.validators import validate_student_payload

logger = logging.getLogger(__name__)


class StudentService:
    """Service handling all student-related database operations."""

    def __init__(self, db=None):
        self._db = db

    @property
    def db(self):
        return self._db if self._db is not None else get_database()

    @property
    def collection(self):
        return self.db["students"]

    # ==========================================
    # CREATE Operations
    # ==========================================

    def create_student(self, data):
        """
        Create a new student document.
        Validates payload, prevents duplicate _id or email, sets BSON timestamps.
        """
        is_valid, errors, cleaned = validate_student_payload(data, is_update=False)
        if not is_valid:
            return {"success": False, "errors": errors, "status_code": 400}

        cleaned["created_at"] = datetime.now(timezone.utc)
        cleaned["updated_at"] = datetime.now(timezone.utc)

        try:
            # PyMongo insert_one()
            result = self.collection.insert_one(cleaned)
            logger.info("Inserted new student with _id: %s", result.inserted_id)
            return {
                "success": True,
                "student_id": result.inserted_id,
                "student": cleaned,
                "status_code": 201
            }
        except DuplicateKeyError as exc:
            err_msg = str(exc)
            if "uniq_idx_email" in err_msg or "email" in err_msg:
                return {
                    "success": False,
                    "errors": {"email": f"Email '{cleaned.get('email')}' is already registered to another student."},
                    "status_code": 409
                }
            return {
                "success": False,
                "errors": {"_id": f"Student ID '{cleaned.get('_id')}' already exists in the system."},
                "status_code": 409
            }
        except PyMongoError as exc:
            logger.error("Database error inserting student: %s", exc)
            return {
                "success": False,
                "errors": {"database": str(exc)},
                "status_code": 500
            }

    def bulk_create_students(self, students_list):
        """
        Insert multiple student documents using insert_many().
        Demonstrates batch insertion with error handling.
        """
        validated_students = []
        for item in students_list:
            is_valid, _, cleaned = validate_student_payload(item, is_update=False)
            if is_valid:
                cleaned["created_at"] = datetime.now(timezone.utc)
                cleaned["updated_at"] = datetime.now(timezone.utc)
                validated_students.append(cleaned)

        if not validated_students:
            return {"success": False, "inserted_count": 0, "message": "No valid records provided"}

        try:
            # PyMongo insert_many() with ordered=False to continue on individual errors
            result = self.collection.insert_many(validated_students, ordered=False)
            return {"success": True, "inserted_count": len(result.inserted_ids)}
        except PyMongoError as exc:
            logger.warning("Partial batch insert error: %s", exc)
            return {"success": False, "error": str(exc)}

    # ==========================================
    # READ Operations
    # ==========================================

    def get_student_by_id(self, student_id):
        """
        Retrieve a single student by numeric ID using find_one().
        """
        try:
            numeric_id = int(student_id)
        except (ValueError, TypeError):
            return None

        # PyMongo find_one() with parameterized query filter
        return self.collection.find_one({"_id": numeric_id})

    def get_students(self, query=None, department=None, semester=None,
                     min_attendance=None, max_attendance=None,
                     page=1, page_size=10, sort_by="_id", sort_order=1):
        """
        Retrieve paginated student records with advanced filtering.
        Supports text search, department, semester, and attendance range filters.
        """
        filter_doc = {}

        # Department filter
        if department and str(department).strip():
            filter_doc["department"] = str(department).strip().upper()

        # Semester filter
        if semester is not None and str(semester).strip() != "":
            try:
                filter_doc["semester"] = int(semester)
            except ValueError:
                pass

        # Attendance range filter
        att_range = {}
        if min_attendance is not None and str(min_attendance).strip() != "":
            try:
                att_range["$gte"] = float(min_attendance)
            except ValueError:
                pass
        if max_attendance is not None and str(max_attendance).strip() != "":
            try:
                att_range["$lte"] = float(max_attendance)
            except ValueError:
                pass
        if att_range:
            filter_doc["attendance"] = att_range

        # Search term query (by numeric ID, regex name, or regex email)
        if query and str(query).strip():
            term = str(query).strip()
            # If search term is all digits, match exact ID or regex name/email
            if term.isdigit():
                filter_doc["$or"] = [
                    {"_id": int(term)},
                    {"name": {"$regex": term, "$options": "i"}},
                    {"email": {"$regex": term, "$options": "i"}}
                ]
            else:
                filter_doc["$or"] = [
                    {"name": {"$regex": term, "$options": "i"}},
                    {"email": {"$regex": term, "$options": "i"}}
                ]

        # Calculate pagination bounds
        page = max(1, int(page))
        page_size = max(1, min(100, int(page_size)))
        skip_count = (page - 1) * page_size

        # PyMongo count_documents()
        total_count = self.collection.count_documents(filter_doc)
        total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 1

        # PyMongo find() with sort(), skip(), and limit()
        cursor = self.collection.find(filter_doc).sort(sort_by, sort_order).skip(skip_count).limit(page_size)
        students = list(cursor)

        return {
            "students": students,
            "total": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "filter": filter_doc
        }

    def get_distinct_departments(self):
        """Return distinct department codes using PyMongo distinct()."""
        return sorted(self.collection.distinct("department"))

    def get_distinct_semesters(self):
        """Return distinct semester numbers using PyMongo distinct()."""
        return sorted(self.collection.distinct("semester"))

    # ==========================================
    # UPDATE Operations
    # ==========================================

    def update_student(self, student_id, data):
        """
        Update an existing student record using PyMongo update_one() and $set.
        Prevents duplicate email on update.
        """
        try:
            numeric_id = int(student_id)
        except (ValueError, TypeError):
            return {"success": False, "errors": {"_id": "Invalid student ID."}, "status_code": 400}

        # Check existing
        existing = self.collection.find_one({"_id": numeric_id})
        if not existing:
            return {"success": False, "errors": {"_id": f"Student with ID {numeric_id} not found."}, "status_code": 404}

        is_valid, errors, cleaned = validate_student_payload(data, is_update=True)
        if not is_valid:
            return {"success": False, "errors": errors, "status_code": 400}

        # Prepare update operations
        set_fields = {}
        for key, value in cleaned.items():
            if key != "_id":
                set_fields[key] = value

        set_fields["updated_at"] = datetime.now(timezone.utc)

        update_query = {"$set": set_fields}

        try:
            # PyMongo update_one()
            res = self.collection.update_one({"_id": numeric_id}, update_query)
            updated_doc = self.collection.find_one({"_id": numeric_id})
            return {
                "success": True,
                "modified_count": res.modified_count,
                "student": updated_doc,
                "status_code": 200
            }
        except DuplicateKeyError:
            return {
                "success": False,
                "errors": {"email": f"Email '{cleaned.get('email')}' is already registered to another student."},
                "status_code": 409
            }
        except PyMongoError as exc:
            logger.error("Database error updating student %s: %s", numeric_id, exc)
            return {"success": False, "errors": {"database": str(exc)}, "status_code": 500}

    def update_attendance(self, student_id, new_attendance):
        """
        Update student attendance using $set.
        """
        try:
            numeric_id = int(student_id)
            att_val = float(new_attendance)
            if att_val < 0 or att_val > 100:
                return {"success": False, "error": "Attendance must be between 0 and 100."}
        except (ValueError, TypeError):
            return {"success": False, "error": "Invalid attendance value or ID."}

        res = self.collection.update_one(
            {"_id": numeric_id},
            {"$set": {"attendance": round(att_val, 2), "updated_at": datetime.now(timezone.utc)}}
        )
        return {"success": res.matched_count > 0, "modified_count": res.modified_count}

    def add_or_update_course_mark(self, student_id, course_code, mark):
        """
        Add or modify a mark for a specific course using dot notation in $set.
        Demonstrates updating embedded document fields: marks.<course_code>.
        """
        try:
            numeric_id = int(student_id)
            score = float(mark)
            if score < 0 or score > 100:
                return {"success": False, "error": "Mark must be between 0 and 100."}
        except (ValueError, TypeError):
            return {"success": False, "error": "Invalid mark or student ID."}

        course_key = str(course_code).strip().upper()
        if not course_key:
            return {"success": False, "error": "Course code is required."}

        # PyMongo update_one() with dot notation for embedded document key
        res = self.collection.update_one(
            {"_id": numeric_id},
            {
                "$set": {
                    f"marks.{course_key}": round(score, 2),
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        return {"success": res.matched_count > 0, "modified_count": res.modified_count}

    def add_skills(self, student_id, skills_list):
        """
        Add new skills to the student's skills array without duplicates using $addToSet.
        Demonstrates PyMongo array update operator $addToSet with $each.
        """
        try:
            numeric_id = int(student_id)
        except (ValueError, TypeError):
            return {"success": False, "error": "Invalid student ID."}

        if not isinstance(skills_list, list):
            skills_list = [str(skills_list).strip()]
        cleaned_skills = [str(s).strip() for s in skills_list if str(s).strip()]

        if not cleaned_skills:
            return {"success": False, "error": "No valid skills provided."}

        # PyMongo update_one() using $addToSet to avoid duplicates in array
        res = self.collection.update_one(
            {"_id": numeric_id},
            {
                "$addToSet": {"skills": {"$each": cleaned_skills}},
                "$set": {"updated_at": datetime.now(timezone.utc)}
            }
        )
        return {"success": res.matched_count > 0, "modified_count": res.modified_count}

    def increment_attendance_for_department(self, department, bonus_percentage=2.0):
        """
        Demonstrates update_many() and $inc operator.
        Safely increments attendance for all students in a department, capped at 100.
        """
        # PyMongo update_many() with $inc
        res = self.collection.update_many(
            {"department": str(department).upper(), "attendance": {"$lte": 100 - bonus_percentage}},
            {
                "$inc": {"attendance": bonus_percentage},
                "$set": {"updated_at": datetime.now(timezone.utc)}
            }
        )
        return {"matched_count": res.matched_count, "modified_count": res.modified_count}

    # ==========================================
    # DELETE Operations
    # ==========================================

    def delete_student(self, student_id):
        """
        Delete a student by numeric ID using delete_one().
        Returns meaningful status if student does not exist.
        """
        try:
            numeric_id = int(student_id)
        except (ValueError, TypeError):
            return {"success": False, "message": "Invalid student ID format.", "status_code": 400}

        # PyMongo delete_one()
        res = self.collection.delete_one({"_id": numeric_id})
        if res.deleted_count == 0:
            return {"success": False, "message": f"Student with ID {numeric_id} was not found.", "status_code": 404}

        logger.info("Deleted student with ID: %s", numeric_id)
        return {"success": True, "message": f"Student {numeric_id} deleted successfully.", "status_code": 200}

    def delete_students_by_department(self, department):
        """
        Demonstrates delete_many() by removing students matching a query filter.
        """
        res = self.collection.delete_many({"department": str(department).upper()})
        return {"deleted_count": res.deleted_count}
