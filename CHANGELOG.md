# Changelog

本文件记录 Marginalia 边注系统的所有版本变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/)。

## [0.3.1] - 2026-05-15

### Added

- `README.md` 新增"跨工作区部署"指引：支持将 rules.md 改编为 Agent 配置文件内联段
- `README.md` 新增"版本标签"推荐：在知识库索引中使用版本标签帮助 AI 识别系统版本
- `README.md` 新增"部署后检查"警示：提醒用户清理平台默认模板中与 Marginalia 冲突的旧自动化段

## [0.3.0] - 2026-05-15

### Changed

- `rules.md` 审计触发从收工规则移到读取规则（事件驱动）：AI 在读取中发现异常时提醒用户，而非要求收工时运行 audit.py
- `rules.md` 收工规则删除"运行 audit.py"（实地报告显示 0/18 次执行）

### Added

- `audit.py` 新增 `--brief` 参数，只输出 `P0:X P1:X P2:X` 单行摘要
- `audit.py` 新增 `--exit-code-only` 参数，无输出，仅通过退出码反映状态（P0>0→2, P1>0→1, 0→0）
- `README.md` 新增"平台集成"章节，说明 Claude Code / OpenClaw / CI 场景下 audit.py 的不同运行方式

## [0.2.1] - 2026-05-15

### Fixed

- `audit.py` 模板占位符不再误报为断链（`[[wikilink]]`、`[[concepts/xxx]]` 等）
- `audit.py` 默认跳过 `templates/` 和 `archive/` 目录，减少噪声信号
- `audit.py` 支持 `[[page|alias]]` 别名和 `[[page#heading]]` 锚点语法

### Added

- `audit.py` 新增 `--external-kb-dirs` 参数，支持跨知识库引用解析
- `audit.py` 新增 `--no-skip` 参数，可回退到检查全部文件旧行为
- `node-types.md` 新增"写回位置"表和"信息分类决策"流程图
- `rules.md` 写入规则新增引用，指向 node-types.md 的写回位置决策

## [0.2.0] - 2026-05-14

### Added

- 初始公开版本
- `schema/rules.md` — AI 行为规则（读取、写入、收工、约束）
- `schema/node-types.md` — 页面类型定义（concept、decision、annotation、comparison）
- `schema/first-ingest.md` — 首次知识摄入指南
- `scripts/init.py` — 创建知识库骨架
- `scripts/audit.py` — 检查知识库健康
- `scripts/verify.py` — 验证知识库完整性
- `templates/` — 页面模板
- `example/` — 示例知识库
