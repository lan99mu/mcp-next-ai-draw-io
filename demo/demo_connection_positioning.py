#!/usr/bin/env python3
"""
Demonstration of Connection Positioning Features

This script shows how to use entry/exit points, waypoints, and all connection
positioning features available in the MCP Draw.io Server.
"""

import tempfile
from pathlib import Path
from mcp_drawio_server import Diagram


def demo_entry_exit_points():
    """Demonstrate entry and exit point control"""
    print("=" * 70)
    print("DEMO: Entry and Exit Points")
    print("=" * 70)
    print()
    
    diagram = Diagram(name="Entry Exit Points Demo")
    
    # Create a grid of nodes
    print("Creating a 2x2 grid of nodes...")
    node_a = diagram.add_shape("Node A", x=100, y=100, width=100, height=60)
    node_b = diagram.add_shape("Node B", x=300, y=100, width=100, height=60)
    node_c = diagram.add_shape("Node C", x=100, y=250, width=100, height=60)
    node_d = diagram.add_shape("Node D", x=300, y=250, width=100, height=60)
    
    # Connection 1: Exit from right (1.0, 0.5), enter from left (0.0, 0.5)
    print("\n1. Horizontal connection (right to left):")
    diagram.add_connection(
        node_a, node_b,
        label="Right → Left",
        exit_x=1.0, exit_y=0.5,    # Exit right center
        entry_x=0.0, entry_y=0.5   # Enter left center
    )
    print("   Exit: Right center (1.0, 0.5)")
    print("   Entry: Left center (0.0, 0.5)")
    
    # Connection 2: Exit from bottom (0.5, 1.0), enter from top (0.5, 0.0)
    print("\n2. Vertical connection (bottom to top):")
    diagram.add_connection(
        node_a, node_c,
        label="Bottom ↓ Top",
        exit_x=0.5, exit_y=1.0,    # Exit bottom center
        entry_x=0.5, entry_y=0.0   # Enter top center
    )
    print("   Exit: Bottom center (0.5, 1.0)")
    print("   Entry: Top center (0.5, 0.0)")
    
    # Connection 3: Exit from bottom-right corner, enter at top-left
    print("\n3. Diagonal connection (corner to corner):")
    diagram.add_connection(
        node_b, node_c,
        label="Corner to Corner",
        exit_x=0.0, exit_y=1.0,    # Exit bottom-left
        entry_x=1.0, entry_y=0.0   # Enter top-right
    )
    print("   Exit: Bottom-left corner (0.0, 1.0)")
    print("   Entry: Top-right corner (1.0, 0.0)")
    
    # Save diagram
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "entry_exit_demo.drawio"
        filepath.write_text(diagram.to_drawio_xml(), encoding='utf-8')
        print(f"\n✓ Saved to: {filepath}")
    
    print("\nEntry/Exit Point Reference:")
    print("  X-axis: 0.0 = left, 0.5 = center, 1.0 = right")
    print("  Y-axis: 0.0 = top, 0.5 = center, 1.0 = bottom")
    
    return diagram


def demo_waypoint_routing():
    """Demonstrate waypoint-based routing"""
    print("\n" + "=" * 70)
    print("DEMO: Waypoint Routing")
    print("=" * 70)
    print()
    
    diagram = Diagram(name="Waypoint Routing Demo")
    
    # Create nodes
    print("Creating nodes for routing demo...")
    start = diagram.add_shape("Start", x=100, y=100, width=100, height=60)
    end = diagram.add_shape("End", x=500, y=300, width=100, height=60)
    
    # Connection 1: Simple L-shaped path with one waypoint
    print("\n1. L-shaped path (1 waypoint):")
    diagram.add_connection(
        start, end,
        label="L-Path",
        waypoints=[(150, 330)]
    )
    print("   Waypoint at (150, 330)")
    
    # Connection 2: S-shaped path with multiple waypoints
    obstacle1 = diagram.add_shape("Obstacle", x=250, y=150, width=80, height=80)
    target2 = diagram.add_shape("Target", x=500, y=100, width=100, height=60)
    
    print("\n2. S-shaped path around obstacle (3 waypoints):")
    diagram.add_connection(
        start, target2,
        label="S-Path",
        waypoints=[
            (200, 130),  # First turn
            (200, 90),   # Around obstacle
            (450, 90)    # Approach target
        ]
    )
    print("   Waypoint 1: (200, 130)")
    print("   Waypoint 2: (200, 90)")
    print("   Waypoint 3: (450, 90)")
    
    # Connection 3: Complex zigzag path
    start3 = diagram.add_shape("Complex Start", x=100, y=400, width=100, height=60)
    end3 = diagram.add_shape("Complex End", x=500, y=400, width=100, height=60)
    
    print("\n3. Zigzag path (4 waypoints):")
    diagram.add_connection(
        start3, end3,
        label="Zigzag",
        waypoints=[
            (250, 380),
            (250, 440),
            (400, 440),
            (400, 380)
        ]
    )
    print("   Creating a zigzag pattern with 4 waypoints")
    
    # Save diagram
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "waypoint_demo.drawio"
        filepath.write_text(diagram.to_drawio_xml(), encoding='utf-8')
        print(f"\n✓ Saved to: {filepath}")
    
    print("\nWaypoint Tips:")
    print("  • Use waypoints to route around obstacles")
    print("  • Coordinates are in absolute pixels")
    print("  • Multiple waypoints create complex paths")
    
    return diagram


