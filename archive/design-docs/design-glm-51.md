# GPT54 用户知识库构建体验设计方案

> 日期：2026-05-13
> 状态：设计稿
> 依据：GPT54/PRD.md + GPT54/SPEC.md + GPT54/IMPLEMENTATION_PLAN.md

---

## 一、设计前提

### 1.1 确认的约束

| 项目 | 结论 |
|------|------|
| 目标用户 | 熟悉 AI 助手的开发者（已配置 Claude Code / Cursor 等） |
| 项目关系 | GPT54 是工作目录，最终上传的是按协议重构的 Marginalia 仓库 |
| 摄入方式 | AI 助手驱动摄入（用户对 AI 说需求，AI 按协议执行） |
| 核心约束 | 原创、零依赖、离线优先、纯文本优先、可审计 |

### 1.2 设计目标

用户从 `git clone` 到第一次成功摄入知识节点，应该只需要：

1. 运行一条初始化命令
2. 用 AI 助手打开项目
3. 对 AI 说一句话

不需要手动编辑规则文件、不需要理解 PRD/SPEC 全文、不需要额外安装任何东西。

---

## 二、用户旅程全景

### 2.1 理想旅程（7 步闭环）

```
Step 1: git clone Marginalia
Step 2: python3 scripts/init.py --root ./my-kb
        → 生成骨架 + AI 发现入口 + schema/ 完整规则
Step 3: 用 Claude Code / Cursor 打开 ./my-kb
        → AI 自动读取 CLAUDE.md → 发现 schema/ → 加载协议
Step 4: 对 AI 说"帮我整理这份材料关于 XXX"
        → AI 按 schema/ingest.md 执行摄入工作流
        → 创建节点 → 更新索引 → 回写状态
Step 5: python3 scripts/audit.py --root ./my-kb
        → 发现偏差，输出结构化报告
Step 6: AI 根据审计结果修复偏差
        → 最小必要修改 → 验证 → 回写
Step 7: python3 scripts/verify.py --root ./my-kb
        → 验证通过，循环 Step 4-7
```

### 2.2 旅程中的 5 个核心断点

| 编号 | 断点 | 严重程度 | 说明 |
|------|------|---------|------|
| B1 | AI 助手不知道协议 | 🔴 致命 | 用户 clone 后，AI 不知道要读 PRD/SPEC，不知道节点格式、状态流转、回写规则 |
| B2 | init.py 不生成 AI 配置 | 🔴 致命 | 当前 init.py 只创建目录和空文件，不生成 CLAUDE.md 或等效规则文件 |
| B3 | 没有摄入入口 | 🟡 重要 | M0/M1 只有 init/audit/verify，没有 ingest 工作流定义 |
| B4 | PRD/SPEC 对用户太重 | 🟡 重要 | PRD 490 行 + SPEC 720 行，AI 能读完但用户理解成本高 |
| B5 | Marginalia 自身 vs 用户知识库混淆 | 🟠 中等 | 仓库包含项目文档，用户可能分不清"项目文档"和"知识库模板" |

---

## 三、方案选型

### 3.1 方案 A：CLAUDE.md 即协议入口

init.py 生成 CLAUDE.md，其中包含 PRD/SPEC 的精简版——足够让 AI 知道怎么按协议工作。

| 维度 | 评价 |
|------|------|
| 优势 | 零额外配置，init 一次即可用；与 AI 助手生态天然兼容 |
| 劣势 | CLAUDE.md 需精心控制长度；已有 CLAUDE.md 时冲突；协议更新时已初始化的知识库不会自动更新 |
| 结论 | ❌ 放弃——CLAUDE.md 承载精简版协议，与已有文件冲突且难维护 |

### 3.2 方案 B：Skill/Plugin 封装

将 GPT54 协议封装为 Claude Code Skill 或 Cursor Rule，用户安装 Skill 获得协议能力。

| 维度 | 评价 |
|------|------|
| 优势 | 协议与数据彻底分离；更新只需更新 Skill |
| 劣势 | 依赖特定 AI 助手平台；违反零依赖约束；安装门槛高 |
| 结论 | ❌ 放弃——违反零依赖和平台无关原则 |

