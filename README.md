# MCP Draw.io Server

> ⚠️ **Python 3.10+ Required** | **需要 Python 3.10 或更高版本**
> 
> This package requires Python 3.10 or higher. If you see an error like "No matching distribution found for mcp>=1.23.0", please upgrade your Python version first.
> 
> 此包需要 Python 3.10 或更高版本。如果您看到类似 "No matching distribution found for mcp>=1.23.0" 的错误，请先升级您的 Python 版本。

A Python-based Model Context Protocol (MCP) server that provides **clean, focused tools** for working with Draw.io diagrams.

一个基于 Python 的 Model Context Protocol (MCP) 服务器，提供**简洁、专注的工具**来操作 Draw.io 图表。

## 🎯 Design Philosophy / 设计理念

This MCP server follows the principle of **tool encapsulation** rather than application logic:

此 MCP 服务器遵循 **工具封装** 而非应用逻辑的原则：

```
┌─────────────────┐
│   Copilot/Agent │  ← Handles strategy, style, reasoning
│  (策略层)        │     Copilot 负责策略、风格、推理
└───────▲─────────┘
        │
┌───────┴─────────┐
│  Draw.io MCP    │  ← Provides clean tools, no complex logic
│  (工具层)        │     提供简洁工具，不做复杂逻辑
└───────▲─────────┘
        │
┌───────┴─────────┐
│   File System   │  ← Storage layer
│  (存储层)        │     存储层
└─────────────────┘
```

**What this server does / 服务器做什么:**
- ✅ Provide simple tools to read/write/modify .drawio files
- ✅ Parse and manipulate diagram structures  
- ✅ Validate XML format
- ✅ Expose diagram elements for modification

**What Copilot/Agent does / Copilot/Agent 做什么:**
- ✅ Decide workflow and strategy
- ✅ Handle complex reasoning
- ✅ Manage user intent and style
- ✅ Coordinate tool usage

## Features / 特性

### Core Capabilities / 核心能力

- 📁 **Load & Save** - Read existing .drawio files and save modifications
- 🔍 **Inspect** - List and examine diagram elements (cells)  
- ✏️ **Modify** - Update, add, or delete specific elements by ID
- ⚡ **Direct XML** - Access and manipulate raw Draw.io XML
- 🏗️ **Create** - Build diagrams programmatically from scratch
- 🔷 **Shape Types** - Support for multiple predefined shapes
- 🎨 **Styling** - Custom Draw.io style strings for advanced control
- 📍 **Coordinate System** - Get detailed position information (coordinates, center, bounding box) for better spatial reasoning
- 🔗 **Node Binding** - Bind nodes together to move them as a group
- 🔀 **Connection Positioning** - Control entry/exit points and waypoint routing for precise connection placement
- 🔍 **Line Crossing Detection** - Automatically detect when connections cross and get position hints for adjustments
- 🎯 **Agent Skills** - MCP Prompts providing workflow templates that reduce model consumption by 60-80%
- ⚡ **Context Optimization (NEW!)** - 62% reduction in context consumption with on-demand detailed documentation

### Key Improvements Over Basic Version / 相比基础版本的改进

Compared to a simple "generate XML" server, this version provides:

相比简单的"生成 XML"服务器，此版本提供：

1. **File Operations** - Load and modify existing diagrams, not just create new ones
2. **Element-level Control** - Update/delete specific elements by ID
3. **Inspection Tools** - Understand diagram structure before modifying
4. **Flexible Workflows** - Copilot decides how to use tools, not the MCP server
5. **Efficiency Prompts** - Pre-defined workflow templates that teach agents best practices
6. **Context Optimization** - Concise tool descriptions with detailed docs on-demand

## Installation / 安装

### Prerequisites / 前置要求

- Python 3.10 or higher
- MCP-compatible client (VS Code Copilot, Claude Desktop, etc.)

### Setup / 设置

