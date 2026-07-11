# Investigation: audit.py / verify.py 工具误报

## Summary

`scripts/audit.py` 和 `scripts/verify.py` 在 Marginalia 自带的 `example/` 示例仓库上即触发误报。初步复现确认：audit.py 报告 3 个虚假孤儿页，verify.py 报告 1 个虚假缺失目录。本调查旨在定位根因并排查是否存在同类误报模式。

## Symptoms

- 运行 `python3 scripts/audit.py --root example/` 报告 3 个 P2 孤儿页：
  - `comparisons/memory-systems.md`
  - `concepts/marginalia.md`
  - `decisions/why-marginalia.md`
  但这 3 个页面都被 `example/index.md` 通过 `[[concepts/marginalia]]` 等路径式 wikilink 显式链接。
- 运行 `python3 scripts/verify.py --root example/` 报告 `缺少目录：annotations/`，但 `schema/node-types.md` 明确规定批注是页内 `> [!memo]` 块，并非独立目录；且 `comparisons/` 在 schema 中标记为"可选"。
- `scripts/audit.py` 在系统默认 Python 3.9.6 上直接抛 `TypeError`（使用了 `set[str] | None` 这种 3.10+ 语法）。

## Background / Prior Research

- 仓库 git 历史只有 4 个 commit；audit.py/verify.py 自 `48bd2d6 init: Marginalia v0.3` 引入，后续 `bdcfe3e` 仅清理死代码，未触及检测逻辑。
- `CHANGELOG.md` 显示 v0.2.1 曾修复一批误报（模板占位符、templates/archive 跳过、别名/锚点语法），但孤儿页检测和 verify.py 的目录要求从未被重新审视。
- `docs/feedback/openclaw-field-report-2026-05-15.md` 提到生产部署中审计结果 "P2=5（设计内孤儿页）"，说明孤儿页检测在生产中已产生噪声，但此前被归类为"设计内"而非工具误报。
- `archive/GPT54/scripts/audit.py` 和 `verify.py` 是 GPT54 协议的独立实现（检查 PRD.md/协议标记/任务状态），与当前 Marginalia 知识库脚本无关，不作为对照。

## Investigator Findings

<!-- Pair investigator appends structured analysis here (file:line refs, evidence, conclusions). -->

### 0. Methodology

- Read source: `scripts/audit.py` (221 lines), `scripts/verify.py` (49 lines), `scripts/init.py` (80 lines), `templates/{concept,decision,annotation}.md`, `schema/{rules,node-types,first-ingest}.md`, `example/**`.
- Ran audit/verify against `example/` and `templates/` with default and `--no-skip` flags.
- Ran audit with `--external-kb-dirs ""`, `--external-kb-dirs nonexistent-dir`.
- Dispatched 3 read-only explore probes in parallel:
  - classify all `[[…]]` in templates vs PLACEHOLDER_PATTERNS coverage
  - trace `resolve_wikilink` semantics for path-style links, recursion, traversal, aliasing
  - audit `--no-skip`, `--skip-templates`, `--skip-archive`, `--external-kb-dirs` semantics
- Verified all findings against actual file paths and line numbers.

---

### 1. Findings Index

#### VERIFICATIONS of the 5 already-known defects

| ID | Status | Defect | File:Line |
|---|---|---|---|
| V1 | VERIFIED | `set[str] \| None` syntax crashes Python 3.9 | `scripts/audit.py:43,51,71,95` |
| V2 | VERIFIED | `check_orphan_pages` skips index.md link harvest via `continue` | `scripts/audit.py:107-108` |
| V3 | VERIFIED | Orphan identity mismatch — `all_pages` uses `.md` paths, `all_links` uses path-style without `.md` | `scripts/audit.py:114-119` |
| V4 | VERIFIED | verify.py `REQUIRED_DIRS` includes `annotations/` (fictional) and `comparisons/` (optional in schema) | `scripts/verify.py:6-11` vs `schema/node-types.md:47-53` |
| V5 | VERIFIED | init.py references fictional `wiki/annotations/`; templates reference `[[annotations/xxx]]` | `scripts/init.py:16-19`, `templates/concept.md:67,decision.md:79,annotation.md:66` |

#### NEW defects found during fan-out