### 3.3 方案 C：schema/ 为主，CLAUDE.md 为指路牌（推荐）

init.py 生成骨架时，自动生成 CLAUDE.md（仅指路牌），协议主体在 schema/ 中。AI 读 CLAUDE.md → 发现 schema/ → 加载完整规则。

| 维度 | 评价 |
|------|------|
| 优势 | 解决全部 5 个断点；已有 CLAUDE.md 不冲突；协议更新只改 schema/；平台无关 |
| 劣势 | CLAUDE.md 需精心控制长度；需新增 schema/ingest.md |
| 结论 | ✅ 采用 |

---

## 四、方案 C 详细设计

### 4.1 核心架构：四层分离

```
┌─────────────────────────────────────────────┐
│  发现层（指路牌）                              │
│  CLAUDE.md / .cursorrules / .windsurfrules   │
│  职责：告诉 AI "去读 schema/"                  │
│  大小：< 15 行                                │
└──────────────────┬──────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│  协议层（完整规则）                            │
│  schema/                                     │
│  职责：定义 AI 必须遵守的全部规则               │
│  消费者：AI 助手                              │
└──────────────────┬──────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│  执行层（脚本）                               │
│  scripts/                                    │
│  职责：init / audit / verify 的可执行实现      │
│  消费者：人类 + AI 助手                        │
└──────────────────┬──────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│  数据层（知识 + 状态 + 审计）                   │
│  docs/ + project/ + audit/ + runtime/        │
│  职责：持久化所有知识产物和系统状态              │
│  消费者：人类 + AI 助手 + 审计脚本              │
└─────────────────────────────────────────────┘
```

### 4.2 发现层设计：CLAUDE.md 指路牌

#### 4.2.1 CLAUDE.md 不存在时

init.py 生成以下内容：

```markdown
# CLAUDE.md

<!-- GPT54-PROTOCOL-START version="0.1.0" -->
## GPT54 知识工程协议

本仓库遵循 GPT54 协议。执行任何知识操作前，必须先读取 `schema/` 目录下的规则文件。

读取顺序：
1. `schema/rules.md` — 执行规则与禁止项
2. `schema/node-types.md` — 节点类型与模板
3. `schema/task-states.md` — 任务状态机
4. `schema/ingest.md` — 摄入工作流

协议版本：v0.1.0
<!-- GPT54-PROTOCOL-END -->
```

**不超过 15 行**。CLAUDE.md 只是指路牌，协议的完整内容在 schema/ 里。

#### 4.2.2 CLAUDE.md 已存在时

init.py 检测到已有 CLAUDE.md，执行最小追加：

1. 扫描文件中是否包含 `GPT54-PROTOCOL-START` 标记
2. 不包含 → 在文件末尾追加标记段
3. 已包含 → 比对版本号，若不一致则替换标记段内容
4. 不覆盖、不修改标记段以外的任何内容

追加内容与 4.2.1 中的标记段完全相同。

#### 4.2.3 边界标记规范

```
<!-- GPT54-PROTOCOL-START version="X.Y.Z" -->
...协议引用内容...
<!-- GPT54-PROTOCOL-END -->
```

- `version` 属性与 `schema/rules.md` 中的版本号一致
- init.py 可精确替换两个标记之间的内容
- 用户删除标记段即可完全移除 GPT54 引用
- audit.py 检查标记是否存在、版本是否一致

#### 4.2.4 多平台适配

init.py 通过可选参数生成不同平台的发现文件：

```bash
python3 scripts/init.py --root ./my-kb                          # 默认：CLAUDE.md
python3 scripts/init.py --root ./my-kb --platform cursor        # 额外生成 .cursorrules
python3 scripts/init.py --root ./my-kb --platform windsurf      # 额外生成 .windsurfrules
python3 scripts/init.py --root ./my-kb --platform all           # 生成全部
```

所有平台文件内容相同，只是文件名不同。**协议主体始终在 schema/ 中**。

### 4.3 协议层设计：schema/ 扩展

#### 4.3.1 新增 schema/ingest.md

当前 SPEC 定义了 schema/ 下三个文件：rules.md、node-types.md、task-states.md。需要新增 `schema/ingest.md`，定义摄入工作流。

