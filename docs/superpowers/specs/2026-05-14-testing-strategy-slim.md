# GPT54 测试策略精简方案：从理论驱动到数据驱动

## 文档信息

- **创建日期**：2026-05-14
- **状态**：draft
- **前置文档**：[[2026-05-14-testing-strategy-design]]（四层体系原方案）
- **相关**：[[project/plan]]、GPT54/SPEC.md、GPT54/PRD.md

## 1. 诊断：为什么需要精简

### 1.1 过度设计的三个信号

| 信号 | 表现 | 控制论解释 |
|------|------|-----------|
| 控制器复杂度 >> 受控对象复杂度 | 430 行规格书管理 ~400 行脚本 | 过控（over-control）：控制成本超过控制收益 |
| 无数据的仪表盘 | 趋势追踪、扰动模型从未收到真实数据 | 虚观测（virtual observation）：传感器没有接入受控对象 |
| 空壳测试 | S4/S5 直接 `passed: True`，L1b 测试 `path.write_text()` 能工作 | 形式闭环：回路结构存在但信息流为零 |

### 1.2 根本原因

原方案从理论推导出测试体系（"控制论应该有四层"），而非从实际运行中生长出测试需求（"我们观测到 X 问题，需要 Y 测试来检测"）。

工程控制论的基本工作顺序是：

```
1. 让受控对象运行 → 2. 观测行为 → 3. 识别问题 → 4. 针对问题设计控制
```

原方案跳过了 1-3，直接做了 4。

### 1.3 什么被正确地设计了

- AB 测试不适用于当前阶段的判断 ✅
- 传统 E2E 不适用于 LLM 系统的判断 ✅
- L1a 快照对比的机制设计 ✅
- L2 静态发现测试的方向 ✅
- L4 远期保留的定位 ✅

## 2. 精简方案：两层 + 冻结层

### 2.1 架构

```
┌──────────────────────────────────────────────────────┐
│  冻结层（代码保留，不维护，等前置条件满足后激活）        │
│  L3 协议合规   ←── 需要 LLM 调用能力                  │
│  L4 策略 AB    ←── 需要稳定闭环 + 可量化指标           │
│                                                       │
│  ─────────────────────────────────────────────────    │
│  活跃层                                               │
│  L2 协议发现    ←── 协议完整性（静态检查）              │
│  L1 回归护栏    ←── 确定性回归保护                      │
│    ├─ 快照对比（原 L1a）                               │
│    ├─ 执行器契约（原 L1b，合并入 L1）                   │
│    └─ 接口一致性（原 L1c，合并入 L1）                   │
│                                                       │
│  ─────────────────────────────────────────────────    │
│  受测系统（GPT54 控制闭环）                            │
│  传感器(audit.py) → 控制器(schema/) → 执行器(init/     │
│  verify) → 受控对象(知识库) → 传感器                    │
└──────────────────────────────────────────────────────┘
```

### 2.2 为什么合并 L1a/L1b/L1c

当前三个子层的区分基于"传感器/执行器/接口"的控制论角色。但实际代码中：

- 传感器（audit.py）和执行器（init/verify.py）之间的"接口"就是文件系统路径
- "接口一致性测试"本质是"init 产出的文件能被 audit 解析"——这已经被快照对比覆盖
- "执行器契约测试"中 `test_init_creates_expected_files` 和 `test_init_idempotent` 是有价值的，但不需要独立目录

合并后，L1 就是一个回归测试套件，包含快照对比 + 执行器契约 + 接口检查，放在同一个目录中。

### 2.3 目录结构

```text
tests/
├── unit/              # 原有单元测试（不动）
│   ├── test_init.py
│   ├── test_audit.py
│   └── test_verify.py
├── regression/        # L1：回归护栏（合并 L1a/L1b/L1c）
│   ├── test_audit_snapshot.py     # 快照对比
│   ├── test_init_contract.py      # 执行器契约（从 actuator/ 移入）
│   ├── test_verify_contract.py    # 执行器契约（从 actuator/ 移入）
│   ├── test_schema_conformance.py # 接口一致性（从 interface/ 移入）
│   └── fixtures/
│       └── minimal_expected_tree.txt
├── protocol/          # L2：协议发现（不动）
│   └── test_protocol_discovery.py
├── compliance/        # 冻结层：L3 协议合规（代码保留，不维护）
│   ├── scenarios/
│   │   ├── s1_create_concept.json
│   │   ├── s2_run_audit.json
│   │   ├── s3_cross_ref_update.json
│   │   ├── s4_fix_defect.json
│   │   └── s5_ingest_with_feedforward.json
│   ├── verifier.py
│   └── run_scenarios.py
└── smoke/             # 冒烟测试（不动）
    └── test_cli_smoke.sh
```

