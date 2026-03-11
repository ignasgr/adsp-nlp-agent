import os
import sqlite3
import sys
from contextlib import closing
from datetime import datetime

from agents.mcp import MCPServerStdio
from fastmcp import FastMCP

PREFERENCE_DIR = os.getenv("PREFERENCE_DATA_DIR", "/workspace/preferences")
PREFERENCE_DB_PATH = os.path.join(PREFERENCE_DIR, "preferences.sqlite3")

mcp = FastMCP("Preferences MCP")


def create_preferences_mcp_server() -> MCPServerStdio:
    return MCPServerStdio(
        name="Preferences MCP",
        params={
            "command": sys.executable,
            "args": [
                "src/mcp_servers/preferences.py",
            ],
        },
        cache_tools_list=False,
    )


def _get_connection() -> sqlite3.Connection:
    os.makedirs(PREFERENCE_DIR, exist_ok=True)
    connection = sqlite3.connect(PREFERENCE_DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def _init_db() -> None:
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


@mcp.tool
def get_response_style(username: str) -> dict:
    """Return the saved response style preference for a username."""
    _init_db()

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


@mcp.tool
def update_response_style(username: str, response_style: str) -> dict:
    """Create or update a user's saved response style preference.

    The caller should first read the current response style with
    `get_response_style`, decide on the desired final style, and then call this
    tool with that updated value.
    """
    _init_db()
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


if __name__ == "__main__":
    mcp.run()
