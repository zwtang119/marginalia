# Marginalia Example Wiki Plan

> 日期：2026-05-12
> 状态：规划中

---

## 一、目的

为 Marginalia 项目创建一个示例 wiki，展示协议的实际使用方式。

## 二、示例内容

示例 wiki 将包含以下知识节点：

1. **Concept: 知识节点** — Marginalia 的核心概念
2. **Concept: 质量退化** — 知识库面临的质量挑战
3. **Entity: GPT54** — 本项目的实体信息
4. **Decision: 选择 Markdown 而非数据库** — 关键设计决策

## 三、结构

```
docs/
├── index.md
└── nodes/
    ├── concept-knowledge-node.md
    ├── concept-quality-degradation.md
    ├── entity-gpt54.md
    └── decision-markdown-over-database.md
```

## 四、验证标准

- [ ] audit.py 报告 0 个 P0/P1
- [ ] verify.py 通过语义验证
- [ ] index.md 覆盖所有节点