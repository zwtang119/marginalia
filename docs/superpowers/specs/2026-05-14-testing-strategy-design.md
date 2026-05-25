# GPT54 测试策略设计：基于工程控制论的四层测试体系

## 文档信息

- **创建日期**：2026-05-14
- **修订日期**：2026-05-14
- **状态**：confirmed
- **相关**：[[project/plan]]、GPT54/SPEC.md、GPT54/PRD.md

## 1. 背景与问题

GPT54 是一个零依赖、文件系统优先的协议型知识工程系统，其核心是控制论闭环：传感器（audit.py）→ 控制器（schema/）→ 执行器（init.py/verify.py）→ 受控对象（知识库）。

系统已有基础单元测试（init / audit / verify / protocol_discovery）和 shell 冒烟测试。需要判断是否需要 AB 测试或其他测试类型来优化系统。

## 2. 核心判断：AB 测试不适用于当前阶段

### 2.1 从工程控制论视角分析

AB 测试在传统软件中用于比较两种策略对用户行为指标的影响。在协议型系统中，AB 测试的类比是「比较不同版本的协议规则对知识库质量的影响」。

当前阶段的三个硬约束使 AB 测试不可行：

1. **系统尚未闭环运行**：M0/M1 阶段的重点是「能跑通」而非「哪个方案更优」。AB 测试需要系统已稳定运行。
2. **缺乏可量化指标**：知识库「质量」尚无稳定的数值度量。断链数、薄页面数等结构指标刚刚建立基线。
3. **缺乏统计显著性条件**：LLM 输出有内在随机性，AB 测试需要多次重复实验才能区分信号和噪声。

### 2.2 AB 测试的远期定位

L4 策略 AB 对比作为远期保留，需要三个前置条件：
- 可量化指标稳定（通过 L1 audit 快照持续追踪）
- 控制闭环稳定收敛
- 多轮重复实验能力

## 3. 方案选择：四层渐进式测试体系（方案 C）

### 3.1 为什么不是端到端测试（E2E）

传统 E2E 测试测试完整用户流程。在 GPT54 中，完整流程涉及 LLM 调用（控制器 + 执行器部分），而 LLM 行为是非确定性的。传统 E2E 测试在确定性要求下只能覆盖脚本部分，无法覆盖协议行为部分——这正是「金字塔顶层空心」问题。

方案 C 的解法是将 E2E 的覆盖目标拆解到不同层：
- 确定性的脚本链路 → L1 回归护栏
- 协议发现和解析 → L2 协议发现测试
- 协议文本对 LLM 行为的约束力 → L3 协议合规测试

### 3.2 四层架构

```
┌─────────────────────────────────────────────────────┐
│                  测试体系（元控制层）                    │
│                                                      │
│  L4 策略 AB 对比  ←── 控制策略优化（远期，仅规格记录）     │
│  L3 协议合规测试   ←── 控制器校准（协议清晰度验证）       │
│  L2 协议发现测试   ←── 传感器通路验证（Agent 能读到协议吗）│
│  L1 回归护栏      ←── 传感器/执行器/接口确定性验证       │
│    L1a 传感器校准  ←── audit.py 输出稳定性              │
│    L1b 执行器验证  ←── init/verify 输入输出契约         │
│    L1c 接口一致性  ←── 执行器输出满足控制器输入要求       │
│                                                      │
│  ───────────────────────────────────────────────     │
│  受测系统（GPT54 控制闭环）                            │
│  传感器(audit.py) → 控制器(schema/) → 执行器(init/     │
│  verify) → 受控对象(知识库) → 传感器                    │
└─────────────────────────────────────────────────────┘
```

### 3.3 目录结构

