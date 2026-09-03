# Changelog

All notable changes to the `docx-speech-briefing-builder` project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.2.9] - 2026-09-04

### 🔧 Fixed & Improved
- **Word HTML `<br>` Residual Elimination**: Fixed Markdown tables and paragraphs where raw `<br>`, `<br/>` tags leaked into Word output; now automatically converted to standard cell-level line breaks (`\n` / `<w:br/>`), ensuring clean multiline layout without raw tags.
- **Wave / Tilde / LaTeX `\sim` Spoken Disambiguation**: Resolved the issue where ranges like `S = 115 \sim 138\,\text{MPa}` or `115 ～ 138` were misread by TTS as "反斜杠 sim" or slash syllables; unified LaTeX `\sim`, Unicode `～`, ASCII `~`, and range hyphens `-` directly into natural Chinese spoken word **"至"** (to).
- **LaTeX Thin-Space `\,` Cleanup**: Stripped LaTeX thin spaces `\,` into normal space during speech preprocessing, eliminating erroneous pause commas before units (e.g. `138\,\text{MPa}` -> `138 兆帕`).
- **Unified Range Symbol Option**: Supported standard hyphen `-` and wave `～` interchangeably across typography and speech pipelines.

## [1.2.8] - 2026-09-04

### 🔧 Fixed
- **LaTeX Math vs. Path Backslash Conflict**: Removed premature global `text.replace("\\", " 反斜杠 ")` in `clean_speech_text.py` that erroneously corrupted LaTeX formulas (`\frac`, `\sigma`, `\cdot`, `\tau`, `\text`, `\circ`), which previously caused TTS to read out copious unwanted "反斜杠" in formula-rich reports while Word typography remained clean.
- **Selective Path Backslash Articulation**: Restricted backslash articulation strictly to verified Windows file paths, registry keys, and UNC paths, protecting all engineering LaTeX syntax and Greek symbols.

## [1.2.7] - 2026-09-03

