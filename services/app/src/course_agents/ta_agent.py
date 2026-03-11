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
    preferences_mcp_server,
    user_context: str = "",
) -> Agent:

    instructions = (
        Path(__file__).with_name("instructions").joinpath("ta.md").read_text()
    )

    if user_context:
        instructions = f"{instructions}\n\nAuthenticated user context:\n{user_context}"

    attendance_agent = create_attendance_agent(model_name, attendance_mcp_server)
    lecture_agent = create_lecture_agent(model_name, chroma_mcp_server)
    notebook_agent = create_notebook_agent(model_name, github_mcp_server)

    return Agent(
        name="TA Agent",
        instructions=instructions,
        model=model_name,
        mcp_servers=[preferences_mcp_server],
        tools=[
            attendance_agent.as_tool(
                tool_name="attendance_specialist",
                tool_description=(
                    "Use for absence requests and attendance-record questions. "
                    "Pass a full task description including the student's goal, "
                    "student identifier, class date, and any relevant context."
                ),
            ),
            lecture_agent.as_tool(
                tool_name="lecture_specialist",
                tool_description=(
                    "Use for lecture slide and syllabus questions. "
                    "Pass a full task description including the student's "
                    "question, relevant lecture or slide identifiers, and the "
                    "kind of explanation needed."
                ),
            ),
            notebook_agent.as_tool(
                tool_name="notebook_specialist",
                tool_description=(
                    "Use for notebook and course code questions. "
                    "Pass a full task description including the user's goal, "
                    "the relevant notebook or file path, and what should be explained."
                ),
            ),
        ],
    )
