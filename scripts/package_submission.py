#!/usr/bin/env python3
"""生成课程提交目录和压缩包。"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PACKAGE_DIR = DIST / "knowledge_engineering_submission"


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def entity_count(path: Path) -> int:
    payload = load_json(path)
    if isinstance(payload, dict) and "entities" in payload:
        return len(payload["entities"])
    if isinstance(payload, list):
        return len(payload)
    return 0


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def copy_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(
        src,
        dst,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
    )


def copy_project_runtime_data(code_dir: Path) -> None:
    """复制提交包内脚本运行所需的小型数据文件。"""
    raw_files = [
        ROOT / "data/raw/wikidata/demo_entities.json",
        ROOT / "data/raw/wikidata/demo_subclass_edges.json",
        ROOT / "data/raw/wikidata/demo_wikidata_entities_raw.json",
        ROOT / "data/raw/baidubaike/demo_entities.json",
        ROOT / "data/raw/baidubaike/seed_cn_software.json",
        ROOT / "data/raw/frontier_ai/demo_titles.json",
    ]
    for src in raw_files:
        copy_file(src, code_dir / src.relative_to(ROOT))

    interim_files = [
        ROOT / "data/interim/frontier_ai_entities.json",
        ROOT / "data/interim/wikidata_entities_normalized_from_batches.json",
        ROOT / "data/interim/merged_entities.json",
        ROOT / "data/interim/description_qc_sample.json",
    ]
    for src in interim_files:
        copy_file(src, code_dir / src.relative_to(ROOT))

    for src in (ROOT / "outputs/figures").glob("*"):
        if src.is_file():
            copy_file(src, code_dir / src.relative_to(ROOT))


def write_submission_readme(path: Path) -> None:
    wikidata_entities = entity_count(ROOT / "data/interim/wikidata_entities_normalized_from_batches.json")
    merged_entities = entity_count(ROOT / "data/interim/merged_entities.json")
    qc_sample = entity_count(ROOT / "data/interim/description_qc_sample.json")
    stats = load_json(ROOT / "outputs/figures/wikidata_scale_normalization_stats.json")
    taxonomy = load_json(ROOT / "outputs/figures/taxonomy_governance_report.json")

    path.write_text(
        "\n".join(
            [
                "# 知识工程作业提交说明",
                "",
                "## 项目主题",
                "",
                "软件与 AI 生态一句话知识百科实体集。",
                "",
                "## 作业要求对应",
                "",
                "- 知识图谱结构化部分：通过三级分类、本体去环和单父节点约束组织实体。",
                "- 非结构化自然语言部分：每个实体保留一句话简介，并对简介长度和质量进行控制。",
                "- 完整性目标：聚焦软件与 AI 生态，覆盖操作系统、编程语言、数据库、应用软件、开发工具和前沿 AI 实体。",
                "",
                "## 数据规模",
                "",
                f"- Wikidata 批量规范化实体：{wikidata_entities} 条。",
                f"- 中文来源融合样本：{merged_entities} 条。",
                f"- 简介质量控制样本：{qc_sample} 条。",
                f"- 原始抓取记录：{stats['raw_records']} 条。",
                f"- 去重删除记录：{stats['duplicate_records_removed']} 条。",
                f"- 本体去环删除边：{taxonomy['cycle_edge_count']} 条。",
                f"- 多父节点裁剪边：{taxonomy['multi_parent_pruned_edge_count']} 条。",
                "",
                "## 目录说明",
                "",
                "- `data/entities_5325.json`：主要实体集，每条记录包含实体名、类别、来源和一句话简介。",
                "- `data/chinese_fusion_entities.json`：中文增强和实体对齐结果。",
                "- `data/description_qc_sample.json`：简介质量控制样本。",
                "- `outputs/statistics/`：规模统计、本体治理、融合去重和简介质量控制证据。",
                "- `code/`：项目源码、脚本、配置和测试文件。",
                "- `项目处理报告.md`：完整处理流程说明。",
                "",
                "## 复现命令",
                "",
                "```bash",
                "pip install -r code/requirements.txt",
                "python3 code/scripts/generate_taxonomy_report.py",
                "python3 code/scripts/merge_sources.py",
                "python3 code/scripts/summarize_descriptions.py --limit 100",
                "python3 code/tests/test_taxonomy.py",
                "python3 code/tests/test_alignment.py",
                "python3 code/tests/test_summary_qc.py",
                "```",
                "",
                "## GitHub",
                "",
                "https://github.com/cactusprincess-hub/knowledge-engineering",
                "",
            ]
        ),
        encoding="utf-8",
    )


def build_package() -> Path:
    if PACKAGE_DIR.exists():
        shutil.rmtree(PACKAGE_DIR)
    PACKAGE_DIR.mkdir(parents=True)

    write_submission_readme(PACKAGE_DIR / "README_提交说明.md")
    copy_file(ROOT / "reports/processing_report.md", PACKAGE_DIR / "项目处理报告.md")
    copy_file(ROOT / "reports/report_outline.md", PACKAGE_DIR / "报告提纲.md")

    copy_file(
        ROOT / "data/interim/wikidata_entities_normalized_from_batches.json",
        PACKAGE_DIR / "data/entities_5325.json",
    )
    copy_file(ROOT / "data/interim/merged_entities.json", PACKAGE_DIR / "data/chinese_fusion_entities.json")
    copy_file(ROOT / "data/interim/description_qc_sample.json", PACKAGE_DIR / "data/description_qc_sample.json")

    statistics_dir = PACKAGE_DIR / "outputs/statistics"
    for path in (ROOT / "outputs/figures").glob("*.json"):
        copy_file(path, statistics_dir / path.name)
    copy_file(ROOT / "outputs/figures/taxonomy_tree.txt", statistics_dir / "taxonomy_tree.txt")

    code_dir = PACKAGE_DIR / "code"
    copy_tree(ROOT / "scripts", code_dir / "scripts")
    copy_tree(ROOT / "src", code_dir / "src")
    copy_tree(ROOT / "configs", code_dir / "configs")
    copy_tree(ROOT / "tests", code_dir / "tests")
    copy_file(ROOT / "README.md", code_dir / "README.md")
    copy_file(ROOT / "requirements.txt", code_dir / "requirements.txt")
    copy_project_runtime_data(code_dir)

    archive_base = DIST / "knowledge_engineering_submission"
    shutil.make_archive(str(archive_base), "zip", PACKAGE_DIR)
    return archive_base.with_suffix(".zip")


def main() -> None:
    archive = build_package()
    print(f"Submission package written to: {PACKAGE_DIR}")
    print(f"Zip archive written to: {archive}")


if __name__ == "__main__":
    main()
