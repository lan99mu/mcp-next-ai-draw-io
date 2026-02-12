#!/usr/bin/env python3
"""
Tool definitions for MCP Draw.io Server.

This module contains all tool schema definitions that are exposed via the MCP protocol.
"""

from mcp.types import Tool


def get_tool_definitions() -> list[Tool]:
    """Return all available tool definitions for the MCP server."""
    return [
        Tool(
            name="create_diagram",
            description="Create a new Draw.io diagram in memory.",
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
            description="Load an existing .drawio file from disk.",
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
            description="Get the current diagram as Draw.io XML.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="set_diagram_xml",
            description="Set diagram from raw Draw.io XML.",
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
            description="List all cells (shapes and connections) with IDs, labels, types, and bindings.",
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
            description="Add a connection/edge between two shapes. Supports label positioning and routing.",
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
            description="Bind multiple nodes to move together as a group.",
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
            description="Remove nodes from their binding group.",
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
            description="Move a shape to a new position. Bound nodes move automatically.",
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
            description="Detect line crossings and provide position adjustment hints.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="suggest_bindings",
            description="Analyze diagram and suggest which nodes should be bound together.",
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
            description="List all shapes in the diagram (deprecated: use list_cells).",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]
