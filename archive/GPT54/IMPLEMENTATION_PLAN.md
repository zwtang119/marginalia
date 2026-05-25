# GPT54 M0-M1.5 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建 `GPT54` 的 `M0 协议骨架`、`M1 最小闭环` 与 `M1.5 协议发现和首次摄入入口`，使项目既能形成零依赖闭环，又能让普通用户和 AI 助手顺利进入协议。

**Architecture:** 实现以文件系统为中心，使用 Markdown 保存长期状态，使用 Python 标准库脚本提供 `init`、`audit`、`verify` 三个最小执行器。系统通过 `CLAUDE.md` 作为发现层入口，通过 `schema/` 定义约束与摄入工作流，通过 `project/` 记录状态，通过 `audit/` 保存观测结果，通过 `runtime/` 保存任务态记录。

**Tech Stack:** Markdown, Python 3 标准库, POSIX Shell, `unittest`

---

## 文件结构锁定

### 新增文件

- `GPT54/CLAUDE.md`
- `GPT54/LICENSE`
- `GPT54/CONTRIBUTING.md`
- `GPT54/CODE_OF_CONDUCT.md`
- `GPT54/CHANGELOG.md`
- `GPT54/docs/index.md`
- `GPT54/project/project.md`
- `GPT54/project/plan.md`
- `GPT54/project/progress.md`
- `GPT54/project/open-questions.md`
- `GPT54/schema/rules.md`
- `GPT54/schema/node-types.md`
- `GPT54/schema/task-states.md`
- `GPT54/schema/ingest.md`
- `GPT54/runtime/tasks/.gitkeep`
- `GPT54/runtime/logs/.gitkeep`
- `GPT54/audit/baselines/.gitkeep`
- `GPT54/audit/reports/.gitkeep`
- `GPT54/audit/snapshots/.gitkeep`
- `GPT54/scripts/init.py`
- `GPT54/scripts/audit.py`
- `GPT54/scripts/verify.py`
- `GPT54/tests/fixtures/minimal_expected_tree.txt`
- `GPT54/tests/test_init.py`
- `GPT54/tests/test_audit.py`
- `GPT54/tests/test_verify.py`
- `GPT54/tests/test_protocol_discovery.py`
- `GPT54/tests/smoke/test_cli_smoke.sh`

### 修改文件

- `GPT54/README.md`
- `GPT54/PRD.md`
- `GPT54/SPEC.md`
- `GPT54/IMPLEMENTATION_PLAN.md`

### 设计约束

- `README.md` 负责入口说明，不重复 `PRD/SPEC` 的全部内容。
- `project/` 只保存项目状态，不保存知识节点。
- `schema/` 只保存规则，不放任务进展。
- `scripts/` 只提供最小闭环脚本，不增加额外框架。
- `tests/` 使用 `unittest` 和 shell 冒烟，不引入 `pytest` 或第三方框架。
- 不在当前阶段把 `docs/nodes` 主骨架重写成 `wiki/source` 结构。

### 实施顺序

1. 先补齐仓库骨架和根文档
2. 再写项目状态与规则文件
3. 再用 TDD 实现 `init.py`
4. 再用 TDD 实现 `audit.py`
5. 再用 TDD 实现 `verify.py`
6. 补齐冒烟测试与阶段回写
7. 再进入 `M1.5`：发现层入口和首次摄入入口

### Task 1: 建立 M0 仓库骨架与开源外壳

**Files:**
- Create: `GPT54/CLAUDE.md`
- Modify: `GPT54/README.md`
- Create: `GPT54/LICENSE`
- Create: `GPT54/CONTRIBUTING.md`
- Create: `GPT54/CODE_OF_CONDUCT.md`
- Create: `GPT54/CHANGELOG.md`
- Create: `GPT54/docs/index.md`
- Create: `GPT54/runtime/tasks/.gitkeep`
- Create: `GPT54/runtime/logs/.gitkeep`
- Create: `GPT54/audit/baselines/.gitkeep`
- Create: `GPT54/audit/reports/.gitkeep`
- Create: `GPT54/audit/snapshots/.gitkeep`

- [ ] **Step 1: 创建目录骨架**

```bash
mkdir -p GPT54/docs/nodes GPT54/project GPT54/schema GPT54/runtime/tasks GPT54/runtime/logs GPT54/audit/baselines GPT54/audit/reports GPT54/audit/snapshots GPT54/scripts GPT54/tests/fixtures GPT54/tests/smoke
touch GPT54/runtime/tasks/.gitkeep GPT54/runtime/logs/.gitkeep GPT54/audit/baselines/.gitkeep GPT54/audit/reports/.gitkeep GPT54/audit/snapshots/.gitkeep
```

- [ ] **Step 2: 写入 `README.md`**

写入当前仓库中已有的 `README.md` 内容，并补充 SPEC §18.1 要求但当前缺失的两个章节：

1. **目录说明**（在"关键文件"章节之后）：

```markdown
## 目录说明

- `docs/`：知识节点与导航
- `project/`：项目目标、计划、进展与开放问题
- `schema/`：规则、节点类型、状态机与摄入工作流
- `audit/`：审计基线、报告与快照
- `runtime/`：任务态记录与执行日志
- `scripts/`：零依赖脚本（init、audit、verify）
- `tests/`：单元测试与冒烟测试
```

2. **常用命令**（在"快速开始"章节之后）：

```markdown
## 常用命令

```bash
python3 scripts/init.py --root ./my-kb
python3 scripts/audit.py --root ./my-kb
python3 scripts/verify.py --root ./my-kb
python3 -m unittest discover -s tests
```

M1.5 后额外支持：

```bash
python3 scripts/init.py --root ./my-kb --update-protocol
python3 scripts/init.py --root ./my-kb --platform cursor
```
```

其余章节（快速判断、两条路径、快速开始、核心工作流、关键文件、AI 助手如何进入协议、这是什么/这不是什么、当前状态、贡献和许可证）保持当前 README.md 的内容不变。

- [ ] **Step 2a: 写入 `CLAUDE.md`**

