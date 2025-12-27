# MCP Draw.io Server

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

### Key Improvements Over Basic Version / 相比基础版本的改进

Compared to a simple "generate XML" server, this version provides:

相比简单的"生成 XML"服务器，此版本提供：

1. **File Operations** - Load and modify existing diagrams, not just create new ones
2. **Element-level Control** - Update/delete specific elements by ID
3. **Inspection Tools** - Understand diagram structure before modifying
4. **Flexible Workflows** - Copilot decides how to use tools, not the MCP server

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
      "args": ["/path/to/mcp-next-ai-draw-io/mcp_drawio_server.py"]
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
      "args": ["/path/to/mcp-next-ai-draw-io/mcp_drawio_server.py"]
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

### Modification Tools / 修改工具

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `update_cell` | Update cell properties | `cell_id`, `value`, `x`, `y`, `style`, etc. |
| `delete_cell` | Delete a cell | `cell_id` |
| `add_shape` | Add new shape | `label`, `x`, `y`, `shape_type`, etc. |
| `add_connection` | Add connection (supports label positioning) | `source_id`, `target_id`, `label`, `label_position`, `label_offset_x`, `label_offset_y`, `label_background_color`, etc. |

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

### Creation Tools / 创建工具

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `create_diagram` | Create new diagram | `name` (optional) |

## Supported Shape Types / 支持的形状类型

- `rectangle` - Standard rectangular box
- `ellipse` - Circular/oval shape
- `diamond` - Diamond shape (for decisions)
- `parallelogram` - Parallelogram (for input/output)
- `hexagon` - Hexagon (for preparation)
- `cylinder` - Cylinder (for databases)
- `cloud` - Cloud shape (for cloud services)

Custom shapes can be used via the `style` parameter with Draw.io style strings.

## Testing / 测试

Run the test suite:

```bash
# Basic functionality tests
python test_functionality.py

# File operations tests
python test_file_operations.py
```

## Project Structure / 项目结构

```
mcp-next-ai-draw-io/
├── mcp_drawio_server.py      # Main MCP server
├── test_functionality.py      # Basic tests
├── test_file_operations.py    # File operation tests
├── pyproject.toml             # Project config
├── requirements.txt           # Dependencies
└── README.md                  # This file
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
