#!/usr/bin/env python3
"""
Documentation content for MCP Resources.

This module contains the actual documentation text for on-demand resources.
Keeping documentation content separate from resource handling logic.
"""


def get_tools_overview_content() -> str:
    """Return the tools overview documentation content."""
    return """# Tool Documentation

## File Operations

### create_diagram
Create a new Draw.io diagram from scratch. This initializes a new diagram in memory.

**Usage:** When starting a new diagram project.

### load_diagram
Load an existing .drawio file from disk. This allows you to read and modify existing diagrams.

**Parameters:**
- `path`: Path to the .drawio file to load

### save_diagram
Save the current diagram to a .drawio file on disk.

**Parameters:**
- `path`: Path where the .drawio file should be saved

## Inspection Tools

### list_cells
List all cells (shapes and connections) with their IDs, labels, types, and **binding information**.

**Key Information Provided:**
- Cell IDs for reference
- Cell types (vertex/edge)
- Labels and values
- **Binding status** - Shows `[BOUND to: id1, id2, ...]` for bound nodes
- Position and size information

**Best Practice:** Always check bindings before making changes. If nodes are bound, you only need to adjust ONE node.

### get_cell
Get detailed information about a specific cell by its ID.

**Parameters:**
- `cell_id`: The ID of the cell to retrieve

## Modification Tools

### update_cell
Update a specific cell's properties by ID.

**Parameters:**
- `cell_id`: The ID of the cell to update
- `value`: New label/value for the cell (optional)
- `x`, `y`: New position coordinates (optional)
- `width`, `height`: New dimensions (optional)
- `style`: New Draw.io style string (optional)

### delete_cell
Delete a specific cell by ID from the diagram.

**Parameters:**
- `cell_id`: The ID of the cell to delete

### add_shape
Add a new shape/node to the diagram. Returns the ID of the created shape.

**Parameters:**
- `label`: Label text for the shape
- `x`, `y`: Position coordinates (default: 0, 0)
- `width`, `height`: Shape dimensions (default: 120, 60)
- `shape_type`: Type of shape (default: rectangle)
- `style`: Custom Draw.io style string (optional)

### add_connection
Add a connection/edge between two shapes. Supports label positioning, entry/exit points, and waypoint routing. Returns the ID of the created connection.

**Parameters:**
- `source_id`, `target_id`: IDs of shapes to connect
- `label`: Connection label text (optional)
- `arrow_type`: Arrow style (default: classic)
- `label_position`: Label position (left/right/center)
- `entry_x`, `entry_y`: Entry point on target (0-1)
- `exit_x`, `exit_y`: Exit point on source (0-1)
- `waypoints`: List of [x, y] routing points

## Node Binding Tools

### bind_nodes
**IMPORTANT FOR EFFICIENCY!**

Bind multiple nodes together so they move as a group. When you move one node in a bound group, all bound nodes will move together by the same offset.

**Use Cases:**
- Service and its database
- Component and its label
- Related UI elements
- Layered components

**Best Practice:** Bind related nodes immediately after creating them.

**Parameters:**
- `node_ids`: List of node IDs to bind together (minimum 2 nodes)

### unbind_nodes
Remove nodes from their binding group. The specified nodes will no longer move together.

**Parameters:**
- `node_ids`: List of node IDs to unbind

### get_bound_nodes
Get the list of nodes that are bound to a specific node.

**Parameters:**
- `node_id`: The node ID to query bindings for

### move_shape
Move a shape to a new position. **If the shape is bound to other nodes, all bound nodes will also move by the same offset AUTOMATICALLY.**

This is the PREFERRED way to make local adjustments to groups of related nodes.

**Parameters:**
- `shape_id`: The ID of the shape to move
- `new_x`, `new_y`: New coordinates

**Efficiency Tip:** Check `list_cells` output to see which nodes are bound before moving.

## Analysis Tools

### detect_line_crossings
Detect line crossings in the diagram and provide position hints for adjustments.

**Returns:**
- List of crossing locations
- Suggestions for which nodes to move
- Position adjustment hints

**Use Case:** Optimize diagram layout by fixing overlapping connections.

### suggest_bindings
Analyze the diagram and suggest which nodes should be bound together based on:
- **Proximity**: Nodes close together (within threshold)
- **Naming patterns**: Same prefix/suffix in labels
- **Connections**: Nodes connected to similar targets
- **Related keywords**: service+db, cache+db, etc.

**Parameters:**
- `proximity_threshold`: Maximum distance in pixels (default: 200)

**Returns:** Scored suggestions with reasons.

**Use Case:** Discover binding opportunities to enable efficient local adjustments.

## Deprecated Tools

### list_shapes
List all shapes in the diagram. **Deprecated:** Use `list_cells` instead for more complete information including connections and bindings.
"""


