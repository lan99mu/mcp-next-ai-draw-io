"""
Diagram class for managing Draw.io diagram structures.

This module provides the Diagram class which manages shapes, connections,
and generates Draw.io XML format.
"""

import html
import re
import unicodedata
from typing import Optional
from datetime import datetime, timezone
from .models import Shape, Connection, UMLSection


# Text size calculation constants
CHAR_WIDTH_RATIO = 0.6  # Approximate character width as ratio of font size
LINE_HEIGHT_RATIO = 1.4  # Line height as ratio of font size

# UML diagram constants
UML_SECTION_SEPARATOR = "───────"  # Unicode box drawing for UML section dividers
HTML_LINE_BREAK_RE = re.compile(r"<br\s*/?>", re.IGNORECASE)
HTML_BLOCK_BREAK_RE = re.compile(r"</(?:div|p|li|tr|h[1-6])\s*>|<(?:br|hr)\s*/?>", re.IGNORECASE)
HTML_TAG_RE = re.compile(r"<[^>]+>")
# Non-HTML line break markers that should be coerced into <br> so every label is
# rendered as HTML inside Draw.io (labels are expected to be HTML-style).
NON_HTML_LINE_BREAK_RE = re.compile(r"\\+[ln]")


# Label-size estimation constants (used to decide whether a connection label
# would overlap a node at its natural midpoint).
_LABEL_CHAR_WIDTH_ESTIMATE = 3.5   # px per character, averaged for mixed text
_LABEL_HORIZONTAL_PADDING = 6.0    # px on each side of the text block
_LABEL_LINE_HEIGHT = 7.0           # px per rendered line (half-height units)
_LABEL_MIN_HALF_WIDTH = 20.0       # floor so tiny labels still reserve space
_LABEL_MIN_HALF_HEIGHT = 8.0
_LABEL_CLEARANCE_MARGIN = 8.0      # px gap between label box and any node


