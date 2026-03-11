from pathlib import Path

from agents import Agent


def create_attendance_agent(model_name: str, attendance_mcp_server) -> Agent:
    instructions = Path(__file__).with_name("instructions").joinpath("attendance.md").read_text()
    return Agent(
        name="Attendance Specialist",
        instructions=instructions,
        model=model_name,
        mcp_servers=[attendance_mcp_server],
    )
