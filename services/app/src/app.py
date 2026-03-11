import asyncio
import os

import chainlit as cl
from agents import Agent, Runner, SQLiteSession
from openai.types.responses import ResponseTextDeltaEvent

MODEL_NAME = os.getenv("OPENAI_CHAT_MODEL")

agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant.",
    model=MODEL_NAME,
)


@cl.on_chat_start
async def start_chat() -> None:
    cl.user_session.set("agent_session", SQLiteSession("chainlit_session"))


@cl.on_message
async def on_message(message: cl.Message) -> None:
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
