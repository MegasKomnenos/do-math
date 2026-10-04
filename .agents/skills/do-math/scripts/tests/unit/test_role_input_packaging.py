"""Role input packaging (``context_store.prepare_role_input``, layer 2): direct inputs and references, the canonical submission context, sealed candidate order, continuation, review seats and input overflow.

Most tests give ``prepare_role_input`` a domain-produced state directly. Where
the old tests took the role context from an engine double, the context comes
from the real engine's producers (``core_engine._context``,
``review_engine._prepare_review_context``, both layer 2) on the port fakes over
a real repository (``stored_engine``), so the state the producer reads passed
the storage contract and its artifact reads go to stored bytes.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from do_math.context_store import (build_role_manifest, defer_input_overflow, fit_context, prepare_role_input,
                                   validate_role_manifest)
from support.record_builders import surface_state
from support.state_builders import current_state
from support.fakes.clock import FakeClock
from support.fakes.git_backend import InProcessGit
from support.storage_files import audit_events
from support.storage_records import engine_on, fake_ports, record_store
from support.storage_role_inputs import catalog_opens


def stored_engine(root, instance, runtime):
    """``(engine, head, repository)``: the real engine on the port fakes over the state, stored under the current lifecycle gate."""
    clock, backend = FakeClock(), InProcessGit()
    repository = record_store(root / 'repository', backend=backend, clock=clock)
    runtime = {key: value for key, value in runtime.items() if key != 'status'}
    instance, runtime = current_state({**instance, 'object_format': 'sha1'}, runtime)
    engine, head = engine_on(repository, instance, runtime, workspace=root / 'work', ports=fake_ports(clock, backend))
    return engine, head, repository


def full_surface_state():
    """``surface_state()`` with the empty relation list initialization gives every instance, which the engine's context reads."""
    instance, runtime = surface_state()
    instance['relations'] = []
    return instance, runtime


def role_profile(instance, role):
    return next(p for p in instance['execution_profiles'].values() if p['role'] == role)


