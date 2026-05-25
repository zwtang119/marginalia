# Marginalia 边注系统 — 离线自举文档

> 协议版本：v0.3.1
> 本文档是 Marginalia 的唯一自举入口。AI 无需访问 GitHub，仅凭本文档即可在任意项目中建立完整知识库。

---

## 0. 自举说明

本文档包含 Marginalia 系统的全部规范、脚本源码和模板。AI 读取本文档后，应按第七节的步骤在用户项目中完成部署。

**前提**：一个能执行 Python 脚本的 AI 编程助手 + 一个你想管理知识的项目。

---

## 1. 概念与三原则

Marginalia 是 AI 助手驱动的文档级批注记忆系统。它不是数据库、不是 RAG 引擎、不是在线服务。它是：

- 一套规则（AI 行为协议）
- 一组零依赖 Python 脚本
- 四类 Markdown 页面模板
- 一个纯文件系统的知识库目录

### 三原则

| 原则 | 含义 |
|------|------|
| **同位** | 记忆与知识点同位置——读知识点，即读记忆 |
| **无损** | 原始论据完整保留——不经过 Embedding 压缩 |
| **解耦** | 纯 Markdown 文件——独立于任何平台 |

### 批注格式

```
> [!memo] YYYY-MM-DD 内容
```

---

## 2. 知识库目录结构

```
项目根/
├── CLAUDE.md              ← AI 发现层入口（init.py 自动生成引用段）
└── wiki/                  ← 知识库根目录
    ├── index.md           ← 知识库索引（AI 每次对话首先读取）
    ├── concepts/          ← 概念定义（concept 类型页面）
    ├── decisions/         ← 决策记录（decision 类型页面）
    ├── annotations/       ← 批注集合（annotation 类型页面）
    └── comparisons/       ← 多方案对比（comparison 类型页面）
```

---

## 3. 工具脚本

三个零依赖 Python 脚本，需写在项目根目录的 `scripts/` 下。

### 3.1 init.py — 创建知识库骨架

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

### 3.2 audit.py — 检查知识库健康

