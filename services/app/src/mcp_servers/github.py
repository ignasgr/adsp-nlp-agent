import os

from agents.mcp import MCPServerStreamableHttp
from agents.mcp.util import ToolFilterStatic


def create_github_mcp_server() -> MCPServerStreamableHttp:
    github_mcp_url = os.environ["GITHUB_MCP_URL"]
    github_pat = os.environ["GITHUB_PAT"]

    return MCPServerStreamableHttp(
        name="GitHub MCP",
        params={
            "url": github_mcp_url,
            "headers": {
                "Authorization": f"Bearer {github_pat}",
            },
        },
        cache_tools_list=True,
        tool_filter=ToolFilterStatic(allowed_tool_names=["get_file_contents", "list_branches",]),
    )
