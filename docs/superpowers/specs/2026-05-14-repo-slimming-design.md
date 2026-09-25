> [!NOTE]
> 本文件中的 CDS/Stock-Claw/OpenClaw 项目专属内容已同步迁移到 CDS-teamWiki。
> 活跃副本位置：`CDS-teamWiki/project/plans/marginalia-2026-05-14-repo-slimming-design.md`
>
> 本文件保留在 Marginalia 开源仓库中作为原始记录，未做删除。

# Marginalia 仓库精简设计

> 日期：2026-05-14
> 状态：已确认
> 目标：将 Marginalia 仓库精简为符合开源标准的、AI 助手可读取的参考模板

---

## 一、项目定位

**Marginalia = AI 助手读取的参考模板仓库。**

用户 clone 本仓库后，AI 编程助手读取其中的协议、模板和示例，在用户自己的项目中生成知识库。仓库本身不是安装包，不是 npm 包，不是可部署服务。

### 用户旅程

```
1. 用户 clone Marginalia 到 ~/download/marginalia
2. 用户对 AI 说："参照 ~/download/marginalia，在我的项目里搭建知识库，并摄入文档"
3. AI 自动完成：创建骨架 → 扫描文档 → 提案确认 → 摄入 → 修改用户项目 CLAUDE.md
4. 后续对话中，AI 按 CLAUDE.md 规则自动读取和写入知识库
```

---

## 二、目标目录结构

```
Marginalia/
├── CLAUDE.md                  # 发现层：指向 schema/ 和 example/（~30行）
├── README.md                  # 面向人类用户
├── LICENSE                    # MIT
├── CONTRIBUTING.md            # 贡献指南
│
├── schema/                    # 协议层
│   ├── rules.md               #   AI 行为规则
│   ├── node-types.md          #   页面类型定义
│   └── first-ingest.md        #   首次摄入指南（一次性，完成后用户可删）
│
├── scripts/                   # 工具层
│   ├── init.py                #   创建知识库骨架
│   ├── audit.py               #   检查知识库健康
│   └── verify.py              #   验证知识库完整性
│
├── templates/                 # 模板层
│   ├── concept.md
│   ├── decision.md
│   └── annotation.md
│
├── example/                   # 示例知识库（AI 参照此结构）
│   ├── index.md
│   ├── concepts/
│   │   └── marginalia.md
│   ├── decisions/
│   │   └── why-marginalia.md
│   └── comparisons/
│       └── memory-systems.md
│
└── archive/                   # 归档（不在主文档引用）
    ├── GPT54/                 #   GPT54 完整原始文件
    └── design-docs/           #   根目录散落的设计文档
```

---

## 三、三阶段工作流

### 阶段 1：初始化（init）

**触发**：用户对 AI 说"帮我搭建知识库"

**AI 执行**：
1. 读取 `schema/rules.md` 和 `schema/node-types.md`
2. 参照 `example/` 在用户项目中创建骨架：
   ```
   wiki/
   ├── index.md
   ├── concepts/
   ├── decisions/
   ├── annotations/
   └── comparisons/
   ```
3. 在用户项目的 `CLAUDE.md` 中追加知识库引用段落

### 阶段 2：首次摄入（first-ingest）

**触发**：骨架创建后自动进入

**AI 执行**：
1. 读取 `schema/first-ingest.md`
2. 扫描用户项目目录，识别可摄入文档
3. 列出文档清单 + 建议分类，等用户确认
4. 确认后按模板写入知识库
5. 更新 `wiki/index.md`
6. 完成后提示用户：首次摄入指南文件可以删除

**`schema/first-ingest.md` 核心内容**：

```markdown
# 首次知识摄入指南

> 本文件在首次摄入完成后可删除。

## 扫描规则
- 识别：*.md, *.txt, *.rst
- 跳过：node_modules/, .git/, build/, dist/, vendor/
- 优先：README.md, docs/, design/, adr/, decisions/

## 分类原则
- 概念/机制/术语定义 → concept
- 技术选型/方案决策 → decision
- 会议/笔记/历史记录 → annotation
- 多方案对比 → comparison

## 执行步骤
1. 扫描 → 2. 提案 → 3. 用户确认 → 4. 写入 → 5. 更新索引 → 6. 运行 audit.py 确认无问题
```

### 阶段 3：日常自动摄入与读取

**触发**：用户每次与 AI 对话，由写入用户项目 `CLAUDE.md` 的段落驱动

**写入用户项目 CLAUDE.md 的段落**（~15行）：

> **注意**：追加前先检查用户项目 CLAUDE.md 中是否已有 `## Marginalia` 段落，如有则更新而非重复追加。

```markdown
## Marginalia 知识库

本项目使用 Marginalia 边注系统。知识库位于 wiki/。

### 每次对话开始时
1. 读取 wiki/index.md 了解知识库全貌

### 对话中遇到以下情况时
- 讨论了新概念或机制 → 在 wiki/concepts/ 创建页面
- 做了技术决策 → 在 wiki/decisions/ 记录
- 发现与已有知识的关系 → 用 [[wikilink]] 链接

### 完成实质工作后
- 更新 wiki/index.md（如有新页面）
- 在相关页面添加批注：> [!memo] YYYY-MM-DD 内容
- 运行 `python3 scripts/audit.py --root wiki/`，处理发现的问题
```

---

## 四、工程控制论分析

### 系统要素映射

