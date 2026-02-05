#!/usr/bin/env python3
"""
Demo script showing the line crossing detection feature.

This demonstrates how the MCP service can detect when connections cross
and provide position hints to help AI models adjust the diagram layout.
"""

from mcp_drawio_server.diagram import Diagram
from mcp_drawio_server.xml_operations import get_cells_from_xml
from mcp_drawio_server.crossing_detector import detect_crossings


def demo_crossing_detection_workflow():
    """
    Demonstrate a complete workflow of creating a diagram with crossing lines
    and then detecting and fixing them.
    """
    print("=" * 80)
    print("DEMO: Line Crossing Detection Workflow")
    print("=" * 80)
    
    # Step 1: Create a diagram with crossing connections
    print("\nStep 1: Creating a diagram with potential crossing issues...")
    print("-" * 80)
    
    diagram = Diagram(name="Software Architecture")
    
    # Create components in a layout that will cause crossings
    frontend = diagram.add_shape('Frontend', x=50, y=50, width=120, height=60)
    backend = diagram.add_shape('Backend', x=350, y=50, width=120, height=60)
    database = diagram.add_shape('Database', x=50, y=250, width=120, height=60)
    cache = diagram.add_shape('Cache', x=350, y=250, width=120, height=60)
    
    # Add connections that will cross
    conn1 = diagram.add_connection(frontend, cache, label="Read Cache")
    conn2 = diagram.add_connection(backend, database, label="Query DB")
    
    print(f"Created 4 components:")
    print(f"  - Frontend at (50, 50)")
    print(f"  - Backend at (350, 50)")
    print(f"  - Database at (50, 250)")
    print(f"  - Cache at (350, 250)")
    print(f"\nAdded 2 connections:")
    print(f"  - Frontend → Cache")
    print(f"  - Backend → Database")
    
    # Step 2: Detect crossings
    print("\nStep 2: Detecting line crossings...")
    print("-" * 80)
    
    xml_content = diagram.to_drawio_xml()
    cells = get_cells_from_xml(xml_content)
    crossings = detect_crossings(cells)
    
    if crossings:
        print(f"⚠️  Found {len(crossings)} crossing(s)!\n")
        
        for i, crossing in enumerate(crossings, 1):
            print(f"Crossing {i}:")
            print(f"  Lines: '{crossing['connection1_label']}' ⨯ '{crossing['connection2_label']}'")
            print(f"  Intersection: ({crossing['intersection_point'][0]:.1f}, {crossing['intersection_point'][1]:.1f})")
            print(f"\n{crossing['suggestion']}\n")
    else:
        print("✓ No crossings detected!")
    
    # Step 3: Fix the crossing by adding waypoints
    print("\nStep 3: Fixing crossings by adding waypoints...")
    print("-" * 80)
    
    # Remove the old connection and add a new one with waypoints
    del diagram.connections[conn1]
    
    # Add waypoint to route around the crossing
    conn1_fixed = diagram.add_connection(
        frontend, 
        cache, 
        label="Read Cache",
        waypoints=[(250, 150)]  # Add a waypoint to route around
    )
    
    print("Added waypoint to 'Read Cache' connection at (250, 150)")
    
    # Verify the fix
    xml_content = diagram.to_drawio_xml()
    cells = get_cells_from_xml(xml_content)
    crossings_after = detect_crossings(cells)
    
    print(f"\nRe-checking for crossings...")
    if not crossings_after:
        print("✓ Success! No crossings detected after adjustment!")
    else:
        print(f"⚠️  Still {len(crossings_after)} crossing(s) remaining")
    
    # Step 4: Save the result
    print("\nStep 4: Saving the diagram...")
    print("-" * 80)
    
    output_file = "/tmp/demo_crossing_fixed.drawio"
    with open(output_file, 'w') as f:
        f.write(xml_content)
    
    print(f"✓ Diagram saved to: {output_file}")
    print(f"\nYou can open this file in Draw.io to visualize the result!")
    
    return diagram


def demo_complex_diagram():
    """
    Demonstrate crossing detection on a more complex diagram.
    """
    print("\n\n" + "=" * 80)
    print("DEMO: Complex Diagram with Multiple Crossings")
    print("=" * 80)
    
    diagram = Diagram(name="Microservices Architecture")
    
    # Create a more complex layout
    api_gateway = diagram.add_shape('API Gateway', x=250, y=50, width=120, height=60)
    
    auth_service = diagram.add_shape('Auth Service', x=50, y=200, width=100, height=50)
    user_service = diagram.add_shape('User Service', x=200, y=200, width=100, height=50)
    order_service = diagram.add_shape('Order Service', x=350, y=200, width=100, height=50)
    payment_service = diagram.add_shape('Payment Service', x=500, y=200, width=100, height=50)
    
    db1 = diagram.add_shape('Users DB', x=50, y=350, width=100, height=50)
    db2 = diagram.add_shape('Orders DB', x=350, y=350, width=100, height=50)
    
    # Add many connections
    diagram.add_connection(api_gateway, auth_service, label="Auth")
    diagram.add_connection(api_gateway, user_service, label="Users")
    diagram.add_connection(api_gateway, order_service, label="Orders")
    diagram.add_connection(api_gateway, payment_service, label="Payment")
    
    diagram.add_connection(user_service, db1, label="Query")
    diagram.add_connection(order_service, db2, label="Query")
    
    # Cross-service dependencies that might cause crossings
    diagram.add_connection(order_service, payment_service, label="Process")
    diagram.add_connection(auth_service, user_service, label="Validate")
    
    print(f"Created microservices architecture with 8 components and 8 connections")
    
    # Detect crossings
    xml_content = diagram.to_drawio_xml()
    cells = get_cells_from_xml(xml_content)
    crossings = detect_crossings(cells)
    
    print(f"\nCrossing Detection Results:")
    print(f"  Total connections: 8")
    print(f"  Crossings found: {len(crossings)}")
    
    if crossings:
        print(f"\n⚠️  Detected {len(crossings)} crossing(s) that need attention:\n")
        
        for i, crossing in enumerate(crossings, 1):
            print(f"{i}. '{crossing['connection1_label']}' ⨯ '{crossing['connection2_label']}'")
            print(f"   at ({crossing['intersection_point'][0]:.1f}, {crossing['intersection_point'][1]:.1f})")
        
        print(f"\n💡 Suggestions to improve the diagram:")
        print(f"  - Use waypoints to route connections around each other")
        print(f"  - Adjust entry/exit points to change connection angles")
        print(f"  - Reorganize shapes to minimize crossing paths")
    else:
        print("✓ Great layout! No crossings detected.")
    
    return diagram


if __name__ == "__main__":
    # Run the demos
    diagram1 = demo_crossing_detection_workflow()
    diagram2 = demo_complex_diagram()
    
    print("\n" + "=" * 80)
    print("Demo completed successfully!")
    print("=" * 80)
    print("\nKey Takeaways:")
    print("  1. The MCP service can detect when connections cross each other")
    print("  2. It provides the intersection point coordinates")
    print("  3. It suggests multiple ways to fix crossings:")
    print("     - Add waypoints to route connections")
    print("     - Reposition shapes")
    print("     - Adjust entry/exit points")
    print("  4. AI models can use these hints to automatically improve diagram layouts")
    print("\n" + "=" * 80)
