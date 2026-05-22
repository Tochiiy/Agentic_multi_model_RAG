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
from starlette.requests import Request
from starlette.responses import JSONResponse
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


# ── 3. Health Check Route for Render ──────────────────────────────
@mcp.custom_route("/", methods=["GET"])
async def root_health_check(request: Request) -> JSONResponse:
    """Returns 200 OK to satisfy Render's web service port scans."""
    return JSONResponse({"status": "healthy", "server": "AGENTIC-RAG-MCP-Agent"})

    
# ── 4. Mount FastMCP under a FastAPI wrapper and add API-key validation
from fastapi import FastAPI, Request, HTTPException

# Create a small FastAPI app that mounts the FastMCP ASGI app at /mcp.
# This lets us run the service with a standard ASGI server (uvicorn)
# and add simple middleware (e.g. API key validation) at the outer level.
app = FastAPI()

MCP_API_KEY = os.getenv("MCP_API_KEY", "")


@app.middleware("http")
async def validate_mcp_api_key(request: Request, call_next):
    # Only validate requests that target the mounted MCP app
    if request.url.path.startswith("/mcp"):
        api_key = request.headers.get("x-api-key", "").strip()
        if not MCP_API_KEY or api_key != MCP_API_KEY:
            raise HTTPException(status_code=401, detail="Unauthorized")
    return await call_next(request)


# Mount the FastMCP-generated ASGI app at the /mcp path
mcp_app = mcp.http_app()
app.mount("/mcp", mcp_app)


@app.get("/")
async def outer_root():
    return JSONResponse({"status": "healthy", "server": "AGENTIC-RAG-MCP-Agent (MCP wrapper)"})