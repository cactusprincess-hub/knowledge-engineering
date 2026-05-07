import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from software_ai_kg.summary_qc import select_description_issues, summarize_records


class SummaryQcTests(unittest.TestCase):
    def test_select_description_issues_flags_qid_and_english(self) -> None:
        record = {
            "id": "Q1",
            "entity": "Q1",
            "category": "数据库",
            "description": "database management system",
        }
        issues = select_description_issues(record)
        self.assertIn("qid_label", issues)
        self.assertIn("english_description", issues)
        self.assertIn("generic_description", issues)

    def test_summarize_records_preserves_original_description(self) -> None:
        record = {
            "id": "Q192490",
            "entity": "PostgreSQL",
            "category": "数据库",
            "description": "free and open-source relational database management system",
            "extra": {"raw_description": "free and open-source relational database management system"},
        }
        processed, stats = summarize_records([record], limit=1, max_chars=30)
        self.assertEqual(stats["processed_records"], 1)
        self.assertLessEqual(len(processed[0]["description"]), 30)
        self.assertEqual(
            processed[0]["extra"]["original_description"],
            "free and open-source relational database management system",
        )
        self.assertIn("normalization_method", processed[0]["extra"])


if __name__ == "__main__":
    unittest.main()
