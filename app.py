"""
Student Performance Analytics System - Main Application Entrypoint.

Flask web application integrating PyMongo, MongoDB Aggregation Framework,
and Scikit-Learn predictive analytics for CSE494 coursework.
"""

import os
import logging
from flask import Flask, render_template, jsonify, request
from config import get_config
from database.connection import verify_connection, close_connection, get_database
from routes.dashboard import dashboard_bp
from routes.students import students_bp
from routes.courses import courses_bp
from routes.analytics import analytics_bp

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("app")


def create_app(config_name=None):
    """Application factory for initializing the Flask app with configurations and blueprints."""
    app = Flask(__name__)
    config_obj = get_config(config_name)
    app.config.from_object(config_obj)

    # Verify MongoDB connection
    with app.app_context():
        is_connected, err = verify_connection()
        if is_connected:
            logger.info("MongoDB connection verified successfully on database: %s", config_obj.DATABASE_NAME)
        else:
            logger.warning("MongoDB is currently unreachable: %s", err)

    # Register blueprints
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(analytics_bp)

    # Teardown database resources
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        pass  # MongoClient automatically maintains connection pool

    # Custom Jinja2 Filters
    @app.template_filter("round2")
    def filter_round2(val):
        try:
            return f"{float(val):.2f}"
        except (ValueError, TypeError):
            return "0.00"

    @app.template_filter("risk_badge_class")
    def filter_risk_badge(risk_level):
        if "High" in str(risk_level):
            return "badge-danger"
        elif "Moderate" in str(risk_level):
            return "badge-warning"
        return "badge-success"

    # Global Error Handlers (Prevents leaking stack traces or credentials)
    @app.errorhandler(404)
    def page_not_found(e):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Resource not found", "status_code": 404}), 404
        return render_template("base.html", error_title="404 - Page Not Found", error_message="The requested page could not be located."), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        logger.error("Internal Server Error: %s", e)
        if request.path.startswith("/api/"):
            return jsonify({"error": "An internal server error occurred.", "status_code": 500}), 500
        return render_template("base.html", error_title="500 - Server Error", error_message="An unexpected server error occurred. Please try again."), 500

    @app.errorhandler(400)
    def bad_request(e):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Bad request", "status_code": 400}), 400
        return render_template("base.html", error_title="400 - Bad Request", error_message="The request was invalid."), 400

    return app


if __name__ == "__main__":
    config = get_config()
    app = create_app()
    print("=" * 70)
    print("Student Performance Analytics System (CSE494)")
    print(f"Server starting on http://{config.HOST}:{config.PORT}")
    print(f"MongoDB Target Database: {config.DATABASE_NAME}")
    print("=" * 70)
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
