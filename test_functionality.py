#!/usr/bin/env python3
"""
Simple test script to verify the MCP Draw.io server functionality
This tests the core diagram generation without MCP protocol overhead
"""

from mcp_drawio_server import Diagram


def test_create_simple_diagram():
    """Test creating a simple flowchart"""
    print("Testing simple diagram creation...")
    
    # Create a new diagram
    diagram = Diagram(name="Test Flowchart")
    
    # Add shapes
    start_id = diagram.add_shape("Start", x=100, y=50, width=100, height=40, shape_type="ellipse")
    process_id = diagram.add_shape("Process Data", x=100, y=150, width=120, height=60, shape_type="rectangle")
    decision_id = diagram.add_shape("Is Valid?", x=100, y=270, width=100, height=80, shape_type="diamond")
    end_yes_id = diagram.add_shape("Success", x=50, y=400, width=100, height=40, shape_type="ellipse")
    end_no_id = diagram.add_shape("Error", x=200, y=400, width=100, height=40, shape_type="ellipse")
    
    # Add connections
    diagram.add_connection(start_id, process_id, label="")
    diagram.add_connection(process_id, decision_id, label="")
    diagram.add_connection(decision_id, end_yes_id, label="Yes")
    diagram.add_connection(decision_id, end_no_id, label="No")
    
    # Generate XML
    xml = diagram.to_drawio_xml()
    
    # Verify XML structure
    assert '<mxfile' in xml
    assert 'diagram name="Test Flowchart"' in xml
    assert 'Start' in xml
    assert 'Process Data' in xml
    assert 'Is Valid?' in xml
    
    print("✓ Diagram created successfully")
    print(f"✓ Generated {len(xml)} characters of XML")
    print(f"✓ Contains {len(diagram.shapes)} shapes")
    print(f"✓ Contains {len(diagram.connections)} connections")
    
    return xml


def test_shape_types():
    """Test different shape types"""
    print("\nTesting different shape types...")
    
    diagram = Diagram(name="Shape Types Demo")
    
    shape_types = ["rectangle", "ellipse", "diamond", "parallelogram", "hexagon", "cylinder", "cloud"]
    x_pos = 50
    
    for shape_type in shape_types:
        diagram.add_shape(
            label=shape_type.capitalize(),
            x=x_pos,
            y=100,
            shape_type=shape_type
        )
        x_pos += 150
    
    xml = diagram.to_drawio_xml()
    
    # Verify all shape types are in the XML
    for shape_type in shape_types:
        assert shape_type.capitalize() in xml
    
    print(f"✓ Successfully created {len(shape_types)} different shape types")
    
    return xml


def test_system_architecture():
    """Test creating a system architecture diagram"""
    print("\nTesting system architecture diagram...")
    
    diagram = Diagram(name="System Architecture")
    
    # Add components
    client = diagram.add_shape("Web Browser", x=200, y=50, width=120, height=60)
    lb = diagram.add_shape("Load Balancer", x=200, y=150, width=120, height=60)
    api1 = diagram.add_shape("API Server 1", x=50, y=250, width=120, height=60)
    api2 = diagram.add_shape("API Server 2", x=200, y=250, width=120, height=60)
    api3 = diagram.add_shape("API Server 3", x=350, y=250, width=120, height=60)
    db = diagram.add_shape("Database", x=200, y=350, width=120, height=80, shape_type="cylinder")
    
    # Add connections
    diagram.add_connection(client, lb, label="HTTPS")
    diagram.add_connection(lb, api1)
    diagram.add_connection(lb, api2)
    diagram.add_connection(lb, api3)
    diagram.add_connection(api1, db)
    diagram.add_connection(api2, db)
    diagram.add_connection(api3, db)
    
    xml = diagram.to_drawio_xml()
    
    print(f"✓ Created architecture diagram with {len(diagram.shapes)} components")
    print(f"✓ Created {len(diagram.connections)} connections")
    
    return xml


def save_diagram_to_file(xml_content, filename):
    """Save diagram XML to a file"""
    filepath = f"/tmp/{filename}"
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(xml_content)
    print(f"\n✓ Saved diagram to: {filepath}")
    return filepath


if __name__ == "__main__":
    print("=" * 60)
    print("MCP Draw.io Server - Functionality Tests")
    print("=" * 60)
    
    try:
        # Test 1: Simple diagram
        xml1 = test_create_simple_diagram()
        save_diagram_to_file(xml1, "test_flowchart.drawio")
        
        # Test 2: Shape types
        xml2 = test_shape_types()
        save_diagram_to_file(xml2, "test_shapes.drawio")
        
        # Test 3: System architecture
        xml3 = test_system_architecture()
        save_diagram_to_file(xml3, "test_architecture.drawio")
        
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
