# 扩展方向说明

本项目已完成软件与 AI 生态一句话知识百科的主体构建。后续扩展可围绕数据规模、中文覆盖、前沿实体和应用展示四个方向展开。

## 1. Wikidata 规模扩展

已有批量抓取流程支持按类别分批获取实体。继续扩展时，可增加抓取目标和批次数，并保持 QID 全局去重、类别映射和简介质量控制流程不变。

主要产物：

- `data/raw/wikidata/batches/`
- `data/interim/wikidata_entities_normalized_from_batches.json`
- `outputs/figures/wikidata_scale_normalization_stats.json`

## 2. 本体治理增强

层级治理部分可继续补充更多 `subclass of` 边，扩大循环依赖和多父节点裁剪样本，使本体结构覆盖更多软件子领域。

主要产物：

- `outputs/figures/taxonomy_governance_report.json`
- `outputs/figures/taxonomy_tree.txt`

## 3. 中文软件生态补充

中文增强部分可继续扩充国产软件种子集，包括办公协作、社交通信、图像视频处理、国产操作系统和金融商业软件等类别。实体对齐仍采用标准化名称、别名表和类别约束相结合的方式。

主要产物：

- `data/raw/baidubaike/seed_cn_software.json`
- `data/interim/merged_entities.json`
- `outputs/figures/alignment_stats.json`

## 4. 前沿 AI 实体增量

前沿实体可继续从论文标题、技术报告和科技新闻中抽取，并保留原始来源字段，保证每条新增实体均可追溯。

主要产物：

- `data/interim/frontier_ai_entities.json`
- `outputs/figures/frontier_ai_stats.json`

## 5. 应用展示

在现有实体集基础上，可进一步构建检索、可视化和问答应用，例如按类别浏览实体、展示本体树状结构、查询实体简介和来源。
