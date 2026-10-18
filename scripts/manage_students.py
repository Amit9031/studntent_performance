"""
Interactive Command-Line Tool for Managing Students via Terminal.

Usage:
  python scripts/manage_students.py list [--dept CSE] [--sem 7] [--limit 10]
  python scripts/manage_students.py find <student_id>
  python scripts/manage_students.py add --id 150 --name "Student Name" --email "student@example.com" --dept CSE --sem 6 --att 85.0
  python scripts/manage_students.py remove <student_id>
  python scripts/manage_students.py add-mark --id <student_id> --course <course_code> --mark <score>
"""

import sys
import argparse
from pathlib import Path
from tabulate import tabulate

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.student_service import StudentService
from services.prediction_service import AcademicRiskPredictor


def cmd_list(args):
    service = StudentService()
    res = service.get_students(
        department=args.dept,
        semester=args.sem,
        query=args.query,
        page=1,
        page_size=args.limit
    )

    students = res["students"]
    if not students:
        print("\nNo students found matching your criteria.")
        return

    table_data = []
    for s in students:
        marks_str = ", ".join(f"{k}:{v}" for k, v in s.get("marks", {}).items()) if s.get("marks") else "None"
        skills_str = ", ".join(s.get("skills", [])) if s.get("skills") else "None"
        table_data.append([
            s["_id"],
            s["name"],
            s["email"],
            s["department"],
            f"Sem {s['semester']}",
            f"{s['attendance']}%",
            marks_str,
            skills_str[:30] + ("..." if len(skills_str) > 30 else "")
        ])

    headers = ["ID", "Name", "Email", "Dept", "Sem", "Attendance", "Marks", "Skills"]
    print(f"\nStudents in Database (Showing {len(students)} of {res['total']}):")
    print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))


def cmd_find(args):
    service = StudentService()
    predictor = AcademicRiskPredictor()

    student = service.get_student_by_id(args.id)
    if not student:
        print(f"\n❌ Error: Student with ID {args.id} was not found.")
        return

    print("\n" + "=" * 60)
    print(f"🎓 STUDENT PROFILE: #{student['_id']} - {student['name']}")
    print("=" * 60)
    print(f"  Email:        {student.get('email')}")
    print(f"  Department:   {student.get('department')}")
    print(f"  Semester:     {student.get('semester')}")
    print(f"  Attendance:   {student.get('attendance')}%")
    print(f"  Skills:       {', '.join(student.get('skills', [])) if student.get('skills') else 'None'}")
    print(f"  Created At:   {student.get('created_at')}")

    print("\n📚 Course Marks:")
    if student.get("marks"):
        marks_table = [[k, f"{v} / 100"] for k, v in student["marks"].items()]
        print(tabulate(marks_table, headers=["Course Code", "Mark"], tablefmt="simple"))
    else:
        print("  No course marks recorded.")

    # AI Risk Assessment
    risk_info = predictor.predict_for_student(student)
    rule_eval = risk_info["rule_evaluation"]
    print("\n🧠 Academic Risk Assessment:")
    print(f"  Risk Level:     {rule_eval['risk_level']}")
    print(f"  Reasons:        {', '.join(rule_eval['reasons'])}")
    print(f"  Recommendation: {rule_eval['recommendation']}")
    print("=" * 60)


def cmd_add(args):
    service = StudentService()
    payload = {
        "_id": args.id,
        "name": args.name,
        "email": args.email,
        "department": args.dept,
        "semester": args.sem,
        "attendance": args.att,
        "marks": {},
        "skills": [s.strip() for s in args.skills.split(",")] if args.skills else []
    }

    res = service.create_student(payload)
    if res["success"]:
        print(f"\n✅ Success: Student #{args.id} ('{args.name}') added successfully to MongoDB!")
    else:
        print(f"\n❌ Failed to add student: {res.get('errors')}")


def cmd_remove(args):
    service = StudentService()
    confirm = input(f"Are you sure you want to delete student #{args.id}? (y/n): ") if not args.yes else "y"
    if confirm.lower() != "y":
        print("Deletion canceled.")
        return

    res = service.delete_student(args.id)
    if res["success"]:
        print(f"\n✅ Success: Student #{args.id} deleted from database.")
    else:
        print(f"\n❌ Error: {res.get('message')}")


def cmd_add_mark(args):
    service = StudentService()
    res = service.add_or_update_course_mark(args.id, args.course, args.mark)
    if res["success"]:
        print(f"\n✅ Success: Mark {args.mark} for course '{args.course}' updated for student #{args.id}.")
    else:
        print(f"\n❌ Error: {res.get('error')}")


def main():
    parser = argparse.ArgumentParser(description="Terminal Student Management CLI (MongoDB & PyMongo)")
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # list
    p_list = subparsers.add_parser("list", help="List student records")
    p_list.add_argument("--dept", help="Filter by department (e.g. CSE)")
    p_list.add_argument("--sem", type=int, help="Filter by semester")
    p_list.add_argument("--query", "-q", help="Search by keyword")
    p_list.add_argument("--limit", type=int, default=10, help="Number of records to show")

    # find
    p_find = subparsers.add_parser("find", help="Find single student by ID")
    p_find.add_argument("id", type=int, help="Student ID")

    # add
    p_add = subparsers.add_parser("add", help="Add a new student")
    p_add.add_argument("--id", type=int, required=True, help="Numeric student ID")
    p_add.add_argument("--name", required=True, help="Student full name")
    p_add.add_argument("--email", required=True, help="Student email address")
    p_add.add_argument("--dept", required=True, help="Department (e.g. CSE, IT, ECE)")
    p_add.add_argument("--sem", type=int, required=True, help="Semester (1-12)")
    p_add.add_argument("--att", type=float, required=True, help="Attendance percentage (0-100)")
    p_add.add_argument("--skills", default="", help="Comma-separated skills (e.g. Python,MongoDB)")

    # remove
    p_remove = subparsers.add_parser("remove", help="Remove a student")
    p_remove.add_argument("id", type=int, help="Student ID to delete")
    p_remove.add_argument("-y", "--yes", action="store_true", help="Skip confirmation prompt")

    # add-mark
    p_mark = subparsers.add_parser("add-mark", help="Add or update a mark for a student")
    p_mark.add_argument("--id", type=int, required=True, help="Student ID")
    p_mark.add_argument("--course", required=True, help="Course code (e.g. CSE494)")
    p_mark.add_argument("--mark", type=float, required=True, help="Score (0-100)")

    args = parser.parse_args()

    if args.command == "list":
        cmd_list(args)
    elif args.command == "find":
        cmd_find(args)
    elif args.command == "add":
        cmd_add(args)
    elif args.command == "remove":
        cmd_remove(args)
    elif args.command == "add-mark":
        cmd_add_mark(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