| ID | Category | Defect | File:Line |
|---|---|---|---|
| N1 | AUDIT/PLACEHOLDER | `[[annotations/xxx]]` placeholder escapes PLACEHOLDER_PATTERNS, flagged as BROKEN-P1 (3×) when scanning `templates/` | `scripts/audit.py:9-14`, `templates/concept.md:67,decision.md:79,annotation.md:66` |
| N2 | INIT/SCHEMA | init.py `DIRECTORIES` is missing `wiki/entities/` despite schema listing `entities/` as an optional writeback target | `scripts/init.py:16-19` vs `schema/node-types.md:49` |
| N3 | AUDIT/RESOLVE | `resolve_wikilink` has no recursive / subdirectory search — a bare link `[[marginalia]]` never finds `root/concepts/marginalia.md` | `scripts/audit.py:51-68` |
| N4 | AUDIT/SECURITY | `resolve_wikilink` has no path-containment check — `[[../../../etc/passwd]]` resolves outside the KB; existing system files would be misidentified as valid wikilink targets | `scripts/audit.py:51-68` |
| N5 | AUDIT/CLI | `--no-skip` does NOT actually disable all skip rules — the `-archive` substring check at lines 37-39 runs unconditionally, contradicting the help text | `scripts/audit.py:172-174,32-40` |
| N6 | AUDIT/INDEX | `check_index_exists` message hardcodes `"wiki/index.md"` regardless of `--root` value, misleading users running against any non-`wiki/` root | `scripts/audit.py:122-133` |
| N7 | AUDIT/RESOLVE | `resolve_wikilink` `root.parent` candidates leak outside KB when root is at repo root (e.g., running audit against the Marginalia repo itself) | `scripts/audit.py:55-56` |
| N8 | VERIFY/EXITCODE | `verify.py` returns exit 1 for both "directory does not exist" and "missing dirs/files"; `audit.py` distinguishes (2 vs 2/1) | `scripts/verify.py:42-48` vs `scripts/audit.py:178,213-218` |
| N9 | AUDIT/SKIP | When `--root templates/` is supplied, `should_skip_file` never skips files because `'templates'` is the root, not a child part; the templates/ skip is therefore inert against its own tree | `scripts/audit.py:32-40,40` |
| N10 | AUDIT/PATH | `--external-kb-dirs` silently accepts nonexistent directories and adds non-existent candidates; no warning or exit code | `scripts/audit.py:59-67` |
| N11 | AUDIT/REPORT | orphan `suggested_action` uses bare stem (`[[marginalia]]`) for path-style orphans (`concepts/marginalia.md`), inconsistent with the canonical link convention used elsewhere | `scripts/audit.py:117-119` |
| N12 | AUDIT/PARSE | `audit.py:142-145` severity_distribution initializes `P3:0` but no issue ever uses P3 — dead code branch (low severity) | `scripts/audit.py:142-145` |
| N13 | AUDIT/PARSE | `find_wikilinks` regex `\[\[([^\]]+)\]\]` does not escape `]`; this is correct ASCII behavior but means nested `]]` in raw text (e.g., a code block containing `[[a]]]b]]`) would split incorrectly | `scripts/audit.py:14` (note: not observed to produce false positives in current corpus) |

---

### 2. Detailed NEW Findings

#### N1 — `annotations/` placeholder escapes PLACEHOLDER_PATTERNS (HIGH-IMPACT, NEW)

**Evidence** — `templates/annotation.md:66`:
```
- [[concepts/xxx]]: 相关概念
- [[decisions/xxx]]: 相关决策
- [[annotations/xxx]]: 其他批注
```
Same line in `templates/concept.md:67` and `templates/decision.md:79`.

`PLACEHOLDER_PATTERNS` at `scripts/audit.py:9-14`:
```python
PLACEHOLDER_PATTERNS = [
    re.compile(r"^\[\[wikilink\]\]$", re.IGNORECASE),
    re.compile(r"^\[\[concepts?/[^\]]+\]\]$", re.IGNORECASE),
    re.compile(r"^\[\[decisions?/[^\]]+\]\]$", re.IGNORECASE),
    re.compile(r"^\[\[entities?/[^\]]+\]\]$", re.IGNORECASE),
]
```
No pattern matches `annotations/…`. Confirmed by running audit against `templates/` with `--no-skip`: BROKEN-0001/0002/0003 all flag `[[annotations/xxx]]` at P1 severity. False positives, because the user's `schema/node-types.md:51-53` says annotations live as inline `> [!memo]` blocks, NOT in an `annotations/` directory. **The templates themselves encode a fictional directory `annotations/` that no schema entry supports.**

