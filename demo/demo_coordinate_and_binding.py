#!/usr/bin/env python3
"""
Demo script showcasing coordinate system and node binding features
"""

import tempfile
from pathlib import Path
from mcp_drawio_server import Diagram


def demo_coordinate_system():
    """Demonstrate coordinate system features"""
    print("=" * 70)
    print("DEMO: Coordinate System")
    print("=" * 70)
    
    diagram = Diagram(name="Coordinate System Demo")
    
    # Create a simple layout with three nodes
    print("\n1. Creating three nodes in a vertical layout...")
    node1_id = diagram.add_shape("Server", x=100, y=50, width=120, height=60)
    node2_id = diagram.add_shape("Database", x=100, y=150, width=120, height=60)
    node3_id = diagram.add_shape("Cache", x=100, y=250, width=120, height=60)
    
    print(f"   Created: {node1_id}, {node2_id}, {node3_id}")
    
    # Show coordinate information
    print("\n2. Coordinate information for each node:")
    for node_id, node in diagram.shapes.items():
        center_x = node.x + node.width / 2
        center_y = node.y + node.height / 2
        print(f"\n   {node_id} ({node.label}):")
        print(f"   - Position: ({node.x}, {node.y})")
        print(f"   - Size: {node.width} x {node.height}")
        print(f"   - Center: ({center_x}, {center_y})")
        print(f"   - Bounding box: ({node.x}, {node.y}) to ({node.x + node.width}, {node.y + node.height})")
    
    print("\n3. Spatial relationship analysis:")
    print("   - All nodes are vertically aligned (same x-coordinate: 100)")
    print("   - Node spacing: 100 pixels vertically between nodes")
    print("   - Nodes are arranged in a top-to-bottom flow")
    
    # Save the diagram
    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "coordinate_demo.drawio"
        output_file.write_text(diagram.to_drawio_xml())
        print(f"\n✓ Saved to: {output_file}")
    
    return diagram


def demo_node_binding():
    """Demonstrate node binding features"""
    print("\n" + "=" * 70)
    print("DEMO: Node Binding")
    print("=" * 70)
    
    diagram = Diagram(name="Node Binding Demo")
    
    # Create a microservices architecture
    print("\n1. Creating a microservices architecture...")
    api_id = diagram.add_shape("API Gateway", x=150, y=50, width=120, height=60)
    auth_id = diagram.add_shape("Auth Service", x=50, y=150, width=100, height=60)
    auth_db_id = diagram.add_shape("Auth DB", x=50, y=250, width=100, height=50)
    user_id = diagram.add_shape("User Service", x=250, y=150, width=100, height=60)
    user_db_id = diagram.add_shape("User DB", x=250, y=250, width=100, height=50)
    
    print(f"   Created 5 nodes: API Gateway + 2 microservices with databases")
    
    # Bind each service with its database
    print("\n2. Binding services with their databases...")
    
    # Bind Auth Service with Auth DB
    auth_nodes = [auth_id, auth_db_id]
    for node_id in auth_nodes:
        other_nodes = [nid for nid in auth_nodes if nid != node_id]
        diagram.shapes[node_id].bound_nodes = other_nodes
    print(f"   ✓ Bound {auth_id} with {auth_db_id}")
    
    # Bind User Service with User DB
    user_nodes = [user_id, user_db_id]
    for node_id in user_nodes:
        other_nodes = [nid for nid in user_nodes if nid != node_id]
        diagram.shapes[node_id].bound_nodes = other_nodes
    print(f"   ✓ Bound {user_id} with {user_db_id}")
    
    # Show current positions
    print("\n3. Current positions:")
    for node_id, node in diagram.shapes.items():
        bound_info = f" (bound to: {', '.join(node.bound_nodes)})" if node.bound_nodes else ""
        print(f"   {node_id} '{node.label}': ({node.x}, {node.y}){bound_info}")
    
    # Move a service - its database should move with it
    print(f"\n4. Moving {auth_id} (Auth Service) to a new position...")
    auth_service = diagram.shapes[auth_id]
    old_x, old_y = auth_service.x, auth_service.y
    new_x, new_y = 400, 150
    
    offset_x = new_x - old_x
    offset_y = new_y - old_y
    
    # Move the service
    auth_service.x = new_x
    auth_service.y = new_y
    
    # Move bound nodes (database)
    for bound_id in auth_service.bound_nodes:
        diagram.shapes[bound_id].x += offset_x
        diagram.shapes[bound_id].y += offset_y
    
    print(f"   Moved from ({old_x}, {old_y}) to ({new_x}, {new_y})")
    print(f"   Offset applied: ({offset_x}, {offset_y})")
    print(f"   Auth DB also moved to: ({diagram.shapes[auth_db_id].x}, {diagram.shapes[auth_db_id].y})")
    
    # Show final positions
    print("\n5. Final positions after move:")
    for node_id, node in diagram.shapes.items():
        print(f"   {node_id} '{node.label}': ({node.x}, {node.y})")
    
    # Save the diagram
    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "binding_demo.drawio"
        output_file.write_text(diagram.to_drawio_xml())
        print(f"\n✓ Saved to: {output_file}")
        
        # Verify bindings are in XML
        xml_content = output_file.read_text()
        if 'bound_nodes=' in xml_content:
            print("✓ Bindings are preserved in the XML file")
    
    return diagram


