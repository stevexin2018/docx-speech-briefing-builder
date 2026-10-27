"""Pandoc AST -> verified native DOCX, with staged output and explicit diagnostics."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from zipfile import BadZipFile, ZipFile

from lxml import etree

from .diagnostics import Diagnostic, SourceLocator
from .normalization import normalize_ast
from .source_protection import prepare_source
from .template import configure_reference, enhance_document

MARKDOWN_FORMAT = "markdown+tex_math_dollars+tex_math_single_backslash-smart"
MINIMUM_PANDOC = (3, 12, 1)
RUNTIME_PANDOC = Path(__file__).resolve().parents[1] / ".runtime" / "pandoc" / (
    "pandoc.exe" if os.name == "nt" else "pandoc")
NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
      "m": "http://schemas.openxmlformats.org/officeDocument/2006/math"}


class BuildError(RuntimeError):
    def __init__(self, report):
        self.report = report
        self.diagnostics = report["diagnostics"]
        message = next((item["message"] for item in self.diagnostics if item["severity"] == "error"), "Word 构建失败。")
        super().__init__(message)


class _Abort(Exception):
    pass


def find_pandoc(explicit=None):
    candidate = explicit or os.environ.get("PANDOC_PATH") or (
        str(RUNTIME_PANDOC) if RUNTIME_PANDOC.is_file() else shutil.which("pandoc"))
    if candidate:
        resolved = shutil.which(str(candidate)) or (str(Path(candidate).resolve()) if Path(candidate).is_file() else None)
        if resolved:
            return resolved
    raise FileNotFoundError("未找到 Pandoc 3.12.1 或更新版本；请设置 --pandoc 或 PANDOC_PATH，或安装至 .runtime/pandoc 或 PATH。")


def _execute(pandoc, arguments, data=None, cwd=None):
    return subprocess.run([pandoc, *map(str, arguments)], input=data, capture_output=True,
                          cwd=cwd, timeout=120, check=False)


def _document_text(root):
    pieces = []
    def visit(element):
        local = etree.QName(element).localname
        namespace = etree.QName(element).namespace
        if namespace == NS["w"] and local == "t":
            pieces.append(element.text or "")
        elif namespace == NS["w"] and local in {"br", "cr"}:
            pieces.append("\n")
        elif namespace == NS["w"] and local == "tab":
            pieces.append("\t")
        for child in element:
            visit(child)
        if namespace == NS["w"] and local == "p":
            pieces.append("\n")
    visit(root)
    return "".join(pieces)


def inspect_docx(path):
    with ZipFile(path) as archive:
        if archive.testzip():
            raise ValueError("DOCX 压缩包完整性校验失败。")
        parsed = {}
        for name in archive.namelist():
            if name.endswith((".xml", ".rels")):
                parsed[name] = etree.fromstring(archive.read(name))
        main = parsed["word/document.xml"]
        style_root = parsed["word/styles.xml"]
        heading_styles = set()
        for style in style_root.xpath('//w:style[@w:type="paragraph"]', namespaces=NS):
            levels = style.xpath('w:pPr/w:outlineLvl/@w:val', namespaces=NS)
            if levels and int(levels[0]) < 9:
                heading_styles.add(style.get("{" + NS["w"] + "}styleId"))
        # Template headers/footers may contain their own equations and are not source body content.
        text_parts = [root for name, root in parsed.items() if re.fullmatch(
            r"word/(?:document|footnotes|endnotes)\.xml", name)]
        return {
            "math": sum(len(root.xpath('//m:oMath', namespaces=NS)) for root in text_parts),
            "headings": sum(style in heading_styles for style in main.xpath('//w:pPr/w:pStyle/@w:val', namespaces=NS)),
            "table_math": len(main.xpath('//w:tbl//m:oMath', namespaces=NS)),
            "repeat_headers": len(main.xpath('//w:tblHeader', namespaces=NS)),
            "text": "\n".join(_document_text(root) for root in text_parts),
        }


def _write_report(path, report):
    target = Path(path).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, staged = tempfile.mkstemp(prefix=".briefing-diagnostics-", suffix=".json", dir=target.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(report, stream, ensure_ascii=False, indent=2)
        os.replace(staged, target)
    finally:
        if os.path.exists(staged):
            os.unlink(staged)


def render_markdown(markdown_content, output_path, *, title=None, topic_id=None,
                    pandoc_path=None, reference_doc=None, diagnostics_path=None,
                    source_name="<markdown>"):
    """Return a structured report; raise BuildError without publishing a failed DOCX.

    Only an explicitly supplied diagnostics_path creates a JSON sidecar. Code,
    paths and math are typed separately before engineering text normalization.
    """
    target = Path(output_path).resolve()
    locator = SourceLocator(markdown_content, str(source_name))
    diagnostics = []
    report = {"engine": "pandoc", "status": "failed", "source": str(source_name),
              "source_sha256": hashlib.sha256(markdown_content.encode("utf-8")).hexdigest(),
              "output": str(target), "diagnostics": []}

    def add(code, message, severity="error", literal=None, node=None):
        diagnostics.append(locator.diagnostic(code, severity, message, literal, node))

    def refresh():
        report["diagnostics"] = [item.to_dict() for item in diagnostics]

    try:
        if target.suffix.lower() != ".docx":
            add("INVALID_OUTPUT", "新 Word 引擎的输出扩展名必须是 .docx。")
            raise _Abort()
        source_path = Path(source_name).resolve() if source_name != "<markdown>" else None
        if source_path == target:
            add("OUTPUT_ALIASES_SOURCE", "输出路径不能覆盖原始输入文件。")
            raise _Abort()
        reference_path = Path(reference_doc).resolve() if reference_doc else None
        if diagnostics_path and Path(diagnostics_path).resolve() in {target, source_path, reference_path}:
            add("INVALID_DIAGNOSTICS_PATH", "诊断路径必须与输入、参考模板和 Word 输出路径不同。")
            # Never overwrite a source or DOCX with the diagnostic report.
            diagnostics_path = None
            raise _Abort()
        if reference_doc and Path(reference_doc).resolve() == target:
            add("OUTPUT_ALIASES_REFERENCE", "输出路径不能覆盖参考模板。")
            raise _Abort()
        pandoc = find_pandoc(pandoc_path)
        version_result = _execute(pandoc, ["--version"])
        version_line = version_result.stdout.decode("utf-8", "replace").splitlines()
        match = re.match(r"pandoc(?:\.exe)? (\d+)\.(\d+)(?:\.(\d+))?", version_line[0] if version_line else "")
        if version_result.returncode or not match:
            add("INVALID_PANDOC", "无法确认 Pandoc 可执行文件的版本。")
            raise _Abort()
        version = tuple(int(part or 0) for part in match.groups())
        report["pandoc_version"] = ".".join(map(str, version))
        if version < MINIMUM_PANDOC:
            add("PANDOC_TOO_OLD", "此引擎要求 Pandoc 3.12.1 或更新版本。")
            raise _Abort()
        target.parent.mkdir(parents=True, exist_ok=True)
        cwd = source_path.parent if source_path and source_path.is_file() else None
        with tempfile.TemporaryDirectory(prefix=".briefing-v2-", dir=target.parent) as directory:
            workspace = Path(directory)
            prepared_source, source_diagnostics, protected_paths = prepare_source(markdown_content, str(source_name))
            diagnostics.extend(source_diagnostics)
            if any(item.severity == "error" for item in diagnostics):
                raise _Abort()
            parse_log = workspace / "parse-log.json"
            parsed = _execute(pandoc, ["-f", MARKDOWN_FORMAT, "-t", "json", "--log", parse_log],
                              prepared_source.lstrip("\ufeff").encode("utf-8"), cwd)
            if parsed.returncode:
                add("MARKDOWN_PARSE_FAILED", parsed.stderr.decode("utf-8", "replace").strip() or "Markdown 解析失败。")
                raise _Abort()
            ast, analysis, normalization_diagnostics = normalize_ast(json.loads(parsed.stdout), markdown_content, str(source_name))
            diagnostics.extend(normalization_diagnostics)
            report["source_counts"] = analysis["source_counts"]
            report["normalizations"] = analysis["normalizations"] + protected_paths
            report["protected_bare_paths"] = protected_paths
            if any(item.severity == "error" for item in diagnostics):
                raise _Abort()
            reference = Path(reference_doc).resolve() if reference_doc else workspace / "reference.docx"
            if reference_doc and not reference.is_file():
                add("REFERENCE_NOT_FOUND", "指定的 Word 参考模板不存在。")
                raise _Abort()
            if not reference_doc:
                template_result = _execute(pandoc, ["--print-default-data-file", "reference.docx"])
                if template_result.returncode:
                    add("TEMPLATE_FAILED", template_result.stderr.decode("utf-8", "replace"))
                    raise _Abort()
                reference.write_bytes(template_result.stdout)
                configure_reference(reference)
            staged = workspace / "document.docx"
            conversion_log = workspace / "conversion-log.json"
            converted = _execute(pandoc, ["-f", "json", "-t", "docx", "--standalone", "--fail-if-warnings",
                                          "--log", conversion_log, "--reference-doc", reference, "-o", staged],
                                 json.dumps(ast, ensure_ascii=False).encode("utf-8"), cwd)
            for log in (parse_log, conversion_log):
                if not log.exists():
                    continue
                for event in json.loads(log.read_text(encoding="utf-8")):
                    if event.get("verbosity") not in {"WARNING", "ERROR"}:
                        continue
                    formula = event.get("contents")
                    if not isinstance(formula, str):
                        formula = None
                    matches = [item for item in analysis["formulas"] if item["text"] == formula]
                    add("MATH_CONVERSION_FAILED" if event.get("type") == "CouldNotConvertTeXMath" else "PANDOC_WARNING",
                        event.get("pretty") or event.get("message") or str(event), literal=formula,
                        node=matches[0]["node"] if len(matches) == 1 else None)
            if converted.returncode or any(item.severity == "error" for item in diagnostics):
                if not any(item.severity == "error" for item in diagnostics):
                    add("DOCX_CONVERSION_FAILED", converted.stderr.decode("utf-8", "replace").strip() or "Word 转换失败。")
                raise _Abort()
            has_title = any(block.get("t") == "Header" and block["c"][0] == 1 for block in ast["blocks"])
            report["word_layout"] = enhance_document(staged, title, topic_id, default_template=not reference_doc,
                                                     add_title=bool(title and not has_title))
            metrics = inspect_docx(staged)
            expected_math = analysis["source_counts"].get("Math", 0)
            if metrics["math"] != expected_math:
                add("MATH_COUNT_MISMATCH", f"识别出 {expected_math} 处公式，实际生成 {metrics['math']} 个原生公式对象，已停止交付。")
            expected_headings = analysis["source_counts"].get("Header", 0)
            if metrics["headings"] != expected_headings:
                add("HEADING_COUNT_MISMATCH", "Word 标题结构与源文档不一致，已停止交付。")
            for item in analysis["protected"]:
                if item["text"] not in metrics["text"]:
                    add("PROTECTED_CONTENT_CHANGED", "代码或路径内容未完整保留，已停止交付。", literal=item["text"], node=item["node"])
            if any(item.severity == "error" for item in diagnostics):
                raise _Abort()
            metrics.pop("text")
            report["output_counts"] = metrics
            report["protected_items"] = len(analysis["protected"])
            report["status"] = "success_with_warnings" if any(item.severity == "warning" for item in diagnostics) else "success"
            refresh()
            if diagnostics_path:
                _write_report(diagnostics_path, report)
            os.replace(staged, target)
            return report
    except _Abort:
        pass
    except FileNotFoundError as error:
        add("DEPENDENCY_NOT_FOUND", str(error))
    except subprocess.TimeoutExpired:
        add("PANDOC_TIMEOUT", "Pandoc 在 120 秒内未完成，已停止交付。")
    except (OSError, ValueError, KeyError, BadZipFile, etree.XMLSyntaxError) as error:
        add("BUILD_FAILED", str(error))
    report["status"] = "failed"
    refresh()
    if diagnostics_path:
        try:
            _write_report(diagnostics_path, report)
        except OSError as error:
            diagnostics.append(Diagnostic("DIAGNOSTICS_WRITE_FAILED", "error", str(error), str(source_name)))
            refresh()
    raise BuildError(report)
