#!/usr/bin/env python3
"""
Diagram state management.

This module contains the DiagramState class and utility functions
used across all handler modules.
"""

from typing import Optional
from datetime import datetime, timezone
from ..diagram import Diagram
from ..file_operations import save_diagram_file


class DiagramState:
    """Manages the global diagram state."""

    def __init__(self):
        self.current_diagram: Optional[Diagram] = None
        self.current_xml: Optional[str] = None
        # Autosave configuration
        self.autosave_path: Optional[str] = None
        self.autosave_enabled: bool = False
        # Write observability counters
        self.write_count: int = 0
        self.last_save_time: Optional[str] = None
        self.last_save_bytes: int = 0

    def get_or_create_diagram(self) -> Diagram:
        """Get or create the current diagram."""
        if self.current_diagram is None:
            self.current_diagram = Diagram()
        return self.current_diagram

    def reset(self):
        """Reset the diagram state."""
        self.current_diagram = None
        self.current_xml = None
        self.autosave_path = None
        self.autosave_enabled = False
        self.write_count = 0
        self.last_save_time = None
        self.last_save_bytes = 0

    def maybe_autosave(self) -> Optional[str]:
        """Write to disk if autosave is enabled.

        Returns a short status string suitable for appending to tool output,
        or None if autosave is not active.
        """
        if not (self.autosave_enabled and self.autosave_path):
            return None
        xml_content = self._current_xml_content()
        if xml_content is None:
            return None
        try:
            bytes_written = save_diagram_file(self.autosave_path, xml_content)
            self.write_count += 1
            self.last_save_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            self.last_save_bytes = bytes_written
            return (
                f" [autosaved → {self.autosave_path}"
                f" | v{self.write_count}"
                f" | {bytes_written}B"
                f" | {self.last_save_time}]"
            )
        except Exception as exc:
            return f" [autosave failed: {exc}]"

    def _current_xml_content(self) -> Optional[str]:
        """Return current XML from whichever source is active."""
        if self.current_xml:
            return self.current_xml
        if self.current_diagram:
            return self.current_diagram.to_drawio_xml()
        return None


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
