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
- 📍 **坐标系统** - 获取详细的位置信息（坐标、中心点、边界框）以便更好地进行空间推理
- 🔗 **节点绑定** - 将节点绑定在一起，作为一组移动
- 🔀 **连接定位** - 控制入口/出口点和路径点，实现精确的连接位置
- 🔍 **连线交叉检测** - 自动检测连线交叉并提供位置调整提示

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
      "args": ["-m", "mcp_drawio_server"],
      "cwd": "/path/to/mcp-next-ai-draw-io"
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
      "args": ["-m", "mcp_drawio_server"],
      "cwd": "/path/to/mcp-next-ai-draw-io"
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
| `detect_line_crossings` | 检测连线交叉并获取位置调整提示 | 无 |

### 修改工具

| 工具 | 描述 | 关键参数 |
|------|------|----------|
| `update_cell` | 更新单元格属性 | `cell_id`, `value`, `x`, `y`, `style` 等 |
| `delete_cell` | 删除单元格 | `cell_id` |
| `add_shape` | 添加新形状 | `label`, `x`, `y`, `shape_type` 等 |
| `add_connection` | 添加连接（支持标签位置调整）| `source_id`, `target_id`, `label`, `label_position`, `label_offset_x`, `label_offset_y`, `label_background_color` 等 |

### 节点绑定工具

**重要提示：高效局部调整**：节点绑定是避免逐个编辑大量节点的关键功能！

| 工具 | 描述 | 关键参数 |
|------|------|----------|
| `bind_nodes` | 将多个节点绑定在一起作为一组移动 | `node_ids`（节点 ID 列表）|
| `unbind_nodes` | 将节点从其组中解除绑定 | `node_ids`（节点 ID 列表）|
| `get_bound_nodes` | 获取与特定节点绑定的节点 | `node_id` |
| `move_shape` | 将形状（及其绑定的节点）移动到新位置 | `shape_id`, `new_x`, `new_y` |
| `suggest_bindings` | **新功能** 智能推荐哪些节点应该绑定 | `proximity_threshold`（可选，默认：200）|

**为什么使用绑定？**
- ✅ **效率**：只移动一个节点，相关节点自动一起移动
- ✅ **局部调整**：对特定组进行精确修改，不影响整个图表
- ✅ **可维护性**：保持相关组件在一起（如服务+数据库、组件+标签）
- ✅ **可见性**：`list_cells` 显示哪些节点已绑定，带有 `[BOUND to: ...]` 标识

### 连接标签位置

`add_connection` 工具现在支持调整连接线文字（标签）的位置：

- **`label_position`** - 标签相对于连接线的位置：`"left"`（左侧）、`"right"`（右侧）或 `"center"`（居中）
- **`label_offset_x`** - 标签的水平偏移量（像素）
- **`label_offset_y`** - 标签的垂直偏移量（像素）
- **`label_background_color`** - 标签的背景颜色（如 `"#ffffff"` 或 `"none"`）

**示例：**
```python
# 标签居中
add_connection(source_id, target_id, label="居中标签", label_position="center")

# 自定义偏移
add_connection(source_id, target_id, label="偏移标签", label_offset_x=20, label_offset_y=-10)

# 带背景色
add_connection(source_id, target_id, label="彩色背景", label_background_color="#ffeb3b")

# 组合使用所有功能
add_connection(source_id, target_id, 
    label="完整自定义", 
    label_position="right",
    label_offset_x=-10, 
    label_offset_y=5,
    label_background_color="#e3f2fd")
```

### 连接定位（入口/出口点和路径点）

`add_connection` 工具支持精确控制连接线如何以及在何处附着到形状上：

#### 入口/出口点

使用归一化坐标（0-1）控制连接线附着到形状的位置：
- **`exit_x`**, **`exit_y`** - 连接线从源形状的哪里退出
- **`entry_x`**, **`entry_y`** - 连接线从哪里进入目标形状
- 坐标：`0.0` = 左/上，`0.5` = 中间，`1.0` = 右/下

**示例：**
```python
# 从源的右侧连接到目标的左侧
add_connection(source_id, target_id,
    exit_x=1.0, exit_y=0.5,    # 从源的右中退出
    entry_x=0.0, entry_y=0.5)  # 从目标的左中进入

# 从源的底部连接到目标的顶部
add_connection(source_id, target_id,
    exit_x=0.5, exit_y=1.0,    # 从底部中心退出
    entry_x=0.5, entry_y=0.0)  # 从顶部中心进入
```

#### 路径点

