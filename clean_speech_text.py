#!/usr/bin/env python3
"""
clean_speech_text.py
====================
语音口语化转换清洗器：
将工程 Markdown / 特殊字符转为自然流畅、高可读性的口语文本。
- 精准保留数学与工程运算符号（除以、大于、小于、大于等于、小于等于、等于、不等于）；
- 智能区分工程分式（如 1/4 -> 四分之一, 1 1/4 -> 一又四分之一）、工程单位（kJ/mm -> 千焦每毫米）与条款并列斜杠；
- 精准识别大纲标题编号 (1. -> 第 1 点, 1.1 -> 第 1 点 1 节, 1.2 -> 第 1 点 2 节)；
- 保持小数点逐位精准发音 (0.45 -> 零点四五) 与多级章节编号发音；
- 保留小数区间语义 (1.5 ～ 2.0 -> 1点五至2点零)；
- 彻底杜绝 ASCII 边框线、连字符误读。
"""

import re
import os
import sys

_BS = '\\\\'

CN_NUMS = {
    0: '零', 1: '一', 2: '二', 3: '三', 4: '四', 5: '五',
    6: '六', 7: '七', 8: '八', 9: '九', 10: '十'
}

def int_to_cn(n: int) -> str:
    if n in CN_NUMS:
        return CN_NUMS[n]
    if n < 20:
        return '十' + CN_NUMS.get(n % 10, str(n % 10))
    if n < 100:
        tens = n // 10
        rem = n % 10
        return (CN_NUMS.get(tens, str(tens)) if tens > 1 else '') + '十' + (CN_NUMS.get(rem, '') if rem > 0 else '')
    return str(n)

def convert_mixed_fraction(m):
    whole = int(m.group(1))
    num = int(m.group(2))
    den = int(m.group(3))
    whole_cn = int_to_cn(whole)
    den_cn = int_to_cn(den)
    num_cn = int_to_cn(num)
    return f" {whole_cn}又{den_cn}分之{num_cn} "

def convert_simple_fraction(m):
    num = int(m.group(1))
    den = int(m.group(2))
    den_cn = int_to_cn(den)
    num_cn = int_to_cn(num)
    return f" {den_cn}分之{num_cn} "

def convert_section_number(m):
    num_str = m.group(1)
    parts = num_str.split('.')
    return '第 ' + ' 点 '.join(parts) + ' 节 '

def spoken_signed_number(sign: str, number: str) -> str:
    if sign in ('-', '−'):
        return f'零下 {number}'
    if sign == '+':
        return f'正 {number}'
    return number

def temperature_unit_name(unit: str) -> str:
    return '华氏度' if unit == '°F' else '摄氏度'

def convert_temperature_range(m):
    start = spoken_signed_number(m.group(1), m.group(2))
    end = spoken_signed_number(m.group(4), m.group(5))
    start_unit = temperature_unit_name(m.group(3))
    end_unit = temperature_unit_name(m.group(6))
    return f'{start} {start_unit} 至 {end} {end_unit}'

def convert_temperature_value(m):
    value = spoken_signed_number(m.group(1), m.group(2))
    unit = temperature_unit_name(m.group(3))
    return f'{value} {unit}'

