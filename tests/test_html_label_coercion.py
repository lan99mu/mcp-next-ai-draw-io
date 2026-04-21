#!/usr/bin/env python3
"""Tests for HTML-style label coercion.

Labels emitted by the server must always use HTML (``<br>``) line breaks
because Draw.io renders them with ``html=1``.  The helpers under test accept
plain-text, GraphViz/DOT-style, and already-HTML labels and normalise them
into a single consistent representation.
"""

from mcp_drawio_server.diagram import Diagram, coerce_html_label
from mcp_drawio_server.xml_operations import (
    _format_html_value,
    update_cell_in_xml,
)


def test_coerce_handles_plain_newlines():
    assert coerce_html_label("a\nb") == "a<br>b"
    assert coerce_html_label("a\r\nb") == "a<br>b"
    assert coerce_html_label("a\rb") == "a<br>b"


def test_coerce_handles_graphviz_escapes():
    # Literal backslash-l / backslash-n (as they appear in GraphViz / DOT input)
    assert coerce_html_label("a\\lb") == "a<br>b"
    assert coerce_html_label("a\\nb") == "a<br>b"


def test_coerce_preserves_existing_html():
    assert coerce_html_label("a<br>b") == "a<br>b"
    assert coerce_html_label("") == ""


def test_format_html_value_matches_coerce():
    """``xml_operations._format_html_value`` should use the same rules."""
    assert _format_html_value("a\nb") == coerce_html_label("a\nb")
    assert _format_html_value("a\\lb") == coerce_html_label("a\\lb")


def test_add_shape_emits_html_labels():
    """Labels passed as plain text end up as escaped HTML in the XML."""
    diagram = Diagram(name="HTML Test")
    diagram.add_shape("line1\nline2", x=0, y=0)
    xml = diagram.to_drawio_xml()
    # The label's ``<br>`` is XML-escaped in the attribute value.
    assert "line1&lt;br&gt;line2" in xml


def test_update_cell_coerces_non_html_input():
    diagram = Diagram(name="Update Test")
    shape_id = diagram.add_shape("original", x=0, y=0)
    xml = diagram.to_drawio_xml()

    new_xml = update_cell_in_xml(xml, shape_id, value="one\ntwo\\lthree")
    # ``setAttribute`` XML-escapes ``<br>`` as ``&lt;br&gt;``.
    assert "one&lt;br&gt;two&lt;br&gt;three" in new_xml