**Observed output**:
```
"id": "BROKEN-0001", "severity": "P1",
"message": "断链：[[annotations/xxx]]（在 annotation.md 中）",
```

**Fix paths** (one of):
- Add a placeholder pattern: `re.compile(r"^\[\[annotations?/[^\]]+\]\]$", re.IGNORECASE)`, OR
- Replace `[[annotations/xxx]]` with `[[wikilink]]` in all 3 templates to match the existing placeholder pattern, OR
- Reconcile the schema/init/templates to actually support an `annotations/` directory.

#### N2 — `entities/` missing from init.py DIRECTORIES (MEDIUM-IMPACT, NEW)

**Evidence** — `schema/node-types.md:49`:
```
| entities/      | 实体、系统、对象     | （可选） |
```

`scripts/init.py:16-19`:
```python
DIRECTORIES = [
    "wiki/concepts",
    "wiki/decisions",
    "wiki/annotations",
    "wiki/comparisons",
]
```
`entities/` is missing. Consequence: after `init.py` runs, the KB has no `wiki/entities/`, yet the schema declares it valid. A user following the schema and creating an `entities/foo.md` page may not realize `init.py` did not provision it (it does work because `path.parent.mkdir(parents=True, exist_ok=True)` handles individual subdirs, but the **initialization step silently omits a directory the schema claims to support**).

#### N3 — `resolve_wikilink` has no recursive/subdirectory search (MEDIUM-IMPACT, NEW)

**Evidence** — `scripts/audit.py:53-58`:
```python
candidates = [
    root / f"{link}.md",
    root / link,
    root.parent / f"{link}.md",
    root.parent / link,
]
```
Only 4 flat candidates. A bare link `[[marginalia]]` (no path prefix) never searches `root/concepts/marginalia.md`. **This is a false-positive broken-link source for any KB whose users write bare-name links to nested pages.**

`example/` happens to use path-style links (`[[concepts/marginalia]]`) so the bug is not visible there. But the schema (e.g., `schemas/rules.md` §读取规则) and templates (`templates/concept.md:29` and elsewhere) repeatedly use bare-name references. Any real KB that follows the schema will hit this false positive.

**Implication**: a fundamental property of `resolve_wikilink` (the "wikilink resolution" step that BrokenLink detection depends on) doesn't match how wikilinks are conventionally written.

#### N4 — Path traversal / containment gap in `resolve_wikilink` (LOW-IMPACT for normal users, but worth noting — NEW)

**Evidence** — `scripts/audit.py:52-58` does not validate that resolved candidates are inside `root` or any other allowed boundary. A link `[[../../../etc/passwd]]`:
- `root / f"{link}.md"` → `/etc/passwd.md`
- `root / link` → `/etc/passwd`

`any(c.exists() for c in candidates)` returns True on Linux if `/etc/passwd` exists. **The audit would silently mark a sensitive system file as a "valid wikilink target."** This is a security boundary issue, not currently exploited because links are author-controlled, but it does mean a hostile or careless wikilink text could escape the KB. **No should-not-exist guard**: any path outside the KB either resolves to None (false broken) or to a system file (false valid).

#### N5 — `--no-skip` does NOT disable the `-archive` substring check (MEDIUM-IMPACT CLI BUG, NEW)

**Evidence** — `scripts/audit.py:172-174` help text:
```
--no-skip  禁用所有跳过规则，检查全部文件
```
Translation: "Disable all skip rules, check all files."

But `scripts/audit.py:36-39`:
```python
for part in parts:
    if "-archive" in part.lower():
        return True
```
The substring check is unconditional — `skip_dirs` does not gate it. `--no-skip` only empties the directory-based set (lines 195-200). The flag name and help text are inconsistent with actual behavior.

**Fix**: gate the `-archive` substring check on a flag or on `not args.no_skip`.

#### N6 — `check_index_exists` hardcodes `"wiki/index.md"` in message (LOW-IMPACT, NEW)

**Evidence** — `scripts/audit.py:129`:
```python
"message": "缺少索引文件 wiki/index.md",
```
When running `audit.py --root templates/` the message tells the user to create `wiki/index.md` even though `--root` was `templates/`. The fix is to template the message with the actual root name (or just use the basename). Confirmed by `audit.py --root templates/` output: `"message": "缺少索引文件 wiki/index.md"`.

