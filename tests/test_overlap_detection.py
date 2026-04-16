#!/usr/bin/env python3
"""
Tests for the overlap detection feature.

Covers:
- No overlaps detected when shapes are well-separated
- Node–node overlap detected correctly
- Out-of-container violation detected correctly
- UML section children are not falsely reported
"""

from mcp_drawio_server.diagram import Diagram
from mcp_drawio_server.xml_operations import get_cells_from_xml
from mcp_drawio_server.overlap_detector import detect_overlaps


def _cells(diagram: Diagram) -> list[dict]:
    return get_cells_from_xml(diagram.to_drawio_xml())


# ---------------------------------------------------------------------------
# No-overlap baseline
# ---------------------------------------------------------------------------

def test_no_overlap_separated_shapes():
    """Well-separated shapes must not trigger any overlap reports."""
    d = Diagram("no-overlap")
    d.add_shape("A", x=0, y=0, width=100, height=60)
    d.add_shape("B", x=200, y=0, width=100, height=60)
    d.add_shape("C", x=0, y=200, width=100, height=60)

    result = detect_overlaps(_cells(d))
    assert result["node_overlaps"] == [], "Expected no node overlaps"
    assert result["out_of_container"] == [], "Expected no container violations"


# ---------------------------------------------------------------------------
# Node–node overlap
# ---------------------------------------------------------------------------

def test_node_overlap_detected():
    """Two partially-overlapping shapes must be reported."""
    d = Diagram("overlap")
    d.add_shape("X", x=0, y=0, width=100, height=60)
    d.add_shape("Y", x=50, y=30, width=100, height=60)   # overlaps X

    result = detect_overlaps(_cells(d))
    overlaps = result["node_overlaps"]
    assert len(overlaps) == 1, f"Expected 1 overlap, got {len(overlaps)}"

    pair_labels = {overlaps[0]["shape1_label"], overlaps[0]["shape2_label"]}
    assert pair_labels == {"X", "Y"}


def test_touching_shapes_not_reported():
    """Shapes that share only an edge (no area intersection) must not be reported."""
    d = Diagram("touching")
    d.add_shape("A", x=0, y=0, width=100, height=60)
    d.add_shape("B", x=100, y=0, width=100, height=60)  # touches A on right edge

    result = detect_overlaps(_cells(d))
    assert result["node_overlaps"] == [], "Touching (non-overlapping) shapes should not be reported"


def test_overlap_suggestion_contains_fix():
    """Overlap suggestion must mention which shape to move and include new_x/new_y hint."""
    d = Diagram("overlap-fix")
    d.add_shape("Left", x=0, y=0, width=120, height=60)
    d.add_shape("Right", x=60, y=0, width=120, height=60)  # overlaps Left

    result = detect_overlaps(_cells(d))
    assert result["node_overlaps"], "Expected at least one overlap"
    suggestion = result["node_overlaps"][0]["suggestion"]
    assert "Left" in suggestion or "Right" in suggestion
    assert "new_x" in suggestion.lower() or "move" in suggestion.lower()


def test_multiple_overlaps_all_reported():
    """All overlapping pairs must be reported independently."""
    d = Diagram("multi-overlap")
    # Three mutually-overlapping shapes
    d.add_shape("A", x=0, y=0, width=100, height=100)
    d.add_shape("B", x=50, y=0, width=100, height=100)
    d.add_shape("C", x=25, y=50, width=100, height=100)

    result = detect_overlaps(_cells(d))
    # A-B, A-C, B-C each overlap → 3 pairs
    assert len(result["node_overlaps"]) == 3, (
        f"Expected 3 overlap pairs, got {len(result['node_overlaps'])}"
    )


# ---------------------------------------------------------------------------
# Out-of-container
# ---------------------------------------------------------------------------

def test_shape_inside_container_no_violation():
    """A shape fully inside its parent container must not be reported."""
    d = Diagram("contained")
    container_id = d.add_shape("Domain", x=0, y=0, width=400, height=300, shape_type="container")
    d.add_shape("NodeA", x=50, y=50, width=100, height=60, parent_id=container_id)

    result = detect_overlaps(_cells(d))
    assert result["out_of_container"] == [], "NodeA is fully inside Domain — no violation expected"


def test_shape_escaping_container_detected():
    """A shape whose bounds extend beyond its parent container must be reported."""
    d = Diagram("escape")
    container_id = d.add_shape("Domain", x=0, y=0, width=200, height=150, shape_type="container")
    # Node placed so its right edge (50+200=250) exceeds container right edge (200)
    d.add_shape("BigNode", x=50, y=20, width=200, height=80, parent_id=container_id)

    result = detect_overlaps(_cells(d))
    violations = result["out_of_container"]
    assert len(violations) >= 1, "Expected at least one out-of-container violation"
    assert violations[0]["container_id"] == container_id


def test_out_of_container_suggestion_actionable():
    """Out-of-container suggestion must mention overflow direction and a fix."""
    d = Diagram("escape-fix")
    cid = d.add_shape("Container", x=0, y=0, width=150, height=150, shape_type="container")
    d.add_shape("Child", x=100, y=20, width=100, height=60, parent_id=cid)

    result = detect_overlaps(_cells(d))
    violations = result["out_of_container"]
    assert violations, "Expected a containment violation"
    suggestion = violations[0]["suggestion"]
    assert "overflow" in suggestion.lower() or "extend" in suggestion.lower() or "right" in suggestion.lower()


# ---------------------------------------------------------------------------
# UML class sections must not be falsely flagged
# ---------------------------------------------------------------------------

def test_uml_class_sections_not_reported_as_overlaps():
    """UML class section sub-cells must not be reported as sibling overlaps."""
    d = Diagram("uml-no-false-positive")
    d.add_shape(
        "User\n───────\n- id: int\n- name: string\n───────\n+ login()",
        x=50, y=50, width=200, height=140,
        shape_type="uml_class",
    )

    result = detect_overlaps(_cells(d))
    assert result["node_overlaps"] == [], (
        "UML section cells must not be reported as node–node overlaps"
    )


def test_two_separate_uml_classes_no_overlap():
    """Two well-spaced UML class boxes must not be reported as overlapping."""
    d = Diagram("two-uml")
    d.add_shape("ClassA", x=0, y=0, width=180, height=100, shape_type="uml_class")
    d.add_shape("ClassB", x=300, y=0, width=180, height=100, shape_type="uml_class")

    result = detect_overlaps(_cells(d))
    # Filter to only top-level shapes (not section children)
    assert result["node_overlaps"] == [], (
        "Two non-overlapping UML classes should not be reported"
    )
