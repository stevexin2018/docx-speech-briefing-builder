#!/usr/bin/env python3
"""Explicit v2 trial entry: cached selected outputs and automatic run records."""
import argparse
import sys

from briefing_workflow import CachedBuildError, build_cached_briefing
from briefing_v2.diagnostics import print_diagnostics
from version import __version__


def main(argv=None):
    parser = argparse.ArgumentParser(description='Try the native Word engine with caching and automatic diagnostics.')
    parser.add_argument('--version', action='version', version=f'docx-speech-briefing-builder v{__version__}')
    parser.add_argument('--input', required=True, help='Markdown input')
    parser.add_argument('--docx', help='Requested Word output')
    parser.add_argument('--mp3', help='Requested MP3 output (requires ffprobe for validation)')
    parser.add_argument('--engine', choices=['pandoc', 'legacy'], default='pandoc', help='Word engine; default pandoc')
    parser.add_argument('--pandoc', help='Pandoc executable override')
    parser.add_argument('--reference-doc', help='Custom Word template')
    parser.add_argument('--title', help='Report title')
    parser.add_argument('--topic-id', default='Technology')
    parser.add_argument('--rate', default='+0%', help='Speech rate (default +0%%)')
    parser.add_argument('--voice', default='zh-CN-XiaoxiaoNeural')
    parser.add_argument('--proxy', help='TTS proxy; never recorded in the journal')
    parser.add_argument('--audio-optional', action='store_true', help='Allow Word-only success after an audio failure')
    parser.add_argument('--record-dir', help='Journal directory (default beside the outputs)')
    args = parser.parse_args(argv)
    try:
        report = build_cached_briefing(args.input, args.docx, args.mp3, args.title, args.topic_id,
                                      args.rate, args.proxy, audio_optional=args.audio_optional,
                                      engine=args.engine, pandoc_path=args.pandoc, reference_doc=args.reference_doc,
                                      voice=args.voice, record_dir=args.record_dir)
    except ValueError as error:
        parser.error(str(error))
    except CachedBuildError as error:
        report = error.report
    print(f"engine={report['engine'] or 'audio-only'}; status={report['status']}")
    for kind, output in report['outputs'].items():
        print(f"{kind}: {output['status']} (cache={output['cache']}): {output['path']}")
    print_diagnostics(report['diagnostics'], ('warning', 'error'))
    print(f"record: {report['record_path']}")
    if report['word_diagnostics_path']:
        print(f"word diagnostics: {report['word_diagnostics_path']}")
    return 0 if report['ready_for_delivery'] else 1


if __name__ == '__main__':
    sys.exit(main())
