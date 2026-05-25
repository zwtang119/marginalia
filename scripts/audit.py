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
    parser.add_argument(
        "--skip-templates", action="store_true", default=True,
        help="跳过 templates/ 目录（默认开启）",
    )
    parser.add_argument(
        "--skip-archive", action="store_true", default=True,
        help="跳过 archive/ 目录及 *-archive* 文件（默认开启）",
    )
    parser.add_argument(
        "--no-skip", action="store_true",
        help="禁用所有跳过规则，检查全部文件",
    )
    parser.add_argument(
        "--external-kb-dirs", default="",
        help="外部知识库目录，逗号分隔（如 cds-runtime-kb,cds-vaults）",
    )
    parser.add_argument(
        "--brief", action="store_true",
        help="只输出 P0/P1/P2 计数（单行）",
    )
    parser.add_argument(
        "--exit-code-only", action="store_true",
        help="无输出，仅通过退出码反映状态（P0>0→2, P1>0→1, 0→0）",
    )
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
