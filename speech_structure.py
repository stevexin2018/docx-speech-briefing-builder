"""Parse mathematical structure before the compatibility prose cleaner runs."""
import re
import xml.etree.ElementTree as ET
from engineering_text import cardinal_cn


class SpeechMathError(ValueError):
    """Do not publish speech when mathematical meaning cannot be preserved."""


GREEK = dict(zip("αβγδεζηθικλμνξπρστυφχψωΓΔΘΛΞΠΣΦΨΩϕϵϑ",
    ["阿尔法", "贝塔", "伽马", "德尔塔", "艾普西隆", "截塔", "艾塔", "西塔",
     "约塔", "卡帕", "兰姆达", "缪", "纽", "克西", "派", "柔", "西格玛", "套",
     "宇普西龙", "斐", "希", "普西", "欧米伽", "伽马", "德尔塔", "西塔", "兰姆达",
     "克西", "派", "西格玛", "斐", "普西", "欧米伽", "斐", "艾普西隆", "西塔"]))
OPERATORS = {
    "=": "等于", "+": "加上", "-": "减去", "−": "减去", "±": "正负", "∓": "负正",
    "×": "乘以", "⋅": "乘以", "·": "乘以", "/": "除以", "÷": "除以",
    "<": "小于", ">": "大于", "≤": "小于等于", "≥": "大于等于", "≠": "不等于",
    "≈": "约等于", "≃": "约等于", "≅": "约等于", "∼": "相似于", "∝": "正比于", "≡": "恒等于",
    "(": "括号", ")": "括号结束", "[": "方括号", "]": "方括号结束",
    "{": "大括号", "}": "大括号结束", "|": "竖线", "‖": "双竖线",
    "∘": "复合", "*": "星号运算", "∗": "星号运算",
    ",": "，", ";": "；", ":": "比", "!": "阶乘", "%": "百分号", "°": "度",
    "∑": "求和", "∏": "连乘", "∫": "积分", "∬": "二重积分", "∭": "三重积分",
    "∞": "无穷大", "→": "趋向", "⇒": "推出", "∈": "属于", "∉": "不属于",
    "∂": "偏微分", "∇": "纳布拉", "…": "省略号", "⋯": "省略号", "⋮": "竖向省略号",
    "∧": "且", "∨": "或", "∅": "空集", "∪": "并集", "∩": "交集",
    "⁡": "", "⁢": "乘以", "⁣": "，", ".": "点",
}
FUNCTIONS = {"cos": "余弦", "sin": "正弦", "tan": "正切", "cot": "余切",
    "arccos": "反余弦", "arcsin": "反正弦", "arctan": "反正切", "cosh": "双曲余弦",
    "sinh": "双曲正弦", "tanh": "双曲正切", "max": "最大值", "min": "最小值",
    "log": "对数", "ln": "自然对数", "exp": "指数函数", "lim": "极限", "det": "行列式"}
UNITS = {"m": "米", "mm": "毫米", "cm": "厘米", "s": "秒", "kg": "千克",
         "N": "牛", "Pa": "帕", "MPa": "兆帕", "K": "开尔文", "rad": "弧度"}


def _number(text):
    if re.fullmatch(r"\d+", text):
        return cardinal_cn(text)
    if re.fullmatch(r"\d+\.\d+", text):
        a, b = text.split(".")
        return cardinal_cn(a) + "点" + "".join("零一二三四五六七八九"[int(c)] for c in b)
    raise SpeechMathError("无法口述此数学数字。")


