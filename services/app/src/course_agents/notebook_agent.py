from pathlib import Path

from agents import Agent


def create_notebook_agent(
    model_name: str,
    github_mcp_server,
    github_repo: str,
) -> Agent:
    instructions = (
        Path(__file__)
        .with_name("instructions")
        .joinpath("notebook.md")
        .read_text()
        .format(github_repo=github_repo)
    )
    return Agent(
        name="Notebook Agent",
        instructions=instructions,
        model=model_name,
        mcp_servers=[github_mcp_server],
    )
