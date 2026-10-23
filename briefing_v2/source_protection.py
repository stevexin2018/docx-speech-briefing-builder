"""Protect confident Windows path literals before Markdown interprets backslashes.

This lexical pass skips code and complete math regions. Pandoc remains responsible
for document parsing. Unquoted paths with spaces should be written as inline code.
"""
import re

from .diagnostics import SourceLocator

PATH_PREFIX = r"(?:(?:HKLM|HKCU|HKCR|HKU|HKEY_[A-Z_]+):[\\/]|[A-Za-z]:[\\/]|\\\\[A-Za-z0-9_.-]+[\\/])"
BARE_PATH = re.compile(PATH_PREFIX + r"[^\s，。！？；：、<>\"'`|\[\]{}()$]*")
FENCE = re.compile(r"[ \t]*(?:>[ \t]*)*(`{3,}|~{3,})[^\n]*(?:\n|$)")


def _literal_code(text):
    marker = "`" * (max((len(match[0]) for match in re.finditer(r"`+", text)), default=0) + 1)
    padding = " " if text.endswith("`") else ""
    return marker + padding + text + padding + marker


def prepare_source(source, source_name):
    locator = SourceLocator(source, source_name)
    source = source.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    pieces, diagnostics = [], []
    index, protected_count = 0, 0

    def escaped(position):
        start = position
        while start and source[start - 1] == "\\":
            start -= 1
        return (position - start) % 2 == 1

    while index < len(source):
        if index == 0 and source.startswith("---\n"):
            end = re.search(r"(?m)^(?:---|\.\.\.)[ \t]*(?:\n|$)", source[4:])
            if end:
                finish = 4 + end.end()
                pieces.append(source[index:finish])
                index = finish
                continue
        if index == 0 or source[index - 1] == "\n":
            opening = FENCE.match(source, index)
            if opening:
                marker = opening[1]
                close = re.search(r"(?m)^[ \t]*(?:>[ \t]*)*" + re.escape(marker[0])
                                  + "{" + str(len(marker)) + r",}[ \t]*(?:\n|$)", source[opening.end():])
                finish = opening.end() + close.end() if close else len(source)
                pieces.append(source[index:finish])
                index = finish
                continue
            if re.match(r"(?: {4}| {0,3}\t)", source[index:]):
                finish = source.find("\n", index)
                finish = finish + 1 if finish >= 0 else len(source)
                pieces.append(source[index:finish])
                index = finish
                continue
        if source[index] == "`":
            opening = re.match(r"`+", source[index:])[0]
            close = re.search(r"(?<!`)" + re.escape(opening) + r"(?!`)", source[index + len(opening):])
            if close:
                finish = index + len(opening) + close.end()
                pieces.append(source[index:finish])
                index = finish
                continue
        opener = next((token for token in ("\\[", "\\(", "$$", "$")
                       if source.startswith(token, index) and not escaped(index)), None)
        if opener:
            closer = {"\\[": "\\]", "\\(": "\\)", "$$": "$$", "$": "$"}[opener]
            end = source.find(closer, index + len(opener))
            while end >= 0 and (escaped(end) or (opener == "$" and
                   (source[index + 1].isspace() or source[end - 1].isspace()
                    or (end + 1 < len(source) and source[end + 1].isdigit())))):
                end = source.find(closer, end + len(closer))
            if end >= 0:
                finish = end + len(closer)
                pieces.append(source[index:finish])
                index = finish
                continue
            if opener != "$":
                diagnostics.append(locator.diagnostic("UNCLOSED_MATH", "error", "公式定界符未闭合，请补全后重试。", source[index:]))
        # Quoted Windows paths may contain spaces. Keep surrounding quotes intact.
        if source[index] in "\"'" and re.match(PATH_PREFIX, source[index + 1:]):
            finish = source.find(source[index], index + 1)
            if finish >= 0 and "\n" not in source[index:finish]:
                literal = source[index + 1:finish]
                pieces.append(source[index] + _literal_code(literal) + source[index])
                diagnostics.append(locator.diagnostic("PATH_PROTECTED", "info", "Windows 路径已按字面内容保护。", literal))
                protected_count += 1
                index = finish + 1
                continue
        previous = source[index - 1] if index else ""
        path = BARE_PATH.match(source, index) if not previous or not re.match(r"[\w/\\]", previous) else None
        token_start = max(source.rfind(" ", 0, index), source.rfind("\n", 0, index), source.rfind("\t", 0, index)) + 1
        in_link = source[:index].rstrip().endswith("](") or "://" in source[token_start:index]
        if path and not in_link:
            literal = path[0]
            pieces.append(_literal_code(literal))
            diagnostics.append(locator.diagnostic("PATH_PROTECTED", "info", "Windows 路径已按字面内容保护。", literal))
            protected_count += 1
            index = path.end()
            continue
        pieces.append(source[index])
        index += 1
    return "".join(pieces), diagnostics, protected_count
