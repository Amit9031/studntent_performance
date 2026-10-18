"""
Realistic Deterministic Sample Data Generator for Student Performance Analytics.

Populates the 'courses' and 'students' collections with realistic academic records
covering diverse departments, semesters, skill sets, top performers, and at-risk students.
"""

from datetime import datetime, timezone
import logging
from pymongo.errors import PyMongoError
from database.validators import apply_collection_validators
from database.indexes import create_all_indexes

logger = logging.getLogger(__name__)

# Standard academic courses for CSE and related engineering disciplines
SAMPLE_COURSES = [
    {
        "_id": "CSE494",
        "course_name": "Intelligent NoSQL Databases",
        "credits": 4,
        "department": "CSE",
        "description": "MongoDB Architecture, Aggregation Framework, Indexing, and Document Modeling.",
        "created_at": datetime(2025, 8, 1, 9, 0, 0, tzinfo=timezone.utc)
    },
    {
        "_id": "CSE401",
        "course_name": "Database Management Systems",
        "credits": 4,
        "department": "CSE",
        "description": "Relational Models, Normalization, SQL, Transactions, and ACID Properties.",
        "created_at": datetime(2025, 8, 1, 9, 0, 0, tzinfo=timezone.utc)
    },
    {
        "_id": "CSE402",
        "course_name": "Computer Networks",
        "credits": 3,
        "department": "CSE",
        "description": "OSI & TCP/IP stack, routing protocols, socket programming, and network security.",
        "created_at": datetime(2025, 8, 1, 9, 0, 0, tzinfo=timezone.utc)
    },
    {
        "_id": "CSE403",
        "course_name": "Operating Systems",
        "credits": 4,
        "department": "CSE",
        "description": "Process scheduling, concurrency, virtual memory, file systems, and deadlocks.",
        "created_at": datetime(2025, 8, 1, 9, 0, 0, tzinfo=timezone.utc)
    },
    {
        "_id": "CSE405",
        "course_name": "Machine Learning",
        "credits": 4,
        "department": "CSE",
        "description": "Supervised, unsupervised algorithms, evaluation metrics, and neural networks.",
        "created_at": datetime(2025, 8, 1, 9, 0, 0, tzinfo=timezone.utc)
    },
    {
        "_id": "IT301",
        "course_name": "Web Application Architecture",
        "credits": 3,
        "department": "IT",
        "description": "Modern full-stack web architecture, REST APIs, microservices, and frontends.",
        "created_at": datetime(2025, 8, 1, 9, 0, 0, tzinfo=timezone.utc)
    },
    {
        "_id": "ECE204",
        "course_name": "Digital Signal Processing",
        "credits": 4,
        "department": "ECE",
        "description": "Discrete Fourier transforms, filter design, sampling theory, and applications.",
        "created_at": datetime(2025, 8, 1, 9, 0, 0, tzinfo=timezone.utc)
    }
]

