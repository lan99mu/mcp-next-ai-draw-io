"""
Utility module for detecting line crossings in Draw.io diagrams.

This module provides functions to detect when connections (lines) cross each other
and provide position hints to help AI models adjust them.
"""

import re
from typing import Optional


def get_connection_endpoints(
    connection: dict,
    shapes: dict,
) -> tuple[tuple[float, float], tuple[float, float]]:
    """
    Get the effective start and end points of a connection.
    
    Args:
        connection: Connection cell information from XML
        shapes: Dictionary of shape cells by ID
        
    Returns:
        Tuple of (start_point, end_point) where each point is (x, y)
    """
    source_id = connection.get('source')
    target_id = connection.get('target')

    # Get source and target shapes (may be absent if an endpoint is free-floating)
    source_shape = shapes.get(source_id) if source_id else None
    target_shape = shapes.get(target_id) if target_id else None

    if not source_shape and not target_shape and not (
        connection.get('source_point') and connection.get('target_point')
    ):
        # Not enough information to compute endpoints.
        return ((0, 0), (0, 0))

    # Calculate source point.
    # Draw.io uses the source shape anchor when both a source shape and a
    # ``sourcePoint`` exist, so we mirror that behaviour here — otherwise
    # every autosaved edge would be reported as a false crossing.
    if source_shape:
        src_x = float(source_shape.get('x', 0))
        src_y = float(source_shape.get('y', 0))
        src_w = float(source_shape.get('width', 120))
        src_h = float(source_shape.get('height', 60))

        exit_x = float(connection.get('exit_x', 0.5))
        exit_y = float(connection.get('exit_y', 0.5))

        start_x = src_x + src_w * exit_x
        start_y = src_y + src_h * exit_y
    elif connection.get('source_point'):
        start_x = float(connection['source_point'][0])
        start_y = float(connection['source_point'][1])
    else:
        return ((0, 0), (0, 0))

    # Calculate target point — same precedence as above.
    if target_shape:
        tgt_x = float(target_shape.get('x', 0))
        tgt_y = float(target_shape.get('y', 0))
        tgt_w = float(target_shape.get('width', 120))
        tgt_h = float(target_shape.get('height', 60))

        entry_x = float(connection.get('entry_x', 0.5))
        entry_y = float(connection.get('entry_y', 0.5))

        end_x = tgt_x + tgt_w * entry_x
        end_y = tgt_y + tgt_h * entry_y
    elif connection.get('target_point'):
        end_x = float(connection['target_point'][0])
        end_y = float(connection['target_point'][1])
    else:
        return ((0, 0), (0, 0))

    return ((start_x, start_y), (end_x, end_y))


def _to_float_or_default(value, default: float = 0.0) -> float:
    """Convert value to float, with a default fallback."""
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _is_uml_section(style: str) -> bool:
    """Heuristic for UML class subsection cells.

    UML section cells always carry ``portConstraint=eastwest`` in the style
    strings this server emits.  The looser ``line;...;strokeWidth`` fallback
    from earlier versions matched ordinary divider lines in user diagrams
    and caused spurious skips, so we only honor the authoritative marker
    here.
    """
    style_l = (style or "").lower()
    return "portconstraint=eastwest" in style_l


def _label(cell: dict) -> str:
    """Return a readable label for a cell."""
    raw = (cell.get("value") or "").strip()
    if raw:
        return re.sub(r"<[^>]+>", "", raw).strip() or cell.get("id", "(unknown)")
    return cell.get("id", "(unknown)")


def _connection_points(
    connection: dict,
    shapes: dict,
) -> list[tuple[float, float]]:
    """Get ordered path points for a connection (start -> waypoints -> end)."""
    start, end = get_connection_endpoints(connection, shapes)
    points = [start]

    for waypoint in connection.get("waypoints", []):
        if isinstance(waypoint, (list, tuple)) and len(waypoint) >= 2:
            points.append((_to_float_or_default(waypoint[0]), _to_float_or_default(waypoint[1])))

    points.append(end)
    return points


def _segments_from_points(points: list[tuple[float, float]]) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    """Convert path points to line segments."""
    segments = []
    for i in range(len(points) - 1):
        if points[i] != points[i + 1]:
            segments.append((points[i], points[i + 1]))
    return segments


