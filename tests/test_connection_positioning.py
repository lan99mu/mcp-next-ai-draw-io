#!/usr/bin/env python3
"""
Test suite for connection positioning features including entry/exit points and waypoints.
"""

import tempfile
from pathlib import Path
from mcp_drawio_server import Diagram


def test_entry_exit_points():
    """Test entry and exit point specification"""
    print("\n" + "=" * 70)
    print("TEST: Entry and Exit Points")
    print("=" * 70)
    
    diagram = Diagram(name="Entry Exit Test")
    
    # Create two nodes
    node1 = diagram.add_shape("Source", x=100, y=100, width=100, height=60)
    node2 = diagram.add_shape("Target", x=300, y=200, width=100, height=60)
    
    # Add connection with exit from right side of source (exitX=1, exitY=0.5)
    # and entry to left side of target (entryX=0, entryY=0.5)
    conn_id = diagram.add_connection(
        node1, node2,
        label="Right to Left",
        exit_x=1.0,      # Exit from right side of source
        exit_y=0.5,      # Exit from middle height
        entry_x=0.0,     # Enter left side of target
        entry_y=0.5      # Enter at middle height
    )
    
    print(f"✓ Created connection {conn_id} with entry/exit points")
    print(f"  Exit: (1.0, 0.5) - right center of source")
    print(f"  Entry: (0.0, 0.5) - left center of target")
    
    # Generate XML and verify
    xml = diagram.to_drawio_xml()
    assert 'exitX="1.0"' in xml, "exitX should be in XML"
    assert 'exitY="0.5"' in xml, "exitY should be in XML"
    assert 'entryX="0.0"' in xml, "entryX should be in XML"
    assert 'entryY="0.5"' in xml, "entryY should be in XML"
    
    print("✓ Entry/exit points correctly serialized to XML")
    print("✓ Test passed")
    return diagram


def test_waypoints():
    """Test waypoint routing"""
    print("\n" + "=" * 70)
    print("TEST: Waypoint Routing")
    print("=" * 70)
    
    diagram = Diagram(name="Waypoint Test")
    
    # Create two nodes
    node1 = diagram.add_shape("A", x=100, y=100, width=80, height=60)
    node2 = diagram.add_shape("B", x=400, y=250, width=80, height=60)
    
    # Add connection with waypoints to create a custom path
    waypoints = [
        (250, 130),  # First turn point
        (250, 200),  # Second turn point
        (350, 200)   # Third turn point
    ]
    
    conn_id = diagram.add_connection(
        node1, node2,
        label="Custom Path",
        waypoints=waypoints
    )
    
    print(f"✓ Created connection {conn_id} with {len(waypoints)} waypoints")
    for i, wp in enumerate(waypoints, 1):
        print(f"  Waypoint {i}: ({wp[0]}, {wp[1]})")
    
    # Generate XML and verify
    xml = diagram.to_drawio_xml()
    assert '<Array as="points">' in xml, "Waypoints array should be in XML"
    assert f'<mxPoint x="{waypoints[0][0]}" y="{waypoints[0][1]}"/>' in xml, "First waypoint should be in XML"
    
    print("✓ Waypoints correctly serialized to XML")
    print("✓ Test passed")
    return diagram


def test_source_target_points():
    """Test explicit source and target points"""
    print("\n" + "=" * 70)
    print("TEST: Source and Target Points")
    print("=" * 70)
    
    diagram = Diagram(name="Source Target Test")
    
    # Create two nodes
    node1 = diagram.add_shape("Start", x=100, y=100, width=100, height=60)
    node2 = diagram.add_shape("End", x=300, y=200, width=100, height=60)
    
    # Add connection with explicit source and target points
    conn_id = diagram.add_connection(
        node1, node2,
        label="Explicit Points",
        source_point=(220, 130),  # Explicit source position
        target_point=(300, 230)   # Explicit target position
    )
    
    print(f"✓ Created connection {conn_id} with explicit points")
    print(f"  Source point: (220, 130)")
    print(f"  Target point: (300, 230)")
    
    # Generate XML and verify
    xml = diagram.to_drawio_xml()
    assert 'as="sourcePoint"' in xml, "Source point should be in XML"
    assert 'as="targetPoint"' in xml, "Target point should be in XML"
    
    print("✓ Source/target points correctly serialized to XML")
    print("✓ Test passed")
    return diagram


