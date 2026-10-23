"""Portable cached builds and per-attempt records for controlled v2 trials."""
from contextlib import contextmanager, ExitStack
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import inspect
import json
import math
import os
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile
import time
import uuid

from version import __version__

CORE = Path(__file__).resolve().parent
SCHEMA = 1


class CachedBuildError(RuntimeError):
    def __init__(self, report):
        self.report = report
        super().__init__(f"Briefing {report['status']}; see {report['record_path']}")


def _hash_file(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest() if hasattr(hashlib, 'file_digest') else _stream_hash(stream)


def _stream_hash(stream):
    digest = hashlib.sha256()
    for block in iter(lambda: stream.read(1024 * 1024), b''):
        digest.update(block)
    return digest.hexdigest()


def _key(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()


def _save_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix='.briefing-json-', dir=path.parent)
    try:
        with os.fdopen(descriptor, 'w', encoding='utf-8') as out:
            json.dump(value, out, ensure_ascii=False, indent=2)
            out.write('\n')
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


@contextmanager
def _lock(path):
    """Keep lock files: unlinking a locked inode permits competing writers."""
    with Path(path).open('a+b') as handle:
        if os.name == 'nt':
            import msvcrt
            if handle.seek(0, 2) == 0:
                handle.write(b'0')
                handle.flush()
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            try:
                yield
            finally:
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            try:
                yield
            finally:
                fcntl.flock(handle, fcntl.LOCK_UN)


def valid_asset(path):
    path = Path(path)
    if not path.is_file() or not path.stat().st_size:
        return False
    try:
        if path.suffix.lower() == '.docx':
            from briefing_v2.engine import inspect_docx
            result = inspect_docx(path)
            return bool(result['text'].strip() or result['math'])
        if path.suffix.lower() == '.mp3':
            result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                                     'format=duration:stream=codec_type', '-of', 'json', str(path)],
                                    capture_output=True, text=True, timeout=20)
            data = json.loads(result.stdout)
            duration = float(data['format']['duration'])
            return result.returncode == 0 and math.isfinite(duration) and duration > 0 and any(
                stream.get('codec_type') == 'audio' for stream in data.get('streams', []))
    except (OSError, ValueError, KeyError, subprocess.SubprocessError):
        return False
    except Exception:
        # Invalid ZIP/XML and unsupported media must never become cache hits.
        return False
    return False


def _components(names):
    return {name: _hash_file(CORE / name) for name in sorted(names)}


