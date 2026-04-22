"""Regression tests for edge / node binding XML emission (Requirement 3)."""

import pytest

from mcp_drawio_server.diagram import Diagram


def test_connection_with_free_source_point():
    """An edge with an explicit source_point but no source_id should not emit source=""."""
    d = Diagram()
    target = d.add_shape("Target", x=200, y=100)
    conn_id = d.add_connection(
        source_id="",
        target_id=target,
        source_point=(0.0, 0.0),
    )
    xml = d.to_drawio_xml()
    # Must not emit an empty source="" attribute — drawio treats that as a
    # dangling reference and drops the binding entirely.
    assert 'source=""' not in xml
    assert f'target="{target}"' in xml
    # Conn must still be present.
    assert conn_id in xml


def test_connection_with_free_target_point():
    d = Diagram()
    src = d.add_shape("Src", x=0, y=0)
    conn_id = d.add_connection(
        source_id=src,
        target_id="",
        target_point=(500.0, 500.0),
    )
    xml = d.to_drawio_xml()
    assert 'target=""' not in xml
    assert f'source="{src}"' in xml
    assert conn_id in xml


def test_connection_both_ids_must_exist_when_set():
    """Non-empty source_id pointing to an unknown shape must raise."""
    d = Diagram()
    good = d.add_shape("Good", x=0, y=0)
    with pytest.raises(ValueError, match="not found"):
        d.add_connection(source_id="does_not_exist", target_id=good)


def test_connection_requires_some_source():
    """Empty source_id with no source_point must fail fast."""
    d = Diagram()
    tgt = d.add_shape("Target", x=0, y=0)
    with pytest.raises(ValueError, match="source_id or source_point"):
        d.add_connection(source_id="", target_id=tgt)


def test_edge_parent_is_lca_when_endpoints_share_container():
    """When both endpoints sit inside the same container, edge parent == container."""
    d = Diagram()
    container = d.add_shape("Container", x=0, y=0, width=400, height=300, shape_type="container")
    a = d.add_shape("A", x=10, y=40, parent_id=container)
    b = d.add_shape("B", x=200, y=40, parent_id=container)
    conn_id = d.add_connection(source_id=a, target_id=b)
    xml = d.to_drawio_xml()
    # Find the edge's `parent=` attribute (LCA should be the container).
    edge_line = next(line for line in xml.splitlines() if f'id="{conn_id}"' in line)
    assert f'parent="{container}"' in edge_line


def test_edge_parent_falls_back_to_root_for_top_level_edges():
    """Edges between two top-level shapes still live at the graph root."""
    d = Diagram()
    a = d.add_shape("A", x=0, y=0)
    b = d.add_shape("B", x=200, y=0)
    conn_id = d.add_connection(source_id=a, target_id=b)
    xml = d.to_drawio_xml()
    edge_line = next(line for line in xml.splitlines() if f'id="{conn_id}"' in line)
    assert 'parent="1"' in edge_line


def test_edge_parent_not_inside_one_of_its_endpoints():
    """If A is the parent of B, the edge between them must not have parent=A
    (that would put the edge *inside* one of its own endpoints)."""
    d = Diagram()
    outer = d.add_shape("Outer", x=0, y=0, width=400, height=300, shape_type="container")
    inner = d.add_shape("Inner", x=20, y=40, parent_id=outer)
    conn_id = d.add_connection(source_id=outer, target_id=inner)
    xml = d.to_drawio_xml()
    edge_line = next(line for line in xml.splitlines() if f'id="{conn_id}"' in line)
    # Edge parent should hoist to the graph root, not stay inside "outer".
    assert f'parent="{outer}"' not in edge_line
    assert 'parent="1"' in edge_line
