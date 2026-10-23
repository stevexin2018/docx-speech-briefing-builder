"""Serializable diagnostics with conservative source locations."""
from dataclasses import asdict, dataclass
import re
import sys


@dataclass
class Diagnostic:
    code: str
    severity: str
    message: str
    source: str = "<markdown>"
    line: int = None
    column: int = None
    node: str = None
    excerpt: str = None

    def to_dict(self):
        return {key: value for key, value in asdict(self).items() if value is not None}


class SourceLocator:
    """Return a line only when a literal has one unambiguous source occurrence."""
    def __init__(self, source, name):
        self.source = source
        self.name = name

    def diagnostic(self, code, severity, message, literal=None, node=None):
        line = column = None
        if literal:
            matches = list(re.finditer(re.escape(literal), self.source))
            if len(matches) == 1:
                offset = matches[0].start()
                line = self.source.count("\n", 0, offset) + 1
                column = offset - self.source.rfind("\n", 0, offset)
        return Diagnostic(code, severity, message, self.name, line, column, node,
                          literal[:240] if literal else None)


def print_diagnostics(diagnostics, severities=("warning",), stream=None):
    """Summarize repeated notices; the JSON report retains every source occurrence."""
    groups = {}
    for item in diagnostics:
        if item["severity"] in severities:
            key = (item["code"], item["message"])
            groups.setdefault(key, []).append(item)
    for (code, message), items in groups.items():
        item = items[0]
        location = f"{item['source']}:{item['line']}" if item.get("line") else item["source"]
        occurrences = f"（{len(items)} 处）" if len(items) > 1 else ""
        print(f"{location}: [{code}] {message}{occurrences}", file=stream or sys.stderr)
