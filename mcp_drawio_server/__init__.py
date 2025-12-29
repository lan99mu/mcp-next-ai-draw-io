"""
MCP Draw.io Server Package

A Model Context Protocol (MCP) server that provides tools for creating and 
manipulating Draw.io diagrams.
"""

from .server import main
from .diagram import Diagram
from .models import DiagramElement, Shape, Connection
from .xml_operations import (
    parse_drawio_xml,
    get_cells_from_xml,
    update_cell_in_xml,
    delete_cell_in_xml,
)
from .file_operations import load_diagram_file, save_diagram_file

__all__ = [
    "main",
    "Diagram",
    "DiagramElement",
    "Shape",
    "Connection",
    "parse_drawio_xml",
    "get_cells_from_xml",
    "update_cell_in_xml",
    "delete_cell_in_xml",
    "load_diagram_file",
    "save_diagram_file",
]
