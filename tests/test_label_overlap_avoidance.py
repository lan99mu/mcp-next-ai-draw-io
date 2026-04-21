#!/usr/bin/env python3
"""Tests for auto label overlap avoidance on connections."""

from mcp_drawio_server.diagram import Diagram


def test_label_offset_inserted_when_midpoint_inside_node():
    """When the label's midpoint would land inside another node, an offset is added."""
    diagram = Diagram(name="Label Overlap")

    # A and B are far apart on the x axis; the label midpoint (around x=200, y=30)
    # falls directly inside the obstacle.
    source = diagram.add_shape('A', x=0, y=0, width=80, height=60)
    target = diagram.add_shape('B', x=400, y=0, width=80, height=60)
    # Place obstacle centered on the natural label midpoint.  Auto-route will
    # inject a waypoint around it but the label midpoint on the routed
    # polyline still risks falling inside another shape — disable auto_route
    # here so we can verify the label-offset logic independently.
    diagram.add_shape('Obstacle', x=140, y=-20, width=120, height=100)

    conn_id = diagram.add_connection(
        source, target, label="call",
        edge_style="straight",
        auto_route=False,
    )
    conn = diagram.connections[conn_id]

    # Either label_offset_x or label_offset_y should be set to push it away.
    assert conn.label_offset_x is not None or conn.label_offset_y is not None


def test_no_label_offset_when_path_is_clear():
    """When there's nothing between source and target, no label offset is added."""
    diagram = Diagram(name="Clear Label")

    source = diagram.add_shape('A', x=0, y=0, width=80, height=60)
    target = diagram.add_shape('B', x=300, y=0, width=80, height=60)

    conn_id = diagram.add_connection(source, target, label="call")
    conn = diagram.connections[conn_id]

    assert conn.label_offset_x is None
    assert conn.label_offset_y is None


def test_explicit_offset_is_preserved():
    """User-supplied label_offset_x/y is not overridden by auto avoidance."""
    diagram = Diagram(name="Explicit Offset")

    source = diagram.add_shape('A', x=0, y=0, width=80, height=60)
    target = diagram.add_shape('B', x=400, y=0, width=80, height=60)
    diagram.add_shape('Obstacle', x=140, y=-20, width=120, height=100)

    conn_id = diagram.add_connection(
        source, target, label="call",
        edge_style="straight",
        auto_route=False,
        label_offset_x=12.5,
        label_offset_y=-3.0,
    )
    conn = diagram.connections[conn_id]
    assert conn.label_offset_x == 12.5
    assert conn.label_offset_y == -3.0


def test_disable_label_avoidance():
    """``auto_avoid_label_overlap=False`` leaves the label offset untouched."""
    diagram = Diagram(name="Disable Avoidance")

    source = diagram.add_shape('A', x=0, y=0, width=80, height=60)
    target = diagram.add_shape('B', x=400, y=0, width=80, height=60)
    diagram.add_shape('Obstacle', x=140, y=-20, width=120, height=100)

    conn_id = diagram.add_connection(
        source, target, label="call",
        edge_style="straight",
        auto_route=False,
        auto_avoid_label_overlap=False,
    )
    conn = diagram.connections[conn_id]
    assert conn.label_offset_x is None
    assert conn.label_offset_y is None


def test_empty_label_skips_avoidance():
    """Connections without a label should not get a spurious offset."""
    diagram = Diagram(name="No Label")

    source = diagram.add_shape('A', x=0, y=0, width=80, height=60)
    target = diagram.add_shape('B', x=400, y=0, width=80, height=60)
    diagram.add_shape('Obstacle', x=140, y=-20, width=120, height=100)

    conn_id = diagram.add_connection(
        source, target, label="",
        edge_style="straight",
        auto_route=False,
    )
    conn = diagram.connections[conn_id]
    assert conn.label_offset_x is None
    assert conn.label_offset_y is None
