
import sqlite3
import json
from datetime import datetime, timezone


DATABASE_NAME = "workflow.db"


def initialize_database():
    with sqlite3.connect(DATABASE_NAME) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS workflow_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT NOT NULL,
                status TEXT NOT NULL,
                issues TEXT NOT NULL,
                next_action TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)


def save_workflow_result(case_id, status, issues, next_action):
    created_at = datetime.now(timezone.utc).isoformat()

    with sqlite3.connect(DATABASE_NAME) as connection:
        connection.execute("""
            INSERT INTO workflow_history
            (case_id, status, issues, next_action, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            case_id,
            status,
            json.dumps(issues),
            next_action,
            created_at
        ))


def get_workflow_history(case_id):
    with sqlite3.connect(DATABASE_NAME) as connection:
        connection.row_factory = sqlite3.Row

        rows = connection.execute("""
            SELECT *
            FROM workflow_history
            WHERE case_id = ?
            ORDER BY id DESC
        """, (case_id,)).fetchall()

    results = []

    for row in rows:
        item = dict(row)
        item["issues"] = json.loads(item["issues"])
        results.append(item)

    return results
