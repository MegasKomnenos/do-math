from difflib import unified_diff
import hashlib
import json
from pathlib import Path
import subprocess

from session_tools import REPO, RUN, EVIDENCE, read, save, sha, now

prior = RUN / 'phases/010/tasks/reading-limits/evidence'
manifest = read(prior / 'fixture-manifest.json')
pages = read(prior / 'fixture-page-results.json')
capped = read(prior / 'fixture-capped-results.json')
observed = read(prior / 'fixture-verification.json')
aggregate = read(prior / 'fixture-aggregate-results.json')
results = []
for fixture, checked, clipped in zip(manifest['fixtures'], observed['fixtures'], capped):
    path = prior / fixture['name']
    assert sha(path) == fixture['sha256']
    expected = path.read_text(encoding='utf-8').splitlines()
    assert expected == fixture['expected_lines']
    prefix = fixture['name'].removeprefix('fixture-').removesuffix('.txt')
    local_pages = [page for page in pages if page['case'].startswith(prefix + '-page-')]
    received = []
    for page in local_pages:
        assert page['result']['exit_code'] == 0
        output = page['result']['output'].splitlines()
        assert output == expected[page['start'] - 1:page['end']]
        assert page['start'] == len(received) + 1
        received.extend(output)
    assert received == expected and len(received) == 80
    clipped_text = clipped['result']['output']
    assert clipped['result']['exit_code'] == 0 and 'truncated' in clipped_text and 'END:080' in clipped_text
    intact = [index for index, line in enumerate(expected, 1) if line in clipped_text.splitlines()]
    assert intact == checked['capped_complete_line_ids']
    missing = [index for index in range(1, 81) if index not in intact]
    assert missing == checked['missing_line_ids']
    prefix_end = 0
    while prefix_end + 1 in intact:
        prefix_end += 1
    assert prefix_end + 1 == missing[0]
    results.append({'fixture': fixture['name'], 'sha256': sha(path),
        'original_bytes': fixture['bytes'], 'verified_pages': len(local_pages), 'verified_lines': len(received),
        'complete_prefix_end': prefix_end, 'first_missing_line': missing[0],
        'last_missing_line': missing[-1], 'missing_count': len(missing),
        'visible_tail_end': 80, 'incorrect_next_line_from_tail': 81,
        'correct_next_line_from_prefix': prefix_end + 1,
        'explicit_page_receipt_closes_all_gaps': True})
for inner in aggregate['before_outer_delivery']:
    assert inner['result']['exit_code'] == 0
    assert len(inner['result']['output'].splitlines()) == 10
assert 'truncated' in aggregate['model_observed']['warning']
assert aggregate['model_observed']['complete_ascii_line_ids'] == [1, 2, 3]
assert aggregate['model_observed']['complete_unicode_line_ids'] == [6, 7, 8, 9, 10]
save(EVIDENCE / 'reading-verification.json', {'at_utc': now(), 'result': 'pass',
    'fixtures': results, 'aggregate': {'inner_complete': True, 'outer_complete': False,
        'ascii_missing_from_page': list(range(4, 11)), 'unicode_missing_from_page': list(range(1, 6)),
        'new_procedure': 'Check the final aggregate response; reduce page length or simultaneous outputs, then recover every unconfirmed range.'},
    'long_line': 'Partial characters never establish a complete line. Recover the remaining characters or reread the complete line with a smaller output selection.',
    'source_observation': 'Rechecked original 010 fixtures and 16 pages; no new host read trial or paid/model session.',
    'certification': '13-C/L01 remain not certified; original output byte criterion and unspecified operator profile remain unchanged.'})

start = read(EVIDENCE / 'source-start.json')
paths = ['.claude/skills/do-math/SKILL.md',
    '.claude/skills/do-math/scripts/tests/boundary/test_scheduling_call_jobs.py',
    '.claude/skills/do-math/scripts/tests/structure/test_doc_code.py',
    '.claude/skills/do-math/scripts/tests/sim/test_knowledge_currentness.py']
diffs = []
for path in paths:
    raw = subprocess.check_output(['git', 'show', 'HEAD:' + path], cwd=REPO)
    choices = (raw, raw.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n'))
    original = next(value for value in choices if hashlib.sha256(value).hexdigest() == start[path])
    before = original.decode('utf-8').splitlines(keepends=True)
    after = (REPO / path).read_bytes().decode('utf-8').splitlines(keepends=True)
    assert all(line.endswith('\r\n') for line in after) == all(line.endswith('\r\n') for line in before)
    if path.endswith('/SKILL.md'):
        assert len(before) == len(after)
        differences = [i for i, (a, b) in enumerate(zip(before, after)) if a != b]
        assert differences == [13]
        # All actor boundaries, required document order and edition reuse remain before this changed sentence.
        assert before[13].split('긴 문서는')[0] == after[13].split('긴 문서는')[0]
    diffs.extend(unified_diff(before, after, fromfile='start/' + path, tofile='final/' + path))
(EVIDENCE / 'changes.diff').write_text(''.join(diffs), encoding='utf-8', newline='')
print(json.dumps({'fixtures': results, 'skill_changed_lines': [14], 'diff': 'changes.diff'}, ensure_ascii=False))