def convert_path_to_speech(path_str: str) -> str:
    """将文件系统路径、注册表路径与可执行文件名转换为易于 TTS 自然朗读的口语发音文本，精准保留反斜杠与扩展名发音。"""
    p = path_str.strip('`"\'')
    
    # 1. 驱动器盘符识别：C:\ -> C 盘 反斜杠, C:/ -> C 盘 斜杠, C: -> C 盘
    p = re.sub(r'^([A-Za-z]):\\', r'\1 盘 反斜杠 ', p)
    p = re.sub(r'^([A-Za-z]):/', r'\1 盘 斜杠 ', p)
    p = re.sub(r'^([A-Za-z]):(?![A-Za-z0-9])', r'\1 盘 ', p)
    
    # 2. 注册表前缀识别：HKLM:\ -> H K L M 冒号 反斜杠
    p = re.sub(r'^(HKLM|HKCU|HKCR|HKU|HKEY_[A-Z_]+):\\', r'\1 冒号 反斜杠 ', p)
    p = re.sub(r'^(HKLM|HKCU|HKCR|HKU|HKEY_[A-Z_]+):/', r'\1 冒号 斜杠 ', p)
    
    # 3. UNC 网络共享前缀：\\ -> 反斜杠反斜杠
    p = re.sub(r'^\\\\\\', '反斜杠反斜杠 ', p)
    
    # 4. 路径中所有剩余反斜杠 -> 反斜杠
    p = p.replace('\\', ' 反斜杠 ')
    
    # 5. 路径中正斜杠 -> 斜杠
    p = p.replace('/', ' 斜杠 ')
    
    # 6. 文件扩展名点号转换（防止后续标点清除阶段被误吞）：.lnk -> 点 lnk, .exe -> 点 exe
    p = re.sub(r'\.([A-Za-z0-9]+)(?=[ \t]*$|[，。！？；：、\s])', r' 点 \1 ', p)
    
    return p

