"""
Data models for Draw.io diagram elements.

This module contains Pydantic models representing the core diagram elements:
- DiagramElement: Base class for all diagram elements
- Shape: Represents shapes/nodes in the diagram
- Connection: Represents connections/edges between shapes
"""

from typing import Optional
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
    label_position: Optional[str] = None  # "left", "right", "center"
    label_offset_x: Optional[float] = None  # X offset for label position
    label_offset_y: Optional[float] = None  # Y offset for label position
    label_background_color: Optional[str] = None  # Background color for label
