> [!NOTE]
> 本文件中的 CDS/Stock-Claw/OpenClaw 项目专属内容已同步迁移到 CDS-teamWiki。
> 活跃副本位置：`CDS-teamWiki/investigations/marginalia-feedback-openclaw-field-report-2026-05-15.md`
>
> 本文件保留在 Marginalia 开源仓库中作为原始记录，未做删除。

# Marginalia on OpenClaw: 工程控制论视角的实地反馈报告

> **报告日期**: 2026-05-15
> **部署环境**: OpenClaw v0.x 网关 + Agent 运行时
> **部署时长**: ~2 周（2026-04-30 → 2026-05-15）
> **知识库规模**: 153 页（concepts × 24, entities × 16, decisions × 4, comparisons × 2, annotations × 3, reports × 4, sources × 87, projects × 3）
> **审计结果**: P0=0, P1=0, P2=5（设计内孤儿页）

---

## 0. 执行摘要

Marginalia 的**设计哲学**（同位/无损/解耦三原则）和**工具链**（init/audit/verify）在 OpenClaw 上得到了验证——它们是健壮的、可移植的。问题出在一个更深层的地方：

**Marginalia 假设了一个能自我监督的 AI 演员，但控制论告诉我们，演员不能同时是控制器。**

具体表现为：
- "收工规则"依赖 AI 主动记忆执​​行 → 从未可靠执行
- memo 批注覆盖率缺乏任何检查机制 → 完全空白
- audit 脚本设计为人工运行 → 自动化集成困难（无 --brief、无 exit-code-only、无告警阈值）
- init.py 生成的 CLAUDE.md 段落没有平台适配指引 → 直接照抄导致 OpenClaw cron 架构崩溃

**核心建议**：Marginalia v0.3 应从"协议规范"升级为"平台适配框架 + CI 风格的验证工具链 + 人机协作反馈回路"。分离三个控制问题——状态监控（可自动化）、流程执行（需人机协作）、语义质量（只可人工判断）——不再将它们混为一谈。

---

## 1. 设计评估：三原则验证 ✅

### 同位原则 — 验证通过

```markdown
Knowledge/wiki/concepts/cds.md
├─ 正文：CDS 四层架构定义
└─ 批注：2026-04-30 讨论记录
```

AI 会话沿 `index.md → [[concepts/cds]] → 批注` 的链路自然读取，无需额外检索步骤。在 17 天 18 个会话中，Step 7 的 index.md 先读机制始终正确触发，没有遗漏。

**结论**：同位原则在 OpenClaw Agent 上下文注入模型下工作完美。Agent 的 session startup 流程天然匹配 Marginalia 的"先读 index → 沿 wikilink 深读"模式。

### 无损原则 — 验证通过

因为 wiki/ 就是纯 Markdown 文件，嵌入在 OpenClaw workspace 中。Agent 读取时获得完整原文，不经过任何压缩。对比记忆系统的 embedding/RAG 方案，无损性是 Marginalia 最大的物理优势。

### 解耦原则 — 验证通过

迁移验证：从 `~/Documents/GitHub/Marginalia/example/` 复制脚本模板到 `~/qclaw/workspace/Knowledge/schema/scripts/`，只需修改 --root 参数和 wikilink 前缀适配即可工作。脚本零依赖 → 直接在 macOS/Darwin 的 Python3 上运行。解耦性完全验证。

**评分**: ⭐⭐⭐⭐⭐ (5/5) — 核心三原则在跨平台部署中完全成立。

---

## 2. 核心问题：控制论断层 🟥

### 2.1 演员-控制器混淆（Actor-as-Controller Fallacy）

这是整个系统最根本的设计缺陷。Marginalia 的 schema/rules.md 和 init.py 生成的 CLAUDE.md 段落要求：

```
### 完成实质工作后
- 更新 wiki/index.md（如有新页面）
- 在相关页面添加批注：> [!memo] YYYY-MM-DD 内容
- 运行 `python3 scripts/audit.py --root wiki/`，处理发现的问题
```

**控制论诊断**：

