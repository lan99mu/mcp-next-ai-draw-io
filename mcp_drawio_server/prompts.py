#!/usr/bin/env python3
"""
MCP Prompts for Draw.io Server — Progressive Guidance.

Three-phase workflow:
  1. plan_diagram  — clarify structure before drawing
  2. draw_diagram  — create shapes and connections
  3. review_diagram — optimize layout and fix issues
"""

from mcp.types import (
    Prompt, PromptArgument, PromptMessage, GetPromptResult, TextContent
)


def get_prompt_definitions() -> list[Prompt]:
    """Return progressive prompt definitions (plan → draw → review)."""
    return [
        Prompt(
            name="plan_diagram",
            description="Phase 1: Clarify diagram structure before drawing. Outputs a node/connection plan.",
            arguments=[
                PromptArgument(
                    name="description",
                    description="What the diagram should represent (e.g., 'user login flow', 'microservices architecture')",
                    required=True
                ),
                PromptArgument(
                    name="diagram_type",
                    description="Diagram type: flowchart, architecture, uml_class, activity, swimlane, sequence, component, domain, communication",
                    required=False
                )
            ]
        ),
        Prompt(
            name="draw_diagram",
            description="Phase 2: Create shapes and connections based on a plan. Call this after plan_diagram.",
            arguments=[
                PromptArgument(
                    name="plan",
                    description="The structured plan from phase 1 (nodes and connections to create)",
                    required=True
                ),
                PromptArgument(
                    name="file_path",
                    description="Path to save the .drawio file (optional)",
                    required=False
                )
            ]
        ),
        Prompt(
            name="review_diagram",
            description="Phase 3: Optimize layout — detect crossings, suggest bindings, fix spacing.",
            arguments=[]
        ),
    ]


