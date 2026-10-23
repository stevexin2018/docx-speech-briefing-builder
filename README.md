# docx-speech-briefing-builder

> 🚀 **Universal AI Agent Skill & Python Tool**: Automated Markdown to elegant Word (`.docx`) reports with LaTeX/Unicode math, structured tables, header/footer branding, and natural-speed speech audio (`.mp3`) with concurrent TTS synthesis.

---

## v2.0 alpha structured Word engine

The opt-in Pandoc engine converts typed Markdown to editable Word math and heading styles. It adds protected engineering-unit normalization, repeating table headers, source diagnostics, and staged output validation. The default remains `legacy` during the alpha.

Install [Pandoc 3.12.1 or newer](https://pandoc.org/installing.html), then use its executable from PATH, `PANDOC_PATH`, or `--pandoc`:

```bash
python build_briefing.py --input report.md --docx report.docx --engine pandoc --diagnostics diagnostics.json
```

The same command supports Word only, MP3 only, or both. Audio and Word report success independently; a failed audio request does not discard a successful Word output. Unknown or unconverted formulas fail the new Word build without replacing an existing document. Diagnostics JSON is created only when requested.

See [the v2 engine guide](docs/v2-engine.md) for source conventions, diagnostics, custom Word references, and regression tests. Full LaTeX packages, automatic equation numbering, and interpretation of math written as code are outside this alpha's scope.

## 🌟 Features

- 📄 **Professional Word (.docx) Engine**:
  - Full support for 11-stage LaTeX math formulas $\rightarrow$ Unicode & OMML conversion.
  - Automatic table rendering with alternating row colors and custom header branding.
  - Robust **ASCII art & line-divider filtering** (eliminates markdown table borders and noisy separator rows).
  - Page margin, header/footer, and hierarchy header styling.

- 🎙️ **Normal-Speed Speech Audio (.mp3) Generator**:
  - Powered by neural TTS (`zh-CN-XiaoxiaoNeural` at `+0%` natural rate).
  - **Controlled concurrent TTS synthesis** (`max_concurrency=2`): multiple text segments are synthesized in parallel, reducing multi-segment audio generation time by 60-75%.
  - **Automatic fallback**: if concurrent synthesis fails (rate limit, network issues), automatically degrades to sequential per-segment synthesis for reliable delivery.
  - Engineering-grade text preprocessing: cleans formulas, converts decimal points (e.g. `0.45` -> `零点四五`), handles ranges/temperatures/units.
  - **Zero noise guarantee**: thoroughly eliminates annoying repetitive syllables from hyphens or punctuation.

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

---

## 🚀 Quick Usage (CLI & Python API)

### 1. One-Step Concurrent Build (Recommended)
```bash
python build_briefing.py \
    --input "sample_report.md" \
    --docx "output_report.docx" \
    --mp3 "output_voice.mp3" \
    --title "Engineering Report" \
    --rate "+0%"
```

### 2. Generate Word Document (.docx) Only
```bash
python render_docx.py \
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
