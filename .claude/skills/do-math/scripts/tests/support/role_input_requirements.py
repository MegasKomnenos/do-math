"""Check semantic requirement rows against a real prepared role input.

The actual engine and packager produce both arguments. This observer does not
change a context, fill a missing field, or replace any product method.
"""
import json

from do_math.context_store import read_source
from do_math.role_input_requirements import judgment_input_keys, judgment_input_paths
from do_math.canonical import same_json_value


def assert_judgment_inputs(test, role, prepared, workspace, *, producer_context):
    original = prepared['validation_context']
    delivered = prepared['context']
    manifest = prepared['manifest']
    test.assertEqual(manifest['snapshot'], original['snapshot'])
    catalog = {row['key']: {k: v for k, v in row.items() if k != 'key'}
               for row in manifest['catalog']}
    resolved_keys = {}
    for key in judgment_input_keys(role, original['action']):
        with test.subTest(role=role, required_input=key):
            test.assertIn(key, original, 'actual producer omitted a contract judgment input')
            test.assertIn(key, delivered, 'packaging omitted a contract judgment input')
            value = delivered[key]
            if isinstance(value, dict) and set(value) == {'source_ref', 'total'}:
                ref = value['source_ref']
                test.assertEqual(ref, catalog[key])
                resolved = read_source(workspace, ref, limit=max(1, ref['bytes']))
                test.assertEqual(resolved['status'], 'ok', key)
                test.assertFalse(resolved['truncated'], key)
                value = json.loads(resolved['bytes'])
            resolved_keys[key] = value
            if key == 'tasks' and role in ('research_preparation', 'research_plan'):
                # The checker keeps the complete task registry. The model's
                # comparison population is projected; its catalog retains
                # every original task, including results, at exact sources.
                registry = {row['id']: row for row in producer_context['tasks']}
                test.assertEqual(set(registry), {row['id'] for row in original['tasks']})
                task_catalog = delivered['task_catalog']
                if isinstance(task_catalog, dict) and set(task_catalog) == {'source_ref', 'total'}:
                    ref = task_catalog['source_ref']
                    resolved = read_source(workspace, ref, limit=max(1, ref['bytes']))
                    test.assertEqual(resolved['status'], 'ok')
                    test.assertFalse(resolved['truncated'])
                    task_catalog = json.loads(resolved['bytes'])
                test.assertEqual({row['id'] for row in task_catalog}, set(registry))
                for task in task_catalog:
                    ref = task['source_ref']
                    test.assertEqual(ref['snapshot'], original['snapshot'])
                    resolved = read_source(workspace, ref, limit=max(1, ref['bytes']))
                    test.assertEqual(resolved['status'], 'ok')
                    test.assertFalse(resolved['truncated'])
                    test.assertTrue(same_json_value(json.loads(resolved['bytes']), registry[task['id']]))
                for task in value:
                    expected = registry[task['id']]
                    for field in expected.keys() & task.keys():
                        test.assertTrue(same_json_value(task[field], expected[field]), field)
                if role == 'research_plan':
                    test.assertEqual({row['id'] for row in value},
                                     set(original['ready_task_ids']) | set(original['returned_task_ids']))
                else:
                    test.assertLessEqual({identifier for identifier, row in registry.items()
                                          if row['status'] == 'planned'}, {row['id'] for row in value})
                continue
            test.assertTrue(same_json_value(value, original[key]),
                            'delivered judgment input differs from its sealed producer value: ' + key)
    for path in judgment_input_paths(role, original['action']):
        with test.subTest(role=role, required_path=path):
            value = resolved_keys if path.split('.')[0] in resolved_keys else delivered
            for part in path.split('.'):
                test.assertIsInstance(value, dict, path)
                test.assertIn(part, value, 'contract judgment coordinate is absent: ' + path)
                value = value[part]
            expected = original
            for part in path.split('.'):
                test.assertIsInstance(expected, dict, path)
                test.assertIn(part, expected, 'sealed source omitted required coordinate: ' + path)
                expected = expected[part]
            test.assertTrue(same_json_value(value, expected), path)