def get_prompt_result(name: str, arguments: dict[str, str] | None) -> GetPromptResult:
    """Get a specific prompt template with progressive instructions."""

    if name == "plan_diagram":
        description = (arguments or {}).get("description", "a diagram")
        diagram_type = (arguments or {}).get("diagram_type", "")

        type_hint = ""
        if diagram_type:
            type_hints = {
                "flowchart": "Use shape_type: rectangle for steps, diamond for decisions, ellipse for start/end.",
                "architecture": (
                    "Use rectangle/cylinder/cloud/component. Group by layer with container "
                    "(UI → API → Service → Data). Space layers 250px apart vertically. "
                    "Put external systems in a separate container or use shape_type=cloud."
                ),
                "uml_class": (
                    "Use shape_type: uml_class. Label format: "
                    "'ClassName<br>───────<br>- attr: type<br>───────<br>+ method()'. "
                    "For complex class diagrams, define domain containers first (shape_type=container), "
                    "place each class fully inside its domain via parent_id, keep domains non-overlapping, "
                    "and ensure classes in each domain use consistent grid spacing to avoid overlap."
                ),
                "activity": (
                    "Use activity_start/end/action/decision/fork/join shapes. "
                    "Add activity_note for annotations. Keep one primary flow direction (TB or LR)."
                ),
                "swimlane": "Use swimlane_pool + swimlane_h/swimlane_v. Place child shapes inside with parent_id.",
                "sequence": (
                    "Use shape_type=actor for participants that are human/external, and shape_type=lifeline "
                    "for each system participant (width≈120, height≈400+ so the dashed lifeline extends down). "
                    "Arrange lifelines left-to-right at the same y. Draw messages as connections between "
                    "lifelines with edge_style=straight and the method/event name as the label. "
                    "Use dashed=True for return messages. Optionally wrap alt/loop blocks with shape_type=uml_frame."
                ),
                "component": (
                    "Use shape_type=component for each module. Group related components inside "
                    "shape_type=container (one container per subsystem). Dependencies are dashed connections "
                    "with arrow_type=open; provided/required interfaces can be plain rectangles labeled "
                    "'«interface»<br>Name'. Keep modules aligned on a grid."
                ),
                "domain": (
                    "Domain call / context map. Use shape_type=container for each bounded context, "
                    "place services/entities inside via parent_id. Label connections with the concrete "
                    "action (e.g. '调用下单', '发布订单已支付'). Use dashed edges for async/event flows, "
                    "solid for synchronous calls."
                ),
                "communication": (
                    "Component communication. Use shape_type=rectangle or component for each component, "
                    "shape_type=cloud for external systems, shape_type=cylinder for datastores. "
                    "Every connection must carry a verb-phrase label (e.g. 'HTTP POST /orders', "
                    "'publish OrderPaid'). Use dashed edges for async/event channels."
                ),
            }
            type_hint = type_hints.get(diagram_type, "")

        return GetPromptResult(
            description=f"Plan: {description}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Plan a diagram for: {description}

TASK: Produce a structured plan — do NOT call any tools yet.

1. List every node with: label, shape_type, approximate (x, y), width, height
2. List every connection with: source → target, label, arrow_type
3. Identify groups of related nodes that should be bound together
4. Note the recommended spacing:
   - Vertical: 150–200px between rows
   - Horizontal: 200–250px between columns
   - Domain containers: keep 150–200px gap between domain boundaries

{f"TYPE HINT: {type_hint}" if type_hint else ""}

OUTPUT FORMAT (example):
```
NODES:
  1. "Start"        ellipse       x=200  y=50   80x80
  2. "Validate"     rectangle     x=170  y=200  120x60
  3. "Valid?"        diamond       x=180  y=320  100x80

CONNECTIONS:
  Start → Validate              label=""
  Validate → Valid?             label="check"

BINDINGS:
  Group A: [Start, Validate, Valid?]
```

After confirming the plan, proceed with the `draw_diagram` prompt."""
                    )
                )
            ]
        )

    elif name == "draw_diagram":
        plan = (arguments or {}).get("plan", "")
        file_path = (arguments or {}).get("file_path", "")

        save_step = ""
        if file_path:
            save_step = f"\n5. **Save**: `save_diagram(path=\"{file_path}\")`"
        else:
            save_step = "\n5. **Save**: Ask the user for a file path, then `save_diagram(path=...)`"

        return GetPromptResult(
            description="Draw diagram from plan",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Execute the following plan by calling tools in order:

PLAN:
{plan}

STEPS:
1. **Create diagram**: `create_diagram()`
2. **Add all shapes**: Call `add_shape(...)` for each node in the plan — or, preferably, bundle them into a single `batch_operations(operations=[{{"op": "add_shape", ...}}, ...])` call.
   - Use exact (x, y, width, height) from the plan
   - Record the returned shape IDs
3. **Bind related groups**: use `batch_operations` with `{{"op": "bind_nodes", "node_ids": [...]}}` for each binding group
4. **Add connections**: Call `add_connection(source_id=..., target_id=..., ...)` for each edge — again, `batch_operations` is the preferred way for more than one edge{save_step}

RULES:
- Create ALL shapes before adding connections
- Bind groups IMMEDIATELY after creating their shapes
- Use entry_x/entry_y/exit_x/exit_y for precise connection points when layout matters
- For complex UML class diagrams:
  - Create domain containers first, then classes inside with parent_id
  - Prefer orthogonal edges and add waypoints when avoiding crossings

After drawing, use the `review_diagram` prompt to optimize."""
                    )
                )
            ]
        )

    elif name == "review_diagram":
        return GetPromptResult(
            description="Review and optimize diagram layout",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Review the current diagram and optimize its layout:

STEPS:
1. **Inspect**: `list_cells()` — check positions, bounds, and binding info
2. **Detect overlaps**: `detect_overlaps()` — find node–node overlaps and out-of-container violations
3. **Detect crossings**: `detect_line_crossings()` — find overlapping connections
4. **Suggest bindings**: `suggest_bindings()` — discover ungrouped related nodes
5. **Fix issues**:
    - Each issue returned by `detect_overlaps` / `detect_line_crossings` / `suggest_bindings` carries a structured `fix` field — execute it verbatim via `batch_operations`.
    - For bulk overlap resolution, call `auto_layout_adjust` once and let the server push shapes apart.
    - Move nodes manually with `move_shape` only when finer control is needed (bound nodes follow).
    - Adjust waypoints/anchors with `update_cell(cell_id=..., waypoints=[...], entry_x=..., exit_x=..., label_offset_x=..., label_offset_y=...)`.
5. **Complex UML class diagram checklist**:
   - Nodes must be fully inside their domain containers
   - Domain containers must not overlap each other
   - Class nodes within each domain must not overlap each other
   - Nodes from different domains (or standalone nodes) must not overlap each other
   - Orthogonal polylines should avoid crossings where possible
6. **Verify**: Run `detect_overlaps()` and `detect_line_crossings()` again to confirm fixes
7. **Save**: `save_diagram(path=...)` when satisfied

COMMON FIXES:
- Overlapping shapes → `auto_layout_adjust()` (bulk) or follow the structured `fix` returned by `detect_overlaps`
- Crossed connections → apply the `fix` returned by `detect_line_crossings` (inserts waypoints via `update_cell`)
- Unbound related nodes → apply the `fix` returned by `suggest_bindings` via `batch_operations`
- Nodes outside containers → apply the `fix` returned by `detect_overlaps.out_of_container`"""
                    )
                )
            ]
        )

    else:
        return GetPromptResult(
            description=f"Unknown prompt: {name}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"Prompt '{name}' not found. Available prompts: plan_diagram, draw_diagram, review_diagram."
                    )
                )
            ]
        )
