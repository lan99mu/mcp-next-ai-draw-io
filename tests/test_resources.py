#!/usr/bin/env python3
"""
Test the resources feature for on-demand documentation
"""

import asyncio
import pytest
from mcp_drawio_server.resources import get_resource_definitions, get_resource_content


@pytest.mark.asyncio
async def test_list_resources():
    """Test listing all available resources"""
    print("Testing list_resources()...")
    
    resources = get_resource_definitions()
    
    print(f"\nFound {len(resources)} documentation resources:")
    for resource in resources:
        print(f"\n  URI: {resource.uri}")
        print(f"  Name: {resource.name}")
        print(f"  Description: {resource.description}")
        print(f"  MIME Type: {resource.mimeType}")
    
    # Verify we have the expected resources
    expected_uris = [
        "docs://tools/overview",
        "docs://bindings/guide",
        "docs://workflows/best-practices",
        "docs://shapes/reference"
    ]
    
    resource_uris = [str(r.uri) for r in resources]
    for expected in expected_uris:
        assert expected in resource_uris, f"Missing resource: {expected}"
    
    print("\n✓ All expected resources are present")
    return True


@pytest.mark.asyncio
async def test_read_resource():
    """Test reading specific resources"""
    print("\n\nTesting read_resource()...")
    
    test_cases = [
        ("docs://tools/overview", "Tool Documentation"),
        ("docs://bindings/guide", "Node Bindings Guide"),
        ("docs://workflows/best-practices", "Workflow Best Practices"),
        ("docs://shapes/reference", "Shape Types Reference"),
    ]
    
    for uri, expected_title in test_cases:
        print(f"\n  Testing: {uri}")
        result = get_resource_content(uri)
        
        assert result.contents, f"Missing contents for {uri}"
        assert len(result.contents) > 0, f"No contents in {uri}"
        
        content = result.contents[0]
        assert content.text, f"Missing text content for {uri}"
        assert len(content.text) > 200, f"Content too short for {uri}"
        assert expected_title in content.text, f"Missing title '{expected_title}' in {uri}"
        
        print(f"    ✓ Content length: {len(content.text)} chars")
        print(f"    ✓ Contains expected title: {expected_title}")
    
    print("\n✓ All resources return valid content")
    return True


@pytest.mark.asyncio
async def test_resource_content_quality():
    """Test that resources contain detailed information"""
    print("\n\nTesting resource content quality...")
    
    # Check tools overview
    result = get_resource_content("docs://tools/overview")
    content = result.contents[0].text
    
    # Should contain sections for different tool categories
    assert "## File Operations" in content
    assert "## Inspection Tools" in content
    assert "## Node Binding Tools" in content
    assert "bind_nodes" in content
    
    print("  ✓ Tools overview contains expected sections")
    
    # Check bindings guide
    result = get_resource_content("docs://bindings/guide")
    content = result.contents[0].text
    
    # Should contain efficiency examples
    assert "Without Bindings" in content
    assert "With Bindings" in content
    assert "%" in content  # Should have percentage savings
    
    print("  ✓ Bindings guide contains efficiency examples")
    
    # Check best practices
    result = get_resource_content("docs://workflows/best-practices")
    content = result.contents[0].text
    
    # Should contain workflow patterns
    assert "Bind Early" in content
    assert "Tool Call Reduction" in content
    
    print("  ✓ Best practices contains workflow patterns")
    
    # Check shapes reference
    result = get_resource_content("docs://shapes/reference")
    content = result.contents[0].text
    
    # Should contain shape type documentation
    assert "rectangle" in content
    assert "uml_class" in content
    assert "activity_start" in content
    
    print("  ✓ Shapes reference contains shape documentation")
    
    return True


@pytest.mark.asyncio
async def test_context_savings():
    """Calculate and display context savings"""
    print("\n\nCalculating context savings...")
    
    # Original tool descriptions total: 2669 chars
    # New tool descriptions total: 1010 chars
    # Savings: 1659 chars (62.2%)
    
    original = 2669
    new = 1010
    savings = original - new
    percent = (savings / original) * 100
    
    print(f"  Original description length: {original} chars")
    print(f"  New description length: {new} chars")
    print(f"  Savings: {savings} chars ({percent:.1f}%)")
    print(f"\n  → Initial context consumption reduced by {percent:.1f}%")
    print(f"  → Detailed docs available on-demand via resources")
    
    # Count resource content
    total_resource_chars = 0
    for uri in ["docs://tools/overview", "docs://bindings/guide", 
                "docs://workflows/best-practices", "docs://shapes/reference"]:
        result = get_resource_content(uri)
        total_resource_chars += len(result.contents[0].text)
    
    print(f"\n  Total resource documentation: {total_resource_chars} chars")
    print(f"  → Available only when explicitly requested")
    
    return True


async def main():
    """Run all tests"""
    print("="*60)
    print("Testing MCP Resources Implementation")
    print("="*60)
    
    try:
        await test_list_resources()
        await test_read_resource()
        await test_resource_content_quality()
        await test_context_savings()
        
        print("\n" + "="*60)
        print("✅ All resource tests passed!")
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
