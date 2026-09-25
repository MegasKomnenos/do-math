"""Isolated real public control writes; current engine handler chain before mutation."""
from pathlib import Path
import sys, json
ROOT = next(p for p in Path(__file__).resolve().parents if (p / '.claude/skills/do-math').is_dir())
SCRIPTS = ROOT / '.claude/skills/do-math/scripts'
sys.path[:0] = [str(SCRIPTS), str(SCRIPTS / 'tests')]
from test_query_records import QueryRecordTests, INSTANCE_ID
from do_math.engine import control, ResearchEngine

fixture = QueryRecordTests()
fixture.setUp()
rows = []
try:
    for index, (action, config) in enumerate([
        *((action, [1]) for action in ('pause', 'resume', 'close', 'input', 'configure', 'request',
            'decision', 'knowledge', 'trust', 'external', 'conversation', 'source', 'quiesce', 'release_quiesce')),
        ('decision', {'change': []}),
        ('request', {'role': 'maintenance', 'review_replacement': {'action': []}}),
        ('conversation', {'operation': 'attach', 'id': 'conversation-audit', 'generation': 1,
            'disconnect_policy': 'pause', 'lease_seconds': 1e300}),
    ]):
        rid = 'audit-control-' + str(index)
        row = {'action': action, 'config': config}
        try:
            response = control(fixture.git, INSTANCE_ID, action, text='Boundary audit',
                config=config, request_id=rid)
            row['public_accepted'] = response['accepted']
        except Exception as error:
            row.update(public_accepted=False, public_error=type(error).__name__ + ': ' + str(error))
            rows.append(row)
            continue
        if action in {'quiesce', 'release_quiesce'}:
            row['ingestion'] = 'not executed: maintenance fast-path can mutate; static review recorded separately'
            rows.append(row)
            continue
        path = fixture.workspace / 'control' / INSTANCE_ID / (rid + '.json')
        request = json.loads(path.read_bytes())
        engine = ResearchEngine(fixture.git, INSTANCE_ID)
        # Select exactly the real accepted request under audit, excluding other
        # deliberately malformed requests from this same isolated test inbox.
        engine._inbox = lambda: [request]
        errors = []
        for attempt in range(2):
            try:
                engine._controls()
                errors.append(None)
            except Exception as error:
                errors.append(type(error).__name__ + ': ' + str(error))
        row.update(ingestion_errors=errors, processed=rid in engine.runtime['processed_controls'],
            pending_file_remains=path.is_file())
        rows.append(row)
    result = {'cases': rows, 'scope': 'No actual research or active instance; temporary fixture repository only.'}
    Path(__file__).with_name('control-boundary-results.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))
finally:
    fixture.tearDown()