def demo_combined_features():
    """Demonstrate using both features together"""
    print("\n" + "=" * 70)
    print("DEMO: Combined Features - Layout Management")
    print("=" * 70)
    
    diagram = Diagram(name="Combined Demo")
    
    print("\n1. Creating a 3-tier architecture...")
    
    # Frontend tier
    web_id = diagram.add_shape("Web App", x=150, y=50, width=100, height=60)
    
    # Backend tier
    api1_id = diagram.add_shape("API-1", x=50, y=180, width=80, height=60)
    api2_id = diagram.add_shape("API-2", x=160, y=180, width=80, height=60)
    api3_id = diagram.add_shape("API-3", x=270, y=180, width=80, height=60)
    
    # Data tier
    db1_id = diagram.add_shape("DB-1", x=50, y=300, width=80, height=50)
    db2_id = diagram.add_shape("DB-2", x=160, y=300, width=80, height=50)
    db3_id = diagram.add_shape("DB-3", x=270, y=300, width=80, height=50)
    
    # Bind each API with its database
    print("\n2. Binding each API with its database...")
    for api_id, db_id in [(api1_id, db1_id), (api2_id, db2_id), (api3_id, db3_id)]:
        diagram.shapes[api_id].bound_nodes = [db_id]
        diagram.shapes[db_id].bound_nodes = [api_id]
        print(f"   ✓ Bound {api_id} with {db_id}")
    
    # Calculate and show the center of the entire system
    print("\n3. Analyzing overall layout:")
    all_x = [node.x for node in diagram.shapes.values()]
    all_y = [node.y for node in diagram.shapes.values()]
    all_widths = [node.width for node in diagram.shapes.values()]
    all_heights = [node.height for node in diagram.shapes.values()]
    
    min_x = min(all_x)
    max_x = max(x + w for x, w in zip(all_x, all_widths))
    min_y = min(all_y)
    max_y = max(y + h for y, h in zip(all_y, all_heights))
    
    layout_width = max_x - min_x
    layout_height = max_y - min_y
    layout_center_x = min_x + layout_width / 2
    layout_center_y = min_y + layout_height / 2
    
    print(f"   Overall bounding box: ({min_x}, {min_y}) to ({max_x}, {max_y})")
    print(f"   Layout size: {layout_width} x {layout_height}")
    print(f"   Layout center: ({layout_center_x}, {layout_center_y})")
    
    # Shift the entire middle column (API-2 and DB-2) to the right
    print("\n4. Shifting middle column (API-2 + DB-2) 50 pixels to the right...")
    api2 = diagram.shapes[api2_id]
    old_x = api2.x
    api2.x += 50
    
    # Move bound database
    for bound_id in api2.bound_nodes:
        diagram.shapes[bound_id].x += 50
    
    print(f"   {api2_id} moved from x={old_x} to x={api2.x}")
    print(f"   {db2_id} also moved (bound to {api2_id})")
    
    # Save the diagram
    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "combined_demo.drawio"
        output_file.write_text(diagram.to_drawio_xml())
        print(f"\n✓ Saved to: {output_file}")
    
    print("\n5. Use case summary:")
    print("   - Coordinate system helped analyze the layout structure")
    print("   - Node binding kept each API-DB pair together during reorganization")
    print("   - This enables intelligent diagram layout management by LLMs")
    
    return diagram


if __name__ == "__main__":
    print("\n" + "🎨" * 35)
    print("MCP Draw.io Server - Coordinate System & Node Binding Demo")
    print("🎨" * 35)
    
    demo_coordinate_system()
    demo_node_binding()
    demo_combined_features()
    
    print("\n" + "=" * 70)
    print("✓ All demos completed successfully!")
    print("=" * 70)
    print("\nKey takeaways:")
    print("1. Coordinate system provides detailed spatial information")
    print("2. Node binding enables grouped movement of related elements")
    print("3. Combined, these features enable sophisticated diagram management")
    print("\nThese features help LLMs:")
    print("- Better understand diagram layout and spatial relationships")
    print("- Maintain structural integrity when reorganizing diagrams")
    print("- Make intelligent decisions about element placement")
    print("=" * 70 + "\n")
