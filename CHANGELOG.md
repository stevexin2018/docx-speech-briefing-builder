## [1.2.17] - 2026-09-22

### 🔧 Fixed
- **Decimal Percentage Spoken Order (TTS)**:
  - Fixed an issue where decimal percentages like `0.35%`, `0.040%`, `0.43%`, `0.003%~0.005%` had their reading order reversed into “零点三五 百分号” instead of natural spoken Chinese “百分之零点三五”.
  - Expanded percentage regex patterns (`num_pat`) to correctly capture Chinese decimal strings (`零点...`, `...点...`) converted in preceding passes.
  - Ensured range separators and negative/plus signs (`±0.5%`, `-0.12%`, `0.003%~0.005%`) correctly read as “百分之...至百分之...”.

## [1.2.16] - 2026-09-22

### Changed
- **Default Speech Rate Adjusted to 1.5x (`+50%`)**:
  - Changed CLI default speech rate from `+200%` (3x) to `+50%` (1.5x) for optimal cognitive retention and focused listening flow.
  - Updated all documentation, skill configurations, and examples across `SKILL.md`, `README.md`, and `clean_speech_text.py`.
  - Maintained full backward compatibility for custom `--rate` overrides.

# Changelog

All notable changes to the `docx-speech-briefing-builder` project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.2.15] - 2026-09-16

### 🔧 Fixed & Improved
- **Micrometer & Roughness Spoken Normalization (TTS)**:
  - **Micrometer Units (`μm`, `µm`, `um`)**: Resolved issue where `Ra 3.2 - 6.3 μm` was erroneously read out as **“缪 m”** due to Greek letter `μ` (`\mu`) matching before unit translation; now pre-parsed and naturally spoken as **“微米”** (**“Ra 3点二至6点三 微米”**).
  - **LaTeX Micrometer (`\mu	ext{m}`, `\mu\mathrm{m}`, `\mum`)**: Automatically normalized in both TTS and Word rendering.
  - **Rogue Comma Suppression in Speech**: Cleaned rogue commas generated from LaTeX thin spaces or formula artifacts (e.g. `Ra, 3.2` or `Ra,3.2 ～ 6.3,`), preventing comma pauses in speech.
  - **Leading Decimal Protection**: Constrained outline/section numbering regex to prevent decimal numbers with engineering units at line beginnings (e.g. `0.8 μm`) from being misread as section headings (**“第 0 点 8 节”**).

- **Word (.docx) Typography & LaTeX Space Repair**:
  - **LaTeX Thin Spaces (`\,`, `\;`, `\:`, `\!`)**: Automatically converts LaTeX thin space commands to standard spaces in Phase 0.5. Completely eliminates the bug where `\,` had its backslash stripped in late cleanup, resulting in unwanted literal commas in Word body text (e.g. `$Ra\,3.2 \sim 6.3\,\mu	ext{m}$` previously rendering as `Ra,3.2 ～ 6.3,`).
  - **Unit Preservation in Word**: Prevents `\mum` from being wiped out by LaTeX command cleanup, ensuring `μm` displays clearly in `.docx` documents.
  - **Roughness & Range Comma Stripping**: Strips erroneous commas immediately following roughness symbols (`Ra,`, `Rz,`) or preceding range separators and units (`6.3, ～` -> `6.3 ～`, `10, μm` -> `10 μm`).

## [1.2.14] - 2026-09-16

