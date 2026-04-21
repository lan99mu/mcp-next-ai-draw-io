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


DEFAULT_PARENT_ID = "1"


def _get_cells() -> list[dict]:
    """Get cells from the current diagram state."""
    if diagram_state.current_xml:
        return get_cells_from_xml(diagram_state.current_xml)
    if diagram_state.current_diagram:
        xml_content = diagram_state.current_diagram.to_drawio_xml()
        return get_cells_from_xml(xml_content)
    return []


def _get_absolute_bounds(cell: dict, cells_by_id: dict[str, dict], seen: set[str] | None = None) -> tuple[float, float, float, float]:
    """Resolve a cell's absolute bounds as (x, y, width, height)."""
    x = safe_float(cell.get('x'))
    y = safe_float(cell.get('y'))
    width = safe_float(cell.get('width'))
    height = safe_float(cell.get('height'))
    cell_id = cell.get('id')

    parent_id = cell.get('parent')
    if parent_id and parent_id not in {"0", DEFAULT_PARENT_ID}:
        if seen is None:
            seen = set()
        if cell_id in seen:
            return x, y, width, height
        if cell_id:
            seen.add(cell_id)

        parent = cells_by_id.get(parent_id)
        if parent and parent.get('vertex'):
            parent_x, parent_y, _, _ = _get_absolute_bounds(parent, cells_by_id, seen)
            x += parent_x
            y += parent_y

    return x, y, width, height


def _build_shape_geometry(cell: dict, cells_by_id: dict[str, dict]) -> tuple[dict[str, list[float]], list[tuple[str, list[float], list[float]]]]:
    """Build shape geometry as (points_dict, lines_list) in absolute coordinates."""
    x, y, width, height = _get_absolute_bounds(cell, cells_by_id)
    points = {
        "top_left": [x, y],
        "top_right": [x + width, y],
        "bottom_right": [x + width, y + height],
        "bottom_left": [x, y + height],
        "center": [x + width / 2, y + height / 2],
    }
    lines = [
        ("top", points["top_left"], points["top_right"]),
        ("right", points["top_right"], points["bottom_right"]),
        ("bottom", points["bottom_left"], points["bottom_right"]),
        ("left", points["top_left"], points["bottom_left"]),
    ]
    return points, lines


def _is_contained(container: dict, inner: dict, cells_by_id: dict[str, dict]) -> bool:
    """Check whether one shape fully contains another shape."""
    container_id = container.get('id')
    inner_id = inner.get('id')
    if not container_id or not inner_id:
        return False

    if container_id == inner_id:
        return False

    c_x, c_y, c_w, c_h = _get_absolute_bounds(container, cells_by_id)
    i_x, i_y, i_w, i_h = _get_absolute_bounds(inner, cells_by_id)
    if c_w <= 0 or c_h <= 0 or i_w <= 0 or i_h <= 0:
        return False

    container_area = c_w * c_h
    inner_area = i_w * i_h
    if container_area <= inner_area:
        return False

    return (
        c_x <= i_x
        and c_y <= i_y
        and c_x + c_w >= i_x + i_w
        and c_y + c_h >= i_y + i_h
    )


def _get_bind_relationships(cell: dict, cells: list[dict], cells_by_id: dict[str, dict]) -> dict[str, list[str] | str | None]:
    """Collect explicit and containment-based bind relationships for a cell."""
    explicit = sorted(set(cell.get('bound_nodes', [])))
    contains = set()
    contained_by = None

    parent_id = cell.get('parent')
    if parent_id and parent_id not in {"0", DEFAULT_PARENT_ID} and parent_id in cells_by_id:
        contained_by = parent_id

    for other in cells:
        if not other.get('vertex') or other['id'] == cell['id']:
            continue

        if other.get('parent') == cell['id']:
            contains.add(other['id'])
            continue

        if cell.get('parent') == other['id']:
            contained_by = other['id']
            continue

        if _is_contained(cell, other, cells_by_id):
            contains.add(other['id'])
        elif _is_contained(other, cell, cells_by_id):
            contained_by = other['id']

    return {
        "explicit": explicit,
        "contains": sorted(contains),
        "contained_by": contained_by,
    }


