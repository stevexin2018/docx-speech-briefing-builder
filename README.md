# docx-speech-briefing-builder

**稳定版 / Stable:** [v2.0.0](https://github.com/stevexin2018/docx-speech-briefing-builder/releases/tag/v2.0.0) · [Release notes](docs/release-v2.0.0.md)

The recommended cached workflow defaults to the native Pandoc Word engine. Existing renderer entry points keep their compatibility defaults; select `--engine pandoc` explicitly there.

> 🚀 **Universal AI Agent Skill & Python Tool**: Automated Markdown to elegant Word (`.docx`) reports with LaTeX/Unicode math, structured tables, header/footer branding, and natural-speed speech audio (`.mp3`) with concurrent TTS synthesis.

---

## v2.0 structured Word and speech engine

The Pandoc engine converts typed Markdown to editable Word math and heading styles. It adds protected engineering-unit normalization, repeating table headers, source diagnostics, and staged output validation. Output pagination keeps table rows intact, headers with data, and formula introductions with their formulas, including with custom references.

For v2 builds, use `python trial_briefing.py --input report.md --docx report.docx`.
This dedicated entry defaults to Pandoc and adds separate Word/audio caches and a
JSON record for every attempt, including cache hits and failures. Add `--mp3` only
when audio is requested; cached audio validation requires `ffprobe` on PATH.
The filename is retained for compatibility. See [the cached workflow guide](docs/trial-workflow.md) for Windows/ARM usage and record fields. A successful build does not mark visual, listening, or engineering acceptance complete.

Install [Pandoc 3.12.1 or newer](https://pandoc.org/installing.html). Lookup order is `--pandoc`, `PANDOC_PATH`, a manually installed `.runtime/pandoc/pandoc.exe` (Windows) or `.runtime/pandoc/pandoc` (Linux), then PATH. The optional runtime directory is ignored by Git; binaries are never downloaded implicitly.

```bash
python build_briefing.py --input report.md --docx report.docx --engine pandoc --diagnostics diagnostics.json
```

The same command supports Word only, MP3 only, or both. Audio and Word report success independently; a failed audio request does not discard a successful Word output. Unknown or unconverted formulas fail the new Word build without replacing an existing document. Diagnostics JSON is created only when requested.

Speech parses marked mathematics before prose cleanup, preserving fraction boundaries, signs, powers, roots and common functions. Standard editions, hole counts and model alternatives are protected from arithmetic rules. Unsupported explicit math fails audio construction while retaining prior audio.

See [the v2 engine guide](docs/v2-engine.md) for source conventions, diagnostics, custom Word references, and regression tests. Full LaTeX packages, automatic equation numbering, and interpretation of math written as code remain outside the supported scope.

## 🌟 Features

- 📄 **Professional Word (.docx) Engine**:
  - Supported LaTeX formulas become native editable OMML; unsupported syntax is reported.
  - Automatic table rendering with alternating row colors and custom header branding.
  - Robust **ASCII art & line-divider filtering** (eliminates markdown table borders and noisy separator rows).
  - Page margin, header/footer, and hierarchy header styling.

- 🎙️ **Normal-Speed Speech Audio (.mp3) Generator**:
  - Powered by neural TTS (`zh-CN-XiaoxiaoNeural` at `+0%` natural rate).
  - **Controlled concurrent TTS synthesis** (`max_concurrency=2`): multiple text segments are synthesized in parallel, reducing multi-segment audio generation time by 60-75%.
  - **Bounded retries**: respects Retry-After, cancels remaining requests on failure, and preserves the previous MP3. The requested voice is retained by default; alternate voices require explicit API opt-in. Synchronous synthesis has a 600-second total deadline.
  - Engineering-grade text preprocessing: cleans formulas, converts decimal points (e.g. `0.45` -> `零点四五`), handles ranges/temperatures/units.
  - Cleans redundant punctuation and uses short pauses between Windows path components.

- 🤖 **Universal Agent Support**:
  - Compatible with **OpenAI Codex, OpenClaw, Claude Code, Cursor, LangChain, AutoGPT**, or standalone Python scripts.

---

## 📦 Installation & Dependencies

```bash
git clone https://github.com/stevexin2018/docx-speech-briefing-builder.git
cd docx-speech-briefing-builder
pip install -r requirements.txt
```

### Dependencies
- Python 3.10+ (the declared `latex2mathml` dependency requires it)
- `python-docx`
- `edge-tts`
- `latex2mathml` (structured speech mathematics)
- Pandoc 3.12.1+ for the native Word engine; `ffprobe` for cached MP3 validation

---

## 🚀 Quick Usage (CLI & Python API)

### 1. Cached Native Build (Recommended)
```bash
python trial_briefing.py \
    --input "sample_report.md" \
    --docx "output_report.docx" \
    --mp3 "output_voice.mp3" \
    --title "Engineering Report" \
    --rate "+0%"
```

### 2. Generate Word Document (.docx) Only
```bash
python render_docx.py \
    --engine pandoc \
    --title "Engineering Calculation Report" \
    --topic-id "CALC-001" \
    --input "sample_report.md" \
    --output "output_report.docx"
```

### 3. Generate Speech Narration (.mp3) Only
```bash
python clean_speech_text.py \
    --input "sample_report.md" \
    --output "output_voice.mp3" \
    --rate "+0%"
```

### 4. Run Self-Evolution Regression Tests
```bash
python test_docx_speech_harness.py
```

---

## 🛠️ Project Structure

```text
.
├── SKILL.md                    # Universal Agent Skill Definition
├── README.md                   # Project Documentation
├── build_briefing.py           # Concurrent Build Engine (Word + TTS parallel)
├── render_docx.py              # Word (.docx) Rendering & Math OMML Engine
├── clean_speech_text.py        # Speech Cleaning + Concurrent TTS Synthesis Engine
├── test_docx_speech_harness.py # Regression & Noise-Free Test Harness
├── requirements.txt            # Python Dependencies
└── .gitignore                  # Git Ignore Rules
```

---

## 📄 License
Internal & Open Engineering Project.
