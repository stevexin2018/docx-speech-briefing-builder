# v2 daily trial workflow

Use this workflow when collecting real-report evidence for the v2 release. It
does not send attachments, publish content, install software or update code.
Existing `build_briefing.py` and `render_docx.py` retain their legacy defaults.

## One portable entry

```bash
# Native Word; no audio request or TTS connection
python trial_briefing.py --input report.md --docx report.docx

# Native Word and normal-speed Xiaoxiao narration
python trial_briefing.py --input report.md --docx report.docx --mp3 report.mp3

# Explicit comparison with the compatibility renderer
python trial_briefing.py --input report.md --docx report.docx --engine legacy

# Custom reference; its contents participate in the Word cache key
python trial_briefing.py --input report.md --docx report.docx --reference-doc reference.docx

# Optional Word-only recovery if audio fails
python trial_briefing.py --input report.md --docx report.docx --mp3 report.mp3 --audio-optional
```

The trial entry defaults to `pandoc`. Only requested formats are generated.
Word requires the v2 engine dependencies and Pandoc 3.12.1+; trial MP3 validation
also requires `ffprobe` on PATH. Audio-only calls do not load or probe Pandoc.
Use absolute paths from agent workflows. Output locations follow the user's
requested destination; the library does not hard-code a machine directory.

On ARM, the existing host-owned OpenClaw attachment shim supports:

```bash
python3 /root/.openclaw/skills/docx-speech-briefing-builder/openclaw_assets.py --input /absolute/report.md --title '主题' --out-dir /absolute/media --trial
```

It also accepts `--engine pandoc`, `--pandoc`, `--reference-doc` and
`--record-dir`. Without trial/engine selection it keeps the legacy default.
`--engine` takes precedence over `--trial` when both are provided. Existing
archiving and attachment formatting remain host-owned; `--no-archive` is used
for isolated smoke tests. These host-specific adapters are not bundled in the
portable library.

## Cache contract

The output basename anchors `report.assets.json`. Word and MP3 have separate
entries; matching requires configuration, resolved output path, a valid asset
and its SHA-256. Old/incompatible cache keys cause a rebuild, not a silent reuse.

- Word: source, title/topic, selected engine, library version and relevant code,
  Word dependencies, template content, and Pandoc version/binary for v2.
- MP3: cleaned speech, rate, requested voice, relevant speech code and Edge-TTS
  version. Word engine, title and template do not invalidate unchanged narration.

A changed reference/Pandoc/core invalidates Word. A changed voice/rate invalidates
audio. Broken files are rebuilt. Successful branches survive the other branch's
failure and can be reused on retry. No automatic engine fallback occurs.

Source is frozen for a build. A source/template change during construction blocks
delivery. Outputs and manifests are locked on both platforms, and completed
assets are validated before atomic replacement. Concurrent attempts fail clearly
instead of writing the same output or replacing another attempt's cache manifest.

## Records

By default `report.briefing/` contains a new `<UTC-time>-<id>.json` per attempt,
plus `<UTC-time>-<id>.word.json` for the Word diagnostic details. `--record-dir`
can select another dedicated directory outside source, template and outputs.
Invalid arguments/path aliases are rejected before starting an attempt.

Run records include:

- `core_version`, `engine`, platform/Python information and Word configuration;
- source path/hash, start/end times and per-stage duration;
- output paths, `built`/`reused`/`failed` state and cache hit/miss;
- `rebuilt`, `reused`, `diagnostics`, `review_required`, `ready_for_delivery`;
- the manifest and Word-diagnostic paths.

Status is `success`, `success_with_warnings`, `word_only` (explicit optional-audio
recovery), or `failed`. `ready_for_delivery` means the requested technical build
contract passed (or optional audio recovery applied); it is not a mathematical
correctness or Word pagination guarantee. Warnings still require review.
Legacy records identify that engine; they do not claim the v2 math checks passed.

Cache hits produce a fresh record and restore original diagnostics, including
warnings. Source locations refer to the user's input, not a deleted temporary
snapshot. Failure records remain available when a prior output is retained.
Neither proxy credentials nor full source text are written into run records;
diagnostics can contain short source excerpts. Keep records private with the
reports. There is no automatic deletion or upload, and diagnostics are not
automatically included as delivered attachments.

## Python integration

`briefing_workflow.build_cached_briefing` returns the run report and raises
`CachedBuildError(report)` on a failed required build. Its default is Pandoc;
compatibility adapters explicitly pass `engine='legacy'`. Existing core renderer
APIs remain available for callers that do not want caching or automatic records.
