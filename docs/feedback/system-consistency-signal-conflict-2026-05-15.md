# 补充反馈：三次信号冲突发现与生态扩展案例

> 日期: 2026-05-15
> 关联: openclaw-field-report-2026-05-15.md, memory-md-as-state-vector-2026-05-15.md
> 触发: 工程控制论全景诊断（全系统文档角色映射 + 交叉一致性扫描）

## 背景

在 v0.3.0 发布后，对 OpenClaw 部署做了第二轮控制论审计——不是检查知识库，而是检查**系统本身**是否自洽。发现了三个前次反馈未覆盖的模式。

---

## 反馈 #1: "协议分叉"指引 — 内联改编是合法部署模式

### 发现问题

我们的 OpenClaw 部署没有直接引用 `~/Documents/GitHub/Marginalia/schema/rules.md`。因为 Agent 的工作区是 `~/.qclaw/workspace/`，无法读取工作区外的文件。

**解决方案**：将 rules.md 改编为 AGENTS.md 的"内联段"——带路径适配（`wiki/` → `Knowledge/wiki/`）和少量润色。

```markdown
# AGENTS.md 中的内联段
## Marginalia 知识库（v0.3.0 协议）
### 读取规则
1. 每次对话开始，先读 Knowledge/wiki/index.md
...
```

**效果**：内联段与 Marginalia v0.3.0 的 rules.md 功能等价，且版本标签 `v0.3.0` 允许对照升级。

### 为什么需要反馈

当前 README.md 的"平台集成"章节没有提到"内联改编"这种部署模式。用户可能误以为"引用外部文件才是正确集成"——这在跨工作区场景中不可行。

### 建议

在 README.md 的平台集成章节增加一句：

> **跨工作区部署**：当 Agent 无法引用 Marginalia 仓库中的 schema 文件时（如 OpenClaw 的 Agent 工作区与 Marginalia 仓库不在同一路径），将 `rules.md` 改编为 Agent 配置文件的"内联段"是推荐做法。内联段应标注 `协议版本：Marginalia vX.Y.Z`，方便后续对照升级。

改动量：~3 行。

---

## 反馈 #2: "影子指令"警示 — 平台模板与 Marginalia 的信号冲突

### 发现问题

OpenClaw 的默认 AGENTS.md 模板包含一个 80+ 行的 `## 💓 Heartbeats` 段，描述了：

- 邮件检查、日历检查、天气检查、社交通知检查
- `heartbeat-state.json` 追踪
- "主动 reach out"行为规则
- 心跳期间的 Memory Maintenance

但当 Marginalia 被部署后，`HEARTBEAT.md` 被重写为 8 行——仅检查 `MEMORY.md > 200 行`。AGENTS.md 的 80 行 Heartbeats 段**从未被清理**。后果：

```
AGENTS.md §Heartbeats（80 行）──→ 描述不存在的社交心跳
HEARTBEAT.md（8 行）          ──→ 实际行为
```

**双重信号持续了 15 天**，直到第二轮控制论审计才发现。

### 这是 Marginalia 特有的问题吗？

不完全是——但 Marginalia 的部署流程会产生这个问题。因为：

1. Marginalia 的 `init.py` 在 Agent 配置文件中**追加**知识库引用段
2. 但它不检查 Agent 配置文件中是否有**来自原始平台模板的、与 Marginalia 维护架构冲突的旧段**
3. 跨平台部署时（OpenClaw、Claude Code、Cursor），每个平台都有各自的默认模板，都可能发生这种冲突

**冲突根因**：追加新段落 ≠ 删除旧段落。旧模板的 Heartbeat/自动化规则段成为"影子指令"——存在但不应该被执行。

### 建议

在 README.md 的平台集成章节或 CLAUDE.md 中增加一个警示框：

> ⚠️ **部署后检查**：Marginalia 部署完毕后，扫描 Agent 配置文件中是否有来自原始平台模板的"影子指令"段。典型冲突：
> - Heartbeat/心跳段的自动化规则可能与 Marginalia 的维护架构重叠或矛盾
> - 旧的社会检查指令（邮件/日历）在 Marginalia 维护模型下是噪声
> - 解决方案：删除影子指令段，或将其缩减为指向 `HEARTBEAT.md` 的几行引用

改动量：~5 行警示 + 一个具体示例。

### 通用性证据