def demo_combined_features():
    """Demonstrate combining all connection features"""
    print("\n" + "=" * 70)
    print("DEMO: Combined Connection Features")
    print("=" * 70)
    print()
    
    diagram = Diagram(name="Combined Features Demo")
    
    # Create a microservices architecture
    print("Creating a microservices architecture diagram...")
    
    # API Gateway
    gateway = diagram.add_shape("API Gateway", x=250, y=50, width=120, height=60)
    
    # Services
    auth = diagram.add_shape("Auth Service", x=100, y=200, width=100, height=60)
    user = diagram.add_shape("User Service", x=250, y=200, width=100, height=60)
    order = diagram.add_shape("Order Service", x=400, y=200, width=100, height=60)
    
    # Databases
    auth_db = diagram.add_shape("Auth DB", x=100, y=350, width=80, height=50)
    user_db = diagram.add_shape("User DB", x=250, y=350, width=80, height=50)
    order_db = diagram.add_shape("Order DB", x=400, y=350, width=80, height=50)
    
    print("\n1. Gateway to services with entry/exit control:")
    # Gateway to Auth - exit from bottom-left, enter at top-center
    diagram.add_connection(
        gateway, auth,
        label="Auth",
        exit_x=0.25, exit_y=1.0,
        entry_x=0.5, entry_y=0.0,
        label_position="left"
    )
    
    # Gateway to User - straight down
    diagram.add_connection(
        gateway, user,
        label="User",
        exit_x=0.5, exit_y=1.0,
        entry_x=0.5, entry_y=0.0,
        label_position="center",
        label_background_color="#e3f2fd"
    )
    
    # Gateway to Order - exit from bottom-right, enter at top-center
    diagram.add_connection(
        gateway, order,
        label="Order",
        exit_x=0.75, exit_y=1.0,
        entry_x=0.5, entry_y=0.0,
        label_position="right"
    )
    
    print("   ✓ Fan-out from gateway with precise entry/exit points")
    
    print("\n2. Services to databases with waypoints:")
    # Auth to Auth DB with slight offset
    diagram.add_connection(
        auth, auth_db,
        label="Persist",
        waypoints=[(140, 300)],
        label_offset_x=10,
        label_offset_y=-5
    )
    
    # User to User DB - straight line
    diagram.add_connection(
        user, user_db,
        label="Store",
        exit_x=0.5, exit_y=1.0,
        entry_x=0.5, entry_y=0.0
    )
    
    # Order to Order DB with offset
    diagram.add_connection(
        order, order_db,
        label="Save",
        waypoints=[(440, 300)],
        label_offset_x=-10,
        label_offset_y=-5
    )
    
    print("   ✓ Service-to-database connections with waypoints")
    
    print("\n3. Cross-service communication:")
    # Auth to User - horizontal with waypoints and styling
    diagram.add_connection(
        auth, user,
        label="Verify",
        exit_x=1.0, exit_y=0.5,
        entry_x=0.0, entry_y=0.5,
        label_position="center",
        label_background_color="#fff3e0",
        label_offset_y=10
    )
    
    print("   ✓ Cross-service with all features combined")
    
    # Save diagram
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "combined_demo.drawio"
        filepath.write_text(diagram.to_drawio_xml(), encoding='utf-8')
        print(f"\n✓ Saved to: {filepath}")
    
    print("\nFeatures Demonstrated:")
    print("  ✓ Entry/exit points for precise attachment")
    print("  ✓ Waypoints for custom routing")
    print("  ✓ Label positioning and styling")
    print("  ✓ Combined features working together")
    
    return diagram