```
        ┌─────── Actor ───────┐
        │                      │
        │  "我现在应该写 memo 吗？"  │
        │  "我更新了 index 吗？"    │
        │                      │
        └──────────────────────┘
                 ↑
                 │
        这个系统没有外部控制器
```

同一个 Agent 既执行对话任务（Actor），又要求它记住并执行维护任务（Controller）。这是**二阶控制论中的观测者悖论**——当 Actor 在做实质工作时，它的注意力被任务消耗；当任务完成后要求它"切换到 Controller 模式"，没有外部触发信号来强制这个切换。

**OpenClaw 运行实证**：

- 18 个会话
- 0 次 memo 批注被主动添加
- 0 次 audit 在会话结束时被运行
- AI 在事后自省中承认："是否加 memo 完全取决于我记得与否，没有强制检查"

这不是 AI 能力问题——同一 Agent 在执行明确指令（如"运行 audit.py"）时完全胜任。问题是**没有外部信号触发 Controller 行为**。

### 2.2 平台集成断层

Marginalia 的 init.py 生成的 CLAUDE.md 段落是**平台无关**的——它假设所有 AI 助手平台都有相同的会话模型和自动化能力。但实际平台分化为：

| 平台 | 会话模型 | 自动化机制 | Marginalia 适配状态 |
|------|--------|-----------|-------------------|
| Claude Code | 终端 CLI 交互 | — | init.py 原生设计目标 |
| OpenClaw | Gateway + Agent + cron + heartbeat | 复杂 | 无适配指引 |
| Cursor/Cline | IDE 插件交互 | — | 不确定 |

我们试图在 OpenClaw 上运行 Marginalia 时，做了以下**错误的平台集成**：

```
❌ 创建 4 条 cron job 做维护
   ├─ 864a12f4: 30 分钟心跳 cron → 40M tokens/月，全部静默失败
   ├─ 7afe8d02: 每周 Marginalia 审计 → 与上面重叠
   ├─ 33fe0372: Wiki 周检 → 跑在错误 agent 上（死进程）
   └─ 548a7918: W5 体检 → 跑在错误 agent 上（死进程）

❌ HEARTBEAT.md 膨胀到 100+ 行（官方模板: "Keep this file empty"）

❌ Cron 的 delivery channel 全部未配置 → 605 条运行记录全部 delivered: false
```

**根因**：Marginalia 没有提供平台集成的设计指引。作为协议规范，它定义了"应该发生什么"但没有定义"在 OpenClaw 上应该如何发生"。用户被留在空白处自行设计平台集成——结果是 40M token 的失败实验。

### 2.3 审计工具链的 CI 适配缺失

audit.py 设计得很好——158 行零依赖 Python，wikilink 解析 + 断链检测 + 孤儿页检测。但它缺少自动化 CI 场景的关键功能：

```
缺少的功能：
├── --brief 模式（只输出 P0/P1 计数，适合 cron 告警）
├── --exit-code-only 模式（根据严重度返回非零退出码）
├── --max-p0 N 告警阈值（P0 > N 时才报告，否则静默）
├── --max-p1 N
├── --json 输出（现在有，但需更结构化的 severity_counts 字段）
├── 结构化输出支持（text/json/silent 三种 mode）
└── 随时间追踪趋势的能力（上次 audit 结果缓存对比）
```

这些不是功能膨胀——它们是平台自动化的**最小可行接口**。

---

## 3. 定量证据：605 条运行记录分析

截取 `864a12f4` cron 的 605 条运行记录（2026-04-30 ~ 2026-05-15, 30min 间隔）：

```
总运行次数:       605
成功次数:         603 (99.7%)
失败次数:           2 (Agent 无响应, heartbeat-state 编辑失败)
Delivery 成功:      0 (0%)
Delivery 失败:    605 (100%) — Channel required, not configured

Token 消耗:       ~40M+ 总计
平均/次:          ~25K tokens (含系统提示词注入)
有效信号:           1 条 (08:24 的 "Wiki 周检过期 14天 + MEMORY >100行")
有效信号率:        0.17%

振荡模式:         47 次连续返回 HEARTBEAT_OK 后，问题仍未解决
级联故障:          2/4 crons 跑在错误 agent 上
冗余:              3/4 crons 功能重叠
```

