# docx-speech-briefing-builder

> 🚀 **Universal AI Agent Skill & Python Tool**: Automated Markdown to elegant Word (`.docx`) reports with LaTeX/Unicode math, structured tables, header/footer branding, and 3x high-speed natural speech audio (`.mp3`).

---

## 🌟 Features

- 📄 **Professional Word (.docx) Engine**:
  - Full support for 11-stage LaTeX math formulas $\rightarrow$ Unicode & OMML conversion.
  - Automatic table rendering with alternating row colors and custom header branding.
  - Robust **ASCII art & line-divider filtering** (eliminates markdown table borders and noisy separator rows).
  - Page margin, header/footer, and hierarchy header styling.

- 🎙️ **3x Speech Audio (.mp3) Generator**:
  - Powered by high-speed neural TTS (`zh-CN-XiaoxiaoNeural` at `+200%` rate).
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
- Python 3.8+
- `python-docx`
- `edge-tts`

---

## 🚀 Quick Usage (CLI & Python API)

### 1. Generate Word Document (.docx)
```bash
python render_docx.py \
    --title "Engineering Calculation Report" \
    --topic-id "CALC-001" \
    --input "sample_report.md" \
    --output "output_report.docx"
```

### 2. Generate 3x Speech Narration (.mp3)
```bash
python clean_speech_text.py \
    --input "sample_report.md" \
    --output "output_voice.mp3" \
    --rate "+200%"
```

### 3. Run Self-Evolution Regression Tests
```bash
python test_docx_speech_harness.py
```

---

## 🛠️ Project Structure

```text
.
├── SKILL.md                    # Universal Agent Skill Definition
├── README.md                   # Project Documentation
├── render_docx.py              # Word (.docx) Rendering & Math OMML Engine
├── clean_speech_text.py        # Speech Cleaning & Spoken-Language Normalizer
├── test_docx_speech_harness.py # Regression & Noise-Free Test Harness
├── requirements.txt            # Python Dependencies
└── .gitignore                  # Git Ignore Rules
```

---

## 📄 License
Internal & Open Engineering Project.
