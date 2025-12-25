#!/usr/bin/env python3
"""
MCP Draw.io Server

A Model Context Protocol (MCP) server that provides tools for creating and 
manipulating Draw.io diagrams. This server can be used with VS Code Copilot 
and the Draw.io plugin to generate diagrams programmatically.
"""

import asyncio
import json
import base64
from datetime import datetime, timezone
from typing import Any, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from pydantic import BaseModel, Field


class DiagramElement(BaseModel):
    """Base class for diagram elements"""
    id: str
    label: str = ""
    style: str = ""


class Shape(DiagramElement):
    """Represents a shape/node in the diagram"""
    x: float = 0
    y: float = 0
    width: float = 120
    height: float = 60
    shape_type: str = "rectangle"


class Connection(DiagramElement):
    """Represents a connection/edge between shapes"""
    source_id: str
    target_id: str
    arrow_type: str = "classic"


class Diagram:
    """Manages a Draw.io diagram structure"""
    
    def __init__(self, name: str = "Untitled"):
        self.name = name
        self.shapes: dict[str, Shape] = {}
        self.connections: dict[str, Connection] = {}
        self.next_id = 1
        
    def add_shape(
        self, 
        label: str, 
        x: float = 0, 
        y: float = 0,
        width: float = 120,
        height: float = 60,
        shape_type: str = "rectangle",
        style: str = ""
    ) -> str:
        """Add a shape to the diagram"""
        shape_id = f"shape_{self.next_id}"
        self.next_id += 1
        
        self.shapes[shape_id] = Shape(
            id=shape_id,
            label=label,
            x=x,
            y=y,
            width=width,
            height=height,
            shape_type=shape_type,
            style=style
        )
        return shape_id
    
    def add_connection(
        self,
        source_id: str,
        target_id: str,
        label: str = "",
        arrow_type: str = "classic",
        style: str = ""
    ) -> str:
        """Add a connection between two shapes"""
        if source_id not in self.shapes or target_id not in self.shapes:
            raise ValueError("Source or target shape not found")
            
        conn_id = f"conn_{self.next_id}"
        self.next_id += 1
        
        self.connections[conn_id] = Connection(
            id=conn_id,
            label=label,
            source_id=source_id,
            target_id=target_id,
            arrow_type=arrow_type,
            style=style
        )
        return conn_id
    
    def to_drawio_xml(self) -> str:
        """Convert diagram to Draw.io XML format"""
        timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        xml_parts = [f'<mxfile host="MCP Draw.io Server" modified="{timestamp}" version="1.0.0">']
        xml_parts.append('  <diagram name="{}" id="diagram1">'.format(self.name))
        xml_parts.append('    <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" math="0" shadow="0">')
        xml_parts.append('      <root>')
        xml_parts.append('        <mxCell id="0"/>')
        xml_parts.append('        <mxCell id="1" parent="0"/>')
        
        # Add shapes
        for shape in self.shapes.values():
            style = shape.style or self._get_default_style(shape.shape_type)
            xml_parts.append(
                f'        <mxCell id="{shape.id}" value="{self._escape_xml(shape.label)}" '
                f'style="{style}" vertex="1" parent="1">'
            )
            xml_parts.append(
                f'          <mxGeometry x="{shape.x}" y="{shape.y}" '
                f'width="{shape.width}" height="{shape.height}" as="geometry"/>'
            )
            xml_parts.append('        </mxCell>')
        
        # Add connections
        for conn in self.connections.values():
            style = conn.style or f"edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow={conn.arrow_type};"
            xml_parts.append(
                f'        <mxCell id="{conn.id}" value="{self._escape_xml(conn.label)}" '
                f'style="{style}" edge="1" parent="1" source="{conn.source_id}" target="{conn.target_id}">'
            )
            xml_parts.append('          <mxGeometry relative="1" as="geometry"/>')
            xml_parts.append('        </mxCell>')
        
        xml_parts.append('      </root>')
        xml_parts.append('    </mxGraphModel>')
        xml_parts.append('  </diagram>')
        xml_parts.append('</mxfile>')
        
        return '\n'.join(xml_parts)
    
    @staticmethod
    def _escape_xml(text: str) -> str:
        """Escape special XML characters"""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&apos;'))
    
    @staticmethod
    def _get_default_style(shape_type: str) -> str:
        """Get default style for a shape type"""
        styles = {
            "rectangle": "rounded=0;whiteSpace=wrap;html=1;",
            "ellipse": "ellipse;whiteSpace=wrap;html=1;",
            "diamond": "rhombus;whiteSpace=wrap;html=1;",
            "parallelogram": "shape=parallelogram;perimeter=parallelogramPerimeter;whiteSpace=wrap;html=1;",
            "hexagon": "shape=hexagon;perimeter=hexagonPerimeter2;whiteSpace=wrap;html=1;",
            "cylinder": "shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;",
            "cloud": "ellipse;shape=cloud;whiteSpace=wrap;html=1;",
        }
        return styles.get(shape_type, styles["rectangle"])


# Global diagram storage
current_diagram: Optional[Diagram] = None


