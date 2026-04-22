---
name: drawio-diagramming
description: "mcp-next-ai-draw-io 仓库里的 .drawio 画图工作流与仓库规范。Use when: 画架构图 / 时序图 / 领域调用关系图 / 组件通信图 / 活动图 / 流程图 / 类图等；新增或修改节点与连线；需要批量加节点/连线、自动布局、避免连线穿过节点、避免连线 label 遮挡节点、统一命名与分层；并输出可验收的变更摘要。"
argument-hint: "给我：目标 .drawio 路径（或新建目录）+ 图类型（arch/sequence/comm/domain/activity/flow/class）+ 节点清单 + 关系清单（表格/JSON 都可）+ 主题范围（这张图回答什么问题）"
user-invocable: true
---

# Draw.io 画图（mcp-next-ai-draw-io 仓库规范版）

目标：把架构 / 时序 / 领域调用 / 组件通信 / 活动 / 流程 / 类图等**稳定**落到仓库的 `.drawio` 文件中，并确保：
- 图可读、可维护、可检索
- 修改可追踪、可验收、尽量避免冲突/覆盖
- 连线避开节点，不允许穿过无关节点
- **连线 label 不得遮挡节点**
- **文本标签始终使用 HTML 风格**（换行用 `<br>`）
- 优先复用本项目已有的 MCP 工具能力，而不是手工改 XML

---

## 1. 仓库路径与命名规范

- 遵循用户给出的目标路径；skill 不写死默认目录
- 只描述“要新建一张图”但没给路径时，先确认保存目录再开始
- 建议文件名：`<根目录>/<域>/<主题>-<图类型>.drawio` 或 `<根目录>/<域>/<序号>-<主题>-<图类型>.drawio`
- `<图类型>`：`arch` / `sequence` / `comm` / `domain` / `activity` / `flow` / `class`
- 避免 `Untitled`；文件名短、稳定、可检索；图内可中文，文件名避免纯中文长串

---

## 2. 最低输入契约（缺一项就追问）

必填：
1. **目标文件**：已有文件路径，或新建所需的目录 + 文件名建议
2. **图类型**：架构（arch）/ 时序（sequence）/ 组件通信（comm）/ 领域调用（domain）/ 活动（activity）/ 业务流程（flow）/ 类图（class）
3. **主题范围一句话**：例如“广告投放链路中投放服务与计费服务之间的调用/事件关系”
4. **节点清单**
5. **关系清单**（至少 1 条）

推荐（缺失可用默认值）：
- 方向：`LR`（默认）或 `TB`
- 同步标记：调用 = 同步实线；事件 = 异步虚线
- 外部系统分组：默认需要

推荐关系表格式：

| from | to | 动作(动词) | 载体/协议 | 同步? | 备注 |
|---|---|---|---|---|---|
| A | B | 调用 | HTTP | 是 | /api/xxx |
| B | MQ | 发布 | Kafka | 否 | topic=xxx |

---

## 3. 标签与文本规范（强约束）

### 3.1 HTML 风格标签（必须）
所有 `label`、`value` 都按 HTML 渲染（`html=1`）：

- 换行统一使用 `<br>`
- 多行 UML：`ClassName<br>───────<br>- attr: type<br>───────<br>+ method()`
- 纯文本 `\n` 与 GraphViz 的 `\l`、`\n` 会被自动转成 `<br>`，但**应当直接输入 HTML 格式**，避免依赖自动转换

### 3.2 命名一致性
- 同一概念在一张图中只能有一个稳定叫法
- 节点名优先使用稳定的业务名词
- 连线 label 必须是“动词/动作短语”（例如：`调用下单`、`发布订单已支付`、`读取用户画像`）
- 同一节点既有中文名又有英文系统名：写成 `投放服务 AdService`

---

## 4. 形状与线条语义

形状（按图类型分组）：
- 通用：`container` 域/子系统边界；`rectangle` 服务/组件；`cylinder` 存储；`cloud` 外部系统
- 流程图：`activity_start` / `activity_action` / `activity_decision` / `activity_end` / `activity_fork` / `activity_join`
- 领域模型 / 类图：`uml_class` / `uml_enum` / `uml_interface` / `uml_abstract_class` / `uml_package` / `uml_note`
- 时序图：`actor`（外部角色，简笔人）/ `lifeline`（生命线，带头部标签，纵向 400+）/ `uml_frame`（alt / loop / opt 块）
- 组件图：`component`（带端口凹口的 UML 组件）
- 泳道：`swimlane_pool` / `swimlane_h` / `swimlane_v`

线条：
- 调用（HTTP/gRPC）= 实线 + classic 箭头
- 发布/订阅（Kafka/RabbitMQ）= 虚线 + classic 箭头
- 读写存储 = 实线
- 时序图返回消息 = 虚线
- **所有连线都必须有 label**（动词/动作短语），除非需求显式声明例外
- **连线 label 不得遮挡任何节点**；`add_connection(auto_avoid_label_overlap=true)` 会自动把 label 偏移到空白区域

