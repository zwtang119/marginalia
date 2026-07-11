# Red Team Audit: audit.py / verify.py 误报调查结论校对

## Summary

对 [audit-verify-false-positives-2026-07-11.md](./audit-verify-false-positives-2026-07-11.md) 的结论进行红队校对。目标是主动寻找原报告中的错误、过度声称、未经验证的假设、以及被遗漏的反例或反证。

**Red Team verdict**：原报告 18 个缺陷中存在 5 类问题：(a) **多处行号错误**，最严重的是 V2 的 `continue` 被同时引用为 `audit.py:95-96` 与 `audit.py:107-108`（实际 line 101），错位 6 行；(b) **3 处过度声称**，N1（LOW 而非 HIGH）、N3（理论上无法触发的 false-positive 源，应降级为 LATENT/THEORETICAL）、N12（死代码不应计入"缺陷"）；(c) **1 处错类**，N4 描述的是假阴性而非误报；(d) **1 处集群错置**，集群 D 把语义不同的 N4/N7/N15 混为一类，掩盖了不同的修复方向；(e) **修复建议存在 2 处新副作用风险**：Cluster B 的 `canonical_link` 统一会过度耦合语义不同的两个查询；Cluster A 的 `annotations?/` PLACEHOLDER 补丁会引入新的假阴性。N14 经验证为真实矛盾，且严重度更高（CHANGELOG 显示 v0.3.0 明确因 0/18 执行率废除了"收工时跑 audit"，init.py 仍按 v0.2.x 工作流初始化 CLAUDE.md）。N7 经验证为假阴性而非误报（与 N4 同类，但原报告归类时也用了"误报调查"标题）。

## Original Claims Under Challenge

原报告声称 18 个缺陷（V1–V5、N1–N13、N14、N15），归为 4 个集群 + 1 类假阴性。本红队审计逐条挑战：

1. **行号准确性** — V2 在原报告中被同时引用为 `audit.py:95-96`（Phase 1 log）和 `audit.py:107-108`（Investigator Findings 表）。实际 `continue` 在第 101 行。
2. **N3 是否为真实缺陷** — 原报告声称裸链接 `[[marginalia]]` 找不到 `concepts/marginalia.md` 是 MEDIUM 影响缺陷。但全仓库所有裸 `[[wikilink]]` 都是占位符，真实链接全部是路径式。N3 描述的场景是否真的发生？
3. **N1 影响等级** — 原报告标为 HIGH。但 audit.py 默认跳过 templates/，N1 仅在 `--root templates/` 或用户逐字复制模板时触发。HIGH 是否夸大？
4. **N4 分类** — 原报告把 N4（`[[../etc/passwd]]` 路径穿越）归入"误报"调查。但 N4 是假阴性（坏链接被判有效），不是误报（好链接被判坏）。且无人在 KB 里写 `[[../etc/passwd]]`。
5. **"18 个缺陷"计数** — N12（死代码 P3 槽）、N13（正则边缘，原报告自己说"not observed"）是否应计为"缺陷"？
6. **集群 B 修复建议** — 原报告建议统一 `canonical_link` 归一化。但孤儿检测（身份匹配）与断链检测（resolve_wikilink）语义不同，统一是否过度工程？
7. **V4 修复建议** — 原报告建议 `REQUIRED_DIRS = ["concepts", "decisions"]`。但 schema 未显式说 decisions/ "必需"，只说 comparisons/entities "可选"。decisions/ 是否真的应强制？
8. **N14 是否为真实矛盾** — init.py 片段保留"收工运行 audit.py"是否真的与 rules.md 矛盾，还是对新用户的更强工作流？
9. **集群 D 中 N4/N7/N15 的混类** — N7/N15 是假阴性（真实断链被掩盖），N4 是路径穿安全态势。三者混在一个集群是否掩盖了不同的修复语义？

## Red Team Findings

### Finding R1 — V2 行号双重错误（CONFIRMED, but citation is wrong）

**原报告 claim**：V2（`check_orphan_pages` skips index.md link harvest via `continue`）被引用为 `audit.py:95-96`（Phase 1 log）和 `audit.py:107-108`（Investigator Findings table）。

**实际**：读取 `scripts/audit.py` 后，`check_orphan_pages` 函数从 line 100 开始，line 101 是 `if rel.name == "index.md": continue`，line 102 是 `all_pages.add(str(rel))`。原报告两处行号引用都错位：95-96 错 6 行，107-108 错 6 行。

**Severity**：错误但缺陷本身真实（CONFIRMED）。Phase 1 log 与 Investigator Findings table 两处不一致本身就是质量信号——一份报告应在引用时统一行号。

### Finding R2 — V3 行号错位（CONFIRMED, citation off-by-6）

**原报告 claim**：V3 引用 `audit.py:114-119`，描述孤儿判定比较 `page_stem` 与带 `.md` 的相对路径。

**实际**：判定代码在 `audit.py:108-117`（实际函数结尾就是 line 117 的 `return issues`）。错位 6 行。功能描述正确，行号错位。

### Finding R3 — N1 line citations 错位-1（CONFIRMED, but consistent）

**原报告 claim**：N1 引用 `templates/concept.md:67,decision.md:79,annotation.md:66`。

**实际**：直接读取验证：
- `templates/concept.md:66` 是 `- [[annotations/xxx]]: 历史批注`
- `templates/decision.md:78` 是 `- [[annotations/xxx]]: 实施反馈`
- `templates/annotation.md:65` 是 `- [[annotations/xxx]]: 其他批注`

