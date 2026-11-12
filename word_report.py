#!/usr/bin/env python3
"""Standalone Word entry; produces DOCX only."""
import argparse
from briefing_products import build_word_report, print_result
from briefing_workflow import CachedBuildError
from version import __version__


def main(argv=None):
    p = argparse.ArgumentParser(description="Build only a native Word report.")
    p.add_argument("--version", action="version", version=__version__)
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True, help="DOCX output")
    p.add_argument("--title")
    p.add_argument("--topic-id", default="Technology")
    p.add_argument("--engine", choices=["pandoc", "legacy"], default="pandoc")
    p.add_argument("--pandoc")
    p.add_argument("--reference-doc")
    p.add_argument("--record-dir")
    p.add_argument("--cloud-archive", action="store_true")
    a = p.parse_args(argv)
    try:
        report = build_word_report(
            a.input, a.output, a.title, a.topic_id, engine=a.engine,
            pandoc_path=a.pandoc, reference_doc=a.reference_doc,
            record_dir=a.record_dir, cloud_archive=a.cloud_archive)
    except ValueError as error:
        p.error(str(error))
    except CachedBuildError as error:
        report = error.report
    print_result(report)
    return 0 if report.get("build_contract_passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
