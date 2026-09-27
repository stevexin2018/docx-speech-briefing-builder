"""Shared normalization for engineering quantities and unit exponents."""

import re

# 1. 明确的面积/体积度量单位（支持简写纯数字 2, 3, 4，如 mm2, mm3, cm2, in2 等）
AREA_VOL_UNITS = r'(?:km|cm|mm|um|μm|µm|nm|in|ft|yd)'
POWER_ALL = r'(?:\^\{([234])\}|\^([234])|([234²³⁴]))'
POWER_CARET = r'(?:\^\{([234])\}|\^([234])|([²³⁴]))'

RE_AREA_VOL = re.compile(r'(?<![A-Za-z_])(' + AREA_VOL_UNITS + r')' + POWER_ALL + r'(?![A-Za-z0-9_])')

# 2. 单字母米 m：只有在前面有数字或除号/斜杠时（如 10m2, 10 m2, /m2, /m3），或者显式带有 ^ 时才转换为上标
# 坚决避免将独立的变量或缩写如 m1, m2, m3 误伤
RE_METER = re.compile(r'(?<=\d|\/)([ 	]*)(m)' + POWER_ALL + r'(?![A-Za-z0-9_])|(?<![A-Za-z_])(m)' + POWER_CARET + r'(?![A-Za-z0-9_])')

# 3. 其他物理单位（MPa, Pa, N, J, W, kg, s, mol, L, K 等）：必须有显式脱字号 ^2, ^3 或本身已是 ²³⁴
# 绝对禁止将 K3 (Kimi K3, K3芯片), S2 (S2钢材, S2赛季), N2 (N2工艺), L2 (L2缓存) 转换为上标！
OTHER_UNITS = r'(?:MPa|GPa|kPa|Pa|kJ|MJ|J|kN|N|kg|mg|g|ms|min|s|h|mol|mL|L|K|W|kW|MW|Hz|kHz|MHz|GHz|V|kV|A|mA|Ω|ohm|bar|mbar|°C|°F|℃)'
RE_OTHER = re.compile(r'(?<![A-Za-z_])(' + OTHER_UNITS + r')' + POWER_CARET + r'(?![A-Za-z0-9_])')


def normalize_quantities(text):
    # 清理数字与单位间多余的逗号：如 10, mm3 -> 10 mm3
    all_units = AREA_VOL_UNITS + r'|m|' + OTHER_UNITS
    text = re.sub(r'(?<=\d)[ 	]*[,，][ 	]*(?=(?:' + all_units + r')(?![A-Za-z_]))', ' ', text)

    # 1. 面积体积度量单位
    def _repl_area(m):
        u = m.group(1)
        p = m.group(2) or m.group(3) or m.group(4)
        return u + p.translate(str.maketrans('234', '²³⁴'))
    text = RE_AREA_VOL.sub(_repl_area, text)

    # 2. 单字母米 m
    def _repl_meter(m):
        if m.group(2): # 有前置数字/斜杠
            sp = m.group(1)
            u = m.group(2)
            p = m.group(3) or m.group(4) or m.group(5)
            return sp + u + p.translate(str.maketrans('234', '²³⁴'))
        else: # 显式带 ^ 的 m^2
            u = m.group(6)
            p = m.group(7) or m.group(8) or m.group(9)
            return u + p.translate(str.maketrans('234', '²³⁴'))
    text = RE_METER.sub(_repl_meter, text)

    # 3. 其他物理单位
    def _repl_other(m):
        u = m.group(1)
        p = m.group(2) or m.group(3) or m.group(4)
        return u + p.translate(str.maketrans('234', '²³⁴'))
    text = RE_OTHER.sub(_repl_other, text)

    return text


def cardinal_cn(number):
    """Read a nonnegative integer by base-10000 groups."""
    n = int(number)
    if n == 0:
        return '零'
    digits = '零一二三四五六七八九'
    for value, label in ((100000000, '亿'), (10000, '万')):
        if n >= value:
            high, low = divmod(n, value)
            prefix = '两' if high == 2 else cardinal_cn(high)
            remainder = ('一' if 10 <= low < 20 else '') + cardinal_cn(low)
            return prefix + label + (('零' if low < value // 10 else '') + remainder if low else '')
    result = ''
    pending_zero = False
    for value, label in ((1000, '千'), (100, '百'), (10, '十'), (1, '')):
        digit, n = divmod(n, value)
        if digit:
            if pending_zero:
                result += '零'
            result += digits[digit] + label
            pending_zero = False
        elif result and n:
            pending_zero = True
    return result[1:] if result.startswith('一十') else result
