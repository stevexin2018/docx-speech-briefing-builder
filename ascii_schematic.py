"""Convert recognized labelled section/assembly sketches to ordered prose."""

import re


_RULE = re.compile(r"^\s*([=-])\1{7,}\s*(?:<--\s*(.+))?\s*$")
_LAYER = re.compile(r"^\s*\[([^\]\n]+)\]\s*(?:<--\s*(.+))?\s*$")
_TEXT_LANGUAGES = {"", "text", "txt", "plaintext", "ascii", "diagram", "schematic"}
_BOX_EDGE = re.compile(r"\+[-=]{3,}(?:\+[-=]{3,})*\+|[\u2500-\u257f]{3,}")
_BOX_STROKES = re.compile(r"[\u2500-\u257f]+|\|")
_FILL = re.compile(r"[-=]{3,}|#{3,}|_{3,}")
_LEADER = re.compile(r"<[-=]{2,}|[-=]{2,}>")
_DIRECTION = {"▲": "向上", "△": "向上", "↑": "向上", "▼": "向下",
              "▽": "向下", "↓": "向下", "◀": "向左", "←": "向左",
              "▶": "向右", "→": "向右", "↔": "左右双向", "↕": "上下双向"}
_PROGRAM = re.compile(
    r"^\s*(?:def |class |import |from |return\b|if\b|for\b|while\b|"
    r"function\b|const |let |var |SELECT\b|INSERT\b|UPDATE\b|"
    r"print\s*\(|printf\s*\(|console\.|//|/\*)", re.I)


def schematic_rows(source, language=""):
    """Return prose rows only when the whole code block is a labelled sketch.

    Other code, including formulas and meaningful ASCII operators, stays literal.
    """
    if language.lower() not in _TEXT_LANGUAGES:
        return None
    lines = [line for line in source.splitlines() if line.strip()]
    if not lines:
        return None
    # A block containing only long drawing rules has no spoken content.
    if all(re.fullmatch(r"[\s+\-|=#_\u2500-\u257f]{3,}", line) for line in lines):
        return []
    rows = _layer_rows(lines)
    if rows is not None:
        return rows
    return _assembly_rows(lines)


def _layer_rows(lines):
    rows = []
    rules = 0
    for line in lines:
        rule = _RULE.fullmatch(line)
        if rule:
            rules += 1
            if rule[2]:
                if not rows:
                    return None
                rows[-1] += "；" + rule[2].strip()
            continue
        layer = _LAYER.fullmatch(line)
        if not layer:
            return None
        row = layer[1].strip()
        if layer[2]:
            row += "；" + layer[2].strip()
        rows.append(row)
    return rows if rules >= 2 and len(rows) >= 2 else None


def _assembly_rows(lines):
    # Require an actual box edge plus labelled engineering content. Do not
    # mistake general code, arithmetic or an isolated minus sign for a drawing.
    if not any(_BOX_EDGE.search(line) for line in lines):
        return None
    if any(_PROGRAM.search(line) for line in lines):
        return None
    labelled = [line for line in lines if re.search(r"[\u3400-\u9fff]", line)]
    if len(labelled) < 2:
        # A single annotated connector row can have labels on both sides.
        if len(lines) != 1:
            return None
        parts = _BOX_EDGE.split(lines[0])
        if len(parts) < 2 or not all(
                re.search(r"[\u3400-\u9fff]", part) for part in (parts[0], parts[-1])):
            return None
    rows = []
    for line in lines:
        stripped = line.strip()
        if stripped in _DIRECTION:
            rows.append(_DIRECTION[stripped])
            continue
        value = _LEADER.sub("  ", line)
        value = _BOX_EDGE.sub("  ", value)
        value = _BOX_STROKES.sub("  ", value)
        value = _FILL.sub("  ", value)
        # Residual junctions belong to drawing runs; ordinary '+' in labels,
        # material identifiers, dimensions and negative numbers stay intact.
        value = re.sub(r"(?<!\S)\+(?!\S)", "  ", value)
        value = re.sub(r"\[([^\]\n]+)\]", r"\1", value)
        value = re.sub(r"[ \t]{2,}", "；", value.strip())
        value = value.strip("； ")
        if value:
            rows.append(value)
    return rows or None
