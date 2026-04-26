# 协作与提交流程

这个仓库采用稳定主干加功能分支的方式维护。

## 分支规范

- 稳定分支：`main`
- 开发分支：`codex/<task-name>`

每一轮改动建议都遵循：

1. 从最新 `main` 切出新分支。
2. 只在当前任务分支内提交相关改动。
3. 本地运行最相关的脚本和测试。
4. 推送远端后发起 PR。
5. PR 检查通过后合并回 `main`。

## Commit Message 规范

推荐使用 `类型: 描述`：

- `feat: 增加 Wikidata 实体过滤算法`
- `fix: 修复分类环路检测的死循环问题`
- `docs: 更新实验报告中的数据流转图`
- `refactor: 重构实体对齐逻辑`
- `test: 增加 Wikidata 规范化测试`

避免使用：

- `update`
- `test`
- `111`

## 大文件规范

- 原始大数据文件如果超过 `50MB`，不要直接提交到仓库。
- 仓库中优先保留：
  - 小样本数据
  - 规范化后的统计摘要
  - 数据获取脚本
- 真实全量数据保留在本地，或者压缩后单独管理。

## PR 自查

提交 PR 前，建议先看 GitHub 的 `Files changed`：

- 有没有多余的调试输出
- 有没有误删代码
- 有没有把大文件误加进仓库
- 提交信息是否清楚描述本轮改动

## 推荐命令

```bash
git checkout main
git pull origin main
git checkout -b codex/<task-name>
python3 scripts/run_pipeline.py
python3 tests/test_taxonomy.py
git add .
git commit -m "feat: <task-summary>"
git push -u origin codex/<task-name>
```

## 当前阶段建议

- 初始骨架提交到 `main`
- 真实 Wikidata 接入放到 `codex/wikidata-ingest`
- 中文实体增强放到 `codex/baike-alignment`
- 前沿 AI 增量放到 `codex/frontier-ai-enrichment`
