import os
import sys

from agents.mcp import MCPServerStdio, MCPServerStreamableHttp


def create_github_mcp_server() -> MCPServerStreamableHttp:
    github_mcp_url = os.environ["GITHUB_MCP_URL"]
    github_pat = os.environ["GITHUB_PAT"]

    return MCPServerStreamableHttp(
        name="GitHub MCP",
        params={
            "url": github_mcp_url,
            "headers": {
                "Authorization": f"Bearer {github_pat}",
                "X-MCP-Tools": "get_file_contents",
            },
        },
        cache_tools_list=False,
    )


def create_chroma_mcp_server() -> MCPServerStdio:
    return MCPServerStdio(
        name="Chroma MCP",
        params={
            "command": sys.executable,
            "args": [
                "src/chroma_mcp_server.py",
            ],
        },
        cache_tools_list=False,
    )
