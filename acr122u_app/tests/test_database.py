import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import DatabaseManager

def test_database_creation_and_insertion():
    # Use memory database for testing
    db = DatabaseManager(db_path="sqlite:///:memory:")

    # Check initial empty state
    records = db.get_recent_records()
    assert len(records) == 0

    # Add record
    db.add_record(uid="0411223344", action="DETECT", details="Card Inserted")
    records = db.get_recent_records()

    assert len(records) == 1
    assert records[0].uid == "0411223344"
    assert records[0].action == "DETECT"
    assert records[0].details == "Card Inserted"
    assert records[0].timestamp is not None

def test_database_limit():
    db = DatabaseManager(db_path="sqlite:///:memory:")

    for i in range(10):
        db.add_record(uid=f"UID_{i}", action="TEST")

    records = db.get_recent_records(limit=5)
    assert len(records) == 5
    # The newest should be UID_9
    assert records[0].uid == "UID_9"
