"""Live coordination information and session-owned declarations. Claims are first-wins under one instance lock."""
import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import time
import uuid
from knowledge import canonical, replay
from runtime_support import read_json, write_json

CLAIM_LOCK_SECONDS = 30.0


@contextmanager
def claims_lock(instance):
    """One claim at a time per instance; the OS releases the lock if its holder dies."""
    path = Path(instance) / 'runner' / 'claims.lock'
    deadline = time.monotonic() + CLAIM_LOCK_SECONDS
    with path.open('a+b') as stream:
        if path.stat().st_size == 0:
            stream.write(b'0')
            stream.flush()
        while True:
            stream.seek(0)
            try:
                if os.name == 'nt':
                    import msvcrt
                    msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError:
                if time.monotonic() >= deadline:
                    raise RuntimeError('another claim is still in progress; run the claim again')
                time.sleep(0.05)
        try:
            yield
        finally:
            if os.name == 'nt':
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)


def board(instance, state=None, model=None):
    instance = Path(instance)
    state = state or read_json(instance / 'runner/state.json')
    model = model or replay(instance)
    rows = []
    for pid, pipeline in state['pipelines'].items():
        if pipeline['stage'] == 'done':
            continue
        source = instance / 'sessions' / pipeline['producer'] / 'declaration.json' if pipeline['producer'] else None
        declaration = read_json(source) if source is not None and source.is_file() else {}
        rows.append({'pipeline': pid, 'session': pipeline['producer'], 'role': pipeline['role'],
                     'stage': pipeline['stage'] if pipeline['producer'] else 'queued',
                     'nodes': sorted({canonical(model, n) for n in declaration.get('nodes', []) if n in model['nodes'] or n in model['aliases']}),
                     'declared_at': declaration.get('at')})
    return rows


def claim(session, node):
    session = Path(session).resolve()
    inp = read_json(session / 'input.json')
    if inp['role'] != 'attempt':
        raise ValueError('only attempts declare node occupancy; other roles pursue their assigned responsibilities')
    instance = Path(inp['instance'])
    # Read the board, decide and record in one step, so two attempts cannot both take a node.
    with claims_lock(instance):
        model = replay(instance)
        if node not in model['nodes'] and node not in model['aliases']:
            raise ValueError('unknown node')
        node = canonical(model, node)
        rows = board(instance, model=model)
        path = session / 'declaration.json'
        data = read_json(path) if path.exists() else {'nodes': [], 'at': time.time()}
        held = {canonical(model, n) for n in data['nodes'] if n in model['nodes'] or n in model['aliases']}
        occupants = [r for r in rows if r['role'] == 'attempt' and node in r['nodes'] and r['session'] != inp['session']]
        if occupants and node not in held:
            taken = {n for r in rows if r['role'] == 'attempt' and r['session'] != inp['session'] for n in r['nodes']}
            available = [n for n, v in model['nodes'].items()
                         if v['canonical'] == n and v['state'] == 'unresolved' and n not in taken and n not in held]
            return {'claimed': False, 'node': node, 'nodes': data['nodes'], 'occupants': occupants,
                    'available': available,
                    'reason': 'Another attempt already occupies this node; nothing was recorded. '
                              'Choose an available node. If none is available, follow your guide for that case.',
                    'revision': model['sequence'], 'board': rows}
        if node not in held:
            data['nodes'].append(node)
            write_json(path, data)
    warnings = []
    if model['nodes'][node]['state'] != 'unresolved':
        warnings.append('This node is already settled or contested. Read its evidence before choosing work.')
    # Occupants remain only when an organizer merge joined nodes this attempt already held.
    return {'claimed': True, 'nodes': data['nodes'], 'occupants': occupants, 'warnings': warnings,
            'revision': model['sequence'], 'board': board(instance, model=model)}


def updates(session):
    session = Path(session).resolve()
    inp = read_json(session / 'input.json')
    instance = Path(inp['instance'])
    model = replay(instance)
    state = read_json(instance / 'runner/state.json')
    received = [read_json(p) for p in sorted((session / 'inbox').glob('*.json'))]
    return {'revision': model['sequence'], 'root_state': model['nodes'][canonical(model, 'root')]['state'],
            'board': board(instance, state, model), 'concerns': model['concerns'],
            'comprehensive_reviews': [{k: j.get(k) for k in ('id', 'status', 'session', 'record', 'task')}
                               for j in state['jobs'].values() if j['role'] == 'review' and j['task'].get('kind') == 'comprehensive'],
            'messages': received,
            'user_inputs': inp.get('user_inputs', [])}


def message(session, target, message_file):
    session = Path(session).resolve()
    inp = read_json(session / 'input.json')
    instance = Path(inp['instance'])
    state = read_json(instance / 'runner/state.json')
    if target not in state['sessions']:
        raise ValueError('unknown recipient session')
    text = Path(message_file).read_text(encoding='utf-8')
    if not text.strip():
        raise ValueError('empty coordination message')
    directory = instance / 'sessions' / target / 'inbox'
    directory.mkdir(exist_ok=True)
    name = uuid.uuid4().hex
    write_json(directory / (name + '.json'), {'id': name, 'from': inp['session'], 'at': time.time(), 'text': text})
    return {'delivered': str(directory / (name + '.json'))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('board', 'claim', 'updates', 'message'):
        p = sub.add_parser(name)
        p.add_argument('session', type=Path)
        if name == 'claim':
            p.add_argument('node')
        if name == 'message':
            p.add_argument('target')
            p.add_argument('--file', required=True, type=Path)
    args = parser.parse_args()
    try:
        if args.command == 'claim':
            result = claim(args.session, args.node)
            if not result['claimed']:
                print(json.dumps(result, ensure_ascii=True))
                return 1
        elif args.command == 'message':
            result = message(args.session, args.target, args.file)
        else:
            result = updates(args.session)
        print(json.dumps(result, ensure_ascii=True))
        return 0
    except (OSError, ValueError, KeyError, TypeError, RuntimeError) as exc:
        print(json.dumps({'error': str(exc)}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
