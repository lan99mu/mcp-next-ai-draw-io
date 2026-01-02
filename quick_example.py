#!/usr/bin/env python3
"""
Quick example demonstrating connection position control.
This shows how to use the feature requested in the issue.
"""

from mcp_drawio_server.diagram import Diagram

# Create a simple network diagram with position-controlled connections
diagram = Diagram(name="Network Topology Example")

# Create network components
router = diagram.add_shape("Router", x=300, y=100, width=120, height=60)
laptop1 = diagram.add_shape("Laptop 1", x=100, y=250, width=100, height=60)
laptop2 = diagram.add_shape("Laptop 2", x=300, y=250, width=100, height=60)
laptop3 = diagram.add_shape("Laptop 3", x=500, y=250, width=100, height=60)

# Example 1: Control where connections attach (entry/exit points)
# Connect laptop1 to router: exit from top-right, enter at bottom-left
conn1 = diagram.add_connection(
    laptop1, router,
    label="WiFi",
    exit_x=1.0,    # Exit from right side of laptop
    exit_y=0.0,    # Exit from top
    entry_x=0.0,   # Enter left side of router
    entry_y=1.0    # Enter at bottom
)
print(f"✓ Created connection with entry/exit points: {conn1}")

# Example 2: Control routing path (waypoints)
# Connect laptop2 to router with custom path
conn2 = diagram.add_connection(
    laptop2, router,
    label="Ethernet",
    waypoints=[
        (350, 200),  # Route through this point
    ]
)
print(f"✓ Created connection with waypoint: {conn2}")

# Example 3: Combine entry/exit + waypoints
# Connect laptop3 to router: exit from top-left, route around, enter bottom-right
conn3 = diagram.add_connection(
    laptop3, router,
    label="Cable",
    exit_x=0.0,    # Exit from left side of laptop3
    exit_y=0.0,    # Exit from top
    entry_x=1.0,   # Enter right side of router
    entry_y=1.0,   # Enter at bottom
    waypoints=[
        (480, 200),  # First turn
        (420, 200),  # Second turn
    ]
)
print(f"✓ Created connection with entry/exit + waypoints: {conn3}")

# Save the diagram
xml = diagram.to_drawio_xml()
from pathlib import Path
import tempfile
output = Path(tempfile.gettempdir()) / "network_example.drawio"
output.write_text(xml, encoding='utf-8')

print(f"\n✓ Saved network diagram to: {output}")
print(f"✓ File size: {len(xml)} bytes")
print("\nThis demonstrates the feature: '传入位置来控制连线的位置'")
print("(pass in position to control connection line position)")
