# 系统形态分析报告

> 日期：2026-05-13
> 状态：分析完成

---

## 一、综合形态矩阵

| 维度 | Karpathy | mem0 | claude-mem | WeKnora | superpowers | Marginalia |
|------|----------|------|------------|---------|-------------|------------|
| 存储 | Markdown | 向量DB | Markdown | Markdown | Markdown | Markdown |
| 驱动 | 无 | API | 无 | 无 | Hook | 协议+脚本 |
| 类型 | 6种 | 无 | 无 | 自定义 | 无 | 4+按需 |
| 质量 | 无 | 无 | 无 | 无 | 无 | audit+verify |
| 搜索 | grep | 语义 | 无 | grep | grep | grep |
| 规模 | 扁平 | 分布式 | 扁平 | 扁平 | 扁平 | 扁平 |

## 二、关键发现

### 2.1 Markdown 是共识

所有文件驱动的系统都选择 Markdown。优势：人类可读、Git 友好、AI 原生支持。

### 2.2 驱动是分化点

- Karpathy/mem0/claude-mem/WeKnora：无驱动，依赖 AI 自觉或 API 调用
- superpowers：Hook 自动驱动，最可靠但平台绑定
- Marginalia：协议驱动，平衡了可靠性和平台无关性

### 2.3 类型系统的必要性取决于规模

- 小规模（<50 页）：不需要类型系统
- 中规模（50-200 页）：简单的类型标签有帮助
- 大规模（>200 页）：严格的类型模板必需

### 2.4 质量保障是盲区

除 Marginalia 外，没有任何系统提供自动化的质量检测。

## 三、Marginalia 的设计选择

基于分析，Marginalia 的设计选择：

1. **存储：Markdown** — 共识选择，无争议
2. **驱动：协议 + 脚本** — 平衡可靠性和平台无关性
3. **类型：4 核心 + 按需派生** — 基于使用数据的证据设计
4. **质量：audit + verify** — 唯一提供自动质量检测的系统
5. **搜索：grep** — 中小规模足够
6. **规模：扁平** — 预计 <200 页，不需要分片

## 四、风险评估

| 风险 | 可能性 | 影响 | 缓解 |
|------|--------|------|------|
| 协议驱动不如 Hook 可靠 | 高 | 中 | audit 弥补 |
| 扁平结构在大规模时失控 | 低 | 高 | 按需引入层级 |
| 4 种类型不够用 | 中 | 低 | 按需派生 |

## 五、与 Karpathy 模式的关键差异

Marginalia 不是 Karpathy 模式的简单复制。核心差异：

1. **有类型系统** — Karpathy 定义了 6 种但基于模板，Marginalia 基于使用数据精简到 4 种
2. **有质量保障** — Karpathy 完全依赖 LLM 自检，Marginalia 有 audit.py
3. **有驱动机制** — Karpathy 依赖 Hook（superpowers 模式），Marginalia 用 CLAUDE.md 协议
4. **有摄入工作流** — Karpathy 无明确定义，Marginalia 有 schema/ingest.md