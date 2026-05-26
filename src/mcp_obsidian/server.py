import logging
import os
from collections.abc import Sequence
from typing import Any
from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.types import Receive, Scope, Send

load_dotenv()

from . import obsidian, tools

# Load environment variables

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-obsidian")

obsidian.Obsidian()

app = Server("mcp-obsidian")

def get_path_env(name: str, default: str) -> str:
    value = os.getenv(name, default).strip() or default
    if not value.startswith("/"):
        value = f"/{value}"
    return value.rstrip("/") or "/"


MCP_HOST = os.getenv("MCP_HOST", "127.0.0.1")
MCP_PORT = int(os.getenv("MCP_PORT", "8000"))
MCP_HTTP_PATH = get_path_env("MCP_HTTP_PATH", "/mcp")

tool_handlers = {}
def add_tool_handler(tool_class: tools.ToolHandler):
    global tool_handlers

    tool_handlers[tool_class.name] = tool_class

def get_tool_handler(name: str) -> tools.ToolHandler | None:
    if name not in tool_handlers:
        return None
    
    return tool_handlers[name]

add_tool_handler(tools.ListFilesInDirToolHandler())
add_tool_handler(tools.ListFilesInVaultToolHandler())
add_tool_handler(tools.GetFileContentsToolHandler())
add_tool_handler(tools.SearchToolHandler())
add_tool_handler(tools.PatchContentToolHandler())
add_tool_handler(tools.AppendContentToolHandler())
add_tool_handler(tools.PutContentToolHandler())
add_tool_handler(tools.DeleteFileToolHandler())
add_tool_handler(tools.ComplexSearchToolHandler())
add_tool_handler(tools.BatchGetFileContentsToolHandler())
add_tool_handler(tools.PeriodicNotesToolHandler())
add_tool_handler(tools.RecentPeriodicNotesToolHandler())
add_tool_handler(tools.RecentChangesToolHandler())

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""

    return [th.get_tool_description() for th in tool_handlers.values()]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls for command line run."""
    
    if not isinstance(arguments, dict):
        raise RuntimeError("arguments must be dictionary")


    tool_handler = get_tool_handler(name)
    if not tool_handler:
        raise ValueError(f"Unknown tool: {name}")

    try:
        return tool_handler.run_tool(arguments)
    except Exception as e:
        logger.error(str(e))
        raise RuntimeError(f"Caught Exception. Error: {str(e)}")


async def health(_: Request) -> JSONResponse:
    return JSONResponse({"status": "ok", "server": "mcp-obsidian"})


async def server_info(_: Request) -> JSONResponse:
    return JSONResponse({
        "server": "mcp-obsidian",
        "transport": "streamable-http",
        "mcp_url": f"http://{MCP_HOST}:{MCP_PORT}{MCP_HTTP_PATH}",
    })


class StreamableHTTPASGIApp:
    def __init__(self, session_manager: StreamableHTTPSessionManager):
        self.session_manager = session_manager

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await self.session_manager.handle_request(scope, receive, send)


def create_http_app() -> Starlette:
    session_manager = StreamableHTTPSessionManager(app=app)
    return Starlette(
        routes=[
            Route("/", endpoint=server_info, methods=["GET"]),
            Route("/health", endpoint=health, methods=["GET"]),
            Route(MCP_HTTP_PATH, endpoint=StreamableHTTPASGIApp(session_manager)),
        ],
        lifespan=lambda _: session_manager.run(),
    )


async def main():
    import uvicorn

    logger.info("Starting mcp-obsidian Streamable HTTP server at http://%s:%s%s", MCP_HOST, MCP_PORT, MCP_HTTP_PATH)

    config = uvicorn.Config(
        create_http_app(),
        host=MCP_HOST,
        port=MCP_PORT,
        log_level="info",
    )
    server = uvicorn.Server(config)
    await server.serve()