def speak_math(latex):
    """Speak supported TeX through MathML, preserving explicit group boundaries."""
    # A spacing command immediately before the degree superscript belongs to
    # the preceding number, not to the superscript's base in MathML.
    latex = re.sub(r'(?<=[0-9}])\\(?:\s|,|;|:|!)(?=\s*\^\s*\{?\\circ)', '', latex)
    roughness = re.fullmatch(r'\s*(Ra|Rz|Ry|Rq|Sa|Sz)\\,\s*(\d+(?:\.\d+)?)\s*\\sim\s*'
                             r'(\d+(?:\.\d+)?)\\,\s*\\mu\\(?:text|mathrm)\{m\}\s*', latex)
    if roughness:
        def decimal(value):
            if '.' not in value:
                return value
            a, b = value.split('.')
            return a + '点' + ''.join('零一二三四五六七八九'[int(c)] for c in b)
        return f'{roughness[1]} {decimal(roughness[2])} 至 {decimal(roughness[3])} 微米'
    temperature = re.fullmatch(r"\s*([+−-]?)(\d+(?:\.\d+)?)\s*\^\s*\{?\\circ\}?\s*"
        r"(?:\\(?:text|mathrm)\{([CF])\}|([CF]))\s*", latex)
    if temperature:
        sign, value, a, b = temperature.groups()
        return (("零下 " if sign in {"-", "−"} else "正 " if sign else "") + value +
                (" 摄氏度" if (a or b) == "C" else " 华氏度"))
    from latex2mathml.converter import convert
    try:
        root = ET.fromstring(convert(latex))
    except Exception as error:
        raise SpeechMathError("数学语音结构解析失败；请检查公式，已有音频保留。") from error

    def kind(node):
        return node.tag.rsplit("}", 1)[-1]

    def degree(node):
        children = list(node)
        return (kind(node) == 'msup' and len(children) == 2
                and kind(children[0]) == 'mn'
                and ''.join(children[1].itertext()).strip() in {'∘', '°'})

    def unit(node):
        return (node.text or '').strip() if kind(node) in {'mtext', 'mi'} else ''

    def sequence(nodes):
        parts, previous, index = [], None, 0
        nodes = list(nodes)
        while index < len(nodes):
            node = nodes[index]
            following = index + 1
            while following < len(nodes) and kind(nodes[following]) == 'mspace':
                following += 1
            temp = (degree(node) and following < len(nodes) and unit(nodes[following]) in {'C', 'F'})
            if temp:
                spoken = visit(list(node)[0]) + (' 摄氏度' if unit(nodes[following]) == 'C' else ' 华氏度')
                if previous is not None and kind(previous) == 'mo' and (previous.text or '') in {'-', '−'}:
                    if len(parts) == 1 or (len(parts) >= 2 and parts[-2] in {'等于', '括号', '在', '，', '；'}):
                        parts[-1] = '零下'
                index = following
            else:
                spoken = visit(node)
            index += 1
            if not spoken:
                continue
            is_connector = kind(node) == 'mtext' and unit(node) == '@'
            previous_connector = previous is not None and kind(previous) == 'mtext' and unit(previous) == '@'
            numeric_unit = previous is not None and kind(previous) == 'mn' and unit(node) in UNITS
            if (previous is not None and kind(previous) not in {"mo", "mspace"}
                    and kind(node) not in {"mo", "mspace"} and (previous.text or "") not in FUNCTIONS
                    and not is_connector and not previous_connector and not numeric_unit):
                parts.append("乘以")
            parts.append(spoken)
            previous = node
        return " ".join(parts)

    def visit(node):
        tag, children, text = kind(node), list(node), node.text or ""
        if tag in {"math", "mrow", "mstyle", "mpadded", "semantics", "mtd"}:
            return sequence(children)
        if tag in {"mi", "mtext", "ms"}:
            if "\\" in text:
                raise SpeechMathError("存在未支持的数学命令；不能将命令名直接送入语音。")
            if text == "ℓ":
                return "小写 l"
            if text in GREEK:
                return GREEK[text]
            if text in FUNCTIONS:
                return FUNCTIONS[text]
            if tag == 'mtext' and text.strip() == '@':
                return '在'
            if tag == 'mtext' and text.strip() in UNITS:
                return UNITS[text.strip()]
            if node.get("mathvariant") == "normal" and text in UNITS:
                return UNITS[text]
            return text
        if tag == "mn":
            return _number(text)
        if tag == "mo":
            if text in FUNCTIONS:
                return FUNCTIONS[text]
            if text not in OPERATORS:
                raise SpeechMathError("存在未支持的数学运算符，不能保证语音含义。")
            return OPERATORS[text]
        if tag == "mfrac" and len(children) == 2:
            return f"分子为 {visit(children[0])}，除以分母 {visit(children[1])}，分式结束"
        if tag in {"msub", "msup", "msubsup"}:
            base = visit(children[0])
            if tag in {"msub", "msubsup"}:
                base += f" 下标 {visit(children[1])}，下标结束"
            if tag in {"msup", "msubsup"}:
                power = children[-1]
                value = "".join(power.itertext()).strip()
                if value in {'∘', '°'}:
                    if tag != 'msup' or kind(children[0]) != 'mn':
                        raise SpeechMathError('无法确定圆圈上标的数学含义。')
                    base += ' 度'
                elif value in {'*', '∗'}:
                    base += ' 上标星号'
                elif value in {'2', '3'}:
                    base += {'2': ' 的平方', '3': ' 的立方'}[value]
                else:
                    base += f" 的 {visit(power)} 次方"
            return base
        if tag == "msqrt":
            return f"根号内 {sequence(children)}，根号结束"
        if tag == "mroot" and len(children) == 2:
            return f"{visit(children[1])} 次根号内 {visit(children[0])}，根号结束"
        if tag in {"munder", "mover", "munderover"}:
            base = visit(children[0])
            if tag in {"munder", "munderover"}:
                base += f" 下限 {visit(children[1])}，下限结束"
            if tag in {"mover", "munderover"}:
                base += f" 上方 {visit(children[-1])}，上方结束"
            return base
        if tag == "mtable":
            rows = [f"第{cardinal_cn(i + 1)}行 " + "，".join(visit(cell) for cell in row)
                    for i, row in enumerate(children)]
            return "矩阵开始，" + "；".join(rows) + "，矩阵结束"
        if tag == "mfenced":
            return "括号 " + "，".join(visit(c) for c in children) + " 括号结束"
        if tag in {"mspace", "annotation"}:
            return ""
        raise SpeechMathError(f"此数学结构尚不支持可靠口述：{tag}。")
    return visit(root)


