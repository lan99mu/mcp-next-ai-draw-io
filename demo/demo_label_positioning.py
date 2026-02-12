#!/usr/bin/env python3
"""
Demonstration of Connection Label Positioning Features

This script shows how to use the new label positioning features
when creating diagrams with the MCP Draw.io server.
"""

from mcp_drawio_server import Diagram
import tempfile
from pathlib import Path


def demo_label_positioning():
    """Create a comprehensive demo showing all label positioning features"""
    
    print("=" * 70)
    print("Connection Label Positioning - Feature Demo")
    print("=" * 70)
    print()
    
    # Create a new diagram
    diagram = Diagram(name="Label Positioning Demo")
    
    # Create nodes for the demo
    print("Creating diagram nodes...")
    node_a = diagram.add_shape("Node A", x=100, y=100, width=100, height=60)
    node_b = diagram.add_shape("Node B", x=350, y=100, width=100, height=60)
    node_c = diagram.add_shape("Node C", x=100, y=250, width=100, height=60)
    node_d = diagram.add_shape("Node D", x=350, y=250, width=100, height=60)
    node_e = diagram.add_shape("Center", x=225, y=400, width=100, height=60)
    
    print(f"✓ Created {len(diagram.shapes)} nodes")
    print()
    
    # Demo 1: Basic label positioning
    print("1. Basic Label Position (left, right, center):")
    conn1 = diagram.add_connection(
        node_a, node_b,
        label="Left Aligned",
        label_position="left"
    )
    print("   ✓ Left-aligned label")
    
    conn2 = diagram.add_connection(
        node_b, node_d,
        label="Right Aligned", 
        label_position="right"
    )
    print("   ✓ Right-aligned label")
    
    conn3 = diagram.add_connection(
        node_d, node_c,
        label="Centered",
        label_position="center"
    )
    print("   ✓ Center-aligned label")
    print()
    
    # Demo 2: Label offsets
    print("2. Custom Label Offsets:")
    conn4 = diagram.add_connection(
        node_a, node_c,
        label="Offset Right",
        label_offset_x=30,
        label_offset_y=0
    )
    print("   ✓ Label offset 30px to the right")
    
    conn5 = diagram.add_connection(
        node_c, node_a,
        label="Offset Up",
        label_offset_x=0,
        label_offset_y=-20
    )
    print("   ✓ Label offset 20px upward")
    print()
    
    # Demo 3: Background colors
    print("3. Label Background Colors:")
    conn6 = diagram.add_connection(
        node_a, node_e,
        label="Yellow BG",
        label_background_color="#ffeb3b"
    )
    print("   ✓ Yellow background (#ffeb3b)")
    
    conn7 = diagram.add_connection(
        node_b, node_e,
        label="Blue BG",
        label_background_color="#e3f2fd"
    )
    print("   ✓ Light blue background (#e3f2fd)")
    print()
    
    # Demo 4: Combined features
    print("4. Combining All Features:")
    conn8 = diagram.add_connection(
        node_d, node_e,
        label="Full Custom",
        label_position="right",
        label_offset_x=-10,
        label_offset_y=15,
        label_background_color="#c8e6c9"
    )
    print("   ✓ Right-aligned + offset + green background")
    print()
    
    # Demo 5: Default (no customization)
    print("5. Default Behavior (backward compatibility):")
    conn9 = diagram.add_connection(
        node_c, node_e,
        label="Standard"
    )
    print("   ✓ Standard connection (no positioning parameters)")
    print()
    
    # Save the diagram
    xml = diagram.to_drawio_xml()
    tmp_dir = Path(tempfile.gettempdir())
    filepath = tmp_dir / "label_positioning_demo.drawio"
    filepath.write_text(xml, encoding='utf-8')
    
    print("=" * 70)
    print(f"✓ Demo diagram created with {len(diagram.connections)} connections")
    print(f"✓ Saved to: {filepath}")
    print("=" * 70)
    print()
    print("You can open this file in:")
    print("  • Draw.io Desktop (https://github.com/jgraph/drawio-desktop/releases)")
    print("  • Draw.io Web (https://app.diagrams.net/)")
    print("  • VS Code with Draw.io Integration extension")
    print()
    print("Features demonstrated:")
    print("  ✓ Label position (left, right, center)")
    print("  ✓ Label offset (x and y coordinates)")
    print("  ✓ Label background color")
    print("  ✓ Combining multiple features")
    print("  ✓ Backward compatibility (default behavior)")
    print()
    
    return filepath


if __name__ == "__main__":
    try:
        demo_label_positioning()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
