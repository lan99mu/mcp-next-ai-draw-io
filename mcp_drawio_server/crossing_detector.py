"""
Utility module for detecting line crossings in Draw.io diagrams.

This module provides functions to detect when connections (lines) cross each other
and provide position hints to help AI models adjust them.
"""

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
    
    if not source_id or not target_id:
        return ((0, 0), (0, 0))
    
    # Get source and target shapes
    source_shape = shapes.get(source_id)
    target_shape = shapes.get(target_id)
    
    if not source_shape or not target_shape:
        return ((0, 0), (0, 0))
    
    # Calculate source point
    if connection.get('source_point'):
        # Explicit source point
        start_x = float(connection['source_point'][0])
        start_y = float(connection['source_point'][1])
    else:
        # Use exit point or center
        src_x = float(source_shape.get('x', 0))
        src_y = float(source_shape.get('y', 0))
        src_w = float(source_shape.get('width', 120))
        src_h = float(source_shape.get('height', 60))
        
        exit_x = float(connection.get('exit_x', 0.5))
        exit_y = float(connection.get('exit_y', 0.5))
        
        start_x = src_x + src_w * exit_x
        start_y = src_y + src_h * exit_y
    
    # Calculate target point
    if connection.get('target_point'):
        # Explicit target point
        end_x = float(connection['target_point'][0])
        end_y = float(connection['target_point'][1])
    else:
        # Use entry point or center
        tgt_x = float(target_shape.get('x', 0))
        tgt_y = float(target_shape.get('y', 0))
        tgt_w = float(target_shape.get('width', 120))
        tgt_h = float(target_shape.get('height', 60))
        
        entry_x = float(connection.get('entry_x', 0.5))
        entry_y = float(connection.get('entry_y', 0.5))
        
        end_x = tgt_x + tgt_w * entry_x
        end_y = tgt_y + tgt_h * entry_y
    
    return ((start_x, start_y), (end_x, end_y))


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
            # Get endpoints for both connections
            start1, end1 = get_connection_endpoints(conn1, shapes)
            start2, end2 = get_connection_endpoints(conn2, shapes)
            
            # For now, we'll check simple line segment intersection
            # TODO: Handle waypoints by checking each segment between consecutive waypoints.
            # This would involve: 1) Getting waypoint list from connection, 2) Creating
            # segments between start->wp1, wp1->wp2, ..., wpN->end, 3) Checking each
            # segment pair for intersections.
            intersection = line_segments_intersect(start1, end1, start2, end2)
            
            if intersection:
                # Generate suggestion
                suggestion = _generate_crossing_suggestion(
                    conn1, conn2, intersection, shapes
                )
                
                crossings.append({
                    'connection1_id': conn1['id'],
                    'connection1_label': conn1.get('value', '(no label)'),
                    'connection2_id': conn2['id'],
                    'connection2_label': conn2.get('value', '(no label)'),
                    'intersection_point': intersection,
                    'suggestion': suggestion
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
