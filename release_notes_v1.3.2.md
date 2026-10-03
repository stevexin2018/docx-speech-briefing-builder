### Fixed
- **Python 3.14 argparse compatibility**: Escaped `%` in `--rate` help string (`+0%` to `+0%%`) to prevent `ValueError: badly formed help string` when running `build_briefing.py --help` on Python 3.14+.
