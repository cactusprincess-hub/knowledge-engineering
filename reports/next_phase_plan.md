# 下一阶段任务拆解

本阶段目标是继续提高数据覆盖规模，完善统计证据链，并加强多源融合与质量控制模块的可复现性。

## 第一优先级：扩展 Wikidata 数据规模

目标：

- 在已有批量抓取流程基础上继续扩展实体规模。
- 将原始 SPARQL 结果转换成统一的课程项目 JSON 结构。
- 输出可统计的类别分布、来源计数和去重结果。

具体任务：

1. 运行 `scripts/fetch_wikidata_batches.py` 获取分批原始结果。
2. 使用 `scripts/normalize_wikidata_batches.py` 生成规范化实体。
3. 对缺失简介、异常类别、非软件实体做初筛。
4. 记录真实数据中的误分类样本，反向优化类别规则。

交付标准：

- `data/raw/wikidata/batches/`
- `data/interim/wikidata_entities_normalized_from_batches.json`
- `outputs/figures/wikidata_scale_normalization_stats.json`

## 第二优先级：完善本体治理统计

目标：

- 形成可写入报告的层级治理证据。
- 展示去环、单父节点约束和规范化分类树。

具体任务：

1. 补充更多 `subclass of` 边。
2. 统计发现的循环边数量、删除的循环依赖数量和多父节点裁剪数量。
3. 输出报告可引用的 summary JSON 和文本树结构。

交付标准：

- `outputs/figures/taxonomy_governance_report.json`
- `outputs/figures/taxonomy_tree.txt`

## 第三优先级：国产软件增补与实体对齐

目标：

- 用中文来源补齐 Wikidata 中覆盖不足的国产软件实体。
- 通过别名表和名称标准化降低重复率。

具体任务：

1. 整理国产软件种子集。
2. 将实体存入 `data/raw/baidubaike/`。
3. 增强 `merge_sources.py` 中的标准化命名、别名表、模糊匹配和简介融合逻辑。
4. 统计重复实体数、多源实体数和来源分布。

交付标准：

- `data/interim/merged_entities.json`
- `outputs/figures/alignment_stats.json`

## 第四优先级：前沿 AI 实体增量

目标：

- 从 2024-2025 年论文、技术报告和新闻中提取最新 AI 名词。
- 通过来源回指降低实体增量过程中的事实风险。

具体任务：

1. 收集标题级数据，例如 arXiv、GitHub Trending 和 AI 新闻标题。
2. 抽取候选实体。
3. 生成一句话简介。
4. 增加原文回指字段，保证实体来源可追溯。

交付标准：

- `data/interim/frontier_ai_entities.json`
- `outputs/figures/frontier_ai_stats.json`

## 第五优先级：报告证据链

目标：

- 每个贡献点都能通过数据文件和统计结果支撑。

报告统计项包括：

- 原始实体数。
- 去重后实体数。
- 中文增补实体数。
- 前沿 AI 增补实体数。
- 去环删除边数。
- 多父节点裁剪数。
- 简介质量控制候选条目数。
- 不合格实体过滤数。
