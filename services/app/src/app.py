import asyncio
import os

import chainlit as cl
from agents import Agent, Runner, SQLiteSession
from mcp_servers import create_github_mcp_server
from openai.types.responses import ResponseTextDeltaEvent

MODEL_NAME = os.getenv("OPENAI_CHAT_MODEL")


@cl.on_chat_start
async def start_chat() -> None:
    github_mcp_server = create_github_mcp_server()
    await github_mcp_server.connect()

    agent = Agent(
        name="Assistant",
        instructions="You are a helpful assistant.",
        model=MODEL_NAME,
        mcp_servers=[github_mcp_server],
    )

    cl.user_session.set("agent", agent)
    cl.user_session.set("agent_session", SQLiteSession("chainlit_session"))
    cl.user_session.set("github_mcp_server", github_mcp_server)


@cl.on_chat_end
async def end_chat() -> None:
    github_mcp_server = cl.user_session.get("github_mcp_server")
    if github_mcp_server is not None:
        await github_mcp_server.cleanup()


@cl.on_message
async def on_message(message: cl.Message) -> None:
    agent = cl.user_session.get("agent")
    session = cl.user_session.get("agent_session")
    msg = cl.Message(content="")
    await msg.send()

    result = Runner.run_streamed(
        agent,
        message.content,
        session=session,
    )

    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(
            event.data, ResponseTextDeltaEvent
        ):
            await msg.stream_token(event.data.delta)
            await asyncio.sleep(0.05)

    await msg.update()