这个问题不是 OpenClaw 独有的。任何部署 Marginalia 的平台，如果其 Agent 配置文件有"自动化维护"或"定期检查"的模板段，都会面临同样的冲突。关键是：**Marginalia 自己的维护架构（cron + audit + heartbeat）与平台原始模板的维护假设通常不一致。**

---

## 反馈 #3: SKILL.md — 从 4 类型到 8 类型的生态扩展

### 发现

OpenClaw 部署中，`Knowledge/schema/` 目录下同时存在：

| 文件 | 角色 | 覆盖 |
|------|------|------|
| `node-types.md` | Marginalia 原生分类快查 | 4 类型 (concept/decision/annotation/comparison) |
| `SKILL.md` | LLM Wiki 维护手册 | 6+ 类型 (sources/entities/concepts/syntheses/comparisons/queries) |

两者不冲突——`node-types.md` 是快查表，`SKILL.md` 是完整手册。但 SKILL.md 覆盖了 Marginalia 核心不覆盖的 page types（source、entity、synthesis、query），并引入了 Marginalia 未定义的质量标准（thin page detection、template remnant check、topic batch import）。

在实践中，153 页的生产 wiki 自然地长出了这些扩展类型：

```
sources/ — 92 页 (60%)  ← 最大单一类型，Marginalia 无原生支持
entities/ — 16 页 (10%)  ← Marginalia 标记为"可选"
concepts/ — 36 页 (23%) ← Marginalia 原生支持
其他     — 10 页 (7%)
```

**92 页 source 类型的存在**说明对于导入密集型 wiki，source page 是必要而非可选的。

### 建议

在 `docs/` 或 `archive/` 中创建一个扩展案例文件：

> `docs/ecosystem/extended-node-types-openclaw.md`

内容：
1. 说明如何在 node-types.md 的基础上扩展新类型
2. 以 OpenClaw 部署为例，展示 source/entity/synthesis/query/report 的定义
3. 标注 "这是生态扩展，非核心规范"
4. 链接回 Marginalia 核心的 4 类型

**不合并进核心 schema**（和 v0.3.0 的"不新增节点类型"决策一致），但作为生态存在——让其他用户知道"这是可能的，这是怎么做"。

改动量：一个 `docs/ecosystem/` 目录 + 一个案例文件。核心代码零改动。

### 补充数据点

node-types.md 的 v0.3.0 设计决定是"不新增节点类型"。这个决定是正确的——保持核心简单。但 15 天生产数据表明用户**会**长出自己的扩展。SKILL.md 是这种扩展的一个工作案例。收录它作为生态文档不违反"不新增核心类型"的原则，但为有同样需求的用户提供了路径。

---

## 优先级

| # | 类型 | 优先级 | 改动量 |
|---|------|--------|--------|
| 反馈 #1 | 文档 | 🟡 中 | README.md +3 行 |
| 反馈 #2 | 警示 | 🔴 高 | README.md +5 行警示 |
| 反馈 #3 | 生态案例 | 🟢 低 | 新建 docs/ecosystem/ 目录 |

**反馈 #2 优先级最高**——"影子指令"问题是部署时的普遍风险，且当前 Marginalia 文档对此完全没有警告。

---

## 与前次反馈的关系

| 前次反馈 | v0.3.0 采纳 | 本次补充 |
|---------|-----------|---------|
| 建议 #1 (三回路拆分) | ✅ 采纳 (event-driven audit) | — |
| 建议 #2 (audit.py CI 模式) | ✅ 采纳 (--brief/--exit-code-only) | — |
| 建议 #3 (init.py 平台感知) | ❌ 不采纳 (不分叉) | 反馈 #1 提供了替代方案 ("内联改编"指引) |
| 建议 #4 (平台模板) | ❌ 不采纳 | 反馈 #2 揭示缺失这些模板的后果 |
| 建议 #5 (节点类型扩展) | ❌ 不采纳 | 反馈 #3 提供生态路线 (不合并进核心) |
| MEMORY.md 状态向量 | 未纳入 v0.3.0 | — |

---

*本报告基于第二次全系统控制论审计（AGENTS.md 211 行、HEARTBEAT.md 11 行、Knowledge/schema/ 7 项、Knowledge/wiki/ 155 页），聚焦 Marginalia 部署后的系统自洽性而非知识库内容质量。*