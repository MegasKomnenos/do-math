"""Check semantic requirement rows against a real prepared role input.

The actual engine and packager produce both arguments. This observer does not
change a context, fill a missing field, or replace any product method.
"""
from contextlib import contextmanager
import json

from do_math.context_store import prepare_role_input, read_source
from do_math.role_input_requirements import (judgment_input_keys, judgment_input_paths,
                                           judgment_source_lists, judgment_source_refs)
from do_math.canonical import same_json_value


def assert_judgment_inputs(test, role, prepared, workspace, *, producer_context):
    original = prepared['validation_context']
    delivered = prepared['context']
    manifest = prepared['manifest']
    test.assertEqual(manifest['snapshot'], original['snapshot'])
    catalog = {row['key']: {k: v for k, v in row.items() if k != 'key'}
               for row in manifest['catalog']}
    resolved_keys = {}
    paths = judgment_input_paths(role, original['action'], context=original)
    keys = tuple(dict.fromkeys((*judgment_input_keys(role, original['action']),
                               *(path.split('.')[0].removesuffix('[]') for path in paths))))
    for key in keys:
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
    for path in paths:
        with test.subTest(role=role, required_path=path):
            value = required_path_values(test, resolved_keys, path)
            expected = required_path_values(test, original, path)
            test.assertTrue(same_json_value(value, expected), path)
    for path in judgment_source_lists(role, original['action'], context=original):
        sources, = required_path_values(test, resolved_keys, path)
        test.assertIsInstance(sources, list, path)
        for ref in sources:
            assert_judgment_source(test, role, path, ref, workspace)
    for path in judgment_source_refs(role, original['action'], context=original):
        ref, = required_path_values(test, resolved_keys, path)
        if ref is not None:
            assert_judgment_source(test, role, path, ref, workspace)


def required_path_values(test, root, path):
    """Read required coordinates, sweeping every member at declared [] steps."""
    values = [root]
    for part in path.split('.'):
        many = part.endswith('[]')
        key = part[:-2] if many else part
        following = []
        for value in values:
            test.assertIsInstance(value, dict, path)
            test.assertIn(key, value, 'contract judgment coordinate is absent: ' + path)
            item = value[key]
            if many:
                test.assertIsInstance(item, list, path)
                following.extend(item)
            else:
                following.append(item)
        values = following
    return values


def assert_judgment_source(test, role, path, ref, workspace):
    with test.subTest(role=role, source_path=path, source=ref):
        if 'restoration_error' in ref:
            test.assertNotIn('local_path', ref, 'unverified evidence must not be materialized')
            test.assertTrue({'error_type', 'reason', 'observed_sha256', 'observed_bytes'} <= ref['restoration_error'].keys())
            return
        test.assertIn('local_path', ref)
        test.assertIn('sha256', ref)
        resolved = read_source(workspace, {**ref, 'path': ref['local_path']},
                               limit=ref['bytes'] if ref.get('bytes') else 2 ** 63 - 1)
        test.assertEqual(resolved['status'], 'ok')
        test.assertFalse(resolved['truncated'])


@contextmanager
def observe_judgment_inputs(test):
    """Validate actual owner preparations during an existing flow, without replay.

    Checks run at the packager's return while its sources still exist. Source
    arguments stay owned by that synchronous call; only small role/action
    coordinates survive in the yielded observations. Product calls and return
    values are unchanged. A subtest records a failure even if the owner later
    classifies the preparation as failed.
    """
    from copy import deepcopy
    from support.provider_probes import ObservedCalls
    from support.storage_probes import Returns

    def capture(arguments):
        return arguments['role'], arguments['context'], arguments['workspace']

    with ObservedCalls(prepared=prepare_role_input, capture={'prepared': capture}) as starts:
        def checked(value):
            role, source, workspace = starts.captured('prepared')[-1]
            with test.subTest(prepared_role=role, action=source['action']):
                assert_judgment_inputs(test, role, value, workspace, producer_context=source)
            return {'role': role, 'action': deepcopy(source['action']),
                    'interpretation_stage': value['validation_context'].get('interpretation_stage')}

        with Returns(prepare_role_input, snapshot=checked) as completed:
            yield completed.snapshots
        test.assertEqual(len(starts.calls['prepared']), len(completed.snapshots),
                         'every observed preparation must return an input that the requirement checker examined')


