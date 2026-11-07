"""Addresses must not enter engineering division or fraction verbalization."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from clean_speech_text import clean_speech_text


class WebAddressSpeechTests(unittest.TestCase):
    def test_reported_address_and_relative_year_path(self):
        for source in ["poyo.ai/hub/2026", "https://poyo.ai/hub/2026",
                       "`poyo.ai/hub/2026`", "hub/2026"]:
            with self.subTest(source=source):
                spoken = clean_speech_text(source)
                self.assertIn("hub 斜杠 2026", spoken)
                self.assertNotIn("除以", spoken)
                self.assertNotIn("分之", spoken)

    def test_address_components_and_adjacent_prose(self):
        spoken = clean_speech_text("访问poyo.ai/hub/2026，随后计算 D/t。")
        self.assertIn("poyo 点 ai 斜杠 hub 斜杠 2026", spoken)
        self.assertIn("，随后计算", spoken)
        self.assertIn("D 除以 t", spoken)
        spoken = clean_speech_text("https://example.com/a_b/1/4?q=2&n=3#top。")
        for part in ["a 下划线 b", "1 斜杠 4", "q 等号 2 与 n 等号 3"]:
            self.assertIn(part, spoken)
        self.assertNotIn("分之", spoken)
        self.assertNotIn("除以", spoken)

    def test_math_units_identifiers_and_code_keep_their_rules(self):
        for source in ["D/t", "a/b", "$D/t$", "$hub/2026$"]:
            with self.subTest(source=source):
                self.assertIn("除以", clean_speech_text(source))
        self.assertIn("分之", clean_speech_text("1/4"))
        self.assertIn("每", clean_speech_text("kJ/mm"))
        self.assertNotIn("斜杠", clean_speech_text("3.2/6.3"))
        self.assertNotIn("除以", clean_speech_text("JB/T4712.1-2007"))
        self.assertEqual(clean_speech_text("`a/b`"), "a/b。")


if __name__ == "__main__":
    unittest.main()
