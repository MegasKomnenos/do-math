"""Readers of the local operation telemetry that ``operation_trace`` writes (layer 2).

Status and reports read progress sidecars, error records and span traces; an
unreadable or interrupted file is reported as such, never as a completed span.
"""
import hashlib
import json
from pathlib import Path

from .file_io import read_bytes_shared
from .migration_defaults import clock_or_system


def progress(directory, *, clock=None):
    rows = []
    for path in sorted((Path(directory) / 'live').glob('*.json'))[:16]:
        try:
            rows.append(json.loads(read_bytes_shared(path).decode('utf-8')))
        except (OSError, ValueError):
            rows.append({'event':'unreadable_progress','operation_id':path.stem})
    failures=[]
    for path in sorted((Path(directory)/'errors').glob('*.json'))[-16:]:
        try:failures.append(json.loads(read_bytes_shared(path).decode('utf-8')))
        except (OSError,ValueError):failures.append({'operation_id':path.stem,'status':'unreadable_error_record'})
    return {'source':'local_operation_sidecars','observed_at':clock_or_system(clock).now(),
            'rows':rows,'telemetry_errors':failures,
            'scope':'progress only; not process liveness or authoritative completion'}


def trace_rows(directory, *, clock=None):
    observed_at = clock_or_system(clock).now()
    rows = []
    for path in sorted(Path(directory).glob('*.jsonl')):
        try:
            data = read_bytes_shared(path)
        except OSError:
            rows.append({'event':'unreadable_trace','file':path.name})
            continue
        source = {'path':str(path), 'sha256':hashlib.sha256(data).hexdigest(),
                  'observed_at':observed_at}
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


def phase_rows(directory, *, clock=None):
    spans = {}
    for event in trace_rows(directory, clock=clock):
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
        if 'trace_write_errors' in event: row['trace_write_errors'] = event['trace_write_errors']
    return list(spans.values())
