# Contributing

## How to Propose Changes

1. Fork 本仓库
2. 在 Fork 中修改
3. 提交 Pull Request

## What We Accept

- 对协议（schema/）的改进
- 对脚本（scripts/）的改进
- 对模板（templates/）的改进
- 对示例（example/）的改进
- Bug 修复

## Validation

```bash
python3 scripts/audit.py --root example/
python3 scripts/verify.py --root example/
```

## Hard Rules

- 不引入第三方依赖
- 不把项目实现成 Web App 或数据库产品
- 示例知识库保持精简，不超过 5 个页面