**控制论结论**：这是一个信噪比 0.17% 的控制系统。相当于每花 100 元，0.17 元产生有效信息，99.83 元烧在重复确认"无变化"上。没有控制工程师会容忍 >1% 的信噪比。

但有一个关键反例：**主动会话中的一次手动操作，将 audit 问题从 364 降至 10，再将 P0 从 5 降至 0**。这个闭环执行时间 < 1 小时。对比 cron 系统：605 次运行、2 周时间、0 个问题被解决。

**问：是传感器修好了 Wiki，还是人修好了 Wiki？** **答：人。传感器从未成功传递过一次信号。**

---

## 4. 改进建议

### 建议 #1: 将 rules.md 从"行为指令"升级为"控制架构"

**现状** (schema/rules.md):

```
## 收工规则
1. 更新 wiki/index.md（如有新页面）
2. 在相关页面添加批注：> [!memo] YYYY-MM-DD 内容
3. 运行 `python3 scripts/audit.py --root wiki/`，处理发现的问题
```

**建议**:

```markdown
## 维护架构

Marginalia 维护涉及三个独立控制回路，必须分开处理：

### 回路 A: 状态监控（全自动）
- 传感器: audit.py --brief + verify.py
- 频率: 每日一次（平台 cron）
- 告警条件: P0>0
- 人类动作: 收到告警后手动修复

### 回路 B: 流程执行（人机协作）
- 触发: 会话结束时 AI 提议（非自动执行）
- 内容: "本次是否产生新概念/决策/洞察？[1] 创建页面 [2] 添加 memo [3] 跳过"
- 人类确认后 AI 执行

### 回路 C: 语义质量（全人工）
- memo 覆盖率、概念完整性、分类准确性
- 只可人工判断，不可自动化
- 频率: 月度人工审计

### 平台适配
在不同 AI 平台上部署时，回路 A 的实现不同：
- OpenClaw: 使用 cron + sessionTarget:isolated
- Claude Code: 用户手动运行 audit.py
- 其他平台: 参照以上模式
```

**理由**: 分离三个控制问题 → 消除演员-控制器混淆 → 每个回路有明确的所有者和触发机制。

### 建议 #2: audit.py 增加 CI 模式

```diff
+ --mode {full,brief,silent}  # 输出模式
+ --max-p0 N                  # P0 告警阈值
+ --max-p1 N                  # P1 告警阈值
+ --exit-code-only            # 无输出，仅返回退出码
+ --cache FILE                # 上次审计结果缓存（用于趋势对比）
```

这些不是可选功能——它们是 Marginalia 进入平台自动化生态的**门票**。没有 --brief 模式，每条 cron 报告都是完整的 JSON dump，不适合人类快速阅读。没有 --silent + exit-code-only 模式，cron 无法实现"无告警则静默"。

### 建议 #3: init.py 增加平台感知

```diff
+ --platform {openclaw,claude-code,cursor,generic}
```

当 `--platform openclaw` 时，init.py 应：
1. 生成 OpenClaw 风格的 cron 配置模板（而非通用 CLAUDE.md 段落）
2. 给出 HEARTBEAT.md 的最小配置示例
3. 警告：不要为 wiki 维护创建心跳 cron
4. 建议 delivery channel 配置

**反模式警告**：当前 init.py 生成的 CLAUDE.md 段落在 OpenClaw 上被直接映射为 30 分钟心跳 cron → 40M token 灾难。平台感知初始化是防止用户犯错的唯一方法。

### 建议 #4: 增加"维护模式"模板

在 `templates/` 目录下新增：

```
templates/openclaw/
├── cron-wiki-audit.json     # OpenClaw wiki 审计 cron 配置示例
├── HEARTBEAT.minimal.md     # 最小心跳配置
└── AGENTS.marginalia.md     # Agent 指令段落（替代 init.py 中的通用段落）
```

这不仅适用于 OpenClaw——每种部署平台都应该有对应的适配模板。

