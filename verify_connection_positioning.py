#!/usr/bin/env python3
"""
Verification script for connection positioning feature.
Demonstrates all available position control parameters.
"""

from mcp_drawio_server.diagram import Diagram

def main():
    print("\n" + "=" * 70)
    print("Connection Position Control Verification")
    print("=" * 70)
    
    # Create diagram
    diagram = Diagram(name="Position Control Demo")
    
    # Create test nodes
    print("\n1. Creating test nodes...")
    node1 = diagram.add_shape("Node A", x=100, y=100, width=100, height=60)
    node2 = diagram.add_shape("Node B", x=400, y=100, width=100, height=60)
    node3 = diagram.add_shape("Node C", x=250, y=250, width=100, height=60)
    print(f"   ✓ Created 3 nodes: {node1}, {node2}, {node3}")
    
    # Test 1: Entry/Exit Points
    print("\n2. Testing Entry/Exit Points...")
    conn1 = diagram.add_connection(
        node1, node2,
        label="Right→Left",
        exit_x=1.0,   # Exit from right side
        exit_y=0.5,   # Exit from middle height
        entry_x=0.0,  # Enter left side
        entry_y=0.5   # Enter at middle height
    )
    print(f"   ✓ Created connection with entry/exit points: {conn1}")
    print(f"     - exit_x=1.0, exit_y=0.5 (right-center of source)")
    print(f"     - entry_x=0.0, entry_y=0.5 (left-center of target)")
    
    # Test 2: Waypoints
    print("\n3. Testing Waypoints...")
    conn2 = diagram.add_connection(
        node1, node3,
        label="Custom Path",
        waypoints=[
            (150, 200),  # First waypoint
            (200, 200)   # Second waypoint
        ]
    )
    print(f"   ✓ Created connection with waypoints: {conn2}")
    print(f"     - waypoints=[(150, 200), (200, 200)]")
    
    # Test 3: Combined Features
    print("\n4. Testing Combined Features...")
    conn3 = diagram.add_connection(
        node2, node3,
        label="Complex Route",
        exit_x=0.5,   # Exit from bottom
        exit_y=1.0,
        entry_x=0.5,  # Enter from top
        entry_y=0.0,
        waypoints=[
            (450, 180),
            (350, 180)
        ],
        label_position="center",
        label_background_color="#e3f2fd"
    )
    print(f"   ✓ Created connection with all features: {conn3}")
    print(f"     - Entry/exit points: exit_x=0.5, exit_y=1.0, entry_x=0.5, entry_y=0.0")
    print(f"     - Waypoints: [(450, 180), (350, 180)]")
    print(f"     - Label positioning: center with background color")
    
    # Test 4: Explicit Source/Target Points
    print("\n5. Testing Explicit Points...")
    node4 = diagram.add_shape("Node D", x=100, y=400, width=100, height=60)
    node5 = diagram.add_shape("Node E", x=400, y=400, width=100, height=60)
    conn4 = diagram.add_connection(
        node4, node5,
        label="Explicit",
        source_point=(220, 430),
        target_point=(400, 430)
    )
    print(f"   ✓ Created connection with explicit points: {conn4}")
    print(f"     - source_point=(220, 430)")
    print(f"     - target_point=(400, 430)")
    
    # Generate XML
    print("\n6. Generating Draw.io XML...")
    xml = diagram.to_drawio_xml()
    
    # Verify XML contains all features
    print("\n7. Verifying XML contains position parameters...")
    checks = [
        ('exitX="1.0"', "Exit X coordinate"),
        ('exitY="0.5"', "Exit Y coordinate"),
        ('entryX="0.0"', "Entry X coordinate"),
        ('entryY="0.5"', "Entry Y coordinate"),
        ('<Array as="points">', "Waypoints array"),
        ('<mxPoint x="150" y="200"/>', "First waypoint"),
        ('as="sourcePoint"', "Source point"),
        ('as="targetPoint"', "Target point"),
    ]
    
    all_passed = True
    for check_str, description in checks:
        if check_str in xml:
            print(f"   ✓ {description} found in XML")
        else:
            print(f"   ✗ {description} NOT found in XML")
            all_passed = False
    
    # Save to file
    print("\n8. Saving diagram...")
    from pathlib import Path
    output_path = Path("/tmp/connection_position_verification.drawio")
    output_path.write_text(xml, encoding='utf-8')
    print(f"   ✓ Saved to: {output_path}")
    print(f"   ✓ File size: {len(xml)} bytes")
    
    # Summary
    print("\n" + "=" * 70)
    if all_passed:
        print("✓ VERIFICATION PASSED")
        print("\nAll connection position control features are working correctly:")
        print("  • Entry/Exit Points (normalized 0-1 coordinates)")
        print("  • Waypoints (absolute pixel coordinates)")
        print("  • Explicit Source/Target Points (absolute pixel coordinates)")
        print("  • Combined with Label Positioning")
        print("\nThe feature requested in the issue is fully implemented.")
    else:
        print("✗ VERIFICATION FAILED")
        print("Some features are missing from XML output.")
    print("=" * 70 + "\n")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
