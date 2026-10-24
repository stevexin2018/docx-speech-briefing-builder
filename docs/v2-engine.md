# v2 structured Word and speech engines

The Word engine turns Markdown into editable Word objects through Pandoc's
document tree. The recommended cached entry, `trial_briefing.py`, defaults to
Pandoc. Existing renderer entry points retain their legacy defaults for API
compatibility. Speech now parses marked mathematics before prose cleanup.

## Runtime and commands

Install the Python requirements and Pandoc 3.12.1 or newer separately. Pandoc is
not bundled or downloaded implicitly. Executable lookup is `--pandoc`, then
`PANDOC_PATH`, then a manually installed `.runtime/pandoc/pandoc.exe` on Windows
or `.runtime/pandoc/pandoc` on Linux, then PATH. A managed runtime takes precedence
over an older system installation. The runtime directory is ignored by Git.
The validation baseline is Pandoc 3.12.1 on Windows and Linux ARM64.

```bash
# Word only, with an explicitly requested diagnostics report
python build_briefing.py --input report.md --docx report.docx --engine pandoc --diagnostics diagnostics.json

# Both outputs; existing argument names are preserved
python build_briefing.py --input report.md --docx report.docx --mp3 report.mp3 --engine pandoc

# Audio only; no Word/Pandoc conversion is started
python build_briefing.py --input report.md --mp3 report.mp3

# Direct Word entry point with a custom style reference
python render_docx.py --input report.md --output report.docx --engine pandoc --reference-doc reference.docx
```

Use `--engine legacy`, or omit the engine option, for the existing rendering
behavior. Pandoc-specific options require `--engine pandoc`. Each CLI reports the
same version from `version.py`.

## Content contract

- Mark inline math with `$...$` or `\(...\)` and display math with `$$...$$` or
  `\[...\]`. Formula conversion preserves mathematical syntax; it does not verify
  or correct the mathematics.
- Common fractions, roots, scripts, matrices, cases, aligned equations, sums,
  integrals, accents, delimiters, Chinese labels, table equations and quoted
  equations are covered by structural/Word validation.
- Use Markdown heading levels 1–6, lists, and pipe tables. `<br>` in inline content
  becomes a Word line break. Other raw HTML is reported as unsupported.
- Code spans, code blocks, and link destinations are excluded from engineering
  text normalization. Confident absolute Windows/UNC/registry path literals are
  protected before Markdown interprets their backslashes. Put paths with spaces
  in backticks or quotes; put relative paths and all code examples in backticks.
- Ordinary text units such as `mm2`, `mm²`, and `10 m2` use native Word superscript
  runs. Bare `m2`, model identifiers such as `K3`, and units inside code remain
  unchanged. Explicit Markdown text scripts such as `H~2~O` and `mm^2^` also work.
- An ambiguous `5^` remains unchanged with a warning. Standalone, known symbol
  commands such as `\Delta` and `\tau` become the corresponding characters with a
  warning; they are not treated as a fully identified equation. Other unmarked
  LaTeX is rejected rather than silently removed.
- Equation labels/references and macro definitions (`\label`, `\tag`, `\ref`,
  `\newcommand`, etc.) are outside the supported scope. Unknown math commands are errors.
  Math-like code is kept literal and may receive an informational review hint.

## Diagnostics and publication

The API returns `status`, source hash/counts, output counts, normalization counts,
protected-content counts, and a list of structured diagnostics. Status is
`success`, `success_with_warnings`, or `failed`. A JSON sidecar is written only
when `--diagnostics`/`diagnostics_path` is provided.

Diagnostics contain `code`, `severity`, `message`, and `source`. `line` and
`column` are supplied only for an unambiguous literal source match. A document-tree
`node` pointer is used where available. Repeated or transformed input may have no
line number; a location is never invented. An `excerpt` is retained where
available so repeated input can still be searched. CLI notices are grouped by
code/message; the JSON report keeps each occurrence.

Important codes include:

