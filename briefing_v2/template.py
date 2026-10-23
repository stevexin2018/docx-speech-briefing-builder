"""Word styles and minimal table enhancements, separate from content conversion."""
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor


def configure_reference(path):
    document = Document(path)
    for section in document.sections:
        section.page_width, section.page_height = Cm(21), Cm(29.7)
        section.top_margin = section.bottom_margin = Cm(2)
        section.left_margin = section.right_margin = Cm(2)
    for name in ("Normal", "Body Text", "First Paragraph", "Compact", "Block Text"):
        style = document.styles[name]
        style.font.name = "Times New Roman"
        style.font.size = Pt(10.5)
        style.element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), "宋体")
        style.paragraph_format.line_spacing = 1.2
        style.paragraph_format.space_after = Pt(5)
    for name in ["Title", *[f"Heading {level}" for level in range(1, 10)]]:
        style = document.styles[name]
        style.font.name = "Arial"
        style.font.color.rgb = RGBColor(0, 0, 0)
        style.font.size = Pt(18 if name == "Title" else {"Heading 1": 16, "Heading 2": 13}.get(name, 11))
        style.element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), "黑体")
        style.paragraph_format.keep_with_next = True
    document.save(path)


def enhance_document(path, title=None, topic_id=None, default_template=True, add_title=False):
    document = Document(path)
    if title:
        document.core_properties.title = title
    if topic_id:
        document.core_properties.identifier = topic_id
    if add_title:
        paragraph = document.add_paragraph(title, style="Title")
        document.element.body.remove(paragraph._p)
        document.element.body.insert(0, paragraph._p)
    for table in document.tables:
        if not table.rows:
            continue
        properties = table.rows[0]._tr.get_or_add_trPr()
        if properties.find(qn("w:tblHeader")) is None:
            properties.append(OxmlElement("w:tblHeader"))
        if default_template:
            borders = OxmlElement("w:tblBorders")
            for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
                edge = OxmlElement(f"w:{side}")
                for key, value in (("val", "single"), ("sz", "4"), ("color", "D9D9D9")):
                    edge.set(qn(f"w:{key}"), value)
                borders.append(edge)
            table._tbl.tblPr.append(borders)
    document.save(path)
