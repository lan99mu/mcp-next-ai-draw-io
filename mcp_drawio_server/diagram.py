"""
Diagram class for managing Draw.io diagram structures.

This module provides the Diagram class which manages shapes, connections,
and generates Draw.io XML format.
"""

import re
from typing import Optional
from datetime import datetime, timezone
from .models import Shape, Connection, UMLSection


# Text size calculation constants
CHAR_WIDTH_RATIO = 0.6  # Approximate character width as ratio of font size
LINE_HEIGHT_RATIO = 1.4  # Line height as ratio of font size

# UML diagram constants
UML_SECTION_SEPARATOR = "───────"  # Unicode box drawing for UML section dividers
HTML_LINE_BREAK_RE = re.compile(r"<br\s*/?>", re.IGNORECASE)


def _format_number(value: float) -> str:
    """
    Format a number for XML output, using int format if it's a whole number.
    
    Args:
        value: A numeric value (int or float)
        
    Returns:
        String representation without decimal point for whole numbers,
        otherwise standard float representation
        
    Examples:
        _format_number(250.0) -> "250"
        _format_number(250.5) -> "250.5"
        _format_number(250) -> "250"
    """
    if isinstance(value, (int, float)) and value == int(value):
        return str(int(value))
    return str(value)


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
        style: str = "",
        parent_id: Optional[str] = None,
        dashed: bool = False,
        rounded: bool = False,
        stroke_width: Optional[float] = None,
        fill_color: Optional[str] = None,
        stroke_color: Optional[str] = None,
        font_size: Optional[int] = None,
        font_color: Optional[str] = None,
        opacity: Optional[float] = None,
        overflow: str = "hidden",
        auto_size: bool = False
    ) -> str:
        """Add a shape to the diagram
        
        Args:
            label: Text label for the shape
            x, y: Position coordinates
            width, height: Dimensions (can be auto-calculated if auto_size=True)
            shape_type: Type of shape (rectangle, ellipse, uml_class, etc.)
            style: Custom Draw.io style string (overrides other style options)
            parent_id: ID of parent container/swimlane
            dashed: Whether to use dashed border
            rounded: Whether to use rounded corners
            stroke_width: Border thickness
            fill_color: Background color (e.g., "#ffffff")
            stroke_color: Border color (e.g., "#000000")
            font_size: Text font size
            font_color: Text color
            opacity: Opacity (0-100)
            overflow: Text overflow behavior ("hidden", "visible", "fill")
            auto_size: If True, auto-calculate width/height based on label text
        
        Returns:
            The ID of the created shape
        """
        shape_id = f"shape_{self.next_id}"
        self.next_id += 1
        
        # Check if this is a UML class type that needs section parsing
        uml_class_types = ('uml_class', 'uml_interface', 'uml_abstract_class', 'uml_enum')
        uml_sections = []
        normalized_label = self._normalize_uml_label(label) if shape_type in uml_class_types else label
        class_name = normalized_label
        
        # Use regex to check for any UML separator:
        # - Box-drawing horizontal lines (3+ ─ characters): ───────
        # - Pipe separators for GraphViz/Mermaid-style labels: |
        has_uml_separator = shape_type in uml_class_types and (
            re.search(r'─{3,}', normalized_label) or 
            re.search(r'\|', normalized_label)
        )
        
        if has_uml_separator:
            # Parse the label to extract class name, attributes, and methods
            class_name, uml_sections, calculated_height = self._parse_uml_label(
                normalized_label, width, self.next_id
            )
            # Update next_id to account for generated section IDs
            self.next_id += len(uml_sections)
            
            # Use calculated height if not using default
            if height == 60:
                height = calculated_height
        elif shape_type == "uml_class":
            uml_sections, calculated_height = self._create_default_uml_sections(self.next_id)
            self.next_id += len(uml_sections)
            if height == 60:
                height = calculated_height
        
        # Auto-calculate size if requested (for non-UML or simple UML shapes)
        if auto_size and label and not uml_sections:
            calculated_width, calculated_height = self._calculate_text_size(
                label, shape_type, font_size or 12
            )
            if width == 120:  # Only override if using default
                width = max(width, calculated_width)
            if height == 60:  # Only override if using default
                height = max(height, calculated_height)
        
        self.shapes[shape_id] = Shape(
            id=shape_id,
            label=class_name,
            x=x,
            y=y,
            width=width,
            height=height,
            shape_type=shape_type,
            style=style,
            parent_id=parent_id,
            dashed=dashed,
            rounded=rounded,
            stroke_width=stroke_width,
            fill_color=fill_color,
            stroke_color=stroke_color,
            font_size=font_size,
            font_color=font_color,
            opacity=opacity,
            overflow=overflow,
            uml_sections=uml_sections
        )
        return shape_id
    
    def _parse_uml_label(self, label: str, width: float, start_id: int) -> tuple[str, list, float]:
        """Parse a UML class label and create proper sections.
        
        Supports multiple formats:
        1. Box-drawing style: "Name\\n───────\\n- attr: type"
        2. GraphViz/Mermaid pipe style: "Name|+ attr: type\\\\l|+ method()"
           - Uses | as section separator
           - Uses \\l as line break within sections
        3. HTML line breaks: "Name<br>───────<br>- attr: type"
         
        Args:
            label: The full label with sections separated by horizontal lines or pipes
            width: Width of the shape
            start_id: Starting ID number for sections
            
        Returns:
            Tuple of (class_name, list of UMLSection objects, calculated_height)
        """
        # Constants for UML class layout
        HEADER_HEIGHT = 26
        LINE_HEIGHT = 26
        DIVIDER_HEIGHT = 8
        
        normalized_label = self._normalize_uml_label(label)
        
        # Determine which separator to use:
        # 1. First check for box-drawing horizontal lines (─)
        # 2. Then check for pipe separators (|)
        if re.search(r'─{3,}', normalized_label):
            # Use box-drawing style separator
            parts = re.split(r'─{3,}', normalized_label)
        elif '|' in normalized_label:
            # Use pipe-style separator (GraphViz/Mermaid format)
            parts = normalized_label.split('|')
        else:
            # No recognizable separator
            return label, [], 60
        
        parts = [p.strip() for p in parts if p.strip()]
        
        if len(parts) == 0:
            return label, [], 60
        
        # First part is always the class name
        class_name = parts[0]
        
        # Remaining parts are attribute/method sections
        sections = []
        total_height = HEADER_HEIGHT
        section_id = start_id
        
        for i, part in enumerate(parts[1:]):
            # Clean up the content - remove any remaining line characters
            # and filter out empty lines
            lines = [l.strip() for l in part.split('\n') if l.strip() and not re.match(r'^─+$', l.strip())]
            clean_content = '\n'.join(lines)
            
            if not clean_content:
                continue
                
            # Calculate section height based on number of lines
            section_height = max(len(lines) * LINE_HEIGHT, LINE_HEIGHT)
            
            # Add divider before this section (except for the first section after name)
            if i > 0:
                divider_section = UMLSection(
                    id=f"section_{section_id}",
                    content="",
                    height=DIVIDER_HEIGHT,
                    section_type="line"
                )
                sections.append(divider_section)
                section_id += 1
                total_height += DIVIDER_HEIGHT
            
            # Add text section
            text_section = UMLSection(
                id=f"section_{section_id}",
                content=clean_content,
                height=section_height,
                section_type="text"
            )
            sections.append(text_section)
            section_id += 1
            total_height += section_height
        
        return class_name, sections, total_height

    def _create_default_uml_sections(self, start_id: int) -> tuple[list[UMLSection], float]:
        """Create the default attribute and method compartments for a UML class."""
        header_height = 26
        line_height = 26
        divider_height = 8

        sections = [
            UMLSection(
                id=f"section_{start_id}",
                content="",
                height=line_height,
                section_type="text"
            ),
            UMLSection(
                id=f"section_{start_id + 1}",
                content="",
                height=divider_height,
                section_type="line"
            ),
            UMLSection(
                id=f"section_{start_id + 2}",
                content="",
                height=line_height,
                section_type="text"
            ),
        ]
        return sections, header_height + line_height + divider_height + line_height
    
    @staticmethod
    def _calculate_text_size(label: str, shape_type: str, font_size: int = 12) -> tuple[float, float]:
        """Calculate recommended width and height based on text content.
        
        Args:
            label: The text label
            shape_type: Type of shape (affects padding calculations)
            font_size: Font size in pixels
            
        Returns:
            Tuple of (width, height)
        """
        lines = HTML_LINE_BREAK_RE.sub('\n', label).split('\n')
        max_line_length = max(len(line) for line in lines) if lines else 0
        num_lines = len(lines)
        
        # Calculate character dimensions using constants
        char_width = font_size * CHAR_WIDTH_RATIO
        line_height = font_size * LINE_HEIGHT_RATIO
        
        # Base padding (varies by shape type)
        padding_h = 20
        padding_v = 20
        
        if shape_type in ('uml_class', 'uml_interface', 'uml_abstract_class', 'uml_enum'):
            # UML classes need header space
            padding_v = 30
            padding_h = 15
        elif shape_type == 'uml_package':
            padding_v = 40  # Extra space for folder tab
        
        width = max(max_line_length * char_width + padding_h * 2, 80)
        height = max(num_lines * line_height + padding_v * 2, 40)
        
        return (round(width), round(height))
    
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
        label_background_color: Optional[str] = None,
        entry_x: Optional[float] = None,
        entry_y: Optional[float] = None,
        exit_x: Optional[float] = None,
        exit_y: Optional[float] = None,
        waypoints: Optional[list[tuple[float, float]]] = None,
        source_point: Optional[tuple[float, float]] = None,
        target_point: Optional[tuple[float, float]] = None,
        edge_style: str = "orthogonal",
        dashed: bool = False,
        rounded: bool = False,
        stroke_width: Optional[float] = None,
        stroke_color: Optional[str] = None,
        start_arrow: Optional[str] = None,
        end_arrow: Optional[str] = None
    ) -> str:
        """Add a connection between two shapes.
        
        Args:
            source_id: ID of the source shape
            target_id: ID of the target shape
            label: Connection label text
            arrow_type: Arrow type at the end (classic, block, open, oval, diamond, none)
            style: Custom Draw.io style string (overrides other style options)
            label_position: Label position (left, right, center)
            label_offset_x, label_offset_y: Label offset in pixels
            label_background_color: Background color for label
            entry_x, entry_y: Entry point on target (normalized 0-1)
            exit_x, exit_y: Exit point on source (normalized 0-1)
            waypoints: List of intermediate routing points as (x, y) tuples
            source_point, target_point: Explicit source/target points
            edge_style: Edge routing style ("orthogonal", "straight", "curved", "entity_relation")
            dashed: Whether to use dashed line
            rounded: Whether to use rounded corners for orthogonal edges
            stroke_width: Line thickness
            stroke_color: Line color (e.g., "#000000")
            start_arrow: Arrow at start (overrides default "none")
            end_arrow: Arrow at end (alternative to arrow_type)
            
        Returns:
            The ID of the created connection
        """
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
            label_background_color=label_background_color,
            entry_x=entry_x,
            entry_y=entry_y,
            exit_x=exit_x,
            exit_y=exit_y,
            waypoints=waypoints or [],
            source_point=source_point,
            target_point=target_point,
            edge_style=edge_style,
            dashed=dashed,
            rounded=rounded,
            stroke_width=stroke_width,
            stroke_color=stroke_color,
            start_arrow=start_arrow,
            end_arrow=end_arrow
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
            style = self._build_shape_style(shape)
            
            # Add bound_nodes as a custom attribute if present
            bound_attr = ""
            if shape.bound_nodes:
                # Encode bound nodes as a comma-separated list in a custom attribute
                bound_attr = f' bound_nodes="{",".join(shape.bound_nodes)}"'
            
            # Determine parent
            parent_id = shape.parent_id if shape.parent_id else "1"
            is_uml_class_type = shape.shape_type in ('uml_class', 'uml_interface', 'uml_abstract_class', 'uml_enum')
            shape_value = self._format_html_label(shape.label) if is_uml_class_type else self._escape_xml(shape.label)
            
            xml_parts.append(
                f'        <mxCell id="{shape.id}" value="{shape_value}" '
                f'style="{style}" vertex="1" parent="{parent_id}"{bound_attr}>'
            )
            xml_parts.append(
                f'          <mxGeometry x="{shape.x}" y="{shape.y}" '
                f'width="{shape.width}" height="{shape.height}" as="geometry"/>'
            )
            xml_parts.append('        </mxCell>')
            
            # Add UML class child sections if present
            if shape.uml_sections:
                current_y = 26  # Start after header (26px header height)
                for section in shape.uml_sections:
                    if section.section_type == "text":
                        # Text section for attributes or methods
                        text_style = "text;strokeColor=none;fillColor=none;align=left;verticalAlign=top;spacingLeft=4;spacingRight=4;overflow=hidden;rotatable=0;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;whiteSpace=wrap;html=1;"
                        section_value = self._format_html_label(section.content)
                        xml_parts.append(
                            f'        <mxCell id="{section.id}" value="{section_value}" '
                            f'style="{text_style}" vertex="1" parent="{shape.id}">'
                        )
                        xml_parts.append(
                            f'          <mxGeometry y="{current_y}" width="{shape.width}" height="{section.height}" as="geometry"/>'
                        )
                        xml_parts.append('        </mxCell>')
                    elif section.section_type == "line":
                        # Divider line
                        line_style = "line;strokeWidth=1;fillColor=none;align=left;verticalAlign=middle;spacingTop=-1;spacingLeft=3;spacingRight=3;rotatable=0;labelPosition=right;points=[];portConstraint=eastwest;strokeColor=inherit;"
                        xml_parts.append(
                            f'        <mxCell id="{section.id}" value="" '
                            f'style="{line_style}" vertex="1" parent="{shape.id}">'
                        )
                        xml_parts.append(
                            f'          <mxGeometry y="{current_y}" width="{shape.width}" height="{section.height}" as="geometry"/>'
                        )
                        xml_parts.append('        </mxCell>')
                    current_y += section.height
        
        # Add connections
        for conn in self.connections.values():
            style = self._build_connection_style(conn)
            
            xml_parts.append(
                f'        <mxCell id="{conn.id}" value="{self._escape_xml(conn.label)}" '
                f'style="{style}" edge="1" parent="1" source="{conn.source_id}" target="{conn.target_id}">'
            )
            
            # Build geometry with entry/exit points, waypoints, and offsets
            geometry_attrs = ['relative="1"', 'as="geometry"']
            
            # Add entry/exit points as attributes if specified
            if conn.entry_x is not None:
                geometry_attrs.append(f'entryX="{conn.entry_x}"')
            if conn.entry_y is not None:
                geometry_attrs.append(f'entryY="{conn.entry_y}"')
            if conn.exit_x is not None:
                geometry_attrs.append(f'exitX="{conn.exit_x}"')
            if conn.exit_y is not None:
                geometry_attrs.append(f'exitY="{conn.exit_y}"')
            
            geometry_line = f'          <mxGeometry {" ".join(geometry_attrs)}>'
            xml_parts.append(geometry_line)
            
            # Add source point if specified
            if conn.source_point is not None:
                xml_parts.append(f'            <mxPoint x="{_format_number(conn.source_point[0])}" y="{_format_number(conn.source_point[1])}" as="sourcePoint"/>')
            
            # Add target point if specified
            if conn.target_point is not None:
                xml_parts.append(f'            <mxPoint x="{_format_number(conn.target_point[0])}" y="{_format_number(conn.target_point[1])}" as="targetPoint"/>')
            
            # Add waypoints if specified
            if conn.waypoints:
                xml_parts.append('            <Array as="points">')
                for waypoint in conn.waypoints:
                    xml_parts.append(f'              <mxPoint x="{_format_number(waypoint[0])}" y="{_format_number(waypoint[1])}"/>')
                xml_parts.append('            </Array>')
            
            # Add label offset if specified
            if conn.label_offset_x is not None or conn.label_offset_y is not None:
                offset_x = conn.label_offset_x if conn.label_offset_x is not None else 0
                offset_y = conn.label_offset_y if conn.label_offset_y is not None else 0
                xml_parts.append(f'            <mxPoint x="{_format_number(offset_x)}" y="{_format_number(offset_y)}" as="offset"/>')
            
            xml_parts.append('          </mxGeometry>')
            xml_parts.append('        </mxCell>')
        
        xml_parts.append('      </root>')
        xml_parts.append('    </mxGraphModel>')
        xml_parts.append('  </diagram>')
        xml_parts.append('</mxfile>')
        
        return '\n'.join(xml_parts)
    
    def _build_shape_style(self, shape) -> str:
        """Build the style string for a shape, applying style options."""
        # If custom style is provided, use it as base
        if shape.style:
            style = shape.style
        else:
            style = self._get_default_style(shape.shape_type)
        
        # Apply style options (only if not using custom style)
        if not shape.style:
            style_parts = []
            
            # Apply dashed border
            if shape.dashed:
                style_parts.append("dashed=1")
            
            # Apply rounded corners
            if shape.rounded:
                style_parts.append("rounded=1")
            
            # Apply stroke width
            if shape.stroke_width is not None:
                style_parts.append(f"strokeWidth={shape.stroke_width}")
            
            # Apply fill color
            if shape.fill_color:
                style_parts.append(f"fillColor={shape.fill_color}")
            
            # Apply stroke color
            if shape.stroke_color:
                style_parts.append(f"strokeColor={shape.stroke_color}")
            
            # Apply font size
            if shape.font_size is not None:
                style_parts.append(f"fontSize={shape.font_size}")
            
            # Apply font color
            if shape.font_color:
                style_parts.append(f"fontColor={shape.font_color}")
            
            # Apply opacity
            if shape.opacity is not None:
                style_parts.append(f"opacity={shape.opacity}")
            
            # Apply text overflow
            if shape.overflow and shape.overflow != "hidden":
                style_parts.append(f"overflow={shape.overflow}")
            
            # Append style parts to existing style
            if style_parts:
                style += ";" + ";".join(style_parts)
                if not style.endswith(";"):
                    style += ";"
        
        return style
    
    def _build_connection_style(self, conn) -> str:
        """Build the style string for a connection, applying style options."""
        # If custom style is provided, use it
        if conn.style:
            style = conn.style
        else:
            # Build edge style based on edge_style parameter
            edge_style_map = {
                "orthogonal": "edgeStyle=orthogonalEdgeStyle;orthogonalLoop=1;jettySize=auto;",
                "straight": "edgeStyle=none;",
                "curved": "edgeStyle=orthogonalEdgeStyle;curved=1;",
                "entity_relation": "edgeStyle=entityRelationEdgeStyle;",
            }
            
            base_style = edge_style_map.get(conn.edge_style, edge_style_map["orthogonal"])
            style = f"{base_style}html=1;"
            
            # Apply rounded corners for orthogonal
            if conn.rounded:
                style += "rounded=1;"
            else:
                style += "rounded=0;"
            
            # Apply arrow types
            start_arrow = conn.start_arrow or "none"
            end_arrow = conn.end_arrow if conn.end_arrow else conn.arrow_type
            style += f"startArrow={start_arrow};endArrow={end_arrow};"
            
            # Apply dashed line
            if conn.dashed:
                style += "dashed=1;"
            
            # Apply stroke width
            if conn.stroke_width is not None:
                style += f"strokeWidth={conn.stroke_width};"
            
            # Apply stroke color
            if conn.stroke_color:
                style += f"strokeColor={conn.stroke_color};"
        
        # Add label position to style if specified (applies to both custom and generated)
        if conn.label_position:
            style += f"labelPosition={conn.label_position};"
        
        # Add label background color to style if specified
        if conn.label_background_color:
            style += f"labelBackgroundColor={conn.label_background_color};"
        
        return style
    
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
    def _normalize_uml_label(label: str) -> str:
        """Normalize UML labels so HTML and GraphViz line breaks parse consistently."""
        normalized = HTML_LINE_BREAK_RE.sub('\n', label)
        return re.sub(r'\\+l', '\n', normalized)

    @staticmethod
    def _format_html_label(text: str) -> str:
        """Format label text as escaped HTML with <br> line breaks."""
        normalized = HTML_LINE_BREAK_RE.sub('<br>', text).replace('\n', '<br>')
        return Diagram._escape_xml(normalized)
    
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
            
            # UML Class Diagram shapes
            "uml_class": "swimlane;fontStyle=1;align=center;verticalAlign=top;childLayout=stackLayout;horizontal=1;startSize=26;horizontalStack=0;resizeParent=1;resizeParentMax=0;resizeLast=0;collapsible=1;marginBottom=0;whiteSpace=wrap;html=1;",
            "uml_interface": "swimlane;fontStyle=2;align=center;verticalAlign=top;childLayout=stackLayout;horizontal=1;startSize=26;horizontalStack=0;resizeParent=1;resizeParentMax=0;resizeLast=0;collapsible=1;marginBottom=0;whiteSpace=wrap;html=1;",
            "uml_abstract_class": "swimlane;fontStyle=3;align=center;verticalAlign=top;childLayout=stackLayout;horizontal=1;startSize=26;horizontalStack=0;resizeParent=1;resizeParentMax=0;resizeLast=0;collapsible=1;marginBottom=0;whiteSpace=wrap;html=1;",
            "uml_enum": "swimlane;fontStyle=1;align=center;verticalAlign=top;childLayout=stackLayout;horizontal=1;startSize=26;horizontalStack=0;resizeParent=1;resizeParentMax=0;resizeLast=0;collapsible=1;marginBottom=0;whiteSpace=wrap;html=1;",
            "uml_package": "shape=folder;fontStyle=1;tabWidth=110;tabHeight=30;tabPosition=left;html=1;boundedLbl=1;labelInHeader=1;whiteSpace=wrap;",
            "uml_note": "shape=note;whiteSpace=wrap;html=1;backgroundOutline=1;darkOpacity=0.05;size=15;",
        }
        return styles.get(shape_type, styles["rectangle"])
    
    def add_uml_class(
        self,
        name: str,
        attributes: list[str] = None,
        methods: list[str] = None,
        x: float = 0,
        y: float = 0,
        width: float = 160,
        height: Optional[float] = None,
        class_type: str = "class",
        auto_bind: bool = True
    ) -> dict[str, str]:
        """Add a UML class with proper sections, auto-sized and auto-bound.
        
        This creates a UML class diagram box with properly formatted sections
        for name, attributes, and methods using nested child elements for proper
        Draw.io rendering. The height is auto-calculated based on content.
        
        Args:
            name: Class name (e.g., "User", "«interface»\\nIService")
            attributes: List of attribute strings (e.g., ["- id: int", "+ name: string"])
            methods: List of method strings (e.g., ["+ login()", "+ logout()"])
            x, y: Position coordinates
            width: Width of the class box (default: 160)
            height: Height (auto-calculated if not provided)
            class_type: Type of UML class ("class", "interface", "abstract", "enum")
            auto_bind: Whether to bind the class parts together (default: True)
            
        Returns:
            Dictionary with keys 'class_id' for the main shape ID and 'section_ids' 
            for the child element IDs
        """
        attributes = attributes or []
        methods = methods or []
        
        # Map class_type to shape_type
        shape_type_map = {
            "class": "uml_class",
            "interface": "uml_interface",
            "abstract": "uml_abstract_class",
            "enum": "uml_enum"
        }
        shape_type = shape_type_map.get(class_type, "uml_class")
        
        # Constants for UML class layout
        HEADER_HEIGHT = 26
        LINE_HEIGHT = 26  # Height per text line
        DIVIDER_HEIGHT = 8  # Height for divider lines
        
        # Calculate section heights
        attr_height = max(len(attributes) * LINE_HEIGHT, LINE_HEIGHT) if attributes else 0
        method_height = max(len(methods) * LINE_HEIGHT, LINE_HEIGHT) if methods else 0
        
        # Calculate total height
        if height is None:
            height = HEADER_HEIGHT
            if attributes:
                height += attr_height + DIVIDER_HEIGHT
            if methods:
                height += method_height
                if not attributes:
                    height += DIVIDER_HEIGHT
        
        # Create UML sections list
        uml_sections = []
        current_y = HEADER_HEIGHT
        
        # Attributes section
        if attributes:
            attr_content = "\n".join(attributes)
            attr_section_id = f"section_{self.next_id}"
            self.next_id += 1
            uml_sections.append(UMLSection(
                id=attr_section_id,
                content=attr_content,
                height=attr_height,
                section_type="text"
            ))
            current_y += attr_height
            
            # Divider after attributes (if there are methods)
            if methods:
                divider_id = f"section_{self.next_id}"
                self.next_id += 1
                uml_sections.append(UMLSection(
                    id=divider_id,
                    content="",
                    height=DIVIDER_HEIGHT,
                    section_type="line"
                ))
                current_y += DIVIDER_HEIGHT
        elif methods:
            # Divider before methods (if no attributes)
            divider_id = f"section_{self.next_id}"
            self.next_id += 1
            uml_sections.append(UMLSection(
                id=divider_id,
                content="",
                height=DIVIDER_HEIGHT,
                section_type="line"
            ))
            current_y += DIVIDER_HEIGHT
        
        # Methods section
        if methods:
            method_content = "\n".join(methods)
            method_section_id = f"section_{self.next_id}"
            self.next_id += 1
            uml_sections.append(UMLSection(
                id=method_section_id,
                content=method_content,
                height=method_height,
                section_type="text"
            ))
        
        # Create the main class shape (header only shows name)
        shape_id = f"shape_{self.next_id}"
        self.next_id += 1
        
        self.shapes[shape_id] = Shape(
            id=shape_id,
            label=name,
            x=x,
            y=y,
            width=width,
            height=height,
            shape_type=shape_type,
            uml_sections=uml_sections
        )
        
        section_ids = [s.id for s in uml_sections]
        
        return {"class_id": shape_id, "section_ids": section_ids}
    
    def add_swimlane_pool(
        self,
        name: str,
        lanes: list[str],
        x: float = 0,
        y: float = 0,
        pool_width: float = 800,
        lane_height: float = 200,
        horizontal: bool = True
    ) -> dict[str, str]:
        """Add a swimlane pool with multiple lanes.
        
        Creates a swimlane pool container with the specified lanes. All lanes
        are automatically bound together for easy repositioning.
        
        Args:
            name: Name of the pool
            lanes: List of lane names
            x, y: Position of the pool
            pool_width: Total width of the pool
            lane_height: Height of each lane
            horizontal: If True, lanes are horizontal (stacked vertically)
            
        Returns:
            Dictionary with 'pool_id' and 'lane_ids' list
        """
        pool_height = lane_height * len(lanes) + 30  # 30 for header
        
        # Create pool container
        pool_id = self.add_shape(
            label=name,
            x=x,
            y=y,
            width=pool_width,
            height=pool_height,
            shape_type="swimlane_pool"
        )
        
        # Create lanes
        lane_ids = []
        lane_y_offset = 30  # After pool header
        
        for i, lane_name in enumerate(lanes):
            lane_shape_type = "swimlane_h" if horizontal else "swimlane_v"
            lane_id = self.add_shape(
                label=lane_name,
                x=0,  # Relative to pool
                y=lane_y_offset + (i * lane_height),
                width=pool_width,
                height=lane_height,
                shape_type=lane_shape_type,
                parent_id=pool_id
            )
            lane_ids.append(lane_id)
        
        # Bind all lanes together with the pool
        all_ids = [pool_id] + lane_ids
        for i, shape_id in enumerate(all_ids):
            other_ids = [sid for sid in all_ids if sid != shape_id]
            self.shapes[shape_id].bound_nodes = list(
                set(self.shapes[shape_id].bound_nodes + other_ids)
            )
        
        return {"pool_id": pool_id, "lane_ids": lane_ids}
    
    def bind_shapes(self, shape_ids: list[str]) -> None:
        """Bind multiple shapes together so they move as a group.
        
        Args:
            shape_ids: List of shape IDs to bind together
        """
        for shape_id in shape_ids:
            if shape_id not in self.shapes:
                continue
            other_ids = [sid for sid in shape_ids if sid != shape_id]
            self.shapes[shape_id].bound_nodes = list(
                set(self.shapes[shape_id].bound_nodes + other_ids)
            )