**ingest.md 最小内容**：

```markdown
# Ingest Workflow

## 触发条件

用户或 AI 助手需要新增一个知识节点。

## 执行顺序

1. 读取 `project/project.md`，确认项目范围
2. 读取 `docs/index.md`，了解现有知识网络
3. 确定节点类型（concept / decision / note / entity）
4. 创建节点文件到 `docs/nodes/`，包含最小字段：
   - 唯一标题
   - 节点类型
   - 目的说明
   - 主体内容
   - 相关链接（至少一个 [[wikilink]]）
   - 更新时间
5. 更新 `docs/index.md`，将新节点加入对应类别
6. 在 `runtime/tasks/` 创建任务记录
7. 运行 `python3 scripts/audit.py --root .` 验证
8. 更新 `project/progress.md`

## 禁止项

- 禁止创建无 [[wikilink]] 的孤立节点
- 禁止跳过 index.md 更新
- 禁止跳过 progress.md 回写
- 禁止在未读 project.md 的情况下新增节点
```

#### 4.3.2 schema/rules.md 扩展

在现有 rules.md 中增加一条：

```
8. 执行知识摄入时，必须按 schema/ingest.md 定义的顺序执行
```

### 4.4 执行层设计：init.py 改动

#### 4.4.1 改动清单

| 改动 | 说明 |
|------|------|
| 新增 CLAUDE.md 生成逻辑 | 不存在则创建，已存在则追加标记段 |
| 新增 --platform 参数 | 可选生成 .cursorrules / .windsurfrules |
| 新增 schema/ingest.md 模板 | 初始化时一并生成 |
| 新增 --update-protocol 参数 | 仅更新 CLAUDE.md 标记段和 schema/，不重建目录 |

#### 4.4.2 FILES 字典扩展

```python
FILES = {
    # ... 现有文件 ...
    "schema/ingest.md": "# Ingest Workflow\n\n## 触发条件\n\n用户或 AI 助手需要新增一个知识节点。\n\n## 执行顺序\n\n1. 读取 project/project.md\n2. 读取 docs/index.md\n3. 确定节点类型\n4. 创建节点文件到 docs/nodes/\n5. 更新 docs/index.md\n6. 创建任务记录到 runtime/tasks/\n7. 运行 audit.py 验证\n8. 更新 project/progress.md\n\n## 禁止项\n\n- 禁止创建无 [[wikilink]] 的孤立节点\n- 禁止跳过 index.md 更新\n- 禁止跳过 progress.md 回写\n",
}
```

#### 4.4.3 CLAUDE.md 生成逻辑伪代码

```python
PROTOCOL_BLOCK = '''<!-- GPT54-PROTOCOL-START version="0.1.0" -->
## GPT54 知识工程协议

本仓库遵循 GPT54 协议。执行任何知识操作前，必须先读取 `schema/` 目录下的规则文件。

读取顺序：
1. `schema/rules.md` — 执行规则与禁止项
2. `schema/node-types.md` — 节点类型与模板
3. `schema/task-states.md` — 任务状态机
4. `schema/ingest.md` — 摄入工作流

协议版本：v0.1.0
<!-- GPT54-PROTOCOL-END -->'''

def write_claude_md(root: Path) -> None:
    claude_md = root / "CLAUDE.md"
    if claude_md.exists():
        content = claude_md.read_text(encoding="utf-8")
        if "GPT54-PROTOCOL-START" in content:
            # 替换已有标记段
            import re
            pattern = r'<!-- GPT54-PROTOCOL-START.*?-->.*?<!-- GPT54-PROTOCOL-END -->'
            content = re.sub(pattern, PROTOCOL_BLOCK, content, flags=re.DOTALL)
        else:
            # 追加标记段
            content = content.rstrip() + "\n\n" + PROTOCOL_BLOCK + "\n"
        claude_md.write_text(content, encoding="utf-8")
    else:
        claude_md.write_text("# CLAUDE.md\n\n" + PROTOCOL_BLOCK + "\n", encoding="utf-8")
```

### 4.5 审计层设计：audit.py 扩展

#### 4.5.1 新增检查项