def assert_recovery_judgment_input(test, scene, execution, *, source_snapshot):
    """The separate operator recovery CLI's actual prompt and preserved sources."""
    import hashlib
    from pathlib import Path
    from do_math.execution_profiles import boundary_prompt, resolve_profile

    prompt = scene.cli.calls[-1]['prompt']
    encoded = prompt[prompt.index('\n') + 1:]
    value, end = json.JSONDecoder().raw_decode(encoded)
    profile = resolve_profile(scene.load()[1]['execution_profiles'], execution['execution_profile_ref'])
    test.assertEqual(encoded[end:], boundary_prompt(profile))
    test.assertEqual(set(value), {'failure', 'failure_inputs', 'installation', 'repository',
                                 'instance', 'execution_id', 'profile_ref'})
    test.assertEqual(value['execution_id'], execution['id'])
    test.assertEqual(value['profile_ref'], execution['execution_profile_ref'])
    test.assertTrue(same_json_value(value['failure'], execution['input_manifest']['failure']))
    test.assertEqual(value['installation'], str(scene.installation))
    test.assertEqual(value['repository'], str(scene.sim.repository))
    test.assertEqual(value['instance'], scene.sim.instance_id)
    test.assertEqual([row['artifact_ref'] for row in value['failure_inputs']],
                     execution['input_manifest']['failure'].get('evidence_refs', []))
    for source in value['failure_inputs']:
        raw = Path(source['local_path']).read_bytes()
        test.assertEqual(hashlib.sha256(raw).hexdigest(), source['sha256'])
        test.assertEqual(raw, scene.sim.engine.store.read(source['artifact_ref'], source_snapshot))
    return value


def assert_missing_judgment_inputs_rejected(test, role, prepared, workspace, *, producer_context):
    """Remove each required root from both views; collect the real checker's failures.

    The prepared input is a real producer result, shared read-only below its
    top-level dictionaries. A unittest result preserves subtest failures; an
    assertRaises wrapper would miss those because unittest records them itself.
    """
    original = prepared['validation_context']
    paths = judgment_input_paths(role, original['action'], context=original)
    required = tuple(dict.fromkeys((*judgment_input_keys(role, original['action']),
                                  *(path.split('.')[0].removesuffix('[]') for path in paths))))
    for key in required:
        damaged = {**prepared, 'context': dict(prepared['context']),
                   'validation_context': dict(original)}
        del damaged['context'][key]
        del damaged['validation_context'][key]

        result = judgment_check_result(role, damaged, workspace, producer_context=producer_context)
        with test.subTest(role=role, removed_requirement=key):
            test.assertFalse(result.wasSuccessful(), 'missing requirement passed: ' + key)
            reasons = '\n'.join(reason for _, reason in (*result.failures, *result.errors))
            test.assertIn(key, reasons, 'failure must identify the missing judgment input')


def judgment_check_result(role, prepared, workspace, *, producer_context):
    """Collect both assertions and unittest subtest failures from the real checker."""
    import unittest

    class InputCheck(unittest.TestCase):
        def runTest(self):
            assert_judgment_inputs(self, role, prepared, workspace, producer_context=producer_context)

    result = unittest.TestResult()
    InputCheck().run(result)
    return result


def assert_unreadable_requirement_rejected(test, role, prepared, workspace, *, producer_context):
    """A real mandatory catalog file must fail when absent or changed at the same size."""
    from pathlib import Path

    mapped = [(key, prepared['context'][key]['source_ref'])
              for key in judgment_input_keys(role, prepared['validation_context']['action'])
              if isinstance(prepared['context'][key], dict)
              and set(prepared['context'][key]) == {'source_ref', 'total'}]
    test.assertTrue(mapped, 'this real role input must exercise a required mapped source')
    key, ref = mapped[0]
    path = Path(workspace) / ref['path']
    test.assertTrue(path.resolve().is_relative_to(Path(workspace).resolve()))
    original = path.read_bytes()
    test.assertTrue(original)
    try:
        path.unlink()
        result = judgment_check_result(role, prepared, workspace, producer_context=producer_context)
        test.assertFalse(result.wasSuccessful(), 'missing mandatory source passed: ' + key)
        path.write_bytes(b'X' + original[1:])
        test.assertEqual(path.stat().st_size, len(original))
        result = judgment_check_result(role, prepared, workspace, producer_context=producer_context)
        test.assertFalse(result.wasSuccessful(), 'same-size source corruption passed: ' + key)
    finally:
        path.write_bytes(original)
    test.assertEqual(path.read_bytes(), original)
