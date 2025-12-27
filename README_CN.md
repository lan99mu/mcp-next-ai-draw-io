# MCP Draw.io 服务器

基于 Python 的 Model Context Protocol (MCP) 服务器，提供**简洁、专注的工具**来操作 Draw.io 图表。

[English](./README.md) | 中文

## 🎯 设计理念

此 MCP 服务器遵循 **工具封装** 而非应用逻辑的原则：

```
┌─────────────────┐
│   Copilot/Agent │  ← 负责策略、风格、推理
│    (策略层)      │
└───────▲─────────┘
        │
┌───────┴─────────┐
│  Draw.io MCP    │  ← 提供简洁工具，不做复杂逻辑
│    (工具层)      │
└───────▲─────────┘
        │
┌───────┴─────────┐
│   File System   │  ← 存储层
│    (存储层)      │
└─────────────────┘
```

**服务器负责:**
- ✅ 提供简单的工具来读取/写入/修改 .drawio 文件
- ✅ 解析和操作图表结构
- ✅ 验证 XML 格式
- ✅ 暴露图表元素以供修改

**Copilot/Agent 负责:**
- ✅ 决定工作流和策略
- ✅ 处理复杂推理
- ✅ 管理用户意图和风格
- ✅ 协调工具使用

## 特性

### 核心能力

- 📁 **加载和保存** - 读取现有 .drawio 文件并保存修改
- 🔍 **检查** - 列出和检查图表元素（单元格）
- ✏️ **修改** - 通过 ID 更新、添加或删除特定元素
- ⚡ **直接 XML** - 访问和操作原始 Draw.io XML
- 🏗️ **创建** - 从头开始以编程方式构建图表
- 🔷 **形状类型** - 支持多种预定义形状
- 🎨 **样式** - 自定义 Draw.io 样式字符串以实现高级控制

### 相比基础版本的改进

相比简单的"生成 XML"服务器，此版本提供：

1. **文件操作** - 加载和修改现有图表，而不仅仅是创建新图表
2. **元素级控制** - 通过 ID 更新/删除特定元素
3. **检查工具** - 在修改之前了解图表结构
4. **灵活的工作流** - Copilot 决定如何使用工具，而不是 MCP 服务器

## 安装

### 前置要求

- Python 3.10 或更高版本
- MCP 兼容的客户端（VS Code Copilot、Claude Desktop 等）

### 设置

1. 克隆仓库：
```bash
git clone https://github.com/lan99mu/mcp-next-ai-draw-io.git
cd mcp-next-ai-draw-io
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 配置

### VS Code Copilot

在 MCP 设置配置文件中添加：

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

### Claude Desktop

在 Claude Desktop 配置文件中添加：

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

## 使用示例

### 示例 1：创建新图表

```
用户："创建一个包含开始、处理和结束节点的简单流程图"

Copilot 将：
1. 调用 create_diagram
2. 为每个节点调用 add_shape
3. 调用 add_connection 链接它们
4. 调用 save_diagram 保存结果
```

### 示例 2：修改现有图表

```
用户："加载 diagram.drawio 并将所有矩形改为蓝色"

Copilot 将：
1. 调用 load_diagram 指定路径
2. 调用 list_cells 查看所有元素
3. 为每个矩形调用 update_cell 更新样式
4. 调用 save_diagram 保存更改
```

### 示例 3：检查和报告

```
用户："显示 architecture.drawio 的结构"

Copilot 将：
1. 调用 load_diagram
2. 调用 list_cells 获取所有元素
3. 向用户呈现摘要
```

## 工具参考

### 文件操作

| 工具 | 描述 | 关键参数 |
|------|------|----------|
| `load_diagram` | 加载现有 .drawio 文件 | `path` |
| `save_diagram` | 保存图表到文件 | `path` |
| `get_diagram_xml` | 获取原始 XML 内容 | 无 |
| `set_diagram_xml` | 从原始 XML 设置 | `xml` |

### 检查工具

| 工具 | 描述 | 关键参数 |
|------|------|----------|
| `list_cells` | 列出所有图表元素 | 无 |
| `get_cell` | 获取单元格详细信息 | `cell_id` |

### 修改工具

| 工具 | 描述 | 关键参数 |
|------|------|----------|
| `update_cell` | 更新单元格属性 | `cell_id`, `value`, `x`, `y`, `style` 等 |
| `delete_cell` | 删除单元格 | `cell_id` |
| `add_shape` | 添加新形状 | `label`, `x`, `y`, `shape_type` 等 |
| `add_connection` | 添加连接 | `source_id`, `target_id`, `label` 等 |

### 创建工具

| 工具 | 描述 | 关键参数 |
|------|------|----------|
| `create_diagram` | 创建新图表 | `name`（可选）|

## 支持的形状类型

- `rectangle` - 标准矩形框
- `ellipse` - 圆形/椭圆形
- `diamond` - 菱形（用于决策）
- `parallelogram` - 平行四边形（用于输入/输出）
- `hexagon` - 六边形（用于准备）
- `cylinder` - 圆柱形（用于数据库）
- `cloud` - 云形（用于云服务）

可以通过 `style` 参数使用 Draw.io 样式字符串来使用自定义形状。

## 测试

运行测试套件：

```bash
# 基本功能测试
python test_functionality.py

# 文件操作测试
python test_file_operations.py
```

## 项目结构

```
mcp-next-ai-draw-io/
├── mcp_drawio_server.py      # 主 MCP 服务器
├── test_functionality.py      # 基本测试
├── test_file_operations.py    # 文件操作测试
├── pyproject.toml             # 项目配置
├── requirements.txt           # 依赖
└── README.md                  # 英文文档
```

## 为什么这样设计？

参考 [next-ai-draw-io](https://github.com/DayuanJiang/next-ai-draw-io) 项目后，我们意识到：

**❌ 错误方法（应用层逻辑）:**
- 在 MCP 服务器中构建复杂的工作流
- 添加浏览器预览、版本历史、HTTP 服务器
- 对用户工作流做决策
- 混合工具层和应用层

**✅ 正确方法（工具层封装）:**
- 提供简单、专注的工具
- 让 Copilot/Agent 处理工作流和推理
- 保持 MCP 服务器作为"纯粹"的工具提供者
- 专注于干净的文件操作
- 关注点分离

MCP 服务器是**工具层**，而非**应用层**。

这符合 MCP 的理念：

```
Copilot/Agent (策略、推理) 
    ↓
MCP Server (工具封装)
    ↓  
File System (存储)
```

## 贡献

欢迎贡献！请随时提交 Pull Request。

## 许可证

MIT License

## 致谢

- 灵感来源：[next-ai-draw-io](https://github.com/DayuanJiang/next-ai-draw-io)
- 构建于：[Model Context Protocol](https://modelcontextprotocol.io/)
- 兼容：[Draw.io](https://www.drawio.com/)
