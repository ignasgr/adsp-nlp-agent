from pathlib import Path

from agents import Agent
from agents.mcp import MCPServerStreamableHttp


def create_lecture_agent(model_name: str, chroma_mcp_server: MCPServerStreamableHttp) -> Agent:
    instructions = Path(__file__).with_name("instructions").joinpath("lecture.md").read_text()
    return Agent(
        name="Lecture Agent",
        instructions=instructions,
        model=model_name,
        mcp_servers=[chroma_mcp_server],
    )