```python
#!/usr/bin/env python3
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

SKIP_DIRS_DEFAULT = {"templates", "archive"}
PLACEHOLDER_PATTERNS = [
    re.compile(r"^\[\[wikilink\]\]$", re.IGNORECASE),
    re.compile(r"^\[\[concepts?/[^\]]+\]\]$", re.IGNORECASE),
    re.compile(r"^\[\[decisions?/[^\]]+\]\]$", re.IGNORECASE),
    re.compile(r"^\[\[entities?/[^\]]+\]\]$", re.IGNORECASE),
]


def find_wikilinks(text: str) -> list[str]:
    raw = re.findall(r"\[\[([^\]]+)\]\]", text)
    result = []
    for link in raw:
        target = link.split("|")[0].split("#")[0].strip()
        if target:
            result.append(target)
    return result


def is_placeholder(link: str) -> bool:
    bracketed = f"[[{link}]]"
    return any(p.match(bracketed) for p in PLACEHOLDER_PATTERNS)


def should_skip_file(rel_path: Path, skip_dirs: set[str]) -> bool:
    parts = rel_path.parts
    for d in skip_dirs:
        if d in parts:
            return True
    for part in parts:
        if "archive" in part.lower() and part != part.lower():
            pass
        if "-archive" in part.lower():
            return True
    return False


def find_all_md_files(root: Path, skip_dirs: set[str] | None = None) -> list[Path]:
    skip = skip_dirs or set()
    return sorted(
        p for p in root.rglob("*.md")
        if p.is_file() and not should_skip_file(p.relative_to(root), skip)
    )


def resolve_wikilink(root: Path, link: str, external_kb_dirs: list[str] | None = None) -> bool:
    link = link.strip()
    candidates = [
        root / f"{link}.md",
        root / link,
        root.parent / f"{link}.md",
        root.parent / link,
    ]
    if external_kb_dirs:
        for kb_dir in external_kb_dirs:
            kb_path = Path(kb_dir)
            if not kb_path.is_absolute():
                kb_path = root.parent / kb_dir
            candidates.extend([
                kb_path / f"{link}.md",
                kb_path / link,
            ])
    return any(c.exists() for c in candidates)


def check_broken_links(
    root: Path,
    skip_dirs: set[str] | None = None,
    external_kb_dirs: list[str] | None = None,
) -> list[dict]:
    issues = []
    for md_file in find_all_md_files(root, skip_dirs):
        text = md_file.read_text(encoding="utf-8")
        for link in find_wikilinks(text):
            if is_placeholder(link):
                continue
            if not resolve_wikilink(root, link, external_kb_dirs):
                rel = md_file.relative_to(root)
                issues.append({
                    "id": f"BROKEN-{len(issues) + 1:04d}",
                    "severity": "P1",
                    "type": "broken_wikilink",
                    "path": str(rel),
                    "message": f"断链：[[{link}]]（在 {rel} 中）",
                    "suggested_action": f"创建 {link}.md 或修正链接",
                })
    return issues


def check_orphan_pages(root: Path, skip_dirs: set[str] | None = None) -> list[dict]:
    all_pages = set()
    all_links = set()
    for md_file in find_all_md_files(root, skip_dirs):
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


def audit(
    root: Path,
    skip_dirs: set[str] | None = None,
    external_kb_dirs: list[str] | None = None,
) -> dict:
    skip = skip_dirs if skip_dirs is not None else SKIP_DIRS_DEFAULT
    issues = []
    issues.extend(check_index_exists(root))
    issues.extend(check_broken_links(root, skip, external_kb_dirs))
    issues.extend(check_orphan_pages(root, skip))

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
    parser.add_argument("--skip-templates", action="store_true", default=True)
    parser.add_argument("--skip-archive", action="store_true", default=True)
    parser.add_argument("--no-skip", action="store_true")
    parser.add_argument("--external-kb-dirs", default="")
    parser.add_argument("--brief", action="store_true")
    parser.add_argument("--exit-code-only", action="store_true")
    args = parser.parse_args()
    root = Path(args.root).resolve()

    if not root.exists():
        if not args.exit_code_only:
            print(f"目录不存在：{root}")
        return 2

    skip_dirs = set()
    if not args.no_skip:
        if args.skip_templates:
            skip_dirs.add("templates")
        if args.skip_archive:
            skip_dirs.add("archive")

    external_kb_dirs = [d.strip() for d in args.external_kb_dirs.split(",") if d.strip()] if args.external_kb_dirs else None

    report = audit(root, skip_dirs or None, external_kb_dirs or None)

    if not args.exit_code_only:
        if args.brief:
            d = report["severity_distribution"]
            print(f"P0:{d['P0']} P1:{d['P1']} P2:{d['P2']}")
        else:
            print(json.dumps(report, ensure_ascii=False, indent=2))

    if report["severity_distribution"].get("P0", 0) > 0:
        return 2
    if report["severity_distribution"].get("P1", 0) > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### 3.3 verify.py — 验证知识库完整性

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

---

## 4. 协议规则

### 4.1 读取规则

1. 每次对话开始，先读 `wiki/index.md` 了解知识库全貌
2. 遇到相关知识话题，沿 `[[wikilink]]` 读取相关页面
3. 读取页面时连同页内批注一起读取
4. 如在读取中发现断链、孤儿页或其他异常，提醒用户："发现知识库问题，建议运行 audit.py 检查"

### 4.2 写入规则

1. 对话中产生新概念/机制 → 在 `wiki/concepts/` 创建页面
2. 做了技术决策 → 在 `wiki/decisions/` 记录
3. 发现与已有知识的关系 → 用 `[[wikilink]]` 链接
4. 不确定信息写到哪里 → 参见第五节中的"写回位置"表和"信息分类决策"流程

### 4.3 收工规则

1. 更新 `wiki/index.md`（如有新页面）
2. 在相关页面添加批注：`> [!memo] YYYY-MM-DD 内容`

### 4.4 约束

- 不得引入第三方依赖
- 不得把知识库实现成在线服务或数据库产品
- 批注必须包含日期

---

## 5. 节点类型系统

### 5.1 concept（概念）

定义概念、机制或术语。回答"这是什么"。

最小字段：
- 标题
- 一句话定义
- 详细说明
- 相关链接（`[[wikilink]]`）

### 5.2 decision（决策）

记录技术选型或方案决策。回答"为什么选这个"。

最小字段：
- 标题
- 背景
- 候选方案
- 最终决策及理由
- 相关链接

### 5.3 annotation（批注）

时间敏感的补充信息或历史记录。回答"当时发生了什么"。

页内批注格式：
```markdown
> [!memo] YYYY-MM-DD 内容
>
> 来源：谁说的/什么文档
> 上下文：当时的背景
```

批注有两种形态：
- **页内批注**：写在已有页面的正文旁边，用 `> [!memo]` 格式
- **独立批注页**：在 `annotations/` 目录下创建完整页面，用于跨轮次的模式沉淀

### 5.4 comparison（对比）

多方案对比分析。

最小字段：
- 标题
- 对比维度
- 各方案分析
- 结论
- 相关链接

### 5.5 写回位置

| 信息类型 | 写回位置 |
|----------|----------|
| 概念定义、机制、术语 | `concepts/` |
| 技术选型、方案决策 | `decisions/` |
| 实体、系统、对象 | `entities/`（可选） |
| 多方案对比 | `comparisons/`（可选） |
| 时间敏感记录 | 页内批注（`> [!memo]`） |

写回要求：优先更新已有页面；必要时再新增；新增页面后更新 `index.md`。

### 5.6 信息分类决策

```
新信息到来
    │
    ▼
