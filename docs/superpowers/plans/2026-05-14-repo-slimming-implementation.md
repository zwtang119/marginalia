# Marginalia 仓库精简实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 Marginalia 仓库精简为符合开源标准的、AI 助手可读取的参考模板

**Architecture:** 三阶段工作流（init → 首次摄入 → 日常）。仓库定位为 AI 助手的参考模板，不是安装包。GPT54 子项目的内容吸收合并到根目录层级，不相关的 AI 会话产物归档。

**Tech Stack:** Python 3（零依赖脚本）、Markdown、Shell

**Spec:** `docs/superpowers/specs/2026-05-14-repo-slimming-design.md`

---

## 文件结构映射

| 操作 | 文件 | 职责 |
|------|------|------|
| 归档 | `archive/` | 所有不直接相关的历史文件 |
| 吸收 | `schema/rules.md` | AI 行为规则（来自 GPT54） |
| 吸收 | `schema/node-types.md` | 页面类型定义（来自 GPT54） |
| 新建 | `schema/first-ingest.md` | 首次摄入指南 |
| 吸收 | `scripts/init.py` | 创建知识库骨架（来自 GPT54，需改造） |
| 吸收 | `scripts/audit.py` | 检查知识库健康（来自 GPT54，需改造） |
| 吸收 | `scripts/verify.py` | 验证知识库（来自 GPT54，需改造） |
| 保留 | `templates/concept.md` | 概念页面模板 |
| 保留 | `templates/decision.md` | 决策记录模板 |
| 保留 | `templates/annotation.md` | 批注页面模板 |
| 移动 | `example/concepts/marginalia.md` | 示例概念页（来自 docs/） |
| 移动 | `example/decisions/why-marginalia.md` | 示例决策页（来自 docs/） |
| 移动 | `example/comparisons/memory-systems.md` | 示例对比页（来自 docs/） |
| 新建 | `example/index.md` | 示例知识库索引 |
| 重写 | `CLAUDE.md` | 发现层入口（~30行） |
| 重写 | `README.md` | 面向人类的项目介绍 |
| 移动 | `LICENSE` | MIT 许可（来自 GPT54） |
| 移动 | `CONTRIBUTING.md` | 贡献指南（来自 GPT54，需改造） |

---

### Task 1: 创建归档目录并移动 AI 会话产物

**Files:**
- Create: `archive/design-docs/`（目录）
- Move: 6 个根目录散落文件 → `archive/design-docs/`
- Move: `.trae/` → `archive/.trae/`
- Move: `trash_rm_scripts/` → `archive/trash_rm_scripts/`

- [ ] **Step 1: 创建归档目录**

```bash
mkdir -p archive/design-docs archive/.trae archive/trash_rm_scripts
```

- [ ] **Step 2: 移动根目录散落的设计文档**

```bash
mv design-glm-51.md archive/design-docs/
mv knowledge-base-quality-control.md archive/design-docs/
mv system_morphology_analysis_framework.md archive/design-docs/
mv system_morphology_analysis_report.md archive/design-docs/
mv user-knowledge-base-workflow-Deepseek-v4-pro.md archive/design-docs/
mv GPT54-user-journey-design.k26 archive/design-docs/
```

