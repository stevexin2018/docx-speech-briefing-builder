#!/usr/bin/env python3
"""
test_docx_speech_harness.py
===========================
回归与自进化测试套件：
验证 Word 渲染与 3 倍速语音清洗引擎对复杂工程文本、ASCII 边框、LaTeX 嵌套与连字符的处理能力。
"""

import os
import sys
import docx

# 添加当前目录
DIR = os.path.dirname(os.path.abspath(__file__))
if DIR not in sys.path:
    sys.path.insert(0, DIR)

from clean_speech_text import clean_speech_text
from render_docx import create_docx_document

SAMPLE_MARKDOWN = """
# ASME Sec VIII-1 UG-27 圆筒壁厚分析

+-------------------------------------------------------------+
|                      重要提示与设计边界                     |
+-------------------------------------------------------------+
---------------------------------------------------------------
===============================================================

### 【条款定位与原意】
在设计温度 150°C ~ 350°C 范围内，碳钢材料壁厚在 10-20mm 之间。
接管厚度公差为 0.45mm，容积比为 2:1。

> $t = \\frac{P \\cdot R}{S \\cdot E - 0.6P}$

| 参数 | 物理含义 | 推荐取值 |
| :--- | :--- | :--- |
| P | 设计内压 | 2.5 MPa |
| S | 最大许用应力 | 138 MPa |
| E | 焊接接头系数 | 1.00 |

### 【工程审计重点】
1. 检查环向应力 $\\sigma_\\theta$ 与轴向应力 $\\sigma_z$。
2. 避免以下符号杂音污染：-------------------- ++++++++++ ========== ~~~~~~~~~
"""

def test_speech_cleaning():
    cleaned = clean_speech_text(SAMPLE_MARKDOWN)
    print("\n--- [TTS 清洗结果验证] ---")
    print(cleaned)

    # 断言不包含刺耳的重复读音
    assert "至至" not in cleaned, "错误：TTS 文本中存在连续的'至'发音！"
    assert "加加" not in cleaned, "错误：TTS 文本中存在连续的'加'发音！"
    assert "等于等于" not in cleaned, "错误：TTS 文本中存在连续的'等于'发音！"
    assert "+---" not in cleaned, "错误：TTS 文本中残留 ASCII 边框！"
    assert "10至20" in cleaned, "未能正确识别数值区间！"
    assert "零点四五" in cleaned, "未能正确逐位转换小数！"
    print("\n[✓] TTS 语音清洗测试全部通过！")

def test_docx_rendering():
    out_docx = "/tmp/test_harness_output.docx"
    create_docx_document("UG-27 圆筒壁厚分析", "UG-27", SAMPLE_MARKDOWN, out_docx)
    doc = docx.Document(out_docx)
    
    print("\n--- [Word 渲染结果段落验证] ---")
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    for p in paragraphs:
        assert not p.startswith("+---"), f"错误：Word 段落中残留 ASCII 边框线: {p}"
        assert not p.startswith("----"), f"错误：Word 段落中残留减号分割线: {p}"
        assert not p.startswith("===="), f"错误：Word 段落中残留等号分割线: {p}"
        print("  -", p[:50])

    print("\n[✓] Word 文档渲染测试全部通过！无残留符号行。")

if __name__ == "__main__":
    test_speech_cleaning()
    test_docx_rendering()