项目状态变化？ ──YES──> 更新 index.md
    │
    NO
    ▼
稳定客观事实？ ──YES──> 改正文
    │
    NO
    ▼
可独立复用知识单元？ ──YES──> 新增或更新结构化页面
    │
    NO
    ▼
时间敏感或主观上下文？ ──YES──> 添加批注
    │
    NO
    ▼
不确定时：先说明不确定性，再选择"更新页面"或"批注"
```

---

## 6. 页面模板

以下模板是 AI 创建页面时的参考骨架。具体内容按实际情况填充。

### 6.1 概念页模板

```markdown
# 概念名称

> 一句话定义这个概念。

## 详细说明

- 这是什么？
- 解决什么问题？
- 核心思想是什么？

## 核心特征

### 特征 1

简要说明。

> [!memo] YYYY-MM-DD 批注
> 记录关于这个特征的历史记忆、讨论、反思。

### 特征 2

简要说明。

## 工作机制

用文字描述工作流程。

## 相关页面

- [[concepts/xxx]]: 相关概念
- [[decisions/xxx]]: 相关决策
```

### 6.2 决策记录模板

```markdown
# 决策标题

## 背景

描述决策的背景和上下文。

候选方案：
1. **方案 A**：描述
2. **方案 B**：描述

## 决策结果

**最终决策**：选择的方案及理由。

## 实施计划

1. 步骤 1
2. 步骤 2

## 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 风险 1 | 高/中/低 | 措施 |

## 相关页面

- [[concepts/xxx]]: 相关概念
- [[decisions/xxx]]: 相关决策
```

### 6.3 批注页模板

```markdown
# 批注标题

## 背景

描述这批批注的来源和上下文。

## 问题/发现

**发现时间**：YYYY-MM-DD

**原始描述**：
> "原始描述或引用"

**批注沉淀**：

> [!memo] YYYY-MM-DD 批注
> 记录教训、反思、后续行动。

## 相关页面