def _build_edge_geometry(cell: dict, cells_by_id: dict[str, dict]) -> tuple[list[tuple[str, list[float]]], list[tuple[str, list[float], list[float]]]]:
    """Build edge geometry as (ordered_points, segments) in drawing coordinates."""
    ordered_points: list[tuple[str, list[float]]] = []

    source_point = cell.get('source_point')
    if source_point:
        ordered_points.append((
            "source_point",
            [safe_float(source_point[0]), safe_float(source_point[1])]
        ))
    else:
        source = cells_by_id.get(cell.get('source'))
        if source and source.get('vertex'):
            sx, sy, sw, sh = _get_absolute_bounds(source, cells_by_id)
            ordered_points.append((
                "source_anchor",
                [
                    sx + sw * safe_float(cell.get('exit_x', 0.5), 0.5),
                    sy + sh * safe_float(cell.get('exit_y', 0.5), 0.5),
                ],
            ))

    for index, waypoint in enumerate(cell.get('waypoints', []), start=1):
        ordered_points.append((
            f"waypoint_{index}",
            [safe_float(waypoint[0]), safe_float(waypoint[1])]
        ))

    target_point = cell.get('target_point')
    if target_point:
        ordered_points.append((
            "target_point",
            [safe_float(target_point[0]), safe_float(target_point[1])]
        ))
    else:
        target = cells_by_id.get(cell.get('target'))
        if target and target.get('vertex'):
            tx, ty, tw, th = _get_absolute_bounds(target, cells_by_id)
            ordered_points.append((
                "target_anchor",
                [
                    tx + tw * safe_float(cell.get('entry_x', 0.5), 0.5),
                    ty + th * safe_float(cell.get('entry_y', 0.5), 0.5),
                ],
            ))

    segments = []
    for index in range(len(ordered_points) - 1):
        start_name, start_point = ordered_points[index]
        end_name, end_point = ordered_points[index + 1]
        segments.append((f"{start_name}->{end_name}", start_point, end_point))

    return ordered_points, segments


def _format_point(point: list[float]) -> str:
    """Format a 2D point for display."""
    return f"({point[0]:.1f}, {point[1]:.1f})"


