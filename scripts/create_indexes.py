"""
Standalone script to create and display MongoDB indexes.
Usage: python scripts/create_indexes.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.connection import get_database
from database.indexes import create_all_indexes, list_indexes_info

def main():
    print("=" * 60)
    print("Creating MongoDB Indexes for Student Performance Analytics")
    print("=" * 60)
    db = get_database()
    print(f"Connected to database: {db.name}")

    created = create_all_indexes(db)
    print("\nIndexes Created / Ensured:")
    for coll, idx_list in created.items():
        print(f"  Collection [{coll}]:")
        for idx in idx_list:
            print(f"    - {idx}")

    print("\nCurrent Indexes in Database:")
    info = list_indexes_info(db)
    for coll, idxs in info.items():
        print(f"\n  Collection [{coll}] ({len(idxs)} indexes):")
        for idx in idxs:
            keys_str = ", ".join(f"{k}: {v}" for k, v in idx["key"])
            unique_str = " (UNIQUE)" if idx["unique"] else ""
            print(f"    - {idx['name']}: [{keys_str}]{unique_str}")

    print("\n" + "=" * 60)
    print("Index configuration completed successfully.")
    print("=" * 60)

if __name__ == "__main__":
    main()