布局优先级（从高到低）：
1. 连线不穿过无关节点（`auto_route=true`）
2. 连线 label 不遮挡任何节点（`auto_avoid_label_overlap=true`）
3. 连线交叉数最少
4. 同类节点对齐、留白一致
5. 方向一致（LR 或 TB 不混用）
6. 外部系统与内部系统视觉区隔

---

## 5. 本项目工具映射（必须优先使用）

> **写操作一律走 `batch_operations`**：多个节点 / 连线 / 绑定 / 更新 / 删除等写类操作应当**打包进一次 `batch_operations` 调用**，以节省往返与 token。`add_shape` / `add_connection` / `update_cell` / `delete_cell` / `move_shape` 仅用于真正的单步操作。

文件与会话：
- `load_diagram(path=...)` / `create_diagram(name=...)` / `save_diagram(path=...)`
- 建议 `create_diagram(autosave_path=...)` 或 `load_diagram(autosave=true)` 开启自动保存，省掉显式 `save_diagram`

查询（只读）：
- `list_cells()` 查看全部元素与绑定关系
- `get_cell(cell_id=...)` 查看单个元素细节，**返回值自带 `bound_nodes` 字段**（因此无独立的 `get_bound_nodes` 工具）

批量写入（首选）：
- `batch_operations(operations=[...])` — 支持的 `op`：
  - `add_shape` / `add_connection` — 新增
  - `update_cell` — 更新 label / 位置 / 尺寸 / 样式，**还支持 `waypoints` / `entry_x/y` / `exit_x/y` / `label_offset_x/y`**
  - `delete_cell` — 删除
  - `move_shape` — 移动（绑定节点自动跟随）
  - `bind_nodes` / `unbind_nodes` — 绑定 / 解绑（**仅在 batch 内可用**）
  - `auto_layout_adjust` — 触发自动布局调整

单步便捷工具（只有一个写操作时用）：
- `add_shape(...)` / `add_connection(...)` —— **必须填写 HTML 风格的 `label`**；默认 `auto_route=true`
- `update_cell(...)` / `delete_cell(...)` / `move_shape(...)`

布局与局部调整：
- `auto_layout_adjust(padding=10, max_iterations=20, only_ids=None, dry_run=false)` — **服务端迭代推开**所有重叠，绑定组整体移动、不越出容器、自动路由边自动重算。推荐作为收尾一步
- `suggest_bindings()` — 返回结构化绑定建议

验收检查（只读）：
- `detect_line_crossings()` — 检测连线交叉 + 连线穿过节点（`issue_type=node_crossing`）
- `detect_overlaps()` — 检测节点重叠、label 溢出、容器越界
- 以上三个检查工具（含 `suggest_bindings`）返回的**每一条 issue 都附带 `fix` 字段**，形如：
  ```json
  { "op": "move_shape", "args": {"shape_id": "s2", "new_x": 240, "new_y": 160},
    "rationale": "向右移动以消除与 s1 的重叠" }
  ```
  直接把多个 `fix` 喂进 `batch_operations` 即可落地。

工具使用原则：
1. **先读后改**：`load_diagram` → `list_cells` / `get_cell` → 再改
2. **批量优先**：写操作一律组装进 `batch_operations`；真正只改一处才用单步工具
3. **成组即绑定**：新增一组相关节点后立即在同一个 batch 里加 `{"op": "bind_nodes", "node_ids": [...]}`
4. **收尾跑自动布局**：批量新增 / 迁移后用 `auto_layout_adjust` 一次性推开重叠
5. **验收闭环**：`detect_line_crossings` + `detect_overlaps` → 把返回的 `fix` 直接塞进下一次 `batch_operations`

---

## 6. 标准改图流程

改前安全策略：
- 已有图：先 `load_diagram`，按 label 定位目标区域
- 保守修改：另存备份文件（例如 `xxx_20260314.drawio`）
- 新图：先确认目录和文件名，再 `create_diagram`

步骤：
1. **加载或创建**：`load_diagram` / `create_diagram`（建议开 `autosave`）
2. **扫描现状**：`list_cells`，关键节点 / 连线用 `get_cell`（包含 `bound_nodes` 字段）
3. **批量新增 / 调整**：把所有 `add_shape` / `add_connection` / `update_cell` / `bind_nodes` 打包进**一次** `batch_operations`
   - 按语义选形状，同类节点尺寸统一
   - 连线必带 HTML label；协议、事件名、topic、接口路径写进 label
   - 默认 `auto_route=true`；必要时在同一 batch 里 `update_cell(..., waypoints=[...], entry_x=..., exit_x=...)` 精调
   - 相关节点同步用 `{"op": "bind_nodes", "node_ids": [...]}` 绑定
