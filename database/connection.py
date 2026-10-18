"""
Database Connection Manager using PyMongo.

Provides a thread-safe singleton MongoDB client instance, connection verification,
graceful error handling, and resource teardown for the Flask application.
"""

import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from config import get_config

logger = logging.getLogger(__name__)

# Global client cache
_client = None


def get_mongo_client(uri=None, connect_timeout_ms=None, server_selection_timeout_ms=None):
    """
    Get or create a singleton MongoClient instance.
    PyMongo's MongoClient manages an internal connection pool automatically.
    """
    global _client
    if _client is None:
        config = get_config()
        uri = uri or config.MONGODB_URI
        connect_timeout_ms = connect_timeout_ms or config.MONGODB_CONNECT_TIMEOUT_MS
        server_selection_timeout_ms = server_selection_timeout_ms or config.MONGODB_SERVER_SELECTION_TIMEOUT_MS

        try:
            logger.info("Initializing MongoClient with URI: %s", uri.split("@")[-1] if "@" in uri else uri)
            _client = MongoClient(
                uri,
                connectTimeoutMS=connect_timeout_ms,
                serverSelectionTimeoutMS=server_selection_timeout_ms,
                maxPoolSize=50,
                minPoolSize=5,
                appname="StudentPerformanceAnalytics"
            )
        except Exception as exc:
            logger.error("Failed to initialize MongoClient: %s", exc)
            raise

    return _client


def verify_connection(client=None):
    """
    Verify that MongoDB server is reachable using admin ping command.
    Returns (True, None) if successful, or (False, error_message).
    """
    try:
        c = client or get_mongo_client()
        # The ping command is cheap and does not require auth on admin DB
        c.admin.command("ping")
        return True, None
    except (ConnectionFailure, ServerSelectionTimeoutError) as exc:
        msg = f"Could not connect to MongoDB server: {exc}"
        logger.error(msg)
        return False, msg
    except Exception as exc:
        msg = f"Unexpected error while verifying MongoDB connection: {exc}"
        logger.error(msg)
        return False, msg


def get_database(db_name=None, uri=None):
    """
    Retrieve the MongoDB database instance.
    Uses DATABASE_NAME from configuration if db_name is not provided.
    """
    client = get_mongo_client(uri=uri)
    config = get_config()
    target_db_name = db_name or config.DATABASE_NAME
    return client[target_db_name]


def close_connection():
    """Close the global MongoClient connection and reset singleton."""
    global _client
    if _client is not None:
        try:
            logger.info("Closing MongoDB client connection pool.")
            _client.close()
        except Exception as exc:
            logger.warning("Error closing MongoDB client: %s", exc)
        finally:
            _client = None