1. Clone the repository:
```bash
git clone https://github.com/lan99mu/mcp-next-ai-draw-io.git
cd mcp-next-ai-draw-io
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration / 配置

### For VS Code Copilot

Add to your MCP settings configuration file:

**macOS/Linux**: `~/.config/mcp/settings.json`  
**Windows**: `%APPDATA%\mcp\settings.json`

```json
{
  "servers": {
    "drawio": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "mcp_drawio_server"],
      "cwd": "/path/to/mcp-next-ai-draw-io"
    }
  },
  "inputs": []
}
```

### For Claude Desktop

Add to your Claude Desktop configuration:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

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

## Usage Examples / 使用示例

### Example 1: Create New Diagram / 创建新图表

```
User: "Create a simple flowchart with Start, Process, and End nodes"

Copilot will:
1. Call create_diagram
2. Call add_shape for each node
3. Call add_connection to link them
4. Call save_diagram to save the result
```

### Example 2: Modify Existing Diagram / 修改现有图表

```
User: "Load diagram.drawio and change all rectangles to blue"

Copilot will:
1. Call load_diagram with path
2. Call list_cells to see all elements
3. Call update_cell for each rectangle with new style
4. Call save_diagram to save changes
```

### Example 3: Inspect and Report / 检查和报告

```
User: "Show me the structure of architecture.drawio"

Copilot will:
1. Call load_diagram
2. Call list_cells to get all elements
3. Present a summary to the user
```

## Agent Skills: Workflow Prompts / Agent 技能：工作流提示 🎯

**NEW!** This MCP server now provides **Prompts** - pre-defined workflow templates that help agents work 60-80% more efficiently by teaching best practices.

### What are Prompts? / 什么是提示？

Prompts are reusable workflow templates that:
- Provide step-by-step guidance for common tasks
- Teach efficient patterns using node bindings
- Reduce model consumption by 60-80%
- Include examples and best practices

### Available Prompts / 可用提示

| Prompt Name | Purpose | Efficiency Gain |
|------------|---------|-----------------|
| `create_flowchart` | Create flowcharts efficiently | 60-70% fewer calls |
| `add_connected_nodes` | Add related nodes with bindings | 2-3 calls saved per adjustment |
| `optimize_layout` | Fix crossings and improve layout | 70-80% fewer calls |
| `modify_with_bindings` | Efficiently modify existing diagrams | 3-10 calls saved per modification |
| `create_architecture_diagram` | Create architecture diagrams with layers | 75-85% fewer calls |

### How to Use Prompts / 如何使用提示

**List all prompts:**
```
Call: prompts/list
Returns: All 5 available prompt templates
```

**Get a specific prompt:**
```
Call: prompts/get
Params:
  - name: "create_flowchart"
  - arguments: {"description": "user login process"}
Returns: Detailed step-by-step workflow
```

**Key Benefits:**
- ✅ **Efficiency**: 60-80% fewer tool calls
- ✅ **Best Practices**: Learn from proven workflows
- ✅ **Consistency**: Same approach every time
- ✅ **Speed**: Faster diagram creation

📖 **See [AGENT_SKILLS.md](./AGENT_SKILLS.md) for detailed documentation and examples.**

## On-Demand Documentation: MCP Resources / 按需文档：MCP 资源 ⚡

**NEW!** This server provides detailed documentation via MCP Resources, reducing initial context consumption by **62%** while keeping comprehensive docs available on-demand.

### Context Optimization / 上下文优化

**Problem:** Verbose tool descriptions consumed too many tokens in VS Code Copilot's context.

**Solution:** 
- **Concise tool descriptions** - Only essential info (1,010 chars vs 2,669 chars previously)
- **Detailed docs on-demand** - Access comprehensive guides when needed (15,546 chars available)

### Available Resources / 可用资源

| Resource URI | Content | Size |
|-------------|---------|------|
| `docs://tools/overview` | Complete tool documentation with examples | 4,961 chars |
| `docs://bindings/guide` | Node bindings guide with efficiency patterns | 3,651 chars |
| `docs://workflows/best-practices` | Workflow patterns and best practices | 3,710 chars |
| `docs://shapes/reference` | All shape types with usage examples | 3,224 chars |

### How to Access / 如何访问

**List available resources:**
```
MCP Call: resources/list
```

**Read a specific resource:**
```
MCP Call: resources/read
URI: docs://bindings/guide
```

