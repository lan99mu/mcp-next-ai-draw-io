#!/usr/bin/env python3
"""
MCP Resources for Draw.io Server.

This module contains resource definitions and handlers for on-demand documentation.
Documentation content is stored in docs_content.py.
"""

from mcp.types import Resource, TextResourceContents, ReadResourceResult

from .docs_content import (
    get_tools_overview_content,
    get_bindings_guide_content,
    get_workflows_content,
    get_shapes_reference_content,
)


def get_resource_definitions() -> list[Resource]:
    """Return all available resource definitions."""
    return [
        Resource(
            uri="docs://tools/overview",
            name="Tool Documentation",
            description="Detailed documentation for all available tools",
            mimeType="text/markdown"
        ),
        Resource(
            uri="docs://bindings/guide",
            name="Node Bindings Guide",
            description="Complete guide to using node bindings for efficient diagram editing",
            mimeType="text/markdown"
        ),
        Resource(
            uri="docs://workflows/best-practices",
            name="Workflow Best Practices",
            description="Best practices and efficiency patterns for diagram workflows",
            mimeType="text/markdown"
        ),
        Resource(
            uri="docs://shapes/reference",
            name="Shape Types Reference",
            description="Complete reference of all available shape types",
            mimeType="text/markdown"
        )
    ]


def get_resource_content(uri: str) -> ReadResourceResult:
    """Read detailed documentation resource content."""
    
    if uri == "docs://tools/overview":
        content = get_tools_overview_content()
    elif uri == "docs://bindings/guide":
        content = get_bindings_guide_content()
    elif uri == "docs://workflows/best-practices":
        content = get_workflows_content()
    elif uri == "docs://shapes/reference":
        content = get_shapes_reference_content()
    else:
        content = f"Resource not found: {uri}"
        return ReadResourceResult(
            contents=[TextResourceContents(
                uri=uri,
                mimeType="text/plain",
                text=content
            )]
        )
    
    return ReadResourceResult(
        contents=[TextResourceContents(
            uri=uri,
            mimeType="text/markdown",
            text=content
        )]
    )
