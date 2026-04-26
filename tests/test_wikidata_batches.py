import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from software_ai_kg.wikidata_batches import (
    build_batch_output_path,
    build_manifest,
    summarise_manifest,
)


class WikidataBatchTests(unittest.TestCase):
    def test_build_batch_output_path(self) -> None:
        path = build_batch_output_path(Path("data/raw/wikidata/batches"), "video_game", 200)
        self.assertEqual(str(path), "data/raw/wikidata/batches/video_game_offset_00200.json")

    def test_summarise_manifest(self) -> None:
        target = {
            "name": "programming_language",
            "qid": "Q9143",
            "label": "programming language",
        }
        entries = [
            build_manifest(
                target=target,
                output_path=Path("a.json"),
                batch_index=0,
                offset=0,
                batch_size=100,
                result_count=100,
                skipped_existing=False,
            ),
            build_manifest(
                target=target,
                output_path=Path("b.json"),
                batch_index=1,
                offset=100,
                batch_size=100,
                result_count=40,
                skipped_existing=True,
            ),
        ]
        summary = summarise_manifest(entries)
        self.assertEqual(summary["batch_file_count"], 2)
        self.assertEqual(summary["raw_record_count"], 140)
        self.assertEqual(summary["skipped_existing_batch_count"], 1)
        self.assertEqual(summary["records_by_target"]["programming_language"], 140)


if __name__ == "__main__":
    unittest.main()