### 🔧 Fixed & Improved
- **Windows & System File Path Display in Word**: Added token-protection layer in `render_docx.py` to prevent Windows file paths (e.g. `C:\Users\Public\Desktop\...`), registry keys, and inline code from having backslashes and folder segments wiped out by LaTeX cleanup rules.
- **File Path Speech & Backslash Narration**: Added dedicated `convert_path_to_speech` in `clean_speech_text.py` ensuring all file paths, registry hives, file extensions (`.lnk` -> `点 lnk`, `.exe` -> `点 exe`), and path backslashes `\` are clearly articulated as "反斜杠" in synthesized speech.

## [1.2.6] - 2026-09-02

### 🔧 Fixed & Improved
- **Global Empty-Brace Cleanup**: Removes standalone empty LaTeX braces `{}` during Word and TTS preprocessing, including `{}°C -> °C`.
- **Appendix Reference Slash Disambiguation**: Parallel appendix citations such as `App. 2 / App. Y` now use a natural pause instead of “除以”.
- **Hardness / Numeric Range Narration**: Numeric ranges using `~` / `～` now explicitly read “至”, e.g. `248 ～ 352` and `HRC 24 ～ 38`.

## [1.2.5] - 2026-09-02

### 🔧 Fixed & Improved
- **Approximation Operator Narration**: `≈` / `\approx` now reads as “约等于”, e.g. `d/D ≈ 0.465`.
- **Empty Temperature-Brace Cleanup**: Word rendering removes empty LaTeX braces before temperature units, converting `{}°C` to `°C`.
- **Angular Degree Narration**: Standalone angular values such as `360°` now read as “360度”, without affecting `°C` / `°F` temperature handling.

## [1.2.4] - 2026-09-02

### 🔧 Fixed & Improved
- **Material Grade Slash Disambiguation**:
  - Parallel grades such as `SA-240 304L/316L` and `Alloy 800HT / UNS N08811` now use a natural pause instead of being spoken as “除以”.
  - Mathematical variable ratios such as `D/t` and `P/S` continue to read as “除以”.
- **Signed Temperature Range Narration**:
  - Temperature ranges such as `-269℃ ~ 900℃` now read naturally as “零下269摄氏度至900摄氏度”, preserving both the negative sign and the range separator.

## [1.2.3] - 2026-09-01

### 🔧 Fixed & Improved
- **Word Temperature Typography**:
  - Automatically sanitizes incomplete degree/temperature LaTeX syntax (e.g. `+5^`, `5^`, `+5^\circ	ext{C}`, `5^\circ C`) into standard `+5°C` / `5°C` in `.docx` rendering, preventing corrupted `+5^` output.
- **Engineering Fractions & Mixed Numbers in TTS**:
  - Standard pipe/fraction sizes (e.g. `NPS 1/4`, `3/8 in`, `1/2`) are now spoken naturally as fractions (**“四分之一”**, **“八分之三”**, **“二分之一”**).
  - Mixed fraction expressions (e.g. `NPS 1 1/4`, `1-1/4 in`, `2 1/2`) are spoken as **“一又四分之一”**, **“二又二分之一”**, eliminating the awkward “1 1 除以 4” pronunciation.
  - Pure mathematical variable ratios (`D/t > 80`, `P/S <= 0.385`) strictly preserve the spoken math operator **“除以”**.

## [1.2.2] - 2026-09-01

### 🔧 Fixed
- **Slash Disambiguation**:
  - Parallel decimal-level clauses such as `QW-404.12 / QW-404.33` now use a natural pause instead of being spoken as “除以”.
  - Engineering units such as `kJ/mm` now read naturally as “千焦每毫米”.
  - Multi-letter abbreviations (e.g. `AB/CD`, `RT1/RT2`) now avoid “除以” mispronunciation.
  - Existing mathematical ratios such as `D/t` and `P/S` continue to read as “除以”.
- **Decimal Range Narration**:
  - Fixed line-leading ranges such as `1.5 ～ 2.0` being misclassified as outline headings; they now read as “1点五至2点零”.

## [1.2.1] - 2026-08-31

### 🚀 Added & Improved
- **Math & Engineering Operator Spoken Restoration**:
  - Formulas and ratios (e.g. `D/t > 80`, `P/S <= 0.385`, `R/t >= 10`, `tn/t != 1.0`) now strictly preserve spoken math operators (**"除以"**, **"大于"**, **"小于"**, **"大于等于"**, **"小于等于"**, **"等于"**, **"不等于"**).
  - Resolved previous issue where `/` and comparison operators were stripped into whitespace/swallowed.
- **Standards & Chapter Slash Natural Ellipsis**:
  - Slashes in standard clauses and multi-level sections (e.g. `Part 5.2.4/5.4.3`, `UG-28/UG-29`, `Section VIII-1/VIII-2`) are intelligently recognized as parallel citations and converted into natural pauses without reading "除以" or "斜杠".

## [1.1.1] - 2026-08-31

### 🚀 Added & Improved
- **Section & Outline Heading Speech Normalization**: Introduced smart outline number converter:
  - Multi-level section headings (e.g. `1.1`, `1.2`, `2.1.3`) are now naturally spoken as **"第 1 点 1 节"**, **"第 1 点 2 节"**, etc.
  - Top-level section & numbered lists (e.g. `1.`, `2.`) are spoken as **"第 1 点"**, **"第 2 点"**.
  - Completely resolved the issue where `1.` was swallowed or `1.2` was incorrectly spoken as `2`.

## [1.1.0] - 2026-08-31

### 🚀 Added
- **Formal Version Module**: Introduced `version.py` (`__version__ = "1.1.0"`) and `--version` CLI flag across all tools.
- **ASCII Art & Line Divider Filter**: Added automatic multi-stage line filters in `render_docx.py` and `clean_speech_text.py` to strip out pseudo-table borders (e.g. `+-------+`), markdown dividers (`------`, `======`), and formatting artifacts.
- **Noise-Free Spoken Disambiguation Engine**: Thoroughly overhauled regex parsing to ensure hyphen/tilde symbols are only transformed to "至" (to) or "比" (ratio) when surrounded by actual numeric values (e.g. `10-20mm`, `10%~20%`, `2:1`).
- **Automated Regression Test Suite**: Added `test_docx_speech_harness.py` to prevent repetitive audio noise artifacts ("至至至...", "加加加...", "等于等于...") and verify Word styling.
- **Dedicated Standalone Repository**: Decoupled from monolith workspace into an independent Git project (`stevexin2018/docx-speech-briefing-builder`).

## [1.0.0] - 2026-08-30

### 🚀 Initial Release
- **Word (.docx) Styling Engine**: Implemented 11-stage LaTeX math formula $\rightarrow$ Unicode / OMML converter.
- **High-Speed Voice Narration**: Built-in 3x Xiaoxiao neural voice generator (`+200%` rate) via `edge-tts`.
