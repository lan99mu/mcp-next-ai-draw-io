"""Tests for update_cell extensions (Requirement 2)."""

from mcp_drawio_server.diagram import Diagram
from mcp_drawio_server.xml_operations import get_cells_from_xml, update_cell_in_xml


def test_update_cell_sets_waypoints():
    d = Diagram()
    a = d.add_shape("A", x=0, y=0)
    b = d.add_shape("B", x=300, y=0)
    cid = d.add_connection(a, b, auto_route=False)
    xml = d.to_drawio_xml()

    updated = update_cell_in_xml(xml, cid, waypoints=[[100, 50], [200, 50]])
    edge = next(c for c in get_cells_from_xml(updated) if c["id"] == cid)
    assert edge["waypoints"] == [["100", "50"], ["200", "50"]]


def test_update_cell_replaces_existing_waypoints():
    d = Diagram()
    a = d.add_shape("A", x=0, y=0)
    b = d.add_shape("B", x=300, y=0)
    cid = d.add_connection(a, b, waypoints=[(50, 10), (250, 10)], auto_route=False)
    xml = d.to_drawio_xml()

    updated = update_cell_in_xml(xml, cid, waypoints=[[150, 100]])
    edge = next(c for c in get_cells_from_xml(updated) if c["id"] == cid)
    assert edge["waypoints"] == [["150", "100"]]


def test_update_cell_clears_waypoints_with_empty_list():
    d = Diagram()
    a = d.add_shape("A", x=0, y=0)
    b = d.add_shape("B", x=300, y=0)
    cid = d.add_connection(a, b, waypoints=[(50, 10)], auto_route=False)
    xml = d.to_drawio_xml()

    updated = update_cell_in_xml(xml, cid, waypoints=[])
    edge = next(c for c in get_cells_from_xml(updated) if c["id"] == cid)
    assert edge.get("waypoints", []) == []


def test_update_cell_sets_entry_exit_anchors():
    d = Diagram()
    a = d.add_shape("A", x=0, y=0)
    b = d.add_shape("B", x=300, y=0)
    cid = d.add_connection(a, b, auto_route=False)
    xml = d.to_drawio_xml()

    updated = update_cell_in_xml(
        xml, cid, entry_x=0.0, entry_y=0.5, exit_x=1.0, exit_y=0.5,
    )
    edge = next(c for c in get_cells_from_xml(updated) if c["id"] == cid)
    assert edge["entry_x"] == "0.0"
    assert edge["entry_y"] == "0.5"
    assert edge["exit_x"] == "1.0"
    assert edge["exit_y"] == "0.5"


def test_update_cell_sets_label_offset():
    d = Diagram()
    a = d.add_shape("A", x=0, y=0)
    b = d.add_shape("B", x=300, y=0)
    cid = d.add_connection(a, b, label="hello", auto_route=False)
    xml = d.to_drawio_xml()

    updated = update_cell_in_xml(xml, cid, label_offset_x=25.0, label_offset_y=-10.0)
    edge = next(c for c in get_cells_from_xml(updated) if c["id"] == cid)
    assert edge["label_offset_x"] == 25.0
    assert edge["label_offset_y"] == -10.0
