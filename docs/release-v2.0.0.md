# v2.0.0 — structured Word and engineering speech

The stable v2 release fixes defects found in three private engineering reports.
Use `trial_briefing.py` for the cached native Word/audio workflow; its filename
is retained for integration compatibility. Existing renderer defaults remain
compatible; use `--engine pandoc` when calling those entries directly.

- Parse marked mathematics before prose cleanup. Preserve complete fractions,
  signs, powers, scripts, roots and common functions; fail explicitly when a
  mathematical structure cannot be spoken reliably. Existing MP3s survive failure.
- Protect standard identifiers and edition years, model alternatives, and hole
  counts/dimensions. Preserve commas adjacent to identifiers such as `L=2000`.
- Apply table row, header and formula-introduction pagination guards to every
  native Word output, including documents using custom references.
- Invalidate audio caches for speech-parser/dependency changes. Preserve
  independent Word/audio caches and partial-failure recovery.
- Separate technical build success from manual visual, listening and engineering
  acceptance in schema 2 run records. `fully_accepted` is never inferred from a
  successful build or cache hit.

## Supported boundary

Install the Python requirements, Pandoc 3.12.1+ for native Word, and `ffprobe` for
cached audio validation. Runtime binaries and private reports are not included
in this source release. There is no implicit engine, voice or service switch.

Word and speech mathematics have separate support boundaries. Unsupported speech
math requires an explicit spoken rewrite; it is not silently flattened. Unmarked
ambiguous formulas, arbitrary LaTeX packages/macros, automatic equation numbering
and engineering correctness are not promised by the converter.

Pagination guards do not replace target-client page review, especially for rows
taller than one page or unusual custom references. Audio decoding and text
semantics checks do not constitute listening. The release does not approve the
equipment described in a report or close missing engineering evidence.

## Validation

- Windows (Python 3.14) and Linux ARM64 (Python 3.10): all 70 maintained tests
  passed on each platform, plus the compatibility speech/Word harness.
- Three unchanged private sources: 110 headings, 17 tables and all 985 cells
  matched; the two explicitly marked-math reports retained 15 native equations
  each. The first report's original plain-text formulas remained plain text.
- Microsoft Word client rendering and page review: 11, 16 and 15 pages, with
  the previously observed row/header/formula pagination defects resolved.
- Three complete normal-speed Xiaoxiao MP3s rebuilt on ARM, probed and fully
  decoded without errors. Windows also completed a live native Word/audio smoke
  build and full audio decode. No human listening result is claimed.
- A repeat ARM build reused both formats for all three sources in 0.37–0.48
  seconds per source, creating fresh records without changing the cached assets.
- Original input files and previous preview outputs were retained. Missing
  engineering evidence remains open.

Private input, reports, audio and local paths are excluded from public source
and assets. These checks validate converter behavior; they do not constitute
engineering approval of the reports.
