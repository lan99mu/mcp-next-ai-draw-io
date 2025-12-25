# MCP Draw.io 服务器

基于 Python 的 Model Context Protocol (MCP) 服务器，用于生成 Draw.io 图表文件。

## 简介

这是一个 Python 实现的 MCP 服务器，可以配合 VS Code 的 Copilot 和 Draw.io 插件来生成图表。服务器提供了创建图表、添加形状、连接形状等功能，输出标准的 Draw.io XML 格式文件。

**注意：** 本服务器仅负责**生成** Draw.io 文件，不包含渲染功能。需要使用 Draw.io 软件查看和编辑生成的图表。

## 特性

- ✍️ **生成 Draw.io XML 文件** - 以编程方式创建 .drawio 图表文件
- 🔷 **多种形状类型** - 支持矩形、椭圆、菱形等多种形状
- 🔗 **连接形状** - 在形状之间添加带自定义箭头的连接线
- 💾 **标准格式** - 输出与 Draw.io 和 diagrams.net 兼容
- 🤖 **MCP 兼容** - 可与 VS Code Copilot 等 MCP 客户端配合使用
- 📦 **轻量级** - 简单的 Python 实现，依赖最少

## 安装

### 前置要求

- Python 3.10 或更高版本
- VS Code 安装了 Draw.io 扩展
- MCP 兼容的客户端（如 Claude Desktop、VS Code Copilot）

### 安装步骤

1. 克隆仓库：
```bash
git clone https://github.com/lan99mu/mcp-next-ai-draw-io.git
cd mcp-next-ai-draw-io
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

或者以开发模式安装：
```bash
pip install -e .
```

## 配置

### VS Code Copilot

在 MCP 配置文件中添加：

**macOS/Linux**: `~/.config/mcp/settings.json`  
**Windows**: `%APPDATA%\mcp\settings.json`

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

### Claude Desktop

在 Claude Desktop 配置文件中添加（macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`）：

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

## 使用方法

配置完成后，可以让 AI 助手创建图表。示例提示：

### 创建简单流程图

```
使用 Draw.io MCP 服务器创建一个用户登录流程图：
1. 开始
2. 输入凭据
3. 验证（使用菱形）
4. 如果有效，跳转到仪表板
5. 如果无效，显示错误
```

### 创建系统架构图

```
创建一个系统架构图，包含：
- 浏览器（客户端）
- 负载均衡器
- 三个 API 服务器
- 数据库
并适当连接它们。
```

## 可用工具

MCP 服务器提供以下工具：

### `create_diagram`
创建新的 Draw.io 图表。
- **参数：**
  - `name`（可选）：图表名称（默认："Untitled"）

### `add_shape`
向图表添加形状/节点。
- **参数：**
  - `label`（必需）：形状的标签文本
  - `x`（可选）：X 坐标（默认：0）
  - `y`（可选）：Y 坐标（默认：0）
  - `width`（可选）：形状宽度（默认：120）
  - `height`（可选）：形状高度（默认：60）
  - `shape_type`（可选）：形状类型 - `rectangle`、`ellipse`、`diamond`、`parallelogram`、`hexagon`、`cylinder`、`cloud`（默认："rectangle"）
  - `style`（可选）：自定义 Draw.io 样式字符串

### `add_connection`
在两个形状之间添加连接/边。
- **参数：**
  - `source_id`（必需）：源形状的 ID
  - `target_id`（必需）：目标形状的 ID
  - `label`（可选）：连接的标签文本
  - `arrow_type`（可选）：箭头类型 - `classic`、`block`、`open`、`oval`、`diamond`、`none`（默认："classic"）
  - `style`（可选）：自定义 Draw.io 样式字符串

### `get_diagram`
获取当前图表的 Draw.io XML 格式。

### `list_shapes`
列出图表中的所有形状及其 ID 和标签。

## 输出格式

服务器生成 Draw.io XML 格式的图表，可以：
- 保存为 `.drawio` 文件
- 在 VS Code 的 Draw.io 扩展中打开
- 在 Draw.io 桌面应用程序中打开
- 在 https://app.diagrams.net/ 中打开

## 工作原理

1. MCP 服务器作为后台进程运行
2. 通过 stdio 与 MCP 客户端（如 VS Code Copilot）通信
3. 当收到提示时，AI 助手调用服务器的工具来：
   - 在内存中创建图表结构
   - 添加形状和连接
   - 生成与 Draw.io 兼容的 XML
4. 生成的 XML 可以保存到 `.drawio` 文件
5. 在 Draw.io（VS Code 扩展、桌面应用或 Web）中打开文件以查看和编辑

**重要：** 本服务器仅**生成** Draw.io 文件，不**渲染**图表。需要 Draw.io 软件来可视化输出。

## 支持的形状类型

### 预定义形状（为方便使用）

服务器提供 7 种常用的预定义形状类型：

- **rectangle**：标准矩形框
- **ellipse**：圆形/椭圆形
- **diamond**：菱形（常用于决策点）
- **parallelogram**：平行四边形（常用于输入/输出）
- **hexagon**：六边形（常用于准备步骤）
- **cylinder**：圆柱形（常用于数据库）
- **cloud**：云形（常用于云服务）

### 所有 Draw.io 形状（通过自定义样式）

**服务器支持所有 Draw.io 形状**，通过 `style` 参数可以使用任何 Draw.io 图标：

```python
# 自定义 Draw.io 形状示例：

# 人形图标（UML Actor）
add_shape(label="用户", style="shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;")

# 数据库图标
add_shape(label="MySQL", style="shape=datastore;whiteSpace=wrap;html=1;")

# 文档图标
add_shape(label="报告", style="shape=document;whiteSpace=wrap;html=1;")

# 进程/齿轮图标
add_shape(label="处理中", style="shape=process;whiteSpace=wrap;html=1;backgroundOutline=1;")

# 箭头图标
add_shape(label="方向", style="shape=singleArrow;whiteSpace=wrap;html=1;")

# 还有数百种其他形状...
```

获取任何 Draw.io 形状的样式字符串：
1. 在 Draw.io 中创建该形状
2. 右键点击 → 编辑样式（Edit Style）
3. 复制样式字符串并在 `style` 参数中使用

## 测试

运行功能测试：

```bash
python test_functionality.py
```

这将生成几个示例 .drawio 文件到 `/tmp` 目录。

## 项目结构

```
mcp-next-ai-draw-io/
├── mcp_drawio_server.py    # MCP 服务器主实现
├── pyproject.toml           # 项目配置
├── requirements.txt         # Python 依赖
├── test_functionality.py    # 功能测试
├── README.md               # 英文说明文档
├── README_CN.md            # 中文说明文档（本文件）
└── EXAMPLES.md             # 使用示例
```

## 故障排除

### 服务器无法连接
- 验证 Python 3.10+ 已安装：`python --version`
- 检查 MCP 配置中的路径是否正确
- 确保已安装依赖：`pip install -r requirements.txt`

### 图表无法正确渲染
- 确保将输出保存为 `.drawio` 文件
- 使用 Draw.io 扩展或应用打开
- 检查输出中的 XML 是否完整

### 工具调用不起作用
- 重启 MCP 客户端（VS Code、Claude Desktop 等）
- 检查服务器日志是否有错误
- 验证 MCP 配置文件位置是否正确

## 参考

- 参考项目：[next-ai-draw-io](https://github.com/DayuanJiang/next-ai-draw-io)
- 基于：[Model Context Protocol](https://modelcontextprotocol.io/)
- 兼容：[Draw.io](https://www.drawio.com/)

## 许可证

MIT License
