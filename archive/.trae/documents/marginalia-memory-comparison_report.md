# Marginalia 记忆系统对比报告

> 日期：2026-05-12
> 状态：已完成

---

## 一、对比范围

本报告对比以下记忆系统方案：

1. **Karpathy LLM Wiki** — 最简模式
2. **mem0** — API 驱动
3. **claude-mem** — 文件驱动
4. **Marginalia (GPT54)** — 协议驱动

## 二、对比维度

### 2.1 存储方式

| 方案 | 存储 | 优势 | 劣势 |
|------|------|------|------|
| Karpathy | Markdown 文件 | 人类可读、Git 友好 | 无结构约束 |
| mem0 | 向量数据库 | 语义搜索强 | 需要外部服务 |
| claude-mem | Markdown 文件 | 简单 | 无质量保障 |
| Marginalia | Markdown 文件 | 结构化 + 质量保障 | 初始设置成本 |

### 2.2 驱动机制

| 方案 | 驱动 | 可靠性 |
|------|------|--------|
| Karpathy | Hook (superpowers) | 高 |
| mem0 | API 调用 | 高 |
| claude-mem | 无 | 低 |
| Marginalia | 协议 + 脚本 | 中 |

### 2.3 质量保障

| 方案 | 机制 | 覆盖范围 |
|------|------|---------|
| Karpathy | 无 | 0% |
| mem0 | 无 | 0% |
| claude-mem | 无 | 0% |
| Marginalia | audit + verify | 80%+ |

## 三、结论

Marginalia 在质量保障方面有独特优势，在驱动可靠性上介于 Hook 方案和无驱动方案之间。

## 四、建议

1. 短期：完善 audit.py 的检测覆盖率
2. 中期：考虑 Hook 驱动作为可选增强
3. 长期：根据使用数据调整类型系统