"""Real stored relation + current task producer; actual valid KN revision target."""
from pathlib import Path
import sys, json
from copy import deepcopy
ROOT = next(p for p in Path(__file__).resolve().parents if (p / '.claude/skills/do-math').is_dir())
SCRIPTS = ROOT / '.claude/skills/do-math/scripts'
sys.path[:0] = [str(SCRIPTS), str(SCRIPTS / 'tests')]
from test_query_records import QueryRecordTests
from test_redesign_TASKS import approved_fixture, approve
from do_math import planning, revisions

fixture = QueryRecordTests()
fixture.setUp()
try:
    _, stored, _ = fixture.repository.load(fixture.old_head)
    task, instance, runtime = approved_fixture()
    for family in ('knowledge', 'formal_results', 'expositions', 'identity_assessments',
                   'assessment_uses', 'kind_definitions', 'relations'):
        instance[family] = deepcopy(stored[family])
    task['inputs'].append(fixture.relation_id)
    approve(task, instance, runtime)
    assert planning.task_ready(task, instance, runtime)['state'] == 'ready'
    runtime['executions']['EX-reader'] = {'id': 'EX-reader', 'status': 'running', 'role': 'research_work',
        'action': {'id': 'AC-reader', 'role': 'research_work', 'target': task['id']}}
    results = []
    for endpoint in fixture.kids:
        action = {'id': 'AC-writer', 'role': 'research_preparation',
            'revision_targets': revisions.capture_targets(instance, runtime, [endpoint])}
        waits = planning.revision_waits(action, instance, runtime)
        original = deepcopy(task['inputs'])
        task['inputs'].append(endpoint)
        direct_waits = planning.revision_waits(action, instance, runtime)
        task['inputs'] = original
        assert waits == [] and direct_waits and direct_waits[0]['execution_id'] == 'EX-reader'
        results.append({'endpoint': endpoint, 'relation_only_reader_waits': waits,
            'same_endpoint_direct_reader_waits': direct_waits})
    result = {'stored_relation_snapshot': fixture.old_head, 'relation_id': fixture.relation_id,
        'domain_validation': 'QueryRecordTests current producers and ResearchRepository save/load passed',
        'results': results,
        'scope': 'Revision admission/read dependency bug. Does not assert normal revision bypasses impact invalidation.'}
    Path(__file__).with_name('relation-reader-results.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))
finally:
    fixture.tearDown()