```markdown
# GPT54 Protocol Discovery

<!-- GPT54-PROTOCOL-START -->
本仓库遵循 GPT54 协议。

AI 助手应按以下顺序读取规则文件：

1. `schema/rules.md` — 执行规则
2. `schema/node-types.md` — 节点类型定义
3. `schema/task-states.md` — 任务状态机
4. `schema/ingest.md` — 首次摄入工作流

当前协议版本：v0.1.0
<!-- GPT54-PROTOCOL-END -->
```

- [ ] **Step 3: 写入开源外壳文件**

```text
MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

```markdown
# Contributing

## Scope

只接受符合 `PRD.md` 与 `SPEC.md` 的变更。

## How to Propose Changes

1. 先读 `PRD.md` 与 `SPEC.md`，确认变更在项目范围内
2. 在 `project/open-questions.md` 中记录变更意图
3. 等待维护者确认后再动手

## Workflow

1. 先读 `PRD.md` 与 `SPEC.md`
2. 再读 `project/` 下状态文件
3. 明确目标与成功标准
4. 执行最小必要修改
5. 运行验证
6. 回写状态文件

## Validation

```bash
python3 scripts/audit.py --root .
python3 scripts/verify.py --root .
python3 -m unittest discover -s tests
```

## How to Submit Documentation Changes

文档修改与代码修改遵循相同流程：先确认范围，再执行最小修改，最后验证和回写。

## Changes That Require Prior Discussion

以下改动必须先在 `project/open-questions.md` 中讨论并获得维护者确认：

- 大规模目录重组
- 覆盖已有结论
- 删除大量文件
- 多种解释会显著改变系统边界

## Hard Rules

- 不引入第三方依赖
- 不把项目实现成 Web App 或数据库产品
- 不跳过验证与回写
```

```markdown
# Code of Conduct

## Our Standard

我们要求所有贡献者保持尊重、清晰和可审计的协作方式。

## Unacceptable Behavior

- 人身攻击
- 歧视或骚扰
- 蓄意破坏项目状态与文档

## Escalation Path

1. 发现问题后，先在 `project/open-questions.md` 中记录
2. 维护者在 7 天内响应并判定严重程度
3. 严重违规由维护者直接拒绝相关贡献
4. 争议无法解决时，由项目创建者最终裁定

## Enforcement

维护者有权拒绝不符合项目规则的贡献。
```

```markdown
# Changelog

## 2026-05-13

- Added: 初版 `PRD.md`
- Added: 初版 `SPEC.md`
- Added: 初版 `IMPLEMENTATION_PLAN.md`
```

```markdown
# 知识索引

当前版本只保留最小入口。

- 后续节点应放在 `docs/nodes/`
- 项目状态不放入 `docs/`
```

- [ ] **Step 4: 运行结构检查**

Run: `find GPT54 -maxdepth 2 | sort`

Expected: 输出中包含 `README.md`、`LICENSE`、`CONTRIBUTING.md`、`CODE_OF_CONDUCT.md`、`CHANGELOG.md`、`docs/index.md`、`runtime/`、`audit/`

- [ ] **Step 5: Commit**

```bash
git add GPT54/README.md GPT54/CLAUDE.md GPT54/LICENSE GPT54/CONTRIBUTING.md GPT54/CODE_OF_CONDUCT.md GPT54/CHANGELOG.md GPT54/docs/index.md GPT54/runtime GPT54/audit
git commit -m "feat: add GPT54 M0 repository skeleton"
```

### Task 2: 建立项目状态文件与规则文件

**Files:**
- Create: `GPT54/project/project.md`
- Create: `GPT54/project/plan.md`
- Create: `GPT54/project/progress.md`
- Create: `GPT54/project/open-questions.md`
- Create: `GPT54/schema/rules.md`
- Create: `GPT54/schema/node-types.md`
- Create: `GPT54/schema/task-states.md`

- [ ] **Step 1: 写入 `project/project.md`**

```markdown
# Project

- 项目名称：GPT54
- 一句话目标：构建零依赖、文件系统优先、可被 AI 助手执行的知识工程协议系统
- 当前范围：M0 协议骨架与 M1 最小闭环
- 非目标：Web 服务、数据库、插件平台、在线协作
- 已知约束：原创、零依赖、离线优先、纯文本优先
- 规则版本：v0.1.0
```

- [ ] **Step 2: 写入 `project/plan.md` 与 `project/progress.md`**

```markdown
# Plan

- 当前目标：完成 M0 与 M1 最小闭环
- 成功标准：可初始化、可审计、可验证、可回写
- 当前阶段：M0
- 步骤列表：
  - 建立骨架
  - 建立状态文件
  - 实现 init.py
  - 实现 audit.py
  - 实现 verify.py
- 当前执行中的一步：建立状态文件
- 后续候选步骤：
  - 增加任务模板
  - 加入快照对比
```

```markdown
# Progress

- 最新状态：M0 状态文件正在建立
- 已完成：
  - 已写出 `PRD.md`
  - 已写出 `SPEC.md`
  - 已写出 `IMPLEMENTATION_PLAN.md`
- 当前阻塞：无
- 下一步：实现 `init.py`
```

- [ ] **Step 3: 写入 `project/open-questions.md` 与 `schema/` 规则文件**

```markdown
# Open Questions

- 问题：节点关系是否需要单独关系文件
  - 为什么重要：影响后续关系建模复杂度
  - 需谁确认：维护者
  - 状态：open
```

```markdown
# Rules

- 规则版本：v0.1.0

1. 先读 `PRD.md` 与 `SPEC.md`
2. 再读 `project/` 状态文件
3. 再执行最小必要修改
4. 修改后必须验证
5. 验证后必须回写状态
6. 不得引入第三方依赖
7. 不得把项目实现成在线服务或数据库产品
```

```markdown
# Node Types

- concept：概念节点
- decision：决策节点
- task：任务节点
- note：补充说明节点
```

```markdown
# Task States

- draft
- ready
- in_progress
- blocked
- verify_pending
- done
- archived
```

- [ ] **Step 4: 人工核对最小字段是否齐全**

Run: `sed -n '1,120p' GPT54/project/project.md GPT54/project/plan.md GPT54/project/progress.md GPT54/project/open-questions.md GPT54/schema/rules.md`

Expected: 每个文件都包含 `SPEC.md` 对应的最小字段或等价表达

- [ ] **Step 5: Commit**

```bash
git add GPT54/project GPT54/schema
git commit -m "feat: add GPT54 project and schema state files"
```

### Task 3: 用 TDD 实现 `scripts/init.py`

**Files:**
- Create: `GPT54/scripts/init.py`
- Create: `GPT54/tests/test_init.py`
- Test: `GPT54/tests/test_init.py`

- [ ] **Step 1: 写失败测试**

```python
import pathlib
import subprocess
import tempfile
import unittest


