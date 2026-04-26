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

## 推荐命令

```bash
git checkout main
git pull origin main
git checkout -b codex/<task-name>
python3 scripts/run_pipeline.py
python3 tests/test_taxonomy.py
git add .
git commit -m "<task-summary>"
git push -u origin codex/<task-name>
```

## 当前阶段建议

- 初始骨架提交到 `main`
- 真实 Wikidata 接入放到 `codex/wikidata-ingest`
- 中文实体增强放到 `codex/baike-alignment`
- 前沿 AI 增量放到 `codex/frontier-ai-enrichment`
