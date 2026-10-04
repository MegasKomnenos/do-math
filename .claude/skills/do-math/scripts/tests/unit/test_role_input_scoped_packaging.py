"""Role input packaging (``context_store``): what ``prepare_role_input`` and ``fit_context`` give each role.

These are the layer-2 packaging rules on plain records (``record_fixtures``),
with no engine: which context keys a role scope inlines, maps or blocks, which
snapshot records it may read and cite, how large inputs move to exact sources,
and which formal fields a judgment receives. The engine's context producer and
the installed read tool are tested in ``sim.test_role_input_context`` and
``boundary.test_role_input_snapshot_reach``.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from do_math import contracts, knowledge_records, submission
from do_math.canonical import canonical_json
from do_math.context_store import fit_context, input_class, prepare_role_input, read_source, restore_continuation
from support.knowledge_builders import verified_knowledge
from support.record_builders import surface_state
from support.engine_context import (DERIVED_KEYS, INTENT_DIRECT, JUDGED, OPERATIONAL_DIRECT, PLANNING_DIRECT,
                                    central_check_knowledge, context_state, is_map_entry, prepare)

class InputFittingTests(unittest.TestCase):
    def test_assigned_role_uses_exact_registry_references_even_below_input_limit(self):
        instance, _ = context_state()
        profiles = list(instance['execution_profiles'].values())
        context = {'action': {'role': 'research_work'}, 'task': {'id': 'TK-one', 'question': 'Fixed'},
                   'execution_profiles': profiles, 'role_profile_refs': instance['role_profile_refs'],
                   'tasks': [{'id': 'TK-one', 'question': 'Fixed'}] * 10}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = fit_context(context, max_bytes=10_000_000, workspace=root, mandatory_keys=['task'],
                                 role='research_work', map_keys=[key for key in context
                                                                 if input_class('research_work', key) == 'map'])
            self.assertEqual(set(result['context']['tasks']), {'source_ref', 'total'})
            self.assertIsInstance(result['context']['execution_profiles'], dict,
                                  'The already assigned role need not repeatedly inline the full registry')
            ref = result['context']['execution_profiles']['source_ref']
            self.assertEqual(json.loads(read_source(root, ref)['bytes']), profiles)
            self.assertEqual(result['context']['task'], context['task'])
            self.assertLess(result['actual_bytes'], result['original_bytes'])

    def test_large_task_catalog_moves_to_fixed_source_without_shrinking_selection(self):
        catalog = [{'id': 'TK-past', 'title': 'Earlier result', 'report': 'failure' * 1000}]
        context = {'tasks': [{'id': 'TK-ready'}], 'ready_task_ids': ['TK-ready'],
                   'ongoing_work': [{'execution_id': 'EX-active', 'reason': 'still checking'}],
                   'task_catalog': catalog}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fitted = fit_context(context, max_bytes=1000, workspace=root,
                                 mandatory_keys=['tasks', 'ready_task_ids', 'ongoing_work'],
                                 role='research_plan')
            self.assertIsNone(fitted['overflow'])
            self.assertEqual(fitted['context']['ready_task_ids'], ['TK-ready'])
            self.assertEqual(fitted['context']['ongoing_work'], context['ongoing_work'])
            ref = fitted['context']['task_catalog']['source_ref']
            raw = (root / ref['path']).read_bytes()
            self.assertEqual(submission.load_json(raw), catalog)
            self.assertEqual((ref['sha256'], ref['bytes']), (hashlib.sha256(raw).hexdigest(), len(raw)))

    def test_missing_reader_task_is_an_input_error(self):
        from support.entry import entry
        _entry = entry()
        instance, runtime = surface_state()
        runtime['tasks'] = {'TK': {'id': 'TK', 'status': 'waiting', 'results': [{'report': 'evidence'}]}}
        profile = next(p for p in instance['execution_profiles'].values() if p['role'] == 'research_plan')
        with tempfile.TemporaryDirectory() as directory, self.assertRaisesRegex(ValueError, 'preserve every current task'):
            prepare_role_input({'action': {'role': 'research_plan'}, 'ready_task_ids': [],
                'tasks': [], 'resources': {}, 'knowledge_catalog': []}, instance=instance,
                runtime=runtime, role='research_plan', profile=profile, snapshot='a' * 40,
                workspace=Path(directory), activity_id='AY', clock=_entry.ports.clock)

    def test_missing_population_is_input_error(self):
        from support.entry import entry
        _entry = entry()
        instance, runtime = context_state()
        profile = next(p for p in instance['execution_profiles'].values() if p['role'] == 'research_plan')
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, 'fixed ready_task_ids'):
                prepare_role_input({'action': {'role': 'research_plan'}, 'resources': {}, 'knowledge_catalog': []},
                    instance=instance, runtime=runtime, role='research_plan', profile=profile,
                    snapshot='a' * 40, workspace=Path(directory), activity_id='AC-1', clock=_entry.ports.clock)

    def test_continuation_preserves_older_files_and_latest_replacements(self):
        raw = {"old": b"old proof", "new": b"new proof", "notes": b"old notes", "result-first": b"first", "result-second": b"second"}

        def entry(path, ref):
            return {"path": path, "artifact_ref": ref, "sha256": hashlib.sha256(raw[ref]).hexdigest(), "bytes": len(raw[ref])}
        runtime = {"executions": {
            "EX-first": {"id": "EX-first", "role": "research_work", "status": "ended", "owner_activity_id": "AY-one", "continuation_of": None,
                "result_ref": "result-first", "output_files": [entry("proof.lean", "old"), entry("notes.txt", "notes")]},
            "EX-second": {"id": "EX-second", "role": "research_work", "status": "ended", "owner_activity_id": "AY-one", "continuation_of": "EX-first",
                "result_ref": "result-second", "output_files": [entry("proof.lean", "new")]}}}
        action = {"role": "research_work", "continuation_of": "EX-second"}
        with tempfile.TemporaryDirectory() as temporary:
            context = restore_continuation(runtime, action, Path(temporary), snapshot="fixed", read_artifact=raw.__getitem__)
            self.assertEqual({row["path"]: row["artifact_ref"] for row in context["previous_output_files"]},
                             {"proof.lean": "new", "notes.txt": "notes"})
            self.assertEqual([row["execution_id"] for row in context["continuation_history"]], ["EX-first", "EX-second"])
            self.assertEqual((Path(temporary) / "input/previous-output/proof.lean").read_bytes(), b"new proof")
            runtime["executions"]["EX-first"]["continuation_of"] = "EX-second"
            with self.assertRaisesRegex(ValueError, "cycle"):
                restore_continuation(runtime, action, Path(temporary), snapshot="fixed", read_artifact=raw.__getitem__)


class FormalJudgmentInputTests(unittest.TestCase):
    def assert_judged(self, view, verification):
        self.assertEqual(view, {name: verification[name] for name in JUDGED})

    def assert_environment(self, formal):
        # verified_knowledge's trust environment TE-test allows no axiom.
        self.assertEqual((formal.pop('trust_environment_id'), formal.pop('allowed_axioms')), ('TE-test', []))

    def test_identity_review_proposal_carries_only_the_judged_formal_fields(self):
        from do_math.review_cycle import review_proposal
        instance, _, kid, verification = central_check_knowledge()
        formal = review_proposal(instance, kid)['formal']
        self.assert_environment(formal)
        self.assert_judged(formal, verification)

    def test_judged_formal_view_states_its_environment_allowed_axioms(self):
        # A central check stores no allowed axioms; the judgment compares axioms with its environment's.
        environment = {'id': 'TE-test', 'status': 'active', 'toolchain': {'version': 'test-fixture'},
                       'allowed_axioms': ['propext']}
        instance, _, kid, _ = verified_knowledge(environment)
        verification = instance['formal_results'][instance['knowledge'][kid]['formal_result_id']]['verification']
        self.assertNotIn('allowed_axioms', verification)
        self.assertEqual(knowledge_records.proposal_view(instance, kid)['formal']['allowed_axioms'], ['propext'])

    def test_reviewed_proposal_fixes_the_sources_it_used(self):
        # 계약/동일성-검토.md 39: transcriptions are compared with the originals actually used.
        from do_math.review_cycle import review_proposal
        instance, _, kid, _ = central_check_knowledge()
        record = instance['knowledge'][kid]
        record.update(source_refs=['paper.pdf'], source_basis=[{'name': 'paper.pdf', 'sha256': 'e' * 64}])
        proposal = review_proposal(instance, kid)
        self.assertEqual((proposal['source_refs'], proposal['source_basis']),
                         (record['source_refs'], record['source_basis']))


class RoleInputClassTests(unittest.TestCase):
    def test_every_role_judgment_requirement_names_its_installed_contract(self):
        from do_math.role_input_requirements import ROLE_INPUT_REQUIREMENTS, judgment_input_keys
        assignments = contracts.reading_map()
        self.assertEqual(set(ROLE_INPUT_REQUIREMENTS), set(contracts.ROLES))
        for role, row in ROLE_INPUT_REQUIREMENTS.items():
            with self.subTest(role=role):
                self.assertIn(row['contract'], assignments[role])
                self.assertTrue(row['keys'])
                self.assertEqual(len(row['keys']), len(set(row['keys'])))
                self.assertEqual(judgment_input_keys(role, {'role': role})[:len(row['keys'])],
                                 row['keys'])

    def test_review_stage_requirements_cover_every_current_schema_branch(self):
        import ast
        import inspect
        from do_math import review_cycle
        from do_math.role_input_requirements import REVIEW_STAGE_INPUTS, judgment_input_paths
        tree = ast.parse(inspect.getsource(review_cycle.stage_schema))
        stages = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Compare) and isinstance(node.left, ast.Name) and node.left.id == 'stage':
                self.assertEqual(len(node.comparators), 1)
                right = node.comparators[0]
                candidates = right.elts if isinstance(right, (ast.Tuple, ast.List)) else [right]
                for value in candidates:
                    self.assertIsInstance(value, ast.Constant, 'opaque stage selection needs a declared population')
                    self.assertIsInstance(value.value, str)
                    stages.add(value.value)
        self.assertTrue(stages)
        self.assertEqual(stages, set(REVIEW_STAGE_INPUTS))
        for stage in stages:
            with self.subTest(stage=stage):
                schema = review_cycle.stage_schema(stage)
                self.assertIn('proposal_digest', schema['required'])
                paths = judgment_input_paths('identity_review', {'stage': stage}, context={})
                self.assertTrue({'role_review.' + key for key in REVIEW_STAGE_INPUTS[stage]} <= set(paths))

    def test_role_input_maps_context_its_scope_does_not_inline(self):
        """About 1.2 s, over the 0.2 s unit budget: fourteen scopes each package a full input into files."""
        planning, intent, operational = PLANNING_DIRECT, INTENT_DIRECT, OPERATIONAL_DIRECT
        cases = [  # (action, direct inputs, keys it inlines, keys it receives only as map entries)
            ({'role': 'research_work'}, {'task': {'id': 'TK-1'}},
             {'formal_verifier', 'relations', 'user_inputs', 'external_operations', 'external_rejections', 'open_questions',
              'goal', 'policies', 'decisions', 'relation_validation_source'},
             {'model_policy', 'resources', 'budget_unit', 'academic_requirements', 'academic_phase', 'academic_validation',
              'repetition_holds', 'goal_revision', 'policy_revision', 'events', 'recent_history', 'execution_profiles',
              'role_profile_refs', 'pending_revisions', 'blocked_actions'}),
            ({'role': 'supplemental_research'}, {'task': {'id': 'TK-1'}},
             {'relation_validation_source', 'goal', 'user_inputs', 'external_operations', 'formal_verifier'},
             {'model_policy', 'events', 'recent_history', 'execution_profiles'}),
            ({'role': 'supplemental_research', 'review_cycle_id': 'RC-1'},
             {'review_research': {'sources': []}, 'proposal': {'revision': 1}},
             {'formal_verifier', 'relations', 'decisions'},
             {'relation_validation_source', 'goal', 'policies', 'user_inputs', 'external_operations', 'external_rejections',
              'model_policy', 'execution_profiles'}),
            ({'role': 'operational_review'}, operational,
             {'repetition_holds', 'events', 'recent_history', 'goal_revision', 'policy_revision', 'decisions',
              'user_inputs', 'external_operations', 'blocked_actions'},
             {'model_policy', 'resources', 'budget_unit', 'formal_verifier', 'external_rejections', 'academic_requirements',
              'academic_phase', 'academic_validation', 'pending_revisions', 'execution_profiles',
              'role_profile_refs'}),
            ({'role': 'goal_audit'}, {'eligible_knowledge': []},
             {'academic_requirements', 'academic_phase', 'academic_validation', 'decisions', 'relations', 'goal',
              'policies', 'goal_revision', 'policy_revision', 'external_rejections', 'open_questions'},
             {'formal_verifier', 'model_policy', 'resources', 'execution_profiles', 'role_profile_refs', 'events',
              'user_inputs', 'external_operations', 'repetition_holds'}),
            ({'role': 'task_contract_review'}, {'task': {'id': 'TK-1'}},
             {'model_policy', 'resources', 'budget_unit', 'formal_verifier', 'academic_requirements',
              'academic_phase', 'external_operations', 'external_rejections', 'open_questions'},
             {'execution_profiles', 'role_profile_refs', 'events', 'academic_validation', 'goal_revision',
              'policy_revision', 'repetition_holds', 'user_inputs', 'recent_history'}),
            ({'role': 'intent_interpretation', 'stage': 'interpret'}, intent,
             {'formal_verifier', 'academic_requirements', 'configuration_source', 'goal_revision'},
             {'recent_history', 'user_inputs', 'open_questions', 'events', 'model_policy', 'academic_phase',
              'execution_profiles', 'role_profile_refs'}),
            ({'role': 'intent_interpretation', 'stage': 'check'}, intent,
             {'academic_requirements', 'goal_revision', 'goal', 'relations', 'decisions', 'configuration_source'},
             {'formal_verifier', 'recent_history', 'user_inputs', 'open_questions', 'events', 'model_policy', 'resources',
              'external_operations', 'external_rejections', 'repetition_holds', 'academic_phase', 'academic_validation',
              'execution_profiles', 'role_profile_refs'}),
            ({'role': 'intent_interpretation', 'stage': 'delegation_check', 'delegation_application_id': 'DA-1'}, intent,
             {'decisions'},
             {'configuration_source', 'goal', 'policies', 'goal_revision', 'policy_revision', 'relations',
              'formal_verifier', 'execution_profiles', 'role_profile_refs', 'academic_requirements'}),
            ({'role': 'maintenance'}, {},
             {'resources', 'budget_unit', 'formal_verifier', 'pending_revisions', 'blocked_actions',
              'recent_history', 'user_inputs', 'external_operations', 'external_rejections', 'goal', 'relations', 'decisions'},
             {'model_policy', 'academic_requirements', 'academic_phase', 'academic_validation', 'repetition_holds',
              'goal_revision', 'policy_revision', 'events', 'open_questions', 'execution_profiles', 'role_profile_refs'}),
            ({'role': 'maintenance', 'kind_definition_id': 'KD-1'}, {},
             {'decisions'},
             {'goal', 'policies', 'relations', 'formal_verifier', 'resources', 'budget_unit', 'pending_revisions',
              'blocked_actions', 'user_inputs', 'recent_history', 'external_operations',
              'external_rejections'}),
            ({'role': 'maintenance', 'stage': 'impact_review'}, {'impact_review_input': {}},
             {'goal', 'relations', 'formal_verifier'},
             {'resources', 'pending_revisions', 'blocked_actions', 'user_inputs', 'recent_history', 'external_operations'}),
            ({'role': 'research_plan'}, planning,
             {'model_policy', 'resources', 'academic_validation', 'repetition_holds', 'events', 'goal_revision',
              'pending_revisions', 'blocked_actions', 'external_rejections'},
             {'user_inputs', 'execution_profiles', 'role_profile_refs'}),
            ({'role': 'research_preparation'}, planning,
             {'model_policy', 'resources', 'academic_phase', 'repetition_holds', 'events', 'user_inputs',
              'external_operations'},
             {'academic_validation', 'execution_profiles', 'role_profile_refs'}),
        ]
        for action, direct, inlined, mapped in cases:
            with self.subTest(action=action), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                context = prepare(action, direct, root=root)['context']
                self.assertEqual(inlined - context.keys(), set())
                self.assertEqual({key for key in inlined if is_map_entry(context[key])}, set())
                self.assertEqual(mapped & DERIVED_KEYS & context.keys(), set())
                for key in mapped - DERIVED_KEYS:
                    self.assertTrue(is_map_entry(context.get(key)), key)
                    self.assertEqual((root / context[key]['source_ref']['path']).read_bytes(), canonical_json([]))

    def test_independent_judgment_never_receives_its_blocked_context(self):
        """About 0.3 s, over the 0.2 s unit budget: four scopes each package a full input into files."""
        # 계약/보충-조사.md 23, 공통-실행.md 69 (review lineage); 계약/목표-감사.md 13; 계약/의도-해석.md 69.
        instance, runtime = surface_state()
        runtime['executions']['EX-seat'] = {'id': 'EX-seat', 'role': 'identity_review', 'status': 'ended',
                                            'action': {'role': 'identity_review', 'review_cycle_id': 'RC-1'}}
        private = {'tasks': [{'id': 'TK-private'}], 'recent_history': [], 'open_questions': [], 'question_links': [],
                   'user_inputs': []}
        review_lineage = {'tasks', 'recent_history', 'open_questions', 'question_links'}
        cases = [
            ({'role': 'supplemental_research', 'review_cycle_id': 'RC-1'},
             {'review_research': {'sources': []}, 'proposal': {'revision': 1}}, review_lineage),
            ({'role': 'operational_review', 'target': 'EX-seat'}, OPERATIONAL_DIRECT, review_lineage),
            ({'role': 'goal_audit'}, {'eligible_knowledge': []}, {'recent_history'}),
            ({'role': 'intent_interpretation', 'stage': 'delegation_check', 'delegation_application_id': 'DA-1'},
             INTENT_DIRECT, {'recent_history', 'user_inputs', 'open_questions', 'question_links'}),
        ]
        for action, direct, blocked in cases:
            with self.subTest(action=action), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                fitted = prepare(action, direct, instance=instance, runtime=runtime, extra=private, root=root)
                self.assertEqual(blocked & fitted['context'].keys(), set())
                self.assertEqual(blocked & fitted['validation_context'].keys(), set())
                self.assertEqual({key for key in blocked if (root / 'input/catalog' / (key + '.json')).exists()}, set())
                if 'tasks' in blocked:
                    self.assertNotIn('TK-private', canonical_json(fitted['validation_context']).decode())

    def test_record_index_lists_the_snapshot_records_the_role_may_read(self):
        from support.record_builders import task_contract
        instance, runtime = surface_state()
        runtime['tasks'] = {'TK-1': task_contract()}
        governance_sources = sorted(instance['governance_sources'])
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            readable = prepare({'role': 'maintenance'}, instance=instance, runtime=runtime, root=Path(first))
            judged = prepare({'role': 'task_contract_review', 'target': 'TK-1'}, {'task': task_contract()},
                             instance=instance, runtime=runtime, root=Path(second))
        index = readable['validation_context']['record_index']
        self.assertEqual((index['runtime/executions'], index['runtime/activities'], index['runtime/tasks']),
                         (['EX-1'], ['AC-1'], ['TK-1']))
        self.assertEqual(index['research/governance_sources'], governance_sources)
        # An independent judgment reads the research canon and only the supplied part of the execution ledger.
        index = judged['validation_context']['record_index']
        self.assertEqual({family for family in index if family.startswith('runtime/')}, {'runtime/tasks'})
        self.assertEqual(index['research/governance_sources'], governance_sources)
        for fitted, ledger in ((readable, 'readable'), (judged, 'supplied_only')):
            record_map = fitted['context']['record_map']
            self.assertEqual(record_map['ledger'], ledger)
            self.assertEqual(record_map['families'], {family: len(ids) for family, ids in
                                                      fitted['validation_context']['record_index'].items()})
            self.assertTrue(is_map_entry(fitted['context']['record_index']))

    def test_snapshot_record_outside_the_prompt_passes_the_shared_reference_check(self):
        # A record of the input snapshot is citable although no inline key shows it (R5).
        from support.entry import entry
        _entry = entry()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fitted = prepare({'role': 'maintenance'}, extra={'execution_id': 'EX-check'}, root=root)
            fixed = fitted['validation_context']
            self.assertNotIn('AC-1', canonical_json(fitted['context']).decode())
            output = {'summary': 'Inspect', 'used_sources': ['AC-1'], 'questions': [],
                      'report': 'Inspected the activity record', 'remaining_work': []}
            schema = contracts.schema_for('maintenance')
            self.assertEqual(submission.payload_issues(output, schema, fixed, {}, root, clock=_entry.ports.clock), [])
            output['used_sources'] = ['AC-absent']
            self.assertEqual([row['path'] for row in submission.payload_issues(output, schema, fixed, {}, root, clock=_entry.ports.clock)],
                             ['output/used_sources/0'])

    def test_independent_judgment_cites_the_research_canon_but_not_an_unsupplied_ledger_record(self):
        from support.record_builders import task_contract
        instance, runtime = surface_state()
        runtime['tasks'] = {'TK-1': task_contract()}
        # A published exposition that no key of this input shows.
        instance['expositions'] = {'EP-1': {'id': 'EP-1'}}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixed = prepare({'role': 'task_contract_review', 'target': 'TK-1'}, {'task': task_contract()},
                            instance=instance, runtime=runtime, root=root)['validation_context']
            submission.validate_reference('EP-1', fixed, root)
            submission.validate_reference('TK-1', fixed, root)
            with self.assertRaisesRegex(ValueError, 'reference must identify supplied input, a record of the input '
                                                    'snapshot or a preserved workspace file: EX-1'):
                submission.validate_reference('EX-1', fixed, root)

    def test_contract_reviewer_reads_the_ledger_records_its_contract_names(self):
        # 계약/작업-계약-검토.md 21·43·85: the reviewer reads the records the published contract cites.
        # An academic task's inputs name the goal audit executions of its solution basis.
        from support.record_builders import task_contract
        instance, runtime = surface_state()
        task = {**task_contract(), 'inputs': ['EX-1'], 'basis_refs': ['KN-1', 'AC-1']}
        runtime['tasks'] = {'TK-1': task}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixed = prepare({'role': 'task_contract_review', 'target': 'TK-1'}, {'task': deepcopy(task)},
                            instance=instance, runtime=runtime, root=root)['validation_context']
            index = fixed['record_index']
            self.assertEqual((index.get('runtime/executions'), index.get('runtime/activities')), (['EX-1'], ['AC-1']))
            submission.validate_reference('EX-1', fixed, root)

    def test_review_seat_operational_review_reads_the_evidence_its_input_supplies(self):
        # 공통-실행.md 「독립 판단의 차단」: an independent judgment reads the ledger records and
        # files its input supplies; an operational review supplies them as admissible_basis_refs.
        from do_math.context_store import readable_snapshot_path
        instance, runtime = surface_state()
        runtime['executions']['EX-seat'] = {'id': 'EX-seat', 'role': 'identity_review', 'status': 'ended',
                                            'action': {'role': 'identity_review', 'review_cycle_id': 'RC-1'}}
        runtime['observation_facts'] = {identifier: {'id': identifier} for identifier in ('OF-seat', 'OF-other')}
        runtime['self_check_obligations'] = {'SC-seat': {'id': 'SC-seat', 'execution_id': 'EX-seat'}}
        result = 'runtime/artifacts/BA-seat/result.json'
        direct = {**OPERATIONAL_DIRECT, 'execution_to_review': {'id': 'EX-seat'},
                  'admissible_basis_refs': ['EX-seat', 'OF-seat', 'SC-seat', result]}
        with tempfile.TemporaryDirectory() as directory:
            fixed = prepare({'role': 'operational_review', 'target': 'EX-seat'}, direct, instance=instance,
                            runtime=runtime, root=Path(directory))['validation_context']
        self.assertEqual(fixed['record_map']['ledger'], 'supplied_only')
        index = fixed['record_index']
        self.assertEqual((index.get('runtime/observation_facts'), index.get('runtime/self_check_obligations')),
                         (['OF-seat'], ['SC-seat']))
        self.assertTrue(readable_snapshot_path(fixed, result))
        self.assertFalse(readable_snapshot_path(fixed, 'runtime/artifacts/BA-other/result.json'))

    def test_citable_records_cover_every_readable_work_record(self):
        # Task inputs and completion evidence may name any record the role can read (공통-실행.md 41).
        for action, direct in (({'role': 'research_preparation'}, PLANNING_DIRECT),
                               ({'role': 'operational_review', 'target': 'EX-1'}, OPERATIONAL_DIRECT)):
            with self.subTest(action=action), tempfile.TemporaryDirectory() as directory:
                fixed = prepare(action, direct, root=Path(directory))['validation_context']
                self.assertTrue({'EX-1', 'AC-1'} <= set(fixed['supplied_record_ids']), fixed['supplied_record_ids'])

    def test_citable_record_list_reaches_the_prompt_as_a_map_entry(self):
        """About 0.25 s, over the 0.2 s unit budget: two scopes each package a full input into files."""
        # supplied_record_ids grows with the snapshot's records like record_index, so the prompt carries
        # its map entry while the checker reads the whole list (공통-실행.md 「기록 지도와 읽기 도구」).
        for action, direct in (({'role': 'research_preparation'}, PLANNING_DIRECT),
                               ({'role': 'operational_review', 'target': 'EX-1'}, OPERATIONAL_DIRECT)):
            with self.subTest(action=action), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                fitted = prepare(action, direct, root=root)
                mapped = fitted['context']['supplied_record_ids']
                self.assertTrue(is_map_entry(mapped), mapped)
                self.assertEqual(json.loads((root / mapped['source_ref']['path']).read_bytes()),
                                 fitted['validation_context']['supplied_record_ids'])

    def test_scope_follows_the_role_the_input_is_prepared_for(self):
        # prepare_role_input vouches for its role (the selected profile's role), not for action fields.
        from support.entry import entry
        _entry = entry()
        planning = {'tasks': [], 'resources': {}, 'knowledge_catalog': [], 'ready_task_ids': [], 'blocked_actions': []}
        instance, runtime = surface_state()
        profile = next(p for p in instance['execution_profiles'].values() if p['role'] == 'research_plan')
        with tempfile.TemporaryDirectory() as directory:
            context = prepare_role_input({'action': {'id': 'AC-plan'}, 'model_policy': {}, **planning},
                instance=instance, runtime=runtime, role='research_plan', profile=profile, snapshot='a' * 40,
                workspace=Path(directory), activity_id='AC-1', clock=_entry.ports.clock)['context']
        self.assertEqual({'model_policy', 'configuration_source'} - context.keys(), set())

    def test_control_binding_reaches_the_checker_context_but_not_the_prompt(self):
        """About 0.25 s, over the 0.2 s unit budget: it installs the submission and read tools it inspects."""
        from support.entry import entry
        _entry = entry()
        instance, runtime = surface_state()
        profile = next(p for p in instance['execution_profiles'].values() if p['role'] == 'research_work')
        binding = {'execution_id': 'EX-work', 'grant_id': 'GR-1', 'capability': 'secret-capability'}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fitted = prepare_role_input({'action': {'id': 'AC-work', 'role': 'research_work'}, 'task': {'id': 'TK-1'},
                'control_binding': binding}, instance=instance, runtime=runtime, role='research_work', profile=profile,
                snapshot='a' * 40, workspace=root, activity_id='AC-1', install_submission_tools=True,
                max_artifact_bytes=100000, clock=_entry.ports.clock)
            checker = json.loads((root / 'input/submission/context.json').read_bytes())
        self.assertEqual(checker['control_binding'], binding)
        self.assertNotIn('control_binding', fitted['context'])
        self.assertNotIn('secret-capability', fitted['prompt'])


if __name__ == '__main__':
    unittest.main()
