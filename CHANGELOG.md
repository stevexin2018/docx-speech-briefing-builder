## [1.4.1] - 2026-10-03

### 🐛 Fixed
- **工程单位 `mm` 边界断言修复**：将全局文本硬替换 `replace('mm', ' 毫米 ')` 重构为精准的前后字符边界断言 `(?<![A-Za-z_])mm(?![A-Za-z0-9_])`，杜绝将英文单词或拉丁学名中包含的 `mm`（如 `Emmenopterys`、`common`、`summary` 等）拆碎误读为“毫米”。
- 同步更新版本元数据与 Skill 说明至 `v1.4.1`。

## [1.4.0] - 2026-10-03

### 🚀 Added
- **TTS 分段受控并发合成引擎**：将串行逐段 TTS 请求升级为受控双并发（`max_concurrency=2`），多段文本合成耗时缩短 60-75%（实测 3 段文本从 11-20 秒降至 4-5 秒）。
- **自动降级回退机制**：并发合成遇到限流或网络异常时，自动退回串行逐段合成，保证交付可靠性。

### 🔧 Changed
- 更新 `build_briefing.py` 注释与描述为正常语速 + 并发合成。
- 更新 `SKILL.md` 版本号至 1.4.0，修正仓库路径为 GitHub URL（移除旧 Linux `/root/` 路径）。
- 更新 `README.md` 全面反映正常语速与并发特性。
- 更新 `clean_speech_text.py` CLI 版本号至 v1.4.0。

## [1.3.2] - 2026-10-03

### Fixed
- **Python 3.14 argparse 兼容性**：修复 `build_briefing.py` 中 `--rate` help 字符串 `%` 未转义导致 `ValueError` 崩溃的问题。

## [1.3.1] - 2026-10-03

### Changed
- **恢复默认正常语速（回归原点）**：将 Edge-TTS 默认合成语速从 `+50%`（1.5倍速）调整恢复为 `+0%` 标准自然语速（`rate="+0%"`），提供更从容舒缓的听觉体验。
- 更新 `build_briefing.py` 与 `clean_speech_text.py` 默认参数及帮助说明。
- 修复 `clean_speech_text.py` 中 argparse help 字符串格式化转义问题。
- 同步更新 `SKILL.md` 与多机器人调用规范文档。

## [1.3.0] - 2026-09-29

### 🚀 Added & Improved
- **Concurrent Dual-Pipeline Briefing Engine (`build_briefing.py`)**:
  - Implemented high-throughput multithreaded concurrent execution via `concurrent.futures.ThreadPoolExecutor`, executing Word (.docx) document rendering and Edge-TTS 1.5x audio synthesis in parallel.
  - Fully overlaps Word XML compilation within the streaming audio latency window, reducing total generation latency by over 40%.
  - Unifies two separate tool invocations into a single atomic CLI command, cutting Agent dispatch and process orchestration overhead in half.

## [1.2.24] - 2026-09-28

### 🔧 Fixed & Improved
- **Word (.docx) HTML `<br>` & Tag Elimination in Table Cells**:
  - Resolved historical defect where `<br>` / `<br/>` was only cleaned in TTS speech text but leaked literally into Word document table cells.
  - Implemented automatic conversion of `<br>`, `<br/>` directly into standard Word cell line breaks (`\n` / `<w:br/>`) and stripped rogue HTML tags during `clean_inline_text()`.
  - Ensures clean multiline layout in Markdown tables across all rendered Word reports without raw tag residuals.

## [1.2.23] - 2026-09-27

