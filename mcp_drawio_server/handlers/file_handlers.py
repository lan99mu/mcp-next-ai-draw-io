#!/usr/bin/env python3
"""
File operation handlers.

Handlers for create_diagram, load_diagram, and save_diagram tools.

Note: The _handle_get_diagram_xml and _handle_set_diagram_xml functions are 
internal helpers and are NOT exposed as public tools. Direct XML manipulation
is discouraged - use the high-level tools (add_shape, add_connection, etc.) instead.
"""

from typing import Any
from mcp.types import TextContent

from .state import diagram_state
from ..xml_operations import parse_drawio_xml, get_cells_from_xml
from ..file_operations import load_diagram_file, save_diagram_file
from ..diagram import Diagram


def handle_create_diagram(arguments: Any) -> list[TextContent]:
    """Handle create_diagram tool call."""
    diagram_name = arguments.get("name", "Untitled")
    diagram_state.current_diagram = Diagram(name=diagram_name)
    diagram_state.current_xml = None
    return [TextContent(
        type="text",
        text=f"Created new diagram: {diagram_name}\n\nYou can now add shapes and connections using add_shape and add_connection tools."
    )]


def handle_load_diagram(arguments: Any) -> list[TextContent]:
    """Handle load_diagram tool call."""
    try:
        file_path = arguments["path"]
        diagram_state.current_xml = load_diagram_file(file_path)
        diagram_state.current_diagram = None
        
        cells = get_cells_from_xml(diagram_state.current_xml)
        vertex_count = sum(1 for c in cells if c['vertex'])
        edge_count = sum(1 for c in cells if c['edge'])
        
        return [TextContent(
            type="text",
            text=f"Loaded diagram from: {file_path}\n\nDiagram contains:\n- {vertex_count} shapes\n- {edge_count} connections\n- {len(cells)} total cells\n\nUse list_cells to see all elements."
        )]
    except FileNotFoundError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error loading diagram: {str(e)}")]


def handle_save_diagram(arguments: Any) -> list[TextContent]:
    """Handle save_diagram tool call."""
    try:
        file_path = arguments["path"]
        
        if diagram_state.current_xml:
            xml_content = diagram_state.current_xml
        elif diagram_state.current_diagram:
            xml_content = diagram_state.current_diagram.to_drawio_xml()
        else:
            return [TextContent(
                type="text",
                text="Error: No diagram to save. Create a diagram first or load an existing one."
            )]
        
        bytes_written = save_diagram_file(file_path, xml_content)
        
        return [TextContent(
            type="text",
            text=f"Diagram saved to: {file_path}\n\nFile size: {bytes_written} bytes"
        )]
    except Exception as e:
        return [TextContent(type="text", text=f"Error saving diagram: {str(e)}")]


def _handle_get_diagram_xml(arguments: Any) -> list[TextContent]:
    """Internal helper for get_diagram_xml. Not exposed as a public tool."""
    if diagram_state.current_xml:
        xml_content = diagram_state.current_xml
    elif diagram_state.current_diagram:
        xml_content = diagram_state.current_diagram.to_drawio_xml()
    else:
        return [TextContent(
            type="text",
            text="No diagram available. Create a new diagram or load an existing one."
        )]
    
    return [TextContent(
        type="text",
        text=f"Draw.io XML ({len(xml_content)} bytes):\n\n{xml_content}"
    )]


def _handle_set_diagram_xml(arguments: Any) -> list[TextContent]:
    """Internal helper for set_diagram_xml. Not exposed as a public tool."""
    try:
        xml_content = arguments["xml"]
        doc = parse_drawio_xml(xml_content)
        
        if not (doc.getElementsByTagName('mxGraphModel') or doc.getElementsByTagName('mxfile')):
            return [TextContent(
                type="text",
                text="Error: Invalid Draw.io XML - missing mxGraphModel or mxfile element"
            )]
        
        diagram_state.current_xml = xml_content
        diagram_state.current_diagram = None
        
        cells = get_cells_from_xml(xml_content)
        return [TextContent(
            type="text",
            text=f"Diagram XML updated successfully.\n\nDiagram now contains {len(cells)} cells."
        )]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: Invalid XML - {str(e)}")]