| 检查项 | 严重级别 | 说明 |
|--------|---------|------|
| CLAUDE.md 缺失 GPT54 标记 | P1 | AI 助手可能无法发现协议规则 |
| CLAUDE.md 版本与 schema/ 不一致 | P2 | 可能导致 AI 执行过时规则 |
| schema/ingest.md 缺失 | P1 | 摄入工作流未定义 |
| docs/index.md 未覆盖节点 | P1 | 已有，不变 |
| 孤立节点 | P2 | 已有，不变 |

#### 4.5.2 版本一致性检查逻辑

```python
def check_protocol_version(root: Path) -> list[dict]:
    issues = []
    claude_md = root / "CLAUDE.md"
    rules_md = root / "schema" / "rules.md"

    if not claude_md.exists():
        issues.append(make_issue("missing_claude_md_protocol", "P1",
                                 str(claude_md), "CLAUDE.md 缺少 GPT54 协议标记"))
        return issues

    content = claude_md.read_text(encoding="utf-8")
    if "GPT54-PROTOCOL-START" not in content:
        issues.append(make_issue("missing_claude_md_protocol", "P1",
                                 str(claude_md), "CLAUDE.md 缺少 GPT54 协议标记"))
        return issues

    import re
    match = re.search(r'GPT54-PROTOCOL-START version="([^"]+)"', content)
    claude_version = match.group(1) if match else "unknown"

    rules_content = rules_md.read_text(encoding="utf-8") if rules_md.exists() else ""
    rules_match = re.search(r"规则版本[：:]\s*v?([\d.]+)", rules_content)
    rules_version = rules_match.group(1) if rules_match else "unknown"

    if claude_version != rules_version and rules_version != "unknown":
        issues.append(make_issue("protocol_version_mismatch", "P2",
                                 str(claude_md),
                                 f"CLAUDE.md 版本 {claude_version} 与 schema/ 版本 {rules_version} 不一致"))
    return issues
```

### 4.6 仓库结构更新

最终仓库结构在 SPEC 6.0 基础上新增：

```text
ROOT/
├── CLAUDE.md                          ← 新增：AI 助手发现入口
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── CHANGELOG.md
├── PRD.md
├── SPEC.md
├── docs/
│   ├── index.md
│   └── nodes/
├── project/
│   ├── project.md
│   ├── plan.md
│   ├── progress.md
│   └── open-questions.md
├── schema/
│   ├── rules.md
│   ├── node-types.md
│   ├── task-states.md
│   └── ingest.md                      ← 新增：摄入工作流定义
├── audit/
│   ├── baselines/
│   ├── reports/
│   └── snapshots/
├── runtime/
│   ├── tasks/
│   └── logs/
├── scripts/
│   ├── init.py                        ← 改动：生成 CLAUDE.md + ingest.md
│   ├── audit.py                       ← 改动：新增协议标记和版本检查
│   └── verify.py
└── tests/
    ├── fixtures/
    └── smoke/
```

---

## 五、断点解决映射

| 断点 | 解决方式 | 涉及改动 |
|------|---------|---------|
| B1: AI 不知道协议 | CLAUDE.md 指路牌 → schema/ 完整规则 | init.py 新增 CLAUDE.md 生成 |
| B2: init.py 不生成 AI 配置 | init.py 自动生成 CLAUDE.md（含标记段） | init.py 改动 |
| B3: 没有摄入入口 | 新增 schema/ingest.md，定义完整摄入工作流 | 新增文件 + init.py |
| B4: PRD/SPEC 对用户太重 | 用户只读 README，AI 读 CLAUDE.md → schema/，各取所需 | README.md 承担用户版摘要 |
| B5: 项目文档 vs 知识库混淆 | README 明确说明"本仓库是协议+参考实现，用 init.py 生成你自己的知识库" | README.md 改动 |

---

## 六、完整用户操作手册

### 6.1 从零开始构建知识库

