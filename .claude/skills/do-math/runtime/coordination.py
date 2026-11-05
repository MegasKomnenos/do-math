"""Live coordination information and session-owned declarations. No node admission lock."""
import argparse
import json
from pathlib import Path
import time
import uuid
from knowledge import canonical, replay
from runtime_support import read_json, write_json


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
    model = replay(instance)
    if node not in model['nodes'] and node not in model['aliases']:
        raise ValueError('unknown node')
    node = canonical(model, node)
    rows = board(instance, model=model)
    occupants = [r for r in rows if r['role'] == 'attempt' and node in r['nodes'] and r['session'] != inp['session']]
    path = session / 'declaration.json'
    data = read_json(path) if path.exists() else {'nodes': [], 'at': time.time()}
    if node not in data['nodes']:
        data['nodes'].append(node)
    write_json(path, data)
    warnings = []
    if occupants:
        warnings.append('Another attempt occupies this node. Inspect the board and coordinate; this declaration is not permission to duplicate its work.')
    if model['nodes'][node]['state'] != 'unresolved':
        warnings.append('This node is already settled or contested. Read its evidence before choosing work.')
    return {'nodes': data['nodes'], 'occupants': occupants, 'warnings': warnings,
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
        elif args.command == 'message':
            result = message(args.session, args.target, args.file)
        else:
            result = updates(args.session)
        print(json.dumps(result, ensure_ascii=True))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({'error': str(exc)}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
