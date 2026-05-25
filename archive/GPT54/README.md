# GPT54

GPT54 是一个原创的、零依赖的、文件系统优先的开源知识工程协议系统。

它用于在本地目录中构建、维护和审计一个可持续演进的知识库，并用协议约束 AI 助手的行为。它不是 Web App，不是数据库，不是插件平台，也不是在线服务。

## 快速判断

如果以下三项大体符合你，GPT54 适合你：

- 你希望和 AI 助手协作维护长期知识资产，而不是只做临时问答
- 你希望知识库可审计、可追踪、纯本地保存
- 你能接受用 Markdown 和目录结构管理知识，而不是依赖图形界面

如果你想要的是实时协作平台、联网搜索服务、向量数据库或可视化应用，GPT54 不适合你。

## 两条路径

### 1. 协议消费者路径

适合大多数用户。你把 GPT54 当作协议和参考实现，用它生成你自己的知识库。

目标：

- 初始化一个本地知识库
- 让 AI 助手读懂规则
- 开始新增节点、审计和修正

### 2. 协议贡献者路径

适合要修改协议本身的人。你直接维护 GPT54 仓库，修改规则、脚本和测试。

## 快速开始

```bash
python3 scripts/init.py --root ./my-kb
cd ./my-kb
python3 scripts/audit.py --root .
python3 scripts/verify.py --root .
```

完成初始化后，用 AI 助手打开 `./my-kb`，然后说一句类似的话：

```text
帮我创建一个关于机器学习的 concept 节点，并按当前协议更新索引、任务记录和进展。
```

## 常用命令

```bash
python3 scripts/init.py --root ./my-kb
python3 scripts/audit.py --root ./my-kb
python3 scripts/verify.py --root ./my-kb
python3 -m unittest discover -s tests
```

M1.5 后额外支持：

```bash
python3 scripts/init.py --root ./my-kb --update-protocol
python3 scripts/init.py --root ./my-kb --platform cursor
```

## 核心工作流

GPT54 的最小闭环是：

1. 初始化
2. 摄入
3. 审计
4. 修正
5. 验证与回写

没有验证和回写的修改，不算完成。

## 关键文件

- `PRD.md`：产品定义，回答"做什么、为什么做、什么不做"
- `SPEC.md`：执行合同，回答"必须怎样做才算对"
- `IMPLEMENTATION_PLAN.md`：分阶段实施计划

## 目录说明

- `docs/`：知识节点与导航
- `project/`：项目目标、计划、进展与开放问题
- `schema/`：规则、节点类型、状态机与摄入工作流
- `audit/`：审计基线、报告与快照
- `runtime/`：任务态记录与执行日志
- `scripts/`：零依赖脚本（init、audit、verify）
- `tests/`：单元测试与冒烟测试

## AI 助手如何进入协议

GPT54 采用"发现层 -> 协议层 -> 执行层 -> 数据层"的分离设计：

- 发现层：`CLAUDE.md` 或其他平台规则文件，负责把 AI 指向 `schema/`
- 协议层：`schema/`，定义规则、状态机和摄入工作流
- 执行层：`scripts/`，提供 `init`、`audit`、`verify`
- 数据层：`docs/`、`project/`、`audit/`、`runtime/`

对于生成出来的知识库，AI 助手应先读取发现层文件，再按规则文件继续执行。

## 这是什么 / 这不是什么

### GPT54 是

- 一个零依赖的知识工程协议系统
- 一个约束 AI 助手行为的执行合同
- 一个以文件系统为基础的可审计知识库骨架

### GPT54 不是

- 知识管理 SaaS
- 向量数据库或检索服务
- 图形界面优先的笔记应用
- 插件市场或自动化平台

## 当前状态

当前文档已经完成：

- `PRD.md`
- `SPEC.md`
- `IMPLEMENTATION_PLAN.md`

当前实现还未完成：

- `scripts/init.py`
- `scripts/audit.py`
- `scripts/verify.py`
- `schema/ingest.md`

## 贡献

见 `CONTRIBUTING.md`。

## 许可证

见 `LICENSE`。