```bash
# Step 1: 克隆仓库
git clone https://github.com/xxx/Marginalia.git
cd Marginalia

# Step 2: 初始化你的知识库
python3 scripts/init.py --root ./my-kb

# Step 3: 用 Claude Code 打开
claude ./my-kb
# AI 自动读取 CLAUDE.md → 发现 schema/ → 加载协议

# Step 4: 对 AI 说
"帮我整理这份关于 XXX 的材料，创建一个 concept 节点"
# AI 按 schema/ingest.md 执行：
#   1. 读 project.md 确认范围
#   2. 读 index.md 了解现有网络
#   3. 创建节点文件
#   4. 更新 index.md
#   5. 创建任务记录
#   6. 运行 audit.py 验证
#   7. 更新 progress.md

# Step 5: 周期审计
python3 scripts/audit.py --root ./my-kb

# Step 6: 验证
python3 scripts/verify.py --root ./my-kb
```

### 6.2 已有 CLAUDE.md 的项目

```bash
# 在已有项目中初始化 GPT54 协议
python3 scripts/init.py --root ./existing-project

# init.py 检测到已有 CLAUDE.md
# → 在末尾追加 GPT54-PROTOCOL 标记段
# → 不影响原有内容

# 如果只想更新协议标记（不重建目录）
python3 scripts/init.py --root ./existing-project --update-protocol
```

### 6.3 使用 Cursor 的用户

```bash
python3 scripts/init.py --root ./my-kb --platform cursor
# 同时生成 CLAUDE.md 和 .cursorrules
```

---

## 七、SPEC 修订建议

以下修订需在实施前更新到 SPEC.md：

### 7.1 仓库结构合同修订

在 SPEC 6.0 的仓库结构中新增：

```
├── CLAUDE.md              ← 新增
├── schema/
│   └── ingest.md          ← 新增
```

### 7.2 目录职责合同修订

新增 CLAUDE.md 职责：

```
CLAUDE.md 职责：AI 助手发现入口。

约束：
- 必须包含 GPT54-PROTOCOL-START/END 标记段
- 标记段内必须指向 schema/ 目录
- 标记段外的内容由用户自定义，系统不得覆盖
- 版本号必须与 schema/rules.md 一致
```

### 7.3 审计协议合同修订

在最小审计范围（SPEC 12.2）中新增：

```
9. CLAUDE.md 缺少 GPT54 协议标记
10. CLAUDE.md 版本与 schema/ 不一致
11. schema/ingest.md 缺失
```

### 7.4 初始化工作流修订

在 SPEC 13.1 初始化工作流的输出中新增：

```
- CLAUDE.md（含 GPT54 协议标记段）
- schema/ingest.md（摄入工作流定义）
```

---

## 八、风险与对策

| 风险 | 严重程度 | 对策 |
|------|---------|------|
| CLAUDE.md 标记段被用户误删 | 中 | audit.py 检测到缺失时输出 P1 问题，init.py --update-protocol 可修复 |
| AI 助手忽略 CLAUDE.md 中的 schema/ 引用 | 中 | CLAUDE.md 中使用明确的文件路径和读取顺序，减少歧义 |
| schema/ 文件过多导致 AI 注意力稀释 | 中 | 严格限制 schema/ 文件数量（当前 4 个），每个文件不超过 50 行 |
| 不同 AI 助手对 CLAUDE.md 的处理方式不同 | 低 | 核心协议在 schema/ 中，CLAUDE.md 只是指路牌，即使 AI 不读 CLAUDE.md，用户也可手动指向 schema/ |
| 协议版本更新后已初始化知识库不同步 | 低 | audit.py 检测版本不一致，init.py --update-protocol 可更新 |

---

## 九、与现有 IMPLEMENTATION_PLAN 的关系

本方案不替代 IMPLEMENTATION_PLAN，而是在其基础上扩展。具体影响：

| IMPLEMENTATION_PLAN Task | 影响 |
|--------------------------|------|
| Task 1: M0 仓库骨架 | 新增 CLAUDE.md 生成逻辑 |
| Task 2: 项目状态与规则文件 | 新增 schema/ingest.md |
| Task 3: init.py | 改动：新增 CLAUDE.md 生成 + --platform 参数 + --update-protocol 参数 |
| Task 4: audit.py | 改动：新增协议标记和版本检查 |
| Task 5: verify.py | 无影响 |
| Task 6: 冒烟测试 | 新增 CLAUDE.md 生成和追加的测试用例 |

建议在完成 M0/M1 基础闭环后，以 M1.5 的形式实施本方案的改动。