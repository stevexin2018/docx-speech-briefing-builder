#!/usr/bin/env python3
"""Host Word-only launcher using the single installed shared core."""
from pathlib import Path
import sys

CORE = Path(__file__).resolve().parents[2] / "docx-speech-briefing-builder"
if not (CORE / "word_report.py").is_file():
    raise SystemExit("Shared core lacks word_report.py; update the registered core.")
sys.path.insert(0, str(CORE))
from word_report import main

if __name__ == "__main__":
    args = list(sys.argv[1:])
    if "--no-cloud-archive" in args:
        args.remove("--no-cloud-archive")
    elif "--cloud-archive" not in args:
        args.append("--cloud-archive")
    raise SystemExit(main(args))