def test_combined_connection_features():
    """Test combining all connection features"""
    print("\n" + "=" * 70)
    print("TEST: Combined Connection Features")
    print("=" * 70)
    
    diagram = Diagram(name="Combined Test")
    
    # Create nodes
    node1 = diagram.add_shape("Server", x=100, y=100, width=100, height=60)
    node2 = diagram.add_shape("Database", x=400, y=100, width=100, height=60)
    node3 = diagram.add_shape("Cache", x=250, y=250, width=100, height=60)
    
    # Connection 1: Entry/exit points + label positioning
    conn1 = diagram.add_connection(
        node1, node2,
        label="Query",
        exit_x=1.0,
        exit_y=0.5,
        entry_x=0.0,
        entry_y=0.5,
        label_position="center",
        label_background_color="#e3f2fd"
    )
    print(f"✓ Connection 1: Entry/exit + label positioning")
    
    # Connection 2: Waypoints + label offset
    conn2 = diagram.add_connection(
        node1, node3,
        label="Update",
        waypoints=[(150, 200)],
        label_offset_x=10,
        label_offset_y=-20
    )
    print(f"✓ Connection 2: Waypoints + label offset")
    
    # Connection 3: All features combined
    conn3 = diagram.add_connection(
        node2, node3,
        label="Sync",
        exit_x=0.5,
        exit_y=1.0,
        entry_x=0.5,
        entry_y=0.0,
        waypoints=[(450, 200), (350, 200)],
        label_position="right",
        label_offset_x=5,
        label_offset_y=5,
        label_background_color="#ffeb3b"
    )
    print(f"✓ Connection 3: All features combined")
    
    # Verify XML
    xml = diagram.to_drawio_xml()
    assert xml.count('<mxCell') >= 6, "Should have at least 6 cells (3 shapes + 3 connections)"
    
    print("✓ All connection features work together")
    print("✓ Test passed")
    return diagram


def test_xml_persistence():
    """Test that connection positioning is preserved in XML round-trip"""
    print("\n" + "=" * 70)
    print("TEST: XML Persistence")
    print("=" * 70)
    
    diagram = Diagram(name="Persistence Test")
    
    # Create nodes and connection with all features
    node1 = diagram.add_shape("A", x=100, y=100)
    node2 = diagram.add_shape("B", x=300, y=200)
    
    conn_id = diagram.add_connection(
        node1, node2,
        label="Test Connection",
        exit_x=1.0,
        exit_y=0.5,
        entry_x=0.0,
        entry_y=0.5,
        waypoints=[(200, 150)],
        label_position="center",
        label_offset_x=10,
        label_offset_y=-5
    )
    
    # Save to file
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "test.drawio"
        filepath.write_text(diagram.to_drawio_xml(), encoding='utf-8')
        
        print(f"✓ Saved diagram to {filepath}")
        
        # Read back and verify
        xml_content = filepath.read_text(encoding='utf-8')
        
        # Check all features are in XML
        assert 'exitX="1.0"' in xml_content
        assert 'exitY="0.5"' in xml_content
        assert 'entryX="0.0"' in xml_content
        assert 'entryY="0.5"' in xml_content
        assert '<Array as="points">' in xml_content
        assert '<mxPoint x="200" y="150"/>' in xml_content
        assert 'labelPosition=center' in xml_content
        
        print("✓ All connection features persisted in XML")
    
    print("✓ Test passed")
    return diagram


def test_backward_compatibility():
    """Test that existing connections without positioning still work"""
    print("\n" + "=" * 70)
    print("TEST: Backward Compatibility")
    print("=" * 70)
    
    diagram = Diagram(name="Backward Compat Test")
    
    # Create simple connection without new features
    node1 = diagram.add_shape("Old Style A", x=100, y=100)
    node2 = diagram.add_shape("Old Style B", x=300, y=200)
    
    conn_id = diagram.add_connection(
        node1, node2,
        label="Simple Connection"
    )
    
    print(f"✓ Created simple connection {conn_id} without positioning")
    
    # Generate XML - should work without errors
    xml = diagram.to_drawio_xml()
    assert conn_id in xml
    
    print("✓ Simple connections still work correctly")
    print("✓ Test passed")
    return diagram


def run_all_tests():
    """Run all tests"""
    print("\n" + "🔧" * 35)
    print("Connection Positioning Tests")
    print("🔧" * 35)
    
    tests = [
        test_entry_exit_points,
        test_waypoints,
        test_source_target_points,
        test_combined_connection_features,
        test_xml_persistence,
        test_backward_compatibility,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ Test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ Test error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 70)
    
    if failed > 0:
        print("\n✗ Some tests failed!")
        return False
    else:
        print("\n✓ All tests passed!")
        return True


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
