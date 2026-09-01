#!/usr/bin/env python3
"""
test_docx_speech_harness.py
===========================
回归与自进化测试套件 (v1.2.2)：
验证 Word 渲染与 3 倍速语音清洗引擎：
1. 数学与工程运算/比较符号完整保留 (D/t > 80 -> D 除以 t 大于 80, P/S <= 0.385 -> P 除以 S 小于等于 零点三八五)；
2. 标准条款并列斜杠口语化 (Part 5.2.4/5.4.3 -> Part 5 点 2 点 4 5 点 4 点 3, UG-28/UG-29 -> U G 第 28 条 U G 第 29 条)；
3. 大纲标题编号发音 (1. -> 第 1 点, 1.1 -> 第 1 点 1 节, 1.2 -> 第 1 点 2 节)；
4. 复杂工程文本、ASCII 边框行级过滤、LaTeX 嵌套与连字符消歧。
5. 条款/单位斜杠与小数区间号消歧。
"""

import os
import sys
import docx

DIR = os.path.dirname(os.path.abspath(__file__))
if DIR not in sys.path:
    sys.path.insert(0, DIR)

from clean_speech_text import clean_speech_text
from render_docx import create_docx_document

SAMPLE_MARKDOWN = """
1. 项目概况与核心定位

+-------------------------------------------------------------+
|                      重要提示与设计边界                     |
+-------------------------------------------------------------+
---------------------------------------------------------------
===============================================================

### 1.1 仓库基本信息
在设计温度 150°C ~ 350°C 范围内，碳钢材料壁厚在 10-20mm 之间。
当 D/t > 80 时，需按 Part 5.2.4/5.4.3 进行刚性校核。
UG-28/UG-29 要求对于外压圆筒，P/S <= 0.385。
QW-404.12 / QW-404.33 为并列条款，线能量单位为 kJ/mm。
推荐区间为 1.5 ～ 2.0。
接管厚度公差为 0.45mm，容积比为 2:1。

> $t = \\frac{P \\cdot R}{S \\cdot E - 0.6P}$

| 参数 | 物理含义 | 推荐取值 |
| :--- | :--- | :--- |
| P | 设计内压 | 2.5 MPa |
| S | 最大许用应力 | 138 MPa |
| E | 焊接接头系数 | 1.00 |

### 1.2 仓库结构与分发实质
1. 检查环向应力 $\\sigma_\\theta$ 与轴向应力 $\\sigma_z$。
2. 避免以下符号杂音污染：-------------------- ++++++++++ ========== ~~~~~~~~~
"""

def test_speech_cleaning():
    cleaned = clean_speech_text(SAMPLE_MARKDOWN)
    print("\n--- [TTS 清洗结果验证] ---")
    print(cleaned)

    # 验证大纲与章节发音
    assert "第 1 点 项目概况与核心定位" in cleaned or "第 1 点" in cleaned, "错误：一级大纲编号 1. 被吞或发音错误！"
    assert "第 1 点 1 节" in cleaned, "错误：二级大纲编号 1.1 未正确转为'第 1 点 1 节'！"
    assert "第 1 点 2 节" in cleaned, "错误：二级大纲编号 1.2 未正确转为'第 1 点 2 节'！"

    # 验证工程运算符与比较符号
    assert "D 除以 t 大于 80" in cleaned, "错误：D/t > 80 未正确转换为'D 除以 t 大于 80'！"
    assert "P 除以 S 小于等于" in cleaned, "错误：P/S <= 0.385 未正确转换为'P 除以 S 小于等于'！"
    assert "Part 5 点 2 点 4 5 点 4 点 3" in cleaned, "错误：Part 5.2.4/5.4.3 斜杠未正确省略停顿！"
    assert "U G 第 28 条 U G 第 29 条" in cleaned, "错误：UG-28/UG-29 未正确转换为条款停顿！"
    assert "Q W 第 404 点 12 条 Q W 第 404 点 33 条" in cleaned, "错误：QW 小数级并列条款被误读为除法！"
    assert "千焦 每 毫米" in cleaned, "错误：kJ/mm 未正确转换为工程单位‘千焦每毫米’！"
    assert "Q W 第 404 点 12 条 除以" not in cleaned, "错误：QW-404.12/QW-404.33 仍被误读为除法！"
    assert "千焦 除以" not in cleaned, "错误：kJ/mm 仍被误读为除法！"

    # 断言不包含刺耳的重复读音
    assert "至至" not in cleaned, "错误：TTS 文本中存在连续的'至'发音！"
    assert "加加" not in cleaned, "错误：TTS 文本中存在连续的'加'发音！"
    assert "等于等于" not in cleaned, "错误：TTS 文本中存在连续的'等于'发音！"
    assert "+---" not in cleaned, "错误：TTS 文本中残留 ASCII 边框！"
    assert "10至20" in cleaned, "未能正确识别数值区间！"
    assert "1点五至2点零" in cleaned, "未能正确朗读小数区间号‘1.5 ～ 2.0’！"
    assert clean_speech_text("1.5 ～ 2.0") == "1点五至2点零。", "行首小数区间被误判为大纲标题！"
    assert "零点四五" in cleaned, "未能正确逐位转换小数！"
    print("\n[✓] TTS 语音清洗与大纲编号测试全部通过！")

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