def get_bindings_guide_content() -> str:
    """Return the bindings guide documentation content."""
    return """# Node Bindings Guide

## What Are Node Bindings?

Node bindings allow you to group multiple nodes so they move together as a single unit. This is KEY for efficient diagram editing.

## Why Use Bindings?

### Without Bindings (Inefficient)
```
# Moving a service cluster manually
move_shape("svc1", 300, 100)   # Call 1
move_shape("svc2", 300, 200)   # Call 2
move_shape("db1", 300, 300)    # Call 3
move_shape("cache1", 450, 300) # Call 4
# Total: 4 tool calls
```

### With Bindings (Efficient)
```
# One-time setup
bind_nodes(["svc1", "svc2", "db1", "cache1"])

# Future modifications
move_shape("svc1", 300, 100)  # Just ONE call - all 4 move!
# Total: 1 tool call (plus one-time setup)
```

**Result:** 75% reduction in tool calls for adjustments!

## How to Use Bindings

### 1. Create Nodes
```
svc_id = add_shape(label="Service", x=100, y=100)
db_id = add_shape(label="Database", x=100, y=200)
cache_id = add_shape(label="Cache", x=250, y=200)
```

### 2. Bind Immediately
```
bind_nodes(node_ids=[svc_id, db_id, cache_id])
```

**Best Practice:** Bind right after creation, not later!

### 3. Move the Group
```
# Move any one node, all bound nodes follow
move_shape(svc_id, 200, 150)
```

## When to Use Bindings

Bind nodes when they are:

1. **Logically related**
   - Service + Database + Cache
   - Component + Label
   - Parent + Children

2. **Visually grouped**
   - Nodes in the same section
   - Layered components
   - Related UI elements

3. **Should move together**
   - Architecture layers
   - Process flows
   - Component clusters

## Checking Bindings

Use `list_cells` to see current bindings:

```
list_cells()

Output:
- Node: Service (id: abc123) [BOUND to: def456, ghi789]
- Node: Database (id: def456) [BOUND to: abc123, ghi789]
- Node: Cache (id: ghi789) [BOUND to: abc123, def456]
```

## Discovering Binding Opportunities

Use `suggest_bindings()` to find nodes that should be bound:

```
suggest_bindings(proximity_threshold=200)

Returns scored suggestions:
1. Bind 'Service' (abc123) with 'Database' (def456)
   Score: 85/100
   Reasons: proximity, naming pattern, connections
```

## Unbinding Nodes

Remove bindings when needed:

```
unbind_nodes(node_ids=[cache_id])
```

## Common Patterns

### Pattern 1: Layer Binding
```
# Bind all nodes in a layer
ui_nodes = [node1_id, node2_id, node3_id]
bind_nodes(node_ids=ui_nodes)
```

### Pattern 2: Vertical Stack
```
# Bind service stack
stack = [service_id, api_id, db_id, cache_id]
bind_nodes(node_ids=stack)
```

### Pattern 3: Incremental Binding
```
# Start with two nodes
bind_nodes([node1, node2])

# Add more later (they all bind together)
bind_nodes([node1, node3])  # Now node1, node2, node3 are all bound
```

## Efficiency Metrics

| Operation | Without Bindings | With Bindings | Savings |
|-----------|-----------------|---------------|---------|
| Move 5-node group | 5 calls | 1 call | 80% |
| Adjust layer | 10 calls | 2 calls | 80% |
| Reposition cluster | 8 calls | 1 call | 87% |

## Tips & Best Practices

1. ✅ **Bind early** - Right after creating nodes
2. ✅ **Use suggest_bindings** - Discover opportunities
3. ✅ **Check list_cells** - Verify bindings before moving
4. ✅ **Bind logically** - Group related nodes
5. ✅ **Test with one move** - Verify bindings work

## Troubleshooting

**Q: Nodes not moving together?**
A: Check if they're actually bound with `list_cells` or `get_bound_nodes`.

**Q: How do I bind nodes across layers?**
A: Just include all node IDs in the `bind_nodes` call, regardless of position.

**Q: Can I partially unbind?**
A: Yes, use `unbind_nodes` with specific node IDs to remove only those nodes from the group.
"""


