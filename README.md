# 软件与 AI 生态知识图谱

本项目面向知识工程课程作业，围绕“软件与 AI 生态”构建一个具有分层结构、可复现处理流程和质量控制证据的知识图谱。项目重点不是简单堆积词条，而是对多源实体进行规范化、去重、层级治理和简介质量控制。

## 项目目标

项目将实体组织为三级结构：

1. 一级类别：软件与 AI 生态。
2. 二级类别：系统软件、应用软件、人工智能模型与应用、开发工具与框架等。
3. 三级实体：具体软件、模型、工具或框架，例如 Windows 11、WeChat、PyTorch、DeepSeek-V3。

主要工程目标包括：

- 从 Wikidata 批量获取软件相关实体，形成 5000 条以上的基础实体库。
- 清理 `subclass of` 层级中的循环依赖、多父节点和冗余路径，形成稳定的分类树。
- 引入中文来源补充国产软件，并完成中英文别名对齐和实体融合。
- 对过短、过长、英文描述和泛化描述进行自动质量检查，生成统一格式的一句话简介。

## 当前结果

截至当前版本，项目已经形成一套完整的可复现实验流程：

- Wikidata 原始抓取记录：6069 条。
- 规范化后可用实体：5325 条。
- 全局 QID 去重删除重复记录：248 条。
- 检测到跨类别重叠实体：19 条。
- 本体治理处理中删除循环边：3 条。
- 本体治理处理中裁剪多父节点边：5 条。
- 中文来源种子实体：20 条。
- 多源融合后实体：27 条。
- 简介质量控制候选条目：1742 条。

详细处理过程见 [reports/processing_report.md](reports/processing_report.md)。

## 目录结构

```text
software_ai_kg/
├── configs/                  # 分类映射、批量抓取目标、别名配置
├── data/
│   ├── raw/                  # 原始样本与本地抓取缓存
│   ├── interim/              # 中间处理结果
│   └── final/                # 最终实体输出
├── outputs/
│   └── figures/              # 统计结果、治理报告、文本树结构
├── reports/                  # 实验报告与处理说明
├── scripts/                  # 可执行数据处理脚本
├── src/software_ai_kg/       # 核心处理模块
└── tests/                    # 单元测试
```

## 运行方式

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 scripts/run_pipeline.py
python3 tests/test_taxonomy.py
```

## 核心流程

### 1. Wikidata 批量抓取

```bash
python3 scripts/fetch_wikidata_batches.py --batch-size 200 --max-batches 1 --insecure --log-file outputs/logs/wikidata_scale.log
python3 scripts/normalize_wikidata_batches.py
```

该流程会按软件子类分批抓取实体，并基于 QID 进行全局去重。原始批次数据保存在 `data/raw/wikidata/batches/`，统计结果保存在 `outputs/figures/`。

### 2. 本体治理

```bash
python3 scripts/generate_taxonomy_report.py
```

该流程会对分类边进行去环、单父节点选择和人工规则校正，输出：

- `outputs/figures/taxonomy_governance_report.json`
- `outputs/figures/taxonomy_tree.txt`

### 3. 中文增强与多源融合

```bash
python3 scripts/merge_sources.py
```

该流程读取 Wikidata 样本、中文软件种子数据和中英文别名表，完成实体对齐、去重和来源合并。典型融合样例包括 WeChat/微信、WPS Office/WPS、Windows 11。

### 4. 简介质量控制

```bash
python3 scripts/summarize_descriptions.py --limit 100
```

该流程用于识别描述过短、过长、语言不统一或内容过于泛化的条目，并生成规范化的一句话简介。当前版本默认采用离线规则实现，保证不新增原始来源之外的事实；后续也可以在同一接口下替换为人工审核或模型辅助摘要。

## 可复现产物

- `data/interim/wikidata_entities_normalized_from_batches.json`
- `data/interim/merged_entities.json`
- `data/interim/description_qc_sample.json`
- `outputs/figures/wikidata_scale_normalization_stats.json`
- `outputs/figures/taxonomy_governance_report.json`
- `outputs/figures/alignment_stats.json`
- `outputs/figures/description_qc_stats.json`

## 说明

仓库中保留脚本、样本数据和统计结果。大规模原始抓取数据默认通过 `.gitignore` 排除，避免仓库体积过大；需要复现实验时可重新运行抓取脚本生成本地缓存。
