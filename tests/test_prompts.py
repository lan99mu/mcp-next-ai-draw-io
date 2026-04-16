#!/usr/bin/env python3
"""
Test the prompts feature implementation
"""

import asyncio
import pytest
from mcp_drawio_server.prompts import get_prompt_definitions, get_prompt_result


@pytest.mark.asyncio
async def test_list_prompts():
    """Test listing all available prompts"""
    prompts = get_prompt_definitions()

    expected_prompts = [
        "plan_diagram",
        "draw_diagram",
        "review_diagram",
    ]

    prompt_names = [p.name for p in prompts]
    for expected in expected_prompts:
        assert expected in prompt_names, f"Missing prompt: {expected}"


@pytest.mark.asyncio
async def test_get_prompt():
    """Test getting a specific prompt"""
    test_cases = [
        ("plan_diagram", {"description": "user authentication flow"}),
        ("draw_diagram", {"plan": "NODES:\n  1. Start  ellipse  x=0 y=0 80x80"}),
        ("review_diagram", {}),
    ]

    for prompt_name, args in test_cases:
        result = get_prompt_result(prompt_name, args)

        assert result.description, f"Missing description for {prompt_name}"
        assert result.messages, f"Missing messages for {prompt_name}"
        assert len(result.messages) > 0, f"No messages in {prompt_name}"

        msg = result.messages[0]
        assert msg.role == "user", f"Wrong role for {prompt_name}"
        assert msg.content.text, f"Missing text content for {prompt_name}"
        assert len(msg.content.text) > 100, f"Content too short for {prompt_name}"


@pytest.mark.asyncio
async def test_prompt_content_quality():
    """Test that prompts contain useful progressive guidance"""
    # plan_diagram should mention structure planning
    result = get_prompt_result("plan_diagram", {"description": "test"})
    content = result.messages[0].content.text.lower()
    assert "node" in content or "shape" in content
    assert "connection" in content

    # draw_diagram should mention tool calls
    result = get_prompt_result("draw_diagram", {"plan": "dummy plan"})
    content = result.messages[0].content.text.lower()
    assert "add_shape" in content or "create" in content
    assert "bind" in content

    # review_diagram should mention optimization
    result = get_prompt_result("review_diagram", {})
    content = result.messages[0].content.text.lower()
    assert "detect" in content or "crossing" in content
    assert "bind" in content


@pytest.mark.asyncio
async def test_uml_complex_layout_guidance_in_prompts():
    """Ensure prompts include complex UML class diagram overlap-prevention guidance."""
    plan_result = get_prompt_result(
        "plan_diagram",
        {"description": "complex domain model", "diagram_type": "uml_class"},
    )
    plan_content = plan_result.messages[0].content.text.lower()
    assert "container" in plan_content
    assert "parent_id" in plan_content
    assert "overlap" in plan_content

    review_result = get_prompt_result("review_diagram", {})
    review_content = review_result.messages[0].content.text.lower()
    assert "domain containers" in review_content
    assert "fully inside" in review_content
    assert "must not overlap" in review_content
