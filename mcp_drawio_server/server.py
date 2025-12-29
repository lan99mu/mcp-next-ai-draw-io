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
"""

import asyncio
from typing import Any, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .diagram import Diagram
from .xml_operations import (
    parse_drawio_xml,
    get_cells_from_xml,
    update_cell_in_xml,
    delete_cell_in_xml,
)
from .file_operations import load_diagram_file, save_diagram_file


# Global diagram storage
current_diagram: Optional[Diagram] = None
# Store raw XML for loaded diagrams (vs. programmatically created diagrams in current_diagram)
current_xml: Optional[str] = None


def get_or_create_diagram() -> Diagram:
    """Get or create the current diagram"""
    global current_diagram
    if current_diagram is None:
        current_diagram = Diagram()
    return current_diagram


# Initialize MCP server
app = Server("mcp-drawio-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="create_diagram",
            description="Create a new Draw.io diagram from scratch. This initializes a new diagram in memory.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the diagram",
                        "default": "Untitled"
                    }
                }
            }
        ),
        Tool(
            name="load_diagram",
            description="Load an existing .drawio file from disk. This allows you to read and modify existing diagrams.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the .drawio file to load"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="save_diagram",
            description="Save the current diagram to a .drawio file on disk.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path where the .drawio file should be saved"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="get_diagram_xml",
            description="Get the current diagram as Draw.io XML. This returns the complete XML structure that can be inspected or modified.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="set_diagram_xml",
            description="Set the diagram from raw Draw.io XML. This allows direct XML manipulation.",
            inputSchema={
                "type": "object",
                "properties": {
                    "xml": {
                        "type": "string",
                        "description": "Complete Draw.io XML content"
                    }
                },
                "required": ["xml"]
            }
        ),
        Tool(
            name="list_cells",
            description="List all cells (shapes and connections) in the diagram with their IDs, labels, and types. Useful for understanding the diagram structure before making modifications.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_cell",
            description="Get detailed information about a specific cell by its ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "cell_id": {
                        "type": "string",
                        "description": "The ID of the cell to retrieve"
                    }
                },
                "required": ["cell_id"]
            }
        ),
        Tool(
            name="update_cell",
            description="Update a specific cell by ID. You can modify its label, position, size, style, etc.",
            inputSchema={
                "type": "object",
                "properties": {
                    "cell_id": {
                        "type": "string",
                        "description": "The ID of the cell to update"
                    },
                    "value": {
                        "type": "string",
                        "description": "New label/value for the cell"
                    },
                    "x": {
                        "type": "number",
                        "description": "New X coordinate"
                    },
                    "y": {
                        "type": "number",
                        "description": "New Y coordinate"
                    },
                    "width": {
                        "type": "number",
                        "description": "New width"
                    },
                    "height": {
                        "type": "number",
                        "description": "New height"
                    },
                    "style": {
                        "type": "string",
                        "description": "New style string"
                    }
                },
                "required": ["cell_id"]
            }
        ),
        Tool(
            name="delete_cell",
            description="Delete a specific cell by ID from the diagram.",
            inputSchema={
                "type": "object",
                "properties": {
                    "cell_id": {
                        "type": "string",
                        "description": "The ID of the cell to delete"
                    }
                },
                "required": ["cell_id"]
            }
        ),
        Tool(
            name="add_shape",
            description="Add a new shape/node to the diagram. Returns the ID of the created shape.",
            inputSchema={
                "type": "object",
                "properties": {
                    "label": {
                        "type": "string",
                        "description": "Label text for the shape"
                    },
                    "x": {
                        "type": "number",
                        "description": "X coordinate (default: 0)",
                        "default": 0
                    },
                    "y": {
                        "type": "number",
                        "description": "Y coordinate (default: 0)",
                        "default": 0
                    },
                    "width": {
                        "type": "number",
                        "description": "Width of the shape (default: 120)",
                        "default": 120
                    },
                    "height": {
                        "type": "number",
                        "description": "Height of the shape (default: 60)",
                        "default": 60
                    },
                    "shape_type": {
                        "type": "string",
                        "description": "Type of shape (default: rectangle). Includes basic shapes (rectangle, ellipse, diamond, parallelogram, hexagon, cylinder, cloud), activity diagram shapes (activity_start, activity_end, activity_action, activity_decision, activity_fork, activity_join, activity_send_signal, activity_receive_signal, activity_note), and swimlane shapes (swimlane_pool, swimlane_h, swimlane_v, container).",
                        "enum": [
                            "rectangle", "ellipse", "diamond", "parallelogram", "hexagon", "cylinder", "cloud",
                            "activity_start", "activity_end", "activity_action", "activity_decision", 
                            "activity_fork", "activity_join", "activity_send_signal", "activity_receive_signal", "activity_note",
                            "swimlane_pool", "swimlane_h", "swimlane_v", "container"
                        ],
                        "default": "rectangle"
                    },
                    "style": {
                        "type": "string",
                        "description": "Custom Draw.io style string (optional)",
                        "default": ""
                    }
                },
                "required": ["label"]
            }
        ),
        Tool(
            name="add_connection",
            description="Add a connection/edge between two shapes in the diagram. Supports label positioning. Returns the ID of the created connection.",
            inputSchema={
                "type": "object",
                "properties": {
                    "source_id": {
                        "type": "string",
                        "description": "ID of the source shape"
                    },
                    "target_id": {
                        "type": "string",
                        "description": "ID of the target shape"
                    },
                    "label": {
                        "type": "string",
                        "description": "Label text for the connection (optional)",
                        "default": ""
                    },
                    "arrow_type": {
                        "type": "string",
                        "description": "Arrow type (default: classic)",
                        "enum": ["classic", "block", "open", "oval", "diamond", "none"],
                        "default": "classic"
                    },
                    "style": {
                        "type": "string",
                        "description": "Custom Draw.io style string (optional)",
                        "default": ""
                    },
                    "label_position": {
                        "type": "string",
                        "description": "Position of the label relative to the edge: 'left', 'right', or 'center' (optional)",
                        "enum": ["left", "right", "center"]
                    },
                    "label_offset_x": {
                        "type": "number",
                        "description": "Horizontal offset for the label position in pixels (optional)"
                    },
                    "label_offset_y": {
                        "type": "number",
                        "description": "Vertical offset for the label position in pixels (optional)"
                    },
                    "label_background_color": {
                        "type": "string",
                        "description": "Background color for the label, e.g., '#ffffff' or 'none' (optional)"
                    }
                },
                "required": ["source_id", "target_id"]
            }
        ),
        Tool(
            name="list_shapes",
            description="List all shapes in the diagram (deprecated: use list_cells instead for more complete information).",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    global current_diagram, current_xml
    
    if name == "create_diagram":
        diagram_name = arguments.get("name", "Untitled")
        current_diagram = Diagram(name=diagram_name)
        current_xml = None  # Reset XML when creating new diagram
        return [TextContent(
            type="text",
            text=f"Created new diagram: {diagram_name}\n\nYou can now add shapes and connections using add_shape and add_connection tools."
        )]
    
    elif name == "load_diagram":
        try:
            file_path = arguments["path"]
            current_xml = load_diagram_file(file_path)
            current_diagram = None  # Clear in-memory diagram when loading from file
            
            # Parse and get basic info
            cells = get_cells_from_xml(current_xml)
            vertex_count = sum(1 for c in cells if c['vertex'])
            edge_count = sum(1 for c in cells if c['edge'])
            
            return [TextContent(
                type="text",
                text=f"Loaded diagram from: {file_path}\n\nDiagram contains:\n- {vertex_count} shapes\n- {edge_count} connections\n- {len(cells)} total cells\n\nUse list_cells to see all elements, or get_diagram_xml to see the full XML."
            )]
        except FileNotFoundError as e:
            return [TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error loading diagram: {str(e)}"
            )]
    
    elif name == "save_diagram":
        try:
            file_path = arguments["path"]
            
            # Get XML content
            if current_xml:
                xml_content = current_xml
            elif current_diagram:
                xml_content = current_diagram.to_drawio_xml()
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
            return [TextContent(
                type="text",
                text=f"Error saving diagram: {str(e)}"
            )]
    
    elif name == "get_diagram_xml":
        if current_xml:
            xml_content = current_xml
        elif current_diagram:
            xml_content = current_diagram.to_drawio_xml()
        else:
            return [TextContent(
                type="text",
                text="No diagram available. Create a new diagram or load an existing one."
            )]
        
        return [TextContent(
            type="text",
            text=f"Draw.io XML ({len(xml_content)} bytes):\n\n{xml_content}"
        )]
    
    elif name == "set_diagram_xml":
        try:
            xml_content = arguments["xml"]
            # Validate XML by parsing it
            doc = parse_drawio_xml(xml_content)
            
            # Verify it's valid Draw.io XML (has mxGraphModel or mxfile)
            if not (doc.getElementsByTagName('mxGraphModel') or doc.getElementsByTagName('mxfile')):
                return [TextContent(
                    type="text",
                    text="Error: Invalid Draw.io XML - missing mxGraphModel or mxfile element"
                )]
            
            current_xml = xml_content
            current_diagram = None  # Clear in-memory diagram
            
            cells = get_cells_from_xml(xml_content)
            return [TextContent(
                type="text",
                text=f"Diagram XML updated successfully.\n\nDiagram now contains {len(cells)} cells."
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error: Invalid XML - {str(e)}"
            )]
    
    elif name == "list_cells":
        if current_xml:
            cells = get_cells_from_xml(current_xml)
        elif current_diagram:
            xml_content = current_diagram.to_drawio_xml()
            cells = get_cells_from_xml(xml_content)
        else:
            return [TextContent(
                type="text",
                text="No diagram available. Create a new diagram or load an existing one."
            )]
        
        if not cells:
            return [TextContent(
                type="text",
                text="No cells in the diagram yet."
            )]
        
        # Format cells list
        cells_list = []
        for cell in cells:
            cell_type = "Shape" if cell['vertex'] else ("Connection" if cell['edge'] else "Unknown")
            label = cell['value'] or "(no label)"
            pos = f"at ({cell.get('x', '?')}, {cell.get('y', '?')})" if cell['vertex'] else ""
            if cell['edge']:
                pos = f"from {cell['source']} to {cell['target']}"
            
            cells_list.append(f"- ID: {cell['id']}, Type: {cell_type}, Label: {label} {pos}")
        
        return [TextContent(
            type="text",
            text=f"Cells in diagram ({len(cells)} total):\n\n" + "\n".join(cells_list)
        )]
    
    elif name == "get_cell":
        cell_id = arguments["cell_id"]
        
        if current_xml:
            cells = get_cells_from_xml(current_xml)
        elif current_diagram:
            xml_content = current_diagram.to_drawio_xml()
            cells = get_cells_from_xml(xml_content)
        else:
            return [TextContent(
                type="text",
                text="No diagram available."
            )]
        
        # Find the cell
        cell = next((c for c in cells if c['id'] == cell_id), None)
        if not cell:
            return [TextContent(
                type="text",
                text=f"Cell not found: {cell_id}"
            )]
        
        # Format cell info
        cell_info = f"Cell ID: {cell_id}\n"
        cell_info += f"Type: {'Shape' if cell['vertex'] else 'Connection'}\n"
        cell_info += f"Label: {cell['value'] or '(no label)'}\n"
        cell_info += f"Style: {cell['style'] or '(default)'}\n"
        if cell['vertex']:
            cell_info += f"Position: ({cell.get('x', 'N/A')}, {cell.get('y', 'N/A')})\n"
            cell_info += f"Size: {cell.get('width', 'N/A')} x {cell.get('height', 'N/A')}\n"
        if cell['edge']:
            cell_info += f"Source: {cell['source']}\n"
            cell_info += f"Target: {cell['target']}\n"
        
        return [TextContent(
            type="text",
            text=cell_info
        )]
    
    elif name == "update_cell":
        cell_id = arguments["cell_id"]
        
        if current_xml:
            try:
                # Build updates dict from arguments
                updates = {}
                for key in ['value', 'x', 'y', 'width', 'height', 'style']:
                    if key in arguments:
                        updates[key] = arguments[key]
                
                current_xml = update_cell_in_xml(current_xml, cell_id, **updates)
                
                return [TextContent(
                    type="text",
                    text=f"Cell {cell_id} updated successfully.\n\nUpdated fields: {', '.join(updates.keys())}"
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error updating cell: {str(e)}"
                )]
        else:
            return [TextContent(
                type="text",
                text="Error: Can only update cells in loaded diagrams. Use load_diagram first."
            )]
    
    elif name == "delete_cell":
        cell_id = arguments["cell_id"]
        
        if current_xml:
            try:
                current_xml = delete_cell_in_xml(current_xml, cell_id)
                return [TextContent(
                    type="text",
                    text=f"Cell {cell_id} deleted successfully."
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error deleting cell: {str(e)}"
                )]
        else:
            return [TextContent(
                type="text",
                text="Error: Can only delete cells in loaded diagrams. Use load_diagram first."
            )]
    
    elif name == "add_shape":
        diagram = get_or_create_diagram()
        shape_id = diagram.add_shape(
            label=arguments["label"],
            x=arguments.get("x", 0),
            y=arguments.get("y", 0),
            width=arguments.get("width", 120),
            height=arguments.get("height", 60),
            shape_type=arguments.get("shape_type", "rectangle"),
            style=arguments.get("style", "")
        )
        # Update current_xml if we're working with XML
        if current_xml:
            current_xml = diagram.to_drawio_xml()
        
        return [TextContent(
            type="text",
            text=f"Added shape '{arguments['label']}' with ID: {shape_id}"
        )]
    
    elif name == "add_connection":
        diagram = get_or_create_diagram()
        try:
            conn_id = diagram.add_connection(
                source_id=arguments["source_id"],
                target_id=arguments["target_id"],
                label=arguments.get("label", ""),
                arrow_type=arguments.get("arrow_type", "classic"),
                style=arguments.get("style", ""),
                label_position=arguments.get("label_position"),
                label_offset_x=arguments.get("label_offset_x"),
                label_offset_y=arguments.get("label_offset_y"),
                label_background_color=arguments.get("label_background_color")
            )
            # Update current_xml if we're working with XML
            if current_xml:
                current_xml = diagram.to_drawio_xml()
            
            return [TextContent(
                type="text",
                text=f"Added connection from {arguments['source_id']} to {arguments['target_id']} with ID: {conn_id}"
            )]
        except ValueError as e:
            return [TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )]
    
    elif name == "list_shapes":
        # Deprecated - redirect to list_cells
        return await call_tool("list_cells", {})
    
    else:
        return [TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]


async def main():
    """Main entry point for the server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
