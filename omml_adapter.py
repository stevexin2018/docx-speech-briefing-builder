#!/usr/bin/env python3
"""
omml_adapter.py
===============
Word OMML (Office Math Markup Language) 矢量数学公式适配器：
将 LaTeX 语法树解析并降维映射为 ISO/IEC 29500 标准的 OMML 节点 (<m:oMath>, <m:oMathPara>)。
具备零崩溃 Fallback 机制：若解析失败，安全降级回 Unicode 纯文本 Run。
"""

import xml.etree.ElementTree as ET
import latex2mathml.converter

M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"

def _mathml_node_to_omml(elem):
    tag = elem.tag.split('}')[-1]
    text = (elem.text or '').strip()

    if tag == 'mi':
        # 变量：默认斜体
        return f'<m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>{text}</m:t></m:r>'
    elif tag == 'mn':
        # 数值常量：正体
        return f'<m:r><m:rPr><m:sty m:val="p"/></m:rPr><m:t>{text}</m:t></m:r>'
    elif tag == 'mo':
        # 运算符与关系符
        sym = text
        if sym in ['&#x02264;', '&le;', '≤']: sym = '≤'
        elif sym in ['&#x02265;', '&ge;', '≥']: sym = '≥'
        elif sym in ['&#x000D7;', '&times;', '×']: sym = '×'
        elif sym in ['&#x02248;', '&approx;', '≈']: sym = '≈'
        elif sym in ['&#x000B1;', '&plusmn;', '±']: sym = '±'
        return f'<m:r><m:t> {sym} </m:t></m:r>'
    elif tag == 'mtext':
        # 普通正体文本
        return f'<m:r><m:rPr><m:sty m:val="p"/></m:rPr><m:t>{text}</m:t></m:r>'
    elif tag == 'msub':
        base = _mathml_node_to_omml(elem[0])
        sub = _mathml_node_to_omml(elem[1])
        return f'<m:sSub><m:e>{base}</m:e><m:sub>{sub}</m:sub></m:sSub>'
    elif tag == 'msup':
        base = _mathml_node_to_omml(elem[0])
        sup = _mathml_node_to_omml(elem[1])
        return f'<m:sSup><m:e>{base}</m:e><m:sup>{sup}</m:sup></m:sSup>'
    elif tag == 'msubsup':
        base = _mathml_node_to_omml(elem[0])
        sub = _mathml_node_to_omml(elem[1])
        sup = _mathml_node_to_omml(elem[2])
        return f'<m:sSubSup><m:e>{base}</m:e><m:sub>{sub}</m:sub><m:sup>{sup}</m:sup></m:sSubSup>'
    elif tag == 'mfrac':
        num = _mathml_node_to_omml(elem[0])
        den = _mathml_node_to_omml(elem[1])
        return f'<m:f><m:num>{num}</m:num><m:den>{den}</m:den></m:f>'
    elif tag == 'msqrt':
        inner = ''.join(_mathml_node_to_omml(c) for c in elem)
        return f'<m:rad><m:radPr><m:degHide m:val="on"/></m:radPr><m:deg/><m:e>{inner}</m:e></m:rad>'
    elif tag in ['mrow', 'math']:
        return ''.join(_mathml_node_to_omml(c) for c in elem)
    else:
        children = ''.join(_mathml_node_to_omml(c) for c in elem)
        return children if children else f'<m:r><m:t>{text}</m:t></m:r>'

def latex_to_omml(latex_code: str, display: bool = False) -> str:
    """
    将 LaTeX 字符串转换为 OMML XML 字符串。
    如果转换失败，抛出异常交由外层 fallback。
    """
    # 预处理清洗：去除多余外围空格与转义
    tex = latex_code.strip()
    if tex.startswith('$$') and tex.endswith('$$'):
        tex = tex[2:-2].strip()
        display = True
    elif tex.startswith('$') and tex.endswith('$'):
        tex = tex[1:-1].strip()

    mathml_str = latex2mathml.converter.convert(tex)
    root = ET.fromstring(mathml_str)
    inner_omml = _mathml_node_to_omml(root)

    if display:
        return f'<m:oMathPara xmlns:m="{M_NS}"><m:oMath>{inner_omml}</m:oMath></m:oMathPara>'
    return f'<m:oMath xmlns:m="{M_NS}">{inner_omml}</m:oMath>'