def protect_structure(text, path_speaker):
    """Return guarded prose and a restorer; placeholders contain no numbers."""
    vault, prefix = {}, "SPEECHGUARD"
    while prefix in text:
        prefix += "Q"

    def save(value):
        i, letters = len(vault), ""
        while True:
            letters, i = chr(65 + i % 26) + letters, i // 26 - 1
            if i < 0:
                break
        token = prefix + letters + "ZZQ"
        vault[token] = value
        return token

    text = re.sub(r"(?m)^\s*:{3,}(?:\s*(?:\{[^\n]*\}|[\w.-]+))?\s*$", "", text)

    def code(match):
        value = match[0]
        value = "\n".join(value.splitlines()[1:-1]) if value.startswith(("```", "~~~")) else value.strip("`")
        if re.search(r"(?:[A-Za-z]:[\\/]|\\\\|HKLM:|HKCU:)", value):
            return save(path_speaker(value))
        return save(value.replace("\\", " 反斜杠 ").replace("_", " 下划线 "))
    text = re.sub(r"(?ms)^\s*(`{3,}|~{3,})[^\n]*\n.*?^\s*\1\s*$|`+[^`\n]+`+", code, text)
    bare_path = r'''(?<![A-Za-z0-9_])(?:[A-Za-z]:[\\/]|(?:HKLM|HKCU|HKEY_[A-Z_]+):[\\/]|\\\\[A-Za-z0-9_.-]+[\\/])[^\s，。！？；：、`"'<>\[\]{}()]+'''
    text = re.sub(bare_path, lambda m: save(path_speaker(m[0])), text)
    pattern = (r"\$\$(.*?)\$\$|\\\[(.*?)\\\]|\\\((.*?)\\\)|"
               r"(?<![\\$])\$(?![$\s])([^\n$]+?)(?<!\s)\$(?![$\d])")
    text = re.sub(pattern, lambda m: save(speak_math(next(g for g in m.groups() if g is not None))), text, flags=re.S)
    if "$$" in text or r"\[" in text or r"\(" in text:
        raise SpeechMathError("数学定界符未闭合；已有音频保留。")
    def plain_formula(match):
        # Plain prose can use gamma1 or K3 as identifiers. Only unambiguous
        # stand-alone arithmetic with explicit grouping/multiplication is parsed.
        expression = match[1]
        if not re.search(r'[·⋅×/^()]', expression) or re.search(r'[A-Za-zα-ωΑ-Ω]\d', expression):
            return match[0]
        return save(speak_math(expression)) + (match[2] or '')
    text = re.sub(r"(?m)^\s*([A-Za-zα-ωΑ-Ω][A-Za-z0-9_α-ωΑ-Ω]*\s*[=≈]\s*[^\n。；]+)([。；]?)\s*$",
                  plain_formula, text)

    def standard(match):
        items = re.split(r'\s*/\s*(?![TZ]\b|[TZ](?=\d)|(?:IEC|TR|TS)(?=\s|\d))', match[0])
        spoken_items = []
        for item in items:
            head, edition = re.split(r'[-—:](?=\d{4}$)', item, maxsplit=1) if re.search(r'[-—:]\d{4}$', item) else (item, None)
            head = re.sub(r'ISO/(IEC|TR|TS)', r'ISO \1', head)
            spoken = head.replace('/', ' 斜杠 ').replace('.', ' 点 ').replace('-', ' 连接号 ')
            spoken = spoken.replace('ASME', 'A S M E')
            if edition:
                spoken += ' 年版 ' + ''.join('零一二三四五六七八九'[int(c)] for c in edition)
            spoken_items.append(spoken)
        return save(' 或 '.join(spoken_items))
    org = r'(?:ISO(?:/(?:IEC|TR|TS))?|(?:ASTM|ASME|EN|DIN|BS|JIS|AWS|API|NACE|AMPP|WRC|GB|JB|HG|NB|SH|SY|QB|DB\d{0,2})(?:/[TZ])?)\s*'
    number = r'(?:[A-Za-z]{1,6}\s*-?\s*)?\d+(?:[.-]\d+)*(?:[A-Za-z]{1,3})?(?::\d{4})?'
    text = re.sub(r'(?<![A-Za-z0-9_])' + org + number +
                  r'(?:\s*/\s*(?:' + org + r')?' + number + r')*(?![A-Za-z0-9_])', standard, text, flags=re.I)
    text = re.sub(r"(?<![\w.])(\d+)[-－](Φ|φ|∅)?(\d+(?:\.\d+)?)\s*[×x](\d+(?:\.\d+)?)(?![\w.])",
        lambda m: save(f"{m[1]} 个 " + ("直径 " if m[2] else "") + f"{m[3]} 乘以 {m[4]}"), text)
    text = re.sub(r'(?<![\w.])(\d+)[-－][Φφ∅](\d+(?:\.\d+)?)(?![\w.×x])',
                  lambda m: save(f'{m[1]} 个直径 {m[2]}'), text)
    model_tokens = []
    def model(match):
        spoken = match[1] + ' 连接号 ' + match[2]
        if match[3]:
            spoken += ' 或 ' + match[1] + ' 连接号 ' + match[3]
        token = save(spoken)
        model_tokens.append(token)
        return token
    text = re.sub(r'(?<![\w])([A-Z][A-ZⅠⅡⅢⅣ0-9.]*\d[A-ZⅠⅡⅢⅣ0-9.]*)-([A-Z]+)(?:\s*/\s*([A-Z]+))?(?![\w])', model, text)
    if model_tokens:
        choices = '(?:' + '|'.join(map(re.escape, model_tokens)) + ')'
        text = re.sub('(' + choices + r')\s*/\s*(?=' + choices + ')', r'\1 或 ', text)

    def restore(value):
        if vault:
            value = re.sub("|".join(map(re.escape, sorted(vault, key=len, reverse=True))), lambda m: vault[m[0]], value)
        return re.sub(r"\s+", " ", value).strip()
    return text, restore