def get_workflows_content() -> str:
    """Return the workflows best practices documentation content."""
    return """# Workflow Best Practices

## Efficiency Principles

### 1. Bind Early, Move Once
**Pattern:** Create nodes → Bind immediately → Move later

**Bad:**
```
# Create nodes
add_shape(...)  # x5
add_connection(...)  # x4
# Later: move each individually
move_shape(...)  # x5
```

**Good:**
```
# Create nodes
add_shape(...)  # x5
# Bind immediately
bind_nodes([all_ids])  # x1
add_connection(...)  # x4
# Later: move once
move_shape(one_id, ...)  # x1 (moves all)
```

### 2. Check Bindings First
Before modifying, always check `list_cells` to see existing bindings.

### 3. Use Prompts
Leverage MCP Prompts for guided workflows:
- `create_flowchart`
- `add_connected_nodes`
- `optimize_layout`
- `modify_with_bindings`
- `create_architecture_diagram`

### 4. Leverage Analysis Tools
- Use `suggest_bindings` to discover opportunities
- Use `detect_line_crossings` to find issues

## Common Workflows

### Creating a New Diagram

1. **Plan structure** - Think about logical groups
2. **Create nodes** - Use proper spacing (150-200px)
3. **Bind groups** - Bind related nodes immediately
4. **Add connections** - Connect the flow
5. **Optimize** - Use `detect_line_crossings` and `suggest_bindings`

### Modifying Existing Diagrams

1. **Load diagram** - `load_diagram(path)`
2. **Check bindings** - `list_cells()` to see current state
3. **Add bindings if needed** - `bind_nodes()` for efficiency
4. **Make changes** - Move one node per bound group
5. **Save** - `save_diagram(path)`

### Optimizing Layout

1. **Detect issues** - `detect_line_crossings()`
2. **Suggest bindings** - `suggest_bindings()`
3. **Apply bindings** - `bind_nodes()` for top suggestions
4. **Fix crossings** - Move one node per group
5. **Verify** - `detect_line_crossings()` again

## Tool Call Reduction Strategies

### Strategy 1: Batch Creation
Create all related nodes before binding, then bind once.

### Strategy 2: Group Movements
Use bindings to move multiple nodes with one call.

### Strategy 3: On-Demand Details
Use resources and prompts for detailed info instead of verbose tool descriptions.

## Common Mistakes to Avoid

❌ **Creating nodes one at a time without binding**
- Creates inefficiency for future edits

❌ **Moving nodes individually**
- Should bind first, then move group

❌ **Not using suggest_bindings**
- Misses opportunities for efficiency

❌ **Ignoring existing bindings**
- May unintentionally break groupings

## Efficiency Metrics

| Task | Traditional | With Best Practices | Improvement |
|------|-------------|-------------------|-------------|
| Create 10-node flowchart | 25-30 calls | 12-15 calls | 50-60% |
| Modify diagram section | 10-15 calls | 2-3 calls | 80-85% |
| Fix line crossings | 15-20 calls | 4-6 calls | 70-75% |
| Architecture diagram | 40-50 calls | 15-20 calls | 60-70% |

## Advanced Patterns

### Layered Architecture
```
# Create layer 1
ui_nodes = [create nodes...]
bind_nodes(ui_nodes)

# Create layer 2
api_nodes = [create nodes...]
bind_nodes(api_nodes)

# Create vertical stacks
for svc, db in pairs:
    bind_nodes([svc, db])
```

### Incremental Expansion
```
# Start small
core = [node1, node2]
bind_nodes(core)

# Expand gradually
bind_nodes([node1, node3])  # Adds to existing group
```

## Resource Usage

### When to Use What

- **Prompts** → Workflow guidance, step-by-step
- **Resources** → Detailed documentation, reference
- **Tools** → Actual diagram operations
- **list_cells** → Current state, verify bindings

## Summary

**Key Principles:**
1. Bind early and often
2. Move groups, not individuals
3. Use analysis tools to discover opportunities
4. Follow proven workflow patterns
5. Check bindings before changes

**Result:** 60-80% reduction in tool calls!
"""