删除的目录：`actuator/`、`interface/`（内容合并入 `regression/`）。

## 3. 趋势追踪：冻结而非删除

### 3.1 当前问题

`_append_trend()` 函数已写入 audit.py，但：

- 从未在真实知识库上运行过
- converging/diverging/stable 判定逻辑在 init 后 audit 结果恒为 0 缺陷时永远不会触发
- 没有历史数据支撑趋势分析

### 3.2 处理方式

- **代码保留**，不删除
- **冻结**：不在当前阶段维护或增强
- **激活条件**：在真实知识库上积累 ≥5 次真实 audit 数据后，验证趋势判定逻辑是否符合实际行为

### 3.3 激活后的验证清单

- [ ] 5 次真实 audit 数据是否产生有意义的趋势？
- [ ] converging/diverging/stable 判定是否与人工判断一致？
- [ ] 趋势追踪是否帮助发现了人工未注意到的问题？
- [ ] 如果以上任一答案为否，考虑简化或删除

## 4. 扰动模型：降级为观察笔记

### 4.1 当前问题

原方案 §9 列出 6 类扰动及抑制策略，但每一类都是推测，不是从实际运行中总结的。

### 4.2 处理方式

将扰动模型从"规格"降级为"观察笔记"。不删除，但：

- 标记为 `status: unvalidated`
- 每类扰动的"抑制策略"改为"待验证假设"
- 在真实知识库运行后，用实际观察填充或修正

### 4.3 观察方法

在真实知识库上运行闭环时，记录：

| 观察项 | 记录方式 |
|-------|---------|
| audit 输出是否稳定 | 连续 3 次运行同一知识库，对比 counts |
| 代码修改后是否引入退化 | 每次修改后运行 L1，记录结果 |
| Schema 修改后基线是否失效 | 修改 schema 后运行 L1，对比快照 |
| LLM 行为是否合规 | 手动运行 L3 场景，记录结果 |

## 5. AB 测试与端到端测试的决策

### 5.1 AB 测试：不需要

原方案的判断完全正确，三个前置条件均不满足：

1. 可量化指标不稳定（连基线都没有）
2. 控制闭环未运行
3. 统计显著性条件不存在

AB 测试回答"哪个方案更好"，当前阶段的问题是"方案能不能跑"。这是调节和优化的区别。

### 5.2 端到端测试：需要，但不是传统 E2E

传统 E2E 在 LLM 系统中不可行（非确定性）。但需要一个**真实数据驱动的集成测试**：

```python
def test_full_cycle_on_real_kb():
    root = Path("path/to/us-military-kb")
    audit_result = run_audit(root)
    assert audit_result["counts"]["total"] >= 0
    assert audit_result["counts"]["broken_links"] <= 26
    verify_result = run_verify(root)
    assert verify_result.returncode in (0, 1)
```

与原方案的区别：

| 维度 | 原方案 L1-L3 拆解 | 真实数据集成测试 |
|------|------------------|----------------|
| 数据源 | mock fixture（init 生成的空壳知识库） | 真实知识库（美军 KB） |
| 覆盖目标 | 各组件的契约 | 完整闭环能否跑通 |
| 基线来源 | 理论推导 | 实际运行结果 |
| 发现问题的能力 | 只能发现预设的问题 | 能发现未预料的问题 |

### 5.3 集成测试的激活条件

- [ ] audit.py 能在美军知识库上运行并产出有效 JSON
- [ ] 已有至少 1 次真实 audit 基线数据
- [ ] verify.py 能在美军知识库上运行

## 6. 实施路线

### Phase 0：闭环首次运行（P0，立即）

目标：让控制闭环在真实知识库上跑通一次。

| 步骤 | 动作 | 验证 |
|------|------|------|
| 0.1 | 在美军知识库上运行 `audit.py --root <us-military-kb>` | 产出有效 JSON 报告 |
| 0.2 | 记录基线：broken_links、thin_pages、missing_from_index、orphan_pages 的实际数值 | 基线数据写入 `audit/baselines/` |
| 0.3 | 基于基线数据，编写 `test_real_kb_baseline.py` | 测试通过 |

