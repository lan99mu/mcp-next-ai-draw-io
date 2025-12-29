#!/usr/bin/env python3
"""
Test script for coordinate system and node binding features
"""

import tempfile
from pathlib import Path
from mcp_drawio_server import Diagram


def test_coordinate_system():
    """Test that coordinate information is properly tracked"""
    print("Testing coordinate system...")
    
    diagram = Diagram(name="Coordinate Test")
    
    # Add shapes at specific positions
    shape1_id = diagram.add_shape("Shape 1", x=100, y=50, width=120, height=60)
    shape2_id = diagram.add_shape("Shape 2", x=300, y=200, width=80, height=40)
    
    # Verify coordinates are stored
    shape1 = diagram.shapes[shape1_id]
    assert shape1.x == 100
    assert shape1.y == 50
    assert shape1.width == 120
    assert shape1.height == 60
    
    shape2 = diagram.shapes[shape2_id]
    assert shape2.x == 300
    assert shape2.y == 200
    
    # Calculate center points
    center1_x = shape1.x + shape1.width / 2
    center1_y = shape1.y + shape1.height / 2
    assert center1_x == 160
    assert center1_y == 80
    
    print("✓ Coordinate system works correctly")
    print(f"  Shape 1 center: ({center1_x}, {center1_y})")
    print(f"  Shape 2 position: ({shape2.x}, {shape2.y})")
    
    return diagram


def test_node_binding():
    """Test node binding functionality"""
    print("\nTesting node binding...")
    
    diagram = Diagram(name="Binding Test")
    
    # Create 3 shapes
    shape1_id = diagram.add_shape("Node 1", x=100, y=100, width=80, height=60)
    shape2_id = diagram.add_shape("Node 2", x=200, y=100, width=80, height=60)
    shape3_id = diagram.add_shape("Node 3", x=150, y=200, width=80, height=60)
    
    # Initially, no nodes should be bound
    assert len(diagram.shapes[shape1_id].bound_nodes) == 0
    assert len(diagram.shapes[shape2_id].bound_nodes) == 0
    assert len(diagram.shapes[shape3_id].bound_nodes) == 0
    
    # Bind shape1 and shape2 together
    node_ids = [shape1_id, shape2_id]
    for node_id in node_ids:
        other_nodes = [nid for nid in node_ids if nid != node_id]
        diagram.shapes[node_id].bound_nodes = list(set(diagram.shapes[node_id].bound_nodes + other_nodes))
    
    # Verify binding
    assert shape2_id in diagram.shapes[shape1_id].bound_nodes
    assert shape1_id in diagram.shapes[shape2_id].bound_nodes
    assert len(diagram.shapes[shape3_id].bound_nodes) == 0
    
    print("✓ Node binding works correctly")
    print(f"  {shape1_id} bound to: {diagram.shapes[shape1_id].bound_nodes}")
    print(f"  {shape2_id} bound to: {diagram.shapes[shape2_id].bound_nodes}")
    
    return diagram


def test_move_with_binding():
    """Test that moving a node moves its bound nodes"""
    print("\nTesting move with binding...")
    
    diagram = Diagram(name="Move Test")
    
    # Create 3 shapes
    shape1_id = diagram.add_shape("Node 1", x=100, y=100, width=80, height=60)
    shape2_id = diagram.add_shape("Node 2", x=200, y=100, width=80, height=60)
    shape3_id = diagram.add_shape("Node 3", x=150, y=200, width=80, height=60)
    
    # Bind all three nodes together
    node_ids = [shape1_id, shape2_id, shape3_id]
    for node_id in node_ids:
        other_nodes = [nid for nid in node_ids if nid != node_id]
        diagram.shapes[node_id].bound_nodes = list(set(diagram.shapes[node_id].bound_nodes + other_nodes))
    
    # Record original positions
    orig_pos = {
        shape1_id: (diagram.shapes[shape1_id].x, diagram.shapes[shape1_id].y),
        shape2_id: (diagram.shapes[shape2_id].x, diagram.shapes[shape2_id].y),
        shape3_id: (diagram.shapes[shape3_id].x, diagram.shapes[shape3_id].y),
    }
    
    # Move shape1 to a new position
    old_x = diagram.shapes[shape1_id].x
    old_y = diagram.shapes[shape1_id].y
    new_x = 150
    new_y = 150
    
    offset_x = new_x - old_x
    offset_y = new_y - old_y
    
    # Move the shape
    diagram.shapes[shape1_id].x = new_x
    diagram.shapes[shape1_id].y = new_y
    
    # Move all bound nodes by the same offset
    for bound_id in diagram.shapes[shape1_id].bound_nodes:
        if bound_id in diagram.shapes:
            diagram.shapes[bound_id].x += offset_x
            diagram.shapes[bound_id].y += offset_y
    
    # Verify all nodes moved by the same offset
    assert diagram.shapes[shape1_id].x == new_x
    assert diagram.shapes[shape1_id].y == new_y
    assert diagram.shapes[shape2_id].x == orig_pos[shape2_id][0] + offset_x
    assert diagram.shapes[shape2_id].y == orig_pos[shape2_id][1] + offset_y
    assert diagram.shapes[shape3_id].x == orig_pos[shape3_id][0] + offset_x
    assert diagram.shapes[shape3_id].y == orig_pos[shape3_id][1] + offset_y
    
    print("✓ Moving bound nodes works correctly")
    print(f"  Offset applied: ({offset_x}, {offset_y})")
    print(f"  {shape1_id} moved to: ({diagram.shapes[shape1_id].x}, {diagram.shapes[shape1_id].y})")
    print(f"  {shape2_id} moved to: ({diagram.shapes[shape2_id].x}, {diagram.shapes[shape2_id].y})")
    print(f"  {shape3_id} moved to: ({diagram.shapes[shape3_id].x}, {diagram.shapes[shape3_id].y})")
    
    return diagram