def coerce_html_label(text: str) -> str:
    """Coerce a label into HTML-style by normalizing line breaks to ``<br>``.

    Draw.io labels emitted by this server are rendered with ``html=1`` so the
    expected input is HTML.  Users still occasionally pass plain-text or
    GraphViz/DOT-style labels (``\\n``, ``\\l``, raw newline); this helper
    converts all such variants into ``<br>`` so the rendered output is stable.
    """
    if not text:
        return text
    normalized = text.replace('\r\n', '\n').replace('\r', '\n')
    # Convert GraphViz ``\l`` / ``\n`` (literal backslash + letter) and actual
    # newline characters uniformly into HTML line breaks.
    normalized = NON_HTML_LINE_BREAK_RE.sub('<br>', normalized)
    normalized = normalized.replace('\n', '<br>')
    return normalized


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

        if shape_type in uml_class_types:
            width = max(
                width,
                self._calculate_uml_class_width(class_name, uml_sections, font_size or 12)
            )
        
        # Auto-calculate size if requested (for non-UML or simple UML shapes)
        if auto_size and label and not uml_sections:
            calculated_width, calculated_height = self._calculate_text_size(
                label, shape_type, font_size or 12
            )
            width = max(width, calculated_width)
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
        plain_text = Diagram._html_to_plain_text(label)
        lines = plain_text.split('\n') if plain_text else [""]
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

    @staticmethod
    def _text_visual_width(text: str) -> float:
        """Estimate visual width in character units (wide/full-width=2.0, others=1.0)."""
        width = 0.0
        for char in text:
            width += 2.0 if unicodedata.east_asian_width(char) in {"W", "F"} else 1.0
        return width

    @classmethod
    def _calculate_uml_class_width(
        cls,
        class_name: str,
        sections: list[UMLSection],
        font_size: int = 12
    ) -> float:
        """Calculate minimum UML class width to keep section text inside class bounds."""
        lines = []

        header = cls._html_to_plain_text(class_name)
        if header:
            lines.extend(header.split('\n'))

        for section in sections:
            if section.section_type != "text":
                continue
            content = cls._html_to_plain_text(section.content)
            if content:
                lines.extend(content.split('\n'))

        max_visual_width = max((cls._text_visual_width(line) for line in lines), default=0.0)
        char_width = font_size * CHAR_WIDTH_RATIO
        horizontal_padding = 18  # UML left/right spacing and divider margin
        return max(round(max_visual_width * char_width + horizontal_padding * 2), 120)
    
    def _shape_center(self, shape_id: str) -> tuple[float, float]:
        """Return (cx, cy) center of a shape."""
        s = self.shapes[shape_id]
        return (s.x + s.width / 2.0, s.y + s.height / 2.0)

    def _shape_abs_rect(self, shape_id: str) -> tuple[float, float, float, float]:
        """Return (x, y, w, h) of a shape, resolving the parent chain."""
        s = self.shapes.get(shape_id)
        if s is None:
            return (0.0, 0.0, 0.0, 0.0)
        x, y = float(s.x), float(s.y)
        parent_id = s.parent_id
        seen: set[str] = set()
        while parent_id and parent_id in self.shapes and parent_id not in seen:
            seen.add(parent_id)
            p = self.shapes[parent_id]
            x += float(p.x)
            y += float(p.y)
            parent_id = p.parent_id
        return (x, y, float(s.width), float(s.height))

    def _ancestors(self, shape_id: Optional[str]) -> list[str]:
        """Return [shape_id, parent, grandparent, ..., "1"] for the parent chain."""
        if not shape_id:
            return ["1"]
        chain: list[str] = [shape_id]
        seen: set[str] = {shape_id}
        current = self.shapes.get(shape_id)
        while current is not None and current.parent_id and current.parent_id not in seen:
            seen.add(current.parent_id)
            chain.append(current.parent_id)
            current = self.shapes.get(current.parent_id)
        if chain[-1] != "1":
            chain.append("1")
        return chain

    def _edge_parent_id(
        self,
        source_id: Optional[str],
        target_id: Optional[str],
    ) -> str:
        """Return the LCA (lowest-common-ancestor) parent ID for an edge.

        Draw.io expects an edge to live at or above the level of both its
        endpoints in the parent tree. Hoisting it to the LCA prevents weird
        z-order / grouping bugs when endpoints are nested inside different
        swimlanes or containers. Falls back to ``"1"`` (the graph root) when
        either endpoint is missing.
        """
        if not source_id or not target_id:
            return "1"
        if source_id not in self.shapes or target_id not in self.shapes:
            return "1"
        src_chain = self._ancestors(source_id)
        tgt_set = set(self._ancestors(target_id))
        for ancestor in src_chain:
            if ancestor in tgt_set:
                # Never put the edge inside one of its own endpoints; hoist
                # one level further so the edge isn't a child of a vertex
                # it connects to.
                if ancestor == source_id or ancestor == target_id:
                    continue
                return ancestor
        return "1"

    @staticmethod
    def _segment_intersects_rect(
        p1: tuple[float, float],
        p2: tuple[float, float],
        rect: tuple[float, float, float, float],
    ) -> bool:
        """Return True if segment p1→p2 passes through the rectangle interior."""
        rx, ry, rw, rh = rect
        if rw <= 0 or rh <= 0:
            return False

        # Fully inside → crosses.
        def inside(p):
            return rx < p[0] < rx + rw and ry < p[1] < ry + rh

        if inside(p1) or inside(p2):
            return True

        # Parametric clipping (Liang–Barsky style) for fast segment-vs-AABB.
        x1, y1 = p1
        x2, y2 = p2
        dx = x2 - x1
        dy = y2 - y1
        t_enter = 0.0
        t_exit = 1.0
        for p, q in ((-dx, x1 - rx), (dx, rx + rw - x1), (-dy, y1 - ry), (dy, ry + rh - y1)):
            if abs(p) < 1e-12:
                if q < 0:
                    return False
                continue
            t = q / p
            if p < 0:
                if t > t_exit:
                    return False
                if t > t_enter:
                    t_enter = t
            else:
                if t < t_enter:
                    return False
                if t < t_exit:
                    t_exit = t
        # Require the clipped segment to have non-zero length strictly inside.
        return t_exit - t_enter > 1e-9

    def _obstacle_ids(self, source_id: str, target_id: str) -> list[str]:
        """Return shape IDs that should be considered obstacles for a connection."""
        obstacles = []
        exclude = {source_id, target_id}
        # Exclude the source/target's parent chain so we don't try to route
        # around a container we're already inside.
        for sid in (source_id, target_id):
            s = self.shapes.get(sid)
            while s is not None and s.parent_id:
                exclude.add(s.parent_id)
                s = self.shapes.get(s.parent_id)
        for shape_id, shape in self.shapes.items():
            if shape_id in exclude:
                continue
            # Skip UML child sections: they live inside a parent class shape.
            if shape.parent_id and shape.parent_id in self.shapes:
                continue
            if shape.width <= 0 or shape.height <= 0:
                continue
            obstacles.append(shape_id)
        return obstacles

    def _first_blocking_obstacle(
        self,
        p1: tuple[float, float],
        p2: tuple[float, float],
        obstacle_rects: list[tuple[str, tuple[float, float, float, float]]],
    ) -> Optional[tuple[str, tuple[float, float, float, float]]]:
        """Return the first obstacle whose expanded bbox is crossed by segment p1→p2."""
        for shape_id, rect in obstacle_rects:
            if self._segment_intersects_rect(p1, p2, rect):
                return shape_id, rect
        return None

    def _count_path_intersections(
        self,
        path: list[tuple[float, float]],
        obstacle_rects: list[tuple[str, tuple[float, float, float, float]]],
    ) -> int:
        """Count how many (segment, obstacle) pairs intersect for a path."""
        count = 0
        for i in range(len(path) - 1):
            for _shape_id, rect in obstacle_rects:
                if self._segment_intersects_rect(path[i], path[i + 1], rect):
                    count += 1
        return count

    @staticmethod
    def _path_length(path: list[tuple[float, float]]) -> float:
        """Return the total length of a polyline path."""
        total = 0.0
        for i in range(len(path) - 1):
            dx = path[i + 1][0] - path[i][0]
            dy = path[i + 1][1] - path[i][1]
            total += (dx * dx + dy * dy) ** 0.5
        return total

    def _compute_auto_waypoints(
        self,
        source_id: str,
        target_id: str,
        margin: float = 20.0,
        max_iterations: int = 6,
    ) -> list[tuple[float, float]]:
        """Compute waypoints that route a connection around intervening shapes.

        Returns an empty list when a direct line between source and target
        centers does not cross any other shape's bounding box (expanded by
        ``margin``).  Otherwise iteratively inserts orthogonal detour
        waypoints around blocking obstacles.  For each blocker, four detour
        candidates (above / below / left / right) are simulated and the one
        introducing the fewest residual intersections (ties broken by
        shortest path length) is kept.  Iteration continues until the path
        is clear or ``max_iterations`` is reached.
        """
        if source_id not in self.shapes or target_id not in self.shapes:
            return []
        if source_id == target_id:
            return []

        sx_c, sy_c = self._shape_center(source_id)
        tx_c, ty_c = self._shape_center(target_id)
        if sx_c == tx_c and sy_c == ty_c:
            return []

        # Pre-compute expanded obstacle rects once.
        obstacle_rects: list[tuple[str, tuple[float, float, float, float]]] = []
        for shape_id in self._obstacle_ids(source_id, target_id):
            x, y, w, h = self._shape_abs_rect(shape_id)
            if w <= 0 or h <= 0:
                continue
            obstacle_rects.append(
                (shape_id, (x - margin, y - margin, w + 2 * margin, h + 2 * margin))
            )

        path: list[tuple[float, float]] = [(sx_c, sy_c), (tx_c, ty_c)]

        for _ in range(max_iterations):
            # Find the first segment that still crosses an obstacle.
            blocker_index = None
            blocker = None
            for i in range(len(path) - 1):
                b = self._first_blocking_obstacle(path[i], path[i + 1], obstacle_rects)
                if b is not None:
                    blocker_index = i
                    blocker = b
                    break
            if blocker is None:
                break

            seg_start = path[blocker_index]
            seg_end = path[blocker_index + 1]
            _obs_id, (ox, oy, ow, oh) = blocker

            # Candidate orthogonal detours: route the segment through two
            # waypoints so that the bypass follows axis-aligned segments.
            candidates: list[list[tuple[float, float]]] = []

            above_y = oy - 1
            below_y = oy + oh + 1
            left_x = ox - 1
            right_x = ox + ow + 1

            # Route above / below (waypoints share detour_y).
            for detour_y in (above_y, below_y):
                wp1 = (seg_start[0], detour_y)
                wp2 = (seg_end[0], detour_y)
                candidates.append([wp1, wp2])
            # Route left / right (waypoints share detour_x).
            for detour_x in (left_x, right_x):
                wp1 = (detour_x, seg_start[1])
                wp2 = (detour_x, seg_end[1])
                candidates.append([wp1, wp2])

            best_path: Optional[list[tuple[float, float]]] = None
            best_score: Optional[tuple[int, float]] = None
            for cand in candidates:
                # Drop degenerate waypoints (equal to segment endpoints).
                unique_wps = []
                for wp in cand:
                    if wp != seg_start and wp != seg_end and (not unique_wps or wp != unique_wps[-1]):
                        unique_wps.append(wp)
                if not unique_wps:
                    continue
                new_path = (
                    path[: blocker_index + 1] + unique_wps + path[blocker_index + 1:]
                )
                score = (
                    self._count_path_intersections(new_path, obstacle_rects),
                    self._path_length(new_path),
                )
                if best_score is None or score < best_score:
                    best_score = score
                    best_path = new_path

            if best_path is None:
                # No candidate improved things; bail out to avoid infinite loops.
                break
            path = best_path

        # Strip the synthetic source/target endpoints: the caller only wants
        # the interior waypoints.
        return path[1:-1]

    def _edge_label_anchor(
        self,
        source_id: str,
        target_id: str,
        waypoints: list[tuple[float, float]],
    ) -> Optional[tuple[float, float]]:
        """Approximate the (x, y) where Draw.io will anchor an edge label.

        Labels on `relative=1` edges default to the geometric midpoint of the
        routed polyline (source-anchor → waypoints → target-anchor).  This
        helper returns that midpoint so we can check whether it happens to
        land inside another shape.
        """
        if source_id not in self.shapes or target_id not in self.shapes:
            return None

        path: list[tuple[float, float]] = [self._shape_center(source_id)]
        for wp in waypoints:
            path.append((float(wp[0]), float(wp[1])))
        path.append(self._shape_center(target_id))

        # Total polyline length.
        total = 0.0
        seg_lengths: list[float] = []
        for i in range(len(path) - 1):
            dx = path[i + 1][0] - path[i][0]
            dy = path[i + 1][1] - path[i][1]
            length = (dx * dx + dy * dy) ** 0.5
            seg_lengths.append(length)
            total += length

        if total <= 0:
            return path[0]

        # Walk half the total length to find the midpoint.
        half = total / 2.0
        travelled = 0.0
        for i, length in enumerate(seg_lengths):
            if travelled + length >= half:
                t = (half - travelled) / length if length else 0.0
                x = path[i][0] + t * (path[i + 1][0] - path[i][0])
                y = path[i][1] + t * (path[i + 1][1] - path[i][1])
                return (x, y)
            travelled += length
        return path[-1]

    def _estimate_label_half_size(self, label: str) -> tuple[float, float]:
        """Estimate (half_width, half_height) of the rendered label bounding box."""
        plain = Diagram._html_to_plain_text(label or "")
        longest = max((len(line) for line in plain.split('\n')), default=len(plain))
        half_w = max(
            _LABEL_MIN_HALF_WIDTH,
            longest * _LABEL_CHAR_WIDTH_ESTIMATE + _LABEL_HORIZONTAL_PADDING,
        )
        line_count = plain.count('\n') + 1 if plain else 1
        half_h = max(_LABEL_MIN_HALF_HEIGHT, line_count * _LABEL_LINE_HEIGHT)
        return half_w, half_h

    def _existing_label_rects(
        self,
        exclude_conn_id: Optional[str] = None,
    ) -> list[tuple[float, float, float, float]]:
        """Return bounding rectangles for every edge label already placed.

        Each rectangle is ``(x, y, w, h)`` in absolute canvas coordinates and
        incorporates the connection's current ``label_offset_x/y`` if any.
        Connections without a label or without resolvable endpoints are
        skipped.
        """
        rects: list[tuple[float, float, float, float]] = []
        for conn_id, conn in self.connections.items():
            if exclude_conn_id and conn_id == exclude_conn_id:
                continue
            if not conn.label:
                continue
            if conn.source_id not in self.shapes or conn.target_id not in self.shapes:
                continue
            anchor = self._edge_label_anchor(
                conn.source_id, conn.target_id, list(conn.waypoints or [])
            )
            if anchor is None:
                continue
            ax = anchor[0] + (conn.label_offset_x or 0.0)
            ay = anchor[1] + (conn.label_offset_y or 0.0)
            hw, hh = self._estimate_label_half_size(conn.label)
            rects.append((ax - hw, ay - hh, 2 * hw, 2 * hh))
        return rects

    @staticmethod
    def _rects_overlap(
        a: tuple[float, float, float, float],
        b: tuple[float, float, float, float],
    ) -> bool:
        ax, ay, aw, ah = a
        bx, by, bw, bh = b
        return ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah

    def _label_offset_to_avoid_nodes(
        self,
        anchor: tuple[float, float],
        source_id: str,
        target_id: str,
        label_half_width: float,
        label_half_height: float,
        margin: float = _LABEL_CLEARANCE_MARGIN,
        other_label_rects: Optional[list[tuple[float, float, float, float]]] = None,
    ) -> Optional[tuple[float, float]]:
        """Return an (dx, dy) offset pushing the label out of obscuring obstacles.

        Considers **every** non-endpoint node the label currently overlaps as
        well as the bounding boxes of labels already attached to other
        connections.  Generates a grid of candidate shifts (axis-aligned push
        past each obstacle's edge, plus a conservative diagonal fallback) and
        picks the one that fully clears all obstacles with the smallest
        total displacement.  If no candidate fully clears, the candidate
        with the smallest residual overlap area is returned.
        Returns ``None`` only when the natural anchor already sits clear.
        """
        ax, ay = anchor
        label_rect = (
            ax - label_half_width,
            ay - label_half_height,
            2 * label_half_width,
            2 * label_half_height,
        )
        exclude = {source_id, target_id}

        # Collect every node rect the label currently overlaps.
        node_rects: list[tuple[float, float, float, float]] = []
        for shape_id, shape in self.shapes.items():
            if shape_id in exclude:
                continue
            if shape.width <= 0 or shape.height <= 0:
                continue
            # Skip UML class child sections (any shape with a shape parent).
            if shape.parent_id and shape.parent_id in self.shapes:
                continue
            rx, ry, rw, rh = self._shape_abs_rect(shape_id)
            if self._rects_overlap(label_rect, (rx, ry, rw, rh)):
                node_rects.append((rx, ry, rw, rh))

        label_rects = list(other_label_rects or [])
        # Also push away from overlapping existing labels even if no node conflict.
        conflicting_labels = [
            lr for lr in label_rects if self._rects_overlap(label_rect, lr)
        ]
        if not node_rects and not conflicting_labels:
            return None

        obstacles = node_rects + conflicting_labels

        # Build candidate (dx, dy) offsets that clear the bounding box past
        # each obstacle on each of the four axis-aligned sides, plus zero
        # (to allow early exit when only a fallback label-conflict exists).
        candidates: list[tuple[float, float]] = [(0.0, 0.0)]
        for rx, ry, rw, rh in obstacles:
            up_dy = (ry - label_half_height - margin) - ay
            down_dy = (ry + rh + label_half_height + margin) - ay
            left_dx = (rx - label_half_width - margin) - ax
            right_dx = (rx + rw + label_half_width + margin) - ax
            candidates.extend([
                (0.0, up_dy),
                (0.0, down_dy),
                (left_dx, 0.0),
                (right_dx, 0.0),
            ])

        def overlap_area(
            r1: tuple[float, float, float, float],
            r2: tuple[float, float, float, float],
        ) -> float:
            ox1 = max(r1[0], r2[0])
            oy1 = max(r1[1], r2[1])
            ox2 = min(r1[0] + r1[2], r2[0] + r2[2])
            oy2 = min(r1[1] + r1[3], r2[1] + r2[3])
            return max(0.0, ox2 - ox1) * max(0.0, oy2 - oy1)

        def score(candidate: tuple[float, float]) -> tuple[float, float]:
            """Rank candidate offsets: lower is better.

            Primary: total residual overlap area after the shift (zero means
            fully clear). Secondary: displacement magnitude (prefer the
            smallest nudge that still clears every obstacle).
            """
            dx, dy = candidate
            shifted = (
                label_rect[0] + dx,
                label_rect[1] + dy,
                label_rect[2],
                label_rect[3],
            )
            # Primary score term: total overlap area after shift (zero = fully clear).
            residual = sum(overlap_area(shifted, obs) for obs in obstacles)
            # Include the union of node rects and other edge labels that were
            # not originally conflicting, so the chosen offset does not sail
            # into a different unrelated node.
            for shape_id, shape in self.shapes.items():
                if shape_id in exclude:
                    continue
                if shape.width <= 0 or shape.height <= 0:
                    continue
                if shape.parent_id and shape.parent_id in self.shapes:
                    continue
                rect = self._shape_abs_rect(shape_id)
                if rect in node_rects:
                    continue
                residual += overlap_area(shifted, rect)
            for lr in label_rects:
                if lr in conflicting_labels:
                    continue
                residual += overlap_area(shifted, lr)
            return (residual, dx * dx + dy * dy)

        best = min(candidates, key=score)
        if best == (0.0, 0.0):
            # No improvement possible; still prefer an axis-aligned nudge to
            # signal an attempt was made rather than accept the overlap.
            non_trivial = [c for c in candidates if c != (0.0, 0.0)]
            if non_trivial:
                best = min(non_trivial, key=score)
        return best

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
        end_arrow: Optional[str] = None,
        auto_route: bool = True,
        auto_avoid_label_overlap: bool = True,
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
            auto_route: When True (the default) and the caller did not provide
                explicit ``waypoints`` / ``source_point`` / ``target_point``,
                automatically inject a waypoint so the connection routes around
                any shape that would otherwise lie between source and target.
            auto_avoid_label_overlap: When True (the default) and ``label`` is
                non-empty, compute a ``label_offset_x/y`` that pushes the label
                out of any node its natural midpoint would otherwise obscure.
                Ignored when the caller supplies either offset explicitly.

        Returns:
            The ID of the created connection
        """
        # Req 3: allow either endpoint to be free-floating by supplying an
        # explicit source_point / target_point. Previously both IDs were
        # mandatory, which forced callers to invent placeholder shapes.
        missing_source = bool(source_id) and source_id not in self.shapes
        missing_target = bool(target_id) and target_id not in self.shapes
        if missing_source or missing_target:
            # Non-empty IDs must match a real shape. This catches typos and
            # stale references from the AI.
            missing = [x for x, m in ((source_id, missing_source), (target_id, missing_target)) if m]
            raise ValueError(
                f"Source or target shape not found: {', '.join(missing)}"
            )
        if not source_id and source_point is None:
            raise ValueError(
                "Either source_id or source_point must be provided for a connection"
            )
        if not target_id and target_point is None:
            raise ValueError(
                "Either target_id or target_point must be provided for a connection"
            )
            
        conn_id = f"conn_{self.next_id}"
        self.next_id += 1

        effective_waypoints = list(waypoints or [])
        if (
            auto_route
            and not effective_waypoints
            and source_point is None
            and target_point is None
            and source_id in self.shapes
            and target_id in self.shapes
            and edge_style in ("orthogonal", "straight", "curved")
        ):
            effective_waypoints = self._compute_auto_waypoints(source_id, target_id)

        # Auto-avoid label overlap: if the label's natural midpoint lands
        # inside another shape, nudge it via label_offset_x/y.
        effective_label_offset_x = label_offset_x
        effective_label_offset_y = label_offset_y
        if (
            auto_avoid_label_overlap
            and label
            and label_offset_x is None
            and label_offset_y is None
            and source_point is None
            and target_point is None
            and source_id in self.shapes
            and target_id in self.shapes
        ):
            anchor = self._edge_label_anchor(
                source_id, target_id, effective_waypoints
            )
            if anchor is not None:
                # Estimate label bounding box from its rendered text length.
                half_w, half_h = self._estimate_label_half_size(label)
                other_label_rects = self._existing_label_rects()
                offset = self._label_offset_to_avoid_nodes(
                    anchor, source_id, target_id,
                    label_half_width=half_w,
                    label_half_height=half_h,
                    other_label_rects=other_label_rects,
                )
                if offset is not None:
                    effective_label_offset_x, effective_label_offset_y = offset

        self.connections[conn_id] = Connection(
            id=conn_id,
            label=label,
            source_id=source_id,
            target_id=target_id,
            arrow_type=arrow_type,
            style=style,
            label_position=label_position,
            label_offset_x=effective_label_offset_x,
            label_offset_y=effective_label_offset_y,
            label_background_color=label_background_color,
            entry_x=entry_x,
            entry_y=entry_y,
            exit_x=exit_x,
            exit_y=exit_y,
            waypoints=effective_waypoints,
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
            shape_value = self._format_html_label(shape.label)
            
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

            # Req 3: conditionally include source/target attributes. Emitting
            # `source=""` / `target=""` would cause drawio to try to resolve
            # those IDs and silently drop the edge binding when it can't.
            endpoint_parts: list[str] = []
            has_source = bool(conn.source_id) and conn.source_id in self.shapes
            has_target = bool(conn.target_id) and conn.target_id in self.shapes
            if has_source:
                endpoint_parts.append(f'source="{conn.source_id}"')
            if has_target:
                endpoint_parts.append(f'target="{conn.target_id}"')

            # Pick edge parent = LCA of the two endpoints in the parent tree.
            # Falling back to "1" when either endpoint is free-floating keeps
            # behaviour backwards-compatible for existing diagrams.
            edge_parent = self._edge_parent_id(
                conn.source_id if has_source else None,
                conn.target_id if has_target else None,
            )

            endpoint_attr = (" " + " ".join(endpoint_parts)) if endpoint_parts else ""
            xml_parts.append(
                f'        <mxCell id="{conn.id}" value="{self._format_html_label(conn.label)}" '
                f'style="{style}" edge="1" parent="{edge_parent}"{endpoint_attr}>'
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
        # Convert <br> tags to newlines first so the parser can split by line,
        # then reuse the shared HTML coercion for any other backslash escapes.
        normalized = HTML_LINE_BREAK_RE.sub('\n', label)
        return re.sub(r"\\+[ln]", '\n', normalized)

    @staticmethod
    def _format_html_label(text: str) -> str:
        """Format label text as escaped HTML with <br> line breaks.

        Input may be plain text (``\\n``) or already HTML (``<br>``); both are
        coerced into HTML-style (``<br>``) and then XML-escaped for embedding
        in Draw.io attribute values.
        """
        return Diagram._escape_xml(coerce_html_label(text))

    @staticmethod
    def _html_to_plain_text(text: str) -> str:
        """Convert an HTML label into visible plain text for sizing calculations."""
        normalized = text.replace('\r\n', '\n').replace('\r', '\n')
        normalized = HTML_BLOCK_BREAK_RE.sub('\n', normalized)
        normalized = HTML_TAG_RE.sub('', normalized)
        normalized = html.unescape(normalized)
        return normalized.strip('\n')
    
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

            # UML Component / Sequence-diagram shapes
            "actor": "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;outlineConnect=0;",
            "lifeline": "shape=umlLifeline;perimeter=lifelinePerimeter;whiteSpace=wrap;html=1;container=1;dropTarget=0;collapsible=0;recursiveResize=0;outlineConnect=0;",
            "uml_frame": "shape=umlFrame;whiteSpace=wrap;html=1;pointerEvents=0;",
            "component": "shape=component;align=left;spacingLeft=36;whiteSpace=wrap;html=1;",
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

        width = max(
            width,
            self._calculate_uml_class_width(
                name,
                uml_sections,
                12
            )
        )
        
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