- [ ] **Step 3: 移动 .trae/ 和 trash_rm_scripts/**

```bash
mv .trae/documents archive/.trae/
mv .trae/specs archive/.trae/
rm -rf .trae
mv trash_rm_scripts/* archive/trash_rm_scripts/
rm -rf trash_rm_scripts
```

- [ ] **Step 4: 验证根目录已清理**

```bash
ls -la | grep -v "^\." | head -20
```

Expected: 根目录不再有 design-glm-51.md、knowledge-base-quality-control.md 等文件

---

### Task 2: 归档 GPT54 子目录

**Files:**
- Move: `GPT54/` → `archive/GPT54/`

- [ ] **Step 1: 移动整个 GPT54 目录到归档**

```bash
mv GPT54 archive/GPT54
```

- [ ] **Step 2: 验证 GPT54 已不在根目录**

```bash
ls -d GPT54 2>&1
```

Expected: "No such file or directory"

- [ ] **Step 3: 验证归档目录内容完整**

```bash
ls archive/GPT54/
```

Expected: 显示 CLAUDE.md, README.md, schema/, scripts/, tests/ 等

---

### Task 3: 创建 schema/ 协议层

**Files:**
- Create: `schema/rules.md`
- Create: `schema/node-types.md`
- Create: `schema/first-ingest.md`

- [ ] **Step 1: 创建 schema 目录**

```bash
mkdir -p schema
```

- [ ] **Step 2: 创建 schema/rules.md**

写入 `schema/rules.md`：

```markdown
# Rules

- 规则版本：v0.2.0

## 读取规则

1. 每次对话开始，先读 wiki/index.md 了解知识库全貌
2. 遇到相关知识话题，沿 [[wikilink]] 读取相关页面
3. 读取页面时连同页内批注一起读取

## 写入规则

1. 对话中产生新概念/机制 → 在 wiki/concepts/ 创建页面
2. 做了技术决策 → 在 wiki/decisions/ 记录
3. 发现与已有知识的关系 → 用 [[wikilink]] 链接

## 收工规则

1. 更新 wiki/index.md（如有新页面）
2. 在相关页面添加批注：> [!memo] YYYY-MM-DD 内容
3. 运行 `python3 scripts/audit.py --root wiki/`，处理发现的问题

## 约束

- 不得引入第三方依赖
- 不得把知识库实现成在线服务或数据库产品
- 批注必须包含日期
```

- [ ] **Step 3: 创建 schema/node-types.md**

写入 `schema/node-types.md`：

```markdown
# Node Types

## concept（概念）

定义概念、机制或术语。回答"这是什么"。

最小字段：
- 标题
- 一句话定义
- 详细说明
- 相关链接（[[wikilink]]）

## decision（决策）

记录技术选型或方案决策。回答"为什么选这个"。

最小字段：
- 标题
- 背景
- 候选方案
- 最终决策及理由
- 相关链接

## annotation（批注）

时间敏感的补充信息或历史记录。回答"当时发生了什么"。

格式：
```markdown
> [!memo] YYYY-MM-DD 内容
>
> 来源：谁说的/什么文档
> 上下文：当时的背景
```

## comparison（对比）

多方案对比分析。

最小字段：
- 标题
- 对比维度
- 各方案分析
- 结论
- 相关链接
```

- [ ] **Step 4: 创建 schema/first-ingest.md**

写入 `schema/first-ingest.md`：

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

1. 扫描用户项目目录，识别可摄入文档
2. 列出文档清单 + 建议分类，等用户确认
3. 确认后按 templates/ 中的模板写入知识库
4. 更新 wiki/index.md
5. 运行 audit.py 确认无问题
6. 在用户项目的 CLAUDE.md 中追加知识库引用段落
7. 提示用户：首次摄入指南文件可以删除
```

- [ ] **Step 5: 验证 schema/ 文件**

```bash
ls schema/
```

Expected: first-ingest.md, node-types.md, rules.md

---

### Task 4: 改造并创建 scripts/ 工具层

**Files:**
- Create: `scripts/init.py`（基于 GPT54 改造）
- Create: `scripts/audit.py`（基于 GPT54 改造）
- Create: `scripts/verify.py`（基于 GPT54 改造）

- [ ] **Step 1: 删除旧的 shell 脚本**

```bash
rm -f scripts/init.sh scripts/lint.sh
```

- [ ] **Step 2: 创建 scripts/init.py**

基于 GPT54 的 init.py，改造为 Marginalia 版本。写入 `scripts/init.py`：

```python
#!/usr/bin/env python3
import argparse
from pathlib import Path


MARGINALIA_CLAUDE_MD_SNIPPET = """\
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
"""

DIRECTORIES = [
    "wiki/concepts",
    "wiki/decisions",
    "wiki/annotations",
    "wiki/comparisons",
]

FILES = {
    "wiki/index.md": "# 知识库索引\n\n## 概念\n\n## 决策\n\n## 批注\n\n## 对比\n",
}


def initialize(root: Path) -> None:
    for relative_dir in DIRECTORIES:
        (root / relative_dir).mkdir(parents=True, exist_ok=True)
    for relative_file, content in FILES.items():
        path = root / relative_file
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text(content, encoding="utf-8")


def append_claude_md(target: Path) -> None:
    if not target.exists():
        target.write_text(MARGINALIA_CLAUDE_MD_SNIPPET, encoding="utf-8")
        return
    text = target.read_text(encoding="utf-8")
    if "## Marginalia 知识库" in text:
        start = text.find("## Marginalia 知识库")
        end = text.find("\n## ", start + 1)
        if end == -1:
            text = text[:start] + MARGINALIA_CLAUDE_MD_SNIPPET
        else:
            text = text[:start] + MARGINALIA_CLAUDE_MD_SNIPPET + text[end:]
    else:
        text = text.rstrip() + "\n\n" + MARGINALIA_CLAUDE_MD_SNIPPET
    target.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    args = parser.parse_args()
    root = Path(args.root).resolve()

    initialize(root)
    claude_md = root / "CLAUDE.md"
    append_claude_md(claude_md)

    print(f"Initialized Marginalia knowledge base at {root / 'wiki'}")
    print(f"Updated {claude_md} with Marginalia knowledge base rules")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 3: 创建 scripts/audit.py**

基于 GPT54 的 audit.py，改造为 Marginalia 版本。写入 `scripts/audit.py`：

```python
#!/usr/bin/env python3
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path


def find_wikilinks(text: str) -> list[str]:
    return re.findall(r"\[\[([^\]]+)\]\]", text)


def find_all_md_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.md") if p.is_file())


def check_broken_links(root: Path) -> list[dict]:
    issues = []
    for md_file in find_all_md_files(root):
        text = md_file.read_text(encoding="utf-8")
        for link in find_wikilinks(text):
            link_path = link.strip()
            candidates = [
                root / f"{link_path}.md",
                root / f"{link_path}",
                root.parent / f"{link_path}.md",
                root.parent / f"{link_path}",
            ]
            if not any(c.exists() for c in candidates):
                rel = md_file.relative_to(root)
                issues.append({
                    "id": f"BROKEN-{len(issues) + 1:04d}",
                    "severity": "P1",
                    "type": "broken_wikilink",
                    "path": str(rel),
                    "message": f"断链：[[{link_path}]]（在 {rel} 中）",
                    "suggested_action": f"创建 {link_path}.md 或修正链接",
                })
    return issues


def check_orphan_pages(root: Path) -> list[dict]:
    all_pages = set()
    all_links = set()
    for md_file in find_all_md_files(root):
        rel = md_file.relative_to(root)
        if rel.name == "index.md":
            continue
        all_pages.add(str(rel))
        text = md_file.read_text(encoding="utf-8")
        for link in find_wikilinks(text):
            all_links.add(link.strip())

    issues = []
    for page in sorted(all_pages):
        page_stem = Path(page).stem
        if page_stem not in all_links and str(page) not in all_links:
            issues.append({
                "id": f"ORPHAN-{len(issues) + 1:04d}",
                "severity": "P2",
                "type": "orphan_page",
                "path": page,
                "message": f"孤儿页：{page}（无入链）",
                "suggested_action": f"在 index.md 或相关页面添加 [[{page_stem}]] 链接",
            })
    return issues


def check_index_exists(root: Path) -> list[dict]:
    issues = []
    if not (root / "index.md").exists():
        issues.append({
            "id": "IDX-0001",
            "severity": "P0",
            "type": "missing_index",
            "path": "index.md",
            "message": "缺少索引文件 wiki/index.md",
            "suggested_action": "创建 wiki/index.md",
        })
    return issues


def audit(root: Path) -> dict:
    issues = []
    issues.extend(check_index_exists(root))
    issues.extend(check_broken_links(root))
    issues.extend(check_orphan_pages(root))

    distribution = {"P0": 0, "P1": 0, "P2": 0, "P3": 0}
    for issue in issues:
        severity = issue["severity"]
        distribution[severity] = distribution.get(severity, 0) + 1

    return {
        "summary": f"发现 {len(issues)} 个问题",
        "issues": issues,
        "severity_distribution": distribution,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    args = parser.parse_args()
    root = Path(args.root).resolve()

    if not root.exists():
        print(f"目录不存在：{root}")
        return 1

    report = audit(root)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["severity_distribution"].get("P0", 0) > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: 创建 scripts/verify.py**

基于 GPT54 的 verify.py，改造为检查 Marginalia 知识库基本结构。写入 `scripts/verify.py`：

```python
#!/usr/bin/env python3
import argparse
from pathlib import Path


REQUIRED_DIRS = [
    "concepts",
    "decisions",
    "annotations",
    "comparisons",
]

REQUIRED_FILES = [
    "index.md",
]


def verify(root: Path) -> list[str]:
    problems = []
    for d in REQUIRED_DIRS:
        if not (root / d).is_dir():
            problems.append(f"缺少目录：{d}/")
    for f in REQUIRED_FILES:
        if not (root / f).is_file():
            problems.append(f"缺少文件：{f}")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    args = parser.parse_args()
    root = Path(args.root).resolve()

    if not root.exists():
        print(f"目录不存在：{root}")
        return 1

    problems = verify(root)
    if problems:
        for p in problems:
            print(p)
        return 1
    print("Verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 5: 验证脚本可运行**

```bash
python3 scripts/init.py --root /tmp/test-marginalia-init
ls /tmp/test-marginalia-init/wiki/
python3 scripts/verify.py --root /tmp/test-marginalia-init/wiki
python3 scripts/audit.py --root /tmp/test-marginalia-init/wiki
rm -rf /tmp/test-marginalia-init
```

Expected: init 创建 wiki/ 骨架，verify 通过，audit 显示无 P0 问题

---

### Task 5: 创建 example/ 示例知识库

**Files:**
- Create: `example/index.md`
- Move: `docs/concepts/Marginalia.md` → `example/concepts/marginalia.md`
- Move: `docs/decisions/why-marginalia.md` → `example/decisions/why-marginalia.md`
- Move: `docs/comparisons/memory-systems.md` → `example/comparisons/memory-systems.md`

- [ ] **Step 1: 创建 example 目录结构**

```bash
mkdir -p example/concepts example/decisions example/comparisons
```

- [ ] **Step 2: 移动示例文件**

```bash
cp docs/concepts/Marginalia.md example/concepts/marginalia.md
cp docs/decisions/why-marginalia.md example/decisions/why-marginalia.md
cp docs/comparisons/memory-systems.md example/comparisons/memory-systems.md
```

- [ ] **Step 3: 创建 example/index.md**

写入 `example/index.md`：

```markdown
# 知识库索引

## 概念

- [[concepts/marginalia]] — Marginalia 边注系统：同位/无损/解耦三原则

## 决策

- [[decisions/why-marginalia]] — 为什么选择 Marginalia

## 对比

- [[comparisons/memory-systems]] — 记忆系统对比矩阵
```

- [ ] **Step 4: 删除旧的 examples/ 目录**

```bash
rm -rf examples/
```

- [ ] **Step 5: 验证 example/ 结构**

```bash
find example/ -type f | sort
```

Expected:
```
example/comparisons/memory-systems.md
example/concepts/marginalia.md
example/decisions/why-marginalia.md
example/index.md
```

---

### Task 6: 清理旧的 docs/ 目录

**Files:**
- Delete: `docs/` 的大部分内容

- [ ] **Step 1: 删除已迁移到 example/ 的原始文件**

```bash
rm -f docs/concepts/Marginalia.md
rm -f docs/decisions/why-marginalia.md
rm -f docs/comparisons/memory-systems.md
```

- [ ] **Step 2: 删除非核心内容**

```bash
rm -rf docs/concepts/
rm -rf docs/decisions/
rm -rf docs/comparisons/
rm -rf docs/annotations/
rm -rf docs/project/
rm -rf docs/entities/
```

- [ ] **Step 3: 保留 superpowers/specs/ 和 superpowers/plans/（当前设计文档）**

不做任何操作。`docs/superpowers/` 保留，这是当前的设计文档存放位置。

- [ ] **Step 4: 清理 docs/index.md**

由于 `docs/` 下的大部分内容已移走，`docs/index.md` 不再作为知识库索引。将其改为指向项目设计文档的简单索引：

写入 `docs/index.md`：

```markdown
# Marginalia 项目文档

## 设计文档

- [仓库精简设计](superpowers/specs/2026-05-14-repo-slimming-design.md)
- [仓库精简实施计划](superpowers/plans/2026-05-14-repo-slimming-implementation.md)
```

- [ ] **Step 5: 验证 docs/ 只剩必要文件**

```bash
find docs/ -type f | sort
```

Expected: 只有 docs/index.md 和 docs/superpowers/ 下的文件

---

### Task 7: 放置标准开源文件

**Files:**
- Create: `LICENSE`（从 GPT54 复制）
- Create: `CONTRIBUTING.md`（基于 GPT54 改造）

- [ ] **Step 1: 复制 LICENSE**

```bash
cp archive/GPT54/LICENSE LICENSE
```

- [ ] **Step 2: 创建 CONTRIBUTING.md**

基于 GPT54 的 CONTRIBUTING.md 改造为 Marginalia 版本。写入 `CONTRIBUTING.md`：

```markdown
# Contributing

## How to Propose Changes

1. Fork 本仓库
2. 在 Fork 中修改
3. 提交 Pull Request

## What We Accept

- 对协议（schema/）的改进
- 对脚本（scripts/）的改进
- 对模板（templates/）的改进
- 对示例（example/）的改进
- Bug 修复

## Validation

```bash
python3 scripts/audit.py --root example/
python3 scripts/verify.py --root example/
```

## Hard Rules

- 不引入第三方依赖
- 不把项目实现成 Web App 或数据库产品
- 示例知识库保持精简，不超过 5 个页面
```

- [ ] **Step 3: 验证标准文件存在**

```bash
ls LICENSE CONTRIBUTING.md
```

Expected: 两个文件都存在

---

### Task 8: 重写 CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: 重写 CLAUDE.md**

写入 `CLAUDE.md`：

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

- [ ] **Step 2: 验证行数**

```bash
wc -l CLAUDE.md
```

Expected: 约 20-30 行

---

### Task 9: 重写 README.md

**Files:**
- Modify: `README.md`

- [ ] **Step 1: 重写 README.md**

写入 `README.md`：

```markdown
# Marginalia 边注系统

> 文档级批注记忆系统——让记忆附着在知识点旁边，实现同位、无损、解耦。

## 这是什么？

Marginalia 是一个 AI 助手驱动的知识管理系统。它不是数据库，不是 RAG 引擎，不是在线服务。它是：

- 一套 AI 助手能理解的协议规则（`schema/`）
- 一组可运行的工具脚本（`scripts/`）
- 一个示例知识库（`example/`）
- 一套页面模板（`templates/`）

## 使用场景

```
你的项目（如 ~/projects/my-project）
    │
    ▼ 你对 AI 说：
    "参照 ~/download/marginalia，在我的项目里搭建知识库"
    │
    ▼ AI 自动完成：
    1. 创建 wiki/ 知识库骨架
    2. 扫描你的项目文档
    3. 提案分类，你确认后摄入
    4. 之后每次对话自动读取和更新知识库
```

## 快速开始

### 前提

- 一个 AI 编程助手（Claude Code、Cursor、Cline 等）
- 一个你想管理知识的项目

### 步骤

```bash
# 1. Clone 本仓库
git clone https://github.com/xxx/Marginalia.git ~/download/marginalia

# 2. 在你的项目中，对 AI 说：
#    "参照 ~/download/marginalia，在我的项目里搭建知识库，并摄入文档"

# 3. AI 会自动完成一切
```

### 可选：手动初始化

```bash
python3 ~/download/marginalia/scripts/init.py --root ./my-project
python3 ~/download/marginalia/scripts/audit.py --root ./my-project/wiki
python3 ~/download/marginalia/scripts/verify.py --root ./my-project/wiki
```

## 核心概念

| 特征 | 说明 |
|------|------|
| **同位** | 记忆与知识点同位置——读知识点，即读记忆 |
| **无损** | 原始论据完整保留——不经过 Embedding 压缩 |
| **解耦** | 纯 Markdown 文件——独立于任何平台 |

## 目录结构

```
Marginalia/
├── CLAUDE.md              # AI 助手发现层入口
├── schema/                # 协议规则
│   ├── rules.md           #   AI 行为规则
│   ├── node-types.md      #   页面类型定义
│   └── first-ingest.md    #   首次摄入指南
├── scripts/               # 工具脚本（零依赖 Python）
│   ├── init.py            #   创建知识库骨架
│   ├── audit.py           #   检查知识库健康
│   └── verify.py          #   验证知识库完整性
├── templates/             # 页面模板
└── example/               # 示例知识库
```

## 三阶段工作流

### 阶段 1：初始化

AI 在你的项目中创建 `wiki/` 目录和索引文件。

### 阶段 2：首次摄入

AI 扫描你的项目文档，半自动分类为概念、决策、批注或对比，确认后写入知识库。

### 阶段 3：日常使用

每次对话，AI 自动读取知识库、写入新知识、运行审计检查。

## 许可证

MIT
```

- [ ] **Step 2: 验证 README 可读**

```bash
head -5 README.md
```

Expected: 显示标题和描述

---

### Task 10: 清理残留文件

**Files:**
- Delete: `.pytest_cache/`
- Delete: `GPT54/`（已在 Task 2 移到 archive/，此步验证）

- [ ] **Step 1: 删除 .pytest_cache/**

```bash
rm -rf .pytest_cache
```

- [ ] **Step 2: 验证根目录干净**

```bash
ls -la | grep -v "^total" | grep -v "^\."
```

Expected: 只显示 CLAUDE.md、README.md、LICENSE、CONTRIBUTING.md、.gitignore、schema/、scripts/、templates/、example/、archive/、docs/

---

### Task 11: 最终验证

- [ ] **Step 1: 验证目标目录结构**

```bash
find . -maxdepth 3 -not -path "./archive/*" -not -path "./.git/*" -not -path "./docs/superpowers/*" -not -name ".DS_Store" | sort
```

Expected: 与设计文档中的目标目录结构一致

- [ ] **Step 2: 验证脚本可运行**

```bash
python3 scripts/init.py --root /tmp/test-marginalia-final
python3 scripts/verify.py --root /tmp/test-marginalia-final/wiki
python3 scripts/audit.py --root /tmp/test-marginalia-final/wiki
rm -rf /tmp/test-marginalia-final
```

Expected: 全部通过，无 P0 问题

- [ ] **Step 3: 验证 example/ 知识库**

```bash
python3 scripts/verify.py --root example/
python3 scripts/audit.py --root example/
```

Expected: verify 通过，audit 无 P0 问题（可能有 P2 孤儿页，这是可接受的）

- [ ] **Step 4: 验证根目录干净**

```bash
ls *.md *.k26 2>/dev/null
```

Expected: 只显示 CLAUDE.md、README.md、CONTRIBUTING.md，不再有散落的设计文档

---

## 自检

**Spec 覆盖检查：**

| Spec 要求 | 对应 Task |
|-----------|----------|
| 目标目录结构 | Task 1-10 |
| 阶段 1：初始化 | Task 4 (init.py) |
| 阶段 2：首次摄入 | Task 3 (first-ingest.md) |
| 阶段 3：日常规则 | Task 4 (init.py 中的 CLAUDE.md snippet) |
| 文件变动清单（归档） | Task 1, 2 |
| 文件变动清单（吸收） | Task 3, 4, 7 |
| 文件变动清单（移动） | Task 5 |
| 文件变动清单（删除） | Task 6, 10 |
| CLAUDE.md 精简为发现层 | Task 8 |
| README.md 重写 | Task 9 |
| audit 嵌入收工流程 | Task 4 (init.py snippet) |
| 追加前检查冲突 | Task 4 (init.py append_claude_md) |
| 成功标准 5 项 | Task 11 |

**Placeholder 扫描：** 无 TBD/TODO/占位符

**类型一致性：** 所有脚本使用 pathlib.Path，函数签名一致