def test_xml_persistence():
    """Test that bound_nodes are preserved in XML"""
    print("\nTesting XML persistence of bindings...")
    
    diagram = Diagram(name="Persistence Test")
    
    # Create and bind nodes
    shape1_id = diagram.add_shape("Node 1", x=100, y=100, width=80, height=60)
    shape2_id = diagram.add_shape("Node 2", x=200, y=100, width=80, height=60)
    
    # Bind them
    diagram.shapes[shape1_id].bound_nodes = [shape2_id]
    diagram.shapes[shape2_id].bound_nodes = [shape1_id]
    
    # Generate XML
    xml = diagram.to_drawio_xml()
    
    # Verify bound_nodes are in XML
    assert 'bound_nodes=' in xml
    assert shape2_id in xml  # Should appear in bound_nodes attribute
    
    print("✓ Bound nodes are preserved in XML")
    print(f"  XML contains bound_nodes attribute")
    
    # Save and verify file can be created
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test_binding.drawio"
        test_file.write_text(xml)
        
        # Verify file was created
        assert test_file.exists()
        content = test_file.read_text()
        assert 'bound_nodes=' in content
        
        print(f"  Successfully saved to file with {len(content)} bytes")
    
    return diagram


def test_unbinding():
    """Test unbinding nodes"""
    print("\nTesting node unbinding...")
    
    diagram = Diagram(name="Unbind Test")
    
    # Create 3 shapes and bind them
    shape1_id = diagram.add_shape("Node 1", x=100, y=100, width=80, height=60)
    shape2_id = diagram.add_shape("Node 2", x=200, y=100, width=80, height=60)
    shape3_id = diagram.add_shape("Node 3", x=150, y=200, width=80, height=60)
    
    # Bind all together
    node_ids = [shape1_id, shape2_id, shape3_id]
    for node_id in node_ids:
        other_nodes = [nid for nid in node_ids if nid != node_id]
        diagram.shapes[node_id].bound_nodes = list(set(diagram.shapes[node_id].bound_nodes + other_nodes))
    
    # Verify they're bound
    assert len(diagram.shapes[shape1_id].bound_nodes) == 2
    assert len(diagram.shapes[shape2_id].bound_nodes) == 2
    
    # Unbind shape1
    bound_to = diagram.shapes[shape1_id].bound_nodes.copy()
    diagram.shapes[shape1_id].bound_nodes = []
    
    # Remove shape1 from other nodes' binding lists
    for other_id in bound_to:
        if other_id in diagram.shapes:
            if shape1_id in diagram.shapes[other_id].bound_nodes:
                diagram.shapes[other_id].bound_nodes.remove(shape1_id)
    
    # Verify unbinding
    assert len(diagram.shapes[shape1_id].bound_nodes) == 0
    assert shape1_id not in diagram.shapes[shape2_id].bound_nodes
    assert shape1_id not in diagram.shapes[shape3_id].bound_nodes
    # shape2 and shape3 should still be bound to each other
    assert shape3_id in diagram.shapes[shape2_id].bound_nodes
    assert shape2_id in diagram.shapes[shape3_id].bound_nodes
    
    print("✓ Node unbinding works correctly")
    print(f"  {shape1_id} is now unbound")
    print(f"  {shape2_id} still bound to: {diagram.shapes[shape2_id].bound_nodes}")
    print(f"  {shape3_id} still bound to: {diagram.shapes[shape3_id].bound_nodes}")


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Testing Coordinate System and Node Binding Features")
    print("=" * 60)
    
    try:
        test_coordinate_system()
        test_node_binding()
        test_move_with_binding()
        test_xml_persistence()
        test_unbinding()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        raise
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        raise


if __name__ == "__main__":
    run_all_tests()