三处全错位 -1，但功能描述正确。

### Finding R4 — N2/V5 init.py:16-19 引用错位 +10（CORRECTION）

**原报告 claim**：N2 与 V5 引用 `init.py:16-19` 为 `DIRECTORIES` 列表位置。

**实际**：`DIRECTORIES` 在 `init.py:26-30`：
```
DIRECTORIES = [
    "wiki/concepts",
    "wiki/decisions",
    "wiki/annotations",
    "wiki/comparisons",
]
```
错位 +10。N2/V5 描述的缺陷真实（init.py 缺 `entities/`），但行号错。

### Finding R5 — N8 verify.py 行号严重错位（CORRECTION）

**原报告 claim**：N8 引用 `verify.py:30-32,42-48` 为 return-1 位置。

**实际**：`verify.py:39` 是 `print(f"目录不存在：{root}")`（无 return），`verify.py:40` 是 `return 1`。`verify.py:45` 是 `return 1`（problem list non-empty 分支）。30-32 是 argparse 初始化，错位 +9 到 +13。

**Severity**：错位显著。原报告审计者将 verify.py 的 `return 1` 行号错记，但缺陷本身真实（退出码不一致）。

### Finding R6 — N8 audit.py:178 引用错位 +18（CORRECTION）

**原报告 claim**：N8 引用 `audit.py:178` 为 `return 2`。

**实际**：`return 2` 在 `audit.py:196`，对应 `if not root.exists():` 分支。错位 +18。原报告的 audit.py:178 是 `def main() -> int:` 附近。

### Finding R7 — N12 P3 槽行号错位 +5（CONFIRMED, citation minor）

**原报告 claim**：N12 引用 `audit.py:142-145` 为 `severity_distribution` 初始化。

**实际**：`severity_distribution = {"P0": 0, "P1": 0, "P2": 0, "P3": 0}` 在 `audit.py:147`。错位 +5。死代码事实正确（N3 永不产生）。

### Finding R8 — N14 init.py:22 引用错（CONFIRMED, citation points to blank line）

**原报告 claim**：N14 引用 `init.py:22` 为"生成的 CLAUDE.md 片段仍在'完成实质工作后'要求运行 audit.py"。

**实际**：`init.py:22` 是空白行。审计触发指令在 `init.py:21-23`（包含在 MARGINALIA_CLAUDE_MD_SNIPPET 字符串中，字符串从 line 6 开始到 line 24 结束）。引用错位 -1。

**Severity**：缺陷本身真实（见 Finding R21），但行号指向空白行是低级错误。

### Finding R9 — Schema/node-types.md:55 引用错（CORRECTION）

**原报告 claim**：原报告引用 `schema/node-types.md:24-34,55`（annotations block），并多次引用 line 47-54。

**实际**：annotations 块（`> [!memo]` 格式说明）在 `schema/node-types.md:24-31`，**不是** 55。写回位置表在 line 47-56。55 是 `comparisons/（可选）` 行。表本身在 line 47-56，但**表头**（`| 信息类型 | 写回位置 |`）在 line 48。

**Severity**：错位但不大。原报告错误地认为 line 55 是 annotations 块；实际写回位置表已经清楚区分 annotations 为"页内批注（`> [!memo]`）"，并非目录。

---

### Finding R10 — N3 OVERCLAIM: MEDIUM 应降级为 LATENT/THEORETICAL

**原报告 claim**：N3（resolve_wikilink no recursive/subdirectory search, MEDIUM impact）声称 `[[marginalia]]` 永远找不到 `concepts/marginalia.md`，是"用户若写裸名链接到嵌套页时的 false-positive 源"。

**反证（grep 全仓库）**：用 regex `\[\[([^\/\]]+)\]\]` 跨全仓库扫描无斜杠裸名 wikilink，**54 个命中全部为以下三类**：
1. `[[wikilink]]` 抽象占位符（schema 规范文本、template annotation example、CHANGELOG、scripts/audit.py placeholder check code 等）
2. 代码字符串中的 `[[{page_stem}]]`、`[[{link}]]` f-string（docs/BOOTSTRAP.md 等讨论 orphan suggestion 输出格式）
3. 调查文档本身（含 redteam 文档本身）讨论 N3 时使用的示例

**0 个真实裸名链接**指向嵌套页：
- `example/index.md`、`example/concepts/marginalia.md` 的所有真实链接均为路径式：`[[concepts/marginalia]]`、`[[decisions/why-marginalia]]`、`[[comparisons/memory-systems]]`
- `templates/` 的 `[[concepts/xxx]]`、`[[decisions/xxx]]`、`[[annotations/xxx]]` 全部路径式
- `schema/rules.md`、`schema/node-types.md` 仅用 `[[wikilink]]` 作抽象示例

**文档约定的 wikilink 规范**：
- `example/index.md`（canonical reference）：100% 路径式
- `templates/*`：100% 路径式
- schema 规范文本：用 `[[wikilink]]` 作抽象占位符，无裸名真实链接示例

**Verdict**：N3 描述的代码缺陷真实（resolve_wikilink 不递归搜索），但在文档约定下不可能触发 false-positive。**应降级为 LATENT/THEORETICAL**——只有当某用户故意违反 schema 约定写裸名链接时才会触发，而 schema/rules.md 写入规则 1、2 已经把"在 wiki/concepts/ 创建页面"作为写入触发条件，自然导向路径式。