def get_or_create_diagram() -> Diagram:
    """Get or create the current diagram"""
    global current_diagram
    if current_diagram is None:
        current_diagram = Diagram()
    return current_diagram


# Initialize MCP server
app = Server("mcp-drawio-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="create_diagram",
            description="Create a new Draw.io diagram. This will reset any existing diagram.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the diagram",
                        "default": "Untitled"
                    }
                }
            }
        ),
        Tool(
            name="add_shape",
            description="Add a shape/node to the diagram. Supported shape types: rectangle, ellipse, diamond, parallelogram, hexagon, cylinder, cloud.",
            inputSchema={
                "type": "object",
                "properties": {
                    "label": {
                        "type": "string",
                        "description": "Label text for the shape"
                    },
                    "x": {
                        "type": "number",
                        "description": "X coordinate (default: 0)",
                        "default": 0
                    },
                    "y": {
                        "type": "number",
                        "description": "Y coordinate (default: 0)",
                        "default": 0
                    },
                    "width": {
                        "type": "number",
                        "description": "Width of the shape (default: 120)",
                        "default": 120
                    },
                    "height": {
                        "type": "number",
                        "description": "Height of the shape (default: 60)",
                        "default": 60
                    },
                    "shape_type": {
                        "type": "string",
                        "description": "Type of shape (default: rectangle)",
                        "enum": ["rectangle", "ellipse", "diamond", "parallelogram", "hexagon", "cylinder", "cloud"],
                        "default": "rectangle"
                    },
                    "style": {
                        "type": "string",
                        "description": "Custom Draw.io style string (optional)",
                        "default": ""
                    }
                },
                "required": ["label"]
            }
        ),
        Tool(
            name="add_connection",
            description="Add a connection/edge between two shapes in the diagram.",
            inputSchema={
                "type": "object",
                "properties": {
                    "source_id": {
                        "type": "string",
                        "description": "ID of the source shape"
                    },
                    "target_id": {
                        "type": "string",
                        "description": "ID of the target shape"
                    },
                    "label": {
                        "type": "string",
                        "description": "Label text for the connection (optional)",
                        "default": ""
                    },
                    "arrow_type": {
                        "type": "string",
                        "description": "Arrow type (default: classic)",
                        "enum": ["classic", "block", "open", "oval", "diamond", "none"],
                        "default": "classic"
                    },
                    "style": {
                        "type": "string",
                        "description": "Custom Draw.io style string (optional)",
                        "default": ""
                    }
                },
                "required": ["source_id", "target_id"]
            }
        ),
        Tool(
            name="get_diagram",
            description="Get the current diagram as Draw.io XML format. This can be saved to a .drawio file and opened in Draw.io.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="list_shapes",
            description="List all shapes currently in the diagram with their IDs and labels.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    global current_diagram
    
    if name == "create_diagram":
        diagram_name = arguments.get("name", "Untitled")
        current_diagram = Diagram(name=diagram_name)
        return [TextContent(
            type="text",
            text=f"Created new diagram: {diagram_name}"
        )]
    
    elif name == "add_shape":
        diagram = get_or_create_diagram()
        shape_id = diagram.add_shape(
            label=arguments["label"],
            x=arguments.get("x", 0),
            y=arguments.get("y", 0),
            width=arguments.get("width", 120),
            height=arguments.get("height", 60),
            shape_type=arguments.get("shape_type", "rectangle"),
            style=arguments.get("style", "")
        )
        return [TextContent(
            type="text",
            text=f"Added shape '{arguments['label']}' with ID: {shape_id}"
        )]
    
    elif name == "add_connection":
        diagram = get_or_create_diagram()
        try:
            conn_id = diagram.add_connection(
                source_id=arguments["source_id"],
                target_id=arguments["target_id"],
                label=arguments.get("label", ""),
                arrow_type=arguments.get("arrow_type", "classic"),
                style=arguments.get("style", "")
            )
            return [TextContent(
                type="text",
                text=f"Added connection from {arguments['source_id']} to {arguments['target_id']} with ID: {conn_id}"
            )]
        except ValueError as e:
            return [TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )]
    
    elif name == "get_diagram":
        diagram = get_or_create_diagram()
        xml_content = diagram.to_drawio_xml()
        return [TextContent(
            type="text",
            text=f"Draw.io XML:\n\n{xml_content}\n\nYou can save this to a .drawio file and open it in Draw.io or VS Code with the Draw.io extension."
        )]
    
    elif name == "list_shapes":
        diagram = get_or_create_diagram()
        if not diagram.shapes:
            return [TextContent(
                type="text",
                text="No shapes in the diagram yet."
            )]
        
        shapes_list = []
        for shape in diagram.shapes.values():
            shapes_list.append(
                f"- {shape.id}: '{shape.label}' ({shape.shape_type}) at ({shape.x}, {shape.y})"
            )
        
        return [TextContent(
            type="text",
            text="Shapes in diagram:\n" + "\n".join(shapes_list)
        )]
    
    else:
        return [TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]


async def main():
    """Main entry point for the server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
