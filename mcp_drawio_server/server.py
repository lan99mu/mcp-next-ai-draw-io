#!/usr/bin/env python3
"""
MCP Draw.io Server

A Model Context Protocol (MCP) server that provides tools for creating and 
manipulating Draw.io diagrams. This server focuses on providing clean, 
simple tools that Copilot/Agents can use to work with Draw.io files.

Core capabilities:
- Create diagrams programmatically
- Read and parse existing .drawio files
- Modify diagram elements by ID
- Save diagrams to files

This module serves as the main entry point and server initialization.
The implementation is modularized into:
- tools.py: Tool schema definitions
- handlers/: Tool call implementations (split by category)
- prompts.py: MCP prompt templates
- resources.py: On-demand documentation resources
- docs_content.py: Documentation content for resources
"""

import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, Prompt, GetPromptResult, Resource, ReadResourceResult

from .tools import get_tool_definitions
from .handlers import handle_tool_call
from .prompts import get_prompt_definitions, get_prompt_result
from .resources import get_resource_definitions, get_resource_content


# Server-level instructions injected once into the LLM system prompt.
# Keep this concise — it guides optimal tool usage without bloating every request.
SERVER_INSTRUCTIONS = (
    "Draw.io diagram server. Workflow: "
    "1) Use batch_operations to add all shapes+connections in one call instead of individual add_shape/add_connection calls — this is the preferred approach and saves significant tokens. "
    "2) Use create_diagram(autosave_path=...) or load_diagram(autosave=true) to enable autosave so changes appear on disk immediately without a separate save_diagram call. "
    "3) Call list_cells/get_cell only when you need to retrieve IDs or inspect existing elements (get_cell returns bound_nodes — no separate query tool). "
    "4) detect_overlaps, detect_line_crossings, and suggest_bindings now return a structured `fix` field per issue — execute it verbatim via batch_operations (it supports bind_nodes/unbind_nodes/move_shape/update_cell). "
    "5) To resolve overlaps in bulk, call auto_layout_adjust; it respects binding groups and container hierarchy. "
    "6) Call save_diagram explicitly only when autosave is off. "
    "7) For detailed docs on shapes, bindings, or workflows, read the docs:// resources instead of asking questions."
)

# Initialize MCP server
app = Server("mcp-drawio-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return get_tool_definitions()


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list:
    """Handle tool calls."""
    return await handle_tool_call(name, arguments)


@app.list_prompts()
async def list_prompts() -> list[Prompt]:
    """List available prompt templates for common diagram workflows."""
    return get_prompt_definitions()


@app.get_prompt()
async def get_prompt(name: str, arguments: dict[str, str] | None) -> GetPromptResult:
    """Get a specific prompt template with instructions."""
    return get_prompt_result(name, arguments)


@app.list_resources()
async def list_resources() -> list[Resource]:
    """List available documentation resources."""
    return get_resource_definitions()


@app.read_resource()
async def read_resource(uri: str) -> ReadResourceResult:
    """Read detailed documentation resource content."""
    return get_resource_content(uri)


async def main():
    """Main entry point for the server."""
    async with stdio_server() as (read_stream, write_stream):
        init_options = app.create_initialization_options()
        # Inject server instructions so the LLM receives workflow guidance once
        # at session start rather than on every tool description.
        init_options.instructions = SERVER_INSTRUCTIONS
        await app.run(
            read_stream,
            write_stream,
            init_options
        )


if __name__ == "__main__":
    asyncio.run(main())
