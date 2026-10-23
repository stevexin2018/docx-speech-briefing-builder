#!/usr/bin/env python3
"""Build requested Word/audio outputs independently, preserving the existing API."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from pathlib import Path
import sys
import time


class BriefingBuildError(RuntimeError):
    def __init__(self, report):
        self.report = report
        super().__init__("；".join(f"{name}: {message}" for name, message in report["errors"].items()))


def build_docx_worker(input_md, output_docx, title, topic_id, *, engine="legacy", pandoc_path=None,
                       reference_doc=None, diagnostics_path=None):
    from render_docx import create_docx_document
    started = time.time()
    with open(input_md, "r", encoding="utf-8") as stream:
        markdown = stream.read()
    report = create_docx_document(title, topic_id, markdown, output_docx, engine=engine,
                                 pandoc_path=pandoc_path, reference_doc=reference_doc,
                                 diagnostics_path=diagnostics_path, source_name=os.path.abspath(input_md))
    if report:
        from briefing_v2.diagnostics import print_diagnostics
        print_diagnostics(report["diagnostics"])
    return time.time() - started


def build_audio_worker(input_md, output_mp3, rate, voice, proxy):
    from clean_speech_text import clean_speech_text, generate_speech_audio
    started = time.time()
    with open(input_md, "r", encoding="utf-8") as stream:
        raw_text = stream.read()
    generate_speech_audio(clean_speech_text(raw_text), output_mp3, rate=rate, voice=voice, proxy=proxy)
    return time.time() - started


def build_briefing_concurrent(input_md, output_docx=None, output_mp3=None, title=None,
                              topic_id="Technology", rate="+0%", voice="zh-CN-XiaoxiaoNeural", proxy=None, *,
                              engine="legacy", pandoc_path=None, reference_doc=None, diagnostics_path=None):
    if not output_docx and not output_mp3:
        raise ValueError("至少指定 Word 或 MP3 中的一种输出。")
    if diagnostics_path and not output_docx:
        raise ValueError("--diagnostics 需要同时指定 Word 输出。")
    if output_docx and engine == "legacy" and any((pandoc_path, reference_doc, diagnostics_path)):
        raise ValueError("Pandoc、参考模板和结构化诊断选项需要 --engine pandoc。")
    writes = [Path(path).resolve() for path in (output_docx, output_mp3, diagnostics_path) if path]
    reads = {Path(input_md).resolve()}
    if reference_doc:
        reads.add(Path(reference_doc).resolve())
    if len(set(writes)) != len(writes) or any(path in reads for path in writes):
        raise ValueError("输入、参考模板、Word、音频和诊断文件必须使用不同路径。")
    for path in writes:
        path.parent.mkdir(parents=True, exist_ok=True)
    title = title or Path(input_md).stem
    started = time.time()
    report = {"docx_path": output_docx, "mp3_path": output_mp3, "docx_cost": None, "audio_cost": None,
              "outputs": {}, "errors": {}, "error_details": {}}
    with ThreadPoolExecutor(max_workers=2) as executor:
        jobs = {}
        if output_docx:
            jobs[executor.submit(build_docx_worker, input_md, output_docx, title, topic_id, engine=engine,
                                 pandoc_path=pandoc_path, reference_doc=reference_doc,
                                 diagnostics_path=diagnostics_path)] = ("docx", output_docx)
        if output_mp3:
            jobs[executor.submit(build_audio_worker, input_md, output_mp3, rate, voice, proxy)] = ("audio", output_mp3)
        for future in as_completed(jobs):
            name, path = jobs[future]
            try:
                cost = future.result()
                report[name + "_cost"] = cost
                report["outputs"][name] = {"status": "success", "path": path}
            except Exception as error:
                report["errors"][name] = str(error)
                report["outputs"][name] = {"status": "failed", "path": path}
                if hasattr(error, "report"):
                    report["error_details"][name] = error.report
    report["total_cost"] = time.time() - started
    if report["errors"]:
        raise BriefingBuildError(report)
    print(f"[build_briefing] 构建完成，总耗时 {report['total_cost']:.2f}s。")
    return report


def main(argv=None):
    from version import __version__
    parser = argparse.ArgumentParser(description="Build Word, MP3, or both from Markdown.")
    parser.add_argument("--version", action="version", version=f"docx-speech-briefing-builder v{__version__}")
    parser.add_argument("--input", required=True, help="Input Markdown path")
    parser.add_argument("--docx", help="Output Word path")
    parser.add_argument("--mp3", help="Output MP3 path")
    parser.add_argument("--title", help="Document title")
    parser.add_argument("--topic-id", default="Technology", help="Document topic identifier")
    parser.add_argument("--rate", default="+0%", help="Speech rate (default +0%%)")
    parser.add_argument("--voice", default="zh-CN-XiaoxiaoNeural", help="TTS voice")
    parser.add_argument("--proxy", help="TTS proxy URL")
    parser.add_argument("--engine", choices=("legacy", "pandoc"), default="legacy", help="Word engine (default: legacy)")
    parser.add_argument("--pandoc", help="Pandoc executable (or set PANDOC_PATH)")
    parser.add_argument("--reference-doc", help="Word style reference (.docx)")
    parser.add_argument("--diagnostics", help="Optional structured Word diagnostics JSON")
    args = parser.parse_args(argv)
    if not args.docx and not args.mp3:
        parser.error("至少指定 --docx 或 --mp3。")
    try:
        result = build_briefing_concurrent(args.input, args.docx, args.mp3, args.title, args.topic_id,
                                           args.rate, args.voice, args.proxy, engine=args.engine,
                                           pandoc_path=args.pandoc, reference_doc=args.reference_doc,
                                           diagnostics_path=args.diagnostics)
    except ValueError as error:
        parser.error(str(error))
    except BriefingBuildError as error:
        for name, output in error.report["outputs"].items():
            if output["status"] == "success":
                print(f"{name} 构建成功: {output['path']}")
        for name, message in error.report["errors"].items():
            details = error.report["error_details"].get(name, {})
            diagnostics = [item for item in details.get("diagnostics", []) if item["severity"] == "error"]
            if diagnostics:
                from briefing_v2.diagnostics import print_diagnostics
                print_diagnostics(diagnostics, ("error",))
            else:
                print(f"{name} 构建失败: {message}", file=sys.stderr)
        return 1
    for name, output in result["outputs"].items():
        print(f"{name}: {output['path']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