```text
tests/
├── unit/              # L1a: 传感器校准（已有内容迁移至此）
│   ├── test_init.py
│   ├── test_audit.py
│   └── test_verify.py
├── regression/        # L1a: 传感器校准 - 快照对比（新增）
│   ├── test_audit_snapshot.py    # audit 快照对比
│   └── fixtures/
│       └── us_military_kb/       # 美军知识库作为 fixture
├── actuator/          # L1b: 执行器验证（新增）
│   ├── test_init_contract.py     # init.py 输入输出契约
│   └── test_verify_contract.py   # verify.py 输入输出契约
├── interface/         # L1c: 接口一致性（新增）
│   └── test_schema_conformance.py # 执行器输出满足 schema 输入
├── protocol/          # L2: 协议发现测试（已有内容迁移至此）
│   └── test_protocol_discovery.py
├── compliance/        # L3: 协议合规测试（新增）
│   ├── run_scenarios.py         # 场景执行入口
│   ├── verifier.py              # 合规判定器（确定性代码）
│   ├── scenarios/
│   │   ├── s1_create_concept.json
│   │   ├── s2_run_audit.json
│   │   ├── s3_cross_ref_update.json
│   │   ├── s4_fix_defect.json
│   │   └── s5_ingest_with_feedforward.json
│   └── results/                 # 结果记录（gitignore）
└── smoke/             # 冒烟测试（已有，不动）
    └── test_cli_smoke.sh
```

## 4. L1：回归护栏

### 4.1 目的

确保控制闭环中传感器、执行器和接口的确定性——传感器修改后不引入退化，执行器满足输入输出契约，执行器输出满足控制器输入要求。

### 4.2 L1a：传感器校准

确保 `audit.py`（传感器）修改后不引入退化——之前能检测的缺陷不会漏检，输出格式不会变化。

#### 4.2.1 机制：审计快照对比

每次运行 audit.py → 生成结构化 JSON 输出 → 与基线快照对比 → 差异即退化。

#### 4.2.2 快照格式

```json
{
  "meta": {
    "kb_root": "us-military-knowledge",
    "timestamp": "2026-05-14T...",
    "audit_version": "0.1.0"
  },
  "counts": {
    "total_pages": 135,
    "broken_links": 26,
    "thin_pages": 12,
    "missing_from_index": 3,
    "orphan_pages": 5
  },
  "details": {
    "broken_links": [
      {"source": "wiki/concepts/foo.md", "target": "bar.md", "line": 42}
    ],
    "thin_pages": [
      {"path": "wiki/entities/baz.md", "lines": 3}
    ]
  },
  "trend": {
    "history": [28, 25, 22, 20, 18],
    "direction": "converging",
    "total_defects": 18,
    "audit_count": 5
  }
}
```

#### 4.2.3 对比规则

| 检查项 | 断言方式 | 含义 |
|-------|---------|------|
| counts.* | 严格相等 | 缺陷数不能增加 |
| details.broken_links | 子集检查 | 基线中断链必须全部检出 |
| details 结构 | schema 校验 | 输出格式不能变 |
| trend.direction | 枚举校验 | converging / stable / diverging |
| trend.history | 单调性检查（可选） | 收敛时最近 N 次应单调递减 |

### 4.3 L1b：执行器验证

确保 `init.py` 和 `verify.py`（执行器）满足输入输出契约。

| 测试 | 断言 |
|------|------|
| test_init_creates_expected_files | 给定合法 schema，init.py 产出所有契约文件 |
| test_init_rejects_invalid_schema | 给定非法 schema，init.py 报错退出 |
| test_init_idempotent | 对同一 schema 重复运行，输出不变 |
| test_verify_accepts_valid_kb | 给定合规知识库，verify.py 返回 0 |
| test_verify_rejects_invalid_kb | 给定不合规知识库，verify.py 返回非 0 并输出缺陷清单 |
| test_verify_output_format | verify.py 输出满足结构化格式契约 |

### 4.4 L1c：接口一致性

确保执行器输出满足控制器（schema/）的输入要求——这是传感器和执行器之间的耦合测试。

| 测试 | 断言 |
|------|------|
| test_init_output_parseable_by_audit | init.py 产出的文件能被 audit.py 正确解析 |
| test_verify_defects_match_audit | verify.py 报告的缺陷是 audit.py 检出缺陷的子集 |
| test_schema_files_cover_all_node_types | schema/ 中定义的类型覆盖 init.py 产出的所有节点类型 |

### 4.5 约束

- 零 LLM 依赖
- 纯 Python 标准库
- 秒级运行
- CI 自动门禁

