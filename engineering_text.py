"""Shared normalization for engineering quantities and unit exponents."""

import re

UNIT = r'(?:MPa|GPa|kPa|Pa|kJ|MJ|J|kN|N|kg|mg|g|km|cm|mm|um|μm|µm|m|ms|min|s|h|mol|mL|L|K|°C|°F|℃|in)'
POWER = r'(?:\^\{([234])\}|\^([234])|([234²³⁴]))'
UNIT_POWER = re.compile(r'(?<![A-Za-z_])(' + UNIT + ')' + POWER + r'(?![A-Za-z0-9_])')


def normalize_quantities(text):
    text = re.sub(r'(?<=\d)[ \t]*[,，][ \t]*(?=' + UNIT + r'(?![A-Za-z_]))', ' ', text)
    return UNIT_POWER.sub(
        lambda m: m[1] + next(g for g in m.groups()[1:] if g).translate(str.maketrans('234', '²³⁴')),
        text,
    )


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
