#!/usr/bin/env python3
import argparse
from pathlib import Path


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

FILES = {
    "README.md": "# GPT54\n",
    "PRD.md": "# PRD\n",
    "SPEC.md": "# SPEC\n",
    "CLAUDE.md": (
        "# GPT54 Protocol Discovery\n"
        "\n"
        + PROTOCOL_START + "\n"
        + PROTOCOL_BODY
        + PROTOCOL_END + "\n"
    ),
    "docs/index.md": "# 知识索引\n",
    "project/project.md": "# Project\n",
    "project/plan.md": "# Plan\n",
    "project/progress.md": "# Progress\n",
    "project/open-questions.md": "# Open Questions\n",
    "schema/rules.md": (
        "# Rules\n"
        "\n"
        "- 规则版本：v0.1.0\n"
        "\n"
        "## 执行规则\n"
        "\n"
        "1. 先读 PRD 和 SPEC，理解项目目标\n"
        "2. 读取项目状态（project/plan.md、project/progress.md）\n"
        "3. 最小必要修改\n"
        "4. 修改后运行审计和验证\n"
        "5. 回写 progress.md 和 index.md\n"
        "6. 禁止引入第三方依赖\n"
        "7. 禁止做成在线服务\n"
    ),
    "schema/node-types.md": (
        "# Node Types\n"
        "\n"
        "- concept：概念节点\n"
        "- decision：决策节点\n"
        "- task：任务节点\n"
        "- note：补充说明节点\n"
    ),
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


def update_protocol(target_path: Path) -> None:
    if not target_path.exists():
        target_path.write_text(
            f"{PROTOCOL_START}\n{PROTOCOL_BODY}{PROTOCOL_END}\n",
            encoding="utf-8",
        )
        return
    text = target_path.read_text(encoding="utf-8")
    start_idx = text.find(PROTOCOL_START)
    end_idx = text.find(PROTOCOL_END)
    if start_idx == -1 or end_idx == -1:
        text += f"\n{PROTOCOL_START}\n{PROTOCOL_BODY}{PROTOCOL_END}\n"
    else:
        text = text[: start_idx + len(PROTOCOL_START)] + "\n" + PROTOCOL_BODY + text[end_idx:]
    target_path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--update-protocol", action="store_true")
    parser.add_argument("--platform", choices=["cursor"], default=None)
    args = parser.parse_args()
    root = Path(args.root).resolve()

    if args.update_protocol:
        update_protocol(root / "CLAUDE.md")
        print(f"Updated protocol markers in {root / 'CLAUDE.md'}")
        return 0

    if args.platform == "cursor":
        root.mkdir(parents=True, exist_ok=True)
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

    initialize(root)
    print(f"Initialized GPT54 skeleton at {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
