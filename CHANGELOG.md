# Changelog

All notable changes to the `docx-speech-briefing-builder` project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.2.2] - 2026-09-01

### 🔧 Fixed
- **Slash Disambiguation**:
  - Parallel decimal-level clauses such as `QW-404.12 / QW-404.33` now use a natural pause instead of being spoken as “除以”.
  - Engineering units such as `kJ/mm` now read naturally as “千焦每毫米”.
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

---

## [1.1.1] - 2026-08-31

### 🚀 Added & Improved
- **Section & Outline Heading Speech Normalization**: Introduced smart outline number converter:
  - Multi-level section headings (e.g. `1.1`, `1.2`, `2.1.3`) are now naturally spoken as **"第 1 点 1 节"**, **"第 1 点 2 节"**, etc.
  - Top-level section & numbered lists (e.g. `1.`, `2.`) are spoken as **"第 1 点"**, **"第 2 点"**.
  - Completely resolved the issue where `1.` was swallowed or `1.2` was incorrectly spoken as `2`.

---

## [1.1.0] - 2026-08-31

### 🚀 Added
- **Formal Version Module**: Introduced `version.py` (`__version__ = "1.1.0"`) and `--version` CLI flag across all tools.
- **ASCII Art & Line Divider Filter**: Added automatic multi-stage line filters in `render_docx.py` and `clean_speech_text.py` to strip out pseudo-table borders (e.g. `+-------+`), markdown dividers (`------`, `======`), and formatting artifacts.
- **Noise-Free Spoken Disambiguation Engine**: Thoroughly overhauled regex parsing to ensure hyphen/tilde symbols are only transformed to "至" (to) or "比" (ratio) when surrounded by actual numeric values (e.g. `10-20mm`, `10%~20%`, `2:1`).
- **Automated Regression Test Suite**: Added `test_docx_speech_harness.py` to prevent repetitive audio noise artifacts ("至至至...", "加加加...", "等于等于...") and verify Word styling.
- **Dedicated Standalone Repository**: Decoupled from monolith workspace into an independent Git project (`stevexin2018/docx-speech-briefing-builder`).

### 🔧 Fixed
- Fixed Edge-TTS reading continuous hyphens `-` as repetitive "至至至至至..." audio glitches.
- Fixed ASCII decorative frames leaking into Word `.docx` body paragraphs.
- Fixed single-backslash escape issues during JSON-string conversions for LaTeX math functions.

---

## [1.0.0] - 2026-08-30

### 🚀 Initial Release
- **Word (.docx) Styling Engine**: Implemented 11-stage LaTeX math formula $\rightarrow$ Unicode / OMML converter.
- **High-Speed Voice Narration**: Built-in 3x Xiaoxiao neural voice generator (`+200%` rate) via `edge-tts`.
- **Engineering Formatting**: Decimal point speech normalizer (e.g. `0.45` -> `零点四五`), alternating table shading, and brand header/footer banners.
- **Multi-Agent Skill Protocol**: Exported standard `SKILL.md` specification for universal Agent consumption.
