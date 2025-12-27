#!/usr/bin/env python3
"""
Test script for connection label positioning features
"""

import tempfile
from pathlib import Path
from mcp_drawio_server import Diagram


def test_basic_label_positioning():
    """Test basic label position options (left, right, center)"""
    print("Testing basic label positioning...")
    
    diagram = Diagram(name="Label Position Test")
    
    # Create shapes
    shape1 = diagram.add_shape("Source", x=100, y=100, width=100, height=60)
    shape2 = diagram.add_shape("Target", x=400, y=100, width=100, height=60)
    shape3 = diagram.add_shape("Bottom", x=250, y=250, width=100, height=60)
    
    # Add connections with different label positions
    conn1 = diagram.add_connection(
        shape1, shape2, 
        label="Left Label",
        label_position="left"
    )
    
    conn2 = diagram.add_connection(
        shape2, shape3,
        label="Right Label", 
        label_position="right"
    )
    
    conn3 = diagram.add_connection(
        shape3, shape1,
        label="Center Label",
        label_position="center"
    )
    
    xml = diagram.to_drawio_xml()
    
    # Verify label positions are in the XML
    assert "labelPosition=left" in xml, "Left label position not found"
    assert "labelPosition=right" in xml, "Right label position not found"
    assert "labelPosition=center" in xml, "Center label position not found"
    
    print("✓ Basic label positioning works correctly")
    print(f"✓ Created {len(diagram.connections)} connections with different label positions")
    
    return xml


def test_label_offset():
    """Test label offset positioning"""
    print("\nTesting label offset positioning...")
    
    diagram = Diagram(name="Label Offset Test")
    
    # Create shapes
    shape1 = diagram.add_shape("A", x=100, y=100, width=80, height=60)
    shape2 = diagram.add_shape("B", x=300, y=100, width=80, height=60)
    shape3 = diagram.add_shape("C", x=100, y=250, width=80, height=60)
    shape4 = diagram.add_shape("D", x=300, y=250, width=80, height=60)
    
    # Add connections with label offsets
    conn1 = diagram.add_connection(
        shape1, shape2,
        label="Offset +20, +10",
        label_offset_x=20,
        label_offset_y=10
    )
    
    conn2 = diagram.add_connection(
        shape2, shape4,
        label="Offset -15, +5",
        label_offset_x=-15,
        label_offset_y=5
    )
    
    conn3 = diagram.add_connection(
        shape4, shape3,
        label="Offset 0, -20",
        label_offset_x=0,
        label_offset_y=-20
    )
    
    xml = diagram.to_drawio_xml()
    
    # Verify offsets are in the XML (allow for decimal notation)
    assert 'x="20' in xml, "X offset 20 not found"
    assert 'y="10' in xml, "Y offset 10 not found"
    assert 'x="-15' in xml, "X offset -15 not found"
    assert 'y="-20' in xml, "Y offset -20 not found"
    assert 'as="offset"' in xml, "Offset geometry not found"
    
    print("✓ Label offset positioning works correctly")
    print(f"✓ Created {len(diagram.connections)} connections with custom offsets")
    
    return xml


def test_label_background_color():
    """Test label background color"""
    print("\nTesting label background color...")
    
    diagram = Diagram(name="Label Background Test")
    
    # Create shapes
    shape1 = diagram.add_shape("Start", x=150, y=100, width=100, height=60)
    shape2 = diagram.add_shape("End", x=150, y=250, width=100, height=60)
    
    # Add connections with background colors
    conn1 = diagram.add_connection(
        shape1, shape2,
        label="White Background",
        label_background_color="#ffffff"
    )
    
    xml = diagram.to_drawio_xml()
    
    # Verify background color is in the XML
    assert "labelBackgroundColor=#ffffff" in xml, "Label background color not found"
    
    print("✓ Label background color works correctly")
    
    return xml


