"""Modern Word settings and conservative display-equation paragraph repair.

These settings do not assert that a mobile client has passed visual acceptance.
The math objects themselves, including fractions and growing delimiters, remain
unchanged. Narrow-screen clients must still be checked on the actual device.
"""
from copy import deepcopy
import re

from docx.enum.text import WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph

WORD_URI = "http://schemas.microsoft.com/office/word"
SETTINGS_TAIL = (
    "w:compat", "w:docVars", "w:rsids", "m:mathPr", "w:attachedSchema",
    "w:themeFontLang", "w:clrSchemeMapping", "w:doNotIncludeSubdocsInStats",
    "w:doNotAutoCompressPictures", "w:forceUpgrade", "w:captions",
    "w:readModeInkLockDown", "w:smartTagType", "w:shapeDefaults",
    "w:doNotEmbedSmartTags", "w:decimalSymbol", "w:listSeparator",
)
MATH_DEFAULTS = (
    ("m:mathFont", "Cambria Math"), ("m:brkBin", "before"),
    ("m:brkBinSub", "--"), ("m:smallFrac", "0"), ("m:dispDef", None),
    ("m:lMargin", "0"), ("m:rMargin", "0"), ("m:defJc", "centerGroup"),
    ("m:wrapIndent", "0"), ("m:intLim", "subSup"), ("m:naryLim", "undOvr"),
)
CAPTION = re.compile(r"^(?:【[^【】\r\n]{1,80}】|\[[^\[\]\r\n]{1,80}\]|［[^［］\r\n]{1,80}］)$")
STATUS_ANNOTATION = re.compile(r"\s*(【待(?:核验|校验)(?:公式模型|模型|公式)?】)\s*$")


def _insert_before(parent, child, successors):
    for name in successors:
        following = parent.find(qn(name))
        if following is not None:
            parent.insert(parent.index(following), child)
            return
    parent.append(child)


def _setting(settings, tag):
    element = settings.find(qn(tag))
    if element is None:
        element = OxmlElement(tag)
        _insert_before(settings, element, SETTINGS_TAIL[SETTINGS_TAIL.index(tag) + 1:])
    return element


def set_modern_compatibility(document):
    """Target Word 2013+ without altering content or changing its namespaces."""
    settings = document.settings.element
    compatibility = _setting(settings, "w:compat")
    modes = [item for item in compatibility.findall(qn("w:compatSetting"))
             if item.get(qn("w:name")) == "compatibilityMode"]
    mode = modes[0] if modes else OxmlElement("w:compatSetting")
    if not modes:
        compatibility.append(mode)
    for extra in modes[1:]:
        compatibility.remove(extra)
    for name, value in (("name", "compatibilityMode"), ("uri", WORD_URI), ("val", "15")):
        mode.set(qn("w:" + name), value)


def _modern_settings(document):
    set_modern_compatibility(document)
    settings = document.settings.element
    # Fill omissions only; retain explicit font/break/margin choices in an output
    # using a custom reference. Word writes these document defaults itself.
    properties = _setting(settings, "m:mathPr")
    for index, (tag, value) in enumerate(MATH_DEFAULTS):
        if properties.find(qn(tag)) is not None:
            continue
        element = OxmlElement(tag)
        if value is not None:
            element.set(qn("m:val"), value)
        _insert_before(properties, element, [name for name, _ in MATH_DEFAULTS[index + 1:]])


def _text(nodes):
    return "".join(item.text or "" for node in nodes for item in node.iter(qn("w:t")))


def _substantive(nodes):
    return bool(_text(nodes).strip() or any(node.tag in {qn("m:oMath"), qn("m:oMathPara")} for node in nodes))


def _safe_children(paragraph):
    # Leave numbering, section breaks, bookmarks, fields, drawings, hyperlinks
    # and content controls to their author; moving them needs separate rules.
    if paragraph.xpath("./w:pPr/w:numPr | ./w:pPr/w:sectPr"):
        return False
    style = paragraph.xpath("./w:pPr/w:pStyle/@w:val")
    if style and (style[0] in {"Title", "Subtitle"} or re.fullmatch(r"Heading[1-9]", style[0])):
        return False
    for child in paragraph:
        if child.tag not in {qn("w:pPr"), qn("w:r"), qn("m:oMath"), qn("m:oMathPara")}:
            return False
        if child.tag == qn("w:r") and any(item.tag not in {qn("w:rPr"), qn("w:t")} for item in child):
            return False
    return True


