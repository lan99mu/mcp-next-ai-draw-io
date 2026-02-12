#!/usr/bin/env python3
"""
Test script for activity diagrams and swimlane diagrams
Tests the new shape types added to support activity and swimlane diagrams
"""

import tempfile
from pathlib import Path
from mcp_drawio_server import Diagram


def test_activity_diagram():
    """Test creating an activity diagram with all activity shape types"""
    print("Testing activity diagram creation...")
    
    # Create a new diagram
    diagram = Diagram(name="Activity Diagram Test")
    
    # Add activity diagram shapes
    start = diagram.add_shape("", x=200, y=50, width=40, height=40, shape_type="activity_start")
    action1 = diagram.add_shape("Process Order", x=150, y=120, width=140, height=60, shape_type="activity_action")
    decision = diagram.add_shape("Valid?", x=180, y=220, width=80, height=80, shape_type="activity_decision")
    fork = diagram.add_shape("", x=150, y=340, width=140, height=10, shape_type="activity_fork")
    action2 = diagram.add_shape("Send Email", x=50, y=390, width=120, height=60, shape_type="activity_action")
    action3 = diagram.add_shape("Update DB", x=220, y=390, width=120, height=60, shape_type="activity_action")
    join = diagram.add_shape("", x=150, y=490, width=140, height=10, shape_type="activity_join")
    end = diagram.add_shape("", x=200, y=540, width=40, height=40, shape_type="activity_end")
    note = diagram.add_shape("Important Note", x=350, y=120, width=120, height=60, shape_type="activity_note")
    
    # Add connections
    diagram.add_connection(start, action1)
    diagram.add_connection(action1, decision)
    diagram.add_connection(decision, fork, label="Yes")
    diagram.add_connection(fork, action2)
    diagram.add_connection(fork, action3)
    diagram.add_connection(action2, join)
    diagram.add_connection(action3, join)
    diagram.add_connection(join, end)
    
    # Generate XML
    xml = diagram.to_drawio_xml()
    
    # Verify XML structure
    assert '<mxfile' in xml
    assert 'diagram name="Activity Diagram Test"' in xml
    assert 'Process Order' in xml
    assert 'Valid?' in xml
    assert 'Send Email' in xml
    assert 'Update DB' in xml
    assert 'Important Note' in xml
    
    # Verify activity shape styles are present
    assert 'activity_start' in str(diagram.shapes[start].shape_type)
    assert 'activity_end' in str(diagram.shapes[end].shape_type)
    assert 'activity_action' in str(diagram.shapes[action1].shape_type)
    assert 'activity_decision' in str(diagram.shapes[decision].shape_type)
    assert 'activity_fork' in str(diagram.shapes[fork].shape_type)
    assert 'activity_join' in str(diagram.shapes[join].shape_type)
    assert 'activity_note' in str(diagram.shapes[note].shape_type)
    
    print("✓ Activity diagram created successfully")
    print(f"✓ Generated {len(xml)} characters of XML")
    print(f"✓ Contains {len(diagram.shapes)} shapes")
    print(f"✓ Contains {len(diagram.connections)} connections")
    
    return xml


def test_swimlane_diagram():
    """Test creating a swimlane diagram"""
    print("\nTesting swimlane diagram creation...")
    
    # Create a new diagram
    diagram = Diagram(name="Swimlane Diagram Test")
    
    # Add swimlane containers
    pool = diagram.add_shape("Order Processing", x=50, y=50, width=700, height=400, shape_type="swimlane_pool")
    lane1 = diagram.add_shape("Customer", x=50, y=80, width=700, height=120, shape_type="swimlane_h")
    lane2 = diagram.add_shape("Sales", x=50, y=210, width=700, height=120, shape_type="swimlane_h")
    lane3 = diagram.add_shape("Warehouse", x=50, y=340, width=700, height=110, shape_type="swimlane_h")
    
    # Add activities within lanes
    activity1 = diagram.add_shape("Place Order", x=100, y=110, width=100, height=50, shape_type="activity_action")
    activity2 = diagram.add_shape("Review Order", x=250, y=240, width=100, height=50, shape_type="activity_action")
    activity3 = diagram.add_shape("Ship Order", x=400, y=370, width=100, height=50, shape_type="activity_action")
    
    # Add connections
    diagram.add_connection(activity1, activity2, label="Submit")
    diagram.add_connection(activity2, activity3, label="Approve")
    
    # Generate XML
    xml = diagram.to_drawio_xml()
    
    # Verify XML structure
    assert '<mxfile' in xml
    assert 'diagram name="Swimlane Diagram Test"' in xml
    assert 'Order Processing' in xml
    assert 'Customer' in xml
    assert 'Sales' in xml
    assert 'Warehouse' in xml
    assert 'Place Order' in xml
    assert 'Review Order' in xml
    assert 'Ship Order' in xml
    
    # Verify swimlane shape types
    assert 'swimlane_pool' in str(diagram.shapes[pool].shape_type)
    assert 'swimlane_h' in str(diagram.shapes[lane1].shape_type)
    
    print("✓ Swimlane diagram created successfully")
    print(f"✓ Generated {len(xml)} characters of XML")
    print(f"✓ Contains {len(diagram.shapes)} shapes")
    print(f"✓ Contains {len(diagram.connections)} connections")
    
    return xml


