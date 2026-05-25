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

PROTOCOL_MARKER_START = "<!-- GPT54-PROTOCOL-START -->"
PROTOCOL_MARKER_END = "<!-- GPT54-PROTOCOL-END -->"
INGEST_REQUIRED_SECTIONS = ["触发条件", "执行顺序", "禁止项"]


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


def _append_trend(root: Path, counts: dict) -> dict:
    snapshots_dir = root / "audit" / "snapshots"
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    history_path = snapshots_dir / "trend_history.jsonl"

    total_defects = counts.get("total", 0)
    history = []
    if history_path.exists():
        for line in history_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    history.append(json.loads(line).get("total_defects", 0))
                except json.JSONDecodeError:
                    pass

    history.append(total_defects)

    direction = "insufficient"
    if len(history) >= 5:
        last5 = history[-5:]
        if all(last5[i] > last5[i + 1] for i in range(len(last5) - 1)):
            direction = "converging"
        elif all(last5[i] < last5[i + 1] for i in range(len(last5) - 1)):
            direction = "diverging"
        else:
            direction = "stable"
    elif len(history) >= 3:
        last3 = history[-3:]
        if all(last3[i] > last3[i + 1] for i in range(len(last3) - 1)):
            direction = "converging"
        elif all(last3[i] < last3[i + 1] for i in range(len(last3) - 1)):
            direction = "diverging"

    record = {
        "total_defects": total_defects,
        "counts": counts,
        "direction": direction,
        "history": history[-10:],
        "audit_count": len(history),
    }
    with open(history_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--rules-version", default="")
    parser.add_argument("--audit-scope", default="full")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    report = audit(root, rules_version=args.rules_version, audit_scope=args.audit_scope)
    report_path = write_report(root, report)
    _append_trend(root, report["counts"])
    print(report_path)
    return 1 if report["severity_distribution"]["P0"] > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