### 🚀 Added & Improved
- **NPS & Inch Unit Spoken Normalization (TTS)**:
  - **NPS Pipe Size Expressions**: Resolved issue where pipe sizes such as `NPS 24"`, `NPS 24 in`, or standard `NPS 24` were spoken without units or lost the inch mark; now naturally and accurately spoken as **“NPS 24 英寸”**.
  - **Fractional & Mixed NPS**: Supported fractional pipe sizing including `NPS 1/4"`, `NPS 1/4` (**“NPS 四分之一 英寸”**) and `NPS 1 1/4"`, `NPS 1-1/4` (**“NPS 一又四分之一 英寸”**).
  - **Double Quote (") & Prime (″) as Inch Symbol**: Fixed parser issue where trailing double quotes after digits or fractions (`24"`, `1/2"`, `3/8"`, `1-1/4"`, `0.5"`) were treated as generic punctuation and discarded; now accurately recognized as inches (**“24 英寸”**, **“二分之一 英寸”**, **“八分之三 英寸”**).
  - **English Unit Words (`in`, `in.`, `inch`, `inches`)**: Solved issue where `3/8 in`, `1-1/4 in`, `24 in` were left as the English word "in" and mispronounced as `/ɪn/`; now systematically translated into **“英寸”** (**“八分之三 英寸”**, **“一又四分之一 英寸”**, **“24 英寸”**).
  - **Compound & Engineering Units**: Supported heat input and velocity units like `J/in.`, `kJ/in` (**“焦耳 每 英寸”** / **“千焦 每 英寸”**), `in./min` (**“英寸 每 分钟”**), and area/volume powers (`in²` -> **“平方英寸”**, `in³` -> **“立方英寸”**).
  - **Flange & Component Model Codes**: Supported pipe fitting model codes containing inch symbols (e.g. `BL2"-150 RF` -> **“BL 2 英寸 150 RF”**, `WN2"-150` -> **“WN 2 英寸 150”**).

## [1.2.14] - 2026-09-22

### 🔧 Fixed & Improved
- **1.5x Default Speed & Chinese Filename Standardization (1.5倍速基准与中文文件名标准化)**:
  - **1.5x Speech Rate Default**: Standardized default TTS narration rate to **1.5x (+50%)** across documentation, CLI parameters, and integration wrappers for optimal listening comfort and clarity.
  - **Full Chinese Path & Filename Native Support**: Verified and standardized UTF-8 Chinese naming convention (`报告_主题名称_时间戳.docx` / `.mp3`), providing intuitive file identification on mobile devices and desktop clients without character encoding issues.
  - **Documentation & Metadata Sync**: Synchronized `SKILL.md`, `README.md`, and version descriptors.

## [1.2.13] - 2026-09-14

### 🔧 Fixed & Improved
- **Standard Code & Amendment Slash Disambiguation (标准代号与修改单斜杠消歧)**:
  - **Standard Code Suffixes**: Resolved issue where slashes in standard codes (e.g. `GB/T`, `QB/T`, `HG/T`, `JB/T`, `DB11/T`, `GB/Z`, `T/CSAE`) were erroneously read out as math division **“除以”**; now cleanly converted into standard natural spoken letters and pause (e.g. `GB T`, `QB T`, `HG T`, `DB11 T`, `GB Z`, `T CSAE`).
  - **International Standard Organizations & Combined Specs**: Standard body combinations such as `ETRTO/ISO`, `ISO/IEC`, `ISO/TR`, `ISO/TS`, `IEC/TS` preserve slashes as natural separators without triggering math division.
  - **Standard Amendments & Corrigenda**: Slashes before standard revision/amendment tags (e.g. `ISO 5775-1:2014 / Amd 1:2020`, `EN 13445-3:2021 / A1:2023`, `BS EN 1234 / Cor 1`) are cleanly stripped into natural pauses.
  - **Word-Boundary Isolation for RT NDT Acronym**: Constrained the `RT` -> `R T 无损检测` replacement strictly to word boundaries (`\bRT\b`, `\bRT[1-4]\b`), eliminating phonetic corruption in words containing "RT" such as `ETRTO` (which was previously corrupted into `ET R T 无损检测 O`).
  - **Strict Math Division Integrity**: Guaranteed that engineering variable ratios and math formulas (e.g. `D/t > 80`, `P/S <= 0.385`, `d/D ≈ 0.465`, `a/b`) strictly retain **“除以”** (divided by).

## [1.2.12] - 2026-09-06

### Fixed
- Remove stray ASCII/full-width commas between quantities and recognized units.
- Read thousands-grouped numbers as Chinese cardinal values, including decimal fractions and ranges.
- Render engineering unit powers as Unicode superscripts (mm², mm³, mm⁴), and speak area/volume units naturally.
- Add regression checks for quantity normalization, compound units, and Word paragraphs/tables.

## [1.2.11] - 2026-09-06

### 🔧 Fixed & Improved
- **Chinese Translated Names & Interpunct Speech Optimization (间隔号口语化消歧)**:
  - **Foreign Translated Names**: Resolved the issue where middle dots (·) in foreign translated names (e.g. 格蕾塔·齐默·弗里德曼  , 卡尔·马克思, 列夫·托尔斯泰) were erroneously read out as math multiplication **“乘以”**; now cleanly converted into standard natural spoken spacing and syllables without noise.
  - **Names with Latin Initials**: Fully supports translated names containing English initials (e.g. 约翰·F·肯尼迪, J·K·罗琳, 乔治·W·布什, C·罗, J·R·R·托尔金), correctly removing the dots and pronouncing initials and surnames naturally.
  - **Chinese Interpuncts & Bullet Demarcation**: Middle dots in Chinese phrases (中国·北京, 内部受控工程资料 · 请勿外传), book/chapter titles (沁园春·雪), dates (九·一八), and bullet list items (· 第一点) are protected and preserved as natural pauses.
  - **Strict Math Dot Multiplication Scope**: Confined dot-operator (· / ⋅) multiplication speech synthesis strictly to mathematical variables and numerical formulas (e.g. P · R, 2 · 3, $t = \frac{P \cdot R}{S \cdot E}$), eliminating cross-domain phonetic corruption.

## [1.2.10] - 2026-09-04

### 🔧 Fixed & Improved
- **Percentage & Percent-Sign Speech Synthesis**: Resolved issue where `%` was omitted or swallowed in TTS synthesis:
  - **Standalone `%` / Quoted `%`**: Isolated `%` characters (e.g. table headers `合格率(%)`, phrases like `“%”符号`, or isolated units) are now clearly read as **“百分号”** instead of being stripped out by punctuation filtering.
  - **Comprehensive Percentage Recognition**: Added full support for spaced numbers (`95 %`), fullwidth symbols (`95％`), LaTeX escapes (`95\%`), and signed percentages (`±5%` -> **“正负百分之5”**, `-12.5%` -> **“负百分之12点五”**, `+5%` -> **“正百分之5”**).
  - **Percentage Range Continuity**: Supports all percentage range notations (`10%~20%`, `10 % ~ 20 %`, `10％～20％`, `10% - 20%`), naturally articulated as **“百分之10至百分之20”**.

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