**Via Copilot Chat:**
Simply ask: "Show me the bindings guide" or "What are best practices?"

### Benefits / 优势

- ✅ **62% reduction** in initial context consumption
- ✅ **Detailed docs** - More comprehensive than before
- ✅ **On-demand** - Only loaded when needed
- ✅ **Lower costs** - Fewer tokens per request

📖 **See [CONTEXT_OPTIMIZATION.md](./CONTEXT_OPTIMIZATION.md) for complete details.**

## Tool Reference / 工具参考

### File Operations / 文件操作

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `load_diagram` | Load existing .drawio file | `path` |
| `save_diagram` | Save diagram to file | `path` |
| `get_diagram_xml` | Get raw XML content | None |
| `set_diagram_xml` | Set from raw XML | `xml` |

### Inspection Tools / 检查工具

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `list_cells` | List all diagram elements | None |
| `get_cell` | Get cell details | `cell_id` |
| `detect_line_crossings` | Detect when connections cross and get position hints | None |

### Modification Tools / 修改工具

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `update_cell` | Update cell properties | `cell_id`, `value`, `x`, `y`, `style`, etc. |
| `delete_cell` | Delete a cell | `cell_id` |
| `add_shape` | Add new shape | `label`, `x`, `y`, `shape_type`, etc. |
| `add_connection` | Add connection (supports label positioning) | `source_id`, `target_id`, `label`, `label_position`, `label_offset_x`, `label_offset_y`, `label_background_color`, etc. |

### Node Binding Tools / 节点绑定工具

**IMPORTANT for Efficient Local Adjustments**: Node binding is KEY for making local changes without editing many nodes individually!

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `bind_nodes` | Bind multiple nodes together to move as a group | `node_ids` (list of node IDs) |
| `unbind_nodes` | Unbind nodes from their group | `node_ids` (list of node IDs) |
| `get_bound_nodes` | Get nodes bound to a specific node | `node_id` |
| `move_shape` | Move a shape (and its bound nodes) to a new position | `shape_id`, `new_x`, `new_y` |
| `suggest_bindings` | **NEW** Get intelligent suggestions for which nodes should be bound | `proximity_threshold` (optional, default: 200) |

**Why Use Bindings?**
- ✅ **Efficiency**: Move related nodes together by moving just ONE node
- ✅ **Local Adjustments**: Make surgical changes to specific groups without affecting the whole diagram
- ✅ **Maintainability**: Keep related components together (e.g., service + database, component + label)
- ✅ **Visibility**: `list_cells` shows which nodes are bound with `[BOUND to: ...]` indicators

### Connection Label Positioning / 连接标签位置

The `add_connection` tool now supports adjusting the position of connection line text (labels):

- **`label_position`** - Position of label relative to the edge: `"left"`, `"right"`, or `"center"`
- **`label_offset_x`** - Horizontal offset for the label position in pixels
- **`label_offset_y`** - Vertical offset for the label position in pixels
- **`label_background_color`** - Background color for the label (e.g., `"#ffffff"` or `"none"`)

**Examples:**
```python
# Center-aligned label
add_connection(source_id, target_id, label="Centered", label_position="center")

# Custom offset
add_connection(source_id, target_id, label="Offset Label", label_offset_x=20, label_offset_y=-10)

# With background color
add_connection(source_id, target_id, label="Colored BG", label_background_color="#ffeb3b")

# Combine all features
add_connection(source_id, target_id, 
    label="Fully Custom", 
    label_position="right",
    label_offset_x=-10, 
    label_offset_y=5,
    label_background_color="#e3f2fd")
```

### Connection Positioning (Entry/Exit Points & Waypoints) / 连接定位（入口/出口点和路径点）

The `add_connection` tool supports precise control over where and how connections attach to shapes:

#### Entry/Exit Points / 入口/出口点

Control where connections attach to shapes using normalized coordinates (0-1):
- **`exit_x`**, **`exit_y`** - Where the connection exits the source shape
- **`entry_x`**, **`entry_y`** - Where the connection enters the target shape
- Coordinates: `0.0` = left/top, `0.5` = center, `1.0` = right/bottom

