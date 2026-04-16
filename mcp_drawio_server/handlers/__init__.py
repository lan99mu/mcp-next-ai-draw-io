#!/usr/bin/env python3
"""
Tool handlers package for MCP Draw.io Server.

This module provides the main entry point for handling tool calls,
dispatching to appropriate handler functions based on tool name.
"""

from typing import Any
from mcp.types import TextContent

from .file_handlers import (
    handle_create_diagram,
    handle_load_diagram,
    handle_save_diagram,
)
from .cell_handlers import (
    handle_list_cells,
    handle_get_cell,
    handle_update_cell,
    handle_delete_cell,
    handle_add_shape,
    handle_add_connection,
)
from .binding_handlers import (
    handle_bind_nodes,
    handle_unbind_nodes,
    handle_get_bound_nodes,
    handle_move_shape,
)
from .analysis_handlers import (
    handle_detect_line_crossings,
    handle_suggest_bindings,
    handle_detect_overlaps,
)
from .batch_handlers import handle_batch_operations


async def handle_tool_call(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls and dispatch to appropriate handlers."""

    # File operations
    if name == "create_diagram":
        return handle_create_diagram(arguments)
    elif name == "load_diagram":
        return handle_load_diagram(arguments)
    elif name == "save_diagram":
        return handle_save_diagram(arguments)

    # Cell operations
    elif name == "list_cells":
        return handle_list_cells(arguments)
    elif name == "get_cell":
        return handle_get_cell(arguments)
    elif name == "update_cell":
        return handle_update_cell(arguments)
    elif name == "delete_cell":
        return handle_delete_cell(arguments)
    elif name == "add_shape":
        return handle_add_shape(arguments)
    elif name == "add_connection":
        return handle_add_connection(arguments)

    # Binding operations
    elif name == "bind_nodes":
        return handle_bind_nodes(arguments)
    elif name == "unbind_nodes":
        return handle_unbind_nodes(arguments)
    elif name == "get_bound_nodes":
        return handle_get_bound_nodes(arguments)
    elif name == "move_shape":
        return handle_move_shape(arguments)

    # Analysis operations
    elif name == "detect_line_crossings":
        return handle_detect_line_crossings(arguments)
    elif name == "suggest_bindings":
        return handle_suggest_bindings(arguments)
    elif name == "detect_overlaps":
        return handle_detect_overlaps(arguments)

    # Batch operations
    elif name == "batch_operations":
        return handle_batch_operations(arguments)

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]
