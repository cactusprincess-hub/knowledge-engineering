import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from software_ai_kg.io_utils import load_json
from software_ai_kg.wikidata import normalize_wikidata_payload


class WikidataNormalizerTests(unittest.TestCase):
    def test_normalize_payload_filters_non_software(self) -> None:
        payload = load_json(ROOT / "data/raw/wikidata/demo_wikidata_entities_raw.json")
        rules = load_json(ROOT / "configs/wikidata_category_rules.json")

        entities, stats = normalize_wikidata_payload(payload, rules)

        self.assertEqual(stats["raw_records"], 5)
        self.assertEqual(stats["kept_records"], 4)
        self.assertEqual(stats["dropped_records"], 1)
        self.assertEqual(entities[0].id, "Q1406")
        self.assertTrue(all(entity.entity != "Google" for entity in entities))

    def test_normalize_payload_infers_categories(self) -> None:
        payload = load_json(ROOT / "data/raw/wikidata/demo_wikidata_entities_raw.json")
        rules = load_json(ROOT / "configs/wikidata_category_rules.json")

        entities, _ = normalize_wikidata_payload(payload, rules)
        category_by_name = {entity.entity: entity.category for entity in entities}

        self.assertEqual(category_by_name["Windows 11"], "操作系统")
        self.assertEqual(category_by_name["Python"], "编程语言")
        self.assertEqual(category_by_name["PyTorch"], "深度学习框架")
        self.assertEqual(category_by_name["MySQL"], "数据库")

    def test_normalize_payload_drops_generic_description(self) -> None:
        payload = {
            "results": {
                "bindings": [
                    {
                        "item": {"value": "http://www.wikidata.org/entity/Q1"},
                        "itemLabel": {"value": "GenericApp"},
                        "instance": {"value": "http://www.wikidata.org/entity/Q7397"},
                        "instanceLabel": {"value": "software"},
                        "description": {"value": "software"},
                    }
                ]
            }
        }
        rules = load_json(ROOT / "configs/wikidata_category_rules.json")

        entities, stats = normalize_wikidata_payload(payload, rules)

        self.assertEqual(entities, [])
        self.assertEqual(stats["dropped_generic_description"], 1)


if __name__ == "__main__":
    unittest.main()