class InitScriptTest(unittest.TestCase):
    def test_init_creates_expected_structure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp) / "sandbox"
            completed = subprocess.run(
                ["python3", "scripts/init.py", "--root", str(root)],
                cwd="GPT54",
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertTrue((root / "docs" / "index.md").exists())
            self.assertTrue((root / "project" / "project.md").exists())
            self.assertTrue((root / "schema" / "rules.md").exists())
            self.assertIn("Initialized GPT54 skeleton", completed.stdout)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `cd GPT54 && python3 -m unittest tests/test_init.py -v`

Expected: FAIL，错误包含 `can't open file` 或 `No such file or directory: scripts/init.py`

- [ ] **Step 3: 写最小实现**

```python
#!/usr/bin/env python3
import argparse
from pathlib import Path


FILES = {
    "README.md": "# GPT54\n",
    "PRD.md": "# PRD\n",
    "SPEC.md": "# SPEC\n",
    "CLAUDE.md": (
        "# GPT54 Protocol Discovery\n"
        "\n"
        "<!-- GPT54-PROTOCOL-START -->\n"
        "本仓库遵循 GPT54 协议。\n"
        "\n"
        "AI 助手应按以下顺序读取规则文件：\n"
        "\n"
        "1. `schema/rules.md` — 执行规则\n"
        "2. `schema/node-types.md` — 节点类型定义\n"
        "3. `schema/task-states.md` — 任务状态机\n"
        "4. `schema/ingest.md` — 首次摄入工作流\n"
        "\n"
        "当前协议版本：v0.1.0\n"
        "<!-- GPT54-PROTOCOL-END -->\n"
    ),
    "docs/index.md": "# 知识索引\n",
    "project/project.md": "# Project\n",
    "project/plan.md": "# Plan\n",
    "project/progress.md": "# Progress\n",
    "project/open-questions.md": "# Open Questions\n",
    "schema/rules.md": "# Rules\n\n- 规则版本：v0.1.0\n",
    "schema/node-types.md": "# Node Types\n",
    "schema/task-states.md": "# Task States\n",
    "schema/ingest.md": (
        "# Ingest Workflow\n"
        "\n"
        "## 触发条件\n"
        "\n"
        "用户或 AI 助手发出创建节点的请求。\n"
        "\n"
        "## 执行顺序\n"
        "\n"
        "1. 读取 `schema/node-types.md`\n"
        "2. 读取 `schema/rules.md`\n"
        "3. 在 `docs/nodes/` 下创建节点文件\n"
        "4. 更新 `docs/index.md`\n"
        "5. 创建任务记录\n"
        "6. 运行审计\n"
        "7. 运行验证\n"
        "8. 回写进展\n"
        "\n"
        "## 节点最小字段\n"
        "\n"
        "标题、节点类型、目的说明、主体内容、相关链接、更新时间\n"
        "\n"
        "## 禁止项\n"
        "\n"
        "- 禁止跳过索引更新\n"
        "- 禁止创建未定义的节点类型\n"
        "- 禁止跳过审计和验证\n"
    ),
}

DIRECTORIES = [
    "docs/nodes",
    "project",
    "schema",
    "audit/baselines",
    "audit/reports",
    "audit/snapshots",
    "runtime/tasks",
    "runtime/logs",
    "scripts",
    "tests/fixtures",
    "tests/smoke",
]


def initialize(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    for relative_dir in DIRECTORIES:
        (root / relative_dir).mkdir(parents=True, exist_ok=True)
    for relative_file, content in FILES.items():
        path = root / relative_file
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    args = parser.parse_args()
    root = Path(args.root).resolve()
    initialize(root)
    print(f"Initialized GPT54 skeleton at {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: 运行测试并确认通过**

Run: `cd GPT54 && python3 -m unittest tests/test_init.py -v`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add GPT54/scripts/init.py GPT54/tests/test_init.py
git commit -m "feat: add zero-dependency init script"
```

### Task 4: 用 TDD 实现 `scripts/audit.py`

**Files:**
- Create: `GPT54/scripts/audit.py`
- Create: `GPT54/tests/test_audit.py`
- Test: `GPT54/tests/test_audit.py`

- [ ] **Step 1: 写失败测试**

```python
import json
import pathlib
import subprocess
import tempfile
import unittest


class AuditScriptTest(unittest.TestCase):
    def test_audit_reports_missing_required_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp) / "repo"
            subprocess.run(
                ["python3", "scripts/init.py", "--root", str(root)],
                cwd="GPT54",
                check=True,
                capture_output=True,
                text=True,
            )
            (root / "project" / "plan.md").unlink()
            completed = subprocess.run(
                ["python3", "scripts/audit.py", "--root", str(root)],
                cwd="GPT54",
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(completed.returncode, 0)
            report_path = pathlib.Path(completed.stdout.strip().splitlines()[-1])
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(report["issues"][0]["type"], "missing_required_file")
            self.assertEqual(report["issues"][0]["severity"], "P0")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `cd GPT54 && python3 -m unittest tests/test_audit.py -v`

Expected: FAIL，错误包含 `scripts/audit.py` 不存在

- [ ] **Step 3: 写最小实现**

```python
#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


REQUIRED_FILES = [
    "PRD.md",
    "SPEC.md",
    "README.md",
    "CLAUDE.md",
    "project/project.md",
    "project/plan.md",
    "project/progress.md",
    "project/open-questions.md",
    "schema/rules.md",
    "schema/node-types.md",
    "schema/task-states.md",
    "schema/ingest.md",
    "docs/index.md",
]


def build_issue(issue_id: str, path: str) -> dict:
    return {
        "id": issue_id,
        "severity": "P0",
        "type": "missing_required_file",
        "path": path,
        "message": f"缺少必需文件：{path}",
        "expected": "文件存在",
        "actual": "文件不存在",
        "suggested_action": f"创建 {path}",
    }


def audit(root: Path, rules_version: str = "", audit_scope: str = "full") -> dict:
    issues = []
    for index, relative_path in enumerate(REQUIRED_FILES, start=1):
        if not (root / relative_path).exists():
            issues.append(build_issue(f"AUDIT-{index:04d}", relative_path))
    distribution = {"P0": 0, "P1": 0, "P2": 0, "P3": 0}
    for issue in issues:
        distribution[issue["severity"]] += 1
    return {
        "summary": f"发现 {len(issues)} 个问题",
        "issues": issues,
        "counts": {"total": len(issues)},
        "severity_distribution": distribution,
        "next_actions": ["先修复全部 P0 问题", "重新运行审计"] if issues else ["保持当前状态", "继续实现下一阶段"],
        "rules_version": rules_version,
        "audit_scope": audit_scope,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def write_report(root: Path, report: dict) -> Path:
    reports_dir = root / "audit" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S")
    report_path = reports_dir / f"audit-{stamp}.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--rules-version", default="")
    parser.add_argument("--audit-scope", default="full")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    report = audit(root, rules_version=args.rules_version, audit_scope=args.audit_scope)
    report_path = write_report(root, report)
    print(report_path)
    return 1 if report["severity_distribution"]["P0"] > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: 运行测试并确认通过**

Run: `cd GPT54 && python3 -m unittest tests/test_audit.py -v`

Expected: PASS

- [ ] **Step 5: 扩展测试覆盖合法仓库**

```python
def test_audit_passes_for_initialized_repository(self) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp) / "repo"
        subprocess.run(
            ["python3", "scripts/init.py", "--root", str(root)],
            cwd="GPT54",
            check=True,
            capture_output=True,
            text=True,
        )
        completed = subprocess.run(
            ["python3", "scripts/audit.py", "--root", str(root)],
            cwd="GPT54",
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
```

- [ ] **Step 6: Commit**

```bash
git add GPT54/scripts/audit.py GPT54/tests/test_audit.py
git commit -m "feat: add zero-dependency audit script"
```

### Task 5: 用 TDD 实现 `scripts/verify.py`

**Files:**
- Create: `GPT54/scripts/verify.py`
- Create: `GPT54/tests/test_verify.py`
- Test: `GPT54/tests/test_verify.py`

- [ ] **Step 1: 写失败测试**

```python
import pathlib
import subprocess
import tempfile
import unittest


class VerifyScriptTest(unittest.TestCase):
    def test_verify_fails_on_invalid_task_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp) / "repo"
            subprocess.run(
                ["python3", "scripts/init.py", "--root", str(root)],
                cwd="GPT54",
                check=True,
                capture_output=True,
                text=True,
            )
            task_file = root / "runtime" / "tasks" / "task-0001.md"
            task_file.write_text(
                "# Task\n\n- 任务编号：TASK-0001\n- 当前状态：running\n",
                encoding="utf-8",
            )
            completed = subprocess.run(
                ["python3", "scripts/verify.py", "--root", str(root)],
                cwd="GPT54",
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("Invalid task state", completed.stdout)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `cd GPT54 && python3 -m unittest tests/test_verify.py -v`

Expected: FAIL，错误包含 `scripts/verify.py` 不存在

- [ ] **Step 3: 写最小实现**

```python
#!/usr/bin/env python3
import argparse
from pathlib import Path


VALID_STATES = {
    "draft",
    "ready",
    "in_progress",
    "blocked",
    "verify_pending",
    "done",
    "archived",
}


def collect_task_files(root: Path) -> list[Path]:
    tasks_dir = root / "runtime" / "tasks"
    if not tasks_dir.exists():
        return []
    return sorted(path for path in tasks_dir.glob("*.md") if path.is_file())


def extract_state(task_file: Path) -> str | None:
    for line in task_file.read_text(encoding="utf-8").splitlines():
        if line.startswith("- 当前状态："):
            return line.split("：", 1)[1].strip()
    return None


def verify(root: Path) -> list[str]:
    problems = []
    for task_file in collect_task_files(root):
        state = extract_state(task_file)
        if state is None:
            problems.append(f"Missing task state: {task_file}")
        elif state not in VALID_STATES:
            problems.append(f"Invalid task state: {task_file} -> {state}")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    args = parser.parse_args()
    root = Path(args.root).resolve()
    problems = verify(root)
    if problems:
        for problem in problems:
            print(problem)
        return 1
    print("Verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: 运行测试并确认通过**

Run: `cd GPT54 && python3 -m unittest tests/test_verify.py -v`

Expected: PASS

- [ ] **Step 5: 增加通过路径测试**

```python
def test_verify_passes_on_valid_task_state(self) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp) / "repo"
        subprocess.run(
            ["python3", "scripts/init.py", "--root", str(root)],
            cwd="GPT54",
            check=True,
            capture_output=True,
            text=True,
        )
        task_file = root / "runtime" / "tasks" / "task-0001.md"
        task_file.write_text(
            "# Task\n\n- 任务编号：TASK-0001\n- 当前状态：ready\n",
            encoding="utf-8",
        )
        completed = subprocess.run(
            ["python3", "scripts/verify.py", "--root", str(root)],
            cwd="GPT54",
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Verification passed", completed.stdout)
```

- [ ] **Step 6: Commit**

```bash
git add GPT54/scripts/verify.py GPT54/tests/test_verify.py
git commit -m "feat: add zero-dependency verify script"
```

### Task 6: 补齐夹具、冒烟测试与阶段回写

**Files:**
- Create: `GPT54/tests/fixtures/minimal_expected_tree.txt`
- Create: `GPT54/tests/smoke/test_cli_smoke.sh`
- Modify: `GPT54/project/plan.md`
- Modify: `GPT54/project/progress.md`
- Modify: `GPT54/CHANGELOG.md`

- [ ] **Step 1: 写入目录夹具**

```text
README.md
PRD.md
SPEC.md
CLAUDE.md
docs/index.md
project/project.md
project/plan.md
project/progress.md
project/open-questions.md
schema/rules.md
schema/node-types.md
schema/task-states.md
schema/ingest.md
scripts/init.py
scripts/audit.py
scripts/verify.py
```

- [ ] **Step 2: 写冒烟测试**

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT

python3 "${ROOT_DIR}/scripts/init.py" --root "${TMP_DIR}/repo"
python3 "${ROOT_DIR}/scripts/audit.py" --root "${TMP_DIR}/repo"
python3 "${ROOT_DIR}/scripts/verify.py" --root "${TMP_DIR}/repo"

echo "smoke-pass"
```

- [ ] **Step 3: 运行测试矩阵**

Run: `cd GPT54 && chmod +x tests/smoke/test_cli_smoke.sh && python3 -m unittest discover -s tests -v && tests/smoke/test_cli_smoke.sh`

Expected: 单元测试全部 PASS，shell 输出 `smoke-pass`

- [ ] **Step 4: 回写阶段状态**

```markdown
# Plan

- 当前目标：完成 M1 最小闭环实现
- 成功标准：`init.py`、`audit.py`、`verify.py` 已跑通
- 当前阶段：M1
- 步骤列表：
  - 初始化脚本完成
  - 审计脚本完成
  - 验证脚本完成
  - 冒烟测试通过
- 当前执行中的一步：准备进入 M2 规划
- 后续候选步骤：
  - 增加节点摄入
  - 增加审计 Markdown 报告
  - 增加快照对比
```

```markdown
# Progress

- 最新状态：M1 最小闭环已完成
- 已完成：
  - `init.py` 可建立骨架
  - `audit.py` 可输出结构化审计结果
  - `verify.py` 可校验任务状态
  - 单元测试与冒烟测试通过
- 当前阻塞：无
- 下一步：设计 M2 稳定维护态
```

```markdown
# Changelog

## 2026-05-13

- Added: `scripts/init.py`
- Added: `scripts/audit.py`
- Added: `scripts/verify.py`
- Added: `tests/test_init.py`
- Added: `tests/test_audit.py`
- Added: `tests/test_verify.py`
- Added: `tests/smoke/test_cli_smoke.sh`
```

- [ ] **Step 5: Commit**

```bash
git add GPT54/tests/fixtures/minimal_expected_tree.txt GPT54/tests/smoke/test_cli_smoke.sh GPT54/project/plan.md GPT54/project/progress.md GPT54/CHANGELOG.md
git commit -m "test: add GPT54 smoke coverage and stage handoff"
```

### Task 7: M1.5 协议发现与首次摄入入口

**Files:**
- Create: `GPT54/schema/ingest.md`
- Modify: `GPT54/scripts/init.py`
- Modify: `GPT54/scripts/audit.py`
- Create: `GPT54/tests/test_protocol_discovery.py`
- Modify: `GPT54/tests/test_init.py`
- Modify: `GPT54/tests/test_audit.py`
- Modify: `GPT54/project/plan.md`
- Modify: `GPT54/project/progress.md`
- Modify: `GPT54/CHANGELOG.md`

- [ ] **Step 1: 写入 `schema/ingest.md`**

```markdown
# Ingest Workflow

## 触发条件

用户或 AI 助手发出创建节点的请求，包括但不限于：
- 自然语言请求（如"帮我创建一个关于 X 的 concept 节点"）
- AI 助手在执行任务过程中产生新知识需要沉淀

## 执行顺序

1. 读取 `schema/node-types.md`，确定节点类型
2. 读取 `schema/rules.md`，确认当前规则版本
3. 在 `docs/nodes/` 下创建节点文件，文件名使用小写英文加连字符
4. 节点必须包含最小字段：唯一标题、节点类型、目的说明、主体内容、相关链接、更新时间
5. 更新 `docs/index.md`，将新节点加入导航
6. 在 `runtime/tasks/` 下创建任务记录，状态设为 `in_progress`
7. 运行 `audit.py`，确认无 P0 问题
8. 将任务状态推进到 `verify_pending`
9. 运行 `verify.py`，确认通过
10. 将任务状态推进到 `done`，回写 `project/progress.md`

## 节点最小字段

| 字段     | 说明                 |
| -------- | -------------------- |
| 标题     | 唯一，与文件名对应   |
| 节点类型 | 必须在 node-types 中 |
| 目的说明 | 一句话说明为何存在   |
| 主体内容 | 节点的核心知识       |
| 相关链接 | 指向其他节点的链接   |
| 更新时间 | YYYY-MM-DD 格式      |

## 禁止项

- 禁止跳过索引更新直接创建节点
- 禁止创建不在 `node-types.md` 中的节点类型
- 禁止不创建任务记录就完成摄入
- 禁止跳过审计和验证就标记完成
- 禁止在 `docs/nodes/` 以外的目录存放知识节点
```

- [ ] **Step 2: 升级 `init.py`，增加 `--update-protocol` 和 `--platform` 参数**

`CLAUDE.md` 和 `schema/ingest.md` 已在 Task 3 的 FILES 字典中包含。本步只增加 `--update-protocol` 参数（更新 `CLAUDE.md` 标记段而不覆盖标记段外内容）和 `--platform` 参数（为指定平台生成发现层文件）。

```python
PROTOCOL_START = "<!-- GPT54-PROTOCOL-START -->"
PROTOCOL_END = "<!-- GPT54-PROTOCOL-END -->"
PROTOCOL_BODY = (
    "本仓库遵循 GPT54 协议。\n"
    "\n"
    "AI 助手应按以下顺序读取规则文件：\n"
    "\n"
    "1. `schema/rules.md` — 执行规则\n"
    "2. `schema/node-types.md` — 节点类型定义\n"
    "3. `schema/task-states.md` — 任务状态机\n"
    "4. `schema/ingest.md` — 首次摄入工作流\n"
    "\n"
    "当前协议版本：v0.1.0\n"
)


def update_protocol(claude_path: Path) -> None:
    if not claude_path.exists():
        claude_path.write_text(
            f"{PROTOCOL_START}\n{PROTOCOL_BODY}{PROTOCOL_END}\n",
            encoding="utf-8",
        )
        return
    text = claude_path.read_text(encoding="utf-8")
    start_idx = text.find(PROTOCOL_START)
    end_idx = text.find(PROTOCOL_END)
    if start_idx == -1 or end_idx == -1:
        text += f"\n{PROTOCOL_START}\n{PROTOCOL_BODY}{PROTOCOL_END}\n"
    else:
        text = text[: start_idx + len(PROTOCOL_START)] + "\n" + PROTOCOL_BODY + text[end_idx:]
    claude_path.write_text(text, encoding="utf-8")
```

在 `main()` 中增加参数：

```python
parser.add_argument("--update-protocol", action="store_true")
parser.add_argument("--platform", choices=["cursor"], default=None)
```

在 `main()` 逻辑中增加：

```python
if args.update_protocol:
    update_protocol(root / "CLAUDE.md")
    print(f"Updated protocol markers in {root / 'CLAUDE.md'}")
    return 0
if args.platform == "cursor":
    cursor_rules = root / ".cursorrules"
    if not cursor_rules.exists():
        cursor_rules.write_text(
            f"{PROTOCOL_START}\n{PROTOCOL_BODY}{PROTOCOL_END}\n",
            encoding="utf-8",
        )
        print(f"Created {cursor_rules} with protocol markers")
    else:
        update_protocol(cursor_rules)
        print(f"Updated protocol markers in {cursor_rules}")
    return 0
```

- [ ] **Step 3: 更新 `test_init.py`，增加 M1.5 初始化测试**

```python
def test_init_creates_claude_md_with_protocol_markers(self) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp) / "sandbox"
        subprocess.run(
            ["python3", "scripts/init.py", "--root", str(root)],
            cwd="GPT54",
            capture_output=True,
            text=True,
            check=True,
        )
        claude = root / "CLAUDE.md"
        self.assertTrue(claude.exists())
        content = claude.read_text(encoding="utf-8")
        self.assertIn("GPT54-PROTOCOL-START", content)
        self.assertIn("GPT54-PROTOCOL-END", content)
        self.assertIn("schema/rules.md", content)
        self.assertIn("schema/ingest.md", content)


def test_init_creates_ingest_schema(self) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp) / "sandbox"
        subprocess.run(
            ["python3", "scripts/init.py", "--root", str(root)],
            cwd="GPT54",
            capture_output=True,
            text=True,
            check=True,
        )
        ingest = root / "schema" / "ingest.md"
        self.assertTrue(ingest.exists())
        content = ingest.read_text(encoding="utf-8")
        self.assertIn("触发条件", content)
        self.assertIn("执行顺序", content)
        self.assertIn("禁止项", content)