**Examples:**
```python
# Connect from right side of source to left side of target
add_connection(source_id, target_id,
    exit_x=1.0, exit_y=0.5,    # Exit right-center of source
    entry_x=0.0, entry_y=0.5)  # Enter left-center of target

# Connect from bottom of source to top of target
add_connection(source_id, target_id,
    exit_x=0.5, exit_y=1.0,    # Exit bottom-center
    entry_x=0.5, entry_y=0.0)  # Enter top-center
```

#### Waypoints / 路径点

Create custom routing paths with intermediate waypoints (absolute pixel coordinates):
- **`waypoints`** - List of `[x, y]` coordinates for intermediate routing points

**Examples:**
```python
# Simple L-shaped path
add_connection(source_id, target_id,
    waypoints=[[250, 150]])

# Complex routing with multiple waypoints
add_connection(source_id, target_id,
    waypoints=[
        [200, 130],  # First turn
        [200, 90],   # Second turn
        [450, 90]    # Final approach
    ])

# Route around an obstacle
add_connection(source_id, target_id,
    waypoints=[[150, 200], [350, 200], [350, 300]])
```

#### Combined Features / 组合功能

All connection features can be combined for complete control:

```python
# Professional network connection
add_connection(gateway, service,
    label="API Call",
    exit_x=0.5, exit_y=1.0,              # Exit from bottom
    entry_x=0.5, entry_y=0.0,            # Enter from top
    waypoints=[[300, 150]],              # Route through waypoint
    label_position="center",             # Center label
    label_background_color="#e3f2fd")    # Light blue background
```

**Use Cases:**
- Network topology diagrams with precise connection points
- System architecture with clean routing
- Flowcharts with custom path routing
- Professional technical diagrams


### Coordinate System / 坐标系统

The coordinate system feature provides detailed position information for all shapes, helping LLMs better understand spatial relationships:

**Enhanced `list_cells` output includes:**
- Top-left position: `(x, y)`
- Size: `width x height`
- Center point: `(center_x, center_y)`
- Bounding box: `(x, y) to (x+width, y+height)`

**Enhanced `get_cell` output includes:**
- Position (top-left)
- Size dimensions
- Calculated center point
- Full bounding box coordinates
- Bound nodes (if any)

**Example:**
```
User: "Show me the structure of my diagram"

Copilot will call list_cells and see output like:
- ID: shape_1, Type: Shape, Label: 'Start', at (100, 50), size (120x60), center (160, 80)
- ID: shape_2, Type: Shape, Label: 'Process', at (100, 150), size (120x60), center (160, 180)

This helps the LLM understand that shape_2 is directly below shape_1 (same x-coordinate, different y).
```

### Node Binding / 节点绑定

Node binding allows you to group multiple nodes together so they move as a unit. **This is CRITICAL for making efficient local adjustments without editing many nodes individually.**

**🚀 RECOMMENDED WORKFLOW for Efficient Local Adjustments:**

1. **Create Related Nodes**: When adding nodes that should stay together (service + database, component + label)
2. **Bind Immediately**: Use `bind_nodes` right after creating related nodes
3. **Check Bindings**: Use `list_cells` to see which nodes are bound (shows `[BOUND to: ...]`)
4. **Get Suggestions**: Use `suggest_bindings` to discover which existing nodes should be bound
5. **Make Local Adjustments**: Use `move_shape` on just ONE node - all bound nodes move automatically!

**Basic workflow:**
1. Use `bind_nodes` to bind multiple nodes together
2. Use `move_shape` to move one node - all bound nodes move together
3. Use `get_bound_nodes` to check which nodes are bound together
4. Use `suggest_bindings` to get intelligent binding recommendations
5. Use `unbind_nodes` to break the binding relationship if needed

