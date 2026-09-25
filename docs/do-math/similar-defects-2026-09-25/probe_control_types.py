from pathlib import Path
import json, sys, subprocess
ROOT = next(p for p in Path(__file__).resolve().parents if (p / '.claude/skills/do-math').is_dir())
SCRIPTS = ROOT / '.claude/skills/do-math/scripts'
sys.path[:0] = [str(SCRIPTS), str(SCRIPTS / 'tests')]
from test_input_recovery import InputRecoveryPublicTests
from do_math.engine import ResearchEngine, control

fixture = InputRecoveryPublicTests()
fixture.setUp()
rows = []
try:
    cases = [
        ('charter_content_list', {'kind':'charter', 'record':{'kind':'charter', 'content':[]}}),
        ('grant_expiry_number', {'kind':'grant', 'grant':{'kind':'local', 'roles':['maintenance'], 'expires_at':1}}),
    ]
    for name, change in cases:
        request_id = 'UC-audit-' + name
        path = fixture.root / (name + '.json')
        path.write_text(json.dumps(change), encoding='utf-8')
        command = [sys.executable, str(SCRIPTS / 'do_math.py'), 'decision',
                   *fixture.instance_args(fixture.identifier), '--file', str(path), '--request-id', request_id]
        completed = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
        owner = ResearchEngine(fixture.repo, fixture.identifier)
        retries = []
        for _ in range(2):
            try:
                owner.process_controls()
                retries.append('returned')
            except Exception as error:
                retries.append(type(error).__name__ + ': ' + str(error))
        _, _, runtime = owner.store.load()
        rows.append({'case':name, 'payload':change, 'cli_returncode':completed.returncode,
            'cli_stdout':completed.stdout, 'cli_stderr_tail':completed.stderr.splitlines()[-4:],
            'retries':retries, 'processed':request_id in runtime['processed_controls'],
            'published_control_result':owner.control_result(request_id)})
        # Remove only this synthetic pending inbox item so the next malformed case is independent.
        (Path(owner.instance['workspace']) / 'control' / fixture.identifier / (request_id + '.json')).unlink()
    request_id = 'UC-audit-change-list'
    receipt = control(fixture.repo, fixture.identifier, 'decision', config={'change':[]}, request_id=request_id)
    owner = ResearchEngine(fixture.repo, fixture.identifier)
    try:
        owner.process_controls()
        failure = 'returned'
    except Exception as error:
        failure = type(error).__name__ + ': ' + str(error)
    rows.append({'case':'python_public_change_list', 'accepted':receipt['accepted'], 'failure':failure,
                 'processed':request_id in owner.store.load()[2]['processed_controls']})
    for row in rows:
        assert row['processed'] is False, row
        if 'retries' in row: assert all(r.startswith('AttributeError:') for r in row['retries']), row
    rendered = json.dumps(rows, ensure_ascii=False, indent=2)
    Path(__file__).with_name('control-types-result.json').write_text(rendered, encoding='utf-8')
    print(rendered)
finally:
    fixture.doCleanups()
