"""
Routes package initialization and BSON JSON serialization utilities.
"""

from datetime import datetime, date
from bson import ObjectId


def serialize_doc(doc):
    """
    Recursively converts BSON / MongoDB types to standard JSON-serializable Python types.
    Handles datetime, ObjectId, and nested dicts/lists.
    """
    if doc is None:
        return None
    if isinstance(doc, (datetime, date)):
        return doc.isoformat()
    if isinstance(doc, ObjectId):
        return str(doc)
    if isinstance(doc, dict):
        return {k: serialize_doc(v) for k, v in doc.items()}
    if isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
    return doc
