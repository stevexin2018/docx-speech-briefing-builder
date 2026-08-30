---
name: docx-speech-briefing-builder
version: 1.1.0
updated: 2026-08-31
description: 将 Markdown 深度工程报告自动转换为排版 Word 文档 (.docx) 与 3倍速高品质语音讲解音频 (.mp3)。包含 LaTeX 公式 Unicode/OMML 转换、参数表格渲染、大纲标题层级美化、ASCII 边框行级过滤与语音口语化防杂音清洗。
---

# Word & 3x Speech Briefing Builder (v1.1.0)

## 📌 概述
本 Skill 用于将任何大模型生成的 Markdown 深度技术分析报告，一键转换为：
1. **排版 Word 文档 (`.docx`)**：包含页眉页脚、标题层级、Unicode/OMML 公式转换、数据表格交替底色、引用高亮框、**自动剥离 ASCII 文本边框与纯符号分隔线**；
2. **3 倍速晓晓女声讲解音频 (`.mp3`)**：自动剥离 Markdown 符号与公式语法，将工程公式/希腊字母/小数点/温度/百分比口语化，**彻底杜绝连字符与纯符号被误读为“至至至...”、“加加加...”或“等于等于...”**，生成自然流畅的 3 倍速音频。

---

## 🛠️ 核心文件结构
- `version.py`：版本元数据定义 (`__version__ = "1.1.0"`)
- `CHANGELOG.md`：详细版本演进与发布历史
- `render_docx.py`：Word 渲染排版引擎（含 11 阶段 LaTeX $\rightarrow$ Unicode/OMML 转换与 ASCII 边框过滤）
- `clean_speech_text.py`：语音口语化转换清洗器（公式发音转换、断句停顿、数值范围与符号消歧）
- `test_docx_speech_harness.py`：自进化与回归测试套件

---

## 🚀 快速使用 (CLI)

```bash
# 查看当前版本
python render_docx.py --version
python clean_speech_text.py --version

# 方式 1：直接调用核心渲染脚本
python render_docx.py \
    --title "换热器管板厚度计算" \
    --topic-id "UHX-12" \
    --input "/path/to/report.md" \
    --output "/path/to/output.docx"

# 方式 2：生成 3 倍速语音音频
python clean_speech_text.py \
    --input "/path/to/report.md" \
    --output "/path/to/voice.mp3" \
    --rate "+200%"
```

---

## 🔄 引擎持续自我迭代机制

当处理含有新奇 LaTeX 语法、特殊 ASCII 装饰符或复杂数学嵌套的文档时：
1. 运行回归测试套件：`python test_docx_speech_harness.py`
2. 捕获未清洗干净的符号样本，直接添加到 `clean_speech_text.py` 与 `render_docx.py` 中的清洗管道中，实现永久自进化。
