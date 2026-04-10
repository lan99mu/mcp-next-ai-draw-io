# MCP Draw.io Server

> **Python 3.10+ Required**

A Model Context Protocol (MCP) server for creating, inspecting, and editing Draw.io diagrams.

[中文说明](./README_CN.md)

## Quick Start

```bash
git clone https://github.com/lan99mu/mcp-next-ai-draw-io.git
cd mcp-next-ai-draw-io
pip install -r requirements.txt
```

### Configure MCP Client

**VS Code Copilot** (`.vscode/mcp.json`):
```json
{
  "servers": {
    "drawio": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "mcp_drawio_server"],
      "cwd": "/path/to/mcp-next-ai-draw-io"
    }
  }
}
```

**Claude Desktop**:
```json
{
  "mcpServers": {
    "drawio": {
      "command": "python",
      "args": ["-m", "mcp_drawio_server"],
      "cwd": "/path/to/mcp-next-ai-draw-io"
    }
  }
}
```

## Workflow

| Scenario | Steps |
|----------|-------|
| New diagram | `create_diagram` → `add_shape` → `add_connection` → `save_diagram` |
| Edit existing | `load_diagram` → `list_cells` → `update_cell` / `delete_cell` → `save_diagram` |
| Layout tuning | `list_cells` → `bind_nodes` → `move_shape` → `detect_line_crossings` |

## Tool Reference

### File Operations

| Tool | Description |
|------|-------------|
| `create_diagram` | Create a new diagram in memory |
| `load_diagram` | Load an existing `.drawio` file |
| `save_diagram` | Save diagram to a `.drawio` file |

### Inspection

| Tool | Description |
|------|-------------|
| `list_cells` | List all shapes and connections with positions and bindings |
| `get_cell` | Get detailed geometry and bindings for one cell |

### Shapes & Connections

| Tool | Description |
|------|-------------|
| `add_shape` | Add a shape (rectangle, ellipse, diamond, cylinder, cloud, UML class, swimlane, etc.) |
| `add_connection` | Add a connection with label, entry/exit points, waypoints, and styling |
| `update_cell` | Update label, position, size, or style of any cell |
| `delete_cell` | Remove a cell from the diagram |

### Binding & Layout

| Tool | Description |
|------|-------------|
| `bind_nodes` | Bind nodes so they move together as a group |
| `unbind_nodes` | Remove nodes from a binding group |
| `get_bound_nodes` | Query which nodes are bound to a given node |
| `move_shape` | Move a shape (bound nodes follow automatically) |
| `suggest_bindings` | Get intelligent binding suggestions based on proximity and naming |
| `detect_line_crossings` | Detect crossing connections and get fix suggestions |

### MCP Prompts (Progressive Guidance)

Use `prompts/list` and `prompts/get` to access step-by-step workflow templates:

| Prompt | Use When |
|--------|----------|
| `plan_diagram` | Starting a new diagram — clarify structure before drawing |
| `draw_diagram` | Ready to create shapes and connections |
| `review_diagram` | Diagram complete — optimize layout and fix crossings |

### MCP Resources (On-Demand Docs)

Use `resources/read` to fetch detailed documentation only when needed:

| Resource URI | Content |
|-------------|---------|
| `docs://tools/overview` | Full tool parameter reference |
| `docs://bindings/guide` | Binding patterns and efficiency tips |
| `docs://workflows/best-practices` | Workflow optimization strategies |
| `docs://shapes/reference` | All shape types with style examples |

## Supported Shapes

**Basic**: `rectangle`, `ellipse`, `diamond`, `parallelogram`, `hexagon`, `cylinder`, `cloud`

**Activity Diagram**: `activity_start`, `activity_end`, `activity_action`, `activity_decision`, `activity_fork`, `activity_join`, `activity_send_signal`, `activity_receive_signal`, `activity_note`

**Swimlane**: `swimlane_pool`, `swimlane_h`, `swimlane_v`, `container`

**UML Class**: `uml_class`, `uml_interface`, `uml_abstract_class`, `uml_enum`, `uml_package`, `uml_note`

Custom shapes can be specified via the `style` parameter.

## Testing

```bash
python -m pytest tests/ -v
```

## Design Philosophy

The MCP server is a **tool layer**, not an application layer:
```
Copilot/Agent (reasoning & workflow)
    ↓
MCP Server (tool operations)
    ↓
File System (storage)
```

## License

MIT License

## Acknowledgments

- Inspired by [next-ai-draw-io](https://github.com/DayuanJiang/next-ai-draw-io)
- Built with [Model Context Protocol](https://modelcontextprotocol.io/)
- Compatible with [Draw.io](https://www.drawio.com/)
