"""
MongoDB Index Definitions and Management.

Implements single-field, compound, unique, and text indexes for query optimization
and demonstrates how indexes improve search and filtering performance in MongoDB.
"""

import logging
from pymongo import ASCENDING, DESCENDING, TEXT
from pymongo.errors import PyMongoError

logger = logging.getLogger(__name__)


def create_all_indexes(db):
    """
    Create recommended indexes on 'students' and 'courses' collections.
    Returns a dictionary of created index names for each collection.
    """
    results = {"students": [], "courses": []}

    try:
        students = db["students"]

        # 1. Unique index on email: enforces uniqueness at the database engine level
        idx_email = students.create_index(
            [("email", ASCENDING)],
            unique=True,
            name="uniq_idx_email"
        )
        results["students"].append(idx_email)
        logger.info("Created unique index on students.email: %s", idx_email)

        # 2. Single-field index on department: accelerates filtering by department
        idx_dept = students.create_index(
            [("department", ASCENDING)],
            name="idx_department"
        )
        results["students"].append(idx_dept)
        logger.info("Created single-field index on students.department: %s", idx_dept)

        # 3. Single-field index on semester: accelerates semester queries and aggregations
        idx_sem = students.create_index(
            [("semester", ASCENDING)],
            name="idx_semester"
        )
        results["students"].append(idx_sem)
        logger.info("Created single-field index on students.semester: %s", idx_sem)

        # 4. Compound index on department and attendance:
        # Optimizes combined queries like: find({"department": "CSE"}).sort("attendance", -1)
        idx_dept_att = students.create_index(
            [("department", ASCENDING), ("attendance", DESCENDING)],
            name="idx_dept_attendance"
        )
        results["students"].append(idx_dept_att)
        logger.info("Created compound index on students (department, attendance): %s", idx_dept_att)

        # 5. Text index on name and email: powers keyword search across student profiles
        idx_text = students.create_index(
            [("name", TEXT), ("email", TEXT)],
            name="text_idx_name_email"
        )
        results["students"].append(idx_text)
        logger.info("Created text index on students (name, email): %s", idx_text)

        # Courses collection indexes
        courses = db["courses"]
        idx_course_dept = courses.create_index(
            [("department", ASCENDING)],
            name="idx_course_dept"
        )
        results["courses"].append(idx_course_dept)
        logger.info("Created index on courses.department: %s", idx_course_dept)

    except PyMongoError as exc:
        logger.error("Error creating indexes: %s", exc)
        raise

    return results


def list_indexes_info(db):
    """List detailed information about all indexes on students and courses collections."""
    info = {}
    for coll_name in ["students", "courses"]:
        if coll_name in db.list_collection_names():
            coll = db[coll_name]
            info[coll_name] = [
                {
                    "name": idx.get("name"),
                    "key": list(idx.get("key", {}).items()),
                    "unique": idx.get("unique", False)
                }
                for idx in coll.list_indexes()
            ]
        else:
            info[coll_name] = []
    return info


def drop_custom_indexes(db, collection_name="students"):
    """
    Drop all indexes except the default '_id_' index on the specified collection.
    Useful for running unindexed vs indexed performance benchmarks.
    """
    coll = db[collection_name]
    for idx in coll.list_indexes():
        idx_name = idx["name"]
        if idx_name != "_id_":
            coll.drop_index(idx_name)
            logger.info("Dropped index '%s' on collection '%s'", idx_name, collection_name)
