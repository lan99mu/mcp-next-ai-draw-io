#!/usr/bin/env python3
"""
Documentation content for MCP Resources.

Concise reference docs served on-demand via MCP resources.
"""


def get_tools_overview_content() -> str:
    """Return the tools overview documentation content."""
    return """# Tool Reference

## File Operations
- **create_diagram** — Create a new diagram in memory. Optional `name`.
- **load_diagram** — Load a `.drawio` file. Required: `path`.
- **save_diagram** — Save to a `.drawio` file. Required: `path`.

## Inspection
- **list_cells** — List all shapes/connections with IDs, positions, sizes, and binding info.
- **get_cell** — Get detailed geometry, style, and bindings for one cell. Required: `cell_id`.

## Shape & Connection
- **add_shape** — Add a shape. Required: `label`. Key options: `shape_type`, `x`, `y`, `width`, `height`, colors, `parent_id`.
- **add_connection** — Connect two shapes. Required: `source_id`, `target_id`. Key options: `label`, `edge_style`, `arrow_type`, `entry_x/y`, `exit_x/y`, `waypoints`.
- **update_cell** — Update label, position, size, or style. Required: `cell_id`. Only specified fields change.
- **delete_cell** — Remove a cell. Required: `cell_id`.

## Binding & Layout
- **bind_nodes** — Bind nodes to move as a group. Required: `node_ids` (≥2).
- **unbind_nodes** — Remove nodes from binding. Required: `node_ids`.
- **get_bound_nodes** — Query bindings. Required: `node_id`.
- **move_shape** — Move a shape; bound nodes follow. Required: `shape_id`, `new_x`, `new_y`.

## Analysis
- **detect_line_crossings** — Find crossing connections and get fix suggestions.
- **suggest_bindings** — Get binding recommendations based on proximity and naming. Optional: `proximity_threshold`.
"""


def get_bindings_guide_content() -> str:
    """Return the bindings guide documentation content."""
    return """# Node Bindings Guide

## What Are Bindings?
Bindings group nodes so they move together. Moving one node in a group moves all others by the same offset.

## Workflow
1. Create related shapes with `add_shape`
2. Bind them immediately: `bind_nodes(node_ids=[id1, id2, id3])`
3. Later, move the group by moving any ONE node: `move_shape(shape_id=id1, new_x=..., new_y=...)`

## Checking Bindings
- `list_cells()` shows `[BIND: explicit: id1, id2]` for bound nodes
- `get_bound_nodes(node_id=...)` returns the binding list

## Discovering Opportunities
- `suggest_bindings(proximity_threshold=200)` scores node pairs by proximity, alignment, and naming patterns
- Apply top suggestions with `bind_nodes`

## Common Patterns
- **Layer binding**: All nodes at the same Y level
- **Vertical stack**: Service + DB + Cache
- **Incremental**: `bind_nodes([a, b])` then later `bind_nodes([a, c])` — all three join the same group

## Unbinding
- `unbind_nodes(node_ids=[id])` removes specific nodes from their group
"""


def get_workflows_content() -> str:
    """Return the workflows best practices documentation content."""
    return """# Workflow Best Practices

## Progressive Workflow (Recommended)
Use the three MCP prompts in order:
1. **plan_diagram** — Clarify nodes, connections, and groups before drawing
2. **draw_diagram** — Execute the plan: create shapes, bind, connect, save
3. **review_diagram** — Optimize: detect crossings, suggest bindings, fix layout

## Key Principles
- **Bind early**: Right after creating related shapes
- **Move groups**: `move_shape` one node; bound nodes follow
- **Check first**: `list_cells` before modifying to see existing bindings
- **Analyze**: `suggest_bindings` + `detect_line_crossings` after drawing

## Spacing Guidelines
- Vertical between rows: 150–200px
- Horizontal between columns: 200–250px
- Between architecture layers: 250–300px

## Common Workflows

### New Diagram
`create_diagram` → `add_shape` (all nodes) → `bind_nodes` → `add_connection` → `save_diagram`

### Modify Existing
`load_diagram` → `list_cells` → `bind_nodes` (if needed) → `move_shape` / `update_cell` → `save_diagram`

### Optimize Layout
`detect_line_crossings` → `suggest_bindings` → `bind_nodes` → `move_shape` → verify
"""


def get_shapes_reference_content() -> str:
    """Return the shapes reference documentation content."""
    return """# Shape Types Reference

## Basic Shapes
| Shape | Use For |
|-------|---------|
| `rectangle` | Processes, components, general boxes |
| `ellipse` | Start/end, states, actors |
| `diamond` | Decisions, gateways |
| `parallelogram` | Input/Output, data |
| `hexagon` | Preparation, predefined processes |
| `cylinder` | Databases, storage |
| `cloud` | Cloud services, external systems |

## Activity Diagram
| Shape | Use For |
|-------|---------|
| `activity_start` | Filled circle — workflow start |
| `activity_end` | Double circle — workflow end |
| `activity_action` | Rounded rect — actions |
| `activity_decision` | Diamond — branch |
| `activity_fork` / `activity_join` | Bar — parallel split/merge |
| `activity_send_signal` / `activity_receive_signal` | Pentagon — signals |
| `activity_note` | Annotation |

## Swimlane
| Shape | Use For |
|-------|---------|
| `swimlane_pool` | Pool container |
| `swimlane_h` | Horizontal lane |
| `swimlane_v` | Vertical lane |
| `container` | Generic grouping |

## UML Class Diagram
| Shape | Use For |
|-------|---------|
| `uml_class` | Three-compartment class box |
| `uml_interface` | Interface (italic) |
| `uml_abstract_class` | Abstract class (bold+italic) |
| `uml_enum` | Enumeration |
| `uml_package` | Package/namespace |
| `uml_note` | Comment/note |

UML label format: `ClassName<br>───────<br>- attr: type<br>───────<br>+ method()`

## Style Options
Shapes: `fill_color`, `stroke_color`, `font_color`, `font_size`, `dashed`, `rounded`, `stroke_width`, `opacity`, `overflow`, `auto_size`

Connections: `edge_style` (orthogonal/straight/curved/entity_relation), `arrow_type`, `start_arrow`, `end_arrow`, `dashed`, `rounded`, `stroke_width`, `stroke_color`

## Connection Points
- `exit_x/exit_y`: Where the line leaves the source (0–1 normalized)
- `entry_x/entry_y`: Where the line enters the target (0–1 normalized)
- `waypoints`: `[[x,y], ...]` for intermediate bend points
- `source_point/target_point`: `[x,y]` for explicit endpoints

## Default Dimensions
- Most shapes: 120×60
- Ellipse/circle: 80×80
- Diamond: 100×80
- Activity start/end: 40×40
- UML class: 160×120+ (use `auto_size=True`)
"""