- [[concepts/xxx]]: 相关概念
- [[decisions/xxx]]: 相关决策
```

---

## 7. 部署自举流程

AI 读取本文档后，在用户项目中按以下步骤操作：

### 步骤 1：创建 scripts/ 目录和三个脚本

在项目根目录创建 `scripts/` 目录，将第三节中的三个 Python 脚本完整写入：

```
项目根/
└── scripts/
    ├── init.py     ← 第三节 3.1 的完整代码
    ├── audit.py    ← 第三节 3.2 的完整代码
    └── verify.py   ← 第三节 3.3 的完整代码
```

### 步骤 2：运行 init.py 创建知识库骨架

```bash
python3 scripts/init.py --root .
```

这会在项目根目录下创建 `wiki/` 目录结构，并在 `CLAUDE.md` 中追加 Marginalia 引用段。

### 步骤 3：运行 verify.py 确认骨架完整

```bash
python3 scripts/verify.py --root wiki/
```

预期输出：`Verification passed`

### 步骤 4：首次知识摄入

1. 扫描项目目录，识别可摄入文档（`*.md`, `*.txt`, `*.rst`；跳过 `node_modules/`, `.git/`, `build/`, `dist/`, `vendor/`）
2. 按第 5.6 节的分类决策树对每个文档分类（concept / decision / annotation / comparison）
3. 列出文档清单和建议分类，等用户确认
4. 按第六节的模板将内容写入 `wiki/` 相应目录
5. 更新 `wiki/index.md`，添加新页面的索引条目
6. 运行 `python3 scripts/audit.py --root wiki/ --brief`，确认无 P0/P1 问题

### 步骤 5：完成

提示用户：知识库已就绪。之后的每次对话中，AI 将自动按第 4 节的规则读取和写入知识库。

---

## 8. 日常使用工作流

### AI 会话启动时

1. 读取 `wiki/index.md` 了解知识库全貌
2. 根据对话话题，沿 `[[wikilink]]` 读取相关页面

### 会话过程中

- 新概念 → 写入 `concepts/`
- 技术决策 → 写入 `decisions/`
- 多方案对比 → 写入 `comparisons/`
- 时间敏感信息 → 添加页内批注 `> [!memo]`
- 发现链接关系 → 添加 `[[wikilink]]`

### 会话结束时

- 更新 `wiki/index.md`（如有新页面）
- 添加批注记录本次会话的关键洞察

### 审计

- 手动：`python3 scripts/audit.py --root wiki/` 获取完整报告
- 快速扫描：`python3 scripts/audit.py --root wiki/ --brief`
- CI/CD：`python3 scripts/audit.py --root wiki/ --exit-code-only`

---

## 9. 平台集成与部署注意事项

### audit.py 运行方式

```bash
# 手动交互：完整 JSON 报告
python3 scripts/audit.py --root wiki/

# 快速扫描：单行摘要 P0:X P1:X P2:X
python3 scripts/audit.py --root wiki/ --brief

# CI/CD：仅退出码，无输出（P0>0→2, P1>0→1, 0→0）
python3 scripts/audit.py --root wiki/ --exit-code-only
```

### 跨工作区部署

当 AI 工作区与脚本所在目录不在同一路径时，可将第 4 节的协议规则改编为 AI 配置文件的"内联段"。内联段应标注协议版本：

> 协议版本：Marginalia v0.3.1

### 版本标签

在 `wiki/index.md` 中推荐添加版本标签：

> 知识库 → `wiki/`（Marginalia v0.3.1）

### 部署后检查

> ⚠️ 部署 Marginalia 后，检查 AI 配置文件中是否存在来自平台默认模板的旧自动化段（如心跳、定期检查）。这些旧段可能与 Marginalia 的维护架构冲突。解决方法：删除或缩减旧段。

---

## 10. 约束

- 不得引入第三方依赖
- 不得把知识库实现成在线服务或数据库产品
- 批注必须包含日期
- 优先更新已有页面，必要时才新增
- 新增页面后必须更新 `wiki/index.md`