def test_update_protocol_preserves_user_content(self) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp) / "sandbox"
        subprocess.run(
            ["python3", "scripts/init.py", "--root", str(root)],
            cwd="GPT54",
            capture_output=True,
            text=True,
            check=True,
        )
        claude = root / "CLAUDE.md"
        original = claude.read_text(encoding="utf-8")
        user_content = "\n## My Custom Section\n\nSome user notes here.\n"
        claude.write_text(original + user_content, encoding="utf-8")
        subprocess.run(
            ["python3", "scripts/init.py", "--root", str(root), "--update-protocol"],
            cwd="GPT54",
            capture_output=True,
            text=True,
            check=True,
        )
        updated = claude.read_text(encoding="utf-8")
        self.assertIn("My Custom Section", updated)
        self.assertIn("GPT54-PROTOCOL-START", updated)


def test_platform_cursor_creates_cursorrules(self) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp) / "sandbox"
        subprocess.run(
            ["python3", "scripts/init.py", "--root", str(root), "--platform", "cursor"],
            cwd="GPT54",
            capture_output=True,
            text=True,
            check=True,
        )
        cursorrules = root / ".cursorrules"
        self.assertTrue(cursorrules.exists())
        content = cursorrules.read_text(encoding="utf-8")
        self.assertIn("GPT54-PROTOCOL-START", content)