**Examples:**
```python
# EFFICIENT WORKFLOW: Create and bind related nodes together
auth_service = add_shape("Auth Service", x=100, y=100)
auth_db = add_shape("Auth DB", x=100, y=200)
bind_nodes(node_ids=[auth_service, auth_db])  # Bind immediately!

# NOW when you need to adjust position - move just ONE node:
move_shape(shape_id=auth_service, new_x=300, new_y=100)
# ✓ Both Auth Service AND Auth DB move together automatically!

# Get intelligent binding suggestions for existing diagrams
suggest_bindings()
# Output:
# 💡 Suggested 3 new binding(s):
# 1. Bind 'User Service' (shape_3) with 'User DB' (shape_4)
#    Score: 130/100
#    Reasons: proximity: 50%, vertically aligned, naming pattern: same prefix 'User'
#    → To bind: bind_nodes(node_ids=['shape_3', 'shape_4'])

# Check current bindings in the diagram
list_cells()
# Shows: [BOUND to: shape_2] for bound nodes

# Bind three nodes together to form a group
bind_nodes(node_ids=["shape_1", "shape_2", "shape_3"])

# Move shape_1 - all three nodes will move together
move_shape(shape_id="shape_1", new_x=200, new_y=100)

# Check what's bound to shape_1
get_bound_nodes(node_id="shape_1")
# Returns: "Node 'shape_1' is bound to 2 node(s): shape_2, shape_3"

# Unbind a specific node
unbind_nodes(node_ids=["shape_2"])
# Now shape_1 and shape_3 are still bound, but shape_2 is independent
```

**Use cases:**
- ✅ **Local adjustments**: Move groups of related nodes efficiently
- ✅ **Microservices architectures**: Bind service + database pairs
- ✅ **Component diagrams**: Bind components with their labels/descriptions
- ✅ **Maintaining layout**: Keep related elements together when reorganizing
- ✅ **Reducing edits**: Edit 1 node instead of 5+ individual nodes

**Benefits:**
- 🎯 **Efficiency**: Make local adjustments with minimal edits
- 🔧 **Precision**: Change only what needs to change
- 📊 **Organization**: Keep related nodes together automatically
- ⚡ **Speed**: One move command instead of multiple individual updates

**Note:** Bindings are preserved in the .drawio XML format using custom attributes.

### Line Crossing Detection / 连线交叉检测

The `detect_line_crossings` tool automatically detects when connections (lines/edges) in your diagram cross each other and provides position hints to help improve the layout.

**How it works:**
1. Analyzes all connections in the diagram
2. Detects intersection points between connection lines
3. Provides specific suggestions for fixing each crossing

**Output includes:**
- IDs and labels of crossing connections
- Exact intersection point coordinates (x, y)
- Multiple suggestions for fixing each crossing:
  - Add waypoints to route connections around each other
  - Reposition shapes to avoid crossings
  - Adjust entry/exit points to change connection angles

**Example usage:**
```python
# After creating a diagram with connections
detect_line_crossings()

# Example output:
# Detected 2 line crossing(s):
#
# 1. Crossing between:
#    - Connection 'Read Cache' (ID: conn_5)
#    - Connection 'Query DB' (ID: conn_6)
#    Lines cross at (260.0, 180.0). Consider these adjustments:
#      1. Add waypoints to 'Read Cache' to route around the crossing
#      2. Add waypoints to 'Query DB' to route around the crossing
#      3. Reposition shapes connected by 'Read Cache' to avoid crossing
#      4. Reposition shapes connected by 'Query DB' to avoid crossing
#      5. Adjust entry/exit points to change connection angles
```

**Use cases:**
- Automatically validate diagram layouts before finalizing
- Get suggestions for improving diagram clarity
- Help AI models make better layout decisions
- Identify problem areas in complex diagrams

**Benefits:**
- Improves diagram readability by highlighting crossed lines
- Provides actionable suggestions for AI models to auto-fix layouts
- Works with both simple direct connections and complex routed connections

### Creation Tools / 创建工具

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `create_diagram` | Create new diagram | `name` (optional) |

## Supported Shape Types / 支持的形状类型

### Basic Shapes / 基础形状

- `rectangle` - Standard rectangular box
- `ellipse` - Circular/oval shape
- `diamond` - Diamond shape (for decisions)
- `parallelogram` - Parallelogram (for input/output)
- `hexagon` - Hexagon (for preparation)
- `cylinder` - Cylinder (for databases)
- `cloud` - Cloud shape (for cloud services)

