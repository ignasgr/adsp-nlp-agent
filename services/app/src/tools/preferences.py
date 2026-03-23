import os
import sqlite3
from contextlib import closing
from datetime import datetime
from typing import Any

from agents import RunContextWrapper, function_tool

PREFERENCE_DIR = os.getenv("PREFERENCE_DATA_DIR", "/workspace/preferences")
PREFERENCE_DB_PATH = os.path.join(PREFERENCE_DIR, "preferences.sqlite3")


def _get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(PREFERENCE_DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def _init_db() -> None:
    os.makedirs(PREFERENCE_DIR, exist_ok=True)
    with closing(_get_connection()) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS user_preferences (
                username TEXT PRIMARY KEY,
                response_style TEXT,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.commit()


_init_db()


@function_tool
def get_response_style(ctx: RunContextWrapper[Any]) -> dict:
    """Return the authenticated user's saved response style preference."""
    username = ctx.context.username

    with closing(_get_connection()) as connection:
        row = connection.execute(
            """
            SELECT username, response_style, updated_at
            FROM user_preferences
            WHERE username = ?
            """,
            (username,),
        ).fetchone()

    if row is None:
        return {"username": username, "response_style": "", "updated_at": None}

    return dict(row)


@function_tool
def update_response_style(
    ctx: RunContextWrapper[Any],
    response_style: str,
) -> dict:
    """Create or update the authenticated user's saved response style preference."""
    username = ctx.context.username
    updated_at = datetime.utcnow().isoformat(timespec="seconds") + "Z"

    with closing(_get_connection()) as connection:
        connection.execute(
            """
            INSERT INTO user_preferences (username, response_style, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(username) DO UPDATE SET
                response_style = excluded.response_style,
                updated_at = excluded.updated_at
            """,
            (username, response_style, updated_at),
        )
        connection.commit()

    return {
        "username": username,
        "response_style": response_style,
        "updated_at": updated_at,
    }