```

- [ ] **Step 4: 运行测试并确认通过**

Run: `cd GPT54 && python3 -m unittest tests/test_init.py -v`

Expected: PASS（含新增的 4 个 M1.5 测试）

- [ ] **Step 5: 升级 `audit.py`，增加 M1.5 专项审计**

`CLAUDE.md` 和 `schema/ingest.md` 的文件缺失检查已由 REQUIRED_FILES 列表覆盖。本步增加两项专项检查：标记段完整性和摄入规则章节完整性。

在 `REQUIRED_FILES` 列表后增加：

```python
PROTOCOL_MARKER_START = "<!-- GPT54-PROTOCOL-START -->"
PROTOCOL_MARKER_END = "<!-- GPT54-PROTOCOL-END -->"
INGEST_REQUIRED_SECTIONS = ["触发条件", "执行顺序", "禁止项"]
```

在 `audit()` 函数中，在 REQUIRED_FILES 检查之后增加以下检查逻辑：

```python
    claude_path = root / "CLAUDE.md"
    if claude_path.exists():
        claude_text = claude_path.read_text(encoding="utf-8")
        if PROTOCOL_MARKER_START not in claude_text or PROTOCOL_MARKER_END not in claude_text:
            issues.append({
                "id": f"AUDIT-{len(issues) + 1:04d}",
                "severity": "P0",
                "type": "missing_protocol_markers",
                "path": "CLAUDE.md",
                "message": "CLAUDE.md 缺少 GPT54 协议标记段",
                "expected": f"包含 {PROTOCOL_MARKER_START} 和 {PROTOCOL_MARKER_END}",
                "actual": "标记段不完整或不存在",
                "suggested_action": "运行 init.py --update-protocol 补充标记段",
            })
        else:
            schema_version = ""
            rules_path = root / "schema" / "rules.md"
            if rules_path.exists():
                for line in rules_path.read_text(encoding="utf-8").splitlines():
                    if "规则版本" in line or "version" in line.lower():
                        schema_version = line.split("：", 1)[-1].strip() if "：" in line else line.split(":", 1)[-1].strip()
                        break
            claude_version = ""
            for line in claude_text.splitlines():
                if "协议版本" in line or "protocol version" in line.lower():
                    claude_version = line.split("：", 1)[-1].strip() if "：" in line else line.split(":", 1)[-1].strip()
                    break
            if schema_version and claude_version and schema_version != claude_version:
                issues.append({
                    "id": f"AUDIT-{len(issues) + 1:04d}",
                    "severity": "P1",
                    "type": "version_mismatch",
                    "path": "CLAUDE.md",
                    "message": f"CLAUDE.md 协议版本 ({claude_version}) 与 schema/ 规则版本 ({schema_version}) 不一致",
                    "expected": f"版本一致 ({schema_version})",
                    "actual": f"CLAUDE.md={claude_version}, schema/={schema_version}",
                    "suggested_action": "运行 init.py --update-protocol 同步版本",
                })

    ingest_path = root / "schema" / "ingest.md"
    if ingest_path.exists():
        ingest_text = ingest_path.read_text(encoding="utf-8")
        for section in INGEST_REQUIRED_SECTIONS:
            if section not in ingest_text:
                issues.append({
                    "id": f"AUDIT-{len(issues) + 1:04d}",
                    "severity": "P1",
                    "type": "incomplete_ingest_schema",
                    "path": "schema/ingest.md",
                    "message": f"schema/ingest.md 缺少必要章节：{section}",
                    "expected": f"包含「{section}」章节",
                    "actual": f"缺少「{section}」章节",
                    "suggested_action": f"在 schema/ingest.md 中补充「{section}」章节",
                })
