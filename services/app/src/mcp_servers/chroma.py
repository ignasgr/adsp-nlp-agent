import os

from agents.mcp import MCPServerStreamableHttp


def create_chroma_mcp_server() -> MCPServerStreamableHttp:
    chroma_mcp_url = os.getenv("CHROMA_MCP_URL", "http://chroma_mcp:8001/mcp")
    return MCPServerStreamableHttp(
        name="Chroma MCP",
        params={"url": chroma_mcp_url},
        cache_tools_list=True,
    )
