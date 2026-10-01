"""Command-line side of the workspace read tool (layer 3).

``input/tools/read_input.py`` runs ``read_main`` inside the producer's own
process. It wires the record map rules in ``context_store`` to a Git state store
and an append-only read log; the engine never runs it, so the log's times come
from the operating system's clock.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .context_store import (READ_LOG, _READ_LOCK, read_content, read_refusal, read_stable, record_summaries,
                            relative_path, safe_path)
from .file_io import os_lock


def _append_reads(workspace, rows, *, clock):
    log = safe_path(workspace, READ_LOG)
    log.parent.mkdir(parents=True, exist_ok=True)
    with os_lock(safe_path(workspace, _READ_LOCK), blocking=True), log.open('ab') as stream:
        for row in rows:
            stream.write(json.dumps({'at': clock.now(), **row}, ensure_ascii=False, sort_keys=True).encode('utf-8') + b'\n')


def read_main(argv=None, *, ports=None, environment=None):
    """Read this execution's input snapshot within its record map (input/tools/read_input.py).

    Records come back decoded, other files as text or base64, or written to --output. Every
    read, refusal and error is appended to checks/reads.jsonl.
    """
    import os
    from .wiring import real_ports
    environment = dict(os.environ) if environment is None else environment
    ports = real_ports(environment=environment) if ports is None else ports
    clock, jobs, backend = ports.clock, ports.jobs, ports.git_backend
    import argparse
    import sys
    from .values import strict_json_loads
    parser = argparse.ArgumentParser(description=read_main.__doc__)
    parser.add_argument('--list', action='store_true', help='record_index families, or with --family their records')
    parser.add_argument('--family', help='a root/family of record_index, with --list')
    parser.add_argument('--id', action='append', default=[], help='a record ID of record_index (repeatable)')
    parser.add_argument('--path', action='append', default=[], help='a file path of the input snapshot (repeatable)')
    parser.add_argument('--output', help='workspace-relative file for the bytes of one --path')
    args = parser.parse_args(argv)
    if args.list == bool(args.id or args.path):
        parser.error('give --list, or one or more --id or --path')
    if args.family is not None and not args.list:
        parser.error('--family requires --list')
    if args.output is not None and (args.id or len(args.path) != 1):
        parser.error('--output takes exactly one --path')
    workspace = Path.cwd().resolve()
    context = strict_json_loads(read_stable(safe_path(workspace, 'input/submission/context.json')))
    snapshot, index = context.get('snapshot'), context.get('record_index', {})
    store = []

    def snapshot_store():
        if not store:
            from .git_store import GitStateStore
            binding = context['record_store']
            store.append(GitStateStore(Path(binding['repository']), binding['instance_id'], backend=backend, clock=clock))
        return store[0]

    def read(path):
        return snapshot_store().read_bytes(snapshot, path)

    def entry(request, path, output=None):
        row = {'request': request, 'path': path, 'snapshot': snapshot}
        refusal = read_refusal(context, workspace, path, output)
        if refusal:
            return {**row, 'status': 'refused', 'reason': refusal}
        try:
            raw = read(path)
        except (OSError, ValueError, KeyError, RuntimeError) as error:
            return {**row, 'status': 'error', 'reason': str(error)}
        row.update(status='ok', sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))
        if output is not None:
            target = safe_path(workspace, output)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            return {**row, 'output': relative_path(output).as_posix()}
        return {**row, **read_content(path, raw, read)}

    if args.list and args.family is None:
        result = {'snapshot': snapshot, 'status': 'ok', 'ledger': context.get('record_map', {}).get('ledger'),
                  'families': {family: len(ids) for family, ids in index.items()}}
        logged = []
    elif args.list:
        result = {'snapshot': snapshot, 'family': args.family, 'status': 'refused', 'records': []}
        if args.family in index:
            paths = {identifier: f'{args.family}/{identifier}.json' for identifier in index[args.family]}
            try:
                files = snapshot_store().read_many(snapshot, list(paths.values()))
                result.update(status='ok', records=record_summaries(paths, files))
            except (OSError, ValueError, KeyError, RuntimeError) as error:
                result.update(status='error', reason=str(error))
        logged = [{'request': '--list ' + args.family, 'path': args.family, 'snapshot': snapshot,
                   'status': result['status'], 'count': len(result['records'])}]
    else:
        rows = [entry(identifier, next((f'{family}/{identifier}.json' for family, ids in index.items()
                                        if identifier in ids), None)) for identifier in args.id]
        rows += [entry(path, path, args.output) for path in args.path]
        result = {'snapshot': snapshot, 'status': 'ok' if all(row['status'] == 'ok' for row in rows) else 'incomplete',
                  'records': rows}
        logged = [{key: row[key] for key in ('request', 'path', 'snapshot', 'status', 'sha256', 'bytes', 'reason')
                   if key in row} for row in rows]
    if logged:
        _append_reads(workspace, logged, clock=ports.clock)
    sys.stdout.buffer.write(json.dumps(result, ensure_ascii=False).encode('utf-8') + b'\n')
    return 0 if result['status'] == 'ok' else 1
