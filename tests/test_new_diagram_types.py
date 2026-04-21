#!/usr/bin/env python3
"""Tests for newly supported diagram types (sequence, component, etc.)."""

from mcp_drawio_server.diagram import Diagram
from mcp_drawio_server.tools import get_tool_definitions


def _add_shape_enum() -> list[str]:
    for tool in get_tool_definitions():
        if tool.name == "add_shape":
            return tool.inputSchema["properties"]["shape_type"]["enum"]
    raise AssertionError("add_shape tool not found")


def test_new_shape_types_exposed_in_tool_schema():
    enum = _add_shape_enum()
    for shape_type in ("actor", "lifeline", "uml_frame", "component"):
        assert shape_type in enum, f"{shape_type!r} should be in add_shape enum"


def test_new_shape_types_emit_expected_drawio_styles():
    """Each new shape must render to a recognisable Draw.io style string."""
    diagram = Diagram(name="Sequence/Component Types")
    diagram.add_shape("User", shape_type="actor")
    diagram.add_shape("OrderService", shape_type="lifeline", height=400)
    diagram.add_shape("alt", shape_type="uml_frame")
    diagram.add_shape("InventoryModule", shape_type="component")

    xml = diagram.to_drawio_xml()

    assert "shape=umlActor" in xml
    assert "shape=umlLifeline" in xml
    assert "shape=umlFrame" in xml
    # component style begins with ``shape=component``
    assert "shape=component" in xml


def test_sequence_diagram_round_trip():
    """Build a tiny sequence diagram and confirm it round-trips through XML."""
    from mcp_drawio_server.xml_operations import get_cells_from_xml

    diagram = Diagram(name="Sequence")
    actor = diagram.add_shape("User", shape_type="actor", x=0, y=0, width=40, height=60)
    ls_web = diagram.add_shape("Web", shape_type="lifeline", x=100, y=0, width=120, height=400)
    ls_api = diagram.add_shape("API", shape_type="lifeline", x=280, y=0, width=120, height=400)

    msg_req = diagram.add_connection(actor, ls_web, label="open page", edge_style="straight")
    msg_call = diagram.add_connection(ls_web, ls_api, label="fetch /orders", edge_style="straight")
    msg_ret = diagram.add_connection(
        ls_api, ls_web, label="200 OK", edge_style="straight", dashed=True
    )

    cells = get_cells_from_xml(diagram.to_drawio_xml())
    labels = {c["value"] for c in cells if c["edge"]}
    assert "open page" in labels
    assert "fetch /orders" in labels
    assert "200 OK" in labels

    # The dashed return message must serialise ``dashed=1`` into the edge style.
    ret_edge = next(c for c in cells if c["value"] == "200 OK")
    assert "dashed=1" in ret_edge["style"]