使用中间路径点（绝对像素坐标）创建自定义路由路径：
- **`waypoints`** - `[x, y]` 坐标列表，用于中间路由点

**示例：**
```python
# 简单的 L 形路径
add_connection(source_id, target_id,
    waypoints=[[250, 150]])

# 具有多个路径点的复杂路由
add_connection(source_id, target_id,
    waypoints=[
        [200, 130],  # 第一个转弯
        [200, 90],   # 第二个转弯
        [450, 90]    # 最终接近
    ])

# 绕过障碍物的路由
add_connection(source_id, target_id,
    waypoints=[[150, 200], [350, 200], [350, 300]])
```

#### 组合功能

所有连接功能可以组合使用以实现完全控制：

```python
# 专业的网络连接
add_connection(gateway, service,
    label="API 调用",
    exit_x=0.5, exit_y=1.0,              # 从底部退出
    entry_x=0.5, entry_y=0.0,            # 从顶部进入
    waypoints=[[300, 150]],              # 通过路径点路由
    label_position="center",             # 居中标签
    label_background_color="#e3f2fd")    # 浅蓝色背景
```

**使用场景：**
- 具有精确连接点的网络拓扑图
- 具有清晰路由的系统架构图
- 具有自定义路径路由的流程图
- 专业技术图表


### 坐标系统

坐标系统功能为所有形状提供详细的位置信息，帮助大语言模型更好地理解空间关系：

**增强的 `list_cells` 输出包括：**
- 左上角位置：`(x, y)`
- 尺寸：`宽度 x 高度`
- 中心点：`(center_x, center_y)`
- 边界框：`(x, y) 到 (x+width, y+height)`

**增强的 `get_cell` 输出包括：**
- 位置（左上角）
- 尺寸大小
- 计算的中心点
- 完整的边界框坐标
- 绑定的节点（如果有）

**示例：**
```
用户："显示我的图表结构"

Copilot 将调用 list_cells 并看到如下输出：
- ID: shape_1, Type: Shape, Label: '开始', at (100, 50), size (120x60), center (160, 80)
- ID: shape_2, Type: Shape, Label: '处理', at (100, 150), size (120x60), center (160, 180)

这帮助大模型理解 shape_2 在 shape_1 正下方（相同的 x 坐标，不同的 y 坐标）。
```

### 节点绑定

节点绑定允许您将多个节点组合在一起，使它们作为一个单元移动。**这是进行高效局部调整而无需逐个编辑大量节点的关键功能。**

**🚀 推荐工作流程：高效局部调整**

1. **创建相关节点**：添加应该保持在一起的节点时（服务+数据库、组件+标签）
2. **立即绑定**：创建相关节点后立即使用 `bind_nodes` 绑定它们
3. **检查绑定**：使用 `list_cells` 查看哪些节点已绑定（显示 `[BOUND to: ...]`）
4. **获取建议**：使用 `suggest_bindings` 发现现有节点中应该绑定的节点
5. **进行局部调整**：只在一个节点上使用 `move_shape` - 所有绑定的节点自动移动！

**基本工作流程：**
1. 使用 `bind_nodes` 将多个节点绑定在一起
2. 使用 `move_shape` 移动一个节点 - 所有绑定的节点一起移动
3. 使用 `get_bound_nodes` 检查哪些节点绑定在一起
4. 使用 `suggest_bindings` 获取智能绑定推荐
5. 如需要，使用 `unbind_nodes` 打破绑定关系

**示例：**
```python
# 高效工作流程：创建并绑定相关节点
auth_service = add_shape("认证服务", x=100, y=100)
auth_db = add_shape("认证数据库", x=100, y=200)
bind_nodes(node_ids=[auth_service, auth_db])  # 立即绑定！

# 现在当需要调整位置时 - 只移动一个节点：
move_shape(shape_id=auth_service, new_x=300, new_y=100)
# ✓ 认证服务和认证数据库都会自动一起移动！

# 为现有图表获取智能绑定建议
suggest_bindings()
# 输出：
# 💡 建议 3 个新绑定：
# 1. 绑定 '用户服务' (shape_3) 和 '用户数据库' (shape_4)
#    评分：130/100
#    原因：接近度：50%，垂直对齐，命名模式：相同前缀 'User'
#    → 绑定方法：bind_nodes(node_ids=['shape_3', 'shape_4'])

# 检查图表中的当前绑定
list_cells()
# 显示：对于绑定的节点显示 [BOUND to: shape_2]

# 将三个节点绑定在一起形成一组
bind_nodes(node_ids=["shape_1", "shape_2", "shape_3"])

# 移动 shape_1 - 三个节点将一起移动
move_shape(shape_id="shape_1", new_x=200, new_y=100)

# 检查什么与 shape_1 绑定
get_bound_nodes(node_id="shape_1")
# 返回："节点 'shape_1' 绑定到 2 个节点：shape_2, shape_3"

# 解除绑定特定节点
unbind_nodes(node_ids=["shape_2"])
# 现在 shape_1 和 shape_3 仍然绑定，但 shape_2 是独立的
```

