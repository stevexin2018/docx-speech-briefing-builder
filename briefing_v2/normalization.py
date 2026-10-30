"""Normalize typed text nodes; never apply document-wide LaTeX substitutions."""
import copy
import re
from collections import Counter

from engineering_text import normalize_quantities
from ascii_schematic import schematic_rows
from .diagnostics import SourceLocator

POWER_UNIT = re.compile(r"(?<![A-Za-z_])((?:km|cm|dm|mm|um|μm|µm|nm|in|ft|yd|m))([²³⁴])(?![A-Za-z0-9_])")
POWER_DIGITS = str.maketrans("²³⁴", "234")
REFERENCE_COMMAND = re.compile(r"\\(?:label|tag|ref|eqref|newcommand|renewcommand|def|usepackage|documentclass)\b")
_REMOVE = object()
BARE_SYMBOLS = {
    "alpha": "α", "beta": "β", "gamma": "γ", "Gamma": "Γ", "delta": "δ", "Delta": "Δ",
    "epsilon": "ε", "varepsilon": "ε", "zeta": "ζ", "eta": "η", "theta": "θ", "Theta": "Θ",
    "iota": "ι", "kappa": "κ", "lambda": "λ", "Lambda": "Λ", "mu": "μ", "nu": "ν",
    "xi": "ξ", "Xi": "Ξ", "pi": "π", "Pi": "Π", "rho": "ρ", "sigma": "σ", "Sigma": "Σ",
    "tau": "τ", "upsilon": "υ", "phi": "φ", "Phi": "Φ", "varphi": "φ", "chi": "χ",
    "psi": "ψ", "Psi": "Ψ", "omega": "ω", "Omega": "Ω", "le": "≤", "leq": "≤",
    "ge": "≥", "geq": "≥", "ne": "≠", "neq": "≠", "approx": "≈", "times": "×", "pm": "±",
}


def looks_like_path(text):
    return bool("\\" in text or re.match(r"(?:[A-Za-z]:/|https?://|(?:\.{1,2}|~)/|/)", text)
                or re.search(r"\.(?:md|docx|pdf|txt|json|py|ps1|exe|dll|csv|mp3)(?:$|[，。；])", text, re.I))


def _unit_inlines(text):
    nodes = []
    previous = 0
    for match in POWER_UNIT.finditer(text):
        prefix = text[previous:match.start()] + match[1]
        if prefix:
            nodes.append({"t": "Str", "c": prefix})
        nodes.append({"t": "Superscript", "c": [{"t": "Str", "c": match[2].translate(POWER_DIGITS)}]})
        previous = match.end()
    if previous == 0:
        return [{"t": "Str", "c": text}]
    if previous < len(text):
        nodes.append({"t": "Str", "c": text[previous:]})
    return nodes