def _packages(names):
    result = {}
    for name in names:
        try:
            result[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            result[name] = 'not-installed'
    return result


def _word_config(raw, title, topic, engine, pandoc_path, reference):
    names = ['render_docx.py', 'build_briefing.py', 'briefing_workflow.py', 'engineering_text.py']
    config = {'source_sha256': hashlib.sha256(raw.encode('utf-8')).hexdigest(),
              'title': title, 'topic': topic, 'engine': engine, 'core_version': __version__,
              'packages': _packages(['python-docx', 'lxml']), 'reference_sha256': None}
    if engine == 'pandoc':
        from briefing_v2.engine import find_pandoc
        executable = find_pandoc(pandoc_path)
        result = subprocess.run([executable, '--version'], capture_output=True, text=True, timeout=20, check=True)
        config['pandoc'] = {'version': result.stdout.splitlines()[0], 'sha256': _hash_file(executable)}
        names += [p.relative_to(CORE).as_posix() for p in (CORE / 'briefing_v2').glob('*.py')]
        if reference:
            config['reference_sha256'] = _hash_file(reference)
    else:
        names.append('omml_adapter.py')
        config['packages'].update(_packages(['latex2mathml']))
    config['components'] = _components(names)
    return config


def _audio_config(raw, rate, voice):
    if not shutil.which('ffprobe'):
        raise FileNotFoundError('ffprobe is required to validate MP3 assets')
    from clean_speech_text import clean_speech_text
    cleaned = clean_speech_text(raw)
    return {'cleaned_sha256': hashlib.sha256(cleaned.encode('utf-8')).hexdigest(), 'rate': rate,
            'voice': voice, 'packages': _packages(['edge-tts']),
            'components': _components(['clean_speech_text.py', 'unit_verbalizer.py', 'engineering_text.py'])}


def _diagnostic(code, message, source, severity='error'):
    return {'code': code, 'severity': severity, 'message': message, 'source': str(source)}


def _error_report(error, engine, source, output):
    if hasattr(error, 'report') and 'diagnostics' in error.report:
        result = deepcopy(error.report)
    else:
        code = 'DEPENDENCY_NOT_FOUND' if isinstance(error, FileNotFoundError) else 'BUILD_FAILED'
        result = {'engine': engine, 'status': 'failed', 'diagnostics': [_diagnostic(
            code, f'构建失败（{type(error).__name__}）；已有输出保留。', source)]}
    result.update(source=str(source), output=str(output))
    for item in result['diagnostics']:
        item['source'] = str(source)
    return result


def _invoke_word(worker, source, stage, title, topic, options):
    parameters = inspect.signature(worker).parameters
    accepts_kwargs = any(p.kind == p.VAR_KEYWORD for p in parameters.values())
    if options['engine'] == 'pandoc' and not ('engine' in parameters or accepts_kwargs):
        raise ValueError('The selected Word worker cannot select the Pandoc engine')
    worker(str(source), str(stage), title, topic, **{
        key: value for key, value in options.items() if key in parameters or accepts_kwargs})


def build_cached_briefing(source, docx=None, mp3=None, title=None, topic='Technology', rate='+0%',
                          proxy=None, workers=None, audio_optional=False, *, engine='pandoc',
                          pandoc_path=None, reference_doc=None, voice='zh-CN-XiaoxiaoNeural',
                          record_dir=None):
    """Build selected outputs; cache by content/configuration; record every valid attempt.

    No sending or archiving occurs here. Compatibility callers explicitly choose
    legacy. Unknown formulas never trigger an implicit switch of engines.
    """
    source = Path(source).resolve()
    targets = {kind: Path(path).resolve() for kind, path in [('docx', docx), ('mp3', mp3)] if path}
    if not targets or engine not in {'legacy', 'pandoc'}:
        raise ValueError('Select an output and a supported Word engine')
    if any(path.suffix.lower() != '.' + kind for kind, path in targets.items()):
        raise ValueError('Output extensions must be .docx and .mp3')
    if engine == 'legacy' and (pandoc_path or reference_doc):
        raise ValueError('Pandoc and reference options require engine=pandoc')
    if not docx and (pandoc_path or reference_doc):
        raise ValueError('Word options require a Word output')
    reference = Path(reference_doc).resolve() if reference_doc else None
    anchor = targets.get('docx') or targets['mp3']
    manifest = anchor.with_suffix('.assets.json')
    records = Path(record_dir).resolve() if record_dir else anchor.with_suffix('.briefing')
    reads = {source, *([reference] if reference else [])}
    locks = [p.with_name('.' + p.name + '.briefing.lock') for p in {manifest, *targets.values()}]
    writes = [*targets.values(), manifest, records, *locks]
    if len(set(writes)) != len(writes) or any(p in reads for p in writes):
        raise ValueError('Source, reference, outputs, manifest and record directory must differ')
    # A source/template inside the reserved journal directory could be replaced by a record.
    if any(p.is_relative_to(records) for p in [*reads, *targets.values(), manifest, *locks]):
        raise ValueError('Keep source, template and outputs outside the record directory')
    for target in targets.values():
        target.parent.mkdir(parents=True, exist_ok=True)
    records.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ-') + uuid.uuid4().hex[:8]
    record_path = records / (run_id + '.json')
    word_path = records / (run_id + '.word.json') if docx else None
    started = time.monotonic()
    record = {'schema_version': SCHEMA, 'run_id': run_id, 'core_version': __version__,
              'started_at': datetime.now(timezone.utc).isoformat(), 'status': 'running',
              'source': str(source), 'engine': engine if docx else None,
              'reference_doc': str(reference) if reference else None,
              'runtime': {'system': platform.system(), 'architecture': platform.machine(), 'python': platform.python_version()},
              'record_path': str(record_path), 'manifest_path': str(manifest),
              'word_diagnostics_path': str(word_path) if word_path else None,
              'outputs': {kind: {'path': str(path), 'status': 'not_started', 'cache': 'unavailable'}
                          for kind, path in targets.items()},
              'diagnostics': [], 'rebuilt': [], 'reused': [], 'ready_for_delivery': False}
    _save_json(record_path, record)
    state = {'schema_version': SCHEMA, 'assets': {}, 'ready_for_delivery': False}
    held = False
    stack = ExitStack()
    try:
        # Also lock each output: different manifests may target the same MP3.
        for path in sorted(locks, key=str):
            stack.enter_context(_lock(path))
        held = True
        if manifest.exists():
            try:
                prior = json.loads(manifest.read_text(encoding='utf-8'))
                if isinstance(prior, dict) and isinstance(prior.get('assets'), dict):
                    state['assets'] = prior['assets']
                else:
                    raise ValueError('Invalid cache metadata')
            except (ValueError, OSError):
                record['diagnostics'].append(_diagnostic('CACHE_METADATA_INVALID',
                    '缓存记录不可读；将重新验证并构建所需文件。', source, 'warning'))
        state.update(record)
        _save_json(manifest, state)
        raw = source.read_text(encoding='utf-8')
        if not raw.strip():
            raise ValueError('Empty source')
        record['source_sha256'] = hashlib.sha256(raw.encode('utf-8')).hexdigest()
        title = title or source.stem
        from build_briefing import build_docx_worker, build_audio_worker
        workers = workers or {'docx': build_docx_worker, 'mp3': build_audio_worker}
        configurations, keys, pending = {}, {}, []
        for kind, target in targets.items():
            try:
                config = (_word_config(raw, title, topic, engine, pandoc_path, reference) if kind == 'docx'
                          else _audio_config(raw, rate, voice))
                configurations[kind] = config
                keys[kind] = _key(config)
                old = state['assets'].get(kind, {})
                if not isinstance(old, dict):
                    old = {}
                hit = (old.get('key') == keys[kind] and old.get('path') == str(target)
                       and valid_asset(target) and old.get('sha256') == _hash_file(target))
                record['outputs'][kind] = {'path': str(target), 'cache': 'hit' if hit else 'miss',
                                           'status': 'reused' if hit else 'pending', 'configuration': config}
                if hit:
                    record['reused'].append(kind)
                    if kind == 'docx':
                        report = deepcopy(old.get('diagnostic_data', {}))
                        if not report or report.get('engine') != engine:
                            record['outputs'][kind].update(status='pending', cache='miss')
                            record['reused'].remove(kind)
                            pending.append(kind)
                            continue
                        report.update(source=str(source), output=str(target))
                        for item in report.get('diagnostics', []):
                            item['source'] = str(source)
                        _save_json(word_path, report)
                        record['diagnostics'].extend(report.get('diagnostics', []))
                else:
                    pending.append(kind)
            except Exception as error:
                report = _error_report(error, engine if kind == 'docx' else 'edge-tts', source, target)
                record['outputs'][kind] = {'path': str(target), 'status': 'failed', 'cache': 'unavailable'}
                record['diagnostics'].extend(report['diagnostics'])
                if kind == 'docx':
                    _save_json(word_path, report)
        with tempfile.TemporaryDirectory(prefix='.briefing-source-', dir=records) as frozen:
            frozen_source = Path(frozen) / 'source.md'
            frozen_source.write_text(raw, encoding='utf-8')
            frozen_reference = None
            if reference and 'docx' in configurations:
                frozen_reference = Path(frozen) / 'reference.docx'
                shutil.copy2(reference, frozen_reference)
                if _hash_file(frozen_reference) != configurations['docx']['reference_sha256']:
                    record['diagnostics'].append(_diagnostic('REFERENCE_CHANGED', '冻结模板时检测到内容变化；请重试。', reference))
                    raise ValueError('Reference changed while freezing')

            def run(kind):
                target = targets[kind]
                begin = time.monotonic()
                with tempfile.TemporaryDirectory(prefix='.briefing-build-', dir=target.parent) as staging:
                    stage = Path(staging) / target.name
                    if kind == 'docx':
                        _invoke_word(workers[kind], frozen_source, stage, title, topic,
                                     {'engine': engine, 'pandoc_path': pandoc_path,
                                      'reference_doc': frozen_reference, 'diagnostics_path': word_path if engine == 'pandoc' else None,
                                      'source_name': str(source)})
                        if engine == 'pandoc':
                            report = json.loads(word_path.read_text(encoding='utf-8'))
                        else:
                            report = {'engine': 'legacy', 'status': 'success', 'diagnostics': [],
                                      'source_sha256': record['source_sha256']}
                        report.update(source=str(source), output=str(target))
                        for item in report['diagnostics']:
                            item['source'] = str(source)
                        _save_json(word_path, report)
                    else:
                        parameters = inspect.signature(workers[kind]).parameters
                        if 'voice' in parameters:
                            workers[kind](str(frozen_source), str(stage), rate, voice, proxy)
                        else:
                            if voice != 'zh-CN-XiaoxiaoNeural':
                                raise ValueError('This worker cannot select a voice')
                            workers[kind](str(frozen_source), str(stage), rate, proxy)
                        report = None
                    if not valid_asset(stage):
                        raise ValueError('Generated asset did not pass validation')
                    entry = {'key': keys[kind], 'path': str(target), 'sha256': _hash_file(stage)}
                    if report is not None:
                        entry['diagnostic_data'] = report
                    os.replace(stage, target)
                return entry, time.monotonic() - begin

            with ThreadPoolExecutor(max_workers=2) as pool:
                futures = {pool.submit(run, kind): kind for kind in pending}
                for future in as_completed(futures):
                    kind = futures[future]
                    try:
                        entry, cost = future.result()
                        state['assets'][kind] = entry
                        record['outputs'][kind].update(status='built', duration_seconds=round(cost, 3))
                        record['rebuilt'].append(kind)
                        if kind == 'docx':
                            record['diagnostics'].extend(entry['diagnostic_data']['diagnostics'])
                    except Exception as error:
                        report = _error_report(error, engine if kind == 'docx' else 'edge-tts', source, targets[kind])
                        record['outputs'][kind]['status'] = 'failed'
                        record['diagnostics'].extend(report['diagnostics'])
                        if kind == 'docx':
                            _save_json(word_path, report)
                    state.update(record)
                    _save_json(manifest, state)
        if source.read_text(encoding='utf-8') != raw:
            record['diagnostics'].append(_diagnostic('SOURCE_CHANGED', '构建期间源稿发生变化；本次结果不可交付。', source))
        if reference and 'docx' in configurations and _hash_file(reference) != configurations['docx']['reference_sha256']:
            record['diagnostics'].append(_diagnostic('REFERENCE_CHANGED', '构建期间模板发生变化；本次结果不可交付。', reference))
        failed = [kind for kind, output in record['outputs'].items() if output['status'] == 'failed']
        errors = [item for item in record['diagnostics'] if item['severity'] == 'error']
        optional_failure = (audio_optional and failed == ['mp3'] and 'docx' in targets
                            and all(item['source'] == str(source) for item in errors)
                            and not any(item['code'] in {'SOURCE_CHANGED', 'REFERENCE_CHANGED'} for item in errors))
        record['ready_for_delivery'] = not failed and not errors or optional_failure
        record['review_required'] = any(item['severity'] == 'warning' for item in record['diagnostics'])
        record['status'] = ('word_only' if optional_failure else
                            'failed' if errors or failed else
                            'success_with_warnings' if record['review_required'] else 'success')
        if optional_failure:
            record.update(delivery_mode='word_only', audio_error='AudioBuildFailed')
            state['assets'].pop('mp3', None)
        record['rebuilt'].sort()
        record['reused'].sort()
        record['title'], record['topic'], record['rate'] = title, topic, rate
        record['stage_seconds'] = {kind: output['duration_seconds'] for kind, output in record['outputs'].items()
                                   if 'duration_seconds' in output}
    except BaseException as error:
        code = 'OUTPUT_BUSY' if not held and isinstance(error, OSError) else 'WORKFLOW_FAILED'
        record['diagnostics'].append(_diagnostic(code, f'流程中止（{type(error).__name__}）；请查看本次记录。', source))
        record['status'] = 'failed'
        record['ready_for_delivery'] = False
        if word_path and not word_path.exists():
            try:
                _save_json(word_path, {'engine': engine, 'status': 'failed', 'source': str(source),
                                      'output': str(targets['docx']), 'diagnostics': record['diagnostics']})
            except OSError:
                record['diagnostics'].append(_diagnostic('DIAGNOSTICS_WRITE_FAILED', 'Word 诊断文件未能写入。', source))
    try:
        record['finished_at'] = datetime.now(timezone.utc).isoformat()
        record['duration_seconds'] = round(time.monotonic() - started, 3)
        _save_json(record_path, record)
        if held:
            state.update(record)
            _save_json(manifest, state)
    finally:
        stack.close()
    if not record['ready_for_delivery']:
        raise CachedBuildError(record)
    # Compatibility adapters need the cache snapshot from this locked attempt,
    # rather than a later read of a manifest another process may have updated.
    return {**record, 'assets': deepcopy(state['assets'])}
