# 用户知识库工作流设计（Deepseek v4 Pro 版）

> 日期：2026-05-13
> 状态：设计稿
> 来源：与 Deepseek v4 Pro 的设计讨论

---

## 一、设计背景

本方案探索用 Deepseek v4 Pro 作为 AI 助手，驱动 Marginalia 知识库工作流。

## 二、核心工作流

### 2.1 初始化

用户运行 `python3 scripts/init.py --root ./my-kb`，系统生成：

```
./my-kb/
├── CLAUDE.md
├── docs/
│   ├── index.md
│   └── nodes/
├── project/
│   ├── project.md
│   ├── plan.md
│   ├── progress.md
│   └── open-questions.md
├── schema/
│   ├── rules.md
│   ├── node-types.md
│   ├── task-states.md
│   └── ingest.md
├── audit/
├── runtime/
└── scripts/  (symlink or copy)
```

### 2.2 日常使用

1. 用户对 AI 说需求
2. AI 读取 CLAUDE.md → 发现 schema/ → 加载规则
3. AI 按 schema/ingest.md 执行摄入
4. AI 创建节点 → 更新 index → 回写状态
5. 用户运行 audit.py 检查质量

### 2.3 质量维护

```bash
python3 scripts/audit.py --root ./my-kb
# 输出结构化报告，按 P0-P3 排序

python3 scripts/verify.py --root ./my-kb
# 语义验证
```

## 三、Deepseek v4 Pro 的特殊考虑

### 3.1 上下文窗口

Deepseek v4 Pro 的上下文窗口较大，可以一次加载更多 schema 文件。

### 3.2 指令遵循

Deepseek 在复杂指令遵循上表现稳定，适合多步骤工作流。

### 3.3 代码生成

Deepseek 的代码生成能力适合生成 init.py、audit.py 等脚本。

## 四、与其他方案的对比

| 维度 | Claude Code | Cursor + Claude | Deepseek v4 Pro |
|------|------------|-----------------|-----------------|
| CLAUDE.md 支持 | 原生 | 通过 .cursorrules | 通过系统提示 |
| Hook 支持 | 原生 | 部分支持 | 不支持 |
| 多文件编辑 | 强 | 强 | 中 |
| 上下文长度 | 中 | 中 | 大 |

## 五、适配方案

Deepseek v4 Pro 不支持 CLAUDE.md 自动加载，需要通过以下方式适配：

1. **系统提示注入**：将 CLAUDE.md 内容作为系统提示的一部分
2. **手动加载**：用户在会话开始时说"读取 CLAUDE.md 并按协议执行"
3. **API 集成**：通过 API 调用时自动注入

## 六、结论

Deepseek v4 Pro 可作为 Marginalia 的 AI 后端，但需要额外的适配工作来弥补 CLAUDE.md 自动加载的缺失。协议层（schema/）的设计是平台无关的，不受影响。