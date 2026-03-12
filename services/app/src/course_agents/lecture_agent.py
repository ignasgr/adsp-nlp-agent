from pathlib import Path

from agents import Agent


def create_lecture_agent(model_name: str, chroma_mcp_server) -> Agent:
    instructions = Path(__file__).with_name("instructions").joinpath("lecture.md").read_text()
    return Agent(
        name="Lecture Agent",
        instructions=instructions,
        model=model_name,
        mcp_servers=[chroma_mcp_server],
    )
