#!/usr/bin/env python3
"""
Node binding operation handlers.

Handlers for bind_nodes, unbind_nodes, get_bound_nodes, and move_shape tools.
"""

from typing import Any
from mcp.types import TextContent

from .state import diagram_state, bind_nodes_helper


def handle_bind_nodes(arguments: Any) -> list[TextContent]:
    """Handle bind_nodes tool call."""
    diagram = diagram_state.get_or_create_diagram()
    node_ids = arguments["node_ids"]
    
    if len(node_ids) < 2:
        return [TextContent(
            type="text",
            text="Error: At least 2 nodes are required to create a binding."
        )]
    
    missing_nodes = [nid for nid in node_ids if nid not in diagram.shapes]
    if missing_nodes:
        return [TextContent(
            type="text",
            text=f"Error: The following node IDs were not found: {', '.join(missing_nodes)}"
        )]
    
    bind_nodes_helper(diagram, node_ids)
    
    if diagram_state.current_xml:
        diagram_state.current_xml = diagram.to_drawio_xml()
    
    return [TextContent(
        type="text",
        text=f"Successfully bound {len(node_ids)} nodes together: {', '.join(node_ids)}\n\nThese nodes will now move together when any one of them is moved."
    )]


def handle_unbind_nodes(arguments: Any) -> list[TextContent]:
    """Handle unbind_nodes tool call."""
    diagram = diagram_state.get_or_create_diagram()
    node_ids = arguments["node_ids"]
    
    missing_nodes = [nid for nid in node_ids if nid not in diagram.shapes]
    if missing_nodes:
        return [TextContent(
            type="text",
            text=f"Error: The following node IDs were not found: {', '.join(missing_nodes)}"
        )]
    
    for node_id in node_ids:
        bound_to = diagram.shapes[node_id].bound_nodes.copy()
        diagram.shapes[node_id].bound_nodes = []
        
        for other_id in bound_to:
            if other_id in diagram.shapes:
                if node_id in diagram.shapes[other_id].bound_nodes:
                    diagram.shapes[other_id].bound_nodes.remove(node_id)
    
    if diagram_state.current_xml:
        diagram_state.current_xml = diagram.to_drawio_xml()
    
    return [TextContent(
        type="text",
        text=f"Successfully unbound {len(node_ids)} nodes: {', '.join(node_ids)}"
    )]


def handle_get_bound_nodes(arguments: Any) -> list[TextContent]:
    """Handle get_bound_nodes tool call."""
    diagram = diagram_state.get_or_create_diagram()
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
        text=f"Node '{node_id}' is bound to {len(bound_nodes)} node(s):\n\n" + 
             "\n".join(f"- {nid}" for nid in bound_nodes)
    )]


def handle_move_shape(arguments: Any) -> list[TextContent]:
    """Handle move_shape tool call."""
    diagram = diagram_state.get_or_create_diagram()
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
    
    offset_x = new_x - old_x
    offset_y = new_y - old_y
    
    shape.x = new_x
    shape.y = new_y
    
    moved_nodes = [shape_id]
    for bound_id in shape.bound_nodes:
        if bound_id in diagram.shapes:
            diagram.shapes[bound_id].x += offset_x
            diagram.shapes[bound_id].y += offset_y
            moved_nodes.append(bound_id)
    
    if diagram_state.current_xml:
        diagram_state.current_xml = diagram.to_drawio_xml()
    
    if len(moved_nodes) > 1:
        return [TextContent(
            type="text",
            text=f"Moved shape '{shape_id}' from ({old_x}, {old_y}) to ({new_x}, {new_y}).\n\nAlso moved {len(moved_nodes) - 1} bound node(s) by offset ({offset_x}, {offset_y}):\n" + 
                 "\n".join(f"- {nid}" for nid in moved_nodes[1:])
        )]
    else:
        return [TextContent(
            type="text",
            text=f"Moved shape '{shape_id}' from ({old_x}, {old_y}) to ({new_x}, {new_y})."
        )]
