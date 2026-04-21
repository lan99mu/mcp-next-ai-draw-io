#!/usr/bin/env python3
"""
Tool definitions for MCP Draw.io Server.

This module contains all tool schema definitions that are exposed via the MCP protocol.
"""

from mcp.types import Tool


def get_tool_definitions() -> list[Tool]:
    """Return all available tool definitions for the MCP server."""
    return [
        # --- File Operations ---
        Tool(
            name="create_diagram",
            description="Create a new empty Draw.io diagram in memory.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Diagram name",
                        "default": "Untitled"
                    },
                    "autosave_path": {
                        "type": "string",
                        "description": "If set, write the file to this path after every mutating operation (autosave mode)"
                    }
                }
            }
        ),
        Tool(
            name="load_diagram",
            description="Load an existing .drawio file from disk into memory.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute or relative path to the .drawio file"
                    },
                    "autosave": {
                        "type": "boolean",
                        "description": "If true, write changes back to this file after every mutating operation",
                        "default": False
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="save_diagram",
            description="Save the current in-memory diagram to a .drawio file.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path to save (auto-adds .drawio extension if missing)"
                    }
                },
                "required": ["path"]
            }
        ),

        # --- Inspection ---
        Tool(
            name="list_cells",
            description="List all cells (shapes and connections) with IDs, labels, types, positions, and binding info.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_cell",
            description="Get detailed geometry, style, and binding info for a single cell by ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "cell_id": {
                        "type": "string",
                        "description": "Cell ID to inspect"
                    }
                },
                "required": ["cell_id"]
            }
        ),

        # --- Shape Operations ---
        Tool(
            name="add_shape",
            description="Add a shape to the diagram. Returns the new shape ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "label": {
                        "type": "string",
                        "description": "Shape label text. **Labels must be HTML-style** — use `<br>` for line breaks. Plain `\\n` or GraphViz `\\l` are auto-converted to `<br>`. For UML class shapes, use: 'ClassName<br>───────<br>- attr: type<br>───────<br>+ method()'"
                    },
                    "x": {
                        "type": "number",
                        "description": "X position (default: 0)",
                        "default": 0
                    },
                    "y": {
                        "type": "number",
                        "description": "Y position (default: 0)",
                        "default": 0
                    },
                    "width": {
                        "type": "number",
                        "description": "Width in pixels (default: 120)",
                        "default": 120,
                        "minimum": 10,
                        "maximum": 2000
                    },
                    "height": {
                        "type": "number",
                        "description": "Height in pixels (default: 60)",
                        "default": 60,
                        "minimum": 10,
                        "maximum": 2000
                    },
                    "shape_type": {
                        "type": "string",
                        "description": "Shape type",
                        "enum": [
                            "rectangle", "ellipse", "diamond", "parallelogram", "hexagon", "cylinder", "cloud",
                            "activity_start", "activity_end", "activity_action", "activity_decision",
                            "activity_fork", "activity_join", "activity_send_signal", "activity_receive_signal", "activity_note",
                            "swimlane_pool", "swimlane_h", "swimlane_v", "container",
                            "uml_class", "uml_interface", "uml_abstract_class", "uml_enum", "uml_package", "uml_note",
                            "actor", "lifeline", "uml_frame", "component"
                        ],
                        "default": "rectangle"
                    },
                    "style": {
                        "type": "string",
                        "description": "Custom Draw.io style string (overrides shape_type defaults)",
                        "default": ""
                    },
                    "parent_id": {
                        "type": "string",
                        "description": "Parent container/swimlane ID for nested shapes"
                    },
                    "fill_color": {
                        "type": "string",
                        "description": "Background color, e.g. '#dae8fc'",
                        "pattern": "^#[0-9a-fA-F]{6}$"
                    },
                    "stroke_color": {
                        "type": "string",
                        "description": "Border color, e.g. '#6c8ebf'",
                        "pattern": "^#[0-9a-fA-F]{6}$"
                    },
                    "font_color": {
                        "type": "string",
                        "description": "Text color, e.g. '#000000'",
                        "pattern": "^#[0-9a-fA-F]{6}$"
                    },
                    "font_size": {
                        "type": "integer",
                        "description": "Font size in px",
                        "minimum": 6,
                        "maximum": 72
                    },
                    "dashed": {
                        "type": "boolean",
                        "description": "Dashed border",
                        "default": False
                    },
                    "rounded": {
                        "type": "boolean",
                        "description": "Rounded corners",
                        "default": False
                    },
                    "stroke_width": {
                        "type": "number",
                        "description": "Border thickness in px",
                        "minimum": 0,
                        "maximum": 20
                    },
                    "opacity": {
                        "type": "number",
                        "description": "Opacity (0=transparent, 100=opaque)",
                        "minimum": 0,
                        "maximum": 100
                    },
                    "overflow": {
                        "type": "string",
                        "description": "Text overflow behavior",
                        "enum": ["hidden", "visible", "fill"],
                        "default": "hidden"
                    },
                    "auto_size": {
                        "type": "boolean",
                        "description": "Auto-calculate size from label text",
                        "default": False
                    }
                },
                "required": ["label"]
            }
        ),

        # --- Connection Operations ---
        Tool(
            name="add_connection",
            description="Add a connection between two shapes. Returns the new connection ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "source_id": {
                        "type": "string",
                        "description": "Source shape ID"
                    },
                    "target_id": {
                        "type": "string",
                        "description": "Target shape ID"
                    },
                    "label": {
                        "type": "string",
                        "description": "Connection label. **Must be HTML-style** — use `<br>` for line breaks. Plain `\\n` / GraphViz `\\l` are auto-converted to `<br>`.",
                        "default": ""
                    },
                    "edge_style": {
                        "type": "string",
                        "description": "Routing style",
                        "enum": ["orthogonal", "straight", "curved", "entity_relation"],
                        "default": "orthogonal"
                    },
                    "arrow_type": {
                        "type": "string",
                        "description": "End arrow type",
                        "enum": ["classic", "block", "open", "oval", "diamond", "diamondThin", "none"],
                        "default": "classic"
                    },
                    "start_arrow": {
                        "type": "string",
                        "description": "Start arrow type",
                        "enum": ["none", "classic", "block", "open", "oval", "diamond", "diamondThin"],
                        "default": "none"
                    },
                    "end_arrow": {
                        "type": "string",
                        "description": "End arrow type (overrides arrow_type if set)",
                        "enum": ["none", "classic", "block", "open", "oval", "diamond", "diamondThin"]
                    },
                    "exit_x": {
                        "type": "number",
                        "description": "Exit point X on source (0=left, 0.5=center, 1=right)",
                        "minimum": 0,
                        "maximum": 1
                    },
                    "exit_y": {
                        "type": "number",
                        "description": "Exit point Y on source (0=top, 0.5=center, 1=bottom)",
                        "minimum": 0,
                        "maximum": 1
                    },
                    "entry_x": {
                        "type": "number",
                        "description": "Entry point X on target (0=left, 0.5=center, 1=right)",
                        "minimum": 0,
                        "maximum": 1
                    },
                    "entry_y": {
                        "type": "number",
                        "description": "Entry point Y on target (0=top, 0.5=center, 1=bottom)",
                        "minimum": 0,
                        "maximum": 1
                    },
                    "waypoints": {
                        "type": "array",
                        "items": {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 2,
                            "maxItems": 2
                        },
                        "description": "Intermediate bend points as [[x,y], ...] in absolute pixels"
                    },
                    "source_point": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "description": "Explicit source point [x, y] in absolute pixels"
                    },
                    "target_point": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "description": "Explicit target point [x, y] in absolute pixels"
                    },
                    "label_position": {
                        "type": "string",
                        "description": "Label alignment on the edge",
                        "enum": ["left", "right", "center"]
                    },
                    "label_offset_x": {
                        "type": "number",
                        "description": "Label horizontal offset in pixels"
                    },
                    "label_offset_y": {
                        "type": "number",
                        "description": "Label vertical offset in pixels"
                    },
                    "label_background_color": {
                        "type": "string",
                        "description": "Label background color, e.g. '#ffffff' or 'none'"
                    },
                    "style": {
                        "type": "string",
                        "description": "Custom Draw.io style string (overrides all other style options)",
                        "default": ""
                    },
                    "dashed": {
                        "type": "boolean",
                        "description": "Dashed line",
                        "default": False
                    },
                    "rounded": {
                        "type": "boolean",
                        "description": "Rounded corners (orthogonal edges only)",
                        "default": False
                    },
                    "stroke_width": {
                        "type": "number",
                        "description": "Line thickness in px",
                        "minimum": 0,
                        "maximum": 20
                    },
                    "stroke_color": {
                        "type": "string",
                        "description": "Line color, e.g. '#000000'",
                        "pattern": "^#[0-9a-fA-F]{6}$"
                    },
                    "auto_route": {
                        "type": "boolean",
                        "description": "When true (default), automatically insert a waypoint so the connection routes around any shape that lies between source and target. Set false to draw a straight line even if it crosses other nodes.",
                        "default": True
                    },
                    "auto_avoid_label_overlap": {
                        "type": "boolean",
                        "description": "When true (default) and the connection has a non-empty label, automatically compute a label_offset_x/y so the label sits outside any node its natural midpoint would obscure. Ignored when label_offset_x or label_offset_y is explicitly provided.",
                        "default": True
                    }
                },
                "required": ["source_id", "target_id"]
            }
        ),

        # --- Cell Modification ---
        Tool(
            name="update_cell",
            description="Update properties of an existing cell. Only specified fields are changed.",
            inputSchema={
                "type": "object",
                "properties": {
                    "cell_id": {
                        "type": "string",
                        "description": "ID of the cell to update"
                    },
                    "value": {
                        "type": "string",
                        "description": "New label text. **Must be HTML-style** — use `<br>` for line breaks. Plain `\\n` / GraphViz `\\l` are auto-converted to `<br>`."
                    },
                    "x": {
                        "type": "number",
                        "description": "New X position"
                    },
                    "y": {
                        "type": "number",
                        "description": "New Y position"
                    },
                    "width": {
                        "type": "number",
                        "description": "New width",
                        "minimum": 10
                    },
                    "height": {
                        "type": "number",
                        "description": "New height",
                        "minimum": 10
                    },
                    "style": {
                        "type": "string",
                        "description": "New Draw.io style string"
                    }
                },
                "required": ["cell_id"]
            }
        ),
        Tool(
            name="delete_cell",
            description="Delete a cell (shape or connection) by ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "cell_id": {
                        "type": "string",
                        "description": "ID of the cell to delete"
                    }
                },
                "required": ["cell_id"]
            }
        ),

        # --- Binding & Layout ---
        Tool(
            name="bind_nodes",
            description="Bind nodes into a group so they move together.",
            inputSchema={
                "type": "object",
                "properties": {
                    "node_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 2,
                        "description": "List of node IDs to bind (minimum 2)"
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
                        "minItems": 1,
                        "description": "List of node IDs to unbind"
                    }
                },
                "required": ["node_ids"]
            }
        ),
        Tool(
            name="get_bound_nodes",
            description="Query which nodes are bound to a given node.",
            inputSchema={
                "type": "object",
                "properties": {
                    "node_id": {
                        "type": "string",
                        "description": "Node ID to query"
                    }
                },
                "required": ["node_id"]
            }
        ),
        Tool(
            name="move_shape",
            description="Move a shape to a new position. All bound nodes move automatically by the same offset.",
            inputSchema={
                "type": "object",
                "properties": {
                    "shape_id": {
                        "type": "string",
                        "description": "Shape ID to move"
                    },
                    "new_x": {
                        "type": "number",
                        "description": "New X position"
                    },
                    "new_y": {
                        "type": "number",
                        "description": "New Y position"
                    }
                },
                "required": ["shape_id", "new_x", "new_y"]
            }
        ),

        # --- Analysis ---
        Tool(
            name="detect_line_crossings",
            description="Detect crossing connections and suggest position adjustments.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="detect_overlaps",
            description="Detect overlapping shapes, out-of-container boundary violations, and edge-label overlaps (label↔node and label↔label), with fix suggestions.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="suggest_bindings",
            description="Analyze diagram and suggest which nodes should be bound, based on proximity, naming, and connections.",
            inputSchema={
                "type": "object",
                "properties": {
                    "proximity_threshold": {
                        "type": "number",
                        "description": "Max distance in pixels to consider nodes related (default: 200)",
                        "default": 200,
                        "minimum": 50,
                        "maximum": 1000
                    }
                }
            }
        ),

        # --- Batch Operations ---
        Tool(
            name="batch_operations",
            description="Execute multiple diagram operations in one call to reduce token usage.",
            inputSchema={
                "type": "object",
                "properties": {
                    "operations": {
                        "type": "array",
                        "description": (
                            "Ordered list of operations. Each item is an object with an 'op' key "
                            "plus the parameters of that operation. "
                            "Supported ops: add_shape, add_connection, bind_nodes, unbind_nodes, "
                            "move_shape, update_cell, delete_cell."
                        ),
                        "items": {
                            "type": "object",
                            "properties": {
                                "op": {
                                    "type": "string",
                                    "enum": [
                                        "add_shape", "add_connection",
                                        "bind_nodes", "unbind_nodes",
                                        "move_shape", "update_cell", "delete_cell"
                                    ],
                                    "description": "Operation name"
                                }
                            },
                            "required": ["op"],
                            "additionalProperties": True
                        },
                        "minItems": 1
                    }
                },
                "required": ["operations"]
            }
        ),
    ]
