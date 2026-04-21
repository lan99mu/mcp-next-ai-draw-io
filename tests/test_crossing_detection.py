#!/usr/bin/env python3
"""
Test script for line crossing detection feature.
"""

from mcp_drawio_server.diagram import Diagram
from mcp_drawio_server.xml_operations import get_cells_from_xml
from mcp_drawio_server.crossing_detector import detect_crossings


def test_crossing_detection():
    """Test basic crossing detection"""
    print("\n" + "=" * 70)
    print("TEST: Line Crossing Detection")
    print("=" * 70)
    
    # Create a diagram with crossing lines
    diagram = Diagram(name="Crossing Test")
    
    # Create 4 shapes arranged in a square pattern
    # A (top-left)     B (top-right)
    # C (bottom-left)  D (bottom-right)
    s1 = diagram.add_shape('A', x=0, y=0, width=80, height=60)
    s2 = diagram.add_shape('B', x=300, y=0, width=80, height=60)
    s3 = diagram.add_shape('C', x=0, y=200, width=80, height=60)
    s4 = diagram.add_shape('D', x=300, y=200, width=80, height=60)
    
    # Add two connections that will cross
    # Line 1: from A to D (top-left to bottom-right)
    c1 = diagram.add_connection(s1, s4, label="Line 1")
    
    # Line 2: from B to C (top-right to bottom-left) - should cross with Line 1
    c2 = diagram.add_connection(s2, s3, label="Line 2")
    
    print(f"Created diagram with 4 shapes and 2 connections")
    print(f"  Shape A: (0, 0)")
    print(f"  Shape B: (300, 0)")
    print(f"  Shape C: (0, 200)")
    print(f"  Shape D: (300, 200)")
    print(f"  Line 1: A → D (diagonal)")
    print(f"  Line 2: B → C (diagonal)")
    
    # Convert to XML and parse cells
    xml_content = diagram.to_drawio_xml()
    cells = get_cells_from_xml(xml_content)
    
    print(f"\nParsed {len(cells)} cells from diagram")
    
    # Detect crossings
    crossings = detect_crossings(cells)
    
    print(f"\nDetected {len(crossings)} crossing(s)")
    
    if crossings:
        for i, crossing in enumerate(crossings, 1):
            print(f"\nCrossing {i}:")
            print(f"  Connection 1: {crossing['connection1_label']} (ID: {crossing['connection1_id']})")
            print(f"  Connection 2: {crossing['connection2_label']} (ID: {crossing['connection2_id']})")
            print(f"  Intersection at: ({crossing['intersection_point'][0]:.1f}, {crossing['intersection_point'][1]:.1f})")
            print(f"  Suggestion:\n{crossing['suggestion']}")
        print("\n✓ Crossing detection successful!")
    else:
        print("\n✗ ERROR: Expected to find crossings but found none!")
        return False
    
    return True


def test_no_crossing():
    """Test that parallel lines are not detected as crossing"""
    print("\n" + "=" * 70)
    print("TEST: No Crossing Detection")
    print("=" * 70)
    
    # Create a diagram with non-crossing lines
    diagram = Diagram(name="No Crossing Test")
    
    # Create 4 shapes arranged horizontally
    s1 = diagram.add_shape('A', x=0, y=0, width=80, height=60)
    s2 = diagram.add_shape('B', x=150, y=0, width=80, height=60)
    s3 = diagram.add_shape('C', x=300, y=0, width=80, height=60)
    s4 = diagram.add_shape('D', x=450, y=0, width=80, height=60)
    
    # Add connections that don't cross
    # Line 1: A → B
    c1 = diagram.add_connection(s1, s2, label="Line 1")
    
    # Line 2: C → D (separate from Line 1)
    c2 = diagram.add_connection(s3, s4, label="Line 2")
    
    print(f"Created diagram with 4 shapes and 2 non-crossing connections")
    
    # Convert to XML and parse cells
    xml_content = diagram.to_drawio_xml()
    cells = get_cells_from_xml(xml_content)
    
    # Detect crossings
    crossings = detect_crossings(cells)
    
    print(f"\nDetected {len(crossings)} crossing(s)")
    
    if len(crossings) == 0:
        print("✓ Correctly detected no crossings!")
        return True
    else:
        print("✗ ERROR: Found crossings where none should exist!")
        for crossing in crossings:
            print(f"  Unexpected crossing: {crossing['connection1_label']} ⨯ {crossing['connection2_label']}")
        return False