### 建议 #5: node-type 系统升级

当前 4 节点类型（concept/decision/annotation/comparison）在实际使用中太少了。我们的 wiki/ 自然演化出：

| 节点类型 | Marginalia 定义 | 实际使用 | 建议 |
|---------|---------------|---------|------|
| concept | ✅ | ✅ 24 页 | 保持 |
| decision | ✅ | ⚠️ 4 页 | 保持（低频但重要） |
| annotation | ✅ | ⚠️ 3 页 | 保持 |
| comparison | ✅ | ⚠️ 2 页 | 保持 |
| **report** | ❌ | ⚠️ 4 页 | **建议增加** |
| **project** | ❌ | ⚠️ 3 页 | **建议增加** |
| **source** | ❌ | ⚠️ 87 页 | 建议讨论（可选） |
| **entities** | 标记为"可选" | ⚠️ 16 页 | 提升为正式类型 |

**`report`（报告）**: 周期性或一次性分析报告，非决策、非概念、非批注。比 annotation 更长，比 concept 更具体。node-types.md 中没有位置。

**`project`（项目）**: 项目仪表板页（目标/状态/进度/开放问题）。当前 node-types.md 的分类决策树无法归类此类内容。

**建议**：在 node-types.md 中增加 report 为第五种正式类型，project 为第六种。source 和 entities 保持为"可选"但提供模板和索引位置。

### 建议 #6: 从"零依赖脚本"升级为"零依赖 + 标准接口"

保持零依赖核心原则（✅ 已验证重要），但增加：
- `audit.py --format json` 的 schema 文档（当前 JSON 输出无 schema 定义）
- `audit.py --format text` 的人类可读格式（带颜色？）
- `verify.py --json` 的 JSON 输出（当前只有 print 语句）
- 所有脚本的 `--help` 完整性检查（init.py 的 --help 缺少描述）

---

## 5. 控制论健全性评分

| 维度 | Marginalia v0.2 (当前) | 采纳建议后 (v0.3) | 评分依据 |
|------|---------------------|-----------------|---------|
| **可观测性** | 3/10 | 8/10 | audit.py 优秀，但缺自动化集成 |
| **可控性** | 2/10 | 7/10 | 演员-控制器混淆 → 分离三回路 |
| **稳定性** | 5/10 | 8/10 | 无振荡设计，但平台集成易出错 |
| **鲁棒性** | 7/10 | 9/10 | 纯 Markdown + 零依赖 = 本身很 robust |
| **平台可移植性** | 4/10 | 9/10 | 缺平台适配层 |
| **总评** | **4.2/10** | **8.2/10** | |

---

## 6. 致谢与评价

Marginalia 的核心洞见——记忆不应被压缩成向量、不应存储在外部数据库、不应绑定特定会话——已经被 17 天 153 页的 OpenClaw 部署完全验证。init.py、audit.py、verify.py 这三个零依赖 Python 脚本在跨平台移植中的表现证明了这个方向的正确性。

本报告的批评集中在**控制架构**层面——不是工具做得不好，而是"AI 自我维护"这个假设在控制论上不成立。这不是 Marginalia 独有的问题——所有 AI 驱动的知识管理系统都面临同样的演员-控制器悖论。Marginalia 有机会成为第一个正确解决这个问题的系统。

**建议优先级**：
1. 🔴 立即: 拆分 rules.md 的收工规则为三回路（建议 #1）
2. 🔴 立即: audit.py 增加 --brief/--exit-code-only（建议 #2）
3. 🟡 短期: node-type 系统增加 report/project 类型（建议 #5）
4. 🟡 短期: init.py 平台感知参数（建议 #3）
5. 🟢 中期: 平台模板目录（建议 #4）
6. 🟢 中期: 标准接口文档（建议 #6）

---

*本报告基于 OpenClaw 平台上 Marginalia v0.2 的 15 天生产级部署数据（605 条 cron 运行记录、18 个主会话、153 页知识库），采用工程控制论（Ashby 必要多样性定律、分离原理、信噪比分析）作为分析框架。*