### 🚀 Added & Improved
- **Robust Chunked Streaming & Zero-Truncation TTS Engine (工业级分段流式抗截断语音合成)**:
  - **Native Async Python API**: Switched from external `edge-tts` CLI subprocess invocations to native Python `edge_tts.Communicate` async streaming API, gaining full control over audio packets and connection state.
  - **Smart Punctuation-Aware Chunking (智能自然标点切分)**: Implemented `split_text_chunks()` to automatically partition lengthy documents into safe-length segments (800~1000 characters) bounded by Chinese punctuation (`。！？；\n`), completely eliminating WebSocket transmission timeouts on long connections.
  - **Chunk-Level Exponential Backoff Retry (分块级指数退避重试)**: Added automated 3-attempt retry per chunk, seamlessly recovering from network jitter, proxy resets, and TCP RST interruptions without failing the entire document.
  - **Seamless MP3 Splicing (内存/文件流式无损拼接)**: Sequentially streams and writes audio frames into a single unified output file, ensuring perfectly continuous narration without acoustic breaks or artifacts.
  - **Multi-OS Adaptive Resilience (跨平台自适应与双重代理环境兼容)**: Solves the long-audio truncation issue under complex proxy configurations (e.g. Clash Verge System Proxy + TUN mode on Windows) while maintaining optimal speed on Linux (ARM/x86 VPS) and macOS.

## [1.2.19] - 2026-09-27

### 🔧 Fixed & Improved
- **Identifier, Account ID & Phone Number Digit-by-Digit Speech Synthesis (账号ID、电话号码与长数字编码逐位口语化消歧)**:
  - **Publisher & Account IDs**: Resolved issue where long identifier codes (e.g. `ca-pub-7710126386333548`, `pub-7710126386333548`, `ID: 9876543210`) were erroneously read out as astronomical cardinal quantities (such as "七千七百一十万亿..."); now cleanly converted to natural digit-by-digit spoken words (`ca pub 七七一零一二六三八六三三三五四八`).
  - **Telephone & Mobile Numbers**:
    - **Mobile numbers**: 11-digit mobile numbers (e.g. `13800138000`, `+86 13912345678`) are automatically formatted into standard Chinese 3-4-4 cadence (`一三八 零零一三 八零零零`).
    - **Landline numbers**: Area codes and local numbers (e.g. `010-12345678`, `0755-88888888 转 123`) preserve natural pauses without being mistaken as numeric ranges ("至").
    - **400 / 800 Hotlines**: Toll-free hotlines (e.g. `400-888-1234`, `800-820-5555`) are strictly pronounced digit-by-digit (`四零零 八八八 一二三四`).
  - **Order & Tracking Codes**: Numbers preceded by tags like 订单、编号、流水号、工单 (e.g. `订单编号20260927110614`) are pronounced digit-by-digit.
  - **Protection of True Quantities**: Preserved normal physical measurements, temperatures, thicknesses, and thousands-grouped cardinal numbers (e.g. `150°C ~ 350°C`, `10-20mm`, `1,234,567 元`).

## [1.2.18] - 2026-09-22

### 🔧 Fixed & Improved
- **1.5x Default Speed & Native Chinese Filename Support (1.5倍速发音基准与中文文件名支持)**:
  - **1.5x Narration Rate**: Officially standardized the default TTS narration rate to **1.5x (+50%)** across documentation, skill specifications, and CLI wrappers for optimal listening comprehension.
  - **Chinese Filename & Path Native Support**: Validated full UTF-8 native Chinese naming convention (`报告_中文主题_时间戳.docx` / `.mp3`), providing intuitive mobile/desktop document browsing without character encoding issues.
  - **Metadata & SKILL.md Sync**: Synchronized `SKILL.md`, `version.py`, and `CHANGELOG.md` to version **v1.2.18**.

## [1.2.17] - 2026-09-22

### 🔧 Fixed
- **Decimal Percentage Spoken Order (TTS)**:
  - Fixed an issue where decimal percentages like `0.35%`, `0.040%`, `0.43%`, `0.003%~0.005%` had their reading order reversed into “零点三五 百分号” instead of natural spoken Chinese “百分之零点三五”.
  - Expanded percentage regex patterns (`num_pat`) to correctly capture Chinese decimal strings (`零点...`, `...点...`) converted in preceding passes.
  - Ensured range separators and negative/plus signs (`±0.5%`, `-0.12%`, `0.003%~0.005%`) correctly read as “百分之...至百分之...”.
