#!/usr/bin/env python3
"""Standalone speech preflight and MP3 entry; never produces a Word file."""
import argparse
import os
from briefing_products import build_speech_audio, preview_speech, print_result
from briefing_workflow import CachedBuildError
from version import __version__


def main(argv=None):
    p = argparse.ArgumentParser(description="Preflight narration or build only MP3.")
    p.add_argument("--version", action="version", version=__version__)
    p.add_argument("--input", required=True)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--output", help="MP3 output")
    mode.add_argument("--preview", action="store_true", help="Print expected reading without TTS")
    p.add_argument("--title")
    p.add_argument("--topic-id", default="Technology")
    p.add_argument("--rate", default="+0%")
    p.add_argument("--voice", default="zh-CN-XiaoxiaoNeural")
    p.add_argument("--proxy")
    p.add_argument("--record-dir")
    p.add_argument("--allow-literal-code", action="store_true")
    p.add_argument("--cloud-archive", action="store_true")
    p.add_argument("--math-mode", choices=("smart","strict"), default="smart",
                   help="Formula reading: natural smart (default) or explicit strict")
    a = p.parse_args(argv)
    os.environ['ENGINEERING_MATH_SPEECH_MODE'] = a.math_mode
    try:
        if a.preview:
            print(preview_speech(a.input, allow_literal_code=a.allow_literal_code))
            return 0
        report = build_speech_audio(
            a.input, a.output, a.title, a.topic_id, rate=a.rate, voice=a.voice,
            proxy=a.proxy, record_dir=a.record_dir,
            allow_literal_code=a.allow_literal_code, cloud_archive=a.cloud_archive)
    except (ValueError, OSError) as error:
        p.error(str(error))
    except CachedBuildError as error:
        report = error.report
    print_result(report)
    return 0 if report.get("build_contract_passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
