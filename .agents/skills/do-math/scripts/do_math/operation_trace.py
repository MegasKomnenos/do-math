"""Bounded operational telemetry; never a grant or a mathematical judgment."""
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from threading import Lock
import time
import uuid
import warnings
from functools import wraps
from inspect import signature

_sink = ContextVar('do_math_operation_trace', default=None)
_parent = ContextVar('do_math_operation_span', default=None)


class OperationTrace:
    def __init__(self, directory, *, operation_id=None):
        self.id = operation_id or uuid.uuid4().hex
        self.path = Path(directory) / (self.id + '.jsonl')
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = Lock()
        self.live = self.path.parent / 'live' / (self.id + '.json')
        self.live.parent.mkdir(parents=True, exist_ok=True)
        self.errors = 0
        self.active = {}
        self.parent_operation_id = os.environ.get('DO_MATH_PARENT_OPERATION_ID')

    def emit(self, row):
        # No raw requests, prompts, argv, credentials, or control capabilities.
        row = {'operation_id': self.id, 'parent_operation_id':self.parent_operation_id,
               'observed_at': datetime.now(timezone.utc).isoformat(), **row}
        raw = json.dumps(row, ensure_ascii=False, separators=(',', ':')) + '\n'
        try:
            with self.lock:
                with self.path.open('a', encoding='utf-8') as stream:
                    stream.write(raw)
                span = row.get('span_id')
                if row.get('event') in {'started','progress'}:
                    self.active[span] = {**self.active.get(span, {}), **row}
                elif span:
                    self.active.pop(span, None)
                temporary = self.live.with_suffix('.tmp')
                temporary.write_text(json.dumps({**row, 'active_spans':list(self.active.values())},
                    ensure_ascii=False), encoding='utf-8')
                os.replace(temporary, self.live)
        except OSError:
            self.errors += 1
            if self.errors == 1:
                warnings.warn('operation telemetry write failed; execution authority is unchanged', RuntimeWarning)


@contextmanager
def tracing(directory, *, operation_id=None):
    try:
        sink = OperationTrace(directory, operation_id=operation_id)
    except OSError:
        warnings.warn('operation telemetry unavailable', RuntimeWarning)
        yield None
        return
    token = _sink.set(sink)
    try:
        yield sink
    finally:
        _sink.reset(token)
        try:
            sink.live.unlink(missing_ok=True)
        except OSError:
            pass


@contextmanager
def phase(name, **binding):
    sink = _sink.get()
    span_id, parent, started = uuid.uuid4().hex, _parent.get(), time.perf_counter_ns()
    row = {'span_id': span_id, 'parent_span_id': parent, 'phase': name, **binding}
    if sink:
        sink.emit({**row, 'event': 'started'})
    token = _parent.set(span_id)
    outcome = 'completed'
    class Counters(dict):
        last = 0.
        def update(self, *args, **kwargs):
            super().update(*args, **kwargs)
            current = time.monotonic()
            if sink and current - self.last >= 1:
                sink.emit({**row, 'event':'progress', 'elapsed_ns':time.perf_counter_ns() - started, **self})
                self.last = current
    counters = Counters()
    try:
        yield counters
    except BaseException:
        outcome = 'interrupted'
        raise
    finally:
        _parent.reset(token)
        if sink:
            sink.emit({**row, 'event': outcome, 'elapsed_ns': time.perf_counter_ns() - started,
                       'trace_write_errors':sink.errors, **counters})


def measured(name):
    """Measure a boundary without copying/logging its potentially sensitive arguments."""
    def decorate(function):
        @wraps(function)
        def run(*args, **kwargs):
            with phase(name):
                return function(*args, **kwargs)
        return run
    return decorate


def engine_operation(name):
    def decorate(function):
        @wraps(function)
        def run(self, *args, **kwargs):
            with tracing(Path(self.instance['workspace']) / 'operations'):
                with phase(name, instance_id=self.instance['id']):
                    return function(self, *args, **kwargs)
        return run
    return decorate


def workspace_operation(name):
    def decorate(function):
        parameters = signature(function)
        @wraps(function)
        def run(*args, **kwargs):
            workspace = parameters.bind(*args, **kwargs).arguments['workspace']
            with tracing(Path(workspace) / 'operations'):
                with phase(name):
                    return function(*args, **kwargs)
        return run
    return decorate


def child_environment():
    """Only a trace correlation crosses the process boundary, never authority."""
    sink = _sink.get()
    return {**os.environ, **({'DO_MATH_PARENT_OPERATION_ID':sink.id} if sink else {})}


def progress(directory):
    rows = []
    for path in sorted((Path(directory) / 'live').glob('*.json'))[:16]:
        try:
            rows.append(json.loads(path.read_text(encoding='utf-8')))
        except (OSError, ValueError):
            rows.append({'event':'unreadable_progress','operation_id':path.stem})
    return {'source':'local_operation_sidecars','observed_at':datetime.now(timezone.utc).isoformat(),
            'rows':rows,'scope':'progress only; not process liveness or authoritative completion'}


def trace_rows(directory):
    import hashlib
    rows = []
    for path in sorted(Path(directory).glob('*.jsonl')):
        try:
            data = path.read_bytes()
        except OSError:
            rows.append({'event':'unreadable_trace','file':path.name})
            continue
        source = {'path':str(path), 'sha256':hashlib.sha256(data).hexdigest(),
                  'observed_at':datetime.now(timezone.utc).isoformat()}
        for raw in data.splitlines():
            try:
                value = json.loads(raw)
                if not isinstance(value, dict):
                    raise ValueError('trace must be an object')
                rows.append({**value, '_trace_source':source})
            except (ValueError, UnicodeError):
                # An interrupted append is unknown, not a fabricated end time.
                rows.append({'event': 'incomplete_trace', 'file': path.name})
    return rows


def phase_rows(directory):
    spans = {}
    for event in trace_rows(directory):
        if not all(isinstance(event.get(k), str) for k in ('span_id','operation_id','phase','event','observed_at')):
            continue
        key = (event['operation_id'], event['span_id'])
        row = spans.setdefault(key, {'unit':'operation_phase', 'id':key[0] + ':' + key[1],
            'operation_id':key[0], 'span_id':key[1], 'parent_span_id':event.get('parent_span_id'),
            'parent_operation_id':event.get('parent_operation_id'),
            'phase':event['phase'], 'created_at_utc':None, 'ended_at_utc':None, 'elapsed_ns':None})
        row['evidence_source'] = {'kind':'local_operation_file', **event['_trace_source']}
        if event['event'] == 'started': row['created_at_utc'] = event['observed_at']
        if event['event'] in {'completed','interrupted'}:
            row.update(ended_at_utc=event['observed_at'], elapsed_ns=event['elapsed_ns'], outcome=event['event'])
        for name in ('file_count','completed_files','read_bytes','peak_pending','trace_write_errors'):
            if name in event: row[name] = event[name]
    return list(spans.values())