def clean_speech_text(text: str) -> str:
    """
    通用语音清洗引擎 (v1.2.6)：
    将工程 Markdown / 特殊字符转为自然流畅、高可读性的口语文本。
    """
    if not text:
        return ""

    # 1. 预处理：行级过滤与大纲编号转换
    lines = text.split("\n")
    cleaned_lines = []
    
    for line in lines:
        l = line.strip()
        if not l:
            continue
            
        # 过滤掉纯符号构成的分割线、装饰线、ASCII 表格边框等 (+----+----+ 或 -------------- 或 ======)
        if re.match(r'^[-+_=\*~#|`\s]{2,}$', l):
            continue
        # 过滤 Markdown 表格对齐分割线: |:---|:---|
        if re.match(r'^\|[\s:\-\+\\\\|=]+\|$', l):
            continue

        # 移除 Markdown 标题符 (#, ##, ### 等) 与引用/无序列表前缀 (-, *, +)
        # 注意：避免误吞以正负温标开头的行（如 +5°C 或 -20°C）
        l = re.sub(r'^[#>*+\-]+[ \t]+(?!\d)|^[#>]+[ \t]*', '', l)

        # 大纲与章节编号口语化转换（杜绝 1. 被吞或 1.2 读成 2）
        # 1.1 多级大纲编号 (如 1.1, 1.2, 2.1.3)
        l = re.sub(r'^(\d+(?:\.\d+)+)[ \t]+(?![~～\-至])(?=\S)', convert_section_number, l)
        # 1.2 顶级大纲/有序列表 (如 1., 2., 1、, 1))
        l = re.sub(r'^(\d+)(?:[、\)]|\.(?!\d))[ \t]*', r'第 \1 点 ', l)

        # 移除纯外框的 | 符号 (如 ASCII 框里的 | 文字 |)
        l = re.sub(r'^\|[ \t]*', '', l)
        l = re.sub(r'[ \t]*\|$', '', l)

        # 确保每个独立段落/列表项末尾有明确标点，在 TTS 中产生自然停顿
        if not l.endswith(("。", "！", "？", "；", "：")):
            l += "。"
        cleaned_lines.append(l)

    # 拼接段落
    text = " 。 ".join(cleaned_lines)

    # 2. 路径识别与 Markdown 标记清洗
    # 2.1 优先处理行内代码块 `...` 中的文件路径与程序名
    def _repl_inline_code(m):
        code_content = m.group(1).strip()
        if (re.search(r'[A-Za-z]:[\\/]', code_content) or 
            '\\' in code_content or 
            re.search(r'\.(?:exe|dll|lnk|msi|bat|cmd|docx|md|txt|xml|json|config|log|swidtag|hdi|spv|onnx|ptx|bc|hio|sldprt|sldasm|slddrw|eprt|easm|edrw|dwg|dxf|step|stp|iges|igs|sat|x_t|x_b|3dxml|cgr|catpart|catproduct|prt|asm|ipt|iam|par|jt|stl|obj|xvl|mp3|wav|zip|tar|gz|7z|pdf|html|htm|py|ps1|sh)\b', code_content, re.IGNORECASE) or
            re.search(r'^(?:HKLM|HKCU|HKCR|HKU|HKEY_):', code_content)):
            return convert_path_to_speech(code_content)
        return code_content

    text = re.sub(r'`([^`\r\n]+)`', _repl_inline_code, text)

    # 2.2 识别未包裹反引号的裸露路径（Windows 盘符路径、注册表路径、UNC 共享路径）
    bare_path_pattern = r'(?<![A-Za-z0-9_])(?:[A-Za-z]:[\\/]|(?:HKLM|HKCU|HKCR|HKU|HKEY_[A-Z_]+):[\\/]|\\\\[A-Za-z0-9_.-]+[\\/])[^\s，。！？；：、`"\'<>\[\]{}()]+'
    text = re.sub(bare_path_pattern, lambda m: convert_path_to_speech(m.group(0)), text)

    # 2.3 转换任何残留的反斜杠（确保路径中所有的反斜杠均被自然发音为“反斜杠”）
    text = re.sub(r'(?<=[A-Za-z0-9_\u4e00-\u9fa5])\\(?=[A-Za-z0-9_\u4e00-\u9fa5])', ' 反斜杠 ', text)
    text = text.replace('\\', ' 反斜杠 ')

    # 2.4 移除粗体/斜体/剩余行内代码等 Markdown 标记
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)

    # 3. 彻底消除连续重复的无意义符号（防止触发重复发音）
    text = re.sub(r'[\-+_=~*#|]{2,}', ' ', text)

    # 3.1 移除所有空 LaTeX 花括号（如 {}°C -> °C），避免 Word/TTS 残留。
    text = re.sub(r'\{\s*\}', '', text)
    # 3.2 温度与度数 LaTeX / 简写符号预修复 (如 +5^\circ\text{C}, 5^\circ C, +5^ 环境下 -> +5°C)
    text = re.sub(r'(?:\^|\^\{|\{)?' + _BS + r'(?:circ|degree)(?:\})?\s*(?:' + _BS + r'(?:text|mathrm)?\{?([CFcf])\}?|([CFcf]))', r'°\1\2', text)
    text = re.sub(r'(?:\^|\^\{|\{)?' + _BS + r'(?:circ|degree)(?:\})?', '°', text)
    text = re.sub(r'([+\-]?\d+(?:\.\d+)?)\^(?=[ \t]*[CFcf]\b)', r'\1°', text)
    text = re.sub(r'([+\-]?\d+(?:\.\d+)?)\^(?=[ \t]*[\u4e00-\u9fa5（\(\)，。！？；：`\'"]|$)', r'\1°C', text)

    # 4. 【关键】条款、标识符与单位中的斜杠消歧（在除法识别前执行）
    # 4.1 复合条款名并列，支持小数级条款号
    #     (如 QW-404.12/QW-404.33, UG-28/UG-29, VIII-1/VIII-2)
    clause_id = r'[A-Za-z]+-[A-Za-z0-9]+(?:\.[A-Za-z0-9]+)*'
    text = re.sub(fr'({clause_id})\s*/\s*({clause_id})', r'\1 \2', text)
    # 4.2 Part / Clause / Section / Appendix(App.) 等引用并列（如 App. 2 / App. Y）。
    reference_label = r'(?:Part|Clause|Section|Table|Fig|Figure|Appendix|App\.?)'
    text = re.sub(fr'({reference_label}\s*[A-Za-z0-9.]+)\s*/\s*({reference_label}\s*[A-Za-z0-9.]+)', r'\1 \2', text, flags=re.IGNORECASE)
    # 4.3 多级章节编号并列 (如 5.2.4/5.4.3 或 4.1.2/4.1.3)
    text = re.sub(r'(\b\d+(?:\.\d+)+\b)\s*/\s*(\b\d+(?:\.\d+)+\b)', r'\1 \2', text)
    # 4.4 中文条款并列 (如 第 28 条/第 29 条)
    text = re.sub(r'(第\s*\d+\s*条)\s*/\s*(第\s*\d+\s*条)', r'\1 \2', text)
    # 4.5 工程单位中的“/”表示“每”，而不是数学口语“除以” (如 kJ/mm, N/mm2, mm/s)
    unit_token = r'(?:kJ|MJ|J|kN|N|MPa|GPa|Pa|kg|g|mg|km|cm|mm|m|s|min|h|K|mol|L|mL)(?:[²³23])?'
    text = re.sub(fr'(?<![A-Za-z0-9])({unit_token})\s*/\s*({unit_token})(?![A-Za-z0-9])', r'\1 每 \2', text)
    # 4.6 多字母名称/缩写并列不按除法朗读；单字母公式变量 D/t、P/S 仍留给后续除法规则。
    text = re.sub(r'\b([A-Za-z]{2,})\s*/\s*([A-Za-z]{2,})\b', r'\1 \2', text)
    # 4.7 带材料体系标签的并列牌号 (如 Alloy 800HT / UNS N08811) 省略斜杠并自然停顿。
    material_label = r'(?:Alloy|UNS|Grade|Type)'
    text = re.sub(fr'\b({material_label}\s+[A-Za-z0-9.-]+)\s*/\s*({material_label}\s+[A-Za-z0-9.-]+)\b', r'\1 \2', text, flags=re.IGNORECASE)
    # 4.8 数字开头或字母开头的材料牌号并列 (如 304L/316L、A516-70/A537-1、A1/B2、RT1/RT2)。
    material_grade = r'(?=[A-Za-z0-9.-]*[A-Za-z])(?=[A-Za-z0-9.-]*\d)[A-Za-z0-9.-]+'
    text = re.sub(fr'\b({material_grade})\s*/\s*({material_grade})\b', r'\1 \2', text)

    # 5. 标准与条款口语发音
    text = re.sub(r'Sec\s+VIII-1', 'Sec VIII 第 1 卷', text, flags=re.IGNORECASE)
    text = re.sub(r'UG-(\d+)', r'U G 第 \1 条', text)
    text = re.sub(r'UW-(\d+)', r'U W 第 \1 条', text)
    text = re.sub(r'UCS-(\d+)', r'U C S 第 \1 条', text)
    text = re.sub(r'UHA-(\d+)', r'U H A 第 \1 条', text)
    def convert_qw_clause(m):
        return 'Q W 第 ' + ' 点 '.join(m.group(1).split('.')) + ' 条'
    text = re.sub(r'QW-(\d+(?:\.\d+)*)', convert_qw_clause, text)

    # 6. 多级章节编号口语化 (如 5.2.4 -> 5 点 2 点 4)
    def convert_multi_dot(m):
        parts = m.group(0).split('.')
        return ' 点 '.join(parts)
    text = re.sub(r'\b\d+(?:\.\d+){2,}\b', convert_multi_dot, text)

    # 7. 小数点逐位发音 (如 0.385 -> 零点三八五)
    digit_map = {'0':'零', '1':'一', '2':'二', '3':'三', '4':'四', '5':'五', '6':'六', '7':'七', '8':'八', '9':'九'}
    def fix_decimal_speech(m):
        int_p = m.group(1)
        dec_p = m.group(2)
        int_str = '零' if int_p == '0' else int_p
        dec_str = ''.join(digit_map.get(d, d) for d in dec_p)
        return f'{int_str}点{dec_str}'
    text = re.sub(r'(\d+)\.(\d+)', fix_decimal_speech, text)

    # 8. 工程分式、带分数、比例与范围
    # 8.1 带分数 (如 1 1/4, 2 1/2, 1-1/4, 2-1/2, 3 3/8 -> 一又四分之一, 二又二分之一)
    text = re.sub(r'(?<![A-Za-z0-9.])(\d+)[ \t\-]+(\d+)\s*/\s*(\d+)(?![A-Za-z0-9.])', convert_mixed_fraction, text)
    # 8.2 纯数字真/假分数 (如 1/4, 1/2, 3/4, 3/8, 5/16, 11/16 -> 四分之一, 二分之一)
    text = re.sub(r'(?<![A-Za-z0-9./])(\d{1,3})\s*/\s*(\d{1,3})(?![A-Za-z0-9./])', convert_simple_fraction, text)
    # 8.3 带正负号的温度与温度区间（如 -269℃ ~ 900℃ -> 零下269摄氏度至900摄氏度）。
    decimal_number = r'\d+(?:点[零一二三四五六七八九]+)?'
    temperature_unit = r'(?:℃|°C|°F)'
    text = re.sub(fr'([+\-−]?)({decimal_number})\s*({temperature_unit})\s*[~～至]\s*([+\-−]?)({decimal_number})\s*({temperature_unit})', convert_temperature_range, text)
    text = re.sub(fr'([+\-−]?)({decimal_number})\s*({temperature_unit})', convert_temperature_value, text)
    # 8.4 比例与普通数值范围 (2:1 -> 2 比 1, 10-20mm -> 10至20毫米)
    text = re.sub(r'(\d+(?:点[\w]+)?)\s*[:比]\s*(\d+(?:点[\w]+)?)', r'\1 比 \2', text)
    text = re.sub(r'(\d+(?:点[\w]+)?)%\s*[~～\-至]\s*(\d+(?:点[\w]+)?)%', r'百分之\1至百分之\2', text)
    text = re.sub(r'(\d+(?:点[\w]+)?)\s*[~～﹋〜～至]\s*(\d+(?:点[\w]+)?)', r'\1 至 \2', text)
    text = re.sub(r'(\d+(?:点[\w]+)?)\s*-\s*(\d+(?:点[\w]+)?)', r'\1至\2', text)
    text = re.sub(r'(\d+(?:点[\w]+)?)%', r'百分之\1', text)

    # 9. 希腊字母口语化
    greek_tts_map = {
        r'\alpha': ' 阿尔法 ', r'\beta': ' 贝塔 ', r'\gamma': ' 伽马 ', r'\Gamma': ' 伽马 ',
        r'\delta': ' 德尔塔 ', r'\Delta': ' 德尔塔 ', r'\epsilon': ' 艾普西隆 ', r'\varepsilon': ' 艾普西隆 ',
        r'\zeta': ' 截塔 ', r'\eta': ' 艾塔 ', r'\theta': ' 西塔 ', r'\Theta': ' 西塔 ',
        r'\iota': ' 约塔 ', r'\kappa': ' 卡帕 ', r'\lambda': ' 兰姆达 ', r'\Lambda': ' 兰姆达 ',
        r'\mu': ' 缪 ', r'\nu': ' 纽 ', r'\xi': ' 克西 ', r'\Xi': ' 克西 ',
        r'\pi': ' 派 ', r'\Pi': ' 派 ', r'\rho': ' 柔 ', r'\sigma': ' 西格玛 ',
        r'\Sigma': ' 西格玛 ', r'\tau': ' 套 ', r'\upsilon': ' 宇普西龙 ', r'\phi': ' 斐 ',
        r'\Phi': ' 斐 ', r'\varphi': ' 斐 ', r'\chi': ' 希 ', r'\psi': ' 普西 ',
        r'\Psi': ' 普西 ', r'\omega': ' 欧米伽 ', r'\Omega': ' 欧米伽 ',
        'α': ' 阿尔法 ', 'β': ' 贝塔 ', 'γ': ' 伽马 ', 'Γ': ' 伽马 ',
        'δ': ' 德尔塔 ', 'Δ': ' 德尔塔 ', 'ε': ' 艾普西隆 ',
        'ζ': ' 截塔 ', 'η': ' 艾塔 ', 'θ': ' 西塔 ', 'Θ': ' 西塔 ',
        'ι': ' 约塔 ', 'κ': ' 卡帕 ', 'λ': ' 兰姆达 ', 'Λ': ' 兰姆达 ',
        'μ': ' 缪 ', 'ν': ' 纽 ', 'ξ': ' 克西 ', 'Ξ': ' 克西 ',
        'π': ' 派 ', 'Π': ' 派 ', 'ρ': ' 柔 ', 'σ': ' 西格玛 ',
        'Σ': ' 西格玛 ', 'τ': ' 套 ', 'υ': ' 宇普西龙 ', 'φ': ' 斐 ',
        'Φ': ' 斐 ', 'χ': ' 希 ', 'ψ': ' 普西 ', 'Ψ': ' 普西 ',
        'ω': ' 欧米伽 ', 'Ω': ' 欧米伽 '
    }
    for k, v in greek_tts_map.items():
        if k.startswith('\\\\'):
            text = re.sub(re.escape(k) + r'\b', v, text)
        else:
            text = text.replace(k, v)

    # 10. 比较与运算符号口语化（精准保留 大于、小于、大于等于、小于等于、等于、不等于、除以、乘以）
    # 10.1 比较符
    text = re.sub(r'\\ge\b|\\geq\b|>=|≥', ' 大于等于 ', text)
    text = re.sub(r'\\approx\b|≈|≃|≅', ' 约等于 ', text)
    text = re.sub(r'\\le\b|\\leq\b|<=|≤', ' 小于等于 ', text)
    text = re.sub(r'!=|≠|\\ne\b|\\neq\b', ' 不等于 ', text)
    text = re.sub(r'>', ' 大于 ', text)
    text = re.sub(r'<', ' 小于 ', text)
    text = re.sub(r'==|(?<=[A-Za-z0-9])\s*=\s*(?=[A-Za-z0-9])|(?<=\s)=\s*(?=\s)', ' 等于 ', text)

    # 10.2 乘除法与加减
    text = re.sub(r'\\times\b|×|\\cdot\b|·', ' 乘以 ', text)
    text = re.sub(r'\\pm\b|±', ' 正负 ', text)
    # 除法/比值: 凡是在英文、数字、下标花括号之间的 / 均读作 除以 (如 D/t, P/S, a/b)
    text = re.sub(r'([A-Za-z0-9_\}]+)\s*/\s*([A-Za-z0-9_\{]+)', r'\1 除以 \2', text)
    # 加减符号: 变量/数字间转为“加上”，前置正负号转为“正/负”
    text = re.sub(r'(?<=[A-Za-z0-9])\s*\+\s*(?=[A-Za-z0-9])', ' 加上 ', text)
    text = re.sub(r'(?<![A-Za-z0-9])\+\s*(?=\d)', '正 ', text)

    # 11. LaTeX 结构与函数
    text = re.sub(r'\\sqrt\{\\frac\{([^{}]+)\}\{([^{}]+)\}\}', r'根号下 \1 除以 \2', text)
    text = re.sub(r'\\sqrt\{([^{}]+)\}', r'根号下 \1', text)
    text = re.sub(r'\\left\(|\\right\)', '', text)
    text = re.sub(r'\\left\[|\\right\]', '', text)
    text = re.sub(r'\\frac\{([^{}]+)\}\{([^{}]+)\}', r'\1 除以 \2', text)
    text = re.sub(r'\\Delta\s*t_\{?thin\}?|\\Delta\s*t_{\\text\{thin\}}', '冲压减薄裕量', text)
    text = re.sub(r'\\text\{([^{}]+)\}', r'\1', text)
    text = re.sub(r'\$([^$]+)\$', r'\1', text)

    # 12. 温标识别 (如 150 摄氏度, +5 摄氏度, -20 摄氏度)
    text = re.sub(r'(正\s*\d+|[+\\-]?\d+(?:点[\w]+)?)\s*(?:℃|°C|\^\s*\\circ\s*\\text\{C\}|\^\s*\\circ\s*C|\\degree\s*C)', r'\1 摄氏度 ', text)
    text = re.sub(r'(正\s*\d+|[+\\-]?\d+(?:点[\w]+)?)\s*(?:°F|\^\s*\\circ\s*\\text\{F\}|\^\s*\\circ\s*F|\\degree\s*F)', r'\1 华氏度 ', text)

    # 12.1 无数值前缀的温标单位（如单位列表中的 °C / °F）。
    text = re.sub(r'(?<![A-Za-z0-9])°C\b', ' 摄氏度 ', text)
    text = re.sub(r'(?<![A-Za-z0-9])°F\b', ' 华氏度 ', text)
    # 12.2 角度识别：剩余的“数值°”按角度朗读（温标 °C / °F 已在前序规则中处理）。
    text = re.sub(r'([+\-−]?\d+(?:点[零一二三四五六七八九]+)?)\s*°(?![CFcf])', r'\1 度 ', text)

    # 13. 单位与工程缩写
    text = text.replace('ASME', 'A S M E ')
    text = text.replace('Appendix', '附录')
    text = text.replace('kJ', ' 千焦 ')
    text = text.replace('MPa', ' 兆帕 ')
    text = text.replace('mm', ' 毫米 ')
    text = text.replace('RT1', ' R T 1 ')
    text = text.replace('RT2', ' R T 2 ')
    text = text.replace('RT3', ' R T 3 ')
    text = text.replace('RT4', ' R T 4 ')
    text = text.replace('RT', ' R T 无损检测 ')

    # 14. 清理孤立无用符号（保留汉字、英文字母、数字和核心中文标点）
    text = re.sub(r'[`\*•~_#|\\\'\"<>\(\)\[\]\{\}]', ' ', text)
    text = re.sub(r'[^\w\s\u4e00-\u9fa5，。！？；：、]', ' ', text)
    
    # 15. 空格与标点修剪
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'([，。！？；：、])\s*([，。！？；：、])+', r'\1', text)
    text = re.sub(r'^[，。！？；：、\s]+', '', text)
    text = re.sub(r'[，。！？；：、\s]+$', '。', text)

    return text.strip()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Clean speech text and generate 3x audio.")
    parser.add_argument("--version", action="version", version="docx-speech-briefing-builder v1.2.7")
    parser.add_argument("--input", help="Input markdown file")
    parser.add_argument("--output", help="Output mp3 file")
    parser.add_argument("--rate", default="+200%", help="Speech rate")
    parser.add_argument("--proxy", default=None, help="Proxy URL (e.g. http://127.0.0.1:7897)")
    args = parser.parse_args()

    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            raw = f.read()
        cleaned = clean_speech_text(raw)
        if args.output:
            import os, subprocess, socket
            proxy = args.proxy or os.environ.get("HTTP_PROXY") or os.environ.get("HTTPS_PROXY") or os.environ.get("ALL_PROXY") or os.environ.get("http_proxy") or os.environ.get("https_proxy")
            if not proxy:
                for p_candidate in ["127.0.0.1:7897", "127.0.0.1:7890"]:
                    host, port = p_candidate.split(":")
                    try:
                        with socket.create_connection((host, int(port)), timeout=0.3):
                            proxy = f"http://{p_candidate}"
                            break
                    except Exception:
                        pass

            cmd = ["edge-tts", "--voice", "zh-CN-XiaoxiaoNeural", f"--rate={args.rate}", "--text", cleaned, "--write-media", args.output]
            if proxy:
                cmd.extend(["--proxy", proxy])
            subprocess.run(cmd, check=True)
            print(f"Audio saved to {args.output}")
        else:
            print(cleaned)
