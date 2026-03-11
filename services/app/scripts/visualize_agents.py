import os
import sys
from pathlib import Path

from agents.extensions.visualization import draw_graph


ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from course_agents import create_ta_agent  # noqa: E402
from mcp_servers import (  # noqa: E402
    create_attendance_mcp_server,
    create_chroma_mcp_server,
    create_github_mcp_server,
)


def main() -> None:
    model_name = os.getenv("OPENAI_CHAT_MODEL", "gpt-4.1-mini")
    output_dir = Path(os.getenv("ARTIFACTS_DIR", "/artifacts"))
    output_dir.mkdir(parents=True, exist_ok=True)

    ta_agent = create_ta_agent(
        model_name=model_name,
        github_mcp_server=create_github_mcp_server(),
        chroma_mcp_server=create_chroma_mcp_server(),
        attendance_mcp_server=create_attendance_mcp_server(),
    )

    output_path = output_dir / "agent_graph"
    draw_graph(ta_agent, filename=str(output_path))
    print(f"Saved agent graph to {output_path}.png")


if __name__ == "__main__":
    main()
