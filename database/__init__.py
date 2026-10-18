"""
Database package initialization.
Exports connection utilities, schema validators, indexes, and seed functions.
"""

from database.connection import (
    get_mongo_client,
    get_database,
    verify_connection,
    close_connection
)
from database.validators import (
    STUDENT_JSON_SCHEMA,
    COURSE_JSON_SCHEMA,
    apply_collection_validators,
    validate_student_payload,
    validate_course_payload
)
from database.indexes import (
    create_all_indexes,
    list_indexes_info,
    drop_custom_indexes
)
from database.seed import (
    seed_database,
    SAMPLE_COURSES,
    SAMPLE_STUDENTS
)

__all__ = [
    "get_mongo_client",
    "get_database",
    "verify_connection",
    "close_connection",
    "STUDENT_JSON_SCHEMA",
    "COURSE_JSON_SCHEMA",
    "apply_collection_validators",
    "validate_student_payload",
    "validate_course_payload",
    "create_all_indexes",
    "list_indexes_info",
    "drop_custom_indexes",
    "seed_database",
    "SAMPLE_COURSES",
    "SAMPLE_STUDENTS"
]