class RoleInputTests(unittest.TestCase):
    def test_optional_display_copies_are_referenced_instead_of_reclassified_as_mandatory(self):
        """Original 3-C/B-32 counterexample, across every current role."""
        from do_math import contracts, governance
        from do_math.canonical import canonical_json
        instance, _ = surface_state()
        for role in contracts.ROLES:
            action = {'id': 'AC-optional-copy', 'role': role}
            fixed = {'governance': governance.governance_view(instance), 'action': action}
            context = {**fixed, 'goal': 'g' * 800, 'policies': 'p' * 800,
                       'implementation_documents': [{'content': 'i' * 800}]}
            budget = len(canonical_json(fixed)) + 1000
            with self.subTest(role=role), tempfile.TemporaryDirectory() as directory:
                fitted = fit_context(context, max_bytes=budget, workspace=Path(directory),
                                     mandatory_keys=['governance', 'action'], role=role)
                self.assertIsNone(fitted['overflow'])
                self.assertEqual(fitted['context']['governance'], fixed['governance'])
                self.assertEqual(fitted['context']['action'], action)
                self.assertEqual({row['key'] for row in fitted['reductions']},
                                 {'goal', 'policies', 'implementation_documents'})

    def test_checker_sees_canonical_catalog_beyond_direct_comparison(self):
        """About 0.25 s, over the 0.2 s unit budget: the role input with its submission tools is prepared and sealed for two roles."""
        from support.entry import entry
        _entry = entry()
        from support.record_builders import contract_check, task_contract, task_disposition
        from support.role_answers import assessment, candidate
        from do_math.submission import contract_check_errors
        from do_math.planning import validate_plan_submission
        instance, runtime = surface_state()
        runtime['tasks'] = {identifier: {**task_contract(), 'id': identifier, 'status': status, 'results': []}
            for identifier, status in [('TK-ready', 'planned'), ('TK-completed', 'completed'), ('TK-waiting', 'waiting')]}
        runtime['tasks']['TK-completed']['results'] = [{'execution_id': 'EX-old', 'report': 'preserved'}]
        readers = deepcopy(list(runtime['tasks'].values()))
        readers[1]['results'][0]['local_path'] = 'restored/output.txt'
        returned = {**task_contract(), 'id': 'TK-returned', 'status': 'waiting',
                    'results': [{'execution_id': 'EX-returned', 'report': 'A returned proof sketch'}]}
        for obligation in returned['completion_obligations']:
            obligation['evidence_required'] = ['EX-returned']
        runtime['tasks']['TK-returned'] = returned
        readers.append(deepcopy(returned))
        for role in ('research_plan', 'research_preparation'):
            with self.subTest(role=role), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                profile = role_profile(instance, role)
                fitted = prepare_role_input({'instance_id': instance['id'], 'action': {'id': 'A', 'role': role},
                    'tasks': readers, 'resources': {}, 'knowledge_catalog': [], 'ready_task_ids': ['TK-ready'],
                    'blocked_actions': []},
                    instance=instance, runtime=runtime, role=role, profile=profile,
                    snapshot='a' * 40, workspace=root, activity_id='AC-1', install_submission_tools=True, clock=_entry.ports.clock)
                context = json.loads((root / 'input/submission/context.json').read_bytes())
                tasks = {t['id']: t for t in context['tasks']}
                self.assertEqual(tasks, runtime['tasks'])
                self.assertNotIn('TK-completed', [t['id'] for t in fitted['context']['tasks']])
                plan = {'dispositions': [task_disposition('TK-ready')], 'task_assessments': [assessment(returned)]}
                validate_plan_submission(plan, tasks, ['TK-ready'])
                with self.assertRaisesRegex(ValueError, 'plan must assess every returned task exactly once'):
                    validate_plan_submission({**plan, 'task_assessments': []}, tasks, ['TK-ready'])
                proposal = candidate('new')
                entry = contract_check('new', sibling_boundaries=[{'task_id': 'TK-completed', 'revision': 1,
                    'boundary': 'Use the completed sibling boundary', 'independent_of_next_revision': True}])
                self.assertEqual(contract_check_errors(proposal, entry, [], tasks, set(), set()), [])
                entry['sibling_boundaries'][0]['revision'] = 2
                self.assertTrue(contract_check_errors(proposal, entry, [], tasks, set(), set()))
                for extra in ('TK-completed', 'TK-waiting'):
                    invalid = deepcopy(plan)
                    invalid['dispositions'][0]['parallel_task_ids'] = [extra]
                    with self.assertRaisesRegex(ValueError, 'parallel references must identify distinct other tasks'):
                        validate_plan_submission(invalid, tasks, ['TK-ready'])

    def test_plan_receives_returned_work_separately_from_ready_selection_population(self):
        from support.entry import entry
        _entry = entry()
        instance, runtime = surface_state()
        runtime['tasks'] = {'TK-returned': {'id': 'TK-returned', 'status': 'waiting',
            'question': 'Assess the actual result',
            'results': [{'execution_id': 'EX-1', 'report': 'An actual supplied result'}]}}
        profile = role_profile(instance, 'research_plan')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fitted = prepare_role_input({'instance_id': instance['id'], 'action': {'id': 'A', 'role': 'research_plan'},
                'tasks': deepcopy(list(runtime['tasks'].values())),
                'resources': {}, 'knowledge_catalog': [], 'ready_task_ids': []}, instance=instance, runtime=runtime,
                role='research_plan', profile=profile,
                snapshot='a' * 40, workspace=root, activity_id='AC-1', install_submission_tools=True, clock=_entry.ports.clock)
            direct = fitted['context']
            self.assertEqual(direct['ready_task_ids'], [])
            self.assertEqual(direct['returned_task_ids'], ['TK-returned'])
            # The sealed order orders `tasks`; its seed is manifest evidence, not role context.
            self.assertEqual(fitted['manifest']['candidate_order']['ids'], [])
            self.assertNotIn('candidate_order', direct)
            self.assertEqual([t['id'] for t in direct['tasks']], ['TK-returned'])
            self.assertEqual(direct['tasks'][0]['result_count'], 1)
            validation = json.loads((root / 'input/submission/context.json').read_bytes())
            self.assertEqual(validation['tasks'][0]['results'], runtime['tasks']['TK-returned']['results'])

    def test_impact_review_evidence_is_required_direct_input(self):
        from support.entry import entry
        _entry = entry()
        from do_math.execution_profiles import build_profiles
        instance, runtime = surface_state()
        instance['config']['max_input_bytes'] = 16000
        instance.update(build_profiles(instance['config'], host=_entry.ports.host))
        profile = role_profile(instance, 'maintenance')
        action = {'id': 'AC-impact', 'role': 'maintenance', 'stage': 'impact_review',
                  'input_basis': {'impact_review': {'producer_execution_id': 'EX-producer', 'plans': {}}}}
        evidence = {'request': action['input_basis']['impact_review'],
                    'output': {'explanation': 'original evidence ' * 6000}, 'extensions': {}, 'records': {}}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fitted = prepare_role_input({'action': action, 'impact_review_input': evidence}, instance=instance,
                runtime=runtime, role='maintenance', profile=profile, snapshot='a' * 40, workspace=root / 'oversize',
                activity_id='AC-impact', clock=_entry.ports.clock)
            self.assertIn('impact_review_input', fitted['manifest']['required_direct_keys'])
            self.assertEqual(fitted['context']['impact_review_input'], evidence)
            self.assertIsNotNone(fitted['overflow'])
            self.assertIn('impact_review_input', fitted['overflow']['required_direct_keys'])
            with self.assertRaisesRegex(ValueError, 'impact_review_input'):
                prepare_role_input({'action': action}, instance=instance, runtime=runtime, role='maintenance',
                    profile=profile, snapshot='a' * 40, workspace=root / 'missing', activity_id='AC-impact', clock=_entry.ports.clock)

    def test_compaction_preserves_producer_validation_inputs(self):
        from support.entry import entry
        _entry = entry()
        from do_math import submission
        instance, runtime = surface_state()
        runtime['tasks'] = {'TK-1': {'id': 'TK-1', 'status': 'planned', 'question': 'P',
            'results': [{'execution_id': 'EX-preserved', 'report': 'Detailed result'}],
            'reviews': [{'execution_id': 'EX-review', 'decision': 'revise'}]}}
        profile = role_profile(instance, 'research_preparation')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fitted = prepare_role_input({'instance_id': instance['id'], 'action': {'id': 'A', 'role': 'research_preparation'},
                'tasks': deepcopy(list(runtime['tasks'].values())),
                'resources': {}, 'knowledge_catalog': [], 'blocked_actions': []}, instance=instance, runtime=runtime,
                role='research_preparation', profile=profile,
                snapshot='a' * 40, workspace=root, activity_id='AC-1', install_submission_tools=True,
                max_artifact_bytes=100000, clock=_entry.ports.clock)
            preview = json.loads((root / 'input/submission/context.json').read_bytes())
            self.assertIn('EX-preserved', submission.supplied_reference_ids(preview))
            self.assertIn('EX-review', submission.supplied_reference_ids(preview))
            self.assertEqual(preview['tasks'][0]['results'], runtime['tasks']['TK-1']['results'])
            self.assertNotIn('results', fitted['context']['tasks'][0])

    def test_engine_context_restores_multihop_git_artifact(self):
        """The engine's continuation context restores two stages of stored artifacts from Git.

        The two ended maintenance executions, their output files and
        checkpoints are stored with the artifacts through the storage contract,
        and the engine reloads them. About 0.25 s, over the 0.2 s unit budget:
        the real engine loads and validates the stored state twice.
        """
        from support.entry import entry
        _entry = entry()
        from do_math import activities, execution_lifecycle
        from do_math.execution_profiles import profile_ref
        from do_math.observations import preserve_checkpoint
        raw = b'ancestral evidence'
        ref = 'runtime/artifacts/EX-a/lemma.txt'
        newer = b'latest lemma'
        latest_ref = 'runtime/artifacts/EX-b/lemma.txt'
        keep_ref = 'runtime/artifacts/EX-a/keep.txt'
        artifacts = {ref: raw, latest_ref: newer, keep_ref: b'keep ancestor file',
                     'runtime/artifacts/EX-a/result.json': b'{"stage":"EX-a"}',
                     'runtime/artifacts/EX-b/result.json': b'{"stage":"EX-b"}'}

        def entry(path, artifact_ref):
            data = artifacts[artifact_ref]
            return {'path': path, 'artifact_ref': artifact_ref, 'sha256': hashlib.sha256(data).hexdigest(),
                    'bytes': len(data)}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            engine, head, repository = stored_engine(root, *full_surface_state())
            runtime = deepcopy(engine.runtime)
            activities.open_activity(runtime, activity_id='AT-resume', activity_kind='research',
                                     owner_ref=engine.instance['id'], input_refs=[], opened_at='2026-09-20T00:00:00Z')
            maintenance = profile_ref(role_profile(engine.instance, 'maintenance'))
            outputs = {'EX-a': [entry('lemma.txt', ref), entry('keep.txt', keep_ref)],
                       'EX-b': [entry('lemma.txt', latest_ref)]}
            for identifier, previous in (('EX-a', None), ('EX-b', 'EX-a')):
                execution = execution_lifecycle.create_execution(
                    execution_id=identifier, owner_activity_id='AT-resume', actor_kind='ai', input_manifest=[],
                    profile_ref=maintenance, created_at='2026-09-20T00:00:00Z', continuation_of=previous)
                execution.update(role='maintenance', result_ref='runtime/artifacts/' + identifier + '/result.json',
                                 output_files=outputs[identifier],
                                 action={'id': 'AC-' + identifier, 'role': 'maintenance',
                                         **({'continuation_of': previous} if previous else {})})
                activities.assign_execution(runtime, 'AT-resume', execution)
                execution_lifecycle.transition_execution(execution, 'ended', at='2026-09-20T00:00:02Z',
                    outcome='cancelled', reason='interrupted', disposition='resume')
            runtime['checkpoints'] = {identifier: preserve_checkpoint(
                root / ('checkpoint-' + identifier), artifact_prefix='runtime/artifacts/' + identifier + '/checkpoint',
                max_bytes=4096, clock=_entry.ports.clock)[0] for identifier in ('EX-a', 'EX-b')}
            with repository.writer_lock():
                head = repository.save_with_state(head, engine.instance, runtime, artifacts=artifacts)[0]
            engine._reload()
            self.assertEqual(engine.head, head)
            workspace = root / 'resume'
            context = engine._context({'id': 'AC-c', 'role': 'maintenance', 'continuation_of': 'EX-b'}, workspace,
                                      execution_id='EX-c')
            self.assertEqual([row['path'] for row in context['previous_output_files']], ['keep.txt', 'lemma.txt'])
            self.assertEqual((workspace / 'input/previous-output/lemma.txt').read_bytes(), newer)
            self.assertEqual((workspace / 'input/previous-output/keep.txt').read_bytes(), artifacts[keep_ref])
            self.assertEqual([row['execution_id'] for row in context['continuation_history']], ['EX-a', 'EX-b'])
            for stage in context['continuation_history']:
                source = stage['result_source']
                self.assertEqual(source['snapshot'], engine.head)
                self.assertEqual((workspace / source['local_path']).read_bytes(), artifacts[source['artifact_ref']])
                self.assertEqual(stage['checkpoint'], engine.runtime['checkpoints'][stage['execution_id']])
            self.assertNotEqual(engine.runtime['checkpoints']['EX-a'], engine.runtime['checkpoints']['EX-b'])

    def test_candidate_population_is_compact_profile_bound_and_reproducible(self):
        """About 0.3 s, over the 0.2 s unit budget: the role input with three 100 kB tasks is prepared and sealed twice (first and replay)."""
        from support.entry import entry
        _entry = entry()
        from do_math.context_store import read_source
        from do_math.execution_profiles import boundary_prompt
        instance, runtime = surface_state()
        runtime['tasks'] = {identifier: {'id': identifier, 'status': 'planned', 'question': identifier,
            'revision': 1, 'scope': {'included': ['P'], 'excluded': []},
            'large_detail': 'x' * 100000} for identifier in ['TK-z', 'TK-a', 'TK-m']}
        profile = role_profile(instance, 'research_preparation')
        context = {'action': {'id': 'AC-prep', 'role': 'research_preparation'}, 'resources': {},
                   'tasks': deepcopy(list(runtime['tasks'].values())),
                   'blocked_actions': [], 'pending_revisions': [], 'knowledge_catalog': []}
        with tempfile.TemporaryDirectory() as directory:
            fitted = prepare_role_input(context, instance=instance, runtime=runtime, role='research_preparation',
                profile=profile, snapshot='a' * 40, workspace=Path(directory) / 'first', activity_id='AC-prep', clock=_entry.ports.clock)
            actual = fitted['context']
            self.assertTrue(fitted['prompt'].endswith(boundary_prompt(profile)))
            self.assertNotIn('config', actual)
            self.assertIn('profile_selection', actual)
            self.assertEqual(actual['execution_profile'], profile)
            self.assertEqual({row['id'] for row in actual['tasks']}, set(runtime['tasks']))
            self.assertNotIn('large_detail', actual['tasks'][0])
            for row in actual['tasks']:
                restored = read_source(Path(directory) / 'first', row['source_ref'], limit=200000)
                self.assertEqual(json.loads(restored['bytes']), runtime['tasks'][row['id']])
            order = fitted['manifest']['candidate_order']
            self.assertEqual(order['ids'], [row['id'] for row in actual['tasks']])
            replay = prepare_role_input(context, instance=instance, runtime=runtime, role='research_preparation',
                profile=profile, snapshot='a' * 40, workspace=Path(directory) / 'replay', activity_id='AC-prep',
                candidate_order=order, clock=_entry.ports.clock)
            self.assertEqual(replay['manifest']['candidate_order'], order)
            self.assertEqual(replay['prompt'], fitted['prompt'])

    def test_multihop_restores_latest_file_and_stage_evidence(self):
        from do_math import context_store
        with tempfile.TemporaryDirectory() as directory:
            archive = {}

            def entry(name, body, generation):
                path = 'runtime/artifacts/' + generation + '/' + name
                archive[path] = body
                return {'path': name, 'artifact_ref': path, 'sha256': hashlib.sha256(body).hexdigest(), 'bytes': len(body)}
            runtime = {'executions': {
                'EX-a': {'id': 'EX-a', 'status': 'ended', 'role': 'maintenance', 'owner_activity_id': 'AT-resume',
                         'action': {'role': 'maintenance'},
                         'output_files': [entry('lemma.txt', b'old', 'A'), entry('keep.txt', b'keep', 'A')]},
                'EX-b': {'id': 'EX-b', 'status': 'ended', 'role': 'maintenance', 'owner_activity_id': 'AT-resume',
                         'action': {'role': 'maintenance', 'continuation_of': 'EX-a'},
                         'output_files': [entry('lemma.txt', b'new', 'B')]}}, 'checkpoints': {}}
            for identifier in ('EX-a', 'EX-b'):
                ref = 'runtime/artifacts/' + identifier + '/result.json'
                archive[ref] = json.dumps({'stage': identifier}).encode('utf-8')
                runtime['executions'][identifier]['result_ref'] = ref
                runtime['checkpoints'][identifier] = {'partial': 'checkpoint ' + identifier}
            result = context_store.restore_continuation(runtime, {'role': 'maintenance', 'continuation_of': 'EX-b'},
                Path(directory), snapshot='a' * 40, read_artifact=lambda path: archive[path])
            self.assertEqual([row['execution_id'] for row in result['continuation_history']], ['EX-a', 'EX-b'])
            for stage in result['continuation_history']:
                ref = stage['result_source']
                self.assertEqual((Path(directory) / ref['local_path']).read_bytes(), archive[ref['artifact_ref']])
                self.assertEqual(ref['sha256'], hashlib.sha256(archive[ref['artifact_ref']]).hexdigest())
                self.assertEqual(stage['checkpoint'], runtime['checkpoints'][stage['execution_id']])
            self.assertEqual((Path(directory) / 'input/previous-output/lemma.txt').read_bytes(), b'new')
            self.assertEqual((Path(directory) / 'input/previous-output/keep.txt').read_bytes(), b'keep')
            runtime['executions']['EX-a']['owner_activity_id'] = 'AT-other'
            with self.assertRaisesRegex(ValueError, 'activity'):
                context_store.restore_continuation(runtime, {'role': 'maintenance', 'continuation_of': 'EX-b'},
                    Path(directory) / 'other', snapshot='a' * 40, read_artifact=lambda path: archive[path])
            runtime['executions']['EX-a']['owner_activity_id'] = 'AT-resume'
            runtime['executions']['EX-a']['action']['continuation_of'] = 'EX-b'
            with self.assertRaisesRegex(ValueError, 'cycle'):
                context_store.restore_continuation(runtime, {'role': 'maintenance', 'continuation_of': 'EX-b'},
                    Path(directory) / 'cycle', snapshot='a' * 40, read_artifact=lambda path: archive[path])

    def test_required_direct_action_is_never_replaced_by_reference(self):
        with tempfile.TemporaryDirectory() as d:
            action = {'id': 'A', 'reason': 'essential ' * 1000}
            result = fit_context({'action': action}, max_bytes=500, workspace=Path(d), mandatory_keys=['action'])
            self.assertEqual(result['context']['action'], action)
            self.assertIsNotNone(result['overflow'])

    def test_required_input_overflow_is_structured_and_lossless(self):
        with tempfile.TemporaryDirectory() as directory:
            result = fit_context({"goal": "x" * 1000, "action": {"id": "A"}}, max_bytes=100,
                                 workspace=Path(directory), mandatory_keys=["goal", "action"],
                                 role="research_work", profile_id="P1", activity_id="ACT-1")
        overflow = result["overflow"]
        self.assertEqual(overflow["kind"], "input_overflow")
        self.assertEqual(overflow["role"], "research_work")
        self.assertEqual(overflow["activity_id"], "ACT-1")
        self.assertGreater(overflow["actual_bytes"], overflow["limit_bytes"])
        self.assertEqual(result["context"]["goal"], "x" * 1000)

    def test_role_manifest_distinguishes_required_direct_views_from_references(self):
        context = {"goal": "prove it", "policies": "no external effect", "tasks": [{"id": "T1", "status": "ready"}]}
        with tempfile.TemporaryDirectory() as directory:
            manifest = build_role_manifest(context, workspace=Path(directory), role="research_plan",
                                           direct_keys=["goal", "policies"], reference_keys=["tasks"])
        self.assertEqual([row["key"] for row in manifest["direct"]], ["goal", "policies"])
        self.assertEqual(manifest["references"][0]["key"], "tasks")
        self.assertEqual(manifest["references"][0]["source_ref"]["path"], "input/catalog/tasks.json")
        with self.assertRaisesRegex(ValueError, 'role manifest keys are missing: missing'):
            build_role_manifest(context, workspace=Path(directory), role="research_plan",
                                direct_keys=["missing"], reference_keys=[])

    def test_role_input_uses_current_schema_documents_and_private_resume_bytes(self):
        """The manifest reuses ``fit_context``'s catalog: every catalog file is created once and none is read back.

        ``write_source_catalog`` compares each catalog file it finds before
        reusing it, so a second catalog of this context (the manifest's own)
        would open the written files for reading.
        """
        from support.entry import entry
        _entry = entry()
        from do_math import contracts
        from do_math.context_store import verify_manifest_artifacts
        instance, runtime = surface_state()
        profile = role_profile(instance, 'research_work')
        context = {'action': {'role': 'research_work'}, 'task': {'id': 'TK-1'},
                   'previous_execution': {'id': 'EX-old', 'failure': 'must not disappear'},
                   'resume_checkpoint': {'remaining_work': 'P'},
                   'recent_history': [{'kind': 'note', 'summary': 'x' * 1000}]}
        with tempfile.TemporaryDirectory() as d:
            with audit_events('open') as opened:
                result = prepare_role_input(context, instance=instance, runtime=runtime, role='research_work',
                    profile=profile, snapshot='a' * 40, workspace=Path(d), activity_id='AC-1',
                    artifact_prefix='runtime/artifacts/EX-1', clock=_entry.ports.clock)
            opens = catalog_opens(opened, d)
            names = [name for name, _ in opens]
            self.assertIn('resume_checkpoint.json', names)
            self.assertEqual(len(names), len(set(names)))
            self.assertEqual({mode for _, mode in opens}, {'x'})
            self.assertEqual(result['context']['resume_checkpoint'], context['resume_checkpoint'])
            self.assertTrue(validate_role_manifest(result['manifest']))
            self.assertEqual(result['manifest']['prompt']['sha256'], hashlib.sha256(result['prompt'].encode()).hexdigest())
            self.assertEqual(result['manifest']['output_contract']['id'], contracts.schema_for('research_work')['x-contract-id'])
            self.assertIn('previous_execution', result['manifest']['required_direct_keys'])
            broken = deepcopy(result['manifest'])
            broken['direct'] = [r for r in broken['direct'] if r['key'] != 'resume_checkpoint']
            with self.assertRaisesRegex(ValueError, 'required direct input is missing or duplicated'):
                validate_role_manifest(broken)
            self.assertEqual(verify_manifest_artifacts(result['manifest'], result['artifacts'].__getitem__), [])
            result['artifacts'][result['manifest']['prompt']['artifact_ref']] = b'changed'
            with self.assertRaisesRegex(ValueError, 'input artifact bytes differ: prompt'):
                verify_manifest_artifacts(result['manifest'], result['artifacts'].__getitem__)

    def test_preparation_compares_full_population_and_only_effective_k_summaries(self):
        """The preparation role gets the whole selectable population and only effective K summaries from the real engine's context.

        The task is ``task_contract()`` with the grant, profile and basis a
        stored task must resolve. About 0.6 s, over the 0.2 s unit budget: the
        real engine loads and validates the stored state twice.
        """
        from support.entry import entry
        _entry = entry()
        from support.record_builders import task_contract
        from do_math import governance, knowledge_records
        from do_math.execution_profiles import profile_ref
        instance, runtime = full_surface_state()
        instance.setdefault('governance_sources', {})['GS-task'] = governance.preserve_source(
            'GS-task', 'Authorize the fixture research.', origin='user')
        instance, runtime, _ = governance.apply_decision(instance, runtime, {'kind': 'grant', 'grant': {
            'id': 'GR-1', 'kind': 'local', 'roles': ['research_work'], 'reuse': 'reusable'}}, source_ref='GS-task', clock=_entry.ports.clock)
        value = task_contract()
        value.update(profile_refs=[profile_ref(role_profile(instance, 'research_work'))], basis_refs=['context:goal'])
        runtime['tasks'][value['id']] = value
        waiting = deepcopy(value)
        waiting.update(id='TK-2', status='waiting')
        runtime['tasks']['TK-2'] = waiting
        instance, kid = knowledge_records.create_candidate(instance, {'title': 'Candidate', 'kind': 'conjecture',
            'statement': 'P', 'explanation': 'Unproved', 'summary': 'Do not call this verified',
            'lean_code': '', 'declaration_names': [], 'dependencies': []}, source_ref='SRC', actor_ref='EX-1', clock=_entry.ports.clock)
        profile = role_profile(instance, 'research_preparation')
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            engine, head, repository = stored_engine(root, instance, runtime)
            context = engine._context({'role': 'research_preparation'}, root / 'first')
            result = prepare_role_input(context, instance=engine.instance, runtime=engine.runtime,
                role='research_preparation', profile=profile, snapshot=head, workspace=root / 'first',
                activity_id='AC-1', clock=_entry.ports.clock)
            self.assertEqual([r['id'] for r in result['context']['tasks']], [value['id']])
            self.assertEqual(result['context']['knowledge_catalog'][0]['id'], kid)
            self.assertFalse(result['context']['knowledge_catalog'][0]['usable_as_k'])
            self.assertEqual(result['context']['knowledge_catalog'][0]['verified_summaries'], [])
            self.assertIn('knowledge_catalog', result['manifest']['required_direct_keys'])
            revised_runtime = deepcopy(engine.runtime)
            revised_runtime['queue'] = [{'id': 'A-revise', 'role': 'research_preparation', 'revision_targets': {'TK-2': 1}}]
            head = repository.save_with_state(head, engine.instance, revised_runtime)[0]
            engine._reload()
            context = engine._context({'role': 'research_preparation'}, root / 'revised')
            revised = prepare_role_input(context, instance=engine.instance, runtime=engine.runtime,
                role='research_preparation', profile=profile, snapshot=head, workspace=root / 'revised',
                activity_id='AC-1', clock=_entry.ports.clock)
        self.assertEqual({row['id'] for row in revised['context']['tasks']}, {value['id'], 'TK-2'})
        self.assertEqual([row['id'] for row in revised['context']['tasks']], revised['manifest']['candidate_order']['ids'])

    def test_verified_summary_tracks_identity_use_withdrawal(self):
        """The knowledge catalog's verified summary follows the identity assessment's use, on the real engine's context.

        The theorem candidate carries a verified synthetic formal result and one
        sealed identity review (``review_fixtures.reviewed_candidate``); this
        tests propagation, not Lean. About 0.7 s, over the 0.2 s unit budget:
        the real engine loads and validates the stored state twice.
        """
        from support.entry import entry
        _entry = entry()
        from support.review_inputs import reviewed_candidate
        from do_math.knowledge_records import set_assessment_use
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            base, surface_runtime = full_surface_state()
            reviewed, runtime, kid, assessment = reviewed_candidate(root / 'trust', verified=True)
            instance = {**base, **reviewed}
            runtime = {**{key: value for key, value in surface_runtime.items()
                          if key not in ('activities', 'executions')}, **runtime}
            engine, head, repository = stored_engine(root, instance, runtime)
            profile = role_profile(engine.instance, 'research_preparation')

            def prepare(name):
                context = engine._context({'role': 'research_preparation'}, root / name)
                return prepare_role_input(context, instance=engine.instance, runtime=engine.runtime,
                    role='research_preparation', profile=profile, snapshot=engine.head, workspace=root / name,
                    activity_id='AC-1', clock=_entry.ports.clock)
            row = prepare('first')['context']['knowledge_catalog'][0]
            self.assertEqual(row['id'], kid)
            self.assertTrue(row['usable_as_k'])
            self.assertEqual(row['verified_summaries'][0]['text'], 'Truth')
            self.assertEqual(row['verified_summaries'][0]['basis']['assessment_id'], assessment)
            withdrawn = set_assessment_use(engine.instance, assessment, 'withdrawn', 'fixture withdrawal', 'user')
            repository.save_with_state(head, withdrawn, engine.runtime)
            engine._reload()
            row = prepare('withdrawn')['context']['knowledge_catalog'][0]
            self.assertFalse(row['usable_as_k'])
            self.assertEqual(row['verified_summaries'], [])

    def test_review_input_matches_real_seat_view_and_rejects_peer_injection(self):
        from support.entry import entry
        _entry = entry()
        from do_math.review_cycle import start_review, next_actions, context_for
        instance, runtime = surface_state()
        cycle = start_review({'revision': 1, 'statement': 'P'}, reviewers=2)
        runtime['review_cycles'] = {'RC-1': cycle}
        action = next_actions(cycle)[0]
        context = {'action': {**action, 'id': 'A-review', 'role': 'identity_review', 'review_cycle_id': 'RC-1',
                              'grant_id': 'GR-current-execution'},
                   'role_review': context_for(cycle, action)}
        profile = role_profile(instance, 'identity_review')
        with tempfile.TemporaryDirectory() as d:
            result = prepare_role_input(context, instance=instance, runtime=runtime, role='identity_review',
                profile=profile, snapshot='a' * 40, workspace=Path(d), activity_id='AC-1', clock=_entry.ports.clock)
            self.assertEqual(result['manifest']['private_scope']['slot'], action['slot'])
        context['role_review']['peer_private'] = {'unsealed': 'do not expose'}
        with tempfile.TemporaryDirectory() as d, self.assertRaisesRegex(ValueError, 'seat-scoped'):
            prepare_role_input(context, instance=instance, runtime=runtime, role='identity_review',
                profile=profile, snapshot='a' * 40, workspace=Path(d), activity_id='AC-1', clock=_entry.ports.clock)

    def test_engine_review_context_reaches_role_input_with_bound_identity_and_policy(self):
        """The real engine's review context binds the identity basis and policy into the role input; a forged one is refused.

        The state is the one the old review engine double held
        (``review_candidate_state``) merged with ``surface_state``'s adopted
        charter, stored in a real repository. About 0.3 s, over the 0.2 s unit
        budget: a synthetic trust toolchain is hashed and the real engine loads
        the stored state.
        """
        from support.entry import entry
        _entry = entry()
        from support.state_builders import governance_start
        from support.review_inputs import start_scoped_review
        from support.storage_role_inputs import review_candidate_state
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            review_instance, review_runtime, scope = review_candidate_state(root / 'trust')
            instance, _ = surface_state()
            # The review state starts from governance_start's families; the adopted charter
            # comes from surface_state, so each family keeps the records of both.
            state = {**instance, **review_instance,
                     'config': {**instance['config'], **review_instance['config']},
                     **{family: {**instance[family], **review_instance[family]} for family in governance_start()}}
            engine, head, repository = stored_engine(root, state, review_runtime)
            start_scoped_review(engine, 'K1', scope, None)
            action = {**next(a for a in engine.runtime['queue'] if a['role'] == 'identity_review'),
                      'grant_id': 'GR-current-execution'}
            workspace = root / 'review'
            review = engine._prepare_review_context(action, workspace)['context']
            profile = role_profile(engine.instance, 'identity_review')
            context = {'action': action, 'role_review': review}

            def prepare():
                return prepare_role_input(context, instance=engine.instance, runtime=engine.runtime,
                    role='identity_review', profile=profile, snapshot=engine.head,
                    workspace=workspace, activity_id='AC-1', clock=_entry.ports.clock)
            result = prepare()
            self.assertEqual(result['context']['role_review']['identity_basis'], review['identity_basis'])
            self.assertEqual(result['context']['role_review']['policy_ref'], review['policy_ref'])
            for field in ('identity_basis', 'policy_ref'):
                with self.subTest(field=field):
                    context['role_review'] = {**review, field: 'forged'}
                    with self.assertRaisesRegex(ValueError,
                                                'review direct input differs from authorized seat view: ' + field):
                        prepare()

    def test_submission_context_is_installed_before_single_input_seal(self):
        from support.entry import entry
        _entry = entry()
        instance, runtime = surface_state()
        profile = role_profile(instance, 'research_work')
        context = {'instance_id': instance['id'], 'action': {'id': 'A-work', 'role': 'research_work'},
                   'task': {'id': 'TK-1'}, 'formal_verifier': {'reference': 'tool:lean'}}
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            result = prepare_role_input(context, instance=instance, runtime=runtime, role='research_work',
                profile=profile, snapshot='a' * 40, workspace=root, activity_id='AC-1',
                install_submission_tools=True, max_artifact_bytes=100000,
                artifact_prefix='runtime/artifacts/EX-1', clock=_entry.ports.clock)
            preview = json.loads((root / 'input/submission/context.json').read_bytes())
            self.assertEqual(preview['formal_verifier'], result['context']['formal_verifier'])
            self.assertEqual(preview['governance'], result['context']['governance'])
            self.assertIn('submission_contract', result['manifest']['required_direct_keys'])

    def test_role_overflow_keeps_original_sizes_and_waits_on_activity(self):
        from support.entry import entry
        _entry = entry()
        from do_math import execution_profiles, execution_lifecycle
        instance, runtime = surface_state()
        profile = role_profile(instance, 'research_work')
        body = {k: deepcopy(v) for k, v in profile.items() if k not in {'id', 'sha256'}}
        body['input']['max_input_bytes'] = 200
        profile = execution_profiles.seal_profile(body)
        with tempfile.TemporaryDirectory() as d:
            result = prepare_role_input({'action': {}, 'task': {'id': 'TK', 'evidence': 'x' * 3000}},
                instance=instance, runtime=runtime, role='research_work', profile=profile,
                snapshot='a' * 40, workspace=Path(d), activity_id='AC-1', clock=_entry.ports.clock)
        overflow = result['overflow']
        self.assertGreater(overflow['original_bytes'], 3000)
        self.assertIn('resolution_question', overflow)
        self.assertEqual(defer_input_overflow(runtime, overflow, at='2026-09-20T00:00:01Z', question_ref='Q-1')['status'],
                         'working')
        execution_lifecycle.transition_execution(runtime['executions']['EX-1'], 'ended',
            at='2026-09-20T00:00:02Z', outcome='cancelled', reason='input overflow', disposition='question')
        self.assertEqual(defer_input_overflow(runtime, overflow, at='2026-09-20T00:00:03Z', question_ref='Q-1')['status'],
                         'waiting')
        self.assertEqual(runtime['activities']['AC-1']['status'], 'waiting')

    def test_role_overflow_records_the_context_budget_it_compared(self):
        # Mandatory context below the whole limit still overflows the budget left after
        # the fixed documents, schema and framing; the record states that budget.
        from support.entry import entry
        _entry = entry()
        from do_math import contracts, execution_profiles
        instance, runtime = surface_state()
        profile = role_profile(instance, 'research_work')
        fixed = lambda p: len(execution_profiles.prepare_prompt(contracts.render_prompt('research_work', {}), p).encode('utf-8'))
        from support.provider_probes import ObservedCalls
        for budget in (1000, 2000, 4000):
            body = {k: deepcopy(v) for k, v in profile.items() if k not in {'id', 'sha256'}}
            body['input']['max_input_bytes'] = fixed(profile) + budget
            selected = execution_profiles.seal_profile(body)
            limit = selected['input']['max_input_bytes']
            with self.subTest(context_budget=budget), tempfile.TemporaryDirectory() as d:
                with ObservedCalls(pack=fit_context, capture={'pack': lambda args: args['max_bytes']}) as measured:
                    overflow = prepare_role_input({'action': {}, 'task': {'id': 'TK', 'evidence': '한글' * 3000}},
                        instance=instance, runtime=runtime, role='research_work', profile=selected,
                        snapshot='a' * 40, workspace=Path(d), activity_id='AC-1', clock=_entry.ports.clock)['overflow']
                self.assertEqual(overflow['reason'], 'mandatory_context_exceeds_limit')
                self.assertEqual((overflow['limit_bytes'], overflow['context_budget_bytes']),
                                 (limit, limit - fixed(selected)))
                self.assertEqual(measured.captured('pack'), [overflow['context_budget_bytes']])
                self.assertLess(overflow['context_budget_bytes'], overflow['mandatory_bytes'])
                self.assertLess(overflow['mandatory_bytes'], overflow['limit_bytes'])
                self.assertGreater(overflow['packed_bytes'], limit)

    def test_assessment_only_input_contains_waiting_contract_and_review_history(self):
        from support.entry import entry
        _entry = entry()
        instance, runtime = surface_state()
        task = {'id': 'TK-rejected', 'status': 'waiting', 'question': 'Compare the two methods',
            'reviews': [{'execution_id': 'EX-review', 'decision': 'revision_required'}],
            'model_assessment_history': [{'assessment': {'difficulty': 'high'}}]}
        runtime['tasks'] = {task['id']: task}
        profile = role_profile(instance, 'research_preparation')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fitted = prepare_role_input({'action': {'id': 'A', 'role': 'research_preparation',
                'assessment_targets': {task['id']: {'revision': 1}}}, 'resources': {},
                'tasks': [deepcopy(task)], 'knowledge_catalog': [], 'blocked_actions': []},
                instance=instance, runtime=runtime, role='research_preparation', profile=profile,
                snapshot='a' * 40, workspace=root, activity_id='ACT', install_submission_tools=True,
                max_artifact_bytes=100000, clock=_entry.ports.clock)
            supplied = fitted['context']['tasks']
            self.assertEqual([t['id'] for t in supplied], [task['id']])
            original = json.loads((root / supplied[0]['source_ref']['path']).read_bytes())
            self.assertEqual(original, task)
            checked = json.loads((root / 'input/submission/context.json').read_bytes())
            self.assertEqual(checked['tasks'], [task])


if __name__ == '__main__':
    unittest.main()
