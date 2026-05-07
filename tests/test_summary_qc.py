import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from software_ai_kg.summary_qc import select_summary_reasons, summarize_records


class SummaryQcTests(unittest.TestCase):
    def test_select_summary_reasons_flags_qid_and_english(self) -> None:
        record = {
            "id": "Q1",
            "entity": "Q1",
            "category": "数据库",
            "description": "database management system",
        }
        reasons = select_summary_reasons(record)
        self.assertIn("qid_label", reasons)
        self.assertIn("english_description", reasons)
        self.assertIn("generic_description", reasons)

    def test_summarize_records_adds_prompt_and_preserves_before(self) -> None:
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
            processed[0]["extra"]["description_before_summary"],
            "free and open-source relational database management system",
        )
        self.assertIn("summary_instruction", processed[0]["extra"])


if __name__ == "__main__":
    unittest.main()
