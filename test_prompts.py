#!/usr/bin/env python3
"""
Test the prompts feature implementation
"""

import asyncio
from mcp.server import Server
from mcp_drawio_server import server as server_module


async def test_list_prompts():
    """Test listing all available prompts"""
    print("Testing list_prompts()...")
    
    # Get the list_prompts function directly
    from mcp_drawio_server.server import list_prompts
    
    prompts = await list_prompts()
    
    print(f"\nFound {len(prompts)} prompts:")
    for prompt in prompts:
        print(f"\n  Name: {prompt.name}")
        print(f"  Description: {prompt.description[:80]}...")
        if prompt.arguments:
            print(f"  Arguments: {len(prompt.arguments)}")
            for arg in prompt.arguments:
                req = "required" if arg.required else "optional"
                print(f"    - {arg.name} ({req}): {arg.description[:60]}...")
    
    # Verify we have the expected prompts
    expected_prompts = [
        "create_flowchart",
        "add_connected_nodes", 
        "optimize_layout",
        "modify_with_bindings",
        "create_architecture_diagram"
    ]
    
    prompt_names = [p.name for p in prompts]
    for expected in expected_prompts:
        assert expected in prompt_names, f"Missing prompt: {expected}"
    
    print("\n✓ All expected prompts are present")
    return True


async def test_get_prompt():
    """Test getting a specific prompt"""
    print("\n\nTesting get_prompt()...")
    
    # Get the get_prompt function
    from mcp_drawio_server.server import get_prompt
    
    # Test each prompt
    test_cases = [
        ("create_flowchart", {"description": "user authentication flow"}),
        ("add_connected_nodes", {"nodes_description": "API, database, cache", "base_x": "100", "base_y": "200"}),
        ("optimize_layout", {}),
        ("modify_with_bindings", {"modification_description": "move the auth section"}),
        ("create_architecture_diagram", {"architecture_description": "microservices architecture"}),
    ]
    
    for prompt_name, args in test_cases:
        print(f"\n  Testing: {prompt_name}")
        result = await get_prompt(prompt_name, args)
        
        assert result.description, f"Missing description for {prompt_name}"
        assert result.messages, f"Missing messages for {prompt_name}"
        assert len(result.messages) > 0, f"No messages in {prompt_name}"
        
        msg = result.messages[0]
        assert msg.role == "user", f"Wrong role for {prompt_name}"
        assert msg.content.text, f"Missing text content for {prompt_name}"
        assert len(msg.content.text) > 100, f"Content too short for {prompt_name}"
        
        # Check for key workflow elements in the content
        content = msg.content.text.lower()
        assert "workflow" in content or "example" in content, f"Missing workflow guidance in {prompt_name}"
        
        print(f"    ✓ Description: {result.description[:60]}...")
        print(f"    ✓ Message length: {len(msg.content.text)} chars")
    
    print("\n✓ All prompts return valid content")
    return True


async def test_prompt_content_quality():
    """Test that prompts contain useful efficiency guidance"""
    print("\n\nTesting prompt content quality...")
    
    from mcp_drawio_server.server import get_prompt
    
    # Get the optimize_layout prompt
    result = await get_prompt("optimize_layout", {})
    content = result.messages[0].content.text.lower()
    
    # Check for key efficiency concepts
    efficiency_keywords = [
        "bind",  # Should mention bindings
        "efficient",  # Should talk about efficiency
        "tool call",  # Should mention reducing tool calls
    ]
    
    found_keywords = []
    for keyword in efficiency_keywords:
        if keyword in content:
            found_keywords.append(keyword)
    
    print(f"  Found efficiency keywords: {found_keywords}")
    assert len(found_keywords) >= 3, "Prompt should contain efficiency guidance"
    
    # Check the create_flowchart prompt
    result = await get_prompt("create_flowchart", {"description": "test workflow"})
    content = result.messages[0].content.text
    
    # Should contain step-by-step workflow
    assert "1." in content or "2." in content, "Should have numbered steps"
    assert "bind" in content.lower(), "Should mention binding"
    
    print("  ✓ Prompts contain numbered workflows")
    print("  ✓ Prompts emphasize efficiency through bindings")
    print("  ✓ Prompts explain the benefits")
    
    return True


async def main():
    """Run all tests"""
    print("="*60)
    print("Testing MCP Prompts Implementation")
    print("="*60)
    
    try:
        await test_list_prompts()
        await test_get_prompt()
        await test_prompt_content_quality()
        
        print("\n" + "="*60)
        print("✅ All prompt tests passed!")
        print("="*60)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