**Additional scoping**: `check_index_exists` only checks `root/index.md`. Nested `concepts/index.md`, `decisions/index.md`, etc., are never inspected (line 124). If a KB omits the root `index.md` but supplies per-directory indices, audit still flags P0 missing-index. Probably intentional, but worth noting that the index-existence check is monolithic.

#### N7 — `root.parent` candidates leak outside the KB (LOW-IMPACT, NEW)

**Evidence** — `scripts/audit.py:55-56`:
```python
root.parent / f"{link}.md",
root.parent / link,
```
If the user runs audit against the repo root (e.g., `audit.py --root /path/to/Marginalia/` instead of `--root /path/to/Marginalia/wiki/`), candidates include files outside the wiki, e.g., `CHANGELOG.md`, `README.md`, etc. False positives (links that are "valid" because they point at a sibling file the auditor wasn't supposed to be aware of) or false negatives (legit wikilink missing because the auditor searched two-levels-up).

#### N8 — `verify.py` exit-code inconsistency with `audit.py` (LOW-IMPACT, NEW)

**Evidence** — `scripts/verify.py:30-32,42-48`:
```python
if not root.exists():
    print(f"目录不存在：{root}")
    return 1
```
`scripts/audit.py:178-181`:
```python
if not root.exists():
    if not args.exit_code_only:
        print(f"目录不存在：{root}")
    return 2
```
Audit returns 2 for "directory does not exist," verify returns 1. Both report "目录不存在" — exit codes are not aligned. CI scripts that key off exit code may treat the two tools inconsistently.

#### N9 — `--root templates/` never triggers templates/ skip (DOCUMENTATION/UX BUG, NEW)

**Evidence** — `scripts/audit.py:32-40,33-35`:
```python
def should_skip_file(rel_path: Path, skip_dirs: set[str]) -> bool:
    parts = rel_path.parts
    for d in skip_dirs:
        if d in parts:
            return True
```
When `root = templates/` and `rel_path = concept.md`, `rel_path.parts = ('concept.md',)` — `'templates'` is NOT in `parts`. The directory-skip loop never fires. **The templates/ skip only works when templates is a subdirectory of an outer root, NOT when it is the root itself.** Running `audit.py --root templates/` always reports the 7 false positives in templates (1 P0, 3 P1, 3 P2). The intended behavior is presumably "always skip the templates directory tree" — but the implementation is path-relative.

#### N10 — `--external-kb-dirs` silently ignores nonexistent dirs (LOW-IMPACT, NEW)

**Evidence** — `scripts/audit.py:59-67`:
```python
if external_kb_dirs:
    for kb_dir in external_kb_dirs:
        kb_path = Path(kb_dir)
        if not kb_path.is_absolute():
            kb_path = root.parent / kb_dir
        candidates.extend([
            kb_path / f"{link}.md",
            kb_path / link,
        ])
```
A typo in `--external-kb-dirs` (e.g., `cds-runtme-kb` instead of `cds-runtime-kb`) is silently accepted. No warning. No exit code change. The auditor just reports more BROKEN entries. Contrast with most lint tools that warn on missing config.

#### N11 — Orphan `suggested_action` recommends bare-stem link for path-style orphans (LOW-IMPACT, NEW)

**Evidence** — `scripts/audit.py:117-119`:
```python
"message": f"孤儿页：{page}（无入链）",
"suggested_action": f"在 index.md 或相关页面添加 [[{page_stem}]] 链接",
```
For `concepts/marginalia.md`, `page_stem = "marginalia"` so the suggestion is `[[marginalia]]`. But the canonical convention used in `example/index.md` is path-style `[[concepts/marginalia]]`. Following the suggestion literally creates a link whose target the orphan check will register against page_stem — so it WOULD resolve the orphan — but the new link style is inconsistent with the rest of the KB. **The fix for orphan detection will diverge from the fix for orphan identity**, perpetuating two competing conventions.

#### N12 — Dead-code `P3` severity slot (LOW-IMPACT, NEW)

**Evidence** — `scripts/audit.py:142-145`:
```python
distribution = {"P0": 0, "P1": 0, "P2": 0, "P3": 0}
```
No code path produces P3. Not a false positive, but worth flagging as dead initialization.

#### N13 — `find_wikilinks` regex robustness (NOT OBSERVED to false-positive, NEW NOTE)

**Evidence** — `scripts/audit.py:14`: `re.findall(r"\[\[([^\]]+)\]\]", text)`. The greedy match against `[^]]+` correctly terminates at the first `]]`. Edge cases like `[[a]]b]]` (which contains two `]]` substrings) could mis-parse, but in current corpus all wikilinks are well-formed. No false positive found in practice on `example/` or `templates/`.

---

### 3. Empirical Cross-Reference

#### 3a. Actual runs and outputs

| Command | Output summary |
|---|---|
| `audit.py --root example/` | 3 P2 orphans (already-known defect V3 confirmed) |
| `audit.py --root example/ --no-skip` | **Identical** to without `--no-skip` (defect N5 not triggered because example/ has no `-archive` content) |
| `audit.py --root templates/` | 7 issues: 1 P0 (missing index, message says `wiki/index.md` despite running against `templates/`) + 3 P1 BROKEN for `[[annotations/xxx]]` (defect N1) + 3 P2 orphans (defect N9) |
| `audit.py --root templates/ --no-skip` | **Identical** (defect N9 root-as-skip-name bug means templates never skips itself) |
| `audit.py --root example/ --external-kb-dirs nonexistent-dir` | Same as default — invalid KB dir silently dropped (defect N10) |
| `verify.py --root example/` | `缺少目录：annotations/` only (defect V4 confirmed; comparisons/ exists) |
| `verify.py --root templates/` | `缺少目录：concepts/`, `缺少目录：decisions/`, `缺少目录：annotations/`, `缺少目录：comparisons/`, `缺少文件：index.md` (5 errors, because templates is not a KB) |

#### 3b. New defects ranked by impact

| Rank | ID | Severity | Blast radius |
|---|---|---|---|
| 1 | N1 | HIGH | Templates-flagged BROKEN-P1 against any user KB that copies templates verbatim |
| 2 | N3 | MEDIUM | Any user writing bare `[[name]]` links to nested pages |
| 3 | N5 | MEDIUM | Users invoking `--no-skip` expecting templates skipped |
| 4 | N9 | MEDIUM | Same — root=`templates/` doesn't get the template-skip benefit |
| 5 | N4 | MEDIUM (security posture) | Hostile/lazy wikilinks escape KB |
| 6 | N2 | LOW-MEDIUM | Schema claim vs init.py reality drift |
| 7 | N6 | LOW | Hardcoded "wiki/" in message misleads |
| 8 | N7 | LOW | root.parent fallback can match siblings |
| 9 | N8 | LOW | Exit code inconsistency |
| 10 | N10 | LOW | Silent external KB dir typo |
| 11 | N11 | LOW | suggested_action diverges from canonical convention |
| 12 | N12 | TRIVIAL | Dead `P3` slot |
| 13 | N13 | NOT OBSERVED | find_wikilinks regex corner-case |

#### 3c. Counts of NEW vs VERIFICATIONS

- VERIFICATIONS: 5/5 of the originally identified defects re-confirmed with file:line evidence.
- NEW: 13 defects identified during fan-out, of which N1 (placeholder gap) is the most likely to ship noise to downstream users.
- The "5 known" combine with N1, N2, N9 to form a tight cluster: schema/templates/init/scripts disagree about whether `annotations/` exists, and audit/verify both penalize the disagreement.

---

### 4. Notes on Verification of Hypotheses from Task Brief

- **Double-reporting in `check_broken_links`**: NOT observed. Each wikilink that fails resolution produces exactly one issue. The duplicates in the templates/ output come from the SAME broken link `[[annotations/xxx]]` in three separate files — not double-reporting.
- **Placeholder skip correctness**: PLACEHOLDER_PATTERNS correctly skips `[[wikilink]]` and the singular/plural `concepts?/`, `decisions?/`, `entities?/` patterns; but misses `annotations/` (defect N1) and any user-defined directory patterns (e.g., `tasks/`, `notes/`) that aren't on the audit's hardcoded list.
- **`-archive` substring match**: confirmed N5 above; it is NOT a legitimate-file skip bug — it is unrelated to `--no-skip` semantics.
- **`check_index_exists` message accuracy**: confirmed N6; hardcoded `"wiki/index.md"` regardless of `--root`.
- **verify.py beyond REQUIRED_DIRS**: confirmed N8 (exit code consistency); no `index.md` content check, no schema conformance check, no `> [!memo]` date-format check. Schema templates use `YYYY-MM-DD` but audit/verify don't validate this format anywhere.

---

## Investigation Log

### Phase 1 - Initial Reproduction
**Hypothesis:** audit.py/verify.py 在 example/ 上产生误报。
**Findings:** 已复现 3 个孤儿页误报 + 1 个缺失目录误报 + 1 个 Python 3.9 兼容性崩溃。
**Evidence:**
- `scripts/audit.py:95-119` `check_orphan_pages` 在循环中对 `index.md` 执行 `continue`，导致 index.md 的正文与 wikilink 从未被读取。
- `scripts/audit.py:109-110` 孤儿判定条件 `page_stem not in all_links and str(page) not in all_links` 只比较 stem（如 `marginalia`）和带 `.md` 的相对路径（如 `concepts/marginalia.md`），但路径式 wikilink 的链接目标是 `concepts/marginalia`（无 `.md`），两者永不匹配。
- `scripts/verify.py:6-11` `REQUIRED_DIRS` 包含 `annotations`，但 `schema/node-types.md:24-34,55` 明确批注是页内 `> [!memo]` 块；`comparisons/` 在 `schema/node-types.md:54` 标记为可选。
- `scripts/audit.py:43,51,71,95` 使用 `set[str] | None` 语法，Python 3.9 不支持。
**Conclusion:** 已确认多处误报源，需进一步排查是否存在同类模式（如断链检测的路径解析、外部 KB 解析、placeholder 规则等）。

### Phase 2 - Pair Investigator Fan-out
**Hypothesis:** 5 known defects 之外还存在同类误报模式。
**Findings:** 验证 5/5 已知缺陷（V1–V5），新发现 13 个缺陷（N1–N13）；合成阶段再补 1 个（N14 init.py 片段过期）+ 1 类缺失缺陷（N15 边界逃逸假阴性）。
**Evidence:** 见上文 ## Investigator Findings 第 2 节及下文 Root Cause。
**Conclusion:** 误报不是孤立 bug，而是 4 个结构性集群。

### Phase 3 - Chat Synthesis
**Hypothesis:** 18 个缺陷可归并为少数根因集群。
**Findings:** 确认 4 个集群（annotations/ 四方不一致、链接身份模型缺失、--root 相对路径假设、边界逃逸）；识别出 1 类此前未列出的假阴性缺陷（N15）。
**Evidence:** 见下文 Root Cause 第 4、5 集群与 N15。
**Conclusion:** 根因是 schema 与脚本/模板/init 多处漂移，加上 resolve_wikilink 缺少统一链接身份模型与边界约束。

---

## Root Cause

误报不是孤立 bug，而是 4 个结构性集群 + 1 个合成阶段补登的缺陷类。共 **18 个独立缺陷**（5 验证 + 13 新发现 + N14 + N15 类）。

### 集群 A — `annotations/` 虚构目录（四方不一致）→ V4 + V5 + N1（+ N2 部分）

`schema/node-types.md:24-34,55` 明确规定批注是页内 `> [!memo]` 块，**不是目录**。但代码四处与之冲突：

| 代码点 | 行为 | 文件:行 |
|---|---|---|
| `verify.py` | 把 `annotations/` 列为**必需**目录 | `scripts/verify.py:6-11` |
| `init.py` | **创建** `wiki/annotations/` 目录 | `scripts/init.py:28` |
| `templates/{concept,decision,annotation}.md` | 用 `[[annotations/xxx]]` **链接**到该目录 | `templates/concept.md:67`、`decision.md:79`、`annotation.md:66` |
| `audit.py` PLACEHOLDER_PATTERNS | **不识别** `[[annotations/xxx]]` 为占位符，判为断链 | `scripts/audit.py:9-14` |

一个上游决策（删除 `annotations/` 目录概念）即可同时消除 V4、V5、N1。N2（`entities/` 缺失）是 init.py 与 schema 在另一可选目录上的平行漂移，同 PR 不同因。

### 集群 B — 链接身份模型缺失 → V2 + V3 + N11 + N3

四个缺陷共享同一前提缺失：脚本从未在"页面路径"与"wikilink 目标"之间建立规范等价关系。

- **V2** `audit.py:107-108` — `check_orphan_pages` 遇到 `index.md` 直接 `continue`，跳过了链收集，导致 index.md 的出链永不计入 `all_links`。
- **V3** `audit.py:114-119` — 孤儿判定比较 `page_stem`（如 `marginalia`）和带 `.md` 的相对路径（如 `concepts/marginalia.md`），但路径式 wikilink 目标是 `concepts/marginalia`（无 `.md`），三种形式互不匹配。
- **N11** `audit.py:117-119` — 孤儿 `suggested_action` 建议用裸 stem `[[marginalia]]`，与 `example/index.md` 的路径式约定 `[[concepts/marginalia]]` 不一致，修一处会强化另一处的不一致。
- **N3** `audit.py:53-58` — `resolve_wikilink` 只检查 4 个扁平候选，无递归/子目录搜索；裸链接 `[[marginalia]]` 永远找不到 `concepts/marginalia.md`。

统一修法：定义 `canonical_link(page_path, link_target) -> page_path | None`，所有检查经此归一化。

### 集群 C — `--root` 相对路径假设 → N5 + N9 + N6

三个 CLI/UX 缺陷都假设知识库布局固定为 `wiki/`：

- **N5** `audit.py:36-39,172-174` — `--no-skip` 帮助文本说"禁用所有跳过规则"，但 `-archive` 子串检查是无条件的，`--no-skip` 并未禁用它。
- **N9** `audit.py:32-40` — 当 `--root templates/` 时，`templates` 是根而非子部分，`should_skip_file` 永不触发 templates 跳过；扫描 templates/ 自身时报 7 个误报（已实测）。
- **N6** `audit.py:129` — `check_index_exists` 消息硬编码 `wiki/index.md`，无论 `--root` 是什么（已实测 `--root templates/` 仍提示 `wiki/index.md`）。

统一修法：跳过路径与索引路径都从 `--root` 派生，而非硬编码。

### 集群 D — KB 边界逃逸 → N4 + N7 + N15（假阴性）

`resolve_wikilink` 既无路径包含检查，又用 `root.parent` 作候选源，产生两类问题：

- **N4** `audit.py:52-58` — 无包含检查；`[[../../../etc/passwd]]` 在 Linux 上会因 `/etc/passwd` 存在而被判为有效 wikilink。
- **N7** `audit.py:55-56` — `root.parent` 候选在 KB 位于 repo 根时泄漏到知识库之外（`CHANGELOG.md`、`README.md` 等兄弟文件被误判为有效链接目标）。
- **N15（合成阶段补登，假阴性）** — 当用户在 repo 根运行 `audit.py --root .`，页面里写 `[[../sibling-project/notes]]` 时，`resolve_wikilink` 经 `root.parent` 找到兄弟项目文件并判为 OK，`check_broken_links` 漏报。这是**假阴性**（真实断链被掩盖），与 N4 的假阳性共享同一边界缺失。

统一修法：所有解析候选必须 `resolve()` 后落在 `root` 内（或显式声明的 `--external-kb-dirs` 内），否则视为断链。

### 其他独立缺陷

- **V1** `audit.py:43,51,71,95` — `set[str] | None` 是 PEP 604 语法，Python 3.9 运行时崩溃（实测 `TypeError`）。
- **N8** `verify.py:30-32` vs `audit.py:178` — 退出码不一致（verify 对缺失 root 返回 1，audit 返回 2）。
- **N10** `audit.py:59-67` — `--external-kb-dirs` 静默接受不存在的目录。
- **N12** `audit.py:147` — `severity_distribution` 初始化 `P3:0` 但无任何 issue 使用 P3，死代码。
- **N13** `audit.py:18` — `find_wikilinks` 正则在嵌套 `]]` 文本上理论会错切，当前语料未观察到。
- **N14（新发现）** `init.py:22` — 生成的 CLAUDE.md 片段仍在"完成实质工作后"要求运行 `audit.py`，但 `rules.md` v0.3.0 已将该触发移至"读取规则"（事件驱动）。init.py 与当前 rules.md 矛盾。

## Recommendations

按用户影响排序的修复优先级（典型 50–200 页知识库，Python 3.9）：

### P0 — 必须先修（阻塞安装或核心承诺失效）

1. **V1 — Python 3.9 兼容**（`scripts/audit.py:1`）：在文件首行加 `from __future__ import annotations`，使 PEP 604 注解在 3.9+ 惰性求值。一行修复，解除硬阻塞。
2. **集群 A — 删除 `annotations/` 目录概念**（4 处）：
   - `scripts/verify.py:6-11`：`REQUIRED_DIRS` 收窄为 `["concepts", "decisions"]`（`comparisons/` 改可选，`annotations/` 删除）。
   - `scripts/init.py:25-30`：`DIRECTORIES` 删除 `"wiki/annotations"`；可选补 `"wiki/entities"`（修 N2）。
   - `templates/concept.md:67`、`decision.md:79`、`annotation.md:66`：删除 `- [[annotations/xxx]]: ...` 行。
   - `scripts/audit.py:9-14`：可选给 `PLACEHOLDER_PATTERNS` 加 `annotations?/` 模式作为过渡防御（若仍有用户旧模板残留）。
3. **集群 B — 统一链接身份模型**（`scripts/audit.py:95-119, 51-68`）：
   - `check_orphan_pages`：先读所有文件的 wikilinks（含 `index.md`），再仅把 `index.md` 排除出孤儿候选；页面身份用去 `.md` 后缀的相对路径，与路径式 wikilink 对齐。
   - `resolve_wikilink`：增加子目录递归搜索（修 N3），使裸 `[[marginalia]]` 能找到 `concepts/marginalia.md`。
   - 孤儿 `suggested_action` 改用路径式 `[[concepts/marginalia]]`（修 N11）。

### P1 — 应尽快修（文档与边界完整性）

4. **N14 — init.py 片段对齐 rules.md v0.3.0**（`scripts/init.py:6-23`）：把"完成实质工作后 - 运行 audit.py"改为"读取规则 - 发现异常时提醒运行 audit.py"，与 `schema/rules.md:10` 一致。
5. **集群 D — KB 边界包含检查**（`scripts/audit.py:51-68`）：所有 `resolve_wikilink` 候选 `resolve()` 后必须落在 `root`（或 `--external-kb-dirs`）内，否则视为断链；移除或限制 `root.parent` 候选（修 N4、N7、N15）。

### P2 — 可延后（CLI/UX 与小瑕疵）

6. **集群 C — `--root` 派生路径**（`scripts/audit.py:32-40,129,172-174`）：跳过目录名与索引消息从 `--root` 派生；`--no-skip` 真正禁用 `-archive` 子串检查（修 N5、N6、N9）。
7. **N8 — 退出码对齐**（`scripts/verify.py:30-48`）：缺失 root 返回 2，结构与 audit.py 一致。
8. **N10 — `--external-kb-dirs` 校验**（`scripts/audit.py:59-67`）：不存在的目录给出 warning。
9. **N12 — 删除死代码 `P3` 槽**（`scripts/audit.py:147`）。
10. **N2 — init.py 补 `wiki/entities/`**（`scripts/init.py:25-30`）。
11. **N13 — 正则健壮性**：低优先，当前语料无触发。

## Preventive Measures

1. **Schema 作为单一事实源**。把 `verify.py` 的 `REQUIRED_DIRS`、`init.py` 的 `DIRECTORIES`、`audit.py` 的跳过目录与占位符模式集中到一个由 `schema/node-types.md` 派生的契约（JSON/YAML），三个脚本共同引用。今天它们是三个文件里的 Python 字面量，漂移不可避免——本次 18 个缺陷中有 7 个源于此。

2. **回归基线测试**。把 `audit.py --root example/` 与 `verify.py --root example/` 固化为 CI 断言（期望 `P0:P1:P2 = 0:0:0` 与 `Verification passed`）。`archive/GPT54/tests/regression/test_audit_snapshot.py` 已有快照测试范式可借鉴。当前仓库 `tests/` 为空，是本次误报长期未被发现的主因。

3. **跨脚本一致性表**。在 `CONTRIBUTING.md` 增加一张表，列明 schema ↔ verify.py ↔ init.py ↔ templates 的不变量；任何 schema 新增类型（如 `entities`、`reports`、`projects`，见 `docs/feedback/openclaw-field-report-2026-05-15.md`）必须四处同步更新。

4. **明确 Python 最低版本**。`from __future__ import annotations` 让脚本在 3.9+ 可运行，但应在 `README.md` 标注 `python_requires>=3.9`，避免用户在更老版本上困惑。

5. **`audit.py --check-self` 模式**。新增一个 flag，强制对仓库自带 `example/` 运行审计并以非零退出码反映任何回归——把"示例仓库自身触发误报"这类问题变成 CI 失败而非用户报告。

6. **`resolve_wikilink` 边界与递归作为独立单测**。N3（无递归）、N4/N7/N15（无边界）都集中在同一个函数；为它写"裸链接能找到子目录页"、"`..` 逃逸被拒"、"`root.parent` 不参与解析"三个单测，防止回归。

7. **`init.py` 生成的 CLAUDE.md 片段纳入 schema 版本同步**。N14 表明 init.py 的模板段落与 rules.md 各自演进；片段应从 `schema/rules.md` 生成或在 CI 校验其与 rules.md 一致。
