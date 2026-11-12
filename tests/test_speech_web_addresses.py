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
                self.assertIn("hub，2026", spoken)
                self.assertNotIn("斜杠", spoken)
                self.assertNotIn("除以", spoken)
                self.assertNotIn("分之", spoken)

    def test_address_components_and_adjacent_prose(self):
        spoken = clean_speech_text("访问poyo.ai/hub/2026，随后计算 D/t。")
        self.assertIn("poyo 点 ai，hub，2026", spoken)
        self.assertIn("，随后计算", spoken)
        self.assertIn("D 除以 t", spoken)
        spoken = clean_speech_text("https://example.com/a_b/1/4?q=2&n=3#top。")
        for part in ["a b", "1，4", "q 等号 2 与 n 等号 3"]:
            self.assertIn(part, spoken)
        self.assertNotIn("分之", spoken)
        self.assertNotIn("除以", spoken)

    def test_reported_github_url_uses_natural_pauses_in_markdown(self):
        address = "https://github.com/Zagitta/gpu-unlock/blob/main/kernel/gpu_unlock/recipes.c"
        expected = "github 点 com，Zagitta，gpu unlock，blob，main，kernel，gpu unlock，recipes 点 c"
        for source in [address, f"`{address}`", f"<{address}>", f"[源码]({address})"]:
            with self.subTest(source=source):
                spoken = clean_speech_text(source)
                self.assertIn(expected, spoken)
                for unwanted in ["连接号", "下划线", "斜杠", "除以", "分之"]:
                    self.assertNotIn(unwanted, spoken)

    def test_hostname_query_fragment_and_repeated_slashes(self):
        cases = {
            "https://gpu-unlock.example.com/a_b//c-d/":
                "gpu unlock 点 example 点 com，a b，c d。",
            "https://example.com?build_id=gpu_unlock-v2":
                "example 点 com 问号 build id 等号 gpu unlock v2。",
            "https://example.com#gpu_unlock-v2":
                "example 点 com 井号 gpu unlock v2。",
            "`https://example.com?build_id=gpu_unlock-v2`":
                "example 点 com 问号 build id 等号 gpu unlock v2。",
        }
        for source, expected in cases.items():
            with self.subTest(source=source):
                self.assertEqual(clean_speech_text(source), expected)

    def test_math_units_identifiers_and_code_keep_their_rules(self):
        for source in ["D/t", "a/b", "$D/t$", "$hub/2026$"]:
            with self.subTest(source=source):
                self.assertIn("除以", clean_speech_text(source))
        self.assertIn("分之", clean_speech_text("1/4"))
        self.assertIn("每", clean_speech_text("kJ/mm"))
        self.assertNotIn("斜杠", clean_speech_text("3.2/6.3"))
        self.assertNotIn("除以", clean_speech_text("JB/T4712.1-2007"))
        self.assertEqual(clean_speech_text("`a/b`"), "a/b。")
        self.assertEqual(clean_speech_text("`gpu_unlock`"), "gpu 下划线 unlock。")
        self.assertEqual(clean_speech_text(r"$W_{m2}$"), "W、m二。")
        self.assertIn("减去", clean_speech_text("$a-b$"))


if __name__ == "__main__":
    unittest.main()
