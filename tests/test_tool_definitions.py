#!/usr/bin/env python3
"""Tests for MCP tool definitions."""

from mcp_drawio_server.tools import get_tool_definitions


def test_add_shape_tool_documents_html_uml_labels():
    """The add_shape tool should instruct the model to use HTML UML labels."""
    tools = {tool.name: tool for tool in get_tool_definitions()}

    add_shape = tools["add_shape"]
    label_description = add_shape.inputSchema["properties"]["label"]["description"]
    shape_type_description = add_shape.inputSchema["properties"]["shape_type"]["description"]

    assert "HTML text with <br> line breaks" in label_description
    assert "plain uml_class label still creates empty attributes and methods compartments" in label_description
    assert "uml_class creates a three-compartment class box" in shape_type_description
