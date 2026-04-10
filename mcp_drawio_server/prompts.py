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
                    description="Diagram type: flowchart, architecture, uml_class, activity, swimlane",
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
                "architecture": "Use rectangle/cylinder/cloud. Group by layer (UI → API → Data). Space layers 250px apart vertically.",
                "uml_class": "Use shape_type: uml_class. Label format: 'ClassName<br>───────<br>- attr: type<br>───────<br>+ method()'.",
                "activity": "Use activity_start/end/action/decision/fork/join shapes.",
                "swimlane": "Use swimlane_pool + swimlane_h/swimlane_v. Place child shapes inside with parent_id.",
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
2. **Add all shapes**: Call `add_shape(...)` for each node in the plan.
   - Use exact (x, y, width, height) from the plan
   - Record the returned shape IDs
3. **Bind related groups**: Call `bind_nodes(node_ids=[...])` for each binding group
4. **Add connections**: Call `add_connection(source_id=..., target_id=..., ...)` for each edge{save_step}

RULES:
- Create ALL shapes before adding connections
- Bind groups IMMEDIATELY after creating their shapes
- Use entry_x/entry_y/exit_x/exit_y for precise connection points when layout matters

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
1. **Inspect**: `list_cells()` — check positions, overlaps, and binding info
2. **Detect crossings**: `detect_line_crossings()` — find overlapping connections
3. **Suggest bindings**: `suggest_bindings()` — discover ungrouped related nodes
4. **Fix issues**:
   - Bind suggested groups: `bind_nodes(node_ids=[...])`
   - Move nodes to fix crossings: `move_shape(...)` (bound nodes follow)
   - Adjust waypoints or entry/exit points if connections overlap
5. **Verify**: Run `detect_line_crossings()` again to confirm fixes
6. **Save**: `save_diagram(path=...)` when satisfied

COMMON FIXES:
- Overlapping shapes → increase spacing (move_shape)
- Crossed connections → add waypoints or adjust entry/exit points
- Unbound related nodes → bind_nodes to group them"""
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
