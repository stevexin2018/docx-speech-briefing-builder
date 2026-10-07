---
name: docx-speech-briefing-builder
version: 1.5.2
updated: 2026-10-08
description: 将 Markdown 深度工程报告自动转换为排版 Word 文档 (.docx) 与正常语速高品质语音讲解音频 (.mp3)。核心引擎已完全独立解耦至独立仓库 (https://github.com/stevexin2018/docx-speech-briefing-builder)。
---

# Word & Normal Speed Speech Briefing Builder (v1.5.2)

## 📌 概述
本 Skill 作为 OpenClaw 技能协议入口，底层直接连接 **`docx-speech-briefing-builder` 独立组件库**（独立 Git 仓库：`https://github.com/stevexin2018/docx-speech-briefing-builder`）。

一键将 Markdown 深度技术分析报告转换为（全链路原生支持中文文件名与 UTF-8 路径）：
1. **排版 Word 文档 (`.docx`)**：包含页眉页脚、标题层级、Unicode/OMML 公式转换、数据表格交替底色、引用高亮框、**自动剥离 ASCII 文本边框与纯符号分隔线**、**自动规范化温度度数排版（如 5^ / +5^ / +5^\circ\text{C} -> 5°C / +5°C）**；
2. **正常语速晓晓女声讲解音频 (`.mp3`)**：完整保留数学与工程运算符，口语化大纲编号与单位，默认以标准自然正常语速（+0%）生成高品质音频；
3. **一体化并发执行引擎 (`build_briefing.py`)**：通过多线程并发池同时并行执行 Word 渲染与 Edge-TTS 音频流合成，彻底消灭串行等待时间；
4. **TTS 分段受控并发合成**：多段文本默认双并发请求（`max_concurrency=2`），失败时自动降级回退串行逐段合成，兼顾速度与可靠性。

---

## 🛠️ 独立仓库架构与核心文件
独立仓库：`https://github.com/stevexin2018/docx-speech-briefing-builder`
- `version.py`：版本元数据定义 (`__version__ = "1.5.2"`)
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
