# Tasks

## Phase 1：层级四交付（本周）

- [ ] Task 1：在目标项目的 CLAUDE.md 中追加记忆系统协议段落（~80行）
  - [ ] SubTask 1.1：编写"会话启动"规则（读 index.md → 读相关页面 → 说明知道了什么）
  - [ ] SubTask 1.2：编写"任务完成"规则（问自己有没有新知识 → 写入对应类型 → 更新 index）
  - [ ] SubTask 1.3：编写"反逃避表"（4 条核心逃避想法及反驳）
  - [ ] SubTask 1.4：编写"页面类型"定义（Concept 核心类型 + Entity/Source/Decision 按需类型）
  - [ ] SubTask 1.5：编写"质量底线"（断链=0，有定义，index 覆盖）
  - [ ] SubTask 1.6：创建 wiki/ 目录结构（concepts/ + index.md），其他按需

- [ ] Task 2：验证层级四——在目标项目上执行一次真实任务，验证闭环
  - [ ] SubTask 2.1：开始新会话，观察 AI 是否自动读 wiki/index.md
  - [ ] SubTask 2.2：执行一个真实任务
  - [ ] SubTask 2.3：任务完成后，观察 AI 是否判断有新知识并写回 wiki
  - [ ] SubTask 2.4：开始第二次会话，验证能读到上一步写入的内容

- [ ] Task 3：根据 Task 2 的验证结果，记录发现和问题
  - [ ] SubTask 3.1：记录 AI 遵守规则的程度
  - [ ] SubTask 3.2：记录 AI 逃避规则的方式（如有）
  - [ ] SubTask 3.3：记录实际使用了哪些页面类型
  - [ ] SubTask 3.4：决定是否需要演进到层级三（增加更详细的行为约束和工作流）

## Phase 2：按需演进（视 Phase 1 结果决定）

- [ ] Task 4（可选）：演进到层级三——增强 CLAUDE.md 的行为约束和完整工作流
  - [ ] SubTask 4.1：根据 Phase 1 发现的逃避方式，扩展反逃避表
  - [ ] SubTask 4.2：增加完整的页面类型模板（每种类型的最小格式定义）
  - [ ] SubTask 4.3：增加 lint 工作流规则（定期自检断链和矛盾）
  - [ ] SubTask 4.4：增加 ingest / query / writeback 最小工作流步骤
  - [ ] SubTask 4.5：增加 log.md 维护规则

- [ ] Task 5（可选）：演进到层级二——增强 audit_wiki.py
  - [ ] SubTask 5.1：增加优先级排序输出（P0-P3）
  - [ ] SubTask 5.2：增加稳定性度量（总缺陷数变化趋势）
  - [ ] SubTask 5.3：合并 SKILL.md 规则到 CLAUDE.md

- [ ] Task 6（可选）：演进到层级一——增加 Hook 自动驱动
  - [ ] SubTask 6.1：编写 session-start Hook（参考 superpowers）
  - [ ] SubTask 6.2：编写独立的 using-wiki Skill 文件
  - [ ] SubTask 6.3：编写 post-tool-use Hook（检测写回机会）

# Task Dependencies

- [Task 2] depends on [Task 1]
- [Task 3] depends on [Task 2]
- [Task 4] depends on [Task 3]（仅在 Phase 1 发现 AI 逃避规则时）
- [Task 5] depends on [Task 3]（仅在 LLM 自检不够准确时）
- [Task 6] depends on [Task 4] and [Task 5]（仅在需要全自动驱动时）