"""
Configuration settings for the Student Performance Analytics System.
Supports development, testing, and production environments via environment variables.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / ".env")


class Config:
    """Base application configuration."""
    SECRET_KEY = os.getenv("SECRET_KEY", "cse494-default-secret-key-change-in-production")
    
    # MongoDB settings
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "student_analytics")
    
    # MongoDB connection timeouts (milliseconds)
    MONGODB_CONNECT_TIMEOUT_MS = int(os.getenv("MONGODB_CONNECT_TIMEOUT_MS", 5000))
    MONGODB_SERVER_SELECTION_TIMEOUT_MS = int(os.getenv("MONGODB_SERVER_SELECTION_TIMEOUT_MS", 5000))
    
    # Web server settings
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", 5001))
    DEBUG = os.getenv("FLASK_DEBUG", "1") == "1"
    TESTING = False
    
    # Pagination defaults
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 100


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True


class TestingConfig(Config):
    """Testing environment configuration."""
    TESTING = True
    DEBUG = False
    DATABASE_NAME = os.getenv("TEST_DATABASE_NAME", "student_analytics_test")


class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}


def get_config(env_name=None):
    """Return the configuration class for the given environment name."""
    if not env_name:
        env_name = os.getenv("FLASK_ENV", "development").lower()
    return config_by_name.get(env_name, DevelopmentConfig)