### Phase 1：回归保护（P1，Phase 0 完成后）

目标：确保闭环行为不退化。

| 步骤 | 动作 | 验证 |
|------|------|------|
| 1.1 | 合并 actuator/ 和 interface/ 到 regression/ | 所有测试仍通过 |
| 1.2 | 基于真实基线数据增强 `test_audit_snapshot.py` | 快照对比使用真实数据 |
| 1.3 | 修复 26 个断链 | 再次 audit，broken_links 数下降 |
| 1.4 | 运行 audit 确认缺陷数下降 | 闭环首次验证：传感器→执行器→受控对象→传感器 |

### Phase 2：协议发现增强（P2，Phase 1 稳定后）

目标：确保协议文件结构完整。

| 步骤 | 动作 | 验证 |
|------|------|------|
| 2.1 | 增强 `test_protocol_discovery.py`，覆盖 schema 文件间的引用完整性 | 测试通过 |
| 2.2 | 在协议修改后运行 L2，确认引用链完整 | 反馈回路闭合 |

### Phase 3：数据驱动扩展（P3，积累 ≥5 次真实 audit 数据后）

目标：基于真实数据决定是否激活趋势追踪和 L3。

| 步骤 | 动作 | 验证 |
|------|------|------|
| 3.1 | 分析 5 次真实 audit 数据，判断趋势追踪是否有意义 | 决策：激活或删除 `_append_trend()` |
| 3.2 | 如有 LLM 调用能力，激活 L3 合规测试 | 至少 1 个场景可自动运行 |
| 3.3 | 用实际观察验证或修正扰动模型 | 每类扰动有实际数据支撑 |

## 7. 迁移清单

### 保留不动

- `tests/unit/` — 原有单元测试
- `tests/protocol/` — L2 协议发现
- `tests/smoke/` — 冒烟测试
- `tests/compliance/` — 冻结，代码保留

### 合并

| 原位置 | 新位置 | 动作 |
|-------|-------|------|
| `tests/actuator/test_init_contract.py` | `tests/regression/test_init_contract.py` | 移动 |
| `tests/actuator/test_verify_contract.py` | `tests/regression/test_verify_contract.py` | 移动 |
| `tests/interface/test_schema_conformance.py` | `tests/regression/test_schema_conformance.py` | 移动 |

### 删除

| 目标 | 动作 |
|------|------|
| `tests/actuator/` | 移动内容后删除空目录 |
| `tests/interface/` | 移动内容后删除空目录 |

### 新增

| 文件 | 用途 |
|------|------|
| `tests/regression/test_real_kb_baseline.py` | 真实知识库基线集成测试（Phase 0） |

## 8. 成功标准

### Phase 0 完成标准

1. audit.py 在美军知识库上产出有效 JSON 报告
2. 基线数据已记录（broken_links、thin_pages 等实际数值）
3. 基于真实基线的集成测试通过

### Phase 1 完成标准

1. 目录结构已合并，所有测试通过
2. 断链数从 26 下降
3. 闭环首次验证：修改→audit→确认缺陷数下降

### 整体成功标准

1. 控制闭环在真实知识库上实际运行
2. 测试体系基于真实数据而非理论推导
3. 每个测试都有明确的数据来源和激活条件
4. 冻结层的激活决策基于实证而非计划

## 9. 与原方案的差异总结

| 维度 | 原方案 | 精简方案 |
|------|-------|---------|
| 层数 | 4 层（L1-L4） | 2 活跃层 + 1 冻结层 |
| L1 子层 | L1a/L1b/L1c 独立目录 | 合并为一个 regression/ |
| 趋势追踪 | 立即实现并运行 | 冻结，等 ≥5 次真实数据 |
| 扰动模型 | 规格级（6 类 + 抑制策略） | 降级为观察笔记（待验证假设） |
| L3 合规 | 框架已实现（S4/S5 空壳） | 冻结，等 LLM 调用能力 |
| 集成测试 | 无（拆解到 L1-L3） | 新增真实知识库基线测试 |
| 驱动方式 | 理论推导 | 数据驱动 |
| 规格篇幅 | ~430 行 | ~200 行 |
