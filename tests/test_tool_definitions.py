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
    shape_type_description = add_shape.inputSchema["properties"]["shape_type"]["description"]
    connection_label_description = add_connection.inputSchema["properties"]["label"]["description"]
    update_value_description = update_cell.inputSchema["properties"]["value"]["description"]

    assert "HTML text with <br> line breaks" in label_description
    assert "All labels are handled as HTML text" in label_description
    assert "plain uml_class label still creates empty attributes and methods compartments" in label_description
    assert "uml_class creates a three-compartment class box" in shape_type_description
    assert "Connection labels are handled as HTML text" in connection_label_description
    assert "Values are handled as HTML text" in update_value_description