### 4.6 稳定性分析：趋势追踪

控制论的核心问题是闭环系统是否稳定。L1 不仅检测"这次是否退化"，还追踪"系统是否收敛"。

#### 4.6.1 机制

每次 audit 运行后，将 `counts` 中的关键指标追加到历史序列文件 `tests/regression/fixtures/trend_history.jsonl`（每行一条 JSON 记录）。

#### 4.6.2 趋势判定规则

| 条件 | 判定 | 含义 |
|------|------|------|
| 最近 N 次（默认 5）总缺陷数单调递减 | converging | 系统收敛，闭环有效 |
| 最近 N 次总缺陷数变化 ≤ 阈值 | stable | 系统稳态，缺陷数不再下降 |
| 最近 M 次（默认 3）总缺陷数单调递增 | diverging | 系统发散，闭环失效，需人工介入 |
| 历史记录不足 N 条 | insufficient | 数据不足，无法判定 |

#### 4.6.3 总缺陷数定义

```
total_defects = broken_links + thin_pages + missing_from_index + orphan_pages
```

### 4.7 收敛/发散判据

| 判据 | 阈值 | 触发动作 |
|------|------|---------|
| converging | 连续 5 次 total_defects 单调递减 | 正常，记录趋势 |
| stable | 连续 5 次 total_defects 变化 ≤ 2 | 检查是否已达零缺陷基线；若否，考虑调整控制策略 |
| diverging | 连续 3 次 total_defects 单调递增 | **告警**：标记为阻塞，触发 L2 检查协议是否退化 + L3 检查 LLM 行为是否合规 |

## 5. L2：协议发现测试

### 5.1 目的

验证 AI Agent 进入仓库后，能否不依赖外部说明，仅通过文件系统中的协议文件正确发现并理解系统规则。

### 5.2 两类测试

**5.2.1 静态发现测试（确定性）**

验证文件存在性、格式正确性、引用完整性：

| 测试 | 断言 |
|------|------|
| test_entry_point_exists | CLAUDE.md 包含 GPT54-PROTOCOL 标记 |
| test_discovery_chain_complete | CLAUDE.md 中引用的所有 schema 文件都存在 |
| test_schema_files_well_formed | 每个 schema 文件有有效结构 |
| test_node_types_defined | node-types.md 中定义所有必需类型 |
| test_rules_reference_node_types | rules.md 引用的类型在 node-types.md 中都有定义 |
| test_no_circular_references | schema 文件间不存在循环引用 |

**5.2.2 行为发现测试（确定性，mock LLM）**

验证协议内容是否足够让 Agent 做出正确行为决策：

| 测试 | 断言 |
|------|------|
| test_agent_knows_reading_order | 读取顺序：CLAUDE.md → rules.md → ... |
| test_agent_finds_concept_template | 能解析出 concept 节点模板 |
| test_agent_knows_post_task_actions | 知道任务后需更新 progress.md + index.md |
| test_agent_knows_audit_trigger | 知道何时触发审计 |

### 5.3 反馈回路

L2 检测到协议引用断裂后，必须闭合回路：

```
发现引用断裂 → 修复 schema 文件 → 重新运行 L2 静态发现测试 → 通过即闭合
```

| 检测结果 | 修正动作 | 验证 |
|---------|---------|------|
| schema 文件缺失 | 创建或恢复缺失文件 | 重跑 L2 静态发现，全部通过 |
| 引用断裂 | 修复 CLAUDE.md 或 schema 中的引用 | 重跑 L2 静态发现，引用链完整 |
| 格式错误 | 修正 schema 文件结构 | 重跑 L2 静态发现，格式校验通过 |

### 5.4 约束

- 零 LLM 依赖
- 被测对象是协议文本本身
- CI 自动门禁

## 6. L3：协议合规测试（Prompt 测试）

### 6.1 目的

校准协议文本的清晰度和约束力。核心思想：如果多个不同 LLM 在面对同一协议时产生相同类型的违规，问题在协议设计而非 LLM。

