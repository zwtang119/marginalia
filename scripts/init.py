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