# 35 Realistic student records covering top performers, average students, and at-risk students
SAMPLE_STUDENTS = [
    # Top Performers (Avg >= 90)
    {
        "_id": 101,
        "name": "Amit Ranjan",
        "email": "amit.ranjan@example.com",
        "department": "CSE",
        "semester": 7,
        "attendance": 94.5,
        "marks": {"CSE494": 96.0, "CSE401": 92.0, "CSE402": 90.0, "CSE405": 95.0},
        "skills": ["Python", "MongoDB", "Machine Learning", "System Design"],
        "created_at": datetime(2025, 8, 15, 10, 0, 0, tzinfo=timezone.utc)
    },
    {
        "_id": 102,
        "name": "Priya Sharma",
        "email": "priya.sharma@example.com",
        "department": "CSE",
        "semester": 7,
        "attendance": 98.0,
        "marks": {"CSE494": 98.0, "CSE401": 95.0, "CSE402": 92.0, "CSE403": 94.0},
        "skills": ["Python", "MongoDB", "Data Structures", "Docker"],
        "created_at": datetime(2025, 8, 15, 10, 5, 0, tzinfo=timezone.utc)
    },
    {
        "_id": 103,
        "name": "Rohan Verma",
        "email": "rohan.verma@example.com",
        "department": "IT",
        "semester": 6,
        "attendance": 92.0,
        "marks": {"IT301": 91.0, "CSE401": 89.0, "CSE402": 92.0},
        "skills": ["JavaScript", "React", "Node.js", "MongoDB"],
        "created_at": datetime(2025, 8, 15, 10, 10, 0, tzinfo=timezone.utc)
    },
    {
        "_id": 104,
        "name": "Ananya Gupta",
        "email": "ananya.gupta@example.com",
        "department": "AIDS",
        "semester": 5,
        "attendance": 96.0,
        "marks": {"CSE405": 97.0, "CSE494": 93.0, "CSE401": 91.0},
        "skills": ["Python", "PyTorch", "NLP", "Machine Learning"],
        "created_at": datetime(2025, 8, 15, 10, 15, 0, tzinfo=timezone.utc)
    },
    {
        "_id": 105,
        "name": "Karthik Nair",
        "email": "karthik.nair@example.com",
        "department": "ECE",
        "semester": 6,
        "attendance": 91.5,
        "marks": {"ECE204": 94.0, "CSE401": 88.0, "CSE402": 90.0},
        "skills": ["MATLAB", "Embedded C", "Signal Processing", "Python"],
        "created_at": datetime(2025, 8, 15, 10, 20, 0, tzinfo=timezone.utc)
    },

    # Good Performers (75 <= Avg < 90)
    {
        "_id": 106,
        "name": "Sneha Reddy",
        "email": "sneha.reddy@example.com",
        "department": "CSE",
        "semester": 7,
        "attendance": 88.0,
        "marks": {"CSE494": 85.0, "CSE401": 84.0, "CSE402": 82.0, "CSE405": 87.0},
        "skills": ["Java", "Spring Boot", "SQL", "MongoDB"],
        "created_at": datetime(2025, 8, 15, 10, 25, 0, tzinfo=timezone.utc)
    },
    {
        "_id": 107,
        "name": "Vikas Patel",
        "email": "vikas.patel@example.com",
        "department": "IT",
        "semester": 6,
        "attendance": 86.5,
        "marks": {"IT301": 84.0, "CSE401": 79.0, "CSE402": 81.0},
        "skills": ["Python", "Flask", "PostgreSQL", "HTML/CSS"],
        "created_at": datetime(2025, 8, 15, 10, 30, 0, tzinfo=timezone.utc)
    },
    {
        "_id": 108,
        "name": "Divya Krishnan",
        "email": "divya.krishnan@example.com",
        "department": "CSE",
        "semester": 5,
        "attendance": 89.0,
        "marks": {"CSE401": 86.0, "CSE403": 83.0, "CSE402": 85.0},
        "skills": ["C++", "Algorithms", "Linux", "Git"],
        "created_at": datetime(2025, 8, 15, 10, 35, 0, tzinfo=timezone.utc)
    },
    {
        "_id": 109,
        "name": "Arjun Singhania",
        "email": "arjun.singhania@example.com",
        "department": "ECE",
        "semester": 4,
        "attendance": 84.0,
        "marks": {"ECE204": 80.0, "CSE401": 78.0, "CSE402": 82.0},
        "skills": ["Verilog", "C", "Microcontrollers"],
        "created_at": datetime(2025, 8, 15, 10, 40, 0, tzinfo=timezone.utc)
    },
    {
        "_id": 110,
        "name": "Meera Joshi",
        "email": "meera.joshi@example.com",
        "department": "AIDS",
        "semester": 5,
        "attendance": 87.0,
        "marks": {"CSE405": 88.0, "CSE494": 82.0, "CSE401": 85.0},
        "skills": ["Python", "TensorFlow", "Pandas", "Scikit-Learn"],
        "created_at": datetime(2025, 8, 15, 10, 45, 0, tzinfo=timezone.utc)
    },
    {
        "_id": 111,
        "name": "Tanmay Deshmukh",
        "email": "tanmay.deshmukh@example.com",
        "department": "ME",
        "semester": 4,
        "attendance": 82.0,
        "marks": {"CSE401": 76.0, "CSE402": 79.0},
        "skills": ["AutoCAD", "SolidWorks", "Python Basics"],
        "created_at": datetime(2025, 8, 15, 10, 50, 0, tzinfo=timezone.utc)
    },
    {
        "_id": 112,
        "name": "Bhavna Iyer",
        "email": "bhavna.iyer@example.com",
        "department": "CSE",
        "semester": 3,
        "attendance": 90.0,
        "marks": {"CSE401": 85.0, "CSE403": 88.0},
        "skills": ["Python", "Java", "Object Oriented Design"],
        "created_at": datetime(2025, 8, 15, 10, 55, 0, tzinfo=timezone.utc)
    },
    {
        "_id": 113,
        "name": "Siddharth Rao",
        "email": "siddharth.rao@example.com",
        "department": "IT",
        "semester": 7,
        "attendance": 85.0,
        "marks": {"IT301": 86.0, "CSE494": 84.0, "CSE402": 80.0},
        "skills": ["React", "Express", "MongoDB", "TailwindCSS"],
        "created_at": datetime(2025, 8, 15, 11, 0, 0, tzinfo=timezone.utc)
    },
    {
        "_id": 114,
        "name": "Pooja Hegde",
        "email": "pooja.hegde@example.com",
        "department": "CSE",
        "semester": 7,
        "attendance": 89.5,
        "marks": {"CSE494": 88.0, "CSE401": 82.0, "CSE405": 85.0},
        "skills": ["Python", "Data Analysis", "SQL", "Tableau"],
        "created_at": datetime(2025, 8, 15, 11, 5, 0, tzinfo=timezone.utc)
    },
    {
        "_id": 115,
        "name": "Nikhil Agarwal",
        "email": "nikhil.agarwal@example.com",
        "department": "ECE",
        "semester": 6,
        "attendance": 83.0,
        "marks": {"ECE204": 81.0, "CSE401": 77.0, "CSE402": 76.0},
        "skills": ["VLSI", "C++", "MATLAB"],
        "created_at": datetime(2025, 8, 15, 11, 10, 0, tzinfo=timezone.utc)
    },

    # Average Performers (60 <= Avg < 75)
    {
        "_id": 116,
        "name": "Deepak Choudhary",
        "email": "deepak.choudhary@example.com",
        "department": "CSE",
        "semester": 5,
        "attendance": 80.0,
        "marks": {"CSE401": 68.0, "CSE402": 72.0, "CSE403": 65.0},
        "skills": ["Java", "HTML", "CSS"],
        "created_at": datetime(2025, 8, 15, 11, 15, 0, tzinfo=timezone.utc)
    },
    {
        "_id": 117,
        "name": "Ritu Saxena",
        "email": "ritu.saxena@example.com",
        "department": "IT",
        "semester": 4,
        "attendance": 78.5,
        "marks": {"IT301": 70.0, "CSE401": 64.0},
        "skills": ["Python", "PHP", "MySQL"],
        "created_at": datetime(2025, 8, 15, 11, 20, 0, tzinfo=timezone.utc)
    },
    {
        "_id": 118,
        "name": "Harish Menon",
        "email": "harish.menon@example.com",
        "department": "ME",
        "semester": 5,
        "attendance": 79.0,
        "marks": {"CSE401": 65.0, "CSE402": 67.0},
        "skills": ["Thermodynamics", "Python Basics"],
        "created_at": datetime(2025, 8, 15, 11, 25, 0, tzinfo=timezone.utc)
    },
    {
        "_id": 119,
        "name": "Akanksha Roy",
        "email": "akanksha.roy@example.com",
        "department": "CSE",
        "semester": 7,
        "attendance": 81.0,
        "marks": {"CSE494": 74.0, "CSE401": 71.0, "CSE402": 69.0, "CSE405": 72.0},
        "skills": ["Python", "MongoDB", "HTML/CSS"],
        "created_at": datetime(2025, 8, 15, 11, 30, 0, tzinfo=timezone.utc)
    },
    {
        "_id": 120,
        "name": "Gaurav Bhatt",
        "email": "gaurav.bhatt@example.com",
        "department": "AIDS",
        "semester": 3,
        "attendance": 76.0,
        "marks": {"CSE401": 66.0, "CSE405": 71.0},
        "skills": ["Python", "NumPy", "Statistics"],
        "created_at": datetime(2025, 8, 15, 11, 35, 0, tzinfo=timezone.utc)
    },
    {
        "_id": 121,
        "name": "Kavita Saini",
        "email": "kavita.saini@example.com",
        "department": "ECE",
        "semester": 5,
        "attendance": 77.0,
        "marks": {"ECE204": 73.0, "CSE401": 68.0, "CSE402": 64.0},
        "skills": ["C", "Digital Logic", "Arduino"],
        "created_at": datetime(2025, 8, 15, 11, 40, 0, tzinfo=timezone.utc)
    },
    {
        "_id": 122,
        "name": "Manoj Kumar",
        "email": "manoj.kumar@example.com",
        "department": "IT",
        "semester": 6,
        "attendance": 79.0,
        "marks": {"IT301": 71.0, "CSE402": 66.0, "CSE401": 69.0},
        "skills": ["JavaScript", "Bootstrap", "Git"],
        "created_at": datetime(2025, 8, 15, 11, 45, 0, tzinfo=timezone.utc)
    },
    {
        "_id": 123,
        "name": "Shweta Tiwari",
        "email": "shweta.tiwari@example.com",
        "department": "CSE",
        "semester": 4,
        "attendance": 82.5,
        "marks": {"CSE401": 72.0, "CSE403": 70.0},
        "skills": ["C++", "Java", "SQL"],
        "created_at": datetime(2025, 8, 15, 11, 50, 0, tzinfo=timezone.utc)
    },
    {
        "_id": 124,
        "name": "Abhishek Dubey",
        "email": "abhishek.dubey@example.com",
        "department": "ME",
        "semester": 6,
        "attendance": 75.5,
        "marks": {"CSE401": 63.0, "CSE402": 66.0},
        "skills": ["ANSYS", "Python"],
        "created_at": datetime(2025, 8, 15, 11, 55, 0, tzinfo=timezone.utc)
    },
    {
        "_id": 125,
        "name": "Pallavi Sen",
        "email": "pallavi.sen@example.com",
        "department": "CSE",
        "semester": 7,
        "attendance": 80.5,
        "marks": {"CSE494": 73.0, "CSE401": 69.0, "CSE405": 71.0},
        "skills": ["Python", "Flask", "MongoDB"],
        "created_at": datetime(2025, 8, 15, 12, 0, 0, tzinfo=timezone.utc)
    },

    # At-Risk Students: Low Attendance (< 75%) or Low Marks (< 40)
    {
        "_id": 126,
        "name": "Karan Malhotra",
        "email": "karan.malhotra@example.com",
        "department": "CSE",
        "semester": 7,
        "attendance": 58.0,  # At risk: attendance < 75
        "marks": {"CSE494": 62.0, "CSE401": 55.0, "CSE402": 58.0},
        "skills": ["Python", "Gaming"],
        "created_at": datetime(2025, 8, 15, 12, 5, 0, tzinfo=timezone.utc)
    },
    {
        "_id": 127,
        "name": "Sunil Varma",
        "email": "sunil.varma@example.com",
        "department": "IT",
        "semester": 5,
        "attendance": 48.5,  # At risk: attendance < 75
        "marks": {"IT301": 42.0, "CSE401": 38.0},  # Low marks
        "skills": ["HTML"],
        "created_at": datetime(2025, 8, 15, 12, 10, 0, tzinfo=timezone.utc)
    },
    {
        "_id": 128,
        "name": "Tarun Kapoor",
        "email": "tarun.kapoor@example.com",
        "department": "ECE",
        "semester": 6,
        "attendance": 65.0,  # At risk: attendance < 75
        "marks": {"ECE204": 48.0, "CSE401": 45.0, "CSE402": 51.0},
        "skills": ["Electronics Basics"],
        "created_at": datetime(2025, 8, 15, 12, 15, 0, tzinfo=timezone.utc)
    },
    {
        "_id": 129,
        "name": "Neelam Mishra",
        "email": "neelam.mishra@example.com",
        "department": "CSE",
        "semester": 5,
        "attendance": 85.0,
        "marks": {"CSE401": 34.0, "CSE402": 37.0, "CSE403": 39.0},  # At risk: avg marks < 40
        "skills": ["Java Basics"],
        "created_at": datetime(2025, 8, 15, 12, 20, 0, tzinfo=timezone.utc)
    },
    {
        "_id": 130,
        "name": "Rajesh Goswami",
        "email": "rajesh.goswami@example.com",
        "department": "AIDS",
        "semester": 3,
        "attendance": 52.0,  # At risk: attendance < 75
        "marks": {"CSE401": 36.0, "CSE405": 38.0},  # At risk: avg marks < 40
        "skills": ["Python Basics"],
        "created_at": datetime(2025, 8, 15, 12, 25, 0, tzinfo=timezone.utc)
    },
    {
        "_id": 131,
        "name": "Aman Singhal",
        "email": "aman.singhal@example.com",
        "department": "ME",
        "semester": 5,
        "attendance": 62.0,  # At risk: attendance < 75
        "marks": {"CSE401": 48.0, "CSE402": 50.0},
        "skills": ["CAD"],
        "created_at": datetime(2025, 8, 15, 12, 30, 0, tzinfo=timezone.utc)
    },
    {
        "_id": 132,
        "name": "Simran Kaur",
        "email": "simran.kaur@example.com",
        "department": "CSE",
        "semester": 3,
        "attendance": 68.0,  # At risk: attendance < 75
        "marks": {"CSE401": 56.0, "CSE403": 54.0},
        "skills": ["C Programming", "Linux"],
        "created_at": datetime(2025, 8, 15, 12, 35, 0, tzinfo=timezone.utc)
    },
    {
        "_id": 133,
        "name": "Rohit Pillai",
        "email": "rohit.pillai@example.com",
        "department": "IT",
        "semester": 6,
        "attendance": 64.0,  # At risk: attendance < 75
        "marks": {"IT301": 59.0, "CSE402": 52.0},
        "skills": ["CSS", "Web Basics"],
        "created_at": datetime(2025, 8, 15, 12, 40, 0, tzinfo=timezone.utc)
    },
    {
        "_id": 134,
        "name": "Aditya Chauhan",
        "email": "aditya.chauhan@example.com",
        "department": "ECE",
        "semester": 4,
        "attendance": 70.0,  # At risk: attendance < 75
        "marks": {"ECE204": 38.0, "CSE401": 35.0},  # Low marks & attendance
        "skills": ["Breadboard Circuits"],
        "created_at": datetime(2025, 8, 15, 12, 45, 0, tzinfo=timezone.utc)
    },
    {
        "_id": 135,
        "name": "Varun Sethi",
        "email": "varun.sethi@example.com",
        "department": "CSE",
        "semester": 7,
        "attendance": 71.0,  # At risk: attendance < 75
        "marks": {"CSE494": 55.0, "CSE401": 52.0, "CSE405": 58.0},
        "skills": ["Python", "Git"],
        "created_at": datetime(2025, 8, 15, 12, 50, 0, tzinfo=timezone.utc)
    }
]