def normalize_ast(ast, source, source_name="<markdown>"):
    result = copy.deepcopy(ast)
    locator = SourceLocator(source, source_name)
    diagnostics = []
    protected = []
    formulas = []
    counts = Counter()
    changes = 0

    def add(code, severity, message, literal, pointer):
        diagnostics.append(locator.diagnostic(code, severity, message, literal, pointer))

    def visit(value, pointer=""):
        nonlocal changes
        if isinstance(value, list):
            output = []
            for index, item in enumerate(value):
                path = f"{pointer}/{index}"
                if isinstance(item, dict) and item.get("t") == "Str":
                    text = item["c"]
                    if looks_like_path(text):
                        output.append(item)
                        continue
                    normalized = normalize_quantities(text)
                    # Bare m2 stays an identifier; a preceding numeric quantity resolves it.
                    if re.match(r"m[234](?![A-Za-z0-9_])", text) and index >= 2:
                        prior, gap = value[index - 2:index]
                        if (isinstance(prior, dict) and prior.get("t") == "Str"
                                and re.search(r"(?<![A-Za-z0-9_])\d+(?:\.\d+)?$", prior.get("c", ""))
                                and isinstance(gap, dict) and gap.get("t") == "Space"):
                            normalized = "m" + text[1].translate(str.maketrans("234", "²³⁴")) + text[2:]
                    converted = _unit_inlines(normalized)
                    if converted != [item]:
                        changes += 1
                        add("UNIT_NORMALIZED", "info", f"单位 {text!r} 已转换为原生上下标结构。", text, path)
                    if re.search(r"\d\^(?:$|[，。；])", text):
                        add("AMBIGUOUS_POWER", "warning", "孤立的脱字号含义不明确，已保留；请明确指数或温度单位。", text, path)
                    output.extend(converted)
                else:
                    converted = visit(item, path)
                    if converted is not _REMOVE:
                        if isinstance(converted, list) and isinstance(item, dict) and item.get('t') == 'CodeBlock':
                            output.extend(converted)
                        else:
                            output.append(converted)
            return output
        if not isinstance(value, dict):
            return value
        kind = value.get("t")
        if kind:
            counts[kind] += 1
        if kind == "CodeBlock":
            rows = schematic_rows(value["c"][1])
            if rows is not None:
                changes += 1
                add("ASCII_SCHEMATIC_NORMALIZED", "info", "剖面示意图已转为文字层次，移除装饰线。", value["c"][1], pointer)
                return [{"t": "Para", "c": [{"t": "Str", "c": row}]} for row in rows]
        if kind in {"Code", "CodeBlock"}:
            text = value["c"][1]
            protected.append({"kind": kind, "text": text, "node": pointer})
            if re.search(r"[α-ωΑ-Ω√≈∝]|\\(?:frac|sqrt)\b", text) and not looks_like_path(text):
                add("MATH_IN_CODE", "info", "含数学符号的代码片段已按原文保留；需要公式时请使用数学定界符。", text, pointer)
            return value
        if kind == "Math":
            text = value["c"][1]
            normalized = re.sub(r'(?<=\d)"', r'\\text{ in}', text)
            if normalized != text:
                changes += 1
                add("MATH_INCH_QUOTE_NORMALIZED", "info", "公式中的英寸引号已转换为明确的英寸单位。", text, pointer)
                value = {**value, "c": [value["c"][0], normalized]}
                text = normalized
            formulas.append({"text": text, "node": pointer})
            if REFERENCE_COMMAND.search(text):
                add("UNSUPPORTED_LATEX_COMMAND", "error", "此阶段不支持公式编号、引用或宏定义命令，请移出公式或展开定义。", text, pointer)
            if re.search(r"\^\*\d", text):
                add("AMBIGUOUS_SCRIPT", "warning", "星号后紧接数字的上下标写法可能有歧义，已保留原意；请核对分组。", text, pointer)
            return value
        if kind in {"RawInline", "RawBlock"}:
            format_name, text = value["c"]
            if format_name in {"tex", "latex"}:
                symbol = re.fullmatch(r"\\([A-Za-z]+)(\s*)", text)
                if kind == "RawInline" and symbol and symbol[1] in BARE_SYMBOLS:
                    changes += 1
                    add("BARE_SYMBOL_NORMALIZED", "warning", "未标记为公式的符号命令已转换为对应字符；完整表达式建议使用数学定界符。", text, pointer)
                    return {"t": "Str", "c": BARE_SYMBOLS[symbol[1]] + symbol[2]}
                add("UNDELIMITED_LATEX", "error", "数学内容未使用受支持的定界符，无法保证保留；请用 $...$ 或独立公式块。", text, pointer)
            elif format_name == "html":
                if kind == "RawInline" and re.fullmatch(r"<br\s*/?>", text, re.I):
                    changes += 1
                    return {"t": "LineBreak"}
                add("UNSUPPORTED_HTML", "error", "原始 HTML 尚未纳入此引擎的支持范围，请改用 Markdown。", text, pointer)
            else:
                add("UNSUPPORTED_RAW_CONTENT", "error", "此原始内容格式尚未纳入支持范围。", text, pointer)
            return value
        if kind in {"Para", "Plain"} and all(item.get("t") in {"Str", "Space", "SoftBreak"} for item in value["c"]):
            text = "".join(item.get("c", " ") for item in value["c"])
            if re.fullmatch(r"[-+_=*~#|\s]{2,}", text):
                changes += 1
                return _REMOVE
        if kind == "HorizontalRule":
            changes += 1
            return _REMOVE
        return {key: visit(child, f"{pointer}/{key}") for key, child in value.items()}

    result = visit(result)
    return result, {"source_counts": dict(counts), "normalizations": changes,
                    "protected": protected, "formulas": formulas}, diagnostics
