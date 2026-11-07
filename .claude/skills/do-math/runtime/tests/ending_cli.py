"""A deterministic CLI conversation, used only by end-reconsideration tests."""
import json
from pathlib import Path
import sys

session = Path.cwd()
config = json.loads((session / 'work/ending-test.json').read_text())
prompt = sys.stdin.read()
history = session / 'work/turns.jsonl'
number = len(history.read_text().splitlines()) if history.exists() else 0
with history.open('a', encoding='utf-8') as stream:
    stream.write(json.dumps({'turn': number, 'prompt': prompt}) + '\n')
identity = '01234567-89ab-cdef-0123-456789abcdef'
if config.get('change_identity_at') == number:
    identity = 'fedcba98-7654-3210-fedc-ba9876543210'
if not config.get('omit_identity'):
    print(json.dumps({'type': 'thread.started', 'thread_id': identity}), flush=True)
print(json.dumps({'type': 'item.completed', 'item': {'type': 'agent_message',
                  'text': f'Retained mathematical work from turn {number}.'}}), flush=True)
(session / 'output/report.md').write_text(f'Research through turn {number}.', encoding='utf-8')
if json.loads((session / 'input.json').read_text())['role'] == 'peer':
    (session / 'output/record.json').write_text(json.dumps({
        'title': 'Retained investigation', 'description': 'A developed contribution.',
        'exposition': 'report.md', 'claims': [], 'nodes': [], 'relations': [],
        'solutions': [], 'glossary': []}), encoding='utf-8')
if config.get('refuse_at') == number:
    print(json.dumps({'type': 'error', 'message': "You've hit your usage limit. Try again later."}), flush=True)
    raise SystemExit(1)
if config.get('fail_at') == number:
    raise SystemExit(2)
if config.get('no_research'):
    (session / 'output/outcome.json').write_text('{"disposition":"no_research"}')
if number:
    request = json.loads((session / 'end-request.json').read_text())
    target = session / 'output/end-decision.json'
    if config.get('malformed_at') == number:
        target.write_text('{broken')
    elif config.get('stale_at') == number:
        target.write_text(json.dumps({'request_id': 'old-request', 'decision': 'end',
                                     'basis': 'task_completed', 'explanation': 'Stale decision.'}))
    elif number >= config.get('end_after', 100):
        target.write_text(json.dumps({'request_id': request['id'], 'decision': 'end',
                                     'basis': config.get('basis', 'no_way_forward'),
                                     'explanation': 'The scripted investigation has reached its endpoint.'}))
