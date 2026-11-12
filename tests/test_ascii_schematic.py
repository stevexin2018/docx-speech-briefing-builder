"""Labelled drawing borders are not mathematical operators or program code."""
from pathlib import Path
import re
import sys
import tempfile
import unittest

CORE = str(Path(__file__).resolve().parents[1])
if CORE not in sys.path:
    sys.path.append(CORE)
from ascii_schematic import schematic_rows
from clean_speech_text import clean_speech_text
from briefing_v2.normalization import normalize_ast
from briefing_v2.engine import find_pandoc, render_markdown
from docx import Document

try:
    PANDOC = find_pandoc()
except FileNotFoundError:
    PANDOC = None

ASSEMBLY = """        [压力 P 方向]
              ▲
  +-------------+-------------+ <-- 压环 (20 mm)
  | [垫片]      |       [垫片] |
  | ===== [观察窗 (材料待核验)] ===== |
  +-----+       |       +-----+ <-- 基座
  #### | 视口 320 x 40 | ####
  螺柱 M12  +---------------------+  螺柱 M12
  (SA-193 B7)                    (SA-193 B7)"""


class SchematicTests(unittest.TestCase):
    def test_assembly_preserves_annotations_and_repeated_components(self):
        rows = schematic_rows(ASSEMBLY)
        self.assertIsNotNone(rows)
        text = "\n".join(rows)
        self.assertNotRegex(text, r"-{3,}|={3,}|#{3,}|\||\+")
        for term in ["压力 P 方向", "向上", "压环 (20 mm)", "材料待核验",
                     "基座", "视口 320 x 40"]:
            self.assertIn(term, text)
        for term in ["螺柱 M12", "SA-193 B7", "垫片"]:
            self.assertEqual(text.count(term), 2)

    def test_single_connector_unicode_borders_and_pure_rules(self):
        self.assertEqual(schematic_rows("螺柱 M12  +--------+  螺柱 M12"),
                         ["螺柱 M12；螺柱 M12"])
        rows = schematic_rows("┌─────────┐\n│ 盖板 │\n├─────────┤\n│ 垫片 │\n└─────────┘")
        self.assertEqual(rows, ["盖板", "垫片"])
        self.assertEqual(schematic_rows("+----------+\n|          |\n+----------+"), [])
        self.assertEqual(clean_speech_text("```\n+----------+\n+----------+\n```"), "")

    def test_word_and_speech_recognize_fenced_and_indented_sketches(self):
        for source in ["```text\n" + ASSEMBLY + "\n```",
                       "~~~text\n" + ASSEMBLY + "\n~~~",
                       "\n".join("    " + line for line in ASSEMBLY.splitlines())]:
            with self.subTest(source=source[:20]):
                spoken = clean_speech_text(source)
                self.assertNotRegex(spoken, r"-{3,}|={3,}|#{3,}|\||减去|等于")
                self.assertIn("材料待核验", spoken)
                self.assertEqual(spoken.count("螺柱 M12"), 2)
        ast = {"blocks": [{"t": "CodeBlock", "c": [["", ["text"], []], ASSEMBLY]}]}
        result, analysis, diagnostics = normalize_ast(ast, ASSEMBLY)
        self.assertTrue(all(block["t"] == "Para" for block in result["blocks"]))
        self.assertFalse(analysis["protected"])
        self.assertIn("ASCII_SCHEMATIC_NORMALIZED", [d.code for d in diagnostics])

    def test_programs_material_numbers_negative_values_and_math_are_preserved(self):
        for code in ["x = a - b", "D/t", "a +----+ b", "git diff --stat",
                     'print("螺柱 M12 +--------+ 螺柱 M12")']:
            with self.subTest(code=code):
                self.assertIsNone(schematic_rows(code))
        self.assertIsNone(schematic_rows(ASSEMBLY, "python"))
        self.assertIsNone(schematic_rows(ASSEMBLY, "bash"))
        program = "```python\n# 示例\nx = a - b\n```"
        self.assertIn("x = a - b", clean_speech_text(program))
        ast = {"blocks": [{"t": "CodeBlock", "c": [["", ["python"], []], ASSEMBLY]}]}
        result, _, _ = normalize_ast(ast, ASSEMBLY)
        self.assertEqual(result, ast)
        rows = schematic_rows("盖板 -20°C  +--------+  螺柱 SA-193 B7")
        self.assertEqual(rows, ["盖板 -20°C；螺柱 SA-193 B7"])
        self.assertIn("减去", clean_speech_text("$a-b$"))

    @unittest.skipUnless(PANDOC, "Pandoc required")
    def test_native_docx_contains_labels_without_drawing_code(self):
        for source in ["```text\n" + ASSEMBLY + "\n```",
                       "\n".join("    " + line for line in ASSEMBLY.splitlines())]:
            with self.subTest(source=source[:20]), tempfile.TemporaryDirectory() as folder:
                output = Path(folder) / "drawing.docx"
                render_markdown(source, output, pandoc_path=PANDOC)
                paragraphs = Document(output).paragraphs
                text = "\n".join(p.text for p in paragraphs)
                self.assertNotRegex(text, r"-{3,}|={3,}|#{3,}|\|")
                self.assertEqual(text.count("螺柱 M12"), 2)
                self.assertIn("SA-193 B7", text)
                self.assertIn("材料待核验", text)
                self.assertFalse(any(p.style.name == "Source Code" for p in paragraphs))


if __name__ == "__main__":
    unittest.main()
