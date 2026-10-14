import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path('C:/math')
RUN = REPO / 'docs/do-math/continuous-development-2026-10-13'
OUT = RUN / 'phases/026/tasks/role-contract-names/evidence'

def read(path):
    return path.read_text(encoding='utf-8-sig')

def write(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def snapshot(label):
    baseline = json.loads(read(RUN / 'phases/025/manager-evidence/source-inspected.json'))
    current = {p.relative_to(REPO).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for root in ('.claude/skills', '.agents/skills', '.agents/diff')
        for p in (REPO / root).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}
    mismatch = [p for p in sorted(set(baseline) | set(current)) if baseline.get(p) != current.get(p)]
    write(f'source-{label}.json', current)
    result = {'baseline_count': len(baseline), 'current_count': len(current), 'mismatches': mismatch, 'same': not mismatch,
        'scope': ['.claude/skills', '.agents/skills', '.agents/diff'], 'excludes': ['__pycache__', '*.pyc']}
    if label == 'end':
        start = json.loads(read(OUT / 'source-start.json'))
        result['start_end_differences'] = [p for p in start if start[p] != current[p]]
    write(f'preservation-{label}.json', result)
    print(json.dumps(result, ensure_ascii=False))

def population():
    phase = json.loads(read(RUN / 'phases/026/phase.json'))
    task = next(t for t in phase['tasks'] if t['id'] == 'role-contract-names')
    inputs = []
    for ref in task['inputs']:
        root, rel = ref.split(':', 1)
        p = (REPO if root == 'repo' else RUN) / rel
        content = read(p)
        inputs.append({'ref': ref, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'lines': len(content.splitlines())})
    write('inputs.json', inputs)
    docs = []
    for ref in task['inputs']:
        if not ref.startswith('repo:.claude/skills/do-math/계약/'):
            continue
        lines = read(REPO / ref[5:]).splitlines()
        occurrences = []
        fenced = False
        fences = []
        for n, line in enumerate(lines, 1):
            if line.startswith('```'):
                fenced = not fenced
                fences.append({'line': n, 'text': line})
            for match in re.finditer(r'`([^`\n]+)`', line):
                occurrences.append({'line': n, 'text': match.group(1), 'context': line, 'fenced': fenced})
        docs.append({'ref': ref, 'lines': len(lines), 'headings': [{'line': n, 'text': line} for n,line in enumerate(lines,1) if line.startswith('#')], 'fences': fences, 'occurrences': occurrences})
    write('population.json', docs)
    packets = json.loads(read(RUN / 'phases/001/tasks/document-closeout/evidence/followup-packets.json'))
    packet = next(p for p in packets['packets'] if p['id'] == 'N03')
    slices = []
    for old in packet['required_slices']:
        doc = next(d for d in docs if d['ref'] == old['document'])
        headings = doc['headings']
        if old['heading'] == '도입':
            start = 1
            stop = next((h['line']-1 for h in headings if h['text'].startswith('## ')), doc['lines'])
        else:
            matched = [h for h in headings if h['text'] == old['heading']]
            if len(matched) != 1:
                raise ValueError((old['id'], old['heading'], matched))
            start = matched[0]['line']
            stop = next((h['line']-1 for h in headings if h['line'] > start), doc['lines'])
        now = [o for o in doc['occurrences'] if start <= o['line'] <= stop]
        tokens = sorted({o['text'] for o in now})
        slices.append({'id': old['id'], 'document': doc['ref'], 'heading': old['heading'],
            'old_range': [old['start_line'], old['end_line']], 'current_range': [start, stop],
            'current_occurrences': now, 'added_tokens': sorted(set(tokens)-set(old['distinct_tokens'])),
            'removed_tokens': sorted(set(old['distinct_tokens'])-set(tokens)), 'fence_markers': [f for f in doc['fences'] if start <= f['line'] <= stop]})
    write('slice-map.json', slices)
    print('slices', len(slices), 'delta_slices', sum(bool(s['added_tokens'] or s['removed_tokens']) for s in slices))
    print(json.dumps([{'ref': d['ref'], 'lines': d['lines'], 'occurrences': len(d['occurrences']), 'fence_markers': len(d['fences'])} for d in docs], ensure_ascii=False, indent=2))

if sys.argv[1] in ('start', 'end'):
    snapshot(sys.argv[1])
elif sys.argv[1] == 'population':
    population()
elif sys.argv[1] == 'read':
    p = REPO / sys.argv[2]
    lines = read(p).splitlines()
    first = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    last = int(sys.argv[4]) if len(sys.argv) > 4 else len(lines)
    print('\n'.join(f'{n}: {line}' for n,line in enumerate(lines,1) if first <= n <= last))
elif sys.argv[1] == 'inspect':
    for rel in sys.argv[2:]:
        obj = json.loads(read(RUN / rel))
        print(rel, 'KEYS', list(obj) if isinstance(obj, dict) else 'list:'+str(len(obj)))
        def visit(value):
            if isinstance(value, dict):
                if value.get('id') in ('N03', 'PR24') or value.get('packet_id') == 'N03':
                    print(json.dumps(value, ensure_ascii=False, indent=2))
                    return
                for child in value.values():
                    visit(child)
            elif isinstance(value, list):
                for child in value:
                    visit(child)
        visit(obj)
