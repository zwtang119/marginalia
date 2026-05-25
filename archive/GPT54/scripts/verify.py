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