```

- [ ] **Step 6: 更新 `test_audit.py`，增加 M1.5 审计测试**

```python
def test_audit_detects_missing_claude_md(self) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp) / "repo"
        subprocess.run(
            ["python3", "scripts/init.py", "--root", str(root)],
            cwd="GPT54",
            check=True,
            capture_output=True,
            text=True,
        )
        (root / "CLAUDE.md").unlink()
        completed = subprocess.run(
            ["python3", "scripts/audit.py", "--root", str(root)],
            cwd="GPT54",
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(completed.returncode, 0)
        report_path = pathlib.Path(completed.stdout.strip().splitlines()[-1])
        report = json.loads(report_path.read_text(encoding="utf-8"))
        paths = [i["path"] for i in report["issues"]]
        self.assertIn("CLAUDE.md", paths)


def test_audit_detects_missing_protocol_markers(self) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp) / "repo"
        subprocess.run(
            ["python3", "scripts/init.py", "--root", str(root)],
            cwd="GPT54",
            check=True,
            capture_output=True,
            text=True,
        )
        (root / "CLAUDE.md").write_text("# No markers here\n", encoding="utf-8")
        completed = subprocess.run(
            ["python3", "scripts/audit.py", "--root", str(root)],
            cwd="GPT54",
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(completed.returncode, 0)
        report_path = pathlib.Path(completed.stdout.strip().splitlines()[-1])
        report = json.loads(report_path.read_text(encoding="utf-8"))
        types = [i["type"] for i in report["issues"]]
        self.assertIn("missing_protocol_markers", types)


def test_audit_detects_missing_ingest_schema(self) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp) / "repo"
        subprocess.run(
            ["python3", "scripts/init.py", "--root", str(root)],
            cwd="GPT54",
            check=True,
            capture_output=True,
            text=True,
        )
        (root / "schema" / "ingest.md").unlink()
        completed = subprocess.run(
            ["python3", "scripts/audit.py", "--root", str(root)],
            cwd="GPT54",
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(completed.returncode, 0)
        report_path = pathlib.Path(completed.stdout.strip().splitlines()[-1])
        report = json.loads(report_path.read_text(encoding="utf-8"))
        paths = [i["path"] for i in report["issues"]]
        self.assertIn("schema/ingest.md", paths)
```

- [ ] **Step 7: 写入 `test_protocol_discovery.py`**

```python
import pathlib
import subprocess
import tempfile
import unittest


class ProtocolDiscoveryTest(unittest.TestCase):
    def test_claude_md_points_to_all_schema_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp) / "repo"
            subprocess.run(
                ["python3", "scripts/init.py", "--root", str(root)],
                cwd="GPT54",
                check=True,
                capture_output=True,
                text=True,
            )
            claude = root / "CLAUDE.md"
            content = claude.read_text(encoding="utf-8")
            for schema_file in [
                "schema/rules.md",
                "schema/node-types.md",
                "schema/task-states.md",
                "schema/ingest.md",
            ]:
                self.assertIn(schema_file, content, f"CLAUDE.md missing reference to {schema_file}")

    def test_ingest_schema_has_required_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp) / "repo"
            subprocess.run(
                ["python3", "scripts/init.py", "--root", str(root)],
                cwd="GPT54",
                check=True,
                capture_output=True,
                text=True,
            )
            ingest = root / "schema" / "ingest.md"
            content = ingest.read_text(encoding="utf-8")
            for section in ["触发条件", "执行顺序", "禁止项"]:
                self.assertIn(section, content, f"ingest.md missing section: {section}")

    def test_full_init_audit_verify_cycle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp) / "repo"
            subprocess.run(
                ["python3", "scripts/init.py", "--root", str(root)],
                cwd="GPT54",
                check=True,
                capture_output=True,
                text=True,
            )
            audit_result = subprocess.run(
                ["python3", "scripts/audit.py", "--root", str(root)],
                cwd="GPT54",
                capture_output=True,
                text=True,
            )
            self.assertEqual(audit_result.returncode, 0, audit_result.stdout)
            verify_result = subprocess.run(
                ["python3", "scripts/verify.py", "--root", str(root)],
                cwd="GPT54",
                capture_output=True,
                text=True,
            )
            self.assertEqual(verify_result.returncode, 0, verify_result.stderr)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 8: 运行完整测试矩阵**

