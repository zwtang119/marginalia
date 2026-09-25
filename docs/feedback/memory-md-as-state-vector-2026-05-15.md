> [!NOTE]
> 本文件中的 CDS/Stock-Claw/OpenClaw 项目专属内容已同步迁移到 CDS-teamWiki。
> 活跃副本位置：`CDS-teamWiki/investigations/marginalia-feedback-memory-md-as-state-vector-2026-05-15.md`
>
> 本文件保留在 Marginalia 开源仓库中作为原始记录，未做删除。

# 补充反馈：MEMORY.md — 个人状态向量层的涌现

> 日期: 2026-05-15
> 关联: openclaw-field-report-2026-05-15.md

## 发现

在 15 天 OpenClaw 部署中，系统自然演化出一个 Marginalia 当前架构未覆盖的组件：**MEMORY.md**（"冷启动状态向量"）。

它的内容不是 Marginalia 定义的概念/决策/批注/对比中的任何一类。它是：
- 身份坐标（谁、什么角色）
- 当前项目仪表板（核心项目、状态、角色）
- 技术主干定义（CDS、MADG、Role DNA）
- 近期关键决策（带时间戳）
- 个人偏好与盲点
- 术语纠错表（MAMR→MADG 等）

## 为什么 Marginalia 应该关注

MEMORY.md 不是 OpenClaw 特有的产物。任何多会话 AI 助手系统都需要一个"冷启动状态向量"——它是连接**平台会话模型**和**知识库系统**的桥梁。在 Marginalia 的架构图中：

```
当前 Marginalia 模型:
    claude.md → Knowledge/wiki/ → concepts/decisions/comparisons/

实际部署中的模型:
    AGENTS.md（嵌入 Marginalia 协议）
        ↓
    MEMORY.md（个人状态向量）  ← Marginalia 架构中缺失的这一层
        ├→ "知识库 → Knowledge/wiki/（Marginalia v0.3.0 边注系统）"
        └→ "执行偏好 → ~/self-improving/memory.md"
            ↓
    Knowledge/wiki/（Marginalia 知识库）
```

MEMORY.md 的头部行扮演了**路由注释**角色：

```markdown
> 知识库 → `Knowledge/wiki/`（Marginalia v0.3.0 边注系统） | 执行偏好 → `~/self-improving/memory.md` | 此文件 = 冷启动状态向量
```

这个模式具有通用性：它告诉 AI "我有两层外部信息——知识库和偏好——分别去这里找"。这是 claude.md 的"快速进入"指引在个人层面上的等价物。

## 对 Marginalia 的建议

### 1. node-types.md 增加 `profile` 类型（可选/实验性）

当前 node-types.md 的"写回位置"表覆盖了概念、决策、批注、对比，但没有覆盖"个人状态/偏好"这一信息类型。建议增加：

| 信息类型 | 写回位置 |
|----------|----------|
| 个人身份、项目状态、偏好、盲点 | `profile/` 或 `MEMORY.md`（可选/实验性） |

这不是强行把 MEMORY.md 纳入 Marginalia 的管理范围——MEMORY.md 的更新频率和特性与 wiki/ 知识库不同。但 Marginalia 可以**识别**这个层的存在，并在 node-types.md 的信息分类决策树中给出指引：

```
新信息到来
    │
    ▼
是个人状态/偏好变化？ ──YES──> 更新 MEMORY.md（非 wiki/）
    │
    NO
    ▼
（继续现有决策树...）
```

### 2. 推荐"版本标签"模式

MEMORY.md 头部对 Marginalia 的引用是一个有价值的模式：

```markdown
> 知识库 → `Knowledge/wiki/`（Marginalia v0.3.0 边注系统）
```

这告诉 AI：① 知识库在哪里 ② 用的是什么系统 ③ 版本号是什么。如果 Audit.py 或 rules.md 版本升级，AI 可以通过版本标签判断知识库是否需要迁移。

建议 Marginalia 的 README.md 或 init.py 中推荐这种版本标签写法：
```markdown
> 知识库 → `wiki/`（Marginalia v0.3.0）
```

### 3. 更新 CLAUDE.md 的"快速进入"部分

当前 claude.md 的"快速进入"只指向 Marginalia 自身：
```
1. 读 schema/rules.md
2. 读 schema/node-types.md
3. 读 schema/first-ingest.md
```

如果 Marginalia 被部署到包含 MEMORY.md 的项目中，CLAUDE.md 可以建议增加一条：
```
在包含个人状态向量的项目中，AI 应优先读取 MEMORY.md 以恢复状态，再进入知识库
```

## 与 v0.3.0 设计的兼容性

这个建议与现有的 v0.3.0 平台兼容性设计完全兼容：
- ✅ 不分叉（只是文档层面的建议）
- ✅ 不新增依赖
- ✅ 不写平台特定代码
- ✅ 不违反三原则

唯一的改动是 node-types.md 增加一个可选类型说明，和 claude.md/README.md 增加一个推荐模式的示例。

## 优先级

🟢 **低优先级** — 这不阻塞 v0.3.0 的核心改动（三回路拆分 + audit.py CI 模式），但作为一个经过 15 天生产部署验证的、自然涌现的架构模式，值得被 Marginalia 的文档体系记录下来。其他用户在部署 Marginalia 时可能会遇到同样的需求。