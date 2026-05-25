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
