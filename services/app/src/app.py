import asyncio
import json
import os
import re
from dataclasses import dataclass
from datetime import date
from functools import cache

import chainlit as cl
from agents import Runner, SQLiteSession
from course_agents import create_ta_agent
from mcp_servers import (
    create_chroma_mcp_server,
    create_github_mcp_server,
)
from openai.types.responses import ResponseTextDeltaEvent
from tools import (
    get_response_style,
    get_student_record,
    request_absence,
    update_response_style,
)

MODEL_NAME = os.getenv("OPENAI_CHAT_MODEL")
GITHUB_REPO = os.environ["GITHUB_REPO"]


@dataclass
class AppContext:
    username: str
    name: str
    today: str
    github_repo: str


def _session_key_for_user(identifier: str) -> str:
    safe_identifier = re.sub(r"[^a-zA-Z0-9]+", "_", identifier).strip("_").lower()
    return f"chainlit_{safe_identifier or 'user'}"


@cache
def _load_auth_users() -> dict[str, dict]:
    configured_users = json.loads(os.environ["CHAINLIT_AUTH_USERS_JSON"])
    return {user["username"]: user for user in configured_users}


def _item_attr(item, attr_name: str):
    # Agents SDK items are not fully uniform across event types and versions.
    # We first try the wrapper object, then fall back to the underlying raw item.
    value = getattr(item, attr_name, None)
    if value is not None:
        return value

    raw_item = getattr(item, "raw_item", None)
    if raw_item is None:
        return None
    if isinstance(raw_item, dict):
        return raw_item.get(attr_name)
    return getattr(raw_item, attr_name, None)


@cl.password_auth_callback
def password_auth_callback(username: str, password: str):
    user = _load_auth_users().get(username)
    if user is None or user["password"] != password:
        return None

    return cl.User(
        identifier=username,
        metadata={
            "name": user.get("name", username),
            "username": username,
            "provider": "credentials",
        },
    )


@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Request class absence",
            message="I need to request a class absence. Please help me submit it.",
        ),
        cl.Starter(
            label="Ask about lecture slides",
            message="Can you help me understand some lecture slides?",
        ),
        cl.Starter(
            label="Ask about lecture code",
            message="Can you help me understand some of the code in the notebooks?",
        ),
    ]


@cl.on_chat_start
async def start_chat() -> None:
    current_user = cl.user_session.get("user")
    user_identifier = (
        current_user.identifier if current_user is not None else "anonymous"
    )
    user_name = (
        current_user.metadata.get("name", user_identifier)
        if current_user is not None
        else "Anonymous User"
    )

    # Create and connect the GitHub MCP server once per Chainlit chat session.
    github_mcp_server = create_github_mcp_server()
    await github_mcp_server.connect()

    chroma_mcp_server = create_chroma_mcp_server()
    await chroma_mcp_server.connect()

    app_context = AppContext(
        username=user_identifier,
        name=user_name,
        today=date.today().isoformat(),
        github_repo=GITHUB_REPO,
    )

    # The agent gets the MCP server as a tool source. The conversation state is
    # stored separately in SQLiteSession and reused on each user turn.
    agent = create_ta_agent(
        model_name=MODEL_NAME,
        github_mcp_server=github_mcp_server,
        chroma_mcp_server=chroma_mcp_server,
        github_repo=GITHUB_REPO,
        attendance_tools=[get_student_record, request_absence],
        preference_tools=[get_response_style, update_response_style],
    )

    cl.user_session.set("agent", agent)
    cl.user_session.set("app_context", app_context)
    cl.user_session.set(
        "agent_session", SQLiteSession(_session_key_for_user(user_identifier))
    )
    cl.user_session.set("github_mcp_server", github_mcp_server)
    cl.user_session.set("chroma_mcp_server", chroma_mcp_server)


@cl.on_chat_end
async def end_chat() -> None:
    # Clean up the MCP connection when the chat session ends.
    github_mcp_server = cl.user_session.get("github_mcp_server")
    if github_mcp_server is not None:
        await github_mcp_server.cleanup()
    chroma_mcp_server = cl.user_session.get("chroma_mcp_server")
    if chroma_mcp_server is not None:
        await chroma_mcp_server.cleanup()


@cl.on_message
async def on_message(message: cl.Message) -> None:
    # Recover the per-chat agent and session created during chat start.
    agent = cl.user_session.get("agent")
    session = cl.user_session.get("agent_session")
    app_context = cl.user_session.get("app_context")

    # Stream the assistant response into a normal chat message so the main UI
    # stays chat-first, while tool calls are shown separately as steps.
    msg = cl.Message(content="")
    await msg.send()

    result = Runner.run_streamed(
        agent,
        message.content,
        session=session,
        context=app_context,
    )

    async for event in result.stream_events():
        # These are the raw text deltas from the model response.
        if event.type == "raw_response_event" and isinstance(
            event.data, ResponseTextDeltaEvent
        ):
            await msg.stream_token(event.data.delta)
            await asyncio.sleep(0.05)  # paces the typewriter effect in the UI

        # Tool calls are surfaced as Chainlit steps. We only show the tool
        # name and arguments to keep the trace compact and readable.
        elif event.type == "run_item_stream_event":
            if event.name == "tool_called" and event.item.type == "tool_call_item":
                step = cl.Step(
                    name=_item_attr(event.item, "name") or "tool",
                    type="tool",
                    show_input="json",
                )
                step.input = _item_attr(event.item, "arguments")
                await step.send()

    await msg.update()
