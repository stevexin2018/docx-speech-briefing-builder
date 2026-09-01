---
name: docx-speech-briefing-builder
version: 1.2.3
updated: 2026-09-01
description: 将 Markdown 深度工程报告自动转换为排版 Word 文档 (.docx) 与 3倍速高品质语音讲解音频 (.mp3)。核心引擎已完全独立解耦至独立仓库 /root/docx-speech-briefing-builder (https://github.com/stevexin2018/docx-speech-briefing-builder)。
---

# Word & 3x Speech Briefing Builder (v1.2.3)

## 📌 概述
本 Skill 作为 OpenClaw 技能协议入口，底层直接连接 **`docx-speech-briefing-builder` 独立组件库**（独立 Git 仓库：`/root/docx-speech-briefing-builder`）。

一键将 Markdown 深度技术分析报告转换为：
1. **排版 Word 文档 (`.docx`)**：包含页眉页脚、标题层级、Unicode/OMML 公式转换、数据表格交替底色、引用高亮框、**自动剥离 ASCII 文本边框与纯符号分隔线**、**自动规范化温度度数排版（如 5^ / +5^ / +5^\circ\text{C} -> 5°C / +5°C）**；
2. **3 倍速晓晓女声讲解音频 (`.mp3`)**：完整保留数学与工程运算符（除以、大于、小于、大于等于、小于等于、等于、不等于），智能区分公式除法、工程分式（1/4 -> 四分之一, 1 1/4 -> 一又四分之一）、工程单位（kJ/mm -> 千焦每毫米）与条款并列斜杠（QW-404.12 / QW-404.33 省略斜杠自然停顿），口语化多级大纲编号（1.1 -> 第 1 点 1 节），生成自然流畅的 3 倍速音频。

---

## 🛠️ 独立仓库架构与核心文件
独立仓库位置：`/root/docx-speech-briefing-builder`
- `version.py`：版本元数据定义 (`__version__ = "1.2.3"`)
- `CHANGELOG.md`：版本演进与发布历史
- `render_docx.py`：Word 渲染排版引擎
- `clean_speech_text.py`：语音口语化转换清洗器（公式发音转换、大纲章节编号口语化、断句停顿、数值范围与符号消歧）
- `test_docx_speech_harness.py`：自动化回归测试套件

---

## 🚀 快速使用 (CLI)

```bash
# 方式 1：调用生成完整附件包（Word + 3倍速音频）
python3 /root/.openclaw/workspace/scripts/generate_response_assets.py \
    --title "换热器管板厚度计算" \
    --topic-id "UHX-12" \
    --input "/path/to/report.md" \
    --out-dir "/root/.openclaw/workspace/media/responses"

# 方式 2：直接调用独立库 CLI
python3 /root/docx-speech-briefing-builder/render_docx.py \
    --title "UG-27 圆筒壁厚分析" \
    --topic-id "UG-27" \
    --input "/path/to/report.md" \
    --output "/path/to/output.docx"

python3 /root/docx-speech-briefing-builder/clean_speech_text.py \
    --input "/path/to/report.md" \
    --output "/path/to/voice.mp3" \
    --rate "+200%"
```

---

## 🔄 独立迭代机制

日常迭代优化在 `/root/docx-speech-briefing-builder` 中进行：
1. 修改代码并运行回归测试：`cd /root/docx-speech-briefing-builder && python3 test_docx_speech_harness.py`
2. 测试通过后提交并发布 Release：`git commit` & `gh release create vX.Y.Z`
3. 主工作区自动享受最新引擎能力，无需在主仓库中重复搬运代码。
