import sqlite3
from pathlib import Path
from datetime import datetime, timezone


DB_PATH = Path("backend/governance.db")


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS governance_reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trace_id TEXT NOT NULL,
                question TEXT,
                feedback_value TEXT NOT NULL,
                review_priority TEXT NOT NULL,
                review_status TEXT NOT NULL,
                root_cause TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        connection.commit()


def create_review(
    trace_id: str,
    question: str | None,
    feedback_value: str,
    review_priority: str = "High",
):
    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO governance_reviews (
                trace_id,
                question,
                feedback_value,
                review_priority,
                review_status,
                root_cause,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                trace_id,
                question,
                feedback_value,
                review_priority,
                "Pending Review",
                "Pending Classification",
                now,
                now,
            ),
        )

        connection.commit()

        return cursor.lastrowid


def list_reviews():
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM governance_reviews
            ORDER BY created_at DESC
            """
        ).fetchall()

        return [
            dict(row)
            for row in rows
        ]


def update_root_cause(
    review_id: int,
    root_cause: str,
):
    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        connection.execute(
            """
            UPDATE governance_reviews
            SET
                root_cause = ?,
                review_status = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                root_cause,
                "Under Review",
                now,
                review_id,
            ),
        )

        connection.commit()


def resolve_review(review_id: int):
    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        connection.execute(
            """
            UPDATE governance_reviews
            SET
                review_status = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                "Resolved",
                now,
                review_id,
            ),
        )

        connection.commit()