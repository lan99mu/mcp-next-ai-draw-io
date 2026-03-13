#!/usr/bin/env python3
"""
Focused tests for get_cell geometry output and containment bindings.
"""

from mcp_drawio_server.diagram import Diagram
from mcp_drawio_server.handlers.cell_handlers import handle_get_cell
from mcp_drawio_server.handlers.state import diagram_state
from mcp_drawio_server.xml_operations import get_cells_from_xml


def setup_function():
    """Reset shared handler state before each test."""
    diagram_state.reset()


def teardown_function():
    """Reset shared handler state after each test."""
    diagram_state.reset()


def test_get_cells_extracts_parent_and_raw_geometry_points():
    """XML parsing should retain parent info and raw point definitions."""
    diagram = Diagram("Geometry Parse Test")

    source_id = diagram.add_shape("Source", x=100, y=100, width=100, height=60)
    target_id = diagram.add_shape("Target", x=320, y=100, width=120, height=80)
    child_id = diagram.add_shape("Child", x=20, y=30, width=60, height=40, parent_id=source_id)

    connection_id = diagram.add_connection(
        source_id=source_id,
        target_id=target_id,
        entry_x=0,
        entry_y=0.5,
        exit_x=1,
        exit_y=0.5,
        waypoints=[(240, 130)],
        source_point=(200, 130),
        target_point=(320, 140),
    )

    cells = get_cells_from_xml(diagram.to_drawio_xml())

    child_cell = next(cell for cell in cells if cell["id"] == child_id)
    assert child_cell["parent"] == source_id

    connection_cell = next(cell for cell in cells if cell["id"] == connection_id)
    assert connection_cell["geometry_points"] == [
        {"type": "entry", "x": "0.0", "y": "0.5"},
        {"type": "exit", "x": "1.0", "y": "0.5"},
        {"type": "waypoint", "x": "240", "y": "130"},
        {"type": "sourcePoint", "x": "200", "y": "130"},
        {"type": "targetPoint", "x": "320", "y": "140"},
    ]


def test_get_cell_returns_shape_points_and_containment_bindings():
    """get_cell should show node points, lines, and containment bind relationships."""
    diagram = Diagram("Containment Test")

    container_id = diagram.add_shape("Container", x=50, y=50, width=300, height=200, shape_type="container")
    child_id = diagram.add_shape("Child", x=20, y=30, width=80, height=40, parent_id=container_id)

    diagram_state.current_diagram = diagram
    result = handle_get_cell({"cell_id": container_id})[0].text

    assert "Points:" in result
    assert "top_left: (50.0, 50.0)" in result
    assert "bottom_right: (350.0, 250.0)" in result
    assert "Lines:" in result
    assert "top: (50.0, 50.0) -> (350.0, 50.0)" in result
    assert "Bind relationships:" in result
    assert f"contains: {child_id}" in result

    child_result = handle_get_cell({"cell_id": child_id})[0].text
    assert "Absolute position (top-left): (70.0, 80.0)" in child_result
    assert f"contained_by: {container_id}" in child_result


def test_get_cell_returns_connection_points_and_segments():
    """get_cell should show every edge point and line segment."""
    diagram = Diagram("Connection Geometry Test")

    source_id = diagram.add_shape("Source", x=100, y=100, width=100, height=60)
    target_id = diagram.add_shape("Target", x=320, y=120, width=100, height=60)

    connection_id = diagram.add_connection(
        source_id=source_id,
        target_id=target_id,
        exit_x=1,
        exit_y=0.5,
        entry_x=0,
        entry_y=0.5,
        waypoints=[(240, 130), (240, 150)],
    )

    diagram_state.current_diagram = diagram
    result = handle_get_cell({"cell_id": connection_id})[0].text

    assert "Entry anchor (normalized): (0.0, 0.5)" in result
    assert "Exit anchor (normalized): (1.0, 0.5)" in result
    assert "Points:" in result
    assert "source_anchor: (200.0, 130.0)" in result
    assert "waypoint_1: (240.0, 130.0)" in result
    assert "waypoint_2: (240.0, 150.0)" in result
    assert "target_anchor: (320.0, 150.0)" in result
    assert "Lines:" in result
    assert "source_anchor->waypoint_1: (200.0, 130.0) -> (240.0, 130.0)" in result
    assert "waypoint_2->target_anchor: (240.0, 150.0) -> (320.0, 150.0)" in result
