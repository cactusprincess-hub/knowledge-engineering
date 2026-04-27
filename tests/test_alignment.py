import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from software_ai_kg.alignment import apply_alias_groups, deduplicate_entities_with_stats
from software_ai_kg.models import EntityRecord


class AlignmentTests(unittest.TestCase):
    def test_alias_groups_merge_chinese_and_english_names(self) -> None:
        records = [
            EntityRecord(
                id="Q384496",
                entity="WeChat",
                category="社交通信",
                description="Tencent-developed messaging app.",
                source=["Wikidata"],
            ),
            EntityRecord(
                id="B-CN-0001",
                entity="微信",
                category="社交通信",
                description="微信是腾讯推出的即时通信与移动社交应用。",
                source=["Baidu Baike"],
            ),
        ]
        alias_groups = [{"canonical": "WeChat", "aliases": ["WeChat", "微信", "Weixin"]}]

        aliased = apply_alias_groups(records, alias_groups)
        merged, stats = deduplicate_entities_with_stats(aliased)

        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0].source, ["Baidu Baike", "Wikidata"])
        self.assertIn("微信", merged[0].aliases)
        self.assertIn("微信", merged[0].description)
        self.assertEqual(stats["multi_source_entity_count"], 1)
        self.assertEqual(stats["duplicate_records_removed"], 1)


if __name__ == "__main__":
    unittest.main()