| 控制论要素 | 实现 | 可靠性 |
|-----------|------|--------|
| **传感器** | `audit.py`（程序化检查断链、孤儿页、格式） | 高 |
| **控制器** | 用户项目 CLAUDE.md 中的 ~15 行规则 | 中-高（越短遵从率越高） |
| **执行器** | AI 助手 | 中 |
| **反馈回路** | audit → AI 修复 → 再 audit | 闭环 |
| **设定值** | 无断链、无孤儿页、index 完整 | 可验证 |

### 关键设计原则

1. **CLAUDE.md 只做发现层**：不重复 schema/ 的内容，只指向文件路径
2. **体检嵌入收工流程**：audit.py 不是"定期运行"的独立动作，而是"完成实质工作后"的必做步骤
3. **承认 AI 指令不可靠**：设计安全网（audit.py），不依赖 AI 自律
4. **首次摄入用独立文件**：`first-ingest.md` 只在首次使用时读取，完成后可删
5. **追加前检查冲突**：写入用户项目 CLAUDE.md 前先检查是否已有 Marginalia 段落

### 各指令类型遵从率与设计对策

| 指令类型 | 遵从率 | 设计对策 |
|---------|--------|---------|
| 输出格式（`> [!memo]`） | ~90% | 放在 CLAUDE.md 中，可靠 |
| 流程步骤（先 A 再 B） | ~70-85% | 控制在 3 步以内 |
| 收工步骤（完成工作后做 X） | ~50-70% | audit.py 嵌入收工流程 + 作为安全网 |
| 独立定期动作（定期做 X） | ~30-50% | 不使用此模式，全部嵌入已有流程 |

---

## 五、文件变动清单

### 保留并修改

| 文件 | 操作 |
|------|------|
| `CLAUDE.md` | 精简到 ~50 行 |
| `README.md` | 重写：项目定位 + 使用场景 + 快速开始 + 目录说明 |

### 移动（从 GPT54 吸收）

| 源 | 目标 |
|-----|------|
| `GPT54/LICENSE` | `LICENSE` |
| `GPT54/CONTRIBUTING.md` | `CONTRIBUTING.md` |
| `GPT54/schema/rules.md` | `schema/rules.md` |
| `GPT54/schema/node-types.md` | `schema/node-types.md` |
| `GPT54/scripts/init.py` | `scripts/init.py` |
| `GPT54/scripts/audit.py` | `scripts/audit.py` |
| `GPT54/scripts/verify.py` | `scripts/verify.py` |

### 移动（从 docs/ 到 example/）

| 源 | 目标 |
|-----|------|
| `docs/concepts/Marginalia.md` | `example/concepts/marginalia.md` |
| `docs/decisions/why-marginalia.md` | `example/decisions/why-marginalia.md` |
| `docs/comparisons/memory-systems.md` | `example/comparisons/memory-systems.md` |
| — | `example/index.md`（新建，精简版索引） |

### 新建

| 文件 | 内容 |
|------|------|
| `schema/first-ingest.md` | 首次摄入指南 |

### 归档

| 源 | 目标 |
|-----|------|
| `GPT54/` 整个目录 | `archive/GPT54/` |
| `design-glm-51.md` | `archive/design-docs/` |
| `knowledge-base-quality-control.md` | `archive/design-docs/` |
| `system_morphology_analysis_framework.md` | `archive/design-docs/` |
| `system_morphology_analysis_report.md` | `archive/design-docs/` |
| `user-knowledge-base-workflow-Deepseek-v4-pro.md` | `archive/design-docs/` |
| `GPT54-user-journey-design.k26` | `archive/design-docs/` |
| `.trae/` | `archive/.trae/` |
| `trash_rm_scripts/` | `archive/trash_rm_scripts/` |

### 删除

| 文件/目录 | 原因 |
|----------|------|
| `docs/`（大部分） | 保留内容已移到 example/，其余归档 |
| `examples/wiki/` | 被 example/ 替代 |
| `scripts/init.sh` | 被 Python 脚本替代 |
| `scripts/lint.sh` | 被 Python 脚本替代 |
| `.pytest_cache/` | 构建产物 |
| `GPT54/schema/task-states.md` | 日常维护不需要状态机 |
| `GPT54/schema/ingest.md` | 被 first-ingest.md 替代 |
| `GPT54/tests/` | 保留测试需重新组织，暂归档到 archive/GPT54/ |

---

## 六、精简后 CLAUDE.md 大纲（~30行）

> CLAUDE.md 只做发现层，不重复 schema/ 中的详细规则。

```markdown
# Marginalia 边注系统

AI 助手驱动的文档级批注记忆系统。本仓库是参考模板。

## 快速进入
1. 读 schema/rules.md 理解行为规则
2. 读 schema/node-types.md 理解页面类型
3. 读 schema/first-ingest.md 理解首次摄入流程
4. 参照 example/ 在用户项目中创建知识库

## 三原则
- 同位：记忆附着在知识点旁边
- 无损：保留原话，不压缩
- 解耦：纯 Markdown，独立于平台

## 批注格式
> [!memo] YYYY-MM-DD 内容
```

---

## 七、成功标准

1. 根目录干净：只有 CLAUDE.md、README.md、LICENSE、CONTRIBUTING.md、.gitignore
2. 一个新访客 5 分钟内理解项目是什么、怎么用
3. AI 编程助手读取本仓库后能在用户项目中正确创建知识库
4. 三阶段工作流（init → 首次摄入 → 日常）完整可用
5. audit.py 作为安全网，确保反馈闭环
