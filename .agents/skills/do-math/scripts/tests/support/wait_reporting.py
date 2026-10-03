"""13-B assertions on a producer's actual durable wait and public projection."""
from copy import deepcopy
import json

from do_math.reporting import status_report, render_human_report


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
    for value in row.values():
        if isinstance(value, (dict, list)):
            value.clear()
    test.assertEqual((instance, runtime), before)
    test.assertEqual(engine.store.load(), (head, *before))
