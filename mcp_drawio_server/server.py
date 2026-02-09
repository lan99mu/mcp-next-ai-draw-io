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
from mcp.types import Tool, TextContent, Prompt, PromptArgument, PromptMessage, GetPromptResult

from .diagram import Diagram
from .xml_operations import (
    parse_drawio_xml,
    get_cells_from_xml,
    update_cell_in_xml,
    delete_cell_in_xml,
)
from .file_operations import load_diagram_file, save_diagram_file
from .crossing_detector import detect_crossings


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


def safe_float(value, default=0.0) -> float:
    """Safely convert a value to float, returning default if conversion fails"""
    if value is None or value == '':
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def bind_nodes_helper(diagram: Diagram, node_ids: list[str]) -> None:
    """Helper function to bind multiple nodes together"""
    for node_id in node_ids:
        # Get the other nodes in the group (all except this one)
        other_nodes = [nid for nid in node_ids if nid != node_id]
        # Update the bound_nodes list to include all other nodes in the group
        diagram.shapes[node_id].bound_nodes = list(set(diagram.shapes[node_id].bound_nodes + other_nodes))


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
            description="List all cells (shapes and connections) in the diagram with their IDs, labels, types, and BINDING information. Shows which nodes are bound together (moving as a group). IMPORTANT: Check bindings before making changes - if nodes are bound, you only need to adjust ONE node and all bound nodes move together automatically. This is KEY for efficient local adjustments.",
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
                        "description": "Type of shape (default: rectangle). Includes basic shapes (rectangle, ellipse, diamond, parallelogram, hexagon, cylinder, cloud), activity diagram shapes (activity_start, activity_end, activity_action, activity_decision, activity_fork, activity_join, activity_send_signal, activity_receive_signal, activity_note), swimlane shapes (swimlane_pool, swimlane_h, swimlane_v, container), and UML class diagram shapes (uml_class, uml_interface, uml_abstract_class, uml_enum, uml_package, uml_note).",
                        "enum": [
                            "rectangle", "ellipse", "diamond", "parallelogram", "hexagon", "cylinder", "cloud",
                            "activity_start", "activity_end", "activity_action", "activity_decision", 
                            "activity_fork", "activity_join", "activity_send_signal", "activity_receive_signal", "activity_note",
                            "swimlane_pool", "swimlane_h", "swimlane_v", "container",
                            "uml_class", "uml_interface", "uml_abstract_class", "uml_enum", "uml_package", "uml_note"
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
            description="Add a connection/edge between two shapes in the diagram. Supports label positioning, entry/exit points, and waypoint routing. Returns the ID of the created connection.",
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
                    },
                    "entry_x": {
                        "type": "number",
                        "description": "Entry point X coordinate on target shape (normalized 0-1, where 0=left, 0.5=center, 1=right) (optional)"
                    },
                    "entry_y": {
                        "type": "number",
                        "description": "Entry point Y coordinate on target shape (normalized 0-1, where 0=top, 0.5=center, 1=bottom) (optional)"
                    },
                    "exit_x": {
                        "type": "number",
                        "description": "Exit point X coordinate on source shape (normalized 0-1, where 0=left, 0.5=center, 1=right) (optional)"
                    },
                    "exit_y": {
                        "type": "number",
                        "description": "Exit point Y coordinate on source shape (normalized 0-1, where 0=top, 0.5=center, 1=bottom) (optional)"
                    },
                    "waypoints": {
                        "type": "array",
                        "items": {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 2,
                            "maxItems": 2
                        },
                        "description": "List of intermediate routing points as [x, y] coordinates in absolute pixels (optional)"
                    },
                    "source_point": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "description": "Explicit source point as [x, y] coordinates in absolute pixels (optional, overrides exit point)"
                    },
                    "target_point": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "description": "Explicit target point as [x, y] coordinates in absolute pixels (optional, overrides entry point)"
                    }
                },
                "required": ["source_id", "target_id"]
            }
        ),
        Tool(
            name="bind_nodes",
            description="Bind multiple nodes together so they move as a group. When you move one node in a bound group, all bound nodes will move together by the same offset. USE THIS when nodes are logically related (e.g., a service and its database, a component and its label). This enables EFFICIENT LOCAL ADJUSTMENTS - you only need to move ONE node instead of multiple nodes individually. BEST PRACTICE: Bind related nodes immediately after creating them.",
            inputSchema={
                "type": "object",
                "properties": {
                    "node_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of node IDs to bind together (minimum 2 nodes)"
                    }
                },
                "required": ["node_ids"]
            }
        ),
        Tool(
            name="unbind_nodes",
            description="Remove nodes from their binding group. The specified nodes will no longer move together with other nodes.",
            inputSchema={
                "type": "object",
                "properties": {
                    "node_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of node IDs to unbind"
                    }
                },
                "required": ["node_ids"]
            }
        ),
        Tool(
            name="get_bound_nodes",
            description="Get the list of nodes that are bound to a specific node.",
            inputSchema={
                "type": "object",
                "properties": {
                    "node_id": {
                        "type": "string",
                        "description": "The node ID to query bindings for"
                    }
                },
                "required": ["node_id"]
            }
        ),
        Tool(
            name="move_shape",
            description="Move a shape to a new position. If the shape is bound to other nodes, all bound nodes will also move by the same offset AUTOMATICALLY. This is the PREFERRED way to make local adjustments to groups of related nodes. Check list_cells output to see which nodes are bound before moving.",
            inputSchema={
                "type": "object",
                "properties": {
                    "shape_id": {
                        "type": "string",
                        "description": "The ID of the shape to move"
                    },
                    "new_x": {
                        "type": "number",
                        "description": "New X coordinate for the shape"
                    },
                    "new_y": {
                        "type": "number",
                        "description": "New Y coordinate for the shape"
                    }
                },
                "required": ["shape_id", "new_x", "new_y"]
            }
        ),
        Tool(
            name="detect_line_crossings",
            description="Detect line crossings in the diagram and provide position hints for adjustments. This helps identify where connections (edges) cross each other and suggests ways to fix them.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="suggest_bindings",
            description="Analyze the diagram and suggest which nodes should be bound together based on proximity, naming patterns, and connections. Use this to identify related nodes that should move as a group for efficient local adjustments. Helps you discover opportunities to use bindings instead of editing many nodes individually.",
            inputSchema={
                "type": "object",
                "properties": {
                    "proximity_threshold": {
                        "type": "number",
                        "description": "Maximum distance (in pixels) between nodes to consider them related. Default is 200.",
                        "default": 200
                    }
                }
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
        
        # Format cells list with coordinate system information
        cells_list = []
        for cell in cells:
            cell_type = "Shape" if cell['vertex'] else ("Connection" if cell['edge'] else "Unknown")
            label = cell['value'] or "(no label)"
            
            if cell['vertex']:
                # For shapes, show detailed coordinate information
                x = safe_float(cell.get('x'))
                y = safe_float(cell.get('y'))
                width = safe_float(cell.get('width'))
                height = safe_float(cell.get('height'))
                # Calculate center point
                center_x = x + width / 2
                center_y = y + height / 2
                pos = f"at ({x}, {y}), size ({width}x{height}), center ({center_x}, {center_y})"
                
                # Show binding information prominently
                bound_nodes = cell.get('bound_nodes', [])
                if bound_nodes:
                    pos += f" [BOUND to: {', '.join(bound_nodes)}]"
            elif cell['edge']:
                pos = f"from {cell['source']} to {cell['target']}"
            else:
                pos = ""
            
            cells_list.append(f"- ID: {cell['id']}, Type: {cell_type}, Label: '{label}', {pos}")
        
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
            x = safe_float(cell.get('x'))
            y = safe_float(cell.get('y'))
            width = safe_float(cell.get('width'))
            height = safe_float(cell.get('height'))
            center_x = x + width / 2
            center_y = y + height / 2
            cell_info += f"Position (top-left): ({x}, {y})\n"
            cell_info += f"Size: {width} x {height}\n"
            cell_info += f"Center: ({center_x}, {center_y})\n"
            cell_info += f"Bounding box: ({x}, {y}) to ({x + width}, {y + height})\n"
            
            # Show bound nodes if any
            bound_nodes = cell.get('bound_nodes', [])
            if bound_nodes:
                cell_info += f"Bound to {len(bound_nodes)} node(s): {', '.join(bound_nodes)}\n"
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
            # Convert waypoints from list of lists to list of tuples
            waypoints = arguments.get("waypoints")
            if waypoints:
                waypoints = [tuple(wp) for wp in waypoints]
            
            # Convert source/target points from lists to tuples
            source_point = arguments.get("source_point")
            if source_point:
                source_point = tuple(source_point)
            
            target_point = arguments.get("target_point")
            if target_point:
                target_point = tuple(target_point)
            
            conn_id = diagram.add_connection(
                source_id=arguments["source_id"],
                target_id=arguments["target_id"],
                label=arguments.get("label", ""),
                arrow_type=arguments.get("arrow_type", "classic"),
                style=arguments.get("style", ""),
                label_position=arguments.get("label_position"),
                label_offset_x=arguments.get("label_offset_x"),
                label_offset_y=arguments.get("label_offset_y"),
                label_background_color=arguments.get("label_background_color"),
                entry_x=arguments.get("entry_x"),
                entry_y=arguments.get("entry_y"),
                exit_x=arguments.get("exit_x"),
                exit_y=arguments.get("exit_y"),
                waypoints=waypoints,
                source_point=source_point,
                target_point=target_point
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
    
    elif name == "bind_nodes":
        diagram = get_or_create_diagram()
        node_ids = arguments["node_ids"]
        
        if len(node_ids) < 2:
            return [TextContent(
                type="text",
                text="Error: At least 2 nodes are required to create a binding."
            )]
        
        # Verify all nodes exist
        missing_nodes = [nid for nid in node_ids if nid not in diagram.shapes]
        if missing_nodes:
            return [TextContent(
                type="text",
                text=f"Error: The following node IDs were not found: {', '.join(missing_nodes)}"
            )]
        
        # Bind the nodes together using helper function
        bind_nodes_helper(diagram, node_ids)
        
        # Update current_xml if we're working with XML
        if current_xml:
            current_xml = diagram.to_drawio_xml()
        
        return [TextContent(
            type="text",
            text=f"Successfully bound {len(node_ids)} nodes together: {', '.join(node_ids)}\n\nThese nodes will now move together when any one of them is moved."
        )]
    
    elif name == "unbind_nodes":
        diagram = get_or_create_diagram()
        node_ids = arguments["node_ids"]
        
        # Verify all nodes exist
        missing_nodes = [nid for nid in node_ids if nid not in diagram.shapes]
        if missing_nodes:
            return [TextContent(
                type="text",
                text=f"Error: The following node IDs were not found: {', '.join(missing_nodes)}"
            )]
        
        # Remove bindings for specified nodes
        for node_id in node_ids:
            bound_to = diagram.shapes[node_id].bound_nodes.copy()
            diagram.shapes[node_id].bound_nodes = []
            
            # Also remove this node from other nodes' binding lists
            for other_id in bound_to:
                if other_id in diagram.shapes:
                    if node_id in diagram.shapes[other_id].bound_nodes:
                        diagram.shapes[other_id].bound_nodes.remove(node_id)
        
        # Update current_xml if we're working with XML
        if current_xml:
            current_xml = diagram.to_drawio_xml()
        
        return [TextContent(
            type="text",
            text=f"Successfully unbound {len(node_ids)} nodes: {', '.join(node_ids)}"
        )]
    
    elif name == "get_bound_nodes":
        diagram = get_or_create_diagram()
        node_id = arguments["node_id"]
        
        if node_id not in diagram.shapes:
            return [TextContent(
                type="text",
                text=f"Error: Node ID '{node_id}' not found."
            )]
        
        bound_nodes = diagram.shapes[node_id].bound_nodes
        
        if not bound_nodes:
            return [TextContent(
                type="text",
                text=f"Node '{node_id}' is not bound to any other nodes."
            )]
        
        return [TextContent(
            type="text",
            text=f"Node '{node_id}' is bound to {len(bound_nodes)} node(s):\n\n" + "\n".join(f"- {nid}" for nid in bound_nodes)
        )]
    
    elif name == "move_shape":
        diagram = get_or_create_diagram()
        shape_id = arguments["shape_id"]
        new_x = arguments["new_x"]
        new_y = arguments["new_y"]
        
        if shape_id not in diagram.shapes:
            return [TextContent(
                type="text",
                text=f"Error: Shape ID '{shape_id}' not found."
            )]
        
        shape = diagram.shapes[shape_id]
        old_x = shape.x
        old_y = shape.y
        
        # Calculate offset
        offset_x = new_x - old_x
        offset_y = new_y - old_y
        
        # Move the shape
        shape.x = new_x
        shape.y = new_y
        
        # Move all bound nodes by the same offset
        moved_nodes = [shape_id]
        for bound_id in shape.bound_nodes:
            if bound_id in diagram.shapes:
                diagram.shapes[bound_id].x += offset_x
                diagram.shapes[bound_id].y += offset_y
                moved_nodes.append(bound_id)
        
        # Update current_xml if we're working with XML
        if current_xml:
            current_xml = diagram.to_drawio_xml()
        
        if len(moved_nodes) > 1:
            return [TextContent(
                type="text",
                text=f"Moved shape '{shape_id}' from ({old_x}, {old_y}) to ({new_x}, {new_y}).\n\nAlso moved {len(moved_nodes) - 1} bound node(s) by offset ({offset_x}, {offset_y}):\n" + "\n".join(f"- {nid}" for nid in moved_nodes[1:])
            )]
        else:
            return [TextContent(
                type="text",
                text=f"Moved shape '{shape_id}' from ({old_x}, {old_y}) to ({new_x}, {new_y})."
            )]
    
    elif name == "detect_line_crossings":
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
        
        # Detect crossings
        crossings = detect_crossings(cells)
        
        if not crossings:
            return [TextContent(
                type="text",
                text="No line crossings detected in the diagram. All connections are clear!"
            )]
        
        # Format crossing information
        result_parts = [f"Detected {len(crossings)} line crossing(s):\n"]
        
        for i, crossing in enumerate(crossings, 1):
            result_parts.append(f"\n{i}. Crossing between:")
            result_parts.append(f"   - Connection '{crossing['connection1_label']}' (ID: {crossing['connection1_id']})")
            result_parts.append(f"   - Connection '{crossing['connection2_label']}' (ID: {crossing['connection2_id']})")
            result_parts.append(f"   {crossing['suggestion']}")
        
        return [TextContent(
            type="text",
            text="\n".join(result_parts)
        )]
    
    elif name == "suggest_bindings":
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
        
        proximity_threshold = arguments.get("proximity_threshold", 200)
        
        # Get all shapes
        shapes = [cell for cell in cells if cell.get('vertex')]
        
        if len(shapes) < 2:
            return [TextContent(
                type="text",
                text="Not enough shapes in the diagram to suggest bindings. Need at least 2 shapes."
            )]
        
        # Analyze and suggest bindings
        suggestions = []
        already_bound = set()
        
        for i, shape1 in enumerate(shapes):
            for shape2 in shapes[i + 1:]:
                shape1_id = shape1['id']
                shape2_id = shape2['id']
                
                # Skip if already bound to each other
                bound_nodes_1 = shape1.get('bound_nodes', [])
                bound_nodes_2 = shape2.get('bound_nodes', [])
                if shape2_id in bound_nodes_1 or shape1_id in bound_nodes_2:
                    pair_key = tuple(sorted([shape1_id, shape2_id]))
                    already_bound.add(pair_key)
                    continue
                
                # Calculate distance between centers
                x1 = safe_float(shape1.get('x', 0))
                y1 = safe_float(shape1.get('y', 0))
                w1 = safe_float(shape1.get('width', 120))
                h1 = safe_float(shape1.get('height', 60))
                center1_x = x1 + w1 / 2
                center1_y = y1 + h1 / 2
                
                x2 = safe_float(shape2.get('x', 0))
                y2 = safe_float(shape2.get('y', 0))
                w2 = safe_float(shape2.get('width', 120))
                h2 = safe_float(shape2.get('height', 60))
                center2_x = x2 + w2 / 2
                center2_y = y2 + h2 / 2
                
                distance = ((center2_x - center1_x) ** 2 + (center2_y - center1_y) ** 2) ** 0.5
                
                # Check if nodes are close enough
                if distance <= proximity_threshold:
                    label1 = shape1.get('value', shape1_id)
                    label2 = shape2.get('value', shape2_id)
                    
                    # Calculate reason score based on various factors
                    reasons = []
                    score = 0
                    
                    # Proximity score
                    proximity_score = int((1 - distance / proximity_threshold) * 100)
                    reasons.append(f"proximity: {proximity_score}% (distance: {distance:.1f}px)")
                    score += proximity_score
                    
                    # Vertical alignment (same or close X position)
                    if abs(center1_x - center2_x) < 50:
                        reasons.append("vertically aligned")
                        score += 20
                    
                    # Horizontal alignment (same or close Y position)
                    if abs(center1_y - center2_y) < 50:
                        reasons.append("horizontally aligned")
                        score += 20
                    
                    # Check for naming patterns suggesting relationship
                    label1_lower = label1.lower()
                    label2_lower = label2.lower()
                    
                    # Same prefix (e.g., "Service A" and "DB A")
                    label1_words = label1.split()
                    label2_words = label2.split()
                    if label1_words and label2_words:
                        if label1_words[-1] == label2_words[-1]:  # Same suffix
                            reasons.append(f"naming pattern: same suffix '{label1_words[-1]}'")
                            score += 30
                        elif label1_words[0] == label2_words[0]:  # Same prefix
                            reasons.append(f"naming pattern: same prefix '{label1_words[0]}'")
                            score += 25
                    
                    # Related keywords
                    related_pairs = [
                        ('service', 'db'), ('service', 'database'),
                        ('api', 'db'), ('api', 'database'),
                        ('app', 'db'), ('app', 'database'),
                        ('frontend', 'backend'),
                        ('client', 'server'),
                        ('cache', 'db'), ('cache', 'database')
                    ]
                    
                    for word1, word2 in related_pairs:
                        if (word1 in label1_lower and word2 in label2_lower) or \
                           (word2 in label1_lower and word1 in label2_lower):
                            reasons.append(f"related keywords: '{word1}' and '{word2}'")
                            score += 35
                            break
                    
                    # Only suggest if score is reasonable
                    if score >= 50:
                        suggestions.append({
                            'id1': shape1_id,
                            'id2': shape2_id,
                            'label1': label1,
                            'label2': label2,
                            'score': score,
                            'reasons': reasons,
                            'distance': distance
                        })
        
        # Sort by score (highest first)
        suggestions.sort(key=lambda x: x['score'], reverse=True)
        
        # Format output
        if not suggestions and not already_bound:
            return [TextContent(
                type="text",
                text=f"No binding suggestions found. No shapes are within {proximity_threshold}px of each other or have clear relationships."
            )]
        
        result_parts = []
        
        if already_bound:
            result_parts.append(f"✓ Found {len(already_bound)} existing binding(s):")
            for pair in sorted(already_bound):
                result_parts.append(f"  - {pair[0]} and {pair[1]} are already bound")
            result_parts.append("")
        
        if suggestions:
            result_parts.append(f"💡 Suggested {len(suggestions)} new binding(s) for efficient local adjustments:\n")
            
            for i, suggestion in enumerate(suggestions[:10], 1):  # Limit to top 10
                result_parts.append(f"{i}. Bind '{suggestion['label1']}' ({suggestion['id1']}) with '{suggestion['label2']}' ({suggestion['id2']})")
                result_parts.append(f"   Score: {suggestion['score']}/100")
                result_parts.append(f"   Reasons: {', '.join(suggestion['reasons'])}")
                result_parts.append(f"   → To bind: bind_nodes(node_ids=['{suggestion['id1']}', '{suggestion['id2']}'])")
                result_parts.append("")
            
            if len(suggestions) > 10:
                result_parts.append(f"... and {len(suggestions) - 10} more suggestions with lower scores")
            
            result_parts.append("\n✨ TIP: After binding, use move_shape() on just ONE node - all bound nodes move automatically!")
        
        return [TextContent(
            type="text",
            text="\n".join(result_parts)
        )]
    
    else:
        return [TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]


@app.list_prompts()
async def list_prompts() -> list[Prompt]:
    """List available prompt templates for common diagram workflows"""
    return [
        Prompt(
            name="create_flowchart",
            description="Efficiently create a flowchart diagram with proper node placement and automatic bindings for related elements. This workflow guides you through creating nodes, connecting them, and using bindings to group related elements.",
            arguments=[
                PromptArgument(
                    name="description",
                    description="High-level description of the flowchart (e.g., 'user login process', 'order fulfillment workflow')",
                    required=True
                )
            ]
        ),
        Prompt(
            name="add_connected_nodes",
            description="Add multiple related nodes with connections and automatic bindings. Best for extending existing diagrams efficiently by creating a group of related nodes that can be moved together.",
            arguments=[
                PromptArgument(
                    name="nodes_description",
                    description="Description of the nodes to add and their relationships (e.g., 'service, database, and cache nodes connected in sequence')",
                    required=True
                ),
                PromptArgument(
                    name="base_x",
                    description="Starting X coordinate for the new nodes (optional, default: 0)",
                    required=False
                ),
                PromptArgument(
                    name="base_y", 
                    description="Starting Y coordinate for the new nodes (optional, default: 0)",
                    required=False
                )
            ]
        ),
        Prompt(
            name="optimize_layout",
            description="Optimize diagram layout by detecting and fixing line crossings, suggesting bindings, and improving spacing. This helps clean up messy diagrams with minimal manual adjustments.",
            arguments=[]
        ),
        Prompt(
            name="modify_with_bindings",
            description="Efficiently modify an existing diagram by leveraging node bindings. This workflow shows how to check existing bindings and use them to make local adjustments by moving just one node instead of many.",
            arguments=[
                PromptArgument(
                    name="modification_description",
                    description="Description of what to modify (e.g., 'move the authentication section down', 'adjust database cluster spacing')",
                    required=True
                )
            ]
        ),
        Prompt(
            name="create_architecture_diagram",
            description="Create a software architecture diagram with proper layering and component grouping. Uses bindings to group related components that should move together.",
            arguments=[
                PromptArgument(
                    name="architecture_description",
                    description="Description of the architecture (e.g., '3-tier web application', 'microservices with API gateway')",
                    required=True
                )
            ]
        )
    ]


@app.get_prompt()
async def get_prompt(name: str, arguments: dict[str, str] | None) -> GetPromptResult:
    """Get a specific prompt template with instructions"""
    
    if name == "create_flowchart":
        description = arguments.get("description", "a flowchart") if arguments else "a flowchart"
        
        return GetPromptResult(
            description=f"Create {description} efficiently using bindings",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Create a flowchart for: {description}

WORKFLOW (follow this order to minimize model calls):

1. **Plan the structure**: Think about the main steps and their relationships
2. **Create nodes in logical groups**: 
   - Use add_shape() to create related nodes (e.g., all decision nodes, all process nodes)
   - Place them with proper spacing (150-200px between nodes)
3. **Bind related nodes immediately**:
   - After creating a group of related nodes, use bind_nodes() to group them
   - Example: bind_nodes(node_ids=["start", "process1", "decision1"])
   - This allows you to move the entire group by adjusting just ONE node later
4. **Add connections**: 
   - Use add_connection() between nodes
   - Set proper entry/exit points for clean routing
5. **Use suggest_bindings()**: 
   - Check for additional binding opportunities
   - Bind nodes that should move together
6. **Check for crossings**:
   - Use detect_line_crossings() to identify issues
   - Fix by moving just ONE node from bound groups (all bound nodes move automatically)

BEST PRACTICES:
✓ Bind nodes EARLY (right after creation)
✓ Use vertical spacing of 150-200px between levels
✓ Use horizontal spacing of 200-250px between parallel paths
✓ Move bound groups by adjusting just ONE node, not all nodes individually
✓ Check suggest_bindings() after creating the initial structure

This approach reduces model calls by 60-80% compared to adjusting each node individually!"""
                    )
                )
            ]
        )
    
    elif name == "add_connected_nodes":
        nodes_desc = arguments.get("nodes_description", "related nodes") if arguments else "related nodes"
        base_x = arguments.get("base_x", "0") if arguments else "0"
        base_y = arguments.get("base_y", "0") if arguments else "0"
        
        return GetPromptResult(
            description=f"Add {nodes_desc} with automatic bindings",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Add {nodes_desc} to the diagram starting at position ({base_x}, {base_y})

EFFICIENT WORKFLOW:

1. **List existing cells** to understand the current diagram:
   - Use list_cells() to see what already exists
   - Note any existing bindings (shown as [BOUND to: ...])
   
2. **Create all new nodes in one batch**:
   - Use add_shape() for each node with proper spacing
   - Keep track of the created node IDs
   
3. **Bind the new nodes together IMMEDIATELY**:
   - Use bind_nodes(node_ids=[id1, id2, id3, ...])
   - This creates a movable group
   
4. **Add connections**:
   - Connect the nodes using add_connection()
   - Connect to existing nodes if needed
   
5. **Verify and optimize**:
   - Use suggest_bindings() to check if these new nodes should be bound to existing nodes
   - If the new nodes should move with existing groups, add those bindings too

EXAMPLE:
```
# Create nodes
svc_id = add_shape(label="Service", x=100, y=100)
db_id = add_shape(label="Database", x=100, y=200) 
cache_id = add_shape(label="Cache", x=250, y=200)

# Bind immediately - this is KEY for efficiency!
bind_nodes(node_ids=[svc_id, db_id, cache_id])

# Add connections
add_connection(source_id=svc_id, target_id=db_id)
add_connection(source_id=svc_id, target_id=cache_id)

# Now moving any ONE of these nodes moves all 3 together!
```

This saves 2-3 tool calls per adjustment compared to moving nodes individually."""
                    )
                )
            ]
        )
    
    elif name == "optimize_layout":
        return GetPromptResult(
            description="Optimize diagram layout with minimal adjustments",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Optimize the current diagram layout efficiently

OPTIMIZATION WORKFLOW:

1. **Detect crossings**:
   - Use detect_line_crossings() to find all crossing issues
   - This identifies which nodes need adjustment
   
2. **Suggest bindings** before making changes:
   - Use suggest_bindings() to identify nodes that should move together
   - Bind related nodes BEFORE adjusting positions
   - This ensures when you move one node, related nodes move too
   
3. **Apply bindings strategically**:
   - For each high-scoring suggestion, use bind_nodes()
   - Focus on binding nodes that are:
     * Close together (proximity)
     * Have matching names (same prefix/suffix)
     * Are functionally related (service+db, ui+api, etc.)
   
4. **Fix crossings with minimal moves**:
   - For each crossing, move just ONE node from the bound group
   - All bound nodes will move automatically
   - Verify crossings are resolved with detect_line_crossings()
   
5. **Final spacing check**:
   - Use suggest_bindings() again to see if any new opportunities emerged
   - Verify layout looks clean with list_cells()

EFFICIENCY GAIN:
- Without bindings: Need to move each node individually = 5-10 tool calls per section
- With bindings: Move one node per bound group = 1-2 tool calls per section
- Result: 70-80% reduction in tool calls

IMPORTANT: Always bind BEFORE moving nodes to maximize efficiency!"""
                    )
                )
            ]
        )
    
    elif name == "modify_with_bindings":
        modification = arguments.get("modification_description", "the diagram") if arguments else "the diagram"
        
        return GetPromptResult(
            description=f"Modify {modification} using efficient binding-based workflow",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Modify the diagram: {modification}

BINDING-AWARE MODIFICATION WORKFLOW:

1. **Check existing bindings FIRST**:
   - Use list_cells() to see all nodes and their bindings
   - Look for [BOUND to: ...] annotations
   - This tells you which nodes already move together
   
2. **Identify the modification scope**:
   - Which nodes need to move?
   - Are they already bound together?
   - If not, should they be bound?
   
3. **Create new bindings if needed**:
   - If multiple unbound nodes need to move together, bind them first
   - Use bind_nodes(node_ids=[...])
   - This is a one-time setup that saves many future calls
   
4. **Make the modification efficiently**:
   - Move just ONE node from each bound group
   - Use move_shape(shape_id=one_node_id, new_x=..., new_y=...)
   - All bound nodes move automatically
   
5. **Verify the change**:
   - Use list_cells() to confirm positions
   - Use detect_line_crossings() to check for new issues

EXAMPLE - Moving a service cluster:
```
# Without bindings (inefficient):
move_shape("svc1", 300, 100)  # Call 1
move_shape("svc2", 300, 200)  # Call 2  
move_shape("db1", 300, 300)   # Call 3
move_shape("cache1", 450, 300) # Call 4
# Total: 4 calls

# With bindings (efficient):
bind_nodes(["svc1", "svc2", "db1", "cache1"])  # One-time setup
move_shape("svc1", 300, 100)  # Just ONE call - all 4 move!
# Total: 2 calls (and future modifications only need 1 call)
```

KEY INSIGHT: Bindings are an INVESTMENT - spend 1 call to set them up, save 3-10 calls on every future adjustment!"""
                    )
                )
            ]
        )
    
    elif name == "create_architecture_diagram":
        arch_desc = arguments.get("architecture_description", "a system architecture") if arguments else "a system architecture"
        
        return GetPromptResult(
            description=f"Create {arch_desc} with proper component grouping",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Create an architecture diagram for: {arch_desc}

ARCHITECTURE DIAGRAM WORKFLOW:

1. **Plan layers/tiers**:
   - Identify logical layers (e.g., presentation, business, data)
   - Plan vertical spacing: 250-300px between layers
   - Plan horizontal spacing: 200-250px between components
   
2. **Create components layer by layer**:
   - Start with the top layer (e.g., UI/frontend)
   - Use add_shape() for each component
   - Use consistent Y coordinates within a layer
   
3. **Bind components within each layer**:
   - After creating all components in a layer, bind them
   - Example: bind_nodes(["ui1", "ui2", "ui3"])
   - This allows moving entire layers together
   
4. **Create cross-layer component groups**:
   - For vertical stacks (e.g., service + its database), bind them too
   - Use suggest_bindings() to identify these relationships
   - Bind vertical stacks: bind_nodes(["service", "service_db", "service_cache"])
   
5. **Add connections**:
   - Connect components with add_connection()
   - Use entry/exit points for clean routing
   - Add waypoints if needed for complex routing
   
6. **Optimize layout**:
   - Use detect_line_crossings() to find issues
   - Move one node per bound group to fix crossings
   - All bound components move together

LAYERING STRATEGY:
```
Layer 1 (Y=100): UI components - bind together
Layer 2 (Y=350): API/Service components - bind together  
Layer 3 (Y=600): Data components - bind together

Vertical stacks: Each service+db+cache stack bound together

Result:
- Move entire layers by adjusting ONE node
- Move service stacks by adjusting ONE component
- Total tool calls reduced by 75-85%
```

BEST PRACTICES:
✓ Bind horizontally (all components in a layer)
✓ Bind vertically (component + its dependencies)
✓ Use suggest_bindings() to discover implicit relationships
✓ Test moving one node per group to verify bindings work"""
                    )
                )
            ]
        )
    
    else:
        return GetPromptResult(
            description=f"Unknown prompt: {name}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"Prompt '{name}' not found. Use list_prompts to see available prompts."
                    )
                )
            ]
        )


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
