#!/usr/bin/env python3
"""
MCP Draw.io Server

A Model Context Protocol (MCP) server that provides tools for creating and 
manipulating Draw.io diagrams with real-time browser preview.

This enhanced version includes:
- Real-time browser preview via embedded HTTP server
- Diagram editing with ID-based operations
- Version history tracking
- Export to .drawio files
"""

import asyncio
import json
import os
from datetime import datetime, timezone
from typing import Any, Optional, List, Dict
from pathlib import Path
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from pydantic import BaseModel, Field

# Import new modules
from http_server import start_http_server, get_state, set_state
from diagram_operations import apply_diagram_operations, DiagramOperation, extract_cells_info
from history import add_history, get_history, get_history_count


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


# Global diagram storage and session state
current_diagram: Optional[Diagram] = None
current_session: Optional[Dict[str, Any]] = None


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
            name="start_session",
            description="Start a new diagram session with real-time browser preview. Opens a browser window that will show diagram updates in real-time. This should be called first before creating or editing diagrams.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="create_diagram",
            description="Create a new Draw.io diagram. This will reset any existing diagram and display it in the browser (if session is started).",
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
            name="display_diagram",
            description="Display the current diagram in the browser. This pushes the diagram XML to the browser for real-time preview. Use this after adding shapes and connections.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="edit_diagram",
            description="Edit an existing diagram using ID-based operations (update/add/delete cells). You should call get_diagram first to see current cell IDs. Operations: 'update' (replace existing cell), 'add' (add new cell), 'delete' (remove cell).",
            inputSchema={
                "type": "object",
                "properties": {
                    "operations": {
                        "type": "array",
                        "description": "Array of operations to apply",
                        "items": {
                            "type": "object",
                            "properties": {
                                "operation": {
                                    "type": "string",
                                    "enum": ["update", "add", "delete"],
                                    "description": "Operation type"
                                },
                                "cell_id": {
                                    "type": "string",
                                    "description": "The ID of the cell to operate on"
                                },
                                "new_xml": {
                                    "type": "string",
                                    "description": "Complete mxCell XML element (required for update/add)"
                                }
                            },
                            "required": ["operation", "cell_id"]
                        }
                    }
                },
                "required": ["operations"]
            }
        ),
        Tool(
            name="get_diagram",
            description="Get the current diagram as Draw.io XML format. This fetches the latest state from the browser if a session is active.",
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
        ),
        Tool(
            name="export_diagram",
            description="Export the current diagram to a .drawio file on disk.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path to save the diagram (e.g., ./diagram.drawio)"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="get_history",
            description="Get the version history for the current session. Shows how many versions are saved.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    global current_diagram, current_session
    
    if name == "start_session":
        try:
            # Start embedded HTTP server
            port = start_http_server(6002)
            
            # Create session
            import random
            import time
            session_id = f"mcp-{int(time.time()*1000):x}-{random.randint(0, 0xffffff):06x}"
            current_session = {
                'id': session_id,
                'port': port
            }
            
            # Open browser
            import webbrowser
            browser_url = f"http://localhost:{port}?mcp={session_id}"
            webbrowser.open(browser_url)
            
            return [TextContent(
                type="text",
                text=f"Session started successfully!\n\nSession ID: {session_id}\nBrowser URL: {browser_url}\n\nThe browser will now show real-time diagram updates. You can now create or edit diagrams."
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error starting session: {str(e)}"
            )]
    
    elif name == "create_diagram":
        diagram_name = arguments.get("name", "Untitled")
        current_diagram = Diagram(name=diagram_name)
        return [TextContent(
            type="text",
            text=f"Created new diagram: {diagram_name}\n\nYou can now add shapes and connections. Use display_diagram to show it in the browser."
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
    
    elif name == "display_diagram":
        diagram = get_or_create_diagram()
        xml_content = diagram.to_drawio_xml()
        
        # If we have a session, push to browser
        if current_session:
            session_id = current_session['id']
            
            # Save current state to history before updating
            browser_state = get_state(session_id)
            if browser_state and browser_state.get('xml'):
                add_history(session_id, browser_state['xml'], browser_state.get('svg', ''))
            
            # Update browser state
            set_state(session_id, xml_content)
            
            # Add new state to history
            add_history(session_id, xml_content)
            
            return [TextContent(
                type="text",
                text=f"Diagram displayed in browser!\n\nThe diagram is now visible in your browser window.\n\nXML length: {len(xml_content)} characters\nShapes: {len(diagram.shapes)}\nConnections: {len(diagram.connections)}"
            )]
        else:
            return [TextContent(
                type="text",
                text=f"Diagram XML generated:\n\n{xml_content}\n\nNote: No active browser session. Call start_session first for real-time preview, or save this XML to a .drawio file."
            )]
    
    elif name == "edit_diagram":
        if not current_session:
            return [TextContent(
                type="text",
                text="Error: No active session. Please call start_session first."
            )]
        
        session_id = current_session['id']
        
        # Get current state from browser
        browser_state = get_state(session_id)
        if not browser_state or not browser_state.get('xml'):
            return [TextContent(
                type="text",
                text="Error: No diagram to edit. Please create a diagram first with display_diagram."
            )]
        
        current_xml = browser_state['xml']
        
        # Save state before editing
        add_history(session_id, current_xml, browser_state.get('svg', ''))
        
        # Parse operations
        ops_data = arguments.get("operations", [])
        operations = [
            DiagramOperation(
                operation=op.get("operation"),
                cell_id=op.get("cell_id"),
                new_xml=op.get("new_xml")
            )
            for op in ops_data
        ]
        
        # Apply operations
        result = apply_diagram_operations(current_xml, operations)
        errors = result.get('errors', [])
        new_xml = result.get('result', current_xml)
        
        # Update state
        set_state(session_id, new_xml)
        add_history(session_id, new_xml)
        
        # Build response
        success_msg = f"Diagram edited successfully!\n\nApplied {len(operations)} operation(s)."
        error_msg = ""
        if errors:
            error_list = "\n".join([f"- {e.type} {e.cell_id}: {e.message}" for e in errors])
            error_msg = f"\n\nWarnings:\n{error_list}"
        
        return [TextContent(
            type="text",
            text=success_msg + error_msg
        )]
    
    elif name == "get_diagram":
        # Try to get from browser first if we have a session
        if current_session:
            session_id = current_session['id']
            browser_state = get_state(session_id)
            if browser_state and browser_state.get('xml'):
                xml_content = browser_state['xml']
                
                # Extract cell info for easier editing
                cells = extract_cells_info(xml_content)
                cells_summary = "\n".join([
                    f"  - ID: {c['id']}, Label: {c.get('value', 'N/A')}, Type: {'edge' if c.get('edge') else 'vertex'}"
                    for c in cells[:20]  # Show first 20
                ])
                if len(cells) > 20:
                    cells_summary += f"\n  ... and {len(cells) - 20} more cells"
                
                return [TextContent(
                    type="text",
                    text=f"Current diagram XML:\n\n{xml_content}\n\n--- Cell Summary ({len(cells)} cells) ---\n{cells_summary}"
                )]
        
        # Fallback to current diagram
        diagram = get_or_create_diagram()
        xml_content = diagram.to_drawio_xml()
        return [TextContent(
            type="text",
            text=f"Current diagram XML:\n\n{xml_content}\n\nYou can save this to a .drawio file and open it in Draw.io or VS Code with the Draw.io extension."
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
    
    elif name == "export_diagram":
        export_path = arguments.get("path", "diagram.drawio")
        
        # Get XML content
        xml_content = None
        if current_session:
            session_id = current_session['id']
            browser_state = get_state(session_id)
            if browser_state and browser_state.get('xml'):
                xml_content = browser_state['xml']
        
        if not xml_content:
            diagram = get_or_create_diagram()
            xml_content = diagram.to_drawio_xml()
        
        # Ensure .drawio extension
        if not export_path.endswith('.drawio'):
            export_path += '.drawio'
        
        # Write to file
        try:
            file_path = Path(export_path).resolve()
            file_path.write_text(xml_content, encoding='utf-8')
            
            return [TextContent(
                type="text",
                text=f"Diagram exported successfully!\n\nFile: {file_path}\nSize: {len(xml_content)} characters"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error exporting diagram: {str(e)}"
            )]
    
    elif name == "get_history":
        if not current_session:
            return [TextContent(
                type="text",
                text="No active session. History is only available for browser sessions."
            )]
        
        session_id = current_session['id']
        count = get_history_count(session_id)
        
        if count == 0:
            return [TextContent(
                type="text",
                text="No history available yet. History is saved each time you display or edit the diagram."
            )]
        
        return [TextContent(
            type="text",
            text=f"History: {count} version(s) saved for this session.\n\nYou can restore previous versions by manually copying earlier XML from get_diagram calls."
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
