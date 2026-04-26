# 软件与 AI 生态知识图谱课程项目

这个项目是为“知识工程/知识图谱”课程作业准备的最小可执行骨架，围绕 4 个老师容易认可的贡献点展开：

1. 拓扑结构治理：`subclass of` 去环、单父节点约束、层级规范化。
2. 知识消歧与融合：Wikidata、中文来源、前沿 AI 增量数据的对齐与去重。
3. 非结构化增量：从新闻、论文、GitHub Trending 标题中抽取新实体。
4. 噪声过滤：简介清洗、长度控制、类别校验、自动化 QC。

## 目录结构

```text
software_ai_kg/
├── configs/
├── data/
│   ├── raw/
│   │   ├── baidubaike/
│   │   ├── frontier_ai/
│   │   └── wikidata/
│   ├── interim/
│   └── final/
├── outputs/
│   └── figures/
├── reports/
├── scripts/
├── src/
│   └── software_ai_kg/
└── tests/
```

## 快速开始

```bash
cd 项目根目录
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 scripts/run_pipeline.py
python3 tests/test_taxonomy.py
```

运行后会生成：

- `data/interim/frontier_ai_entities.json`
- `data/interim/taxonomy_tree.json`
- `data/interim/merged_entities.json`
- `data/final/entities.json`
- `outputs/figures/project_summary.json`

## 当前骨架已经包含

- 一个可复现的示例数据流
- `Wikidata` 子类边去环与单父节点选择
- 多源实体清洗、对齐、融合
- 简介压缩到 50 字以内
- 基础质量控制与过滤
- 报告提纲与“邀功”表述草稿

## 后续扩展顺序

1. 把 `data/raw/wikidata/` 换成真实 SPARQL 拉取结果。
2. 把 `data/raw/baidubaike/` 换成你实际补充的国产软件数据。
3. 把 `data/raw/frontier_ai/demo_titles.json` 换成机器之心、arXiv、GitHub Trending 标题。
4. 如果你要接入 LLM，把摘要与校验逻辑补到 `scripts/extract_frontier_ai.py` 或单独的 `llm_enrich.py`。

## 开发工作流

- `main`：保持可运行、可提交的稳定版本。
- `codex/*`：每一轮任务先从 `main` 拉新分支开发。
- 完成开发后先本地运行脚本与测试，再推送分支。
- 验证无误后再发起 PR 合并回 `main`。
- 提交信息尽量使用 `类型: 描述`，例如 `feat: 增加 Wikidata 实体规范化脚本`。
- 大于 `50MB` 的原始数据不要直接提交到 Git，仓库里只保留样本与统计结果。

建议分支命名：

- `codex/wikidata-ingest`
- `codex/baike-alignment`
- `codex/frontier-ai-enrichment`
- `codex/report-polish`

## Wikidata 接入流程

```bash
python3 scripts/fetch_wikidata.py --limit 100
python3 scripts/fetch_wikidata.py --limit 100 --offset 100
python3 scripts/normalize_wikidata.py
```

完成后会新增：

- `outputs/figures/wikidata_normalization_stats.json`
- 可选的本地大文件 `data/raw/wikidata/wikidata_entities_raw.json`
- 可选的本地中间文件 `data/interim/wikidata_entities_normalized.json`

如果本机代理会拦截 HTTPS 证书，可以在抓取时加：

```bash
python3 scripts/fetch_wikidata.py --limit 100 --insecure
```

这个选项只建议在本地代理环境下使用。
