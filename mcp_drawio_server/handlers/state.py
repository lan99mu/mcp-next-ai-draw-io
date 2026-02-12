#!/usr/bin/env python3
"""
Diagram state management.

This module contains the DiagramState class and utility functions
used across all handler modules.
"""

from typing import Optional
from ..diagram import Diagram


class DiagramState:
    """Manages the global diagram state."""
    
    def __init__(self):
        self.current_diagram: Optional[Diagram] = None
        self.current_xml: Optional[str] = None
    
    def get_or_create_diagram(self) -> Diagram:
        """Get or create the current diagram."""
        if self.current_diagram is None:
            self.current_diagram = Diagram()
        return self.current_diagram
    
    def reset(self):
        """Reset the diagram state."""
        self.current_diagram = None
        self.current_xml = None


# Global diagram state instance
diagram_state = DiagramState()


def safe_float(value, default=0.0) -> float:
    """Safely convert a value to float, returning default if conversion fails."""
    if value is None or value == '':
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def bind_nodes_helper(diagram: Diagram, node_ids: list[str]) -> None:
    """Helper function to bind multiple nodes together."""
    for node_id in node_ids:
        other_nodes = [nid for nid in node_ids if nid != node_id]
        diagram.shapes[node_id].bound_nodes = list(
            set(diagram.shapes[node_id].bound_nodes + other_nodes)
        )