def test_combined_label_features():
    """Test combining multiple label positioning features"""
    print("\nTesting combined label features...")
    
    diagram = Diagram(name="Combined Label Features Test")
    
    # Create shapes
    shape1 = diagram.add_shape("Source", x=100, y=150, width=120, height=60)
    shape2 = diagram.add_shape("Target", x=400, y=150, width=120, height=60)
    
    # Add connection with all label features combined
    conn = diagram.add_connection(
        shape1, shape2,
        label="Fully Customized Label",
        label_position="center",
        label_offset_x=10,
        label_offset_y=-15,
        label_background_color="#e1f5fe"
    )
    
    xml = diagram.to_drawio_xml()
    
    # Verify all features are present (allow for decimal notation)
    assert "labelPosition=center" in xml, "Label position not found"
    assert 'x="10' in xml, "X offset not found"
    assert 'y="-15' in xml, "Y offset not found"
    assert "labelBackgroundColor=#e1f5fe" in xml, "Background color not found"
    assert 'as="offset"' in xml, "Offset geometry not found"
    
    print("✓ Combined label features work correctly")
    print("✓ All label positioning features can be used together")
    
    return xml


def test_backward_compatibility():
    """Test that connections without label positioning still work"""
    print("\nTesting backward compatibility...")
    
    diagram = Diagram(name="Backward Compatibility Test")
    
    # Create shapes
    shape1 = diagram.add_shape("A", x=100, y=100, width=80, height=60)
    shape2 = diagram.add_shape("B", x=250, y=100, width=80, height=60)
    
    # Add connection without any label positioning (old behavior)
    conn = diagram.add_connection(shape1, shape2, label="Standard Connection")
    
    xml = diagram.to_drawio_xml()
    
    # Should not have label positioning attributes
    # But should still have the label
    assert "Standard Connection" in xml, "Connection label not found"
    assert xml.count("labelPosition") == 0, "Should not have labelPosition when not specified"
    assert xml.count("labelBackgroundColor") == 0, "Should not have labelBackgroundColor when not specified"
    
    # Should have standard geometry (no offset)
    lines = xml.split('\n')
    for i, line in enumerate(lines):
        if 'Standard Connection' in line and 'edge=' in line:
            # Next line should be simple geometry (check bounds first)
            if i + 1 < len(lines):
                assert 'relative="1"' in lines[i+1], "Should have relative geometry"
            break
    
    print("✓ Backward compatibility maintained")
    print("✓ Connections without label positioning work as before")
    
    return xml


def save_diagram_to_file(xml_content, filename):
    """Save diagram XML to a file"""
    tmp_dir = Path(tempfile.gettempdir())
    filepath = tmp_dir / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(xml_content)
    print(f"  → Saved to: {filepath}")
    return filepath


if __name__ == "__main__":
    print("=" * 70)
    print("Connection Label Positioning Tests")
    print("=" * 70)
    
    try:
        # Test 1: Basic label positioning
        xml1 = test_basic_label_positioning()
        save_diagram_to_file(xml1, "test_label_position.drawio")
        
        # Test 2: Label offset
        xml2 = test_label_offset()
        save_diagram_to_file(xml2, "test_label_offset.drawio")
        
        # Test 3: Label background color
        xml3 = test_label_background_color()
        save_diagram_to_file(xml3, "test_label_background.drawio")
        
        # Test 4: Combined features
        xml4 = test_combined_label_features()
        save_diagram_to_file(xml4, "test_label_combined.drawio")
        
        # Test 5: Backward compatibility
        xml5 = test_backward_compatibility()
        save_diagram_to_file(xml5, "test_backward_compat.drawio")
        
        print("\n" + "=" * 70)
        print("✓ All label positioning tests passed!")
        print("=" * 70)
        print("\nNew features available:")
        print("  • label_position: 'left', 'right', or 'center'")
        print("  • label_offset_x: horizontal offset in pixels")
        print("  • label_offset_y: vertical offset in pixels")
        print("  • label_background_color: hex color code or 'none'")
        print("\nGenerated .drawio files can be opened in Draw.io to verify visual results.")
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
