# Plan

- 当前目标：完成 M1.5 协议发现与首次摄入入口
- 成功标准：初始化结果包含 CLAUDE.md 发现层标记段；schema/ingest.md 存在且字段完整；audit.py 可检测协议发现入口和摄入规则缺失；README.md 足以让普通用户完成首次初始化并触发第一次摄入
- 当前阶段：M1.5
- 步骤列表：
  - 写入 schema/ingest.md
  - 升级 init.py 增加 --update-protocol 和 --platform 参数
  - 升级 audit.py 增加 M1.5 专项审计
  - 写入 test_protocol_discovery.py
  - 运行完整测试矩阵
- 当前执行中的一步：准备进入 M2 规划
- 后续候选步骤：
  - 增加节点摄入脚本
  - 增加快照对比
  - 增加审计 Markdown 报告