def test_vertical_swimlane():
    """Test creating a vertical swimlane diagram"""
    print("\nTesting vertical swimlane diagram creation...")
    
    # Create a new diagram
    diagram = Diagram(name="Vertical Swimlane Test")
    
    # Add vertical swimlanes
    container = diagram.add_shape("Process Flow", x=50, y=50, width=600, height=300, shape_type="container")
    vlane1 = diagram.add_shape("Stage 1", x=50, y=80, width=180, height=270, shape_type="swimlane_v")
    vlane2 = diagram.add_shape("Stage 2", x=240, y=80, width=180, height=270, shape_type="swimlane_v")
    vlane3 = diagram.add_shape("Stage 3", x=430, y=80, width=220, height=270, shape_type="swimlane_v")
    
    # Add activities
    act1 = diagram.add_shape("Start", x=100, y=150, width=80, height=50, shape_type="activity_action")
    act2 = diagram.add_shape("Process", x=280, y=150, width=80, height=50, shape_type="activity_action")
    act3 = diagram.add_shape("Complete", x=480, y=150, width=80, height=50, shape_type="activity_action")
    
    # Connect activities
    diagram.add_connection(act1, act2)
    diagram.add_connection(act2, act3)
    
    # Generate XML
    xml = diagram.to_drawio_xml()
    
    # Verify
    assert 'Vertical Swimlane Test' in xml
    assert 'swimlane_v' in str(diagram.shapes[vlane1].shape_type)
    assert 'container' in str(diagram.shapes[container].shape_type)
    
    print("✓ Vertical swimlane diagram created successfully")
    print(f"✓ Contains {len(diagram.shapes)} shapes")
    
    return xml


def test_all_activity_shapes():
    """Test that all activity diagram shape types are available"""
    print("\nTesting all activity diagram shape types...")
    
    diagram = Diagram(name="All Activity Shapes")
    
    activity_shapes = [
        "activity_start",
        "activity_end", 
        "activity_action",
        "activity_decision",
        "activity_fork",
        "activity_join",
        "activity_send_signal",
        "activity_receive_signal",
        "activity_note"
    ]
    
    x_pos = 50
    for shape_type in activity_shapes:
        shape_id = diagram.add_shape(
            label=shape_type.replace("_", " ").title(),
            x=x_pos,
            y=100,
            width=100,
            height=60,
            shape_type=shape_type
        )
        assert shape_id is not None
        assert diagram.shapes[shape_id].shape_type == shape_type
        x_pos += 120
    
    xml = diagram.to_drawio_xml()
    
    # Verify all shapes are in the XML
    for shape_type in activity_shapes:
        label = shape_type.replace("_", " ").title()
        assert label in xml
    
    print(f"✓ Successfully created all {len(activity_shapes)} activity shape types")
    
    return xml


def save_diagram_to_file(xml_content, filename):
    """Save diagram XML to a file"""
    tmp_dir = Path(tempfile.gettempdir())
    filepath = tmp_dir / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(xml_content)
    print(f"✓ Saved diagram to: {filepath}")
    return filepath


if __name__ == "__main__":
    print("=" * 60)
    print("Activity and Swimlane Diagram Tests")
    print("=" * 60)
    
    try:
        # Test activity diagram
        xml1 = test_activity_diagram()
        save_diagram_to_file(xml1, "test_activity_diagram.drawio")
        
        # Test swimlane diagram
        xml2 = test_swimlane_diagram()
        save_diagram_to_file(xml2, "test_swimlane_diagram.drawio")
        
        # Test vertical swimlane
        xml3 = test_vertical_swimlane()
        save_diagram_to_file(xml3, "test_vertical_swimlane.drawio")
        
        # Test all activity shapes
        xml4 = test_all_activity_shapes()
        save_diagram_to_file(xml4, "test_all_activity_shapes.drawio")
        
        print("\n" + "=" * 60)
        print("✓ All tests passed successfully!")
        print("=" * 60)
        print("\nGenerated .drawio files can be opened in:")
        print("  - VS Code with Draw.io extension")
        print("  - Draw.io desktop application")
        print("  - https://app.diagrams.net/")
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
