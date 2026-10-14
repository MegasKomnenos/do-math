import ast
import hashlib
import json
import re
from pathlib import Path

REPO = Path('C:/math')
RUN = REPO / 'docs/do-math/continuous-development-2026-10-13'
OUT = RUN / 'phases/028/tasks/operator-names/evidence'

def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def resolve(ref):
    root, path = ref.split(':', 1)
    return (REPO if root == 'repo' else RUN) / path.split('#')[0]

assignment = next(x for x in read_json(RUN / 'phases/028/assignments.json')['tasks'] if x['task'] == 'operator-names')
baseline = read_json(RUN / 'phases/027/manager-evidence/source-inspected.json')
current = {p: sha(REPO / p) if (REPO / p).is_file() else None for p in baseline}
import sys
phase = 'end' if '--end' in sys.argv else 'start'
write('source-' + phase + '.json', current)
diff = [p for p in baseline if baseline[p] != current[p]]
if phase == 'end':
    start = read_json(OUT / 'source-start.json')
    write('source-preservation.json', {'files': len(current), 'baseline_mismatches': diff, 'start_end_mismatches': [p for p in current if current[p] != start[p]]})
    print(json.dumps({'files': len(current), 'baseline_mismatches': len(diff), 'start_end_mismatches': sum(current[p] != start[p] for p in current)}))
    raise SystemExit(0)

task = next(t for t in read_json(RUN / 'phases/028/phase.json')['tasks'] if t['id'] == 'operator-names')
write('input-profiles.json', [{'ref': ref, 'sha256': sha(resolve(ref)), 'bytes': resolve(ref).stat().st_size} for ref in task['inputs']])
packet = next(p for p in read_json(RUN / 'phases/001/tasks/document-closeout/evidence/followup-packets.json')['packets'] if p['id'] == 'N01')
expected = [x for x in packet['required_slices'] if x['id'] in {s['id'] for s in assignment['slices']}]
assert {x['id'] for x in expected} == {s['id'] for s in assignment['slices']} and len(expected) == 66
sections = []
profiles = []
for doc in assignment['documents']:
    path = resolve(doc)
    lines = path.read_text(encoding='utf-8-sig').splitlines()
    headings = [(0, '도입')]
    fence = False
    for i, line in enumerate(lines):
        if line.startswith('```'): fence = not fence
        if not fence and re.match(r'^#{1,6} ', line): headings.append((i, line))
    slices = [s for s in assignment['slices'] if s['document'] == doc]
    for s in slices:
        matches = [j for j, (_, h) in enumerate(headings) if h == s['heading']]
        assert len(matches) == 1, (s, matches)
        j = matches[0]
        first = headings[j][0]
        original = [x for x in packet['required_slices'] if x['document'] == doc]
        original.sort(key=lambda x: x['start_line'])
        position = next(k for k, x in enumerate(original) if x['id'] == s['id'])
        if position + 1 < len(original):
            next_heading = original[position+1]['heading']
            next_matches = [i for i, h in headings if h == next_heading]
            assert len(next_matches) == 1, next_heading
            last = next_matches[0]
        else:
            last = len(lines)
        text = '\n'.join(lines[first:last])
        inline = []
        fence = False
        code = []
        for i in range(first, last):
            line = lines[i]
            if line.startswith('```'): fence = not fence; code.append({'line': i+1, 'text': line}); continue
            if fence: code.append({'line': i+1, 'text': line}); continue
            for m in re.finditer(r'`([^`]+)`', line): inline.append({'line': i+1, 'column': m.start()+1, 'text': m.group(1)})
        sections.append({**s, 'current_start': first+1, 'current_end': last, 'sha256': sha(path), 'text': text, 'inline': inline, 'code_lines': code})
    profiles.append({'document': doc, 'sha256': sha(path), 'lines': len(lines), 'sections': len(slices)})
sections.sort(key=lambda s: s['id'])
write('section-profiles.json', sections)
write('population.json', {'expected_ids': [s['id'] for s in assignment['slices']], 'actual_ids': [s['id'] for s in sections], 'documents': profiles, 'baseline_files': len(current), 'baseline_mismatches': diff, 'inline_occurrences': sum(len(s['inline']) for s in sections)})
(OUT / 'current-sections.md').write_text('\n\n'.join('=== ' + s['id'] + ' ' + s['document'] + ' ' + str(s['current_start']) + '-' + str(s['current_end']) + ' ===\n' + s['text'] for s in sections), encoding='utf-8')
print(json.dumps({'sections': len(sections), 'inline': sum(len(s['inline']) for s in sections), 'baseline_files': len(current), 'baseline_mismatches': diff, 'documents': profiles}, ensure_ascii=False))
