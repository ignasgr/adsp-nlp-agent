from pathlib import Path

from agents import Agent

from .attendance_agent import create_attendance_agent
from .lecture_agent import create_lecture_agent
from .notebook_agent import create_notebook_agent


def create_ta_agent(
    model_name: str,
    github_mcp_server,
    chroma_mcp_server,
    attendance_mcp_server,
) -> Agent:
    instructions = Path(__file__).with_name("instructions").joinpath("ta.md").read_text()

    attendance_agent = create_attendance_agent(model_name, attendance_mcp_server)
    lecture_agent = create_lecture_agent(model_name, chroma_mcp_server)
    notebook_agent = create_notebook_agent(model_name, github_mcp_server)

    return Agent(
        name="TA Agent",
        instructions=instructions,
        model=model_name,
        tools=[
            attendance_agent.as_tool(
                tool_name="attendance_specialist",
                tool_description="Use for absence requests and attendance-record questions.",
            ),
            lecture_agent.as_tool(
                tool_name="lecture_specialist",
                tool_description="Use for lecture slide and syllabus questions.",
            ),
            notebook_agent.as_tool(
                tool_name="notebook_specialist",
                tool_description="Use for notebook and course code questions.",
            ),
        ],
    )
