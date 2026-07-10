# 作业提交说明

本项目的提交内容围绕“软件与 AI 生态一句话知识百科”展开，重点体现实体集规模、领域完整性、知识图谱层级治理和自然语言简介质量控制。

## 提交包生成

在项目根目录运行：

```bash
python3 scripts/package_submission.py
```

运行后会生成：

- `dist/knowledge_engineering_submission/`
- `dist/knowledge_engineering_submission.zip`

压缩包可直接上传到课程平台。GitHub 仓库保留源码、报告、统计结果和打包脚本；完整实体集会在本地提交包中一并整理。

## 提交包内容

- `README_提交说明.md`：面向老师的项目概览、数据规模和复现命令。
- `项目处理报告.md`：数据处理流程、实体规模、本体治理、多源融合和质量控制说明。
- `data/entities_5325.json`：Wikidata 批量规范化后的 5325 条一句话百科实体。
- `data/chinese_fusion_entities.json`：中文来源增强和中英文实体对齐样本。
- `data/description_qc_sample.json`：简介质量控制样本。
- `outputs/statistics/`：规模统计、去环报告、实体融合统计和简介质量控制统计。
- `code/`：源码、脚本、配置和测试文件。

## GitHub 仓库

公开仓库地址：

https://github.com/cactusprincess-hub/knowledge-engineering

## 推荐提交备注

本项目构建了一个面向软件与 AI 生态的专门领域一句话知识百科实体集，包含 5325 条规范化实体，并补充了本体去环、单父节点约束、多源实体融合和简介质量控制等处理流程。
