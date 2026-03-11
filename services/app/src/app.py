import asyncio
import os

import chainlit as cl
from openai import AsyncOpenAI

MODEL_NAME = os.getenv("OPENAI_CHAT_MODEL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = AsyncOpenAI(api_key=OPENAI_API_KEY)


@cl.on_chat_start
def start_chat():
    cl.user_session.set(
        "message_history",
        [{"role": "system", "content": "You are a helpful assistant."}],
    )


@cl.on_message
async def on_message(message: cl.Message) -> None:

    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": message.content})

    msg = cl.Message(content="")
    await msg.send()

    stream = await client.chat.completions.create(
        model=MODEL_NAME,
        messages=message_history,
        stream=True,
    )

    async for part in stream:
        if token := part.choices[0].delta.content or "":
            await msg.stream_token(token)
            await asyncio.sleep(0.05)

    message_history.append({"role": "assistant", "content": msg.content})

    await msg.update()