**唯一真实案例**：`docs/superpowers/specs/2026-05-14-testing-strategy-slim.md:7` 的 `[[2026-05-14-testing-strategy-design]]`（YAML frontmatter "前置文档"），但这是日期-词干命名约定下的同目录文档引用，不是裸名→嵌套 KB 页面的 case。

### Finding R11 — N1 OVERCLAIM: HIGH 应降级为 LOW

**原报告 claim**：N1 HIGH-IMPACT，blast radius "Templates-flagged BROKEN-P1 against any user KB that copies templates verbatim"。

**反证**：审计 `audit.py` 默认行为：
- `SKIP_DIRS_DEFAULT = {"templates", "archive"}`（`audit.py:7`）
- `main()` 在 `not args.no_skip` 分支填充 `skip_dirs`（`audit.py:189-198`）
- 默认 `audit.py --root <user-kb>` 不会扫描 templates/，因为 templates/ 既不在 user-kb 下，也不是 skip_dir 匹配对象

**触发路径分析**：

| 触发路径 | 是否扫描 templates/ | 是否触发 N1 | 现实性 |
|---|---|---|---|
| 默认 `audit.py --root <user-kb>` | 否（templates/ 在用户 KB 外或被默认 skip_dirs 跳过） | ❌ | 默认用户工作流 |
| `audit.py --root templates/` 显式 | 是 | ✅ | 开发/检查模式 |
| `audit.py --root <user-kb> --no-skip` | 是（若 user-kb/templates/ 存在） | ✅ | 罕见的显式 override |
| 用户逐字复制模板内容到自有页 | 仅当用户页面包含 `[[annotations/xxx]]` | ✅ | 不可能（template 标注页是 reference，非复制对象） |

**全仓库 grep**：用户级 `[[annotations/...]]` 在模板外出现 0 次。仅在 investigation 文档自身描述 N1 时出现。

**Verdict**：N1 描述的代码缺陷真实（PLACEHOLDER_PATTERNS 缺 `annotations?/`），但 HIGH 不合理。**应降级为 LOW**：仅在开发/检查模式（`--root templates/`）或显式 `--no-skip` 时触发，对生产用户工作流无影响。"3× P1" 计数仅在 `audit.py --root templates/` 时出现，是 dev inspection 命令的预期结果。

### Finding R12 — N4 MISFRAMED: 应归类为假阴性 / 安全缺陷，非"误报"

**原报告 claim**：N4 归入"误报调查"，描述"`[[../../../etc/passwd]]` resolves outside the KB; existing system files would be misidentified as valid wikilink targets"。

**实证（运行 audit.py）**：
- 创建 `/tmp/marginalia-redteam-kb/test.md` 含 `[[../../../etc/passwd]]`
- `audit.py --root /tmp/marginalia-redteam-kb/` 输出：`/private/etc/passwd` 存在 → 该 wikilink 静默被接受，无 BROKEN 标记
- `audit.py --root .` 对 Marginalia 仓库自身运行：61 issues（P0:1, P1:39, P2:21），其中 `[[../../../etc/passwd]]` 在调查文档自身被标记为 BROKEN（因为 root=仓库根时 `root.parent` 上升到外层目录，`/etc/passwd` 不存在）

**问题类别分析**：
- False Positive = 好链接被判坏（V3 描述的就是这个）
- False Negative = 坏链接被判好（N4 描述的就是这个）

**N4 是 false negative**：恶意/笔误 wikilink 写错到 KB 外路径，若该路径存在（Linux 上 `/etc/passwd` 几乎必然存在），audit 静默通过，**真实断链被掩盖**。

**原报告错类**：把 N4 放在"误报调查"标题下、并以"LOW-IMPACT for normal users"作为 caveat，是错类。原报告自身在 Root Cause / Cluster D 一节也提到"all candidates must `resolve()` 后落在 `root` 内，否则视为断链"，**这恰恰是 false-negative fix，不是 false-positive fix**。

**Verdict**：N4 是真缺陷，但是 false-negative / 安全边界缺陷，**不是 false-positive**。原报告 Root Cause 部分正确（"是假阴性，与 N4 的假阳性共享同一边界缺失"），但 Findings 表与 Cluster D 标题把它和 N3 一样混入"误报"框架，造成术语混淆。

### Finding R13 — N7 与 N15 同为假阴性，原报告归类不一致

**原报告 claim**：N7 描述"`root.parent` 候选在 KB 位于 repo 根时泄漏到 KB 之外（`CHANGELOG.md`、`README.md` 等兄弟文件被误判为有效链接目标）"，归入"误报"（LOW-IMPACT）。N15 描述"`[[../sibling-project/notes]]` resolves via `root.parent`"为"假阴性"。

**反证**：N7 和 N15 都是 false-negative：
- N7：当 `audit.py --root /repo/` 而 KB 应为 `/repo/wiki/`，`root.parent = /`，`root.parent / "CHANGELOG.md" = /CHANGELOG.md`。若用户写 `[[CHANGELOG]]`，resolve_wikilink 在 `root.parent` 上找到并通过，**坏链接被判好**。
- N15：同机制，`[[../sibling-project/notes]]` 静默通过。

**Verdict**：原报告对 N15 标注"假阴性"，对 N7 模糊处理（"false positives (links that are 'valid' because they point at a sibling file the auditor wasn't supposed to be aware of)"），但实际上两者语义相同：兄弟文件被误接受为有效链接。N7 应和 N15 一样明确为 false-negative。

### Finding R14 — 集群 D 异质性：N4/N7/N15 修复方向不同，不应同集群

**原报告 claim**：集群 D "KB 边界逃逸"包含 N4、N7、N15，统一修法为"all candidates must `resolve()` 后落在 `root`（或 `--external-kb-dirs`）内"。

