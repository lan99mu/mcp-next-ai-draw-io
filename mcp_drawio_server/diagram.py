"""
Diagram class for managing Draw.io diagram structures.

This module provides the Diagram class which manages shapes, connections,
and generates Draw.io XML format.
"""

from typing import Optional
from datetime import datetime, timezone
from .models import Shape, Connection


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
        style: str = "",
        label_position: Optional[str] = None,
        label_offset_x: Optional[float] = None,
        label_offset_y: Optional[float] = None,
        label_background_color: Optional[str] = None
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
            style=style,
            label_position=label_position,
            label_offset_x=label_offset_x,
            label_offset_y=label_offset_y,
            label_background_color=label_background_color
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
            # Build style string with label positioning
            if conn.style:
                style = conn.style
            else:
                style = f"edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow={conn.arrow_type};"
            
            # Add label position to style if specified
            if conn.label_position:
                style += f"labelPosition={conn.label_position};"
            
            # Add label background color to style if specified
            if conn.label_background_color:
                style += f"labelBackgroundColor={conn.label_background_color};"
            
            xml_parts.append(
                f'        <mxCell id="{conn.id}" value="{self._escape_xml(conn.label)}" '
                f'style="{style}" edge="1" parent="1" source="{conn.source_id}" target="{conn.target_id}">'
            )
            
            # Add geometry with label offset if specified
            if conn.label_offset_x is not None or conn.label_offset_y is not None:
                offset_x = conn.label_offset_x if conn.label_offset_x is not None else 0
                offset_y = conn.label_offset_y if conn.label_offset_y is not None else 0
                xml_parts.append(f'          <mxGeometry relative="1" as="geometry">')
                xml_parts.append(f'            <mxPoint x="{offset_x}" y="{offset_y}" as="offset"/>')
                xml_parts.append('          </mxGeometry>')
            else:
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
            # Basic shapes
            "rectangle": "rounded=0;whiteSpace=wrap;html=1;",
            "ellipse": "ellipse;whiteSpace=wrap;html=1;",
            "diamond": "rhombus;whiteSpace=wrap;html=1;",
            "parallelogram": "shape=parallelogram;perimeter=parallelogramPerimeter;whiteSpace=wrap;html=1;",
            "hexagon": "shape=hexagon;perimeter=hexagonPerimeter2;whiteSpace=wrap;html=1;",
            "cylinder": "shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;",
            "cloud": "ellipse;shape=cloud;whiteSpace=wrap;html=1;",
            
            # Activity diagram shapes
            "activity_start": "ellipse;whiteSpace=wrap;html=1;fillColor=#000000;",
            "activity_end": "ellipse;whiteSpace=wrap;html=1;fillColor=#000000;strokeWidth=3;",
            "activity_action": "rounded=1;whiteSpace=wrap;html=1;arcSize=40;",
            "activity_decision": "rhombus;whiteSpace=wrap;html=1;",
            "activity_fork": "shape=line;strokeWidth=4;html=1;",
            "activity_join": "shape=line;strokeWidth=4;html=1;",
            "activity_send_signal": "shape=message;whiteSpace=wrap;html=1;outlineConnect=0;",
            "activity_receive_signal": "shape=message;whiteSpace=wrap;html=1;outlineConnect=0;",
            "activity_note": "shape=note;whiteSpace=wrap;html=1;backgroundOutline=1;size=15;",
            
            # Swimlane shapes
            "swimlane_pool": "swimlane;whiteSpace=wrap;html=1;",
            "swimlane_h": "swimlane;horizontal=0;whiteSpace=wrap;html=1;",
            "swimlane_v": "swimlane;horizontal=1;whiteSpace=wrap;html=1;",
            "container": "swimlane;whiteSpace=wrap;html=1;startSize=23;",
        }
        return styles.get(shape_type, styles["rectangle"])
