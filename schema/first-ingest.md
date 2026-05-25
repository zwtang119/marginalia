# 首次知识摄入指南

> 本文件在首次摄入完成后可删除。

## 扫描规则

- 识别：*.md, *.txt, *.rst
- 跳过：node_modules/, .git/, build/, dist/, vendor/
- 优先：README.md, docs/, design/, adr/, decisions/

## 分类原则

- 概念/机制/术语定义 → concept
- 技术选型/方案决策 → decision
- 会议/笔记/历史记录 → annotation
- 多方案对比 → comparison

## 执行步骤

1. 扫描用户项目目录，识别可摄入文档
2. 列出文档清单 + 建议分类，等用户确认
3. 确认后按 templates/ 中的模板写入知识库
4. 更新 wiki/index.md
5. 运行 audit.py 确认无问题
6. 在用户项目的 CLAUDE.md 中追加知识库引用段落
7. 提示用户：首次摄入指南文件可以删除
