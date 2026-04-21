"""Regression tests for the "line crosses node / labels overlap" badcase.

These cover the scenarios the user reported as unresolved:
* A connection routed around one obstacle should still clear *other* obstacles
  that lie on its way (multi-obstacle iterative routing).
* ``detect_overlaps`` must surface edge labels that sit on top of unrelated
  nodes, as well as edge labels that stack on top of other edge labels.
"""

from mcp_drawio_server.diagram import Diagram
from mcp_drawio_server.xml_operations import get_cells_from_xml
from mcp_drawio_server.crossing_detector import detect_crossings
from mcp_drawio_server.overlap_detector import detect_overlaps


def _node_crossings(cells):
    return [c for c in detect_crossings(cells) if c.get("issue_type") == "node_crossing"]


def test_auto_route_clears_multiple_obstacles():
    """A source-to-target line with TWO obstacles between them should route clear."""
    d = Diagram(name="Multi-obstacle")
    source = d.add_shape("A", x=0, y=0, width=80, height=60)
    target = d.add_shape("B", x=700, y=0, width=80, height=60)
    # Two obstacles both on the straight midline between A and B.
    d.add_shape("Ob1", x=200, y=-20, width=80, height=100)
    d.add_shape("Ob2", x=450, y=-20, width=80, height=100)

    d.add_connection(source, target, label="flow", edge_style="straight")

    cells = get_cells_from_xml(d.to_drawio_xml())
    assert _node_crossings(cells) == [], (
        "Auto-routed connection should avoid every obstacle on its path"
    )


def test_auto_route_prefers_candidate_with_fewest_intersections():
    """When one side is blocked by more obstacles, the router should pick the other."""
    d = Diagram(name="Asymmetric obstacles")
    source = d.add_shape("A", x=0, y=0, width=80, height=60)
    target = d.add_shape("B", x=500, y=0, width=80, height=60)
    # Three obstacles clustered above; clear space below.
    d.add_shape("Above1", x=150, y=-120, width=80, height=80)
    d.add_shape("Above2", x=250, y=-120, width=80, height=80)
    d.add_shape("Above3", x=350, y=-120, width=80, height=80)
    # One obstacle right on the center line to force a detour.
    d.add_shape("Center", x=220, y=-20, width=120, height=100)

    d.add_connection(source, target, label="flow", edge_style="straight")

    cells = get_cells_from_xml(d.to_drawio_xml())
    assert _node_crossings(cells) == [], (
        "Router should choose the detour side with fewer obstacles"
    )


def test_detect_overlaps_reports_edge_label_over_node():
    """An edge whose label anchor lands inside an unrelated node is reported."""
    d = Diagram(name="Label over node")
    source = d.add_shape("A", x=0, y=0, width=80, height=60)
    target = d.add_shape("B", x=500, y=0, width=80, height=60)
    d.add_shape("Obstacle", x=200, y=-30, width=120, height=120)

    # auto_route=False + auto_avoid_label_overlap=False guarantees the label
    # anchor falls on the straight center line and is NOT nudged away.
    d.add_connection(
        source, target, label="midlabel",
        edge_style="straight",
        auto_route=False,
        auto_avoid_label_overlap=False,
    )

    cells = get_cells_from_xml(d.to_drawio_xml())
    label_overlaps = detect_overlaps(cells)["label_overlaps"]
    assert any(
        item.get("issue_type") == "edge_label_over_node"
        for item in label_overlaps
    ), f"Expected edge_label_over_node in {label_overlaps!r}"


def test_detect_overlaps_reports_edge_label_over_label():
    """Two edges whose labels land at the same midpoint collide."""
    d = Diagram(name="Label stack")
    a = d.add_shape("A", x=0, y=0, width=80, height=60)
    b = d.add_shape("B", x=400, y=0, width=80, height=60)
    c = d.add_shape("C", x=0, y=150, width=80, height=60)
    dd = d.add_shape("D", x=400, y=150, width=80, height=60)

    d.add_connection(a, b, label="one", auto_route=False, auto_avoid_label_overlap=False)
    d.add_connection(c, dd, label="two", auto_route=False, auto_avoid_label_overlap=False)
    # Force both labels to land in the same place by explicitly giving them
    # the same offset. This is the configuration the user reported.
    for conn in d.connections.values():
        conn.label_offset_x = 0.0
        conn.label_offset_y = 0.0

    # Also build an intentional label-stack case using explicit label_offset.
    e = d.add_shape("E", x=0, y=300, width=80, height=60)
    f = d.add_shape("F", x=400, y=300, width=80, height=60)
    d.add_connection(e, f, label="same-spot",
                     auto_route=False, auto_avoid_label_overlap=False,
                     label_offset_x=0, label_offset_y=-150)

    cells = get_cells_from_xml(d.to_drawio_xml())
    label_overlaps = detect_overlaps(cells)["label_overlaps"]
    assert any(
        item.get("issue_type") == "edge_label_over_edge_label"
        for item in label_overlaps
    ), f"Expected edge_label_over_edge_label in {label_overlaps!r}"


def test_auto_label_avoidance_considers_existing_labels():
    """When two connections would share a label anchor, the second one is nudged."""
    d = Diagram(name="Label avoidance stacking")
    a = d.add_shape("A", x=0, y=0, width=80, height=60)
    b = d.add_shape("B", x=400, y=0, width=80, height=60)
    c = d.add_shape("C", x=0, y=0, width=80, height=60)  # on top of A
    dd = d.add_shape("D", x=400, y=0, width=80, height=60)  # on top of B

    # First connection uses the default anchor (no offset needed).
    d.add_connection(a, b, label="first")
    # Second connection shares the same midpoint → auto label avoidance
    # should now see the first label as an obstacle and insert an offset.
    conn_id = d.add_connection(c, dd, label="second")
    conn = d.connections[conn_id]
    assert conn.label_offset_x is not None or conn.label_offset_y is not None