Run: `cd GPT54 && python3 -m unittest discover -s tests -v && tests/smoke/test_cli_smoke.sh`

Expected: 全部 PASS，冒烟测试输出 `smoke-pass`

- [ ] **Step 8a: 同步更新 `README.md` 和 `CONTRIBUTING.md`**

SPEC §16.3 要求：如果实际命令发生变化，必须同步更新 README.md 与 CONTRIBUTING.md。

在 `README.md` 的"常用命令"章节中，M1.5 后额外支持的命令已在 Task 1 Step 2 中预置，无需额外修改。

在 `CONTRIBUTING.md` 的 `Validation` 章节中增加 M1.5 命令：

```markdown
## Validation

```bash
python3 scripts/audit.py --root .
python3 scripts/verify.py --root .
python3 -m unittest discover -s tests
```

M1.5 后额外支持：

```bash
python3 scripts/init.py --root . --update-protocol
python3 scripts/init.py --root . --platform cursor
```
```

- [ ] **Step 9: 回写 M1.5 阶段状态**

```markdown
# Plan

- 当前目标：完成 M1.5 协议发现与首次摄入入口
- 成功标准：初始化结果包含 CLAUDE.md 发现层标记段；schema/ingest.md 存在且字段完整；audit.py 可检测协议发现入口和摄入规则缺失；README.md 足以让普通用户完成首次初始化并触发第一次摄入
- 当前阶段：M1.5
- 步骤列表：
  - 写入 schema/ingest.md（源仓库完整版）
  - 升级 init.py 增加 --update-protocol 和 --platform 参数
  - 升级 audit.py 增加 M1.5 专项审计
  - 写入 test_protocol_discovery.py
  - 运行完整测试矩阵
- 当前执行中的一步：准备进入 M2 规划
- 后续候选步骤：
  - 增加节点摄入脚本
  - 增加快照对比
  - 增加审计 Markdown 报告
```