def demo_real_world_scenarios():
    """Demonstrate real-world use cases"""
    print("\n" + "=" * 70)
    print("DEMO: Real-World Scenarios")
    print("=" * 70)
    print()
    
    diagram = Diagram(name="Real World Demo")
    
    print("Scenario: Network Topology Diagram")
    print()
    
    # Router in center
    router = diagram.add_shape("Router", x=250, y=200, width=100, height=80)
    
    # Devices around the router
    laptop = diagram.add_shape("Laptop", x=100, y=100, width=80, height=60)
    desktop = diagram.add_shape("Desktop", x=400, y=100, width=80, height=60)
    server = diagram.add_shape("Server", x=100, y=320, width=80, height=60)
    printer = diagram.add_shape("Printer", x=400, y=320, width=80, height=60)
    
    print("1. Star topology with controlled entry/exit points:")
    
    # Laptop to Router - from bottom-right to top-left
    diagram.add_connection(
        laptop, router,
        label="WiFi",
        exit_x=1.0, exit_y=1.0,
        entry_x=0.0, entry_y=0.0,
        label_position="center",
        label_background_color="#e8f5e9"
    )
    
    # Desktop to Router - from bottom-left to top-right
    diagram.add_connection(
        desktop, router,
        label="Ethernet",
        exit_x=0.0, exit_y=1.0,
        entry_x=1.0, entry_y=0.0,
        label_position="center",
        label_background_color="#e3f2fd"
    )
    
    # Server to Router - from top-right to bottom-left
    diagram.add_connection(
        server, router,
        label="Gigabit",
        exit_x=1.0, exit_y=0.0,
        entry_x=0.0, entry_y=1.0,
        label_position="center",
        label_background_color="#fff3e0"
    )
    
    # Printer to Router - from top-left to bottom-right
    diagram.add_connection(
        printer, router,
        label="USB",
        exit_x=0.0, exit_y=0.0,
        entry_x=1.0, entry_y=1.0,
        label_position="center",
        label_background_color="#fce4ec"
    )
    
    print("   ✓ All devices connect from corners to create clean star pattern")
    
    # Internet connection with waypoint
    internet = diagram.add_shape("Internet", x=250, y=50, width=100, height=40)
    diagram.add_connection(
        internet, router,
        label="WAN",
        exit_x=0.5, exit_y=1.0,
        entry_x=0.5, entry_y=0.0,
        label_position="right",
        label_background_color="#ffebee"
    )
    
    print("   ✓ WAN connection from top")
    
    # Save diagram
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "network_topology.drawio"
        filepath.write_text(diagram.to_drawio_xml(), encoding='utf-8')
        print(f"\n✓ Saved to: {filepath}")
    
    print("\nReal-World Benefits:")
    print("  • Clean, professional diagrams")
    print("  • Precise control over connection routing")
    print("  • Better visual clarity")
    print("  • Matches industry-standard network diagrams")
    
    return diagram


if __name__ == "__main__":
    print("\n" + "🎨" * 35)
    print("MCP Draw.io Server - Connection Positioning Demo")
    print("🎨" * 35)
    print()
    
    demo_entry_exit_points()
    demo_waypoint_routing()
    demo_combined_features()
    demo_real_world_scenarios()
    
    print("\n" + "=" * 70)
    print("✓ All demos completed successfully!")
    print("=" * 70)
    print("\nKey Takeaways:")
    print()
    print("1. Entry/Exit Points (normalized 0-1):")
    print("   • Control where connections attach to shapes")
    print("   • exitX, exitY for source shape")
    print("   • entryX, entryY for target shape")
    print()
    print("2. Waypoints (absolute pixels):")
    print("   • Create custom routing paths")
    print("   • Route around obstacles")
    print("   • Build complex connection patterns")
    print()
    print("3. Combined with Label Positioning:")
    print("   • Complete control over connection appearance")
    print("   • Professional, clean diagrams")
    print("   • Industry-standard visual quality")
    print()
    print("These features enable LLMs to create:")
    print("  ✓ Professional network diagrams")
    print("  ✓ Complex system architectures")
    print("  ✓ Clean flowcharts with precise routing")
    print("  ✓ Industry-standard technical diagrams")
    print("=" * 70 + "\n")