def test_multiple_crossings():
    """Test detection of multiple crossings"""
    print("\n" + "=" * 70)
    print("TEST: Multiple Crossings Detection")
    print("=" * 70)
    
    # Create a diagram with multiple crossing lines
    diagram = Diagram(name="Multiple Crossings Test")
    
    # Create 6 shapes
    s1 = diagram.add_shape('A', x=0, y=100, width=60, height=40)
    s2 = diagram.add_shape('B', x=250, y=0, width=60, height=40)
    s3 = diagram.add_shape('C', x=250, y=200, width=60, height=40)
    s4 = diagram.add_shape('D', x=500, y=100, width=60, height=40)
    
    # Create a star pattern with crossings
    # A → D (horizontal across middle)
    c1 = diagram.add_connection(s1, s4, label="Horizontal")
    
    # B → C (vertical down middle)
    c2 = diagram.add_connection(s2, s3, label="Vertical")
    
    # These two should cross in the middle
    
    print(f"Created diagram with star pattern connections")
    
    # Convert to XML and parse cells
    xml_content = diagram.to_drawio_xml()
    cells = get_cells_from_xml(xml_content)
    
    # Detect crossings
    crossings = detect_crossings(cells)
    
    print(f"\nDetected {len(crossings)} crossing(s)")
    
    if len(crossings) >= 1:
        print("✓ Correctly detected multiple crossings!")
        for i, crossing in enumerate(crossings, 1):
            print(f"  Crossing {i}: {crossing['connection1_label']} ⨯ {crossing['connection2_label']}")
        return True
    else:
        print("✗ ERROR: Expected to find crossings!")
        return False


def test_shared_endpoints_are_not_crossings():
    """Intersections at shared source/target endpoints should not be treated as crossings."""
    diagram = Diagram(name="Shared Endpoint Test")

    center = diagram.add_shape('Center', x=150, y=80, width=80, height=60)
    left = diagram.add_shape('Left', x=0, y=80, width=80, height=60)
    top = diagram.add_shape('Top', x=150, y=0, width=80, height=60)

    diagram.add_connection(left, center, label="left-to-center")
    diagram.add_connection(top, center, label="top-to-center")

    cells = get_cells_from_xml(diagram.to_drawio_xml())
    crossings = detect_crossings(cells)
    line_crossings = [c for c in crossings if c.get("issue_type") != "node_crossing"]

    assert line_crossings == [], "Shared endpoint intersections should not be reported as crossings"


def test_connection_crossing_node_is_reported():
    """A connection passing through an unrelated node should be reported.

    ``auto_route`` is disabled so the straight line really does cross the
    obstacle — the detection logic itself is what is being verified here.
    """
    diagram = Diagram(name="Node Crossing Test")

    source = diagram.add_shape('A', x=0, y=0, width=80, height=60)
    target = diagram.add_shape('B', x=320, y=0, width=80, height=60)
    obstacle = diagram.add_shape('Obstacle', x=160, y=-20, width=80, height=100)

    diagram.add_connection(
        source, target, label="A-to-B", edge_style="straight", auto_route=False
    )

    cells = get_cells_from_xml(diagram.to_drawio_xml())
    crossings = detect_crossings(cells)
    node_crossings = [c for c in crossings if c.get("issue_type") == "node_crossing"]

    assert len(node_crossings) == 1
    assert node_crossings[0]["connection2_label"] == "Obstacle"


def test_auto_route_avoids_intervening_node():
    """With ``auto_route=True`` (default) the connection detours around obstacles."""
    diagram = Diagram(name="Auto Route Test")

    source = diagram.add_shape('A', x=0, y=0, width=80, height=60)
    target = diagram.add_shape('B', x=320, y=0, width=80, height=60)
    diagram.add_shape('Obstacle', x=160, y=-20, width=80, height=100)

    conn_id = diagram.add_connection(source, target, label="A-to-B", edge_style="straight")
    assert diagram.connections[conn_id].waypoints, "Expected auto-routed waypoints"

    cells = get_cells_from_xml(diagram.to_drawio_xml())
    crossings = detect_crossings(cells)
    node_crossings = [c for c in crossings if c.get("issue_type") == "node_crossing"]
    assert node_crossings == [], "Auto-routed connection should not cross the obstacle"


def test_auto_route_noop_when_no_obstacle():
    """Connections with a clear path should not gain spurious waypoints."""
    diagram = Diagram(name="Clear Path")

    source = diagram.add_shape('A', x=0, y=0, width=80, height=60)
    target = diagram.add_shape('B', x=300, y=0, width=80, height=60)

    conn_id = diagram.add_connection(source, target, label="A-to-B")
    assert diagram.connections[conn_id].waypoints == []


if __name__ == "__main__":
    results = []
    
    results.append(("Basic Crossing Detection", test_crossing_detection()))
    results.append(("No Crossing Detection", test_no_crossing()))
    results.append(("Multiple Crossings", test_multiple_crossings()))
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n✓ All tests passed!")
        exit(0)
    else:
        print("\n✗ Some tests failed!")
        exit(1)