def _points_equal(p1: tuple[float, float], p2: tuple[float, float], eps: float = 1e-6) -> bool:
    """Compare 2 points with tolerance."""
    return abs(p1[0] - p2[0]) <= eps and abs(p1[1] - p2[1]) <= eps


def line_segments_intersect(
    p1: tuple[float, float],
    p2: tuple[float, float],
    p3: tuple[float, float],
    p4: tuple[float, float]
) -> Optional[tuple[float, float]]:
    """
    Check if two line segments (p1-p2) and (p3-p4) intersect.
    
    Uses the parametric line equation to find intersection point.
    
    Args:
        p1: Start point of first line segment (x, y)
        p2: End point of first line segment (x, y)
        p3: Start point of second line segment (x, y)
        p4: End point of second line segment (x, y)
        
    Returns:
        The intersection point (x, y) if segments intersect, None otherwise
    """
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4
    
    # Calculate denominators
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    
    if abs(denom) < 1e-10:
        # Lines are parallel or coincident
        return None
    
    # Calculate parameters t and u
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
    
    # Check if intersection is within both line segments
    if 0 <= t <= 1 and 0 <= u <= 1:
        # Calculate intersection point
        intersect_x = x1 + t * (x2 - x1)
        intersect_y = y1 + t * (y2 - y1)
        return (intersect_x, intersect_y)
    
    return None


def _is_shared_endpoint_intersection(
    intersection: tuple[float, float],
    seg1: tuple[tuple[float, float], tuple[float, float]],
    seg2: tuple[tuple[float, float], tuple[float, float]],
) -> bool:
    """Return True if intersection is only at an endpoint shared by both segments."""
    p1, p2 = seg1
    p3, p4 = seg2
    return (
        (_points_equal(intersection, p1) or _points_equal(intersection, p2))
        and (_points_equal(intersection, p3) or _points_equal(intersection, p4))
    )


def _segment_crosses_rect(
    p1: tuple[float, float],
    p2: tuple[float, float],
    rect: tuple[float, float, float, float]
) -> bool:
    """Return True if segment p1→p2 passes through the rectangle interior.

    Uses Liang–Barsky parametric clipping, which robustly handles cases that
    a corner-intersection count would miss (e.g. a segment that enters along
    one edge, crosses the interior, and exits through the same or an
    adjacent edge with only a single unique intersection point).
    """
    rx, ry, rw, rh = rect
    if rw <= 0 or rh <= 0:
        return False

    x1, y1 = p1
    x2, y2 = p2

    def _inside(px: float, py: float) -> bool:
        return rx < px < rx + rw and ry < py < ry + rh

    if _inside(x1, y1) or _inside(x2, y2):
        return True

    dx = x2 - x1
    dy = y2 - y1
    t_enter = 0.0
    t_exit = 1.0
    for p, q in ((-dx, x1 - rx), (dx, rx + rw - x1), (-dy, y1 - ry), (dy, ry + rh - y1)):
        if abs(p) < 1e-12:
            if q < 0:
                return False
            continue
        t = q / p
        if p < 0:
            if t > t_exit:
                return False
            if t > t_enter:
                t_enter = t
        else:
            if t < t_enter:
                return False
            if t < t_exit:
                t_exit = t
    return t_exit - t_enter > 1e-9