| Code | Meaning |
| --- | --- |
| `DEPENDENCY_NOT_FOUND` | Pandoc executable was not found |
| `UNCLOSED_MATH` | A display/backslash math delimiter was not closed |
| `UNDELIMITED_LATEX` | Raw LaTeX would be lost outside a math region |
| `MATH_CONVERSION_FAILED` | Pandoc could not produce a native formula |
| `UNSUPPORTED_LATEX_COMMAND` | References/macros are outside the current scope |
| `MATH_COUNT_MISMATCH` | Native formula count differs from recognized input |
| `PROTECTED_CONTENT_CHANGED` | Code/path content was not retained exactly |
| `AMBIGUOUS_POWER` / `AMBIGUOUS_SCRIPT` | Original syntax needs review |
| `BARE_SYMBOL_NORMALIZED` | A known symbol was retained; math markup is advised |

Conversion uses a temporary file next to the requested output. XML validity,
formula count, heading structure, and protected content are checked before atomic
replacement. Failed conversion never publishes its staged Word document or
replaces an existing Word output. Input, reference, output and diagnostics paths
must be distinct. No automatic fallback changes the requested engine.

When both outputs are requested, each runs independently. A partial failure raises
`BriefingBuildError` with a report identifying completed and failed outputs; CLI
exit status is nonzero. Successful Word output remains available if TTS fails.

TTS retains the requested voice by default. Alternate Edge voices require an
explicit `fallback_voices` API argument; there is no implicit change of service.
Chunks retry with backoff and Retry-After; authorization errors stop immediately.
An exhausted chunk cancels the other requests without replaying the whole text.
The synchronous entry has a 600-second deadline, with 15-second connection and
60-second receive timeouts. Async callers must set their own total deadline.
MP3 publication uses a unique staged file and atomic replacement.

## Python API

```python
from briefing_v2 import BuildError, render_markdown

try:
    report = render_markdown(
        markdown_content,
        output_path,
        source_name=input_path,
        pandoc_path=pandoc_executable,
        diagnostics_path=diagnostics_path,
    )
except BuildError as error:
    report = error.report
```

The existing `create_docx_document` signature is retained; new options are keyword
arguments. `build_briefing_concurrent` keeps existing positional calls and allows
either requested output to be omitted.

## Word styling and validation

The default reference is generated locally from Pandoc's built-in DOCX, then
configured with A4 pages, Chinese body/heading fonts, black heading styles, and
paragraph spacing. Tables receive light borders and repeated headers. A custom
`--reference-doc` supplies its own design; the engine does not rewrite that file.
An existing level-one source heading is retained without adding a duplicate title.
Otherwise an explicitly provided title becomes a Word Title paragraph.

The output applies row non-splitting, repeated headers kept with data, and formula
introductions kept with their equations, including with custom references. Rows
taller than a page and unusual templates still need client review. The engine
checks document structure; final delivery requires rendering and page review in
the target client. Automatic equation numbering, cross-reference conventions,
and broad macro support remain outside the supported scope.

## Speech structure and acceptance

Marked TeX is parsed through MathML before general punctuation/range/unit rules.
Supported structures include fractions, signs, scripts, roots, common functions,
matrices, and limits. Speech names fraction and script boundaries explicitly;
it does not prove an engineering formula correct. Unknown operators, commands,
or structures raise `SpeechMathError`; the cached workflow records
`UNSUPPORTED_SPEECH_MATH` and retains any previous MP3. Word and speech support
are separate: a formula that renders in Word may still require an explicit
spoken rewrite before audio can be built.

Code and paths are protected. Unambiguous standalone plain arithmetic is handled
conservatively; write complex formulas with math delimiters. Standard edition
years and alternative standards/models are identifiers, and `2-24×64` is a hole
count and dimension rather than a range. `L=2000` remains an identifier and does
not consume an adjacent comma as a litre unit.

Run schema 2 separates technical build success from manual acceptance. Visual
review and listening remain `not_performed` when requested outputs exist;
engineering review remains `not_assessed`. `fully_accepted` stays false until an
external acceptance process is completed. See the cached workflow guide.

Run the maintained tests with Pandoc available:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
python test_docx_speech_harness.py
```

Pandoc integration tests skip with an explicit reason if no executable is found;
normalization and output-selection checks still run. Private report corpora are
kept outside the repository. Real-report regression compares recognized formulas,
semantic heading levels, tables, and code/path text. Word may rename localized
style IDs and merge adjacent math runs, so round-trip checks compare semantics
rather than identical XML strings.
