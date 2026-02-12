# Demo: Tool-Focused MCP Workflow

This demonstrates how the refactored MCP server enables Copilot/Agent to have full control over workflows.

## Scenario 1: Create and Modify

**User Request:** "Create a flowchart and then change the Start node to green"

**Copilot's Workflow:**
1. `create_diagram(name="Flowchart")`
2. `add_shape(label="Start", x=100, y=50, shape_type="ellipse")` → returns `shape_1`
3. `add_shape(label="Process", x=100, y=150)` → returns `shape_2`
4. `add_connection(source_id="shape_1", target_id="shape_2")`
5. `save_diagram(path="flowchart.drawio")`
6. `load_diagram(path="flowchart.drawio")`
7. `update_cell(cell_id="shape_1", style="fillColor=#00FF00")`
8. `save_diagram(path="flowchart.drawio")`

**Result:** Copilot orchestrates multiple tools to achieve the goal.

## Scenario 2: Inspect and Refactor Existing Diagram

**User Request:** "Load my architecture diagram and tell me what's in it, then make all databases blue"

**Copilot's Workflow:**
1. `load_diagram(path="architecture.drawio")`
2. `list_cells()` → sees all cells with IDs
3. Analyze and present summary to user
4. `update_cell(cell_id="db1", style="fillColor=#0000FF")`
5. `update_cell(cell_id="db2", style="fillColor=#0000FF")`
6. `save_diagram(path="architecture.drawio")`

**Result:** Copilot reads, understands, and modifies existing diagrams.

## Scenario 3: Complex Transformation

**User Request:** "Load workflow.drawio and replace all decision diamonds with hexagons"

**Copilot's Workflow:**
1. `load_diagram(path="workflow.drawio")`
2. `list_cells()` → identify all diamonds
3. For each diamond cell:
   - `get_cell(cell_id="diamond_X")` → get current properties
   - `delete_cell(cell_id="diamond_X")`
   - `add_shape(label=..., x=..., y=..., shape_type="hexagon")`
   - Update any connections that referenced the old cell
4. `save_diagram(path="workflow.drawio")`

**Result:** Copilot performs complex transformations using simple tools.

## Why This Design Works

### ✅ Advantages:
- **Flexibility**: Copilot can create any workflow
- **Composability**: Tools combine in unlimited ways
- **Simplicity**: Each tool does one thing well
- **Maintainability**: MCP server has minimal logic
- **Extensibility**: Easy to add new tools without changing workflows

### ❌ vs. Complex MCP Server:
If the MCP server tried to do all this internally:
- Would need to anticipate every possible workflow
- Would mix tool layer with application layer
- Would be harder to maintain and extend
- Would limit what Copilot can do

## The Right Abstraction Level

```
┌─────────────────────────────────────┐
│ HIGH LEVEL (Copilot/Agent)          │
│ - Understand user intent            │
│ - Plan multi-step workflows         │
│ - Handle errors and edge cases      │
│ - Present results to user           │
└─────────────────▲───────────────────┘
                  │
┌─────────────────┴───────────────────┐
│ LOW LEVEL (MCP Server)              │
│ - load_diagram                      │
│ - list_cells                        │
│ - update_cell                       │
│ - save_diagram                      │
│ - ... (simple, focused tools)       │
└─────────────────────────────────────┘
```

This separation allows each layer to do what it does best!