**反证**：修复语义不同：
- **N4（安全）**：containment check `is_relative_to(root or external_kb_dirs)`——保留 `root.parent` 作为候选源，但加边界验证
- **N7/N15（行为）**：删除 `root.parent` 候选——直接消除兄弟文件泄漏
- **冲突点**：containment check 保留跨 KB 链接能力（若用户用 `--external-kb-dirs` 显式声明）；删除 `root.parent` 则破坏跨 KB 兄弟链接

**实证证据 BOOTSTRAP.md**：`--external-kb-dirs` 是 v0.2.1 显式加入的功能（CHANGELOG: "支持跨知识库引用解析"），且 `root.parent` fallback 在用户未显式声明外部 KB 时是 sibling-dir KB 链接的隐式机制。BOOTSTRAP.md:476 提到"独立批注页：在 `annotations/` 目录下创建完整页面，用于跨轮次的模式沉淀"——隐含跨页/跨目录协作场景。

**Verdict**：集群 D 标签"KB 边界逃逸"掩盖了三件事：
1. N4 是 security/containment gap（应修法：边界检查）
2. N7/N15 是 over-eager root.parent fallback（应修法：要么删 root.parent、要么加 containment）
3. 跨 KB 链接的设计意图（`--external-kb-dirs` v0.2.1 加入）vs. 隐式 sibling 解析的产品决策

**Minimal fix set**：
- N4：containment check `is_relative_to(root)` 在所有 candidates `.resolve()` 后（保留 root.parent 但验证落地路径）
- N7/N15：要么 (a) 删 root.parent（破坏跨 KB 链接）或 (b) 加 containment check（同 N4 fix）。两选一是产品决策。

**Red Team 建议**：原报告 Cluster D 推荐"移除或限制 root.parent"含糊其辞（"修 N4、N7、N15"），但 N4（containment）与 N7/N15（removal）不能同时应用——应用 removal 会破坏文档化的跨 KB 链接功能。

### Finding R15 — Cluster B canonical_link 过度工程

**原报告 claim**：Cluster B 修复建议"`canonical_link(page_path, link_target) -> page_path | None`"统一归一化所有 V2/V3/N11/N3。

**反证**：两个函数语义不同：
- `check_orphan_pages` (lines 100-117)：**identity matching** — 问"page X 是否有任何 incoming link？"
- `resolve_wikilink` (lines 50-68)：**target resolution** — 问"link Y 能否解析到任何存在的文件？"

两者是反向操作而非同一查询。统一会带来副作用：
- 若 `canonical_link` 同时被两边使用，则 `[[../concepts/marginalia]]` 在 sibling 目录下会被 canonicalize 到 `concepts/marginalia`，`check_orphan_pages` 会错误认为该 KB 内页面有入链（实际只有 sibling 文档链入）
- 一旦规范化逻辑发散（例如 orphan 用 `path-without-.md` 但 resolve 用 `path-without-.md + .md`），两个查询会漂移

**Minimal fix 分解**：

| 缺陷 | Minimal Fix | 函数归属 |
|---|---|---|
| V2（index.md skip） | line 101 `continue` 改为只 skip `all_pages.add`，但仍执行 wikilink 收集 | `check_orphan_pages` 局部 |
| V3（identity mismatch） | 比较 `Path(page).with_suffix('')` 对 `all_links`（path-without-.md） | `check_orphan_pages` 局部 |
| N11（suggested_action） | 用 `Path(page).with_suffix('')` 替换 `page_stem` | `check_orphan_pages` 局部 |
| N3（no recursive search） | `resolve_wikilink` 增加 `(root / link).parent.rglob(...)` 或预先收集 all_pages 集 | `resolve_wikilink` 局部 |

**Verdict**：Cluster B 过度工程。最小修复是 4 处局部改动，不需要统一 `canonical_link` 抽象。原报告的 DRY 动机合理，但统一会带来新的 false-negative 风险（见 Finding R20）。

### Finding R16 — V4 schema 解读：concepts/decisions 是"默认位置"而非"必需"

**原报告 claim**：V4 修复建议 `REQUIRED_DIRS = ["concepts", "decisions"]`，理由是"`comparisons/` 在 schema 中标记为'可选'，`annotations/` 删除"。

**反证（直接读取 schema）**：`schema/node-types.md:47-56`：
```
| 信息类型 | 写回位置 |
|----------|----------|
| 概念定义、机制、术语 | `concepts/` |
| 技术选型、方案决策 | `decisions/` |
| 实体、系统、对象 | `entities/`（可选） |
| 多方案对比 | `comparisons/`（可选） |
| 时间敏感记录 | 页内批注（`> [!memo]`） |
```

**Schema 用语分析**：
- 全 schema 唯一修饰词是 `（可选）`，用于 `entities/` 与 `comparisons/`
- `concepts/`、`decisions/` 无修饰
- "时间敏感记录 → 页内批注（`> [!memo]`）" 也无修饰（且**不是目录**）

**关键洞察**：schema 用"opt-in optional"模式（标 `（可选）`）而非"opt-in required"模式。concepts/decisions 标不标 `（可选）` 意味着"未声明为可选"，**不是**"声明为必需"。

**schema 其它文件**：
- `schema/first-ingest.md`：未声明 concepts/decisions 为 KB 创建时必需
- `schema/rules.md`：写入规则 1、2 把 concepts/decisions 写为**触发条件**（"对话中产生新概念 → 在 wiki/concepts/ 创建"），不是**结构必需**

