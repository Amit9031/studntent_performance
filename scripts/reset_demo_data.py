"""
Safe Demo Data Reset Script for Student Performance Analytics.

Safely purges ONLY the designated 'courses' and 'students' collections in the project
database and repopulates them with the verified deterministic sample dataset.
NEVER touches other collections or unrelated databases.
Usage: python scripts/reset_demo_data.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.connection import get_database
from database.seed import seed_database

def main():
    print("=" * 60)
    print("Safe Demo Data Reset - Student Performance Analytics")
    print("=" * 60)

    db = get_database()
    print(f"Target Database: {db.name}")
    print("Notice: Only 'students' and 'courses' collections will be refreshed.")

    summary = seed_database(db, drop_existing=True)

    print("\nReset Summary:")
    print(f"  - Database: {summary['database']}")
    print(f"  - Total Courses: {summary['courses_total']}")
    print(f"  - Total Students: {summary['students_total']}")
    print("\nDatabase has been successfully restored to initial demo state.")
    print("=" * 60)

if __name__ == "__main__":
    main()
