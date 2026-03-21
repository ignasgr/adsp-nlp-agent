import os

from agents.mcp import MCPServerStreamableHttp

CHROMA_MCP_URL = os.getenv("CHROMA_MCP_URL", "http://chroma_mcp:8001/mcp")


def create_chroma_mcp_server() -> MCPServerStreamableHttp:
    return MCPServerStreamableHttp(
        name="Chroma MCP",
        params={"url": CHROMA_MCP_URL},
        cache_tools_list=True,
    )