def handle_list_cells(arguments: Any) -> list[TextContent]:
    """Handle list_cells tool call."""
    cells = _get_cells()
    if not cells and not (diagram_state.current_xml or diagram_state.current_diagram):
        return [TextContent(
            type="text",
            text="No diagram available. Create a new diagram or load an existing one."
        )]
    
    if not cells:
        return [TextContent(type="text", text="No cells in the diagram yet.")]
    
    cells_list = []
    cells_by_id = {cell['id']: cell for cell in cells}
    for cell in cells:
        cell_type = "Shape" if cell['vertex'] else ("Connection" if cell['edge'] else "Unknown")
        label = cell['value'] or "(no label)"
        
        if cell['vertex']:
            x = safe_float(cell.get('x'))
            y = safe_float(cell.get('y'))
            width = safe_float(cell.get('width'))
            height = safe_float(cell.get('height'))
            abs_x, abs_y, _, _ = _get_absolute_bounds(cell, cells_by_id)
            center_x = abs_x + width / 2
            center_y = abs_y + height / 2
            pos = (
                f"at ({x}, {y}), size ({width}x{height}), "
                f"bounds ({abs_x:.0f},{abs_y:.0f})→({abs_x+width:.0f},{abs_y+height:.0f}), "
                f"center ({center_x:.0f},{center_y:.0f})"
            )
            
            bind_relationships = _get_bind_relationships(cell, cells, cells_by_id)
            bind_parts = []
            if bind_relationships['explicit']:
                bind_parts.append(f"explicit: {', '.join(bind_relationships['explicit'])}")
            if bind_relationships['contains']:
                bind_parts.append(f"contains: {', '.join(bind_relationships['contains'])}")
            if bind_relationships['contained_by']:
                bind_parts.append(f"contained_by: {bind_relationships['contained_by']}")
            if bind_parts:
                pos += f" [BIND: {'; '.join(bind_parts)}]"
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
    
    cells = _get_cells()
    if not cells and not (diagram_state.current_xml or diagram_state.current_diagram):
        return [TextContent(type="text", text="No diagram available.")]
    
    cell = next((c for c in cells if c['id'] == cell_id), None)
    if not cell:
        return [TextContent(type="text", text=f"Cell not found: {cell_id}")]

    cells_by_id = {item['id']: item for item in cells}
    
    cell_info = f"Cell ID: {cell_id}\n"
    cell_info += f"Type: {'Shape' if cell['vertex'] else 'Connection'}\n"
    cell_info += f"Label: {cell['value'] or '(no label)'}\n"
    cell_info += f"Style: {cell['style'] or '(default)'}\n"
    if cell['vertex']:
        x = safe_float(cell.get('x'))
        y = safe_float(cell.get('y'))
        width = safe_float(cell.get('width'))
        height = safe_float(cell.get('height'))
        abs_x, abs_y, _, _ = _get_absolute_bounds(cell, cells_by_id)
        center_x = abs_x + width / 2
        center_y = abs_y + height / 2
        cell_info += f"Position (top-left): ({x}, {y})\n"
        if abs_x != x or abs_y != y:
            cell_info += f"Absolute position (top-left): ({abs_x}, {abs_y})\n"
        cell_info += f"Size: {width} x {height}\n"
        cell_info += f"Center (absolute): ({center_x}, {center_y})\n"
        cell_info += f"Bounding box (absolute): ({abs_x}, {abs_y}) to ({abs_x + width}, {abs_y + height})\n"

        shape_points, shape_lines = _build_shape_geometry(cell, cells_by_id)
        cell_info += "Points:\n"
        for name, point in shape_points.items():
            cell_info += f"  - {name}: {_format_point(point)}\n"

        cell_info += "Lines:\n"
        for name, start, end in shape_lines:
            cell_info += f"  - {name}: {_format_point(start)} -> {_format_point(end)}\n"

        bind_relationships = _get_bind_relationships(cell, cells, cells_by_id)
        if (
            bind_relationships['explicit']
            or bind_relationships['contains']
            or bind_relationships['contained_by']
        ):
            cell_info += "Bind relationships:\n"
            if bind_relationships['explicit']:
                cell_info += (
                    f"  - explicit: {', '.join(bind_relationships['explicit'])}\n"
                )
            if bind_relationships['contains']:
                cell_info += (
                    f"  - contains: {', '.join(bind_relationships['contains'])}\n"
                )
            if bind_relationships['contained_by']:
                cell_info += (
                    f"  - contained_by: {bind_relationships['contained_by']}\n"
                )
    if cell['edge']:
        cell_info += f"Source: {cell['source']}\n"
        cell_info += f"Target: {cell['target']}\n"
        if cell.get('entry_x') is not None or cell.get('entry_y') is not None:
            cell_info += (
                f"Entry anchor (normalized): ({safe_float(cell.get('entry_x', 0.5), 0.5)}, "
                f"{safe_float(cell.get('entry_y', 0.5), 0.5)})\n"
            )
        if cell.get('exit_x') is not None or cell.get('exit_y') is not None:
            cell_info += (
                f"Exit anchor (normalized): ({safe_float(cell.get('exit_x', 0.5), 0.5)}, "
                f"{safe_float(cell.get('exit_y', 0.5), 0.5)})\n"
            )

        edge_points, edge_lines = _build_edge_geometry(cell, cells_by_id)
        if edge_points:
            cell_info += "Points:\n"
            for name, point in edge_points:
                cell_info += f"  - {name}: {_format_point(point)}\n"

        if edge_lines:
            cell_info += "Lines:\n"
            for name, start, end in edge_lines:
                cell_info += f"  - {name}: {_format_point(start)} -> {_format_point(end)}\n"
    
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
                text=f"Cell {cell_id} updated: {', '.join(updates.keys())}" + (diagram_state.maybe_autosave() or "")
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
            return [TextContent(type="text", text=f"Cell {cell_id} deleted." + (diagram_state.maybe_autosave() or ""))]
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
        text=f"Added shape '{arguments['label']}' with ID: {shape_id}" + (diagram_state.maybe_autosave() or "")
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
            end_arrow=arguments.get("end_arrow"),
            auto_route=arguments.get("auto_route", True),
        )
        if diagram_state.current_xml:
            diagram_state.current_xml = diagram.to_drawio_xml()
        
        return [TextContent(
            type="text",
            text=f"Added connection from {arguments['source_id']} to {arguments['target_id']} with ID: {conn_id}" + (diagram_state.maybe_autosave() or "")
        )]
    except ValueError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
