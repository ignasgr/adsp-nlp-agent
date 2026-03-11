import os
import sqlite3
import sys
from contextlib import closing
from datetime import datetime

from agents.mcp import MCPServerStdio
from fastmcp import FastMCP


ATTENDANCE_DIR = os.getenv("ATTENDANCE_DATA_DIR", "/workspace/attendance")
ATTENDANCE_DB_PATH = os.path.join(ATTENDANCE_DIR, "attendance.sqlite3")

mcp = FastMCP("Attendance MCP")


def create_attendance_mcp_server() -> MCPServerStdio:
    return MCPServerStdio(
        name="Attendance MCP",
        params={
            "command": sys.executable,
            "args": [
                "src/mcp_servers/attendance.py",
            ],
        },
        cache_tools_list=False,
    )


def _get_connection() -> sqlite3.Connection:
    os.makedirs(ATTENDANCE_DIR, exist_ok=True)
    connection = sqlite3.connect(ATTENDANCE_DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def _init_db() -> None:
    with closing(_get_connection()) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS absences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                student_name TEXT,
                class_date TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.commit()


def _validate_date(class_date: str) -> str:
    datetime.strptime(class_date, "%Y-%m-%d")
    return class_date


@mcp.tool
def attendance_get_student_record(student_id: str) -> dict:
    """Return the student's current absence summary and request history.

    Use this before approving or discussing absences so the agent can explain
    how many approved absences the student already has on record.
    """
    _init_db()

    with closing(_get_connection()) as connection:
        approved_absence_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM absences
            WHERE student_id = ? AND status = 'approved'
            """,
            (student_id,),
        ).fetchone()[0]

        requests = connection.execute(
            """
            SELECT student_id, student_name, class_date, status, created_at
            FROM absences
            WHERE student_id = ?
            ORDER BY class_date DESC, id DESC
            """,
            (student_id,),
        ).fetchall()

    return {
        "student_id": student_id,
        "approved_absence_count": approved_absence_count,
        "request_count": len(requests),
        "requests": [dict(row) for row in requests],
    }


@mcp.tool
def attendance_request_absence(
    student_id: str,
    class_date: str,
    student_name: str = "",
) -> dict:
    """Create an absence request and auto-approve it if the student has fewer than 2 approved absences.

    Policy:
    - If the student currently has fewer than 2 approved absences, approve.
    - Otherwise, deny automatically.
    """
    _init_db()
    class_date = _validate_date(class_date)

    with closing(_get_connection()) as connection:
        existing = connection.execute(
            """
            SELECT id, student_id, student_name, class_date, status, created_at
            FROM absences
            WHERE student_id = ? AND class_date = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (student_id, class_date),
        ).fetchone()
        if existing is not None:
            return {
                "student_id": existing["student_id"],
                "student_name": existing["student_name"],
                "class_date": existing["class_date"],
                "status": existing["status"],
                "created_at": existing["created_at"],
                "message": "An absence request already exists for this student and class date.",
            }

        approved_absence_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM absences
            WHERE student_id = ? AND status = 'approved'
            """,
            (student_id,),
        ).fetchone()[0]

        status = "approved" if approved_absence_count < 2 else "denied"
        created_at = datetime.utcnow().isoformat(timespec="seconds") + "Z"

        connection.execute(
            """
            INSERT INTO absences (
                student_id,
                student_name,
                class_date,
                status,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (student_id, student_name, class_date, status, created_at),
        )
        connection.commit()

    return {
        "student_id": student_id,
        "student_name": student_name,
        "class_date": class_date,
        "status": status,
        "approved_absence_count_before_request": approved_absence_count,
        "message": (
            "Absence approved automatically."
            if status == "approved"
            else "Absence denied automatically because the student already has 2 approved absences."
        ),
    }


if __name__ == "__main__":
    mcp.run()