def detect_crossings(cells: list[dict]) -> list[dict]:
    """
    Detect all line crossings in a diagram.
    
    Args:
        cells: List of all cells (shapes and connections) from the diagram
        
    Returns:
        List of crossing information dictionaries, each containing:
        - connection1_id: ID of first crossing connection
        - connection1_label: Label of first connection
        - connection2_id: ID of second crossing connection
        - connection2_label: Label of second connection
        - intersection_point: (x, y) coordinates where lines cross
        - suggestion: Text suggestion for how to fix the crossing
    """
    # Separate shapes and connections
    shapes = {cell['id']: cell for cell in cells if cell.get('vertex')}
    connections = [cell for cell in cells if cell.get('edge')]
    
    crossings = []
    
    # Check each pair of connections
    for i, conn1 in enumerate(connections):
        for conn2 in connections[i + 1:]:
            points1 = _connection_points(conn1, shapes)
            points2 = _connection_points(conn2, shapes)
            segments1 = _segments_from_points(points1)
            segments2 = _segments_from_points(points2)

            found_intersection = None
            for seg1 in segments1:
                for seg2 in segments2:
                    intersection = line_segments_intersect(seg1[0], seg1[1], seg2[0], seg2[1])
                    if not intersection:
                        continue
                    if _is_shared_endpoint_intersection(intersection, seg1, seg2):
                        continue
                    found_intersection = intersection
                    break
                if found_intersection:
                    break

            if found_intersection:
                suggestion = _generate_crossing_suggestion(
                    conn1, conn2, found_intersection, shapes
                )

                crossings.append({
                    'issue_type': 'line_crossing',
                    'connection1_id': conn1['id'],
                    'connection1_label': conn1.get('value', '(no label)'),
                    'connection2_id': conn2['id'],
                    'connection2_label': conn2.get('value', '(no label)'),
                    'intersection_point': found_intersection,
                    'suggestion': suggestion
                })

    # Detect connection segments crossing through unrelated node interiors
    for conn in connections:
        source_id = conn.get('source')
        target_id = conn.get('target')
        points = _connection_points(conn, shapes)
        segments = _segments_from_points(points)
        if not segments:
            continue

        for shape_id, shape in shapes.items():
            if shape_id in {source_id, target_id}:
                continue
            if _is_uml_section(shape.get("style", "")):
                continue

            w = _to_float_or_default(shape.get('width'))
            h = _to_float_or_default(shape.get('height'))
            if w <= 0 or h <= 0:
                continue
            rect = (
                _to_float_or_default(shape.get('x')),
                _to_float_or_default(shape.get('y')),
                w,
                h,
            )

            if any(_segment_crosses_rect(s1, s2, rect) for s1, s2 in segments):
                shape_label = _label(shape)
                conn_label = conn.get('value', '(no label)')
                suggestion = (
                    f"Connection '{conn_label}' passes through node '{shape_label}'. "
                    "Add waypoints or adjust entry/exit points so the line routes around the node."
                )
                crossings.append({
                    'issue_type': 'node_crossing',
                    'connection1_id': conn['id'],
                    'connection1_label': conn_label,
                    'connection2_id': shape_id,
                    'connection2_label': shape_label,
                    'intersection_point': None,
                    'suggestion': suggestion,
                })
    
    return crossings


def _generate_crossing_suggestion(
    conn1: dict,
    conn2: dict,
    intersection: tuple[float, float],
    shapes: dict
) -> str:
    """
    Generate a human-readable suggestion for fixing a line crossing.
    
    Args:
        conn1: First connection
        conn2: Second connection
        intersection: Point where lines cross (x, y)
        shapes: Dictionary of shapes
        
    Returns:
        Suggestion text
    """
    ix, iy = intersection
    
    # Get connection labels for better description
    label1 = conn1.get('value', conn1['id'])
    label2 = conn2.get('value', conn2['id'])
    
    suggestions = []
    suggestions.append(
        f"Lines cross at ({ix:.1f}, {iy:.1f}). Consider these adjustments:"
    )
    
    # Get source and target for both connections
    src1_id = conn1.get('source')
    tgt1_id = conn1.get('target')
    src2_id = conn2.get('source')
    tgt2_id = conn2.get('target')
    
    # Suggest using waypoints
    suggestions.append(
        f"  1. Add waypoints to '{label1}' to route around the crossing"
    )
    suggestions.append(
        f"  2. Add waypoints to '{label2}' to route around the crossing"
    )
    
    # Suggest repositioning shapes if possible
    if src1_id in shapes and tgt1_id in shapes:
        suggestions.append(
            f"  3. Reposition shapes connected by '{label1}' to avoid crossing"
        )
    
    if src2_id in shapes and tgt2_id in shapes:
        suggestions.append(
            f"  4. Reposition shapes connected by '{label2}' to avoid crossing"
        )
    
    # Suggest adjusting entry/exit points
    suggestions.append(
        f"  5. Adjust entry/exit points to change connection angles"
    )
    
    return "\n".join(suggestions)
