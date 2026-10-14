import argparse
import hashlib
import json
from pathlib import Path
import subprocess

REPO = Path('C:/math')
RUN = REPO / 'docs/do-math/continuous-development-2026-10-13'
OUT = RUN / 'phases/026/tasks/policy-semantics/evidence'
NAMES = ['conversation_loss_policy', 'disconnect_policy', 'model_policy', 'external_policy', 'adopt_default_review_policy']

def resolve(ref):
    root, name = ref.split(':', 1)
    return (REPO if root == 'repo' else RUN) / name

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def snapshot(stage):
    expected = json.loads((RUN / 'phases/025/manager-evidence/source-inspected.json').read_text(encoding='utf-8-sig'))
    current = {p.relative_to(REPO).as_posix(): sha(p)
               for root in ['.claude/skills', '.agents/skills', '.agents/diff']
               for p in (REPO / root).rglob('*')
               if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}
    task = json.loads((RUN / 'phases/026/phase.json').read_text(encoding='utf-8-sig'))['tasks'][0]
    inputs = {ref: sha(resolve(ref)) for ref in task['inputs']}
    mismatch = [name for name in sorted(set(expected) | set(current)) if expected.get(name) != current.get(name)]
    head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True, capture_output=True, check=True).stdout.strip()
    result = {'head': head, 'source_count': len(current), 'mismatches_with_025': mismatch, 'sources': current, 'inputs': inputs}
    if stage == 'end':
        start = json.loads((OUT / 'source-start.json').read_text(encoding='utf-8'))
        result['changed_since_start'] = [name for name in sorted(set(current) | set(start['sources'])) if current.get(name) != start['sources'].get(name)]
        result['changed_inputs_since_start'] = [name for name in inputs if inputs[name] != start['inputs'].get(name)]
    save('source-' + stage + '.json', result)
    print(json.dumps({k:v for k,v in result.items() if k not in ['sources', 'inputs']}, ensure_ascii=False))

def lines(ref, first, last):
    content = resolve(ref).read_text(encoding='utf-8-sig').splitlines()
    print(ref)
    for number in range(first, min(last, len(content)) + 1):
        print(f'{number}: {content[number-1]}')

def census():
    historical = json.loads(resolve('run:phases/024/tasks/document-waits/evidence/policy-name-decisions.json').read_text(encoding='utf-8-sig'))
    packet = json.loads(resolve('run:phases/001/tasks/document-closeout/evidence/followup-packets.json').read_text(encoding='utf-8-sig'))
    slices = [s for p in packet['packets'] if p['id'] == 'N01' for s in p['required_slices']
              if s['id'] in ['N01-020', 'N01-218', 'N01-230', 'N01-268', 'N01-273']]
    rows = []
    for policy in historical:
        for occurrence in policy['occurrences']:
            old = occurrence['historical']
            content = resolve(old['document']).read_text(encoding='utf-8-sig').splitlines()
            matches = [i + 1 for i, line in enumerate(content) if line == occurrence['current_text']]
            assert len(matches) == 1, (policy['name'], old['document'], matches)
            rows.append({'name': policy['name'], 'historical_line': old['line'], 'line_024': occurrence['current_line'],
                         'current_line': matches[0], 'document': old['document'], 'current_text': content[matches[0] - 1],
                         'sha256_024': occurrence['sha256'], 'sha256_current': sha(resolve(old['document'])),
                         'sentence_unchanged': True})
    documents = sorted({row['document'] for row in rows})
    all_rows = []
    for ref in documents:
        for i, line in enumerate(resolve(ref).read_text(encoding='utf-8-sig').splitlines(), 1):
            for name in NAMES:
                if name in line:
                    all_rows.append({'name': name, 'document': ref, 'line': i, 'text': line})
    result = {'scope': 'Five names only in N01-020/218/230/268/273; surrounding names excluded.',
              'historical_occurrences': rows, 'current_name_line_pairs_in_documents': all_rows,
              'historical_count': len(rows), 'current_name_line_pair_count': len(all_rows), 'slices': slices}
    baseline = json.loads(resolve('run:phases/001/tasks/document-closeout/evidence/binding-inventory.json').read_text(encoding='utf-8-sig'))
    result['001_policy_mentions_equal_024_historical'] = sorted((r['policy'],r['document'],r['line'],r['token']) for r in baseline['other_reference_census']['policy_mentions']) == sorted((p['name'],r['historical']['document'],r['historical']['line'],r['historical']['token']) for p in historical for r in p['occurrences'])
    assert result['001_policy_mentions_equal_024_historical']
    for row in all_rows:
        candidates = [s for s in slices if s['document'] == row['document'] and s['start_line'] <= row['line'] <= s['end_line']+2]
        assert len(candidates) == 1, row
        row['slice_id'] = candidates[0]['id']
    save('population.json', result)
    print(json.dumps({'historical_count': len(rows), 'current_name_line_pair_count': len(all_rows),
                      'current_lines': sorted({(row['document'], row['line']) for row in all_rows}),
                      'unchanged_sentences': all(row['sentence_unchanged'] for row in rows)}, ensure_ascii=False))

def excerpts():
    requests = json.loads((OUT / 'excerpt-requests.json').read_text(encoding='utf-8'))
    result = []
    for request in requests:
        path = resolve(request['reference'])
        content = path.read_text(encoding='utf-8-sig').splitlines()
        first, last = request['lines']
        assert first > 0 and last <= len(content)
        result.append({**request, 'sha256': sha(path), 'text': '\n'.join(f'{i}: {content[i-1]}' for i in range(first, last+1))})
    save('source-excerpts.json', result)
    print(json.dumps({'excerpts': len(result), 'files': len({r['reference'] for r in result})}))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode')
    parser.add_argument('args', nargs='*')
    args = parser.parse_args()
    if args.mode in ['start', 'end']:
        snapshot(args.mode)
    elif args.mode == 'lines':
        lines(args.args[0], int(args.args[1]), int(args.args[2]))
    elif args.mode == 'census':
        census()
    elif args.mode == 'excerpts':
        excerpts()
