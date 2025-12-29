# Feature Summary: Coordinate System and Node Binding

## Overview

This implementation adds two key features to the MCP Draw.io Server as requested:

### 1. 坐标系统 (Coordinate System)

Enhanced position reporting to help LLMs better understand spatial relationships in diagrams.

**What changed:**
- `list_cells` now displays comprehensive coordinate information for shapes:
  - Position (top-left): `(x, y)`
  - Size: `width x height`
  - Center point: `(center_x, center_y)`
  - Full output example: `at (100, 50), size (120x60), center (160, 80)`

- `get_cell` provides detailed position data:
  - Position (top-left)
  - Size dimensions
  - Calculated center point
  - Bounding box coordinates: `(x, y) to (x+width, y+height)`

**Benefits:**
- LLMs can now understand spatial relationships between nodes
- Better decision-making for node placement
- Easier to analyze and modify diagram layouts

### 2. 节点绑定 (Node Binding)

Support for binding nodes together so they move as a group.

**New Tools Added:**

1. `bind_nodes` - Bind multiple nodes together
   - Parameters: `node_ids` (list of node IDs)
   - Minimum 2 nodes required
   - All nodes in the group reference each other

2. `unbind_nodes` - Remove bindings
   - Parameters: `node_ids` (list of node IDs)
   - Removes bindings and cleans up references

3. `get_bound_nodes` - Query bindings
   - Parameters: `node_id` (single node ID)
   - Returns list of bound nodes

4. `move_shape` - Move a shape and its bound nodes
   - Parameters: `shape_id`, `new_x`, `new_y`
   - All bound nodes move by the same offset

**Benefits:**
- Maintain structural integrity when reorganizing diagrams
- Move related components together (e.g., service + database)
- Preserve layout relationships during modifications

## Technical Implementation

### Data Model
- Added `bound_nodes: list[str]` field to `Shape` model
- Bindings are preserved in XML using custom `bound_nodes` attribute

### XML Operations
- Enhanced `get_cells_from_xml` to parse `bound_nodes` attribute
- Updated `to_drawio_xml` to serialize bindings

### Code Quality
- Added `safe_float()` helper for type-safe XML parsing
- Added `bind_nodes_helper()` for reusable binding logic
- Improved error handling for missing nodes

## Testing

### Test Coverage
- `test_coordinate_and_binding.py` - 5 comprehensive tests:
  1. Coordinate system functionality
  2. Node binding
  3. Moving bound nodes
  4. XML persistence of bindings
  5. Unbinding nodes

### Demo Script
- `demo_coordinate_and_binding.py` - Interactive demonstrations:
  1. Coordinate system usage
  2. Node binding workflow
  3. Combined features for layout management

## Documentation

### Updated Files
- `README.md` - Added feature descriptions and examples
- `README_CN.md` - Chinese documentation with examples
- Both include:
  - Feature descriptions
  - Tool reference tables
  - Usage examples
  - Use cases

## Usage Examples

### Coordinate System
```python
# View detailed position information
list_cells()
# Output: ID: shape_1, Type: Shape, Label: 'Server', 
#         at (100, 50), size (120x60), center (160, 80)

get_cell(cell_id="shape_1")
# Output includes: Position, Size, Center, Bounding box
```

### Node Binding
```python
# Bind two nodes together
bind_nodes(node_ids=["shape_1", "shape_2"])

# Move one - both move together
move_shape(shape_id="shape_1", new_x=200, new_y=100)

# Check bindings
get_bound_nodes(node_id="shape_1")
# Output: "Node 'shape_1' is bound to 1 node(s): shape_2"

# Unbind
unbind_nodes(node_ids=["shape_1"])
```

## Files Changed

1. `mcp_drawio_server/models.py` - Added `bound_nodes` field
2. `mcp_drawio_server/server.py` - Added 4 new tools + enhanced reporting
3. `mcp_drawio_server/diagram.py` - XML serialization of bindings
4. `mcp_drawio_server/xml_operations.py` - XML parsing of bindings
5. `README.md` - English documentation
6. `README_CN.md` - Chinese documentation
7. `test_coordinate_and_binding.py` - Test suite
8. `demo_coordinate_and_binding.py` - Demo script

## Test Results

All tests pass successfully:
- ✓ Coordinate system tests
- ✓ Node binding tests
- ✓ XML persistence tests
- ✓ Existing functionality tests (backward compatibility)
- ✓ File operations tests

## Impact

- **Zero breaking changes** - All existing functionality preserved
- **Enhanced capabilities** - LLMs can now better understand and manipulate diagrams
- **Type safety** - Improved with helper functions
- **Code quality** - Better maintainability with extracted helpers
