import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from software_ai_kg.taxonomy import assign_single_parent, remove_cycle_edges


class TaxonomyTests(unittest.TestCase):
    def test_remove_cycle_edges(self) -> None:
        edges = [
            {"parent": "A", "child": "B"},
            {"parent": "B", "child": "C"},
            {"parent": "C", "child": "A"},
        ]
        kept, removed = remove_cycle_edges(edges)
        self.assertEqual(len(kept), 2)
        self.assertEqual(len(removed), 1)

    def test_assign_single_parent(self) -> None:
        edges = [
            {"parent": "客户端软件", "child": "浏览器"},
            {"parent": "互联网应用", "child": "浏览器"},
        ]
        kept, dropped = assign_single_parent(edges, preferred_parents=["客户端软件"])
        self.assertEqual(kept, [{"parent": "客户端软件", "child": "浏览器"}])
        self.assertEqual(dropped, [{"parent": "互联网应用", "child": "浏览器"}])


if __name__ == "__main__":
    unittest.main()
