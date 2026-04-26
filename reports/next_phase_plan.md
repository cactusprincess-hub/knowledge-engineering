# 下一阶段任务拆解

这一阶段的目标不是继续“铺大饼”，而是把课程项目推进到“有真实数据、有统计证据、能写进报告”的状态。

## 第一优先级：接入真实 Wikidata 数据

目标：

- 拉取第一批真实软件实体，建议先做 `500-1000` 条验证流程，再扩到 `5000+`。
- 把原始 SPARQL 结果转换成统一的课程项目 JSON 结构。
- 输出可统计的类别分布和来源计数。

具体任务：

1. 运行 `scripts/fetch_wikidata.py` 获取原始结果。
2. 新建 `scripts/normalize_wikidata.py`，把 SPARQL 返回字段映射成：
   - `id`
   - `entity`
   - `category`
   - `description`
   - `source`
   - `level`
3. 对缺失简介、异常类别、非软件实体做一次初筛。

交付标准：

- `data/raw/wikidata/wikidata_entities_raw.json`
- `data/interim/wikidata_entities_normalized.json`

## 第二优先级：完成本体治理统计

目标：

- 不只是“去环”，而是要能给报告写出量化结果。

具体任务：

1. 补充更多 `subclass of` 边。
2. 统计：
   - 发现了多少条循环边
   - 删除了多少条循环依赖
   - 裁剪了多少条多父节点边
3. 输出一个可直接引用到报告中的 summary JSON。

交付标准：

- `data/interim/taxonomy_tree.json`
- `outputs/figures/taxonomy_stats.json`

## 第三优先级：国产软件增补与实体对齐

目标：

- 用中文来源补齐 Wikidata 中覆盖不全的实体。

具体任务：

1. 先人工整理一个 `50-100` 条国产软件种子集。
2. 把这些实体存入 `data/raw/baidubaike/` 或独立 CSV/JSON。
3. 继续增强 `merge_sources.py`：
   - 标准化命名
   - 别名表
   - 模糊匹配
   - 简介融合
4. 对最终重复实体数做统计。

交付标准：

- `data/interim/merged_entities.json`
- `outputs/figures/alignment_stats.json`

## 第四优先级：前沿 AI 实体增量

目标：

- 从 2024-2025 的论文、技术报告、新闻中提取最新 AI 名词。

具体任务：

1. 收集一批标题级数据：
   - arXiv
   - GitHub Trending
   - 机器之心或其他 AI 新闻
2. 抽取候选实体。
3. 用规则或 LLM 生成一句话简介。
4. 增加“原文回指”字段，降低幻觉风险。

交付标准：

- `data/interim/frontier_ai_entities.json`
- `outputs/figures/frontier_ai_stats.json`

## 第五优先级：报告证据链

目标：

- 每个贡献点都能拿出数据和文件支撑。

你最后报告里最好出现这几类数字：

- 原始实体数
- 去重后实体数
- 中文增补实体数
- 前沿 AI 增补实体数
- 去环删除边数
- 多父节点裁剪数
- 简介平均长度
- 不合格实体过滤数
