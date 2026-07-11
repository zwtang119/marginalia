# Marginalia 边注系统

> 文档级批注记忆系统——让记忆附着在知识点旁边，实现同位、无损、解耦。

## 这是什么？

Marginalia 是一个 AI 助手驱动的知识管理系统。它不是数据库，不是 RAG 引擎，不是在线服务。它是：

- 一套 AI 助手能理解的协议规则（`schema/`）
- 一组可运行的工具脚本（`scripts/`）
- 一个示例知识库（`example/`）
- 一套页面模板（`templates/`）

## 使用场景

```
你的项目（如 ~/github/CDS）
    │
    ▼ 你对 AI 说：
    "参照 ~/download/marginalia，在我的项目里搭建知识库"
    │
    ▼ AI 自动完成：
    1. 创建 wiki/ 知识库骨架
    2. 扫描你的项目文档
    3. 提案分类，你确认后摄入
    4. 之后每次对话自动读取和更新知识库
```

## 快速开始

### 前提

- 一个 AI 编程助手（Claude Code、Cursor、Cline 等）
- 一个你想管理知识的项目

### 步骤

```bash
# 1. Clone 本仓库
git clone https://github.com/zwtang119/marginalia.git ~/download/marginalia

# 2. 在你的项目中，对 AI 说：
#    "参照 ~/download/marginalia，在我的项目里搭建知识库，并摄入文档"

# 3. AI 会自动完成一切
```

### 可选：手动初始化

```bash
python3 ~/download/marginalia/scripts/init.py --root ./my-project
python3 ~/download/marginalia/scripts/audit.py --root ./my-project/wiki
python3 ~/download/marginalia/scripts/verify.py --root ./my-project/wiki
```

## 核心概念

| 特征 | 说明 |
|------|------|
| **同位** | 记忆与知识点同位置——读知识点，即读记忆 |
| **无损** | 原始论据完整保留——不经过 Embedding 压缩 |
| **解耦** | 纯 Markdown 文件——独立于任何平台 |

## 目录结构

```
Marginalia/
├── CLAUDE.md              # AI 助手发现层入口
├── schema/                # 协议规则
│   ├── rules.md           #   AI 行为规则
│   ├── node-types.md      #   页面类型定义
│   └── first-ingest.md    #   首次摄入指南
├── scripts/               # 工具脚本（零依赖 Python）
│   ├── init.py            #   创建知识库骨架
│   ├── audit.py           #   检查知识库健康
│   └── verify.py          #   验证知识库完整性
├── templates/             # 页面模板
└── example/               # 示例知识库
```

## 三阶段工作流

### 阶段 1：初始化

AI 在你的项目中创建 `wiki/` 目录和索引文件。

### 阶段 2：首次摄入

AI 扫描你的项目文档，半自动分类为概念、决策或对比，并在相关页面以 `> [!memo]` 形式添加批注，确认后写入知识库。

### 阶段 3：日常使用

每次对话，AI 自动读取知识库、写入新知识。如 AI 在读取中发现断链或孤儿页，会提醒你运行 audit.py 检查。

## 平台集成

Marginalia 的工具在协议层兼容所有平台——纯 Markdown + 零依赖 Python。

### audit.py 的不同运行方式

```bash
# Claude Code / 手动：完整 JSON 报告
python3 scripts/audit.py --root wiki/

# OpenClaw / heartbeat：单行摘要
python3 scripts/audit.py --root wiki/ --brief

# CI/CD 流水线：仅退出码（P0>0→2, P1>0→1, 0→0）
python3 scripts/audit.py --root wiki/ --exit-code-only
```

### 跨工作区部署

当 Agent 工作区与 Marginalia 仓库不在同一路径时，可将 `schema/rules.md` 改编为 Agent 配置文件的"内联段"。内联段应标注协议版本（如 `协议版本：Marginalia vX.Y.Z`），方便后续对照升级。

### 版本标签

在知识库索引文件中推荐使用版本标签，帮助 AI 识别知识库系统及版本：

> 知识库 → `wiki/`（Marginalia vX.Y.Z）

### 部署后检查

> ⚠️ 部署 Marginalia 后，检查 Agent 配置文件中是否存在来自平台默认模板的旧自动化段（如心跳、定期检查）。这些旧段可能与 Marginalia 的维护架构冲突。解决方法：删除或缩减旧段，替换为指向 Marginalia 工具的引用。

## 许可证

MIT
