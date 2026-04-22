# MCP Draw.io 服务器

> **需要 Python 3.10+**

基于 Python 的 Model Context Protocol (MCP) 服务器，用于创建、检查和编辑 Draw.io 图表。

[English](./README.md) | 中文

## 快速开始

```bash
git clone https://github.com/lan99mu/mcp-next-ai-draw-io.git
cd mcp-next-ai-draw-io
pip install -r requirements.txt
```

### 配置 MCP 客户端

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

## 工作流

| 场景 | 步骤 |
|------|------|
| 新建图表 | `create_diagram` → `add_shape` → `add_connection` → `save_diagram` |
| 编辑现有 | `load_diagram` → `list_cells` → `update_cell` / `delete_cell` → `save_diagram` |
| 布局调整 | `list_cells` → `batch_operations`（`bind_nodes` + `move_shape`）→ `auto_layout_adjust` → `detect_line_crossings` |

## 工具参考

### 文件操作

| 工具 | 描述 |
|------|------|
| `create_diagram` | 在内存中创建新图表 |
| `load_diagram` | 加载现有 `.drawio` 文件 |
| `save_diagram` | 保存图表到 `.drawio` 文件 |

### 检查

| 工具 | 描述 |
|------|------|
| `list_cells` | 列出所有形状和连接，含位置与绑定信息 |
| `get_cell` | 获取某个 cell 的详细几何和绑定信息 |

### 形状与连接

| 工具 | 描述 |
|------|------|
| `add_shape` | 添加形状（矩形、椭圆、菱形、圆柱、云、UML 类、泳道等）|
| `add_connection` | 添加连接线，支持标签、入口/出口点、路径点、样式等 |
| `update_cell` | 更新任意 cell 的标签、位置、尺寸或样式 |
| `delete_cell` | 从图表中删除一个 cell |

### 绑定与布局

节点绑定（`bind_nodes` / `unbind_nodes`）已整合进 `batch_operations`。要查询节点的绑定关系，可直接调用 `get_cell`，其返回值包含 `bound_nodes` 字段。处理大量重叠时优先使用 `auto_layout_adjust`。

| 工具 | 描述 |
|------|------|
| `move_shape` | 移动单个形状（绑定节点自动跟随）|
| `auto_layout_adjust` | 迭代推开重叠形状；绑定组整体移动，不越出容器 |
| `suggest_bindings` | 智能绑定建议，每条建议附带可直接执行的 `fix` |
| `detect_line_crossings` | 检测交叉连线，每条都附带结构化 `fix` |
| `detect_overlaps` | 检测节点重叠 / 越界问题，附带结构化 `fix` |

### MCP 提示词（渐进式引导）

通过 `prompts/list` 和 `prompts/get` 获取分步骤工作流模板：

| 提示词 | 使用时机 |
|--------|----------|
| `plan_diagram` | 开始画图前 — 先明确结构再动手 |
| `draw_diagram` | 准备创建形状和连接 |
| `review_diagram` | 图表完成后 — 优化布局修复交叉 |

### MCP 资源（按需文档）

通过 `resources/read` 在需要时获取详细文档：

| 资源 URI | 内容 |
|----------|------|
| `docs://tools/overview` | 完整工具参数参考 |
| `docs://bindings/guide` | 绑定模式与效率技巧 |
| `docs://workflows/best-practices` | 工作流优化策略 |
| `docs://shapes/reference` | 所有形状类型与样式示例 |

## 支持的形状

**基础**: `rectangle`, `ellipse`, `diamond`, `parallelogram`, `hexagon`, `cylinder`, `cloud`

**活动图**: `activity_start`, `activity_end`, `activity_action`, `activity_decision`, `activity_fork`, `activity_join`, `activity_send_signal`, `activity_receive_signal`, `activity_note`

**泳道**: `swimlane_pool`, `swimlane_h`, `swimlane_v`, `container`

**UML 类图**: `uml_class`, `uml_interface`, `uml_abstract_class`, `uml_enum`, `uml_package`, `uml_note`

可通过 `style` 参数使用自定义形状。

## 测试

```bash
python -m pytest tests/ -v
```

## 设计理念

MCP 服务器是**工具层**，而非应用层：
```
Copilot/Agent（推理与工作流）
    ↓
MCP Server（工具操作）
    ↓
文件系统（存储）
```

## 许可证

MIT License

## 致谢

- 灵感来源：[next-ai-draw-io](https://github.com/DayuanJiang/next-ai-draw-io)
- 构建于：[Model Context Protocol](https://modelcontextprotocol.io/)
- 兼容：[Draw.io](https://www.drawio.com/)