4. **自动布局收尾**：`auto_layout_adjust()` 一次性推开所有重叠（绑定组整体移动、容器子节点不越界、自动路由边自动重算）
5. **验收 & 循环修复**：
   - `detect_line_crossings()` + `detect_overlaps()` + `suggest_bindings()`
   - 把返回的每条 `fix` 直接收集成 `operations` 列表丢进下一次 `batch_operations`
   - 再跑一次检查直到全部达标
6. **保存**：若未开 autosave，调用 `save_diagram(path=...)`

---

## 7. 分图类型专用规则

- **架构图（arch）**：先画系统边界（`container`），再放服务（`rectangle` / `component`）/ 存储（`cylinder`）/ 外部依赖（`cloud`）；推荐分层（入口 → 应用 → 数据 → 外部）；同层组件对齐
- **组件通信图（comm）**：重点表达“谁调谁 / 谁发给谁 / 经过什么协议”；同步（实线）vs 异步（虚线）视觉区分；一条边只表达一个主要动作；推荐使用 `component` 画组件
- **时序图（sequence）**：参与者放在同一 y 坐标、从左到右；外部角色用 `actor`，系统参与者用 `lifeline`（`height` ≥ 400 以伸展出虚线生命线）；消息连线使用 `edge_style=straight`；返回消息用 `dashed=true`；对 `alt` / `loop` / `opt` 段使用 `uml_frame` 包裹
- **领域调用关系图（domain）**：每个限界上下文一个 `container`，其内部实体/服务通过 `parent_id` 放入；调用（同步）用实线，事件（异步）用虚线；label 用具体动作动词（"调用下单"、"发布订单已支付"）
- **领域模型图（class）**：优先 `uml_class` / `uml_enum` / `uml_interface`；类名、属性、方法统一命名；多行文本必须用 `<br>`
- **业务流程图（flow）**：起止节点清晰；决策节点必须有分支条件；主路径单方向阅读
- **活动图（activity）**：`activity_start` → `activity_action` / `activity_decision` / `activity_fork` / `activity_join` → `activity_end`；保持单一主方向

---

## 8. 质量门禁（保存前必查）

1. **连线穿过节点**：`detect_line_crossings()` 中 `issue_type=node_crossing` 必须为 0；如仍有，把返回的 `fix`（包含 `waypoints`）塞进 `batch_operations` 里的 `update_cell`
2. **连线 label 遮挡节点 / 其他连线**：`detect_overlaps()` 返回的 label-overlap 条目附带 `fix`（`update_cell` + `label_offset_x/y`，已是**绝对偏移值**，直接用）
3. **连线交叉数**：`detect_line_crossings()` 中 `issue_type=line_crossing` 尽量为 0
4. **节点重叠 / label 溢出 / 容器越界**：`detect_overlaps()` 必须为 0；
   - **首选方案**：直接调 `auto_layout_adjust()` 让服务端推开
   - **精细调整**：逐条应用 issue 的 `fix`（含 `cause` 字段区分 `body` vs `label_overflow`）
5. **无 label 的连线数量**：0（除非显式豁免）
6. **外部系统分组**：已通过容器 / 虚线边框 / `cloud` 视觉区隔
7. **命名一致性**：同一概念无多种叫法
8. **局部可维护性**：应一起移动的节点已通过 `batch_operations` 里的 `bind_nodes` 绑定

---

## 9. 每次交付的固定输出

1. **保存路径**：`.drawio` 文件的绝对/相对路径
2. **变更摘要**：新增节点、新增连线、删除/替换节点、调整布局
3. **质量检查结果**：
   - 连线穿过节点：`0`
   - 连线交叉：`X`
   - 节点重叠 / 越界：`0`
   - 无 label 的连线：`0`
   - 未分组的外部系统：`是 / 否`

---

## 10. 启动对话的最省时间输入模板

```yaml
target: <根目录>/广告/ad-delivery-comm.drawio
diagram_type: comm
scope: 广告投放链路中投放服务与计费服务之间的调用和事件关系
direction: LR
nodes:
  - { name: 投放服务,     external: false }
  - { name: 计费服务,     external: false }
  - { name: Kafka,       external: false }
  - { name: 广告主后台,   external: true  }
relations:
  - { from: 广告主后台, to: 投放服务, action: 调用创建投放,   protocol: HTTP,  sync: true  }
  - { from: 投放服务,   to: Kafka,   action: 发布投放已创建, protocol: Kafka, sync: false }
  - { from: 计费服务,   to: 投放服务, action: 调用查询投放,   protocol: gRPC,  sync: true  }
```

拿到这些信息后，按本技能文档直接执行改图、保存并给出验收摘要。
