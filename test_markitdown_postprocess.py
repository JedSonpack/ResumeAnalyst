from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


def load_script_module():
    script_path = Path(__file__).with_name("test.py")
    spec = importlib.util.spec_from_file_location("markitdown_script", script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


SCRIPT = load_script_module()


class PostprocessTests(unittest.TestCase):
    def test_clean_markdown_normalizes_and_merges_lines(self) -> None:
        raw = (
            "李恒\n"
            " \x00\x00｜ test@stu.ecnu.edu.cn | \n\n"
            "Agent Tool-Calling 架构优化：通过 Workﬂow 对原\n"
            "⼦⼯具进⾏编排封装。\n\n"
            "项⽬经历\n"
            "RecordParser 解决半包粘包问题。\n"
        )

        cleaned = SCRIPT.clean_markdown(raw)

        self.assertNotIn("\x00", cleaned)
        self.assertNotIn("", cleaned)
        self.assertIn("Agent Tool-Calling 架构优化:通过 Workflow 对原子工具进行编排封装。", cleaned)
        self.assertIn("项目经历", cleaned)
        self.assertIn("项目经历\n\nRecordParser 解决半包粘包问题。", cleaned)
        self.assertIn("test@stu.ecnu.edu.cn", cleaned)

    def test_smart_join_preserves_ascii_word_spacing(self) -> None:
        self.assertEqual(SCRIPT.smart_join("Unique", "Key"), "Unique Key")
        self.assertEqual(SCRIPT.smart_join("Tool-", "Calling"), "Tool-Calling")
        self.assertEqual(SCRIPT.smart_join("Batik", "性能瓶颈"), "Batik性能瓶颈")


if __name__ == "__main__":
    unittest.main()
