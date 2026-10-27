"""Explicit Word file compatibility; does not alter equations or paragraphs."""
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

WORD_URI = 'http://schemas.microsoft.com/office/word'


def use_modern_word_mode(document):
    """Select Word 2013+ mode while preserving other compatibility settings."""
    settings = document.settings.element
    compatibility = settings.find(qn('w:compat'))
    if compatibility is None:
        compatibility = OxmlElement('w:compat')
        settings.insert_element_before(
            compatibility, 'w:docVars', 'w:rsids', 'm:mathPr', 'w:attachedSchema',
            'w:themeFontLang', 'w:clrSchemeMapping', 'w:doNotIncludeSubdocsInStats',
            'w:doNotAutoCompressPictures', 'w:forceUpgrade', 'w:captions',
            'w:readModeInkLockDown', 'w:smartTagType', 'w:shapeDefaults',
            'w:doNotEmbedSmartTags', 'w:decimalSymbol', 'w:listSeparator')
    modes = [item for item in compatibility.findall(qn('w:compatSetting'))
             if item.get(qn('w:name')) == 'compatibilityMode']
    mode = modes[0] if modes else OxmlElement('w:compatSetting')
    if not modes:
        compatibility.append(mode)
    for extra in modes[1:]:
        compatibility.remove(extra)
    for name, value in [('name', 'compatibilityMode'), ('uri', WORD_URI), ('val', '15')]:
        mode.set(qn('w:' + name), value)
    return {'compatibility_mode': 15}