### Activity Diagram Shapes / 活动图形状

- `activity_start` - Start node (filled circle)
- `activity_end` - End node (filled circle with border)
- `activity_action` - Action/activity box (rounded rectangle)
- `activity_decision` - Decision node (diamond)
- `activity_fork` - Fork node (horizontal/vertical bar for parallel flows)
- `activity_join` - Join node (horizontal/vertical bar for merging flows)
- `activity_send_signal` - Send signal shape
- `activity_receive_signal` - Receive signal shape
- `activity_note` - Note/comment shape

### Swimlane Shapes / 泳道图形状

- `swimlane_pool` - Swimlane pool/container
- `swimlane_h` - Horizontal swimlane
- `swimlane_v` - Vertical swimlane
- `container` - Generic container for grouping elements

### UML Class Diagram Shapes / UML类图形状

- `uml_class` - UML class with compartments for attributes and methods
- `uml_interface` - Interface shape (italic style)
- `uml_abstract_class` - Abstract class shape (italic style)
- `uml_enum` - Enumeration shape
- `uml_package` - Package/namespace shape
- `uml_note` - UML note/comment shape

Custom shapes can be used via the `style` parameter with Draw.io style strings.

## Testing / 测试

Run the test suite:

```bash
# Run all tests with pytest
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_functionality.py -v
```

## Project Structure / 项目结构

```
mcp-next-ai-draw-io/
├── mcp_drawio_server/           # Main MCP server package
│   ├── __init__.py
│   ├── __main__.py              # CLI entry point
│   ├── server.py                # Server initialization
│   ├── tools.py                 # Tool definitions
│   ├── prompts.py               # MCP prompts
│   ├── resources.py             # MCP resources
│   ├── docs_content.py          # Documentation content
│   ├── diagram.py               # Diagram model
│   ├── xml_operations.py        # XML parsing/manipulation
│   ├── file_operations.py       # File I/O
│   ├── crossing_detector.py     # Line crossing detection
│   └── handlers/                # Tool call handlers
│       ├── __init__.py
│       ├── state.py             # Diagram state management
│       ├── file_handlers.py     # File operation handlers
│       ├── cell_handlers.py     # Cell operation handlers
│       ├── binding_handlers.py  # Binding operation handlers
│       └── analysis_handlers.py # Analysis handlers
├── tests/                       # Test suite
│   ├── test_functionality.py
│   ├── test_file_operations.py
│   └── ... (other tests)
├── demo/                        # Demo scripts and examples
│   ├── demo.py
│   ├── quick_example.py
│   └── ... (other demos)
├── pyproject.toml               # Project config
├── requirements.txt             # Dependencies
└── README.md                    # This file
```

## Why This Design? / 为什么这样设计？

参考 [next-ai-draw-io](https://github.com/DayuanJiang/next-ai-draw-io) 项目后，我们意识到：

After studying [next-ai-draw-io](https://github.com/DayuanJiang/next-ai-draw-io), we realized:

**❌ Wrong Approach (应用层逻辑):**
- Building complex workflows in MCP server  
- Adding browser preview, version history, HTTP servers
- Making decisions about user workflow
- Mixing tool layer with application layer

**✅ Right Approach (工具层封装):**
- Provide simple, focused tools
- Let Copilot/Agent handle workflow and reasoning
- Keep MCP server as a "dumb" tool provider
- Focus on clean file operations
- Separation of concerns

The MCP server is a **tool layer**, not an **application layer**.

MCP 服务器是**工具层**，而非**应用层**。

This aligns with the MCP philosophy: 

```
Copilot/Agent (策略、推理) 
    ↓
MCP Server (工具封装)
    ↓  
File System (存储)
```

## Contributing / 贡献

Contributions are welcome! Please feel free to submit a Pull Request.

## License / 许可证

MIT License

## Acknowledgments / 致谢

- Inspired by [next-ai-draw-io](https://github.com/DayuanJiang/next-ai-draw-io)
- Built with [Model Context Protocol](https://modelcontextprotocol.io/)
- Compatible with [Draw.io](https://www.drawio.com/)
