"""The separated products cannot silently create the other requested format."""
from pathlib import Path
import contextlib
import io
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import briefing_products as products
from briefing_v2.engine import find_pandoc
import word_report
import speech_narration

try:
    PANDOC = find_pandoc()
except FileNotFoundError:
    PANDOC = None


class IndependentProductTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / "source.md"
        self.source.write_text("# Report\n\n$x_i=a-b$，10 mm。\n", encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    @unittest.skipUnless(PANDOC, "Pandoc required")
    def test_word_build_has_no_tts_and_creates_only_word(self):
        output = self.root / "report.docx"
        with patch("clean_speech_text.generate_speech_audio",
                   side_effect=AssertionError("Word must not synthesize audio")):
            result = products.build_word_report(self.source, output, pandoc_path=PANDOC)
        self.assertEqual(result["product"], "word")
        self.assertEqual(set(result["outputs"]), {"docx"})
        self.assertTrue(output.is_file())
        self.assertFalse(list(self.root.glob("*.mp3")))
        self.assertNotIn("cloud_archive", result)

    def test_wrong_extension_is_rejected_before_any_build(self):
        with patch.object(products, "build_cached_briefing") as build:
            with self.assertRaises(ValueError):
                products.build_word_report(self.source, self.root / "report.mp3")
            with self.assertRaises(ValueError):
                products.build_speech_audio(self.source, self.root / "report.docx")
        build.assert_not_called()

    def test_preview_cleans_diagram_and_retains_math_without_tts(self):
        self.source.write_text(
            "```text\n螺柱 M12 +----------+ 螺柱 M12\n```\n\n"
            "$W_{m2}=a-b$。\nhttps://example.com/gpu-unlock/a_b",
            encoding="utf-8")
        with patch.object(products, "build_cached_briefing") as build:
            text = products.preview_speech(self.source)
        build.assert_not_called()
        self.assertNotIn("----", text)
        self.assertNotIn("下划线", text)
        self.assertIn("减去", text)
        self.assertIn("W、m二", text)
        self.assertIn("gpu unlock", text)

    def test_unclassified_drawing_stops_tts_and_preserves_previous_audio(self):
        self.source.write_text("```text\nTop +----------+ Bottom\n```", encoding="utf-8")
        output = self.root / "report.mp3"
        output.write_bytes(b"previous audio")
        with patch.object(products, "build_cached_briefing") as build:
            with self.assertRaises(products.SpeechPreflightError):
                products.build_speech_audio(self.source, output)
        build.assert_not_called()
        self.assertEqual(output.read_bytes(), b"previous audio")
        self.assertIn("----------", products.preview_speech(
            self.source, allow_literal_code=True))

    def test_cli_does_not_accept_the_other_product_options(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as word:
                word_report.main(["--input", str(self.source), "--output", "r.docx",
                                  "--voice", "unused"])
            with self.assertRaises(SystemExit) as audio:
                speech_narration.main(["--input", str(self.source), "--output", "r.mp3",
                                       "--reference-doc", "unused.docx"])
        self.assertEqual(word.exception.code, 2)
        self.assertEqual(audio.exception.code, 2)

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"),
                         "FFmpeg tools required")
    def test_audio_has_no_word_or_pandoc_and_reuses_its_own_cache(self):
        output = self.root / "report.mp3"
        word = self.root / "report.docx"
        word.write_bytes(b"independent existing word")
        fixture = self.root / "fixture.mp3"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi",
                        "-i", "sine=duration=0.1", str(fixture)],
                       check=True, capture_output=True)
        calls = []
        def audio_worker(source, destination, rate, voice, proxy):
            calls.append((rate, voice))
            shutil.copy2(fixture, destination)
        with patch("briefing_v2.engine.find_pandoc",
                   side_effect=AssertionError("Audio must not require Pandoc")):
            first = products.build_speech_audio(
                self.source, output, workers={"mp3": audio_worker})
            second = products.build_speech_audio(
                self.source, output, workers={"mp3": audio_worker})
        self.assertEqual(first["product"], "speech")
        self.assertEqual(set(first["outputs"]), {"mp3"})
        self.assertEqual(second["reused"], ["mp3"])
        self.assertEqual(calls, [("+0%", "zh-CN-XiaoxiaoNeural")])
        self.assertEqual(word.read_bytes(), b"independent existing word")


if __name__ == "__main__":
    unittest.main()