**使用场景：**
- ✅ **局部调整**：高效移动相关节点组
- ✅ **微服务架构**：绑定服务+数据库对
- ✅ **组件图**：将组件与其标签/描述绑定
- ✅ **维护布局**：重新组织时保持相关元素在一起
- ✅ **减少编辑**：编辑 1 个节点而不是 5+ 个单独的节点

**优势：**
- 🎯 **效率**：用最少的编辑进行局部调整
- 🔧 **精确**：只改变需要改变的内容
- 📊 **组织**：自动保持相关节点在一起
- ⚡ **速度**：一个移动命令代替多个单独更新

**注意：** 绑定关系使用自定义属性保存在 .drawio XML 格式中。

### 连线交叉检测

`detect_line_crossings` 工具可以自动检测图表中连线（线条/边）何时相互交叉，并提供位置提示以帮助改进布局。

**工作原理：**
1. 分析图表中的所有连接
2. 检测连线之间的交叉点
3. 为每个交叉提供具体的修复建议

**输出包括：**
- 交叉连线的 ID 和标签
- 精确的交叉点坐标 (x, y)
- 修复每个交叉的多个建议：
  - 添加路径点以绕过彼此的连线
  - 重新定位形状以避免交叉
  - 调整入口/出口点以改变连接角度

**使用示例：**
```python
# 创建带有连接的图表后
detect_line_crossings()

# 示例输出：
# 检测到 2 个连线交叉：
#
# 1. 交叉于：
#    - 连接 '读取缓存' (ID: conn_5)
#    - 连接 '查询数据库' (ID: conn_6)
#    连线在 (260.0, 180.0) 处交叉。考虑以下调整：
#      1. 向 '读取缓存' 添加路径点以绕过交叉
#      2. 向 '查询数据库' 添加路径点以绕过交叉
#      3. 重新定位 '读取缓存' 连接的形状以避免交叉
#      4. 重新定位 '查询数据库' 连接的形状以避免交叉
#      5. 调整入口/出口点以改变连接角度
```

**使用场景：**
- 在最终确定之前自动验证图表布局
- 获取改进图表清晰度的建议
- 帮助 AI 模型做出更好的布局决策
- 识别复杂图表中的问题区域

**优点：**
- 通过突出显示交叉线条来提高图表可读性
- 为 AI 模型提供可操作的建议以自动修复布局
- 适用于简单的直接连接和复杂的路由连接

### 创建工具

| 工具 | 描述 | 关键参数 |
|------|------|----------|
| `create_diagram` | 创建新图表 | `name`（可选）|

## 支持的形状类型

### 基础形状

- `rectangle` - 标准矩形框
- `ellipse` - 圆形/椭圆形
- `diamond` - 菱形（用于决策）
- `parallelogram` - 平行四边形（用于输入/输出）
- `hexagon` - 六边形（用于准备）
- `cylinder` - 圆柱形（用于数据库）
- `cloud` - 云形（用于云服务）

### 活动图形状

- `activity_start` - 开始节点（实心圆）
- `activity_end` - 结束节点（带边框的实心圆）
- `activity_action` - 活动/动作框（圆角矩形）
- `activity_decision` - 决策节点（菱形）
- `activity_fork` - 分支节点（用于并行流的水平/垂直条）
- `activity_join` - 合并节点（用于合并流的水平/垂直条）
- `activity_send_signal` - 发送信号形状
- `activity_receive_signal` - 接收信号形状
- `activity_note` - 注释/备注形状

### 泳道图形状

- `swimlane_pool` - 泳道池/容器
- `swimlane_h` - 水平泳道
- `swimlane_v` - 垂直泳道
- `container` - 通用容器，用于分组元素

### UML类图形状

- `uml_class` - UML 类，包含属性和方法的分隔区
- `uml_interface` - 接口形状（斜体样式）
- `uml_abstract_class` - 抽象类形状（斜体样式）
- `uml_enum` - 枚举形状
- `uml_package` - 包/命名空间形状
- `uml_note` - UML 注释/备注形状

可以通过 `style` 参数使用 Draw.io 样式字符串来使用自定义形状.

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