def get_shapes_reference_content() -> str:
    """Return the shapes reference documentation content."""
    return """# Shape Types Reference

## Basic Shapes

### rectangle
Standard rectangular box, the default shape type.

**Use for:** Processes, components, general boxes

### ellipse
Oval/circular shape.

**Use for:** Start/end points, states, actors

### diamond
Diamond/rhombus shape.

**Use for:** Decisions, gateways

### parallelogram
Slanted parallelogram shape.

**Use for:** Input/Output, data

### hexagon
Six-sided polygon shape.

**Use for:** Preparation steps, predefined processes

### cylinder
Cylindrical shape with curved top/bottom.

**Use for:** Databases, storage

### cloud
Cloud-shaped element.

**Use for:** Cloud services, external systems

## Activity Diagram Shapes

### activity_start
Circle representing workflow start.

### activity_end
Double circle representing workflow end.

### activity_action
Rounded rectangle for actions/activities.

### activity_decision
Diamond for decision points.

### activity_fork
Black bar for parallel flow splits.

### activity_join
Black bar for parallel flow merges.

### activity_send_signal
Pentagon for signal sending.

### activity_receive_signal
Pentagon (inverted) for signal receiving.

### activity_note
Note/comment annotation.

## Swimlane Shapes

### swimlane_pool
Container for multiple swimlanes.

### swimlane_h
Horizontal swimlane divider.

### swimlane_v
Vertical swimlane divider.

### container
Generic container for grouping. Supports parent_id for child shapes.

## UML Class Diagram Shapes

### uml_class
Standard class box with three sections (name, attributes, methods).

### uml_interface
Interface representation (class with «interface» stereotype).

### uml_abstract_class
Abstract class (class with italic name).

### uml_enum
Enumeration type.

### uml_package
Package container for grouping classes.

### uml_note
Note/comment for UML diagrams.

## Style Options

### Shape Style Parameters

```python
add_shape(
    label="My Shape",
    x=100, y=100,
    # Style options:
    dashed=True,           # Dashed border
    rounded=True,          # Rounded corners
    stroke_width=2,        # Border thickness
    fill_color="#e1f5ff",  # Background color
    stroke_color="#0077cc",# Border color
    font_size=14,          # Text size
    font_color="#333333",  # Text color
    opacity=80,            # Opacity (0-100)
    overflow="hidden",     # Text overflow: hidden/visible/fill
    auto_size=True         # Auto-calculate dimensions from text
)
```

### Connection Style Parameters

```python
add_connection(
    source_id=shape1,
    target_id=shape2,
    # Edge routing:
    edge_style="orthogonal",  # orthogonal/straight/curved/entity_relation
    waypoints=[(200, 150), (200, 250)],  # Polyline bend points
    # Arrows:
    start_arrow="none",       # Arrow at start
    end_arrow="block",        # Arrow at end
    # Line style:
    dashed=True,              # Dashed line
    rounded=True,             # Rounded corners (orthogonal only)
    stroke_width=2,           # Line thickness
    stroke_color="#ff0000"    # Line color
)
```

### Common Style Properties (via style parameter)

- `fillColor`: Background color
- `strokeColor`: Border color  
- `strokeWidth`: Border thickness
- `fontSize`: Text size
- `fontColor`: Text color
- `rounded`: Rounded corners (1/0)
- `dashed`: Dashed line (1/0)
- `opacity`: Opacity (0-100)

## Usage Examples

### Basic Shapes with Styles
```python
# Dashed rectangle with rounded corners
add_shape(label="Process", x=100, y=100, dashed=True, rounded=True)

# Custom colors
add_shape(label="Alert", x=200, y=100, fill_color="#ffcccc", stroke_color="#ff0000")

# Auto-sized shape based on text
add_shape(label="Long description text\\nLine 2\\nLine 3", auto_size=True)
```

### Polyline Connections
```python
# Create a connection with waypoints (bend points)
add_connection(
    source_id=shape1,
    target_id=shape2,
    waypoints=[(150, 200), (150, 350), (300, 350)]  # L-shaped path
)
```

### UML Relationships
```python
# Inheritance (solid line, hollow arrow)
add_connection(source_id=child, target_id=parent, end_arrow="block")

# Interface implementation (dashed line, hollow arrow)
add_connection(source_id=impl, target_id=interface, dashed=True, end_arrow="block")

# Composition (solid line, filled diamond)
add_connection(source_id=whole, target_id=part, start_arrow="diamondThin")

# Aggregation (solid line, hollow diamond)
add_connection(source_id=whole, target_id=part, start_arrow="diamond")
```

### Container with Children
```python
# Create container
container = add_shape("Container", x=50, y=50, width=300, height=200, shape_type="container")

# Add child inside container (relative coordinates)
child = add_shape("Child", x=20, y=30, parent_id=container)
```

## Shape Dimensions

Default dimensions:
- Width: 120px
- Height: 60px

Recommended dimensions by type:
- **rectangle**: 120x60
- **ellipse**: 80x80 (for circles)
- **diamond**: 100x80
- **cylinder**: 120x80
- **activity_start/end**: 40x40
- **activity_action**: 140x60
- **uml_class**: 160x120+ (use auto_size=True)

## Auto-Size Feature

Use `auto_size=True` to automatically calculate shape dimensions based on text content:

```python
# Shape will auto-size to fit the text
class_shape = add_shape(
    label="UserService\\n---\\n+userId: int\\n+name: string\\n+email: string\\n---\\n+getUser()\\n+updateUser()",
    shape_type="uml_class",
    auto_size=True
)
```
"""
