import os
import sqlite3
from contextlib import closing
from datetime import datetime
from typing import Any

from agents import RunContextWrapper, function_tool


ATTENDANCE_DIR = os.getenv("ATTENDANCE_DATA_DIR", "/workspace/attendance")
ATTENDANCE_DB_PATH = os.path.join(ATTENDANCE_DIR, "attendance.sqlite3")


def _get_connection() -> sqlite3.Connection:
    os.makedirs(ATTENDANCE_DIR, exist_ok=True)
    connection = sqlite3.connect(ATTENDANCE_DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def _validate_date(class_date: str) -> str:
    datetime.strptime(class_date, "%Y-%m-%d")
    return class_date


@function_tool
def get_student_record(ctx: RunContextWrapper[Any]) -> dict:
    """Return the authenticated student's current absence summary and request history."""
    username = ctx.context.username

    with closing(_get_connection()) as connection:
        absence_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM absences
            WHERE username = ?
            """,
            (username,),
        ).fetchone()[0]

        requests = connection.execute(
            """
            SELECT username, student_name, class_date, created_at
            FROM absences
            WHERE username = ?
            ORDER BY class_date DESC, id DESC
            """,
            (username,),
        ).fetchall()

    return {
        "username": username,
        "student_name": ctx.context.name,
        "absence_count": absence_count,
        "absences": [dict(row) for row in requests],
    }


@function_tool
def request_absence(ctx: RunContextWrapper[Any], class_date: str) -> dict:
    """Create an absence request for the authenticated student using the course auto-approval policy."""
    username = ctx.context.username
    student_name = ctx.context.name
    class_date = _validate_date(class_date)

    with closing(_get_connection()) as connection:
        existing = connection.execute(
            """
            SELECT id, username, student_name, class_date, created_at
            FROM absences
            WHERE username = ? AND class_date = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (username, class_date),
        ).fetchone()
        if existing is not None:
            return {
                "username": existing["username"],
                "student_name": existing["student_name"],
                "class_date": existing["class_date"],
                "created_at": existing["created_at"],
                "message": "An absence is already recorded for this student and class date.",
            }

        absence_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM absences
            WHERE username = ?
            """,
            (username,),
        ).fetchone()[0]

        if absence_count >= 2:
            return {
                "username": username,
                "student_name": student_name,
                "class_date": class_date,
                "message": (
                    "Absence denied automatically because the student already has 2 absences."
                ),
            }

        created_at = datetime.utcnow().isoformat(timespec="seconds") + "Z"

        connection.execute(
            """
            INSERT INTO absences (
                username,
                student_name,
                class_date,
                created_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (username, student_name, class_date, created_at),
        )
        connection.commit()

    return {
        "username": username,
        "student_name": student_name,
        "class_date": class_date,
        "absence_count": absence_count + 1,
        "message": "Absence approved automatically.",
    }
