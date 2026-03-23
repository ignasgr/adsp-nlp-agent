from pathlib import Path

from agents import Agent, Tool


def create_attendance_agent(model_name: str, attendance_tools: list[Tool]) -> Agent:
    instructions = (
        Path(__file__).with_name("instructions").joinpath("attendance.md").read_text()
    )
    return Agent(
        name="Attendance Agent",
        instructions=instructions,
        model=model_name,
        tools=attendance_tools,
    )