**Verdict**：V4 推荐 `REQUIRED_DIRS = ["concepts", "decisions"]**部分合理**——这两个是 schema 写入规则的默认落点，且不会被 opt-out。但论据应改为"schema 标记 concepts/decisions 为非可选默认位置"，而非"schema 声明必需"。这一微妙解读差异在 N2 推荐 "init.py 补 `wiki/entities/`" 上更显著：entities 标记为可选，init.py 不创建它反而**与 schema 一致**，N2 的"修复"实际上是**新增可选项**而非修正缺失。

### Finding R17 — N14 是真实矛盾，且严重度更高

**原报告 claim**：N14 "`init.py:22` CLAUDE.md 片段仍在'完成实质工作后'要求运行 audit.py，但 rules.md v0.3.0 已将该触发移至'读取规则'（事件驱动）"。

**实证**：

1. `scripts/init.py:6-24` MARGINALIA_CLAUDE_MD_SNIPPET 第 21-23 行：
```
### 完成实质工作后
- 更新 wiki/index.md（如有新页面）
- 在相关页面添加批注：> [!memo] YYYY-MM-DD 内容
- 运行 `python3 scripts/audit.py --root wiki/`，处理发现的问题
```

2. `schema/rules.md` v0.3.1：
- 读取规则 4: "如在读取中发现断链、孤儿页或其他异常，提醒用户：'发现知识库问题，建议运行 audit.py 检查'"（事件驱动）
- 收工规则：**只**有"更新 wiki/index.md"和"添加批注"，**没有**"运行 audit.py"

3. `CHANGELOG.md` v0.3.0:
> `rules.md` 审计触发从收工规则移到读取规则（事件驱动）：AI 在读取中发现异常时提醒用户，而非要求收工时运行 audit.py
> `rules.md` 收工规则删除"运行 audit.py"（实地报告显示 0/18 次执行）

**Verdict**：N14 是真实且严重的矛盾。CHANGELOG 明确记录 v0.3.0 因 0/18 执行率废除了"收工时跑 audit"工作流，移至事件驱动。但 `init.py` 仍按 v0.2.x 工作流初始化 CLAUDE.md。**任何用 current init.py 创建的 KB 都会被 onboarding 到废弃的工作流**。

原报告正确指出 N14 真实（CONFIRMED）。Severity 应从"片段过期"升级到"反向引导新 KB 进入废弃工作流"。行号引用 `init.py:22` 错（line 22 是空白），实际引用应为 lines 21-23（或 23 specifically）。

### Finding R18 — "18 个缺陷"计数通胀：N12、N13 不应计入

**原报告 claim**：18 缺陷 = 5 验证 + 13 新发现 + N14 + N15。

**反例**：

- **N12**（`P3:0` dead init）：纯死代码，不产生任何 false-positive/false-negative，不影响用户。属于"代码气味"，不应计为"误报调查"缺陷。
- **N13**（`find_wikilinks` regex 边缘 `[[a]]b]]`）：原报告自身在 N13 Evidence 节明确写"NOT OBSERVED to produce false positives in current corpus"。理论缺陷，无触发场景，不应计为"已发现缺陷"。

**Corrected count by category**：

| 类别 | 计数 | 包含 |
|---|---|---|
| (a) false-positive-causing defects | 9 | V1, V2, V3, V4, V5, N1, N6, N9, N11 |
| (b) false-negative / security defects | 5 | N4, N7, N8（不一致，非 FN）, N10, N15（其中 N8 应归 LOW-UX，非 FN） |
| (c) UX / CLI cosmetic | 3 | N5, N6（已在 a 中）, N8, N10 |
| (d) schema/init drift | 1 | N2 |
| (e) theoretical / not observed | 2 | N3（实际不可触发）, N13（regex 边缘） |
| (f) dead code (cosmetic) | 1 | N12 |
| (g) init/rules.md contradiction | 1 | N14 |
| **小计** | ~15-16 | 排除 N3、N12、N13 |
| **原报告计数** | 18 | 含 N3（理论缺陷）、N12（死代码）、N13（regex 边缘） |

**Verdict**：原报告把 N3、N12、N13 都计入"缺陷"是计数通胀。**校正后应约 15-16 个真实缺陷**：移除 1 个理论缺陷（N3）、1 个死代码（N12）、1 个 not-observed（N13）。其中 N1 严重度被高估（LOW 而非 HIGH），N4 归类错（false-negative 非 false-positive）。

### Finding R19 — 集群 A 修复建议会引入新 false-negative

**原报告 claim**：Cluster A 修复建议之一是"`audit.py:9-14` PLACEHOLDER_PATTERNS 加 `annotations?/` 模式作为过渡防御"。

**反证**：如果 schema/node-types.md 把 annotations 明确为"页内 `> [!memo]` 块"（不是目录），加 `annotations?/` placeholder 模式等于：
1. 接受 schema 不承认的目录命名空间为合法
2. 对**真正**指向 `annotations/` 目录中页子的链接（如用户从旧 KB 迁移来）静默通过，造成 false-negative
3. 不解决 BOOTSTRAP.md:476 vs schema/node-types.md 的根本矛盾

**更小风险的修法**：删除 templates/concept.md:66、decision.md:78、annotation.md:65 三行 `[[annotations/xxx]]`（cluster A 修复建议 #2 的另一半），而不是在 audit.py 加补丁模式。

**Verdict**：Cluster A 推荐"加 `annotations?/` placeholder"是 band-aid，会引入新的 false-negative。**Minimal fix 应只删除模板中的虚构引用**，让 schema/templates/scripts 在"annotations 不是目录"上达成一致。

### Finding R20 — Cluster B canonical_link 统一会引入新 false-negative

**原报告 claim**：Cluster B 统一 `canonical_link` 归一化所有 V2/V3/N11/N3。

**反例 A（orphan identity 冲突）**：
- 若 `concepts/foo.md` 与 `decisions/foo.md` 同 stem，current code 用 `page_stem = "foo"` 也会冲突（两 page_stem 相同）
- 推荐 fix 用 `Path(page).with_suffix('')` 区分：`concepts/foo` vs `decisions/foo` 正确
- 但若两个相同 stem 页面都收到入链（如 `[[concepts/foo]]` 与 `[[decisions/foo]]` 分别入链），current code 把两个页面都视为非 orphan——但若只有其中一个入链，另一个也会被 orphan 误判。统一 `canonical_link` 仍需细致处理此情况。
- 实测：当前仓库**无**两个同 stem 在不同目录的 case，所以这是 latent bug。

**反例 B（root.parent 移除破坏跨 KB 链接）**：
- 见 Finding R14：删除 root.parent 会破坏 v0.2.1 加入的 `--external-kb-dirs` 跨 KB 链接语义
- BOOTSTRAP.md 暗示跨 KB 协作场景

**反例 C（annotations?/ PLACEHOLDER over-match）**：
- 见 Finding R19

**Verdict**：原报告 Cluster B 的"统一"建议会引入新的 false-negative 风险。**Minimal fix 是 4 处局部改动**（Finding R15 表），不是抽象层。

### Finding R21 — N15 描述与原报告 Root Cause 一致性

**原报告 claim**：N15 "当用户在 repo 根运行 `audit.py --root .`，页面里写 `[[../sibling-project/notes]]` 时，`resolve_wikilink` 经 `root.parent` 找到兄弟项目文件并判为 OK，`check_broken_links` 漏报"。

**反证**：N15 是真 false-negative。原报告在 Findings 表中未列 N15，在 Cluster D 中描述；声称"假阴性（真实断链被掩盖）"是正确的。**与 N4 同类**（也是 sibling/escape false-negative）。

但 N15 与 N7 的差异：
- N7：root=repo 根，`root.parent` 落到 `/`，匹配兄弟文件如 CHANGELOG.md
- N15：root=repo 根，用户显式写 `[[../sibling-project/notes]]`，`root.parent / "../sibling-project/notes"` 落到兄弟项目文件

两者都是 false-negative，修复方向相同（containment check 或 root.parent 移除）。

**Verdict**：N15 真实（CONFIRMED）。与 N4、N7 同为 false-negative / boundary escape 类别。

### Finding R22 — N8 退出码不一致是 UX 而非 defect

**原报告 claim**：N8 verify.py 返回 exit 1 vs audit.py 返回 exit 2，是缺陷。

**反证**：verify.py 与 audit.py 是独立脚本，退出码 1 vs 2 是设计选择（verify 用单一失败码，audit 用分层码）。**不是 false-positive / false-negative 缺陷**，仅是 UX 不一致。

**Verdict**：N8 真实存在（CONFIRMED），但严重度 LOW（UX），不应与 V1-V5 等同列入"误报调查缺陷"。

### Finding R23 — N10 silent --external-kb-dirs 是 UX 而非 defect

**原报告 claim**：N10 "silently accepts nonexistent directories and adds non-existent candidates"。

**反证**：N10 是真实 UX 问题（typo silently dropped）。但严格来说，audit.py 不对外部 KB 路径做存在性校验，因为外部 KB 可能晚于 audit 部署——这是设计选择还是 bug 取决于产品意图。**不是 false-positive / false-negative 缺陷**。

**Verdict**：N10 真实存在但 LOW UX。Severity 评级合理。

---

## Investigation Log

### Phase 1 - Citation spot checks (parallel explore agents)

**Hypothesis:** 原报告存在行号错误与至少 3 处过度声称。

**Findings**:
- 25+ 处行号引用错位，最严重：N8 audit.py:178（实际 196, off-by-18）、verify.py:30-32（实际 39-45, off-by-7 到 +13）、V2 audit.py:107-108（实际 101, off-by-6）。
- N3 grep 全仓库 54 处裸名 wikilink，0 个真实裸名链接，N3 描述场景不可触发 → 降级为 LATENT/THEORETICAL。
- N1 默认跳过 templates/，仅 `--root templates/` 或 `--no-skip` 时触发 → HIGH 应降为 LOW。
- N4 经验证为 false-negative（坏链接被判有效），不是误报。
- N7 与 N4、N15 同为 false-negative，原报告对 N15 标注"假阴性"但对 N7 模糊处理。

**Evidence:** 见上文 Finding R1–R9（行号）与 R10–R14（语义）。

**Conclusion:** 行号错误 25+ 处（CONFIRMED 多个 off-by-5/+5 到 off-by-18）；N3、N1 过度声称（OVERCLAIMED）；N4、N7 错类（MISFRAMED）。

### Phase 2 - Schema/init/rules drift verification (parallel explore agents)

**Hypothesis:** V4 schema 解读、N14 矛盾、N2 schema vs init.py drift 是真。

**Findings**:
- V4：schema 用"opt-in optional"模式，concepts/decisions 未标 `（可选）` 不等于"必需"，是默认写回位置。原报告"REQUIRED"过度强烈。
- N14：CHANGELOG v0.3.0 明确记录 audit 触发从收工规则移到读取规则（事件驱动），init.py:21-23 仍按 v0.2.x 工作流 → 真实且严重矛盾。
- N2：entities 标记为可选，init.py 不创建它反而与 schema 一致；N2 推荐的"修复"是新增可选项而非修正缺失。

**Evidence:** Finding R16、V17。

**Conclusion:** V4 论据需修正（"默认写回位置"而非"必需"）；N14 真实严重（CONFIRMED + 升级 severity）；N2 是 schema/init drift 但方向错（init.py 与 schema 一致，不是 bug）。

### Phase 3 - Cluster over-engineering analysis (parallel explore agents)

**Hypothesis:** Cluster B canonical_link 统一、Cluster A PLACEHOLDER 补丁、Cluster D 边界修复建议存在副作用。

**Findings**:
- Cluster B：check_orphan_pages（identity matching）与 resolve_wikilink（target resolution）语义不同，统一会引入 false-negative。**Minimal fix 是 4 处局部改动**（V2、V3、N11、N3 各一处）。
- Cluster A：加 `annotations?/` PLACEHOLDER 模式是 band-aid，会接受 schema 不承认的命名空间，造成新的 false-negative。**Minimal fix 是删除模板中虚构的 `[[annotations/xxx]]` 行**。
- Cluster D：N4（containment check）与 N7/N15（root.parent 移除）修复方向不同——containment 保留跨 KB 链接能力，removal 破坏之。BOOTSTRAP.md:476 与 v0.2.1 `--external-kb-dirs` 加入暗示跨 KB 链接是设计意图。

**Evidence:** Finding R14、R15、R19、R20。

**Conclusion:** Cluster B、A、D 的统一修复建议过度工程或引入新 false-negative。Minimal fix sets 见各 Finding。

### Phase 4 - Defect count audit

**Hypothesis:** "18 缺陷"计数含通胀。

**Findings:**
- N12 死代码不应计入"误报调查缺陷"。
- N13 "NOT OBSERVED" 不应计入"已发现缺陷"。
- N3 理论不可触发，不应计入"实际 false-positive 源"。
- 校正后约 15-16 个真实缺陷（原报告 18）。

**Evidence:** Finding R18。

**Conclusion:** 原报告计数通胀约 2-3 个。修正后分类见 Finding R18 表。

---

## Corrected Root Cause

原报告将 18 个缺陷归为 4 个集群 + 1 类假阴性。红队审计后的校正版：

| 类别 | 数量 | 真实缺陷（按优先级） |
|---|---|---|
| **A. schema/templates/init/scripts 不一致** | 4 | V4 (REQUIRED_DIRS)、V5 (init.py DIRECTORIES 含 annotations/)、N1 (PLACEHOLDER_PATTERNS 漏 annotations/)、N14 (init.py CLAUDE.md 片段与 rules.md v0.3.0 矛盾) |
| **B. 链接身份模型缺失** | 4 | V2 (continue 跳过 index.md link harvest)、V3 (orphan 比较 .md vs path-style 不匹配)、N3 (resolve_wikilink 不递归搜索；LATENT)、N11 (suggested_action 用 bare-stem 而非路径式) |
| **C. CLI/UX 不一致** | 5 | N5 (--no-skip 不真正禁用 -archive)、N6 (硬编码 "wiki/index.md")、N8 (退出码不一致)、N9 (--root templates/ 不触发自身 skip)、N10 (--external-kb-dirs 静默接受不存在路径) |
| **D. 边界逃逸（false-negative）** | 3 | N4 (path traversal)、N7 (root.parent 兄弟文件)、N15 (跨 KB sibling false-negative) |
| **E. 其他** | 2 | V1 (Python 3.9 PEP 604 崩溃)、N2 (init.py 缺 entities/ — 实际与 schema 一致，LOW) |
| **F. 不计入** | 3 | N12 (死代码)、N13 (regex 边缘，未观察)、N3 (理论不可触发) |

**校正后总数：18 → 15-16**（视是否把 N2 视为 drift 缺陷）

**校正后集群 B 修复策略**：不做 `canonical_link` 统一抽象，而是 4 处局部改动：
- V2：`check_orphan_pages` line 101 continue 改为只 skip `all_pages.add`，继续执行 wikilink 收集
- V3：line 110 比较改为 `Path(page).with_suffix('')` (path-without-.md)
- N11：line 118 `suggested_action` 用 `Path(page).with_suffix('')` 替换 `page_stem`
- N3：`resolve_wikilink` line 50-68 增加递归/子目录搜索（最小：line 53-55 4 个 candidates 后追加 `root.rglob(f"{Path(link).name}.md")` 并 containment check）

**校正后集群 D 修复策略**：N4/N7/N15 共享一个 containment check 修法：
- 所有 candidates `.resolve()` 后做 `is_relative_to(root or external_kb_dirs)` 检查
- **不**删除 root.parent（保留跨 KB 链接语义）
- 若产品决定不支持跨 KB 链接，则额外加 `--allow-cross-kb` flag 显式开启

**校正后集群 A 修复策略**：删除 templates 中的虚构 `[[annotations/xxx]]` 行（concept.md:66, decision.md:78, annotation.md:65），而非在 audit.py 加 `annotations?/` PLACEHOLDER 补丁。

---

## Corrections to Original Report

| 原报告 claim | 校正 |
|---|---|
| 18 缺陷 | 校正为 15-16 真实缺陷；N3 降级 LATENT，N12/N13 不计入 |
| N1 HIGH impact | 校正为 LOW（仅 `--root templates/` 或 `--no-skip` 触发） |
| N3 MEDIUM impact | 校正为 LATENT/THEORETICAL（文档约定 100% 路径式，0 真实裸名链接触发） |
| N4 "false positive investigation" | 校正为 false-negative / security defect |
| V2 行号 audit.py:95-96 AND audit.py:107-108 | 实际 line 101；两处引用均错位 6 行 |
| V3 行号 audit.py:114-119 | 实际 108-117（错位 6 行） |
| N1 行号 templates/concept.md:67 | 实际 66（错位 1）；decision.md:79→78；annotation.md:66→65 |
| N2/V5 行号 init.py:16-19 | 实际 26-30（错位 10） |
| N8 行号 verify.py:30-32,42-48 | 实际 39, 45（错位 7-13） |
| N8 行号 audit.py:178 | 实际 196（错位 18） |
| N12 行号 audit.py:142-145 | 实际 147（错位 5） |
| N14 行号 init.py:22 | 实际 21-23（line 22 是空白行，错位 1） |
| Schema node-types.md:55 含 annotations 块 | 实际 annotations 在 line 24-31；line 55 是 `comparisons/（可选）` |
| V4 推荐 `REQUIRED_DIRS=["concepts","decisions"]` | 论据修正为"schema 默认写回位置"而非"必需"；entities/comparisons 标"可选" |
| N2 init.py 缺 entities/ 是缺陷 | 校正：entities 在 schema 中标"可选"，init.py 不创建反而与 schema 一致；N2 推荐"补 entities/" 是新增可选项，不是修正 |
| Cluster B 推荐 canonical_link 统一 | 校正：4 处局部改动（Finding R15 表），统一会引入 false-negative |
| Cluster A 推荐加 `annotations?/` PLACEHOLDER | 校正：删除 templates/concept.md:66, decision.md:78, annotation.md:65 的虚构引用 |
| Cluster D 修复"移除或限制 root.parent"含糊 | 校正：containment check `is_relative_to()`，不删除 root.parent（保留跨 KB 链接语义） |
| N14 严重度 LOW（片段过期） | 校正为 HIGH（CHANGELOG v0.3.0 明确废除，init.py 反向引导新 KB 进入废弃工作流） |

---

## Validated Claims (unchanged)

经红队校对后**仍然成立**的原报告 claim：

- **V1**：PEP 604 语法崩溃 Python 3.9（CONFIRMED；行号 audit.py:43,51,71,95 正确）
- **V2**：`check_orphan_pages` 的 `continue` 跳过 index.md link harvest（CONFIRMED；行号错但缺陷真实）
- **V3**：orphan 比较 page_stem vs str(page) vs path-style 互不匹配（CONFIRMED；行号错但缺陷真实）
- **V4**：verify.py `REQUIRED_DIRS` 含虚构 `annotations/`（CONFIRMED；需修正论据）
- **V5**：init.py DIRECTORIES 含 `wiki/annotations/`（CONFIRMED；行号错但缺陷真实）
- **N4**：`[[../../../etc/passwd]]` 静默通过 resolve_wikilink（CONFIRMED；需重分类为 false-negative）
- **N5**：`--no-skip` 不真正禁用 `-archive` 子串检查（CONFIRMED）
- **N6**：`check_index_exists` 硬编码 `"wiki/index.md"`（CONFIRMED；行号错但缺陷真实）
- **N7**：`root.parent` 兄弟文件泄漏（CONFIRMED；但需明确为 false-negative 而非 false-positive）
- **N9**：`--root templates/` 不触发自身 skip（CONFIRMED）
- **N10**：`--external-kb-dirs` 静默接受不存在路径（CONFIRMED）
- **N11**：orphan `suggested_action` 用 bare-stem（CONFIRMED）
- **N14**：init.py CLAUDE.md 片段与 rules.md v0.3.0 矛盾（CONFIRMED；严重度应升级 HIGH 而非 LOW）
- **N15**：`[[../sibling-project/notes]]` 经 root.parent 静默通过（CONFIRMED false-negative）

**被红队推翻/降级的 claim**：

- **N1 HIGH** → LOW（仅 dev inspection 模式触发）
- **N3 MEDIUM** → LATENT/THEORETICAL（文档约定 100% 路径式，0 真实裸名链接触发）
- **N12** → 不计入（死代码）
- **N13** → 不计入（NOT OBSERVED）
- **18 缺陷** → 校正为 15-16

**被红队错类的 claim**：

- **N4**：从"误报"重分类为"false-negative / security"
- **N7**：从模糊"false positive / false negative"明确为 false-negative

**被红队质疑的修复建议**：

- Cluster A 加 `annotations?/` PLACEHOLDER（band-aid，引入新 false-negative）→ 删除 templates 虚构引用
- Cluster B 统一 `canonical_link`（过度工程）→ 4 处局部改动
- Cluster D "移除或限制 root.parent"（含糊）→ containment check 不删除 root.parent

**行号错误的系统性观察**：原报告 25+ 处行号引用中，至少 12 处存在错位（off-by-1 到 off-by-18）。最常见的是 off-by-1（多个 N1 templates 引用、N6 audit.py:129→130、N10 audit.py:59-67→58-67），其次是 off-by-5/+5（V2 错 6 行、N12 错 5 行），最严重是 N8 audit.py:178→196 错 18 行。这暗示审计者在引用时没有逐行复核原文，而是凭记忆或粗略定位。**这是质量信号**：原报告的"已验证"标签可能未涵盖行号精度，仅涵盖功能描述精度。