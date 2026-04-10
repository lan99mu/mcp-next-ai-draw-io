#!/usr/bin/env python3
"""
Test the resources feature for on-demand documentation
"""

import pytest
from mcp_drawio_server.resources import get_resource_definitions, get_resource_content


@pytest.mark.asyncio
async def test_list_resources():
    """Test listing all available resources"""
    resources = get_resource_definitions()

    expected_uris = [
        "docs://tools/overview",
        "docs://bindings/guide",
        "docs://workflows/best-practices",
        "docs://shapes/reference"
    ]

    resource_uris = [str(r.uri) for r in resources]
    for expected in expected_uris:
        assert expected in resource_uris, f"Missing resource: {expected}"


@pytest.mark.asyncio
async def test_read_resource():
    """Test reading specific resources"""
    test_cases = [
        ("docs://tools/overview", "Tool Reference"),
        ("docs://bindings/guide", "Node Bindings Guide"),
        ("docs://workflows/best-practices", "Workflow Best Practices"),
        ("docs://shapes/reference", "Shape Types Reference"),
    ]

    for uri, expected_title in test_cases:
        result = get_resource_content(uri)

        assert result.contents, f"Missing contents for {uri}"
        assert len(result.contents) > 0, f"No contents in {uri}"

        content = result.contents[0]
        assert content.text, f"Missing text content for {uri}"
        assert len(content.text) > 100, f"Content too short for {uri}"
        assert expected_title in content.text, f"Missing title '{expected_title}' in {uri}"


@pytest.mark.asyncio
async def test_resource_content_quality():
    """Test that resources contain expected information"""
    # Check tools overview
    result = get_resource_content("docs://tools/overview")
    content = result.contents[0].text
    assert "## File Operations" in content
    assert "## Inspection" in content
    assert "## Binding & Layout" in content
    assert "bind_nodes" in content

    # Check bindings guide
    result = get_resource_content("docs://bindings/guide")
    content = result.contents[0].text
    assert "Workflow" in content
    assert "bind_nodes" in content

    # Check best practices
    result = get_resource_content("docs://workflows/best-practices")
    content = result.contents[0].text
    assert "Bind early" in content or "bind early" in content or "Progressive" in content

    # Check shapes reference
    result = get_resource_content("docs://shapes/reference")
    content = result.contents[0].text
    assert "rectangle" in content
    assert "uml_class" in content
    assert "activity_start" in content
