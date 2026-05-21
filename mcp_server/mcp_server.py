import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_server.mcp_tools import (
    retriever_tool,
    query_transformer_tool,
    web_search_tool,
    calculate_tool,
    get_current_datetime_tool
)
from mcp_server.mcp_utils import validate_api_key
from fastmcp import FastMCP
from typing import List
import uvicorn
import dotenv

dotenv.load_dotenv()


# ── 1. Initialize FastMCP ─────────────────────────────────────────
mcp = FastMCP("AGENTIC-RAG-MCP-Agent")


# ── 2. Register Tools ─────────────────────────────────────────────
@mcp.tool()
async def retriever(queries: List[str]) -> str:
    """Retrieve documents from vector db based on queries."""
    result = await retriever_tool(queries)
    return result["content"][0]["text"]


@mcp.tool()
async def query_transformer(query: str) -> str:
    """Generate 3 versions of the user input for better semantic retrieval."""
    result = await query_transformer_tool(query)
    return result["content"][0]["text"]

@mcp.tool()
async def web_search(query: str) -> dict:
    """Search the web for current information not in the knowledge base."""
    return await web_search_tool(query)

@mcp.tool()
async def calculate(expression: str) -> dict:
    """Evaluate mathematical expressions."""
    return await calculate_tool(expression)

@mcp.tool()
async def get_current_datetime(timezone: str = "UTC") -> dict:
    """Get the current date, time, and day of the week."""
    return await get_current_datetime_tool(timezone)
    
# ── 3. Run with built-in HTTP transport ──────────────────────────
if __name__ == "__main__":
    port = int(os.getenv("PORT", 3001))
    print(f"✅ MCP Server Running: http://0.0.0.0:{port}/mcp")
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=port,
        path="/mcp"
    )