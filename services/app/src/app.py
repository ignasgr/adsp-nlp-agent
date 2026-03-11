import asyncio
import os
from pathlib import Path

import chainlit as cl
from agents import Agent, Runner, SQLiteSession
from mcp_servers import create_chroma_mcp_server, create_github_mcp_server
from openai.types.responses import ResponseTextDeltaEvent

MODEL_NAME = os.getenv("OPENAI_CHAT_MODEL")
COURSE_TA_INSTRUCTIONS = Path(__file__).with_name("instructions.md").read_text()


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


@cl.on_chat_start
async def start_chat() -> None:
    # Create and connect the GitHub MCP server once per Chainlit chat session.
    github_mcp_server = create_github_mcp_server()
    await github_mcp_server.connect()
    chroma_mcp_server = create_chroma_mcp_server()
    await chroma_mcp_server.connect()

    # The agent gets the MCP server as a tool source. The conversation state is
    # stored separately in SQLiteSession and reused on each user turn.
    agent = Agent(
        name="Assistant",
        instructions=COURSE_TA_INSTRUCTIONS,
        model=MODEL_NAME,
        mcp_servers=[github_mcp_server, chroma_mcp_server],
    )

    cl.user_session.set("agent", agent)
    cl.user_session.set("agent_session", SQLiteSession("chainlit_session"))
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

    # Stream the assistant response into a normal chat message so the main UI
    # stays chat-first, while tool calls are shown separately as steps.
    msg = cl.Message(content="")
    await msg.send()

    result = Runner.run_streamed(
        agent,
        message.content,
        session=session,
    )

    async for event in result.stream_events():
        # These are the raw text deltas from the model response.
        if event.type == "raw_response_event" and isinstance(
            event.data, ResponseTextDeltaEvent
        ):
            await msg.stream_token(event.data.delta)
            await asyncio.sleep(0.05)

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
