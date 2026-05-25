# 记忆系统对比

> **类型**：comparison
> **日期**：2026-04-28

---

## 对比维度

| 特征 | Marginalia | Mem0 | Claude-Mem | Obsidian + Dataview |
|------|-----------|------|------------|-------------------|
| 存储方式 | Markdown 文件 | 向量数据库 | JSON 文件 | Markdown + SQLite |
| 信息保真 | 无损 | 有损（Embedding） | 部分有损 | 无损 |
| 检索方式 | wikilink + grep | 向量相似度 | 关键词 | SQL 查询 |
| 平台依赖 | 无 | SDK 绑定 | Claude 绑定 | Obsidian 绑定 |
| AI 原生 | 是（批注格式） | 是 | 是 | 否 |
| 零依赖 | 是 | 否 | 否 | 否 |

---

## 结论

Marginalia 适合以下场景：
- 需要 AI 助手长期维护知识库
- 要求信息无损保留
- 不希望绑定特定平台
- 项目已有 Markdown 文档基础

向量数据库方案适合：
- 需要大规模语义搜索
- 信息精度要求不高
- 可接受平台绑定

---

## 相关页面

- [[concepts/marginalia]]: Marginalia 边注系统
- [[decisions/why-marginalia]]: 为什么选择 Marginalia
