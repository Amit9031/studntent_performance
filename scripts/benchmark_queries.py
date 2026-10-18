"""
Indexing & Query Optimization Benchmark Script for MongoDB and PyMongo.

Benchmarks query execution before and after creating indexes on a dedicated
synthetic dataset of 10,000 student documents in 'benchmark_students'.
Collects explain("executionStats") metrics including:
- executionTimeMillis
- totalDocsExamined
- totalKeysExamined
- winningPlan stage (COLLSCAN vs IXSCAN)
- nReturned documents
"""

import sys
import random
import time
from pathlib import Path
from tabulate import tabulate

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.connection import get_database

BENCHMARK_COLL = "benchmark_students"
NUM_DOCS = 10000


def generate_benchmark_data(num_docs=NUM_DOCS):
    """Generate deterministic synthetic student documents for benchmarking."""
    random.seed(42)
    departments = ["CSE", "IT", "ECE", "ME", "AIDS"]
    skills_pool = ["Python", "MongoDB", "SQL", "Java", "Docker", "Machine Learning", "C++", "React"]

    docs = []
    for i in range(1, num_docs + 1):
        dept = random.choice(departments)
        sem = random.randint(1, 8)
        attendance = round(random.uniform(40.0, 99.5), 1)
        doc = {
            "_id": 10000 + i,
            "name": f"Benchmark Student {i}",
            "email": f"bench.student{i}@university.edu",
            "department": dept,
            "semester": sem,
            "attendance": attendance,
            "marks": {
                "CSE494": round(random.uniform(35.0, 98.0), 1),
                "CSE401": round(random.uniform(35.0, 98.0), 1),
                "CSE402": round(random.uniform(35.0, 98.0), 1)
            },
            "skills": random.sample(skills_pool, k=random.randint(1, 4))
        }
        docs.append(doc)
    return docs


def extract_stats(explain_res):
    """Safely extracts key execution stats from MongoDB explain output."""
    exec_stats = explain_res.get("executionStats", {})
    query_planner = explain_res.get("queryPlanner", {})
    winning_plan = query_planner.get("winningPlan", {})

    # Detect execution stage
    stage = winning_plan.get("stage", "UNKNOWN")
    if stage in ["FETCH", "SORT"] and "inputStage" in winning_plan:
        stage = f"{stage} -> {winning_plan['inputStage'].get('stage', '')}"

    return {
        "execution_time_ms": exec_stats.get("executionTimeMillis", 0),
        "total_docs_examined": exec_stats.get("totalDocsExamined", 0),
        "total_keys_examined": exec_stats.get("totalKeysExamined", 0),
        "n_returned": exec_stats.get("nReturned", 0),
        "winning_stage": stage
    }


def run_benchmark():
    print("=" * 80)
    print("MONGODB QUERY OPTIMIZATION BENCHMARK: COLLSCAN vs IXSCAN")
    print(f"Target Collection: '{BENCHMARK_COLL}' (Isolated Synthetic Dataset)")
    print("=" * 80)

    db = get_database()
    coll = db[BENCHMARK_COLL]

    # Clean up previous benchmark collection if present
    coll.drop()

    print(f"\n[Step 1] Inserting {NUM_DOCS} synthetic student records...")
    t0 = time.time()
    docs = generate_benchmark_data(NUM_DOCS)
    coll.insert_many(docs, ordered=False)
    insert_duration = round(time.time() - t0, 2)
    print(f"-> Successfully inserted {coll.count_documents({})} documents in {insert_duration}s.")

    # Drop any non-default indexes on benchmark collection to guarantee unindexed state
    for idx in coll.list_indexes():
        if idx["name"] != "_id_":
            coll.drop_index(idx["name"])

    # -------------------------------------------------------------------------
    # TEST QUERY 1: Compound Filter (department == 'CSE' AND attendance >= 85)
    # -------------------------------------------------------------------------
    query_1 = {"department": "CSE", "attendance": {"$gte": 85.0}}
    sort_1 = [("attendance", -1)]

    print("\n[Step 2] Executing Query 1 WITHOUT Index...")
    print(f"  Filter: {query_1}")
    print(f"  Sort:   {sort_1}")

    explain_unindexed_q1 = db.command(
        "explain",
        {"find": BENCHMARK_COLL, "filter": query_1, "sort": dict(sort_1)},
        verbosity="executionStats"
    )
    stats_unindexed_q1 = extract_stats(explain_unindexed_q1)

    print("\n[Step 3] Creating Compound Index on [('department', 1), ('attendance', -1)]...")
    idx_q1 = coll.create_index([("department", 1), ("attendance", -1)], name="idx_bench_dept_att")
    print(f"-> Index created: {idx_q1}")

    print("\n[Step 4] Executing Query 1 WITH Compound Index...")
    explain_indexed_q1 = db.command(
        "explain",
        {"find": BENCHMARK_COLL, "filter": query_1, "sort": dict(sort_1)},
        verbosity="executionStats"
    )
    stats_indexed_q1 = extract_stats(explain_indexed_q1)

    # -------------------------------------------------------------------------
    # TEST QUERY 2: Single-field exact match (email == 'bench.student5000@university.edu')
    # -------------------------------------------------------------------------
    query_2 = {"email": "bench.student5000@university.edu"}

    print("\n[Step 5] Executing Query 2 (Email lookup) WITHOUT Unique Index...")
    explain_unindexed_q2 = db.command(
        "explain",
        {"find": BENCHMARK_COLL, "filter": query_2},
        verbosity="executionStats"
    )
    stats_unindexed_q2 = extract_stats(explain_unindexed_q2)

    print("\n[Step 6] Creating Unique Index on 'email'...")
    idx_q2 = coll.create_index([("email", 1)], unique=True, name="idx_bench_email")
    print(f"-> Index created: {idx_q2}")

    print("\n[Step 7] Executing Query 2 WITH Unique Index...")
    explain_indexed_q2 = db.command(
        "explain",
        {"find": BENCHMARK_COLL, "filter": query_2},
        verbosity="executionStats"
    )
    stats_indexed_q2 = extract_stats(explain_indexed_q2)

    # -------------------------------------------------------------------------
    # PRINT RESULTS TABLE
    # -------------------------------------------------------------------------
    table_data = [
        [
            "Q1: Dept + Attendance",
            "Unindexed",
            stats_unindexed_q1["winning_stage"],
            stats_unindexed_q1["total_docs_examined"],
            stats_unindexed_q1["total_keys_examined"],
            stats_unindexed_q1["n_returned"],
            f"{stats_unindexed_q1['execution_time_ms']} ms"
        ],
        [
            "Q1: Dept + Attendance",
            "Indexed (Compound)",
            stats_indexed_q1["winning_stage"],
            stats_indexed_q1["total_docs_examined"],
            stats_indexed_q1["total_keys_examined"],
            stats_indexed_q1["n_returned"],
            f"{stats_indexed_q1['execution_time_ms']} ms"
        ],
        [
            "Q2: Email Lookup",
            "Unindexed",
            stats_unindexed_q2["winning_stage"],
            stats_unindexed_q2["total_docs_examined"],
            stats_unindexed_q2["total_keys_examined"],
            stats_unindexed_q2["n_returned"],
            f"{stats_unindexed_q2['execution_time_ms']} ms"
        ],
        [
            "Q2: Email Lookup",
            "Indexed (Unique)",
            stats_indexed_q2["winning_stage"],
            stats_indexed_q2["total_docs_examined"],
            stats_indexed_q2["total_keys_examined"],
            stats_indexed_q2["n_returned"],
            f"{stats_indexed_q2['execution_time_ms']} ms"
        ]
    ]

    headers = [
        "Query Scenario",
        "Index State",
        "Execution Stage",
        "Docs Examined",
        "Keys Examined",
        "Docs Returned",
        "Exec Time"
    ]

    print("\n" + "=" * 80)
    print("BENCHMARK COMPARISON SUMMARY (10,000 Documents)")
    print("=" * 80)
    print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))

    print("\n[Analysis & Key Takeaways for Viva]")
    print("1. Examination Ratio (Docs Examined / Docs Returned):")
    print(f"   - Q1 Unindexed examined {stats_unindexed_q1['total_docs_examined']} docs for {stats_unindexed_q1['n_returned']} results (Full Collection Scan).")
    print(f"   - Q1 Indexed examined {stats_indexed_q1['total_docs_examined']} docs (Index Scan using B-Tree bounds).")
    print("2. Point Lookup (Q2):")
    print(f"   - Q2 Unindexed examined {stats_unindexed_q2['total_docs_examined']} docs to find 1 record.")
    print(f"   - Q2 Indexed examined exactly {stats_indexed_q2['total_keys_examined']} key and {stats_indexed_q2['total_docs_examined']} doc via O(log N) B-Tree traversal.")
    print("3. Trade-offs:")
    print("   - Indexes drastically reduce disk I/O and query latency on read operations.")
    print("   - However, every insert/update/delete incurs write overhead to maintain B-Tree index structures,")
    print("     and indexes consume additional RAM (WiredTiger cache) and storage space.")

    # Cleanup benchmark collection to leave database clean
    coll.drop()
    print(f"\n[Cleanup] Dropped benchmark collection '{BENCHMARK_COLL}'. Project data remains intact.")
    print("=" * 80)


if __name__ == "__main__":
    run_benchmark()
