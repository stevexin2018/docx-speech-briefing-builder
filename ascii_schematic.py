"""Recognize a narrow class of labelled, horizontal ASCII section sketches."""

import re


_RULE = re.compile(r"^\s*([=-])\1{7,}\s*(?:<--\s*(.+))?\s*$")
_LAYER = re.compile(r"^\s*\[([^\]\n]+)\]\s*(?:<--\s*(.+))?\s*$")


def schematic_rows(source):
    """Return prose rows only when the whole code block is a labelled sketch.

    Other code, including formulas and meaningful ASCII operators, stays literal.
    """
    rows = []
    rules = 0
    for line in source.splitlines():
        if not line.strip():
            continue
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
