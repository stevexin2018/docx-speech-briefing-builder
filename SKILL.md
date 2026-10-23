---
name: docx-speech-briefing-builder
metadata:
  version: "2.0.0a2"
  updated: "2026-10-23"
description: 将 Markdown 深度工程报告自动转换为排版 Word 文档 (.docx) 与正常语速高品质语音讲解音频 (.mp3)。核心引擎已完全独立解耦至独立仓库 (https://github.com/stevexin2018/docx-speech-briefing-builder)。
---

# Word & Normal Speed Speech Briefing Builder (v2.0.0a2)

## 📌 概述
本 Skill 作为 OpenClaw 技能协议入口，底层直接连接 **`docx-speech-briefing-builder` 独立组件库**（独立 Git 仓库：`https://github.com/stevexin2018/docx-speech-briefing-builder`）。

一键将 Markdown 深度技术分析报告转换为（全链路原生支持中文文件名与 UTF-8 路径）：
1. **排版 Word 文档 (`.docx`)**：包含页眉页脚、标题层级、Unicode/OMML 公式转换、数据表格交替底色、引用高亮框、**自动剥离 ASCII 文本边框与纯符号分隔线**、**自动规范化温度度数排版（如 5^ / +5^ / +5^\circ\text{C} -> 5°C / +5°C）**；
2. **正常语速晓晓女声讲解音频 (`.mp3`)**：完整保留数学与工程运算符，口语化大纲编号与单位，默认以标准自然正常语速（+0%）生成高品质音频；
3. **一体化并发执行引擎 (`build_briefing.py`)**：通过多线程并发池同时并行执行 Word 渲染与 Edge-TTS 音频流合成，彻底消灭串行等待时间；
4. **TTS 分段受控并发合成**：多段文本默认双并发请求（`max_concurrency=2`），尊重 Retry-After 退避重试；失败取消其余请求，不整篇重放。默认保持指定音色，不自动换音色或服务。同步入口总时限 600 秒；异步调用方自行设置总时限。失败保留已有 MP3。

路径朗读约定：Windows 文件夹、文件与注册表路径中的反斜杠 `\` 默认转换为中文逗号，让 TTS 自然短暂停顿，不逐层读“反斜杠”“杠”或“backslash”。例如 `D:\项目\报告` 读作“D 盘，项目，报告”；UNC 路径以“网络共享”开头，文件扩展名仍读“点”。此规则仅作用于语音清洗，Word 中保留原始路径，LaTeX 命令沿用原有处理；需要说明字符本身时，在讲解稿中直接写“反斜杠”。

## v2 原生 Word 引擎试用

用户要求 v2 试用、新引擎或带缓存和诊断记录的报告时，使用 `trial_briefing.py`。此入口默认 `pandoc`，支持仅 Word、仅 MP3 或两者；只生成用户要求的格式。Windows 和 ARM 共用相同实现。

```bash
python trial_briefing.py --input report.md --docx report.docx --mp3 report.mp3 --title "工程技术报告"
```

试用入口自动保存 `.assets.json` 缓存清单，以及输出旁 `.briefing` 目录内每次调用的 JSON 和 Word 诊断；缓存命中、失败也记录。查看 `engine`、`status`、`rebuilt`、`reused`、`review_required`，不要把旧引擎缓存当成新引擎验证。诊断文件默认不作为附件交付；不支持的公式不得静默回退旧引擎。录音缓存独立于 Word 引擎和模板，改变语速、音色或语音清洗逻辑时才失效。试用音频需 ffprobe 校验。

ARM 原有 `openclaw_assets.py` 附件入口可加 `--trial`（默认新引擎），或明确指定 `--engine pandoc`；未指定时沿用兼容入口。试用操作不自动发送、发布或更新软件。详细缓存规则、记录字段和两端调用见 [docs/trial-workflow.md](docs/trial-workflow.md)。

当前为 alpha，原有 `build_briefing.py`、`render_docx.py` 默认仍使用兼容引擎 `legacy`；专用试用入口默认 `pandoc`。用户明确需要 Word 或音频时，统一入口支持只传 `--docx`、只传 `--mp3`，或同时传入两者。

启用新引擎时使用 `--engine pandoc`，需要 Pandoc 3.12.1 或更新版本；查找顺序为 `--pandoc`、`PANDOC_PATH`、本机手动安装的 `.runtime/pandoc/pandoc.exe`（Windows）或 `.runtime/pandoc/pandoc`（Linux）、PATH。运行目录不入 Git，也不自动下载程序。不要将机器专属安装路径写入共享代码。示例：

```bash
python build_briefing.py --input report.md --docx report.docx --engine pandoc --diagnostics diagnostics.json
```

新引擎通过文档结构分别处理正文、数学、代码、路径和表格。支持原生公式、标题样式和单位上下标；未知公式或内容丢失会使 Word 构建失败，保留已有输出文件。直接使用原有构建入口时，诊断 JSON 仅在指定 `--diagnostics` 时写出；专用试用入口自动记录。出现 `success_with_warnings` 时，应先核对提示内容再交付正式报告。

数学使用 `$...$`、`$$...$$`、`\(...\)` 或 `\[...\]`；代码和路径优先使用反引号，含空格的路径使用反引号或引号。不要将有歧义的 `5^` 自动补成温度，也不要自动将代码中的表达式改成数学公式。错误码、API、模板配置及支持边界见 [docs/v2-engine.md](docs/v2-engine.md)。

---

## 🛠️ 独立仓库架构与核心文件

若本机存在 `references/host-workflow.md`，另读该文件中的本机入口、缓存与附件约定；当前版本和引擎能力以本文件及 `version.py` 为准。发布、发送等操作仍需用户在当前任务中授权。

独立仓库：`https://github.com/stevexin2018/docx-speech-briefing-builder`
- `version.py`：统一版本元数据定义
- `CHANGELOG.md`：版本演进与发布历史
- `build_briefing.py`：**一体化并行构建引擎**（Word 渲染 + TTS 流式音频全并发）
- `render_docx.py`：Word 渲染排版引擎
- `clean_speech_text.py`：语音口语化转换清洗器 + **受控并发 TTS 合成引擎**
- `test_docx_speech_harness.py`：自动化回归测试套件

---

## 🚀 快速使用 (CLI)

```bash
# 【推荐】方式 1：一步直达一体化并发构建（Word + 正常语速音频完全并发）
python build_briefing.py \
    --input "/path/to/report.md" \
    --docx "/path/to/output.docx" \
    --mp3 "/path/to/output.mp3" \
    --title "工程技术深度解析" \
    --topic-id "Technology" \
    --rate "+0%"

# 方式 2：单独调用 Word 排版
python render_docx.py \
    --title "UG-27 圆筒壁厚分析" \
    --topic-id "UG-27" \
    --input "/path/to/report.md" \
    --output "/path/to/output.docx"

# 方式 3：单独调用语音生成
python clean_speech_text.py \
    --input "/path/to/report.md" \
    --output "/path/to/voice.mp3" \
    --rate "+0%"
```