def seed_database(db, drop_existing=False):
    """
    Populate the 'courses' and 'students' collections with realistic sample data.
    If drop_existing=True, clears records only in 'courses' and 'students'.
    Applies JSON Schema validation and builds indexes.
    """
    logger.info("Starting database seeding for database: %s", db.name)

    # 1. Apply JSON schema validators
    apply_collection_validators(db)

    # 2. Reset if requested (only designated project collections!)
    if drop_existing:
        logger.info("Dropping existing documents in 'courses' and 'students' collections.")
        db["courses"].delete_many({})
        db["students"].delete_many({})

    # 3. Seed Courses (using upsert by _id to avoid duplicates)
    courses_coll = db["courses"]
    courses_inserted = 0
    courses_updated = 0
    for course in SAMPLE_COURSES:
        res = courses_coll.replace_one({"_id": course["_id"]}, course, upsert=True)
        if res.upserted_id is not None:
            courses_inserted += 1
        elif res.modified_count > 0:
            courses_updated += 1

    # 4. Seed Students (using upsert by _id to avoid duplicates)
    students_coll = db["students"]
    students_inserted = 0
    students_updated = 0
    for student in SAMPLE_STUDENTS:
        res = students_coll.replace_one({"_id": student["_id"]}, student, upsert=True)
        if res.upserted_id is not None:
            students_inserted += 1
        elif res.modified_count > 0:
            students_updated += 1

    # 5. Create all indexes
    create_all_indexes(db)

    summary = {
        "database": db.name,
        "courses_total": courses_coll.count_documents({}),
        "students_total": students_coll.count_documents({}),
        "courses_upserted": courses_inserted,
        "students_upserted": students_inserted
    }
    logger.info("Database seeding completed successfully: %s", summary)
    return summary


if __name__ == "__main__":
    from database.connection import get_database
    logging.basicConfig(level=logging.INFO)
    db = get_database()
    result = seed_database(db, drop_existing=False)
    print("Seed result:", result)
