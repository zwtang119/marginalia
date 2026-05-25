# Contributing

## Scope

只接受符合 `PRD.md` 与 `SPEC.md` 的变更。

## How to Propose Changes

1. 先读 `PRD.md` 与 `SPEC.md`，确认变更在项目范围内
2. 在 `project/open-questions.md` 中记录变更意图
3. 等待维护者确认后再动手

## Workflow

1. 先读 `PRD.md` 与 `SPEC.md`
2. 再读 `project/` 下状态文件
3. 明确目标与成功标准
4. 执行最小必要修改
5. 运行验证
6. 回写状态文件

## Validation

```bash
python3 scripts/audit.py --root .
python3 scripts/verify.py --root .
python3 -m unittest discover -s tests
```

## How to Submit Documentation Changes

文档修改与代码修改遵循相同流程：先确认范围，再执行最小修改，最后验证和回写。

## Changes That Require Prior Discussion

以下改动必须先在 `project/open-questions.md` 中讨论并获得维护者确认：

- 大规模目录重组
- 覆盖已有结论
- 删除大量文件
- 多种解释会显著改变系统边界

## Hard Rules

- 不引入第三方依赖
- 不把项目实现成 Web App 或数据库产品
- 不跳过验证与回写
