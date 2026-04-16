#!/usr/bin/env python3
"""
File operation handlers.

Handlers for create_diagram, load_diagram, and save_diagram tools.
"""

from datetime import datetime, timezone
from typing import Any
from mcp.types import TextContent

from .state import diagram_state
from ..xml_operations import get_cells_from_xml
from ..file_operations import load_diagram_file, save_diagram_file
from ..diagram import Diagram


def handle_create_diagram(arguments: Any) -> list[TextContent]:
    """Handle create_diagram tool call."""
    diagram_name = arguments.get("name", "Untitled")
    autosave_path: str | None = arguments.get("autosave_path")

    diagram_state.reset()
    diagram_state.current_diagram = Diagram(name=diagram_name)
    if autosave_path:
        diagram_state.autosave_path = autosave_path
        diagram_state.autosave_enabled = True

    autosave_note = f" Autosave → {autosave_path}" if autosave_path else ""
    return [TextContent(
        type="text",
        text=f"Created: {diagram_name}.{autosave_note}"
    )]


def handle_load_diagram(arguments: Any) -> list[TextContent]:
    """Handle load_diagram tool call."""
    try:
        file_path = arguments["path"]
        autosave: bool = arguments.get("autosave", False)

        diagram_state.reset()
        diagram_state.current_xml = load_diagram_file(file_path)
        if autosave:
            diagram_state.autosave_path = file_path
            diagram_state.autosave_enabled = True

        cells = get_cells_from_xml(diagram_state.current_xml)
        vertex_count = sum(1 for c in cells if c['vertex'])
        edge_count = sum(1 for c in cells if c['edge'])
        autosave_note = " [autosave ON]" if autosave else ""

        return [TextContent(
            type="text",
            text=(
                f"Loaded: {file_path}{autosave_note} | "
                f"{vertex_count} shapes, {edge_count} connections"
            )
        )]
    except FileNotFoundError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error loading diagram: {str(e)}")]


def handle_save_diagram(arguments: Any) -> list[TextContent]:
    """Handle save_diagram tool call."""
    try:
        file_path = arguments["path"]

        xml_content = diagram_state._current_xml_content()
        if xml_content is None:
            return [TextContent(
                type="text",
                text="Error: No diagram to save. Create a diagram first or load an existing one."
            )]

        bytes_written = save_diagram_file(file_path, xml_content)
        diagram_state.write_count += 1
        diagram_state.last_save_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        diagram_state.last_save_bytes = bytes_written

        return [TextContent(
            type="text",
            text=(
                f"Saved: {file_path}"
                f" | v{diagram_state.write_count}"
                f" | {bytes_written}B"
                f" | {diagram_state.last_save_time}"
            )
        )]
    except Exception as e:
        return [TextContent(type="text", text=f"Error saving diagram: {str(e)}")]