### 6.2 测试模型

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  标准化场景   │ ──→ │  LLM + 协议   │ ──→ │  合规判定器   │
│  (scenario)  │     │  (被测对象)    │     │  (verifier)   │
└──────────────┘     └──────────────┘     └──────────────┘
```

### 6.3 五个标准化场景

| 场景 ID | 场景描述 | 验证的协议能力 |
|---------|---------|-------------|
| S1 | 创建一个概念节点 | 节点类型识别、模板遵守、frontmatter 完整性 |
| S2 | 运行一次审计并报告问题 | 审计触发、工具调用、报告格式 |
| S3 | 创建节点后检查跨页引用更新 | 前馈控制、跨页引用、index 同步 |
| S4 | 发现缺陷后执行修复 | 执行器核心工况：缺陷定位→修复→验证闭环 |
| S5 | 摄入新知识时同步更新受影响页面 | 前馈控制：ingest 时主动更新关联页面，而非事后检测 |

### 6.4 合规判定规则

| 检查维度 | S1 | S2 | S3 | S4 | S5 |
|---------|----|----|-----|----|----|
| 文件位置 | docs/nodes/ | audit/reports/ | 更新 docs/index.md | 修复目标文件 | 新增 + 受影响页面 |
| 结构完整 | type: concept | 缺陷清单 + 优先级 | 索引表含新页面 | 缺陷已消除 | 新页面 + 关联更新 |
| wikilink | ≥1 个 [[wikilink]] | 断链指向具体文件 | 新页面在 index | 修复未引入新断链 | 新页面有 wikilink |
| 禁止行为 | 不创建无关文件 | 不跳过 audit | 不遗漏受影响页面 | 不破坏现有内容 | 不遗漏受影响页面 |

### 6.5 反馈回路

L3 检测到 LLM 不合规后，必须闭合回路：

```
发现 LLM 行为不合规 → 诊断原因（协议模糊？协议缺失？模型特性？）→ 修正协议文本 → 重新运行 L3 场景 → 合规率提升即闭合
```

| 诊断结论 | 修正动作 | 验证 |
|---------|---------|------|
| 协议规则模糊 | 细化 schema 中的规则描述 | 重跑 L3，合规率提升 |
| 协议规则缺失 | 在 schema 中新增规则 | 重跑 L3，违规行为消失 |
| 模型特性（仅单模型违规） | 记录为模型已知限制，不修改协议 | 多模型对比确认 |
| 多模型共同违规 | 必定是协议问题 | 修正后重跑 L3 |

### 6.6 运行策略

- **非 CI 门禁**：LLM 调用有成本、延迟和非确定性
- **触发时机**：schema/ 修改时手动运行、发布新协议版本前必跑、Agent 行为异常时诊断
- **多模型对比**：至少两个不同模型，区分协议问题和模型特性
- **判定器确定性**：只有判定逻辑是代码，LLM 输出是输入

## 7. L4：策略 AB 对比（远期保留）

### 7.1 定位

当 L1-L3 全部就绪、控制闭环稳定收敛后，L4 回答：不同版本协议规则对知识库质量的相对效果。

### 7.2 前置条件（当前均不满足）

1. 可量化指标稳定（通过 L1 audit 快照持续追踪）
2. 控制闭环稳定收敛（通过 L1 趋势追踪确认 converging）
3. 统计显著性条件（多次重复实验能力）

### 7.3 当前策略

仅在本规格中记录 L4 的存在和前置条件，不在 M0/M1 范围实现任何代码。

## 8. 层间耦合条件

四层测试不是独立的监测器，而是递阶控制系统。上层对下层的控制通过明确定义的触发规则实现。

### 8.1 触发规则

| 触发条件 | 动作 | 控制论含义 |
|---------|------|-----------|
| L1a 快照 counts 增加 | → 自动触发 L2（检查是否协议变更导致） | 传感器异常 → 检查传感器通路 |
| L1a 趋势 diverging | → 触发 L2 + L3（全面诊断） | 系统发散 → 全链路排查 |
| L1b 执行器契约失败 | → 检查 schema 是否变更 | 执行器失效 → 检查控制器输入 |
| L1c 接口一致性失败 | → 检查 schema/ 与 init/verify 的版本匹配 | 接口断裂 → 版本对齐 |
| L2 发现新引用断裂 | → 触发 L3（评估协议清晰度是否退化） | 传感器通路断裂 → 校准控制器 |
| L3 合规率下降 | → 标记 L1a 基线待更新（协议变更后旧基线可能失效） | 控制器校准 → 重新标定传感器 |

### 8.2 基线更新规则

协议变更（schema/ 修改）后，L1a 快照基线可能失效。更新流程：

1. 修改 schema/ 文件
2. 运行 L2 确认协议结构完整
3. 运行 L3 确认 LLM 行为合规
4. 重新生成 L1a 快照基线
5. 提交新基线到版本控制

## 9. 扰动模型

控制论要求明确识别系统面临的扰动，并为每类扰动设计抑制策略。

### 9.1 扰动分类

| 扰动源 | 类型 | 影响范围 | 抑制策略 |
|-------|------|---------|---------|
| LLM 非确定性 | 随机噪声 | L3 合规判定 | 多模型对比 + 确定性判定器 + 多次运行取众数 |
| 代码退化 | 确定性偏差 | L1a 传感器输出 | 快照对比 + CI 门禁 |
| Schema 演进 | 结构性扰动 | L1a 基线、L2 引用链、L3 合规基线 | 基线更新流程（§8.2）+ L2 引用完整性检查 |
| 知识库规模增长 | 渐进性扰动 | L1a 运行时性能 | 性能基线（audit 运行时间 ≤ 阈值）+ fixture 规模标注 |
| LLM 模型更新 | 阶跃性扰动 | L3 合规基线 | 模型更新后必须重跑 L3 + 重新校准合规率 |
| 人为直接编辑 | 不可控扰动 | 知识库状态 | L1a 下次运行自动检出 + 前馈规则提醒 |

### 9.2 扰动抑制原则

1. **确定性扰动用确定性手段抑制**：代码退化 → 快照对比；Schema 演进 → 基线更新流程
2. **随机噪声用统计手段抑制**：LLM 非确定性 → 多模型对比 + 多次运行
3. **不可控扰动用检测代替抑制**：人为编辑无法阻止，但 L1a 可以检出

## 10. 实施优先级

### Phase 1（立即可做，零新增依赖）

- L1a 传感器校准：test_audit_snapshot.py + us_military_kb fixture + 趋势追踪
- L1b 执行器验证：test_init_contract.py + test_verify_contract.py
- L1c 接口一致性：test_schema_conformance.py
- L2 静态发现：增强 test_protocol_discovery.py

### Phase 2（Phase 1 稳定后）

- L2 行为发现：ProtocolDiscovery 解析类

### Phase 3（需要 LLM 调用能力）

- L3 协议合规：compliance/ 目录 + 5 个场景

### Phase 4（远期，仅规格记录）

- L4 策略 AB 对比

## 11. 现有测试迁移

| 现有文件 | 动作 |
|---------|------|
| tests/test_init.py | → tests/unit/ |
| tests/test_audit.py | → tests/unit/ |
| tests/test_verify.py | → tests/unit/ |
| tests/test_protocol_discovery.py | → tests/protocol/ 并增强 |
| tests/smoke/test_cli_smoke.sh | 不动 |
| tests/fixtures/minimal_expected_tree.txt | 不动 |

不删除任何现有测试，仅重组目录。

## 12. 成功标准

1. L1a：修改 audit.py 后运行快照测试，秒级反馈是否有退化
2. L1b：修改 init/verify 后运行契约测试，秒级反馈是否破坏契约
3. L1c：修改 schema 后运行接口测试，秒级反馈是否引入接口不一致
4. L1 趋势：每次 audit 后自动追踪缺陷数趋势，diverging 时告警
5. L2：新增 schema 文件或修改协议链后，发现测试自动检测引用断裂
6. L2 反馈：发现断裂后修复并重跑，通过即闭合
7. L3：协议修改后能通过场景测试评估 LLM 行为合规性
8. L3 反馈：发现不合规后修正协议并重跑，合规率提升即闭合
9. 层间耦合：L1 异常能自动触发 L2/L3 诊断
10. 整体：测试体系自身零外部依赖，符合 GPT54 的零依赖约束