def _display_inline(paragraph):
    equations = paragraph.findall(qn("m:oMath"))
    if len(equations) != 1 or paragraph.find(qn("m:oMathPara")) is not None:
        return False
    equation = equations[0]
    tall = {qn("m:f"), qn("m:rad"), qn("m:m"), qn("m:eqArr")}
    if not any(item.tag in tall for item in equation.iter()):
        return False
    before = list(paragraph)[:paragraph.index(equation)]
    after = list(paragraph)[paragraph.index(equation) + 1:]
    left, right = _text(before).strip(), _text(after).strip()
    if left and right:
        return False
    outside = left or right
    return not outside or bool(CAPTION.fullmatch(outside))


def _equation_paragraph(paragraph, document):
    formatted = Paragraph(paragraph, document._body).paragraph_format
    # Auto single spacing expands for tall math. Never impose an exact height.
    formatted.line_spacing_rule = WD_LINE_SPACING.SINGLE
    formatted.keep_together = True
    formatted.widow_control = True


def _extract_status_annotation(equation):
    """Move only a recognized trailing status label made of complete math runs.

    Do not cut a mixed math/text run, move a mathematical [x] label, or leave an
    expression ending with an operator. Fractions, delimiters and algebra runs
    are never rebuilt or simplified.
    """
    runs = []
    for child in reversed(list(equation)):
        if child.tag != qn("m:r") or len(child.findall(qn("m:t"))) != 1:
            break
        if any(item.tag not in {qn("m:rPr"), qn("w:rPr"), qn("m:t")} for item in child):
            break
        runs.insert(0, child)
    tail = "".join(run.find(qn("m:t")).text or "" for run in runs)
    match = STATUS_ANNOTATION.search(tail)
    if not match:
        return None
    text = "".join(item.text or "" for item in equation.iter(qn("m:t")))
    prefix = text[:-len(tail)] + tail[:match.start()]
    if not prefix.strip() or prefix.rstrip().endswith(("=", "+", "−", "-", "⋅", "×", "/", "≤", "≥", "<", ">")):
        return None
    offset = 0
    selected = None
    for index, run in enumerate(runs):
        if offset == match.start():
            selected = runs[index:]
            break
        offset += len(run.find(qn("m:t")).text or "")
    if selected is None:
        return None
    for run in selected:
        equation.remove(run)
    annotation = OxmlElement("w:r")
    value = OxmlElement("w:t")
    value.text = match[1]
    annotation.append(value)
    return annotation


def prepare_word_layout(document):
    """Return layout changes, without rewriting formula content or algebra."""
    _modern_settings(document)
    promoted = separated = display_paragraphs = annotations = 0
    # Keep table-cell math and inline math in ordinary prose untouched.
    for paragraph in list(document.element.body.findall(qn("w:p"))):
        if not _safe_children(paragraph):
            continue
        if _display_inline(paragraph):
            equation = paragraph.find(qn("m:oMath"))
            position = paragraph.index(equation)
            display = OxmlElement("m:oMathPara")
            properties = OxmlElement("m:oMathParaPr")
            justify = OxmlElement("m:jc")
            justify.set(qn("m:val"), "center")
            properties.append(justify)
            display.append(properties)
            display.append(equation)
            paragraph.insert(position, display)
            promoted += 1
        if paragraph.find(qn("m:oMathPara")) is None:
            continue
        for display in paragraph.findall(qn("m:oMathPara")):
            equations = display.findall(qn("m:oMath"))
            if len(equations) == 1:
                annotation = _extract_status_annotation(equations[0])
                if annotation is not None:
                    paragraph.insert(paragraph.index(display) + 1, annotation)
                    annotations += 1
        groups, text = [], []
        for child in list(paragraph):
            if child.tag == qn("w:pPr"):
                continue
            if child.tag == qn("m:oMathPara"):
                if _substantive(text):
                    groups.append(text)
                text = []
                groups.append([child])
            else:
                text.append(child)
        if _substantive(text):
            groups.append(text)
        properties = paragraph.find(qn("w:pPr"))
        original_properties = deepcopy(properties) if properties is not None else None
        for child in list(paragraph):
            if child.tag != qn("w:pPr"):
                paragraph.remove(child)
        previous = paragraph
        for index, group in enumerate(groups):
            current = paragraph if index == 0 else OxmlElement("w:p")
            if index:
                if original_properties is not None:
                    current.append(deepcopy(original_properties))
                previous.addnext(current)
            for child in group:
                current.append(child)
            if group[0].tag == qn("m:oMathPara"):
                _equation_paragraph(current, document)
                display_paragraphs += 1
                if index + 1 < len(groups) and groups[index + 1][0].tag != qn("m:oMathPara"):
                    Paragraph(current, document._body).paragraph_format.keep_with_next = True
            previous = current
        if len(groups) > 1:
            separated += 1
    return {"compatibility_mode": 15, "display_paragraphs": display_paragraphs,
            "inline_equations_promoted": promoted, "mixed_paragraphs_separated": separated,
            "status_annotations_moved": annotations}
