#!/usr/bin/env python3
"""
Cell operation handlers.

Handlers for list_cells, get_cell, update_cell, delete_cell,
add_shape, and add_connection tools.
"""

from typing import Any
from mcp.types import TextContent

from .state import diagram_state, safe_float
from ..xml_operations import get_cells_from_xml, update_cell_in_xml, delete_cell_in_xml


def handle_list_cells(arguments: Any) -> list[TextContent]:
    """Handle list_cells tool call."""
    if diagram_state.current_xml:
        cells = get_cells_from_xml(diagram_state.current_xml)
    elif diagram_state.current_diagram:
        xml_content = diagram_state.current_diagram.to_drawio_xml()
        cells = get_cells_from_xml(xml_content)
    else:
        return [TextContent(
            type="text",
            text="No diagram available. Create a new diagram or load an existing one."
        )]
    
    if not cells:
        return [TextContent(type="text", text="No cells in the diagram yet.")]
    
    cells_list = []
    for cell in cells:
        cell_type = "Shape" if cell['vertex'] else ("Connection" if cell['edge'] else "Unknown")
        label = cell['value'] or "(no label)"
        
        if cell['vertex']:
            x = safe_float(cell.get('x'))
            y = safe_float(cell.get('y'))
            width = safe_float(cell.get('width'))
            height = safe_float(cell.get('height'))
            center_x = x + width / 2
            center_y = y + height / 2
            pos = f"at ({x}, {y}), size ({width}x{height}), center ({center_x}, {center_y})"
            
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


def handle_get_cell(arguments: Any) -> list[TextContent]:
    """Handle get_cell tool call."""
    cell_id = arguments["cell_id"]
    
    if diagram_state.current_xml:
        cells = get_cells_from_xml(diagram_state.current_xml)
    elif diagram_state.current_diagram:
        xml_content = diagram_state.current_diagram.to_drawio_xml()
        cells = get_cells_from_xml(xml_content)
    else:
        return [TextContent(type="text", text="No diagram available.")]
    
    cell = next((c for c in cells if c['id'] == cell_id), None)
    if not cell:
        return [TextContent(type="text", text=f"Cell not found: {cell_id}")]
    
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
        
        bound_nodes = cell.get('bound_nodes', [])
        if bound_nodes:
            cell_info += f"Bound to {len(bound_nodes)} node(s): {', '.join(bound_nodes)}\n"
    if cell['edge']:
        cell_info += f"Source: {cell['source']}\n"
        cell_info += f"Target: {cell['target']}\n"
    
    return [TextContent(type="text", text=cell_info)]


def handle_update_cell(arguments: Any) -> list[TextContent]:
    """Handle update_cell tool call."""
    cell_id = arguments["cell_id"]
    
    if diagram_state.current_xml:
        try:
            updates = {}
            for key in ['value', 'x', 'y', 'width', 'height', 'style']:
                if key in arguments:
                    updates[key] = arguments[key]
            
            diagram_state.current_xml = update_cell_in_xml(
                diagram_state.current_xml, cell_id, **updates
            )
            
            return [TextContent(
                type="text",
                text=f"Cell {cell_id} updated successfully.\n\nUpdated fields: {', '.join(updates.keys())}"
            )]
        except Exception as e:
            return [TextContent(type="text", text=f"Error updating cell: {str(e)}")]
    else:
        return [TextContent(
            type="text",
            text="Error: Can only update cells in loaded diagrams. Use load_diagram first."
        )]


def handle_delete_cell(arguments: Any) -> list[TextContent]:
    """Handle delete_cell tool call."""
    cell_id = arguments["cell_id"]
    
    if diagram_state.current_xml:
        try:
            diagram_state.current_xml = delete_cell_in_xml(
                diagram_state.current_xml, cell_id
            )
            return [TextContent(type="text", text=f"Cell {cell_id} deleted successfully.")]
        except Exception as e:
            return [TextContent(type="text", text=f"Error deleting cell: {str(e)}")]
    else:
        return [TextContent(
            type="text",
            text="Error: Can only delete cells in loaded diagrams. Use load_diagram first."
        )]


def handle_add_shape(arguments: Any) -> list[TextContent]:
    """Handle add_shape tool call."""
    diagram = diagram_state.get_or_create_diagram()
    shape_id = diagram.add_shape(
        label=arguments["label"],
        x=arguments.get("x", 0),
        y=arguments.get("y", 0),
        width=arguments.get("width", 120),
        height=arguments.get("height", 60),
        shape_type=arguments.get("shape_type", "rectangle"),
        style=arguments.get("style", ""),
        parent_id=arguments.get("parent_id"),
        dashed=arguments.get("dashed", False),
        rounded=arguments.get("rounded", False),
        stroke_width=arguments.get("stroke_width"),
        fill_color=arguments.get("fill_color"),
        stroke_color=arguments.get("stroke_color"),
        font_size=arguments.get("font_size"),
        font_color=arguments.get("font_color"),
        opacity=arguments.get("opacity"),
        overflow=arguments.get("overflow", "hidden"),
        auto_size=arguments.get("auto_size", False)
    )
    if diagram_state.current_xml:
        diagram_state.current_xml = diagram.to_drawio_xml()
    
    return [TextContent(
        type="text",
        text=f"Added shape '{arguments['label']}' with ID: {shape_id}"
    )]


def handle_add_connection(arguments: Any) -> list[TextContent]:
    """Handle add_connection tool call."""
    diagram = diagram_state.get_or_create_diagram()
    try:
        waypoints = arguments.get("waypoints")
        if waypoints:
            waypoints = [tuple(wp) for wp in waypoints]
        
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
            target_point=target_point,
            edge_style=arguments.get("edge_style", "orthogonal"),
            dashed=arguments.get("dashed", False),
            rounded=arguments.get("rounded", False),
            stroke_width=arguments.get("stroke_width"),
            stroke_color=arguments.get("stroke_color"),
            start_arrow=arguments.get("start_arrow"),
            end_arrow=arguments.get("end_arrow")
        )
        if diagram_state.current_xml:
            diagram_state.current_xml = diagram.to_drawio_xml()
        
        return [TextContent(
            type="text",
            text=f"Added connection from {arguments['source_id']} to {arguments['target_id']} with ID: {conn_id}"
        )]
    except ValueError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
