"""13-B assertions on a producer's actual durable wait and public projection."""
from copy import deepcopy
import json

from do_math.reporting import status_report, render_human_report


def assert_status_report(test, engine):
    """Read one real snapshot and render its JSON value without changing that snapshot."""
    head, instance, runtime = engine.store.load()
    before = deepcopy((instance, runtime))
    report = status_report(engine.store, head, instance, runtime, requested_areas=['record_storage'],
        evaluation_context={'now': engine.ports.clock.now(), 'host_id': engine.host_id})
    test.assertEqual(report['snapshot'], head)
    wire = json.loads(json.dumps(report, ensure_ascii=False))
    test.assertEqual(wire, report)
    human = render_human_report(wire)
    test.assertEqual((instance, runtime), before)
    test.assertEqual(engine.store.load(), (head, *before))
    return report, human


def assert_activity_wait_row(test, report, identifier, activity):
    """Compare the public row to the owner's actual recorded condition."""
    row = report['waiting_activities'][identifier]
    test.assertEqual({key: row[key] for key in activity['waiting']}, activity['waiting'])
    test.assertEqual(row['activity_kind'], activity['activity_kind'])
    test.assertEqual(row['coordinates'], {'activity_id': identifier, 'owner_ref': activity['owner_ref'],
        'execution_ids': activity['assigned_execution_ids']})
    lines = render_human_report(report).splitlines()
    matching = [index for index, line in enumerate(lines) if line.startswith('activity ' + identifier + ':')]
    test.assertEqual(len(matching), 1)
    index = matching[0]
    wait = activity['waiting']
    test.assertIn('wait=' + wait['kind'], lines[index])
    test.assertIn('next=' + str(wait['next_owner']), lines[index])
    test.assertIn('reason=' + wait['reason'].splitlines()[0], lines[index])
    # Reasons may span lines, so locate the structured details after the full reason.
    index += len(wait['reason'].splitlines())
    for offset, field in enumerate(('coordinates', 'condition')):
        prefix = '  ' + field + ': '
        test.assertTrue(lines[index + offset].startswith(prefix), (identifier, field))
        test.assertEqual(json.loads(lines[index + offset][len(prefix):]), row[field])
    row['coordinates']['execution_ids'].append('changed observer copy')
    if isinstance(row['condition'], (dict, list)):
        row['condition'].clear()


def assert_task_wait_report(test, engine, identifier):
    """A real stored task wait, including its explanation and exact basis."""
    _, _, runtime = engine.store.load()
    wait = runtime['tasks'][identifier]['waiting']
    test.assertTrue(wait.get('reason'), wait)
    report, human = assert_status_report(test, engine)
    row = next(row for row in report['tasks'] if row['id'] == identifier)
    test.assertIn(wait, row['waits'])
    test.assertEqual(row['next_owner'], wait['next_owner'])
    lines = human.splitlines()
    position = next(i for i, line in enumerate(lines) if line.startswith('  ' + identifier + ' revision='))
    displayed = []
    for line in lines[position + 1:]:
        if not line.startswith('    '):
            break
        if line.startswith('    wait: '):
            displayed.append(json.loads(line.removeprefix('    wait: ')))
    test.assertIn(wait, displayed)
    next(value for value in row['waits'] if value == wait).clear()
    test.assertEqual(engine.store.load()[2]['tasks'][identifier]['waiting'], wait)


def assert_wait_report(test, engine, identifier):
    head, instance, runtime = engine.store.load()
    before = deepcopy((instance, runtime))
    entry = runtime['waiting_actions'][identifier]
    report = status_report(engine.store, head, instance, runtime, requested_areas=['record_storage'],
        evaluation_context={'now': engine.ports.clock.now(), 'host_id': engine.host_id})
    test.assertEqual(report['snapshot'], head)
    test.assertEqual(report['instance_id'], instance['id'])
    row = report['waiting_actions'][identifier]
    for key, value in entry.items():
        if key != 'action':
            test.assertEqual(row[key], value, (identifier, key))
    test.assertEqual(row['role'], entry['action']['role'])
    test.assertEqual(row['target'], entry['action'].get('target'))
    test.assertEqual(row['coordinates']['action_id'], identifier)
    for field in ('target', 'owner_activity_id', 'profile_ref', 'grant_id', 'review_cycle_id', 'slot', 'round'):
        if field in entry['action'] and entry['action'][field] is not None:
            test.assertEqual(row['coordinates'][field], entry['action'][field])
    lines = render_human_report(report).splitlines()
    matching = [index for index, line in enumerate(lines) if line.startswith('action ' + identifier + ':')]
    test.assertEqual(len(matching), 1)
    index = matching[0]
    test.assertIn('wait=' + entry['kind'], lines[index])
    test.assertIn('next=' + str(entry['next_owner']), lines[index])
    test.assertIn('reason=' + entry['reason'].splitlines()[0], lines[index])
    prefix = '  coordinates: '
    test.assertTrue(lines[index + 1].startswith(prefix))
    test.assertEqual(json.loads(lines[index + 1][len(prefix):]), row['coordinates'])
    owner = entry['action'].get('owner_activity_id')
    activity = runtime.get('activities', {}).get(owner)
    if activity is not None and activity['status'] == 'waiting':
        assert_activity_wait_row(test, report, owner, activity)
    for value in row.values():
        if isinstance(value, (dict, list)):
            value.clear()
    test.assertEqual((instance, runtime), before)
    test.assertEqual(engine.store.load(), (head, *before))
