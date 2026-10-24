import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from build_briefing import BriefingBuildError, build_briefing_concurrent


class BuildSelectionTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.source = Path(self.folder.name) / "input.md"
        self.source.write_text("# Report\n\n正文。", encoding="utf-8")

    def tearDown(self):
        self.folder.cleanup()

    def test_word_only_does_not_call_audio(self):
        with patch("build_briefing.build_audio_worker", side_effect=AssertionError("audio was called")):
            output = self.source.with_suffix(".docx")
            report = build_briefing_concurrent(str(self.source), str(output), engine="legacy")
        self.assertTrue(output.exists())
        self.assertIsNone(report["audio_cost"])

    def test_audio_only_does_not_load_word_engine(self):
        with patch("build_briefing.build_docx_worker", side_effect=AssertionError("Word was called")), \
             patch("build_briefing.build_audio_worker", return_value=0.1) as audio:
            report = build_briefing_concurrent(str(self.source), output_mp3="test.mp3", engine="pandoc")
        self.assertIsNone(report["docx_cost"])
        audio.assert_called_once()

    def test_audio_failure_keeps_successful_word_output(self):
        output = self.source.with_suffix(".docx")
        with patch("build_briefing.build_audio_worker", side_effect=RuntimeError("TTS unavailable")):
            with self.assertRaises(BriefingBuildError) as raised:
                build_briefing_concurrent(str(self.source), str(output), str(self.source.with_suffix(".mp3")), engine="legacy")
        self.assertTrue(output.exists())
        self.assertEqual(raised.exception.report["outputs"]["docx"]["status"], "success")
        self.assertEqual(raised.exception.report["outputs"]["audio"]["status"], "failed")

    def test_rejects_output_collision_before_workers_start(self):
        output = self.source.with_suffix(".docx")
        with patch("build_briefing.build_docx_worker") as worker:
            with self.assertRaises(ValueError):
                build_briefing_concurrent(str(self.source), str(output), str(output))
        worker.assert_not_called()

    def test_requires_an_output(self):
        with self.assertRaises(ValueError):
            build_briefing_concurrent(str(self.source))


if __name__ == "__main__":
    unittest.main()
