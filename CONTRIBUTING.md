# 协作与提交流程

本仓库采用稳定主干加功能分支的方式维护，保证每次提交都有清晰目的，并且主分支始终保留可运行版本。

## 分支规范

- 稳定分支：`main`
- 功能分支：`feature/<task-name>`
- 修复分支：`fix/<issue-name>`
- 文档分支：`docs/<topic-name>`

每一轮改动遵循：

1. 从最新 `main` 切出任务分支。
2. 只提交与当前任务相关的代码、数据样本或文档。
3. 本地运行相关脚本和测试。
4. 推送远端分支并检查改动差异。
5. 确认无误后合并回 `main`。

## Commit Message 规范

推荐使用 `类型: 描述`：

- `feat: 增加 Wikidata 实体过滤算法`
- `fix: 修复分类环路检测问题`
- `docs: 更新实验报告中的数据流转图`
- `refactor: 重构实体对齐逻辑`
- `test: 增加 Wikidata 规范化测试`

避免使用含义不清的提交信息，例如 `update`、`test`、`111`。

## 大文件规范

- 原始大数据文件如果超过 `50MB`，不直接提交到仓库。
- 仓库中优先保留小样本数据、规范化统计摘要和数据获取脚本。
- 全量原始数据保留在本地缓存目录，必要时重新运行脚本生成。

## 提交前检查

提交前检查远端差异：

- 是否包含多余调试输出。
- 是否误删代码或配置。
- 是否误提交大文件。
- 提交信息是否清楚描述本轮改动。

## 推荐命令

```bash
git checkout main
git pull origin main
git checkout -b feature/<task-name>
python3 scripts/run_pipeline.py
python3 tests/test_taxonomy.py
git add .
git commit -m "feat: <task-summary>"
git push -u origin feature/<task-name>
```
