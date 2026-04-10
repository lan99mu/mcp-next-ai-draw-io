#!/usr/bin/env python3
"""Tests for MCP tool definitions."""

from mcp_drawio_server.tools import get_tool_definitions


def test_add_shape_tool_documents_html_uml_labels():
    """The add_shape tool should instruct the model to use HTML labels."""
    tools = {tool.name: tool for tool in get_tool_definitions()}

    add_shape = tools["add_shape"]
    add_connection = tools["add_connection"]
    update_cell = tools["update_cell"]
    label_description = add_shape.inputSchema["properties"]["label"]["description"]
    connection_label_description = add_connection.inputSchema["properties"]["label"]["description"]
    update_value_description = update_cell.inputSchema["properties"]["value"]["description"]

    # add_shape label should mention HTML and UML format
    assert "HTML" in label_description or "<br>" in label_description
    assert "UML" in label_description or "uml" in label_description.lower()

    # add_connection label should mention HTML
    assert "HTML" in connection_label_description or "<br>" in connection_label_description

    # update_cell value should mention HTML
    assert "HTML" in update_value_description or "label" in update_value_description.lower()
