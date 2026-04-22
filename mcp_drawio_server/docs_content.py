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
- **add_shape** — Add a shape. Required: `label` (HTML-style, use `<br>` for line breaks; plain `\n`/`\l` is auto-converted). Key options: `shape_type`, `x`, `y`, `width`, `height`, colors, `parent_id`.
- **add_connection** — Connect two shapes. Required: `source_id`, `target_id`. Key options: `label` (HTML-style), `edge_style`, `arrow_type`, `entry_x/y`, `exit_x/y`, `waypoints`, `auto_route` (default `true` — auto-adds a waypoint so the line routes around intervening shapes).
- **update_cell** — Update label (HTML-style), position, size, or style. Required: `cell_id`. Only specified fields change.
- **delete_cell** — Remove a cell. Required: `cell_id`.

## Binding & Layout
Node binding operations are now available inside `batch_operations`:
- **batch_operations** `{"op": "bind_nodes", "node_ids": [...]}` — Bind nodes to move as a group.
- **batch_operations** `{"op": "unbind_nodes", "node_ids": [...]}` — Remove nodes from binding.
- To query which nodes are bound, call `get_cell(cell_id=...)` and read the `bound_nodes` field.
- **move_shape** — Move a single shape; bound nodes follow. Required: `shape_id`, `new_x`, `new_y`.
- **auto_layout_adjust** — Iteratively resolve overlaps. Options: `padding`, `max_iterations`, `only_ids`, `dry_run`.

## Analysis
- **detect_line_crossings** — Find crossing connections. Each issue carries a structured `fix` ready to execute via `batch_operations`.
- **detect_overlaps** — Find overlapping shapes (node–node, label overflow, out-of-container) with per-issue `fix` descriptors.
- **suggest_bindings** — Get binding recommendations with per-suggestion `fix`. Optional: `proximity_threshold`.
"""


def get_bindings_guide_content() -> str:
    """Return the bindings guide documentation content."""
    return """# Node Bindings Guide

## What Are Bindings?
Bindings group nodes so they move together. Moving one node in a group moves all others by the same offset.

## Workflow
1. Create related shapes with `add_shape` (or bundle into `batch_operations`).
2. Bind them immediately via `batch_operations`:
   `[{"op": "bind_nodes", "node_ids": [id1, id2, id3]}]`.
3. Later, move the group by moving any ONE node: `move_shape(shape_id=id1, new_x=..., new_y=...)`.

## Checking Bindings
- `list_cells()` shows `[BIND: explicit: id1, id2]` for bound nodes.
- `get_cell(cell_id=...)` returns a `bound_nodes` field — no separate query tool needed.

## Discovering Opportunities
- `suggest_bindings(proximity_threshold=200)` scores node pairs by proximity, alignment, and naming patterns.
- Each suggestion includes a structured `fix` (an `{op: "bind_nodes", args: …}` descriptor) — execute it verbatim via `batch_operations`.

## Common Patterns
- **Layer binding**: All nodes at the same Y level.
- **Vertical stack**: Service + DB + Cache.
- **Incremental**: `bind_nodes([a, b])` then later `bind_nodes([a, c])` — all three join the same group.

## Unbinding
- In a batch: `{"op": "unbind_nodes", "node_ids": [id]}` removes specific nodes from their group.
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
`create_diagram` → `batch_operations` (add all shapes + bind groups + add connections) → `save_diagram`

### Modify Existing
`load_diagram` → `list_cells` → `batch_operations` (update_cell / move_shape / bind_nodes as needed) → `save_diagram`

### Optimize Layout
`detect_overlaps` / `detect_line_crossings` / `suggest_bindings` → execute each issue's structured `fix` via `batch_operations`; for bulk overlap resolution call `auto_layout_adjust` once → verify
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

## Sequence / Component Diagram
| Shape | Use For |
|-------|---------|
| `actor` | UML stick-figure participant (external user / role) |
| `lifeline` | Vertical dashed lifeline with labelled header (sequence participant) |
| `uml_frame` | alt/loop/opt interaction frame wrapper |
| `component` | UML component (module / service with port notch) |

UML label format: `ClassName<br>───────<br>- attr: type<br>───────<br>+ method()`

## Label Format (Important)
All labels are rendered as HTML (`html=1`). **Always use HTML-style labels**, i.e. use `<br>` for line breaks. Plain `\n` and GraphViz `\l` / `\n` escapes are auto-converted to `<br>`, but prefer emitting HTML directly so what you send is what gets rendered.

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