```markdown
# Progress

- 最新状态：M1.5 协议发现与首次摄入入口已完成
- 已完成：
  - M0 骨架建立
  - M1 最小闭环（init/audit/verify）
  - M1.5 CLAUDE.md 发现层标记段
  - M1.5 schema/ingest.md 摄入工作流
  - M1.5 audit.py 协议发现入口检测
  - M1.5 test_protocol_discovery.py
  - M1.5 --update-protocol 和 --platform cursor 支持
- 当前阻塞：无
- 下一步：设计 M2 稳定维护态
```

```markdown
# Changelog

## 2026-05-14

- Added: `schema/ingest.md`
- Added: `CLAUDE.md` 发现层标记段生成
- Added: `audit.py` M1.5 审计项（协议标记、摄入规则）
- Added: `test_protocol_discovery.py`
- Added: `init.py --update-protocol` 和 `--platform cursor` 参数
```

- [ ] **Step 10: Commit**

```bash
git add GPT54/schema/ingest.md GPT54/scripts/init.py GPT54/scripts/audit.py GPT54/tests/test_protocol_discovery.py GPT54/tests/test_init.py GPT54/tests/test_audit.py GPT54/project/plan.md GPT54/project/progress.md GPT54/CHANGELOG.md
git commit -m "feat: add GPT54 M1.5 protocol discovery and ingest entry"
```

## 覆盖性检查

- `FR-001 初始化骨架`：Task 1, Task 2, Task 3
- `FR-004 项目状态管理`：Task 2, Task 6
- `FR-005 审计机制`：Task 4, Task 7
- `FR-006 控制决策`：Task 4, Task 7
- `FR-008 验证闭环`：Task 5, Task 6
- `FR-009 AI 助手合同`：由 `PRD.md`、`SPEC.md` 与本计划共同保证；Task 7 补齐发现层入口
- `FR-010 开源外壳`：Task 1
- `M0`：Task 1, Task 2
- `M1`：Task 3, Task 4, Task 5, Task 6
- `M1.5`：Task 7
  - `SPEC §7.8 CLAUDE.md 发现层标记段`：Task 7 Step 2
  - `SPEC §7.3 schema/ingest.md 摄入工作流`：Task 7 Step 1, Step 2
  - `SPEC §12.2 审计项 9`：Task 7 Step 5（missing_protocol_markers）
  - `SPEC §12.2 审计项 10`：Task 7 Step 5（version_mismatch）
  - `SPEC §12.2 审计项 11`：Task 4 REQUIRED_FILES + Task 7 Step 5（incomplete_ingest_schema）
  - `SPEC §12.3 审计输入`：Task 4 Step 3（--rules-version, --audit-scope）
  - `SPEC §16.3 M1.5 测试命令`：Task 7 Step 2（--update-protocol, --platform cursor）
  - `SPEC §16.3 命令同步`：Task 7 Step 8a
  - `SPEC §18.1 README 目录说明/常用命令`：Task 1 Step 2
  - `SPEC §18.2 CONTRIBUTING 如何提议变更/哪些改动必须先讨论`：Task 1 Step 3
  - `SPEC §18.5 CODE_OF_CONDUCT 问题升级路径`：Task 1 Step 3
  - `SPEC §19.3 M1.5 完成条件`：Task 7 全部步骤

### M2 已知缺口

以下 SPEC 条款在 M0-M1.5 中未实现，计划在 M2 阶段补齐：

- `SPEC §12.2 审计项 2`：目录位置错误检测
- `SPEC §12.2 审计项 3`：命名不符合规则检测
- `SPEC §12.2 审计项 4`：docs/index.md 未覆盖节点检测
- `SPEC §12.2 审计项 5`：孤立节点检测
- `SPEC §12.2 审计项 6`：状态文件缺字段检测
- `SPEC §12.2 审计项 8`：审计产物未回写检测
- `SPEC §16.1 测试项 3`：状态机合法迁移测试
- `SPEC §16.2 夹具要求`：缺文件样例、命名错误样例、状态错误样例
- `SPEC §7.4 基线与报告可比较`：快照对比功能

## 自检结论

- 未使用占位符或延后实现标记。
- 没有引入第三方依赖或超出 `M0/M1/M1.5` 范围的功能。
- 任务顺序遵循先骨架、后规则、再脚本、再验证与回写、最后发现层与摄入入口的最小闭环原则。
- `M1.5` 不推翻 `M1` 主骨架，只在 `init.py`、`audit.py` 和 `schema/` 上做增量。
- `CLAUDE.md` 标记段外内容受保护，`--update-protocol` 不会覆盖用户自定义部分。
- `audit.py` 接受 `--rules-version` 和 `--audit-scope` 参数，输出包含 `rules_version` 和 `audit_scope` 字段（满足 SPEC §12.3）。
- `audit.py` 可检测 CLAUDE.md 与 schema/ 版本不一致（满足 SPEC §12.2 审计项 10）。
- `README.md` 包含目录说明和常用命令章节（满足 SPEC §18.1）。
- `CONTRIBUTING.md` 包含如何提议变更和哪些改动必须先讨论（满足 SPEC §18.2）。
- `CODE_OF_CONDUCT.md` 包含问题升级路径（满足 SPEC §18.5）。
- M1.5 命令变化后同步更新 README.md 和 CONTRIBUTING.md（满足 SPEC §16.3）。
- SPEC §12.2 审计项 2-6, 8、§16.1 测试项 3、§16.2 夹具要求、§7.4 基线对比列为 M2 已知缺口。
