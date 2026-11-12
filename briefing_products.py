"""Independent Word and speech products using the shared parser and journal."""
from pathlib import Path
import re
import sys

from briefing_workflow import build_cached_briefing
from clean_speech_text import clean_speech_text


class SpeechPreflightError(ValueError):
    """An unclassified drawing must not become repeated symbol narration."""


def preview_speech(source, *, allow_literal_code=False):
    text = clean_speech_text(Path(source).read_text(encoding="utf-8-sig"))
    if not allow_literal_code and re.search(
            r"[\u2500-\u257f]{2,}|\+[-=]{3,}\+|[-=]{8,}|#{8,}", text):
        raise SpeechPreflightError(
            "语音预检发现尚未转成文字的绘图边框；请先补充文字说明。"
            "明确需要逐字朗读代码时，可使用 --allow-literal-code。")
    return text


def _output(output, suffix):
    if Path(output).suffix.lower() != suffix:
        raise ValueError("本入口仅生成 " + suffix + "，请指定对应扩展名。")


def _finish(source, report, product, cloud_archive, workers):
    report["product"] = product
    if cloud_archive and workers is None:
        bridge_dir = Path.home() / ".openclaw/ops/engineering-media"
        try:
            if not (bridge_dir / "media_bridge.py").is_file():
                raise FileNotFoundError("Host archive adapter missing")
            if str(bridge_dir) not in sys.path:
                sys.path.insert(0, str(bridge_dir))
            from media_bridge import after_build
            after_build(source, report)
        except Exception:
            report["cloud_archive"] = {
                "status": "failed", "reason": "Host archive adapter unavailable",
                "local_files_retained": True,
            }
            print("[cloud-archive] host adapter unavailable; local output retained",
                  file=sys.stderr)
    return report


def build_word_report(source, output, title=None, topic="Technology", *,
                      engine="pandoc", pandoc_path=None, reference_doc=None,
                      record_dir=None, cloud_archive=False, workers=None):
    """Build only DOCX. Audio options and TTS are outside this interface."""
    _output(output, ".docx")
    report = build_cached_briefing(
        source, docx=output, mp3=None, title=title, topic=topic, engine=engine,
        pandoc_path=pandoc_path, reference_doc=reference_doc,
        record_dir=record_dir, workers=workers)
    return _finish(source, report, "word", cloud_archive, workers)


def build_speech_audio(source, output, title=None, topic="Technology", *,
                       rate="+0%", voice="zh-CN-XiaoxiaoNeural", proxy=None,
                       record_dir=None, allow_literal_code=False,
                       cloud_archive=False, workers=None):
    """Preflight and build only MP3; no Word rendering or Pandoc requirement."""
    _output(output, ".mp3")
    preview_speech(source, allow_literal_code=allow_literal_code)
    report = build_cached_briefing(
        source, docx=None, mp3=output, title=title, topic=topic, rate=rate,
        voice=voice, proxy=proxy, record_dir=record_dir, workers=workers)
    return _finish(source, report, "speech", cloud_archive, workers)


def print_result(report):
    print(f"product={report.get('product')}; status={report['status']}")
    for kind, output in report.get("outputs", {}).items():
        print(f"{kind}: {output['status']} (cache={output['cache']}): {output['path']}")
    print(f"record: {report['record_path']}")
    print("manual_review_required=" + str(report.get("manual_review_required", True)))
