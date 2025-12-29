# Package Structure

This document explains the modular structure of the MCP Draw.io Server package.

## Overview

The code has been refactored from a single monolithic file into a well-organized package with clear separation of concerns.

## Module Organization

```
mcp_drawio_server/
├── __init__.py           # Package entry point
├── server.py             # MCP server and tool handlers
├── models.py             # Data models
├── diagram.py            # Diagram class
├── xml_operations.py     # XML parsing/manipulation
└── file_operations.py    # File I/O operations
```

## Module Responsibilities

### `__init__.py` (31 lines)
- **Purpose**: Package initialization and public API
- **Exports**: Main entry point, core classes, and utility functions
- **Usage**: Import from this module to use the package

### `models.py` (38 lines)
- **Purpose**: Pydantic data models for diagram elements
- **Contains**:
  - `DiagramElement`: Base class for all diagram elements
  - `Shape`: Represents shapes/nodes in diagrams
  - `Connection`: Represents edges/connections between shapes
- **Dependencies**: `pydantic`

### `diagram.py` (184 lines)
- **Purpose**: Core diagram management and XML generation
- **Contains**:
  - `Diagram`: Main class for creating and managing diagrams
  - Methods for adding shapes and connections
  - XML generation from diagram structure
  - Style management for different shape types
- **Dependencies**: `models.py`

### `xml_operations.py` (100 lines)
- **Purpose**: XML parsing and manipulation utilities
- **Contains**:
  - `parse_drawio_xml()`: Parse Draw.io XML strings
  - `get_cells_from_xml()`: Extract cells from XML
  - `update_cell_in_xml()`: Modify existing cells
  - `delete_cell_in_xml()`: Remove cells from XML
- **Dependencies**: Python's `xml.dom.minidom`

### `file_operations.py` (52 lines)
- **Purpose**: File system operations for diagrams
- **Contains**:
  - `load_diagram_file()`: Load .drawio files from disk
  - `save_diagram_file()`: Save diagrams to disk
- **Dependencies**: Python's `pathlib`

### `server.py` (606 lines)
- **Purpose**: MCP server implementation and tool handlers
- **Contains**:
  - MCP server initialization
  - Tool definitions (create_diagram, add_shape, etc.)
  - Tool handler implementations
  - Global state management
  - `main()`: Server entry point
- **Dependencies**: All other modules, `mcp` package

## Import Patterns

### For End Users
```python
from mcp_drawio_server import Diagram, main

# Create and use diagrams
diagram = Diagram("My Diagram")
shape_id = diagram.add_shape("Label", x=100, y=100)
```

### For Advanced Usage
```python
from mcp_drawio_server import (
    Diagram,
    get_cells_from_xml,
    update_cell_in_xml,
    load_diagram_file,
    save_diagram_file
)
```

## Design Principles

1. **Single Responsibility**: Each module has one clear purpose
2. **Low Coupling**: Modules depend on abstractions, not implementations
3. **High Cohesion**: Related functionality is grouped together
4. **Backward Compatibility**: Public API remains unchanged
5. **Testability**: Each module can be tested independently

## Benefits of This Structure

- **Maintainability**: Easier to find and modify specific functionality
- **Scalability**: New features can be added to appropriate modules
- **Readability**: Smaller files are easier to understand
- **Reusability**: Modules can be imported and used independently
- **Testing**: Clear module boundaries enable better testing

## Development Workflow

When making changes:

1. **Data models** → Edit `models.py`
2. **Diagram logic** → Edit `diagram.py`
3. **XML operations** → Edit `xml_operations.py`
4. **File I/O** → Edit `file_operations.py`
5. **MCP tools** → Edit `server.py`
6. **Public API** → Update `__init__.py` if needed

## Testing

All existing tests continue to work without modification, demonstrating that the refactoring maintains backward compatibility:

- `test_functionality.py`
- `test_new_diagrams.py`
- `test_file_operations.py`
- `test_label_positioning.py`
- `demo.py`
