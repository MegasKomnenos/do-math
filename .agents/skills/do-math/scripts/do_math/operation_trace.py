"""Bounded operational telemetry; never a grant or a mathematical judgment."""
from contextlib import contextmanager
from contextvars import ContextVar
import json
import os
from pathlib import Path
from threading import Lock, Timer
import time
import uuid
import warnings
from functools import wraps
from inspect import signature
from .file_io import atomic_replace, read_bytes_shared
from .system_clock import now

_sink = ContextVar('do_math_operation_trace', default=None)
# The live progress snapshot lags the trace by at most this many seconds.
LIVE_INTERVAL = 1.0
_parent = ContextVar('do_math_operation_span', default=None)


class OperationTrace:
    """One operation's append-only trace and its throttled live progress snapshot.

    Every row is appended at once. The live snapshot (active spans, read by
    ``progress``) is rewritten at most once per ``LIVE_INTERVAL``; a later row
    inside the interval is written by one pending timer, so the snapshot is
    never more than ``LIVE_INTERVAL`` behind. ``close`` flushes and stops both;
    a row that still arrives afterwards is appended but never rewrites the snapshot.
    """
    def __init__(self, directory):
        self.id = uuid.uuid4().hex
        self.path = Path(directory) / (self.id + '.jsonl')
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = Lock()
        self.live = self.path.parent / 'live' / (self.id + '.json')
        self.live.parent.mkdir(parents=True, exist_ok=True)
        self.errors = 0
        self.failure = None
        self.active = {}
        self.parent_operation_id = os.environ.get('DO_MATH_PARENT_OPERATION_ID')
        self.stream = None
        self.pending = None
        self.live_written = float('-inf')
        self.timer = None
        self.closed = False

    def emit(self, row):
        # No raw requests, prompts, argv, credentials, or control capabilities.
        row = {'operation_id': self.id, 'parent_operation_id':self.parent_operation_id,
               'observed_at': now(), **row}
        raw = json.dumps(row, ensure_ascii=False, separators=(',', ':')) + '\n'
        with self.lock:
            if self.closed:
                try:
                    with self.path.open('a', encoding='utf-8') as stream:
                        stream.write(raw)
                except OSError as error:
                    self._failed('append_trace', error)
                return
            try:
                if self.stream is None:
                    self.stream = self.path.open('a', encoding='utf-8')
                self.stream.write(raw)
                self.stream.flush()
            except OSError as error:
                self._close_stream()
                self._failed('append_trace', error)
            span = row.get('span_id')
            if row.get('event') in {'started','progress'}:
                self.active[span] = {**self.active.get(span, {}), **row}
            elif span:
                self.active.pop(span, None)
            self.pending = {**row, 'active_spans':list(self.active.values())}
            wait = self.live_written + LIVE_INTERVAL - time.monotonic()
            if wait <= 0:
                self._write_live()
            elif self.timer is None:
                self.timer = Timer(wait, self._write_pending)
                self.timer.daemon = True
                self.timer.start()

    def close(self):
        with self.lock:
            self.closed, self.pending = True, None
            if self.timer is not None:
                self.timer.cancel()
                self.timer = None
            self._close_stream()

    def _write_pending(self):
        with self.lock:
            self.timer = None
            # A timer that fired while close() held the lock finds nothing to write.
            if not self.closed and self.pending is not None:
                self._write_live()

    def _write_live(self):
        snapshot, self.pending = self.pending, None
        self.live_written = time.monotonic()
        temporary = self.live.with_suffix('.tmp')
        operation = 'write_live'
        try:
            temporary.write_text(json.dumps(snapshot, ensure_ascii=False), encoding='utf-8')
            operation = 'replace_live'
            atomic_replace(temporary, self.live)
        except OSError as error:
            self._failed(operation, error)

    def _close_stream(self):
        stream, self.stream = self.stream, None
        if stream is not None:
            try:
                stream.close()
            except OSError:
                pass

    def _failed(self, operation, error):
        self.errors += 1
        observed = now()
        self.failure = {'operation_id':self.id,'operation':operation,
            'exception_type':type(error).__name__,'errno':error.errno,
            'winerror':getattr(error,'winerror',None),'count':self.errors,
            'first_at':self.failure['first_at'] if self.failure else observed,'last_at':observed,
            'relative_path':self.path.name if operation=='append_trace' else 'live/'+self.live.name}
        # A separate bounded record survives failure of the live replace.
        # No exception message, raw argv or request is copied into telemetry.
        try:
            directory=self.path.parent/'errors'
            directory.mkdir(exist_ok=True)
            target=directory/(self.id+'.json')
            # Diagnostics must also survive failure of rename itself. A
            # partial diagnostic is reported unreadable, never as authority.
            target.write_text(json.dumps(self.failure,ensure_ascii=False),encoding='utf-8')
        except OSError:
            pass
        if self.errors == 1:
            warnings.warn(f'operation telemetry {operation} failed ({type(error).__name__}, '
                f'errno={error.errno}, winerror={getattr(error,"winerror",None)}); '
                'execution authority is unchanged', RuntimeWarning)


@contextmanager
def tracing(directory):
    try:
        sink = OperationTrace(directory)
    except OSError:
        warnings.warn('operation telemetry unavailable', RuntimeWarning)
        yield None
        return
    token = _sink.set(sink)
    try:
        yield sink
    finally:
        _sink.reset(token)
        sink.close()
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
