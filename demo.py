#!/usr/bin/env python3
"""
Demo script showing how an AI assistant would use the MCP Draw.io server
This simulates the MCP tool calls to create a sample diagram
"""

from mcp_drawio_server import Diagram


def demo_create_flowchart():
    """Demo: Create a simple login flowchart"""
    print("=" * 70)
    print("DEMO: Creating a User Login Flowchart")
    print("=" * 70)
    
    # Simulate: create_diagram tool call
    print("\n1. AI calls create_diagram(name='User Login Flow')")
    diagram = Diagram(name="User Login Flow")
    print("   ✓ Created new diagram")
    
    # Simulate: add_shape tool calls
    print("\n2. AI calls add_shape multiple times to add flowchart steps:")
    
    print("   - Adding 'Start' (ellipse) at (200, 50)")
    start_id = diagram.add_shape("Start", x=200, y=50, width=100, height=40, shape_type="ellipse")
    
    print("   - Adding 'Enter Credentials' (parallelogram) at (200, 130)")
    input_id = diagram.add_shape("Enter Credentials", x=150, y=130, width=200, height=60, 
                                  shape_type="parallelogram")
    
    print("   - Adding 'Validate Credentials' (diamond) at (200, 230)")
    validate_id = diagram.add_shape("Validate\nCredentials?", x=165, y=230, width=150, height=90, 
                                     shape_type="diamond")
    
    print("   - Adding 'Dashboard' (rectangle) at (350, 360)")
    dashboard_id = diagram.add_shape("Go to\nDashboard", x=320, y=360, width=120, height=60)
    
    print("   - Adding 'Show Error' (rectangle) at (50, 360)")
    error_id = diagram.add_shape("Show Error\nMessage", x=20, y=360, width=120, height=60)
    
    print("   - Adding 'End' (ellipse) at (200, 460)")
    end_id = diagram.add_shape("End", x=200, y=460, width=100, height=40, shape_type="ellipse")
    
    # Simulate: add_connection tool calls
    print("\n3. AI calls add_connection to link the shapes:")
    
    print("   - Connecting Start → Enter Credentials")
    diagram.add_connection(start_id, input_id)
    
    print("   - Connecting Enter Credentials → Validate")
    diagram.add_connection(input_id, validate_id)
    
    print("   - Connecting Validate → Dashboard (labeled 'Valid')")
    diagram.add_connection(validate_id, dashboard_id, label="Valid")
    
    print("   - Connecting Validate → Show Error (labeled 'Invalid')")
    diagram.add_connection(validate_id, error_id, label="Invalid")
    
    print("   - Connecting Dashboard → End")
    diagram.add_connection(dashboard_id, end_id)
    
    print("   - Connecting Show Error → End")
    diagram.add_connection(error_id, end_id)
    
    # Simulate: get_diagram tool call
    print("\n4. AI calls get_diagram to retrieve the XML:")
    xml = diagram.to_drawio_xml()
    
    print(f"   ✓ Generated {len(xml)} bytes of Draw.io XML")
    print(f"   ✓ Diagram contains {len(diagram.shapes)} shapes and {len(diagram.connections)} connections")
    
    # Show XML preview
    print("\n5. AI returns the XML to the user (first 500 characters):")
    print("   " + "-" * 66)
    for line in xml.split('\n')[:15]:
        print(f"   {line}")
    print("   ...")
    print("   " + "-" * 66)
    
    print("\n6. User saves the output to 'login_flow.drawio' and opens it in Draw.io")
    print("   The diagram is now visible and can be edited!")
    
    return xml


def demo_system_architecture():
    """Demo: Create a system architecture diagram"""
    print("\n\n" + "=" * 70)
    print("DEMO: Creating a System Architecture Diagram")
    print("=" * 70)
    
    print("\n1. AI creates diagram and adds components:")
    diagram = Diagram(name="E-commerce System Architecture")
    
    # Add components
    client = diagram.add_shape("Web Browser\n(Client)", x=250, y=50, width=140, height=70)
    print("   ✓ Added Web Browser")
    
    lb = diagram.add_shape("Load Balancer", x=250, y=160, width=140, height=60)
    print("   ✓ Added Load Balancer")
    
    api1 = diagram.add_shape("API Server 1", x=80, y=280, width=120, height=60)
    api2 = diagram.add_shape("API Server 2", x=260, y=280, width=120, height=60)
    api3 = diagram.add_shape("API Server 3", x=440, y=280, width=120, height=60)
    print("   ✓ Added 3 API Servers")
    
    cache = diagram.add_shape("Redis\nCache", x=500, y=160, width=100, height=80, 
                              shape_type="cylinder")
    print("   ✓ Added Redis Cache")
    
    db = diagram.add_shape("PostgreSQL\nDatabase", x=250, y=400, width=140, height=90, 
                          shape_type="cylinder")
    print("   ✓ Added Database")
    
    print("\n2. AI connects the components:")
    diagram.add_connection(client, lb, label="HTTPS")
    diagram.add_connection(lb, api1)
    diagram.add_connection(lb, api2)
    diagram.add_connection(lb, api3)
    diagram.add_connection(api1, db, label="SQL")
    diagram.add_connection(api2, db, label="SQL")
    diagram.add_connection(api3, db, label="SQL")
    diagram.add_connection(api2, cache, label="Cache")
    print(f"   ✓ Added {len(diagram.connections)} connections")
    
    xml = diagram.to_drawio_xml()
    print(f"\n3. ✓ Generated complete architecture diagram ({len(xml)} bytes)")
    
    return xml


if __name__ == "__main__":
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "MCP Draw.io Server - Interactive Demo" + " " * 15 + "║")
    print("╚" + "═" * 68 + "╝")
    
    print("\nThis demo shows how an AI assistant (like GitHub Copilot) would")
    print("interact with the MCP Draw.io server to create diagrams.\n")
    
    # Demo 1
    xml1 = demo_create_flowchart()
    
    # Demo 2
    xml2 = demo_system_architecture()
    
    print("\n\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("""
The MCP Draw.io server enables AI assistants to:
  ✓ Create diagrams programmatically through natural language
  ✓ Add various shape types (rectangles, diamonds, cylinders, etc.)
  ✓ Connect shapes with labeled arrows
  ✓ Generate standard Draw.io XML that can be opened in:
    - VS Code with Draw.io extension
    - Draw.io desktop application
    - https://app.diagrams.net/

Key advantage: AI can now generate visual diagrams, not just text!
    """)
    print("=" * 70)
