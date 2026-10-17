"""The purpose scenario's answers against the product's contracts (``support.engine_purpose.PurposeResponder``).

The purpose flows (``flows/test_engine_purpose.py``) answer every role with the
legacy ``support.purpose_answers.PurposeAnswers`` answers and the extensions the model
double's responder writes beside them. These tests feed those answers to the
product's pure schema, profile, role-input and assessment functions (layers 1
and 2), so the scenario cannot satisfy a contract falsely.
"""
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

import jsonschema

from do_math import model_policy, submission
from do_math.configuration import DEFAULT_CONFIG
from do_math.context_store import prepare_role_input
from do_math.execution_profiles import build_profiles
from support.purpose_answers import PurposeAnswers, candidate, parse_context
from support.record_builders import surface_state
from support.role_answers import bind_candidates, disposition, planning_model_assessments
from support.engine_purpose import drive


class PurposeDriveTests(unittest.TestCase):
    """Pure loop policy; product storage and owner execution are covered by the purpose flows."""

    def scenario(self, outcome=None, failures=None):
        sim = SimpleNamespace(instance={'goal_status': 'open'},
            runtime={'status': 'running', 'questions': [], 'queue': [], 'executions': {}},
            model=SimpleNamespace(responder=SimpleNamespace(failures=failures or [])), passes=0)
        def step():
            sim.passes += 1
            if outcome:
                outcome(sim)
        sim.step = step
        sim.waiting = lambda: {'status': sim.runtime['status'], 'passes': sim.passes}
        return sim

    def test_an_already_final_predicate_runs_no_more_owner_passes(self):
        sim = self.scenario()
        drive(self, sim, predicate=lambda s: True)
        self.assertEqual(sim.passes, 0)

    def test_goal_and_later_input_checks_are_not_skipped_by_the_default_predicate(self):
        checked = []
        def outcome(sim):
            if sim.passes == 2:
                checked.append('goal audit input checked')
                sim.instance['goal_status'] = 'mathematically_solved'
        sim = self.scenario(outcome)
        drive(self, sim)
        self.assertEqual((sim.passes, checked), (2, ['goal audit input checked']))

    def test_responder_failure_precedes_a_satisfied_predicate(self):
        sim = self.scenario(failures=['exact input refusal'])
        with self.assertRaisesRegex(AssertionError, '^The purpose responder refused its input: exact input refusal$'):
            drive(self, sim, predicate=lambda s: True)
        self.assertEqual(sim.passes, 0)

    def test_stopped_workflow_reports_its_state_before_another_pass(self):
        for status in ('paused', 'closed', 'waiting'):
            with self.subTest(status=status):
                sim = self.scenario()
                sim.runtime['status'] = status
                sim.runtime['questions'] = [{'id': 'Q-stopped'}]
                with self.assertRaisesRegex(AssertionError, 'Workflow stopped before its fixture outcome:.*Q-stopped'):
                    drive(self, sim)
                self.assertEqual(sim.passes, 0)

    def test_the_bound_counts_owner_passes_and_preserves_the_last_state(self):
        sim = self.scenario()
        with self.assertRaisesRegex(AssertionError, 'bounded scenario:.*"passes": 3'):
            drive(self, sim, limit=3)
        self.assertEqual(sim.passes, 3)


class PurposeAnswerContractTests(unittest.TestCase):
    def test_candidate_fixture_chooses_declared_current_profile_editions(self):
        from support.entry import entry
        _entry = entry()
        prior = build_profiles(DEFAULT_CONFIG, host=_entry.ports.host)
        current = build_profiles({**DEFAULT_CONFIG, 'tool_review_window_seconds': 60,
                                  'self_check_response_window_seconds': 5}, host=_entry.ports.host)
        context = {'execution_profiles': list({**prior['execution_profiles'], **current['execution_profiles']}.values()),
                   'role_profile_refs': current['role_profile_refs'], 'grants': [
                       {'id': 'GR-work', 'status': 'active', 'roles': ['research_work']},
                       {'id': 'GR-revoked', 'status': 'revoked', 'roles': ['research_work']},
                       {'id': 'GR-other', 'status': 'active', 'roles': ['research_plan']}]}
        output = {'candidates': [candidate('one exact edition per model')]}
        bind_candidates(output, context)
        self.assertEqual(output['candidates'][0]['profile_refs'], list(current['role_profile_refs']['research_work']))
        self.assertNotEqual(prior['role_profile_refs']['research_work'], current['role_profile_refs']['research_work'])
        self.assertEqual(output['candidates'][0]['authority_refs'], ['GR-work'])
        context['role_profile_refs']['research_work'] = []
        context['grants'] = []
        bind_candidates(output, context)
        self.assertEqual(output['candidates'][0]['profile_refs'], [])
        self.assertEqual(output['candidates'][0]['authority_refs'], [])

    def test_fixture_reads_returned_report_from_the_actual_supplied_task_source(self):
        from support.entry import entry
        _entry = entry()
        instance, runtime = surface_state()
        runtime['tasks'] = {'TK-returned': {'id': 'TK-returned', 'status': 'waiting',
            'results': [{'execution_id': 'EX-work', 'report': 'The supplied 보고서 states the argument.'}],
            'reviews': [{'decision': 'approved'}], 'revision_history': [{'revision': 1}],
            'assessment_history': [{'decision': 'incomplete'}]}}
        profile = next(p for p in instance['execution_profiles'].values() if p['role'] == 'research_plan')
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            fitted = prepare_role_input({'action': {'role': 'research_plan'}, 'resources': {}, 'ready_task_ids': [],
                                         'knowledge_catalog': [], 'tasks': deepcopy(list(runtime['tasks'].values()))},
                                        instance=instance, runtime=runtime, role='research_plan', profile=profile,
                                        snapshot='a' * 40, workspace=workspace, activity_id='AC-1', clock=_entry.ports.clock)
            self.assertNotIn('results', fitted['context']['tasks'][0])
            observed = parse_context(fitted['prompt'], workspace)
            for field in ('results', 'reviews', 'revision_history', 'assessment_history'):
                self.assertEqual(observed['tasks'][0][field], runtime['tasks']['TK-returned'][field])

    def test_context_reader_rejects_damaged_sources_instead_of_answering_from_a_map(self):
        """K-29: the real source reader and the model's context caller share one fixed reference."""
        import hashlib
        import json
        from do_math.context_store import fit_context, read_source
        from support.default_responder import context_from
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            original = {'text': 'The supplied 원문 must remain complete.', 'items': [{'text': 'nested 원값'}]}
            fitted = fit_context({'user_request': original}, max_bytes=512, workspace=workspace,
                                 mandatory_keys=[], map_keys=['user_request'])
            reference = fitted['context']['user_request']['source_ref']
            raw = (workspace / reference['path']).read_bytes()
            self.assertEqual((len(raw), hashlib.sha256(raw).hexdigest()),
                             (reference['bytes'], reference['sha256']))
            def prompt(context):
                return ('--- CANONICAL INPUT CONTEXT ---\n' + json.dumps(context)
                        + '\n--- OUTPUT JSON SCHEMA ---\n{}')
            self.assertEqual(context_from(prompt(fitted['context']), workspace)['user_request'], original)
            self.assertTrue(read_source(workspace, reference, limit=1)['truncated'])
            self.assertFalse(read_source(workspace, reference, limit=max(1, reference['bytes']))['truncated'])
            for damage, reason in (('missing', 'source_missing'), ('content', 'source hash differs from reference'),
                                   ('length', 'source size differs from reference'),
                                   ('path', 'source ref must contain a path')):
                with self.subTest(damage=damage):
                    context = deepcopy(fitted['context'])
                    ref = context['user_request']['source_ref']
                    path = workspace / reference['path']
                    path.write_bytes(raw)
                    if damage == 'missing':
                        path.unlink()
                    elif damage == 'content':
                        path.write_bytes(raw.replace(b'complete', b'changed!'))
                    elif damage == 'length':
                        ref['bytes'] += 1
                    else:
                        ref.pop('path')
                    with self.assertRaisesRegex(AssertionError, reason):
                        context_from(prompt(context), workspace)
            path.write_bytes(raw)
            # A supplied pointer selects the exact nested JSON value, including list indices.
            pointer_ref = {**reference, 'json_pointer': '/items/0/text'}
            self.assertEqual(context_from(prompt({'selected': {'source_ref': pointer_ref}}), workspace)['selected'],
                             original['items'][0]['text'])

    def test_role_answers_refuse_missing_judgment_inputs_at_the_responder(self):
        from support.default_responder import DefaultResponder
        from support.record_builders import task_contract
        responder = DefaultResponder()
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            task = task_contract()
            context = {'action': {'role': 'task_contract_review'}, 'task': task}
            self.assertTrue(responder.respond('task_contract_review', context, workspace)['item_reviews'])
            for field in ('scope', 'completion_obligations'):
                with self.subTest(field=field):
                    damaged = deepcopy(context)
                    damaged['task'][field] = [] if field == 'completion_obligations' else {}
                    with self.assertRaisesRegex(AssertionError, '^The review fixture requires the actual structured contract$'):
                        responder.respond('task_contract_review', damaged, workspace)
            task['results'] = [{'execution_id': 'EX-work', 'report': 'The exact supplied argument.'}]
            context = {'action': {'role': 'research_plan'}, 'tasks': [task],
                       'ready_task_ids': [], 'knowledge_catalog': []}
            output = responder.respond('research_plan', context, workspace)
            self.assertEqual(output['task_assessments'][0]['item_dispositions'][0]['evidence_refs'], ['EX-work'])
            task['results'][0]['report'] = ''
            with self.assertRaisesRegex(AssertionError, '^Completion fixture requires a supplied nonempty report$'):
                responder.respond('research_plan', context, workspace)

    def test_interpretation_check_requires_the_complete_original_text(self):
        from support.default_responder import DefaultResponder
        responder = DefaultResponder()
        original = 'Preserve 공백\n and the entire original request.'
        context = {'action': {'role': 'intent_interpretation', 'stage': 'interpret'},
                   'user_request': {'text': original}, 'governance': {'charter': {'id': 'CH-current'}}}
        output = responder.respond('intent_interpretation', context, None)
        self.assertEqual(output['import_units'][0]['interpretation'], original)
        self.assertEqual(output['import_units'][0]['source_range'], {'start': 0, 'end': len(original)})
        context['action']['stage'] = 'check'
        context['interpretation_to_check'] = {'source': {'text': original}, 'output': output, 'sha256': 'a' * 64}
        self.assertEqual(responder.respond('intent_interpretation', context, None)['decision'], 'approved')
        output['import_units'][0]['interpretation'] = original[:-1]
        with self.assertRaisesRegex(AssertionError, '^This fixture only approves verbatim, complete interpretation$'):
            responder.respond('intent_interpretation', context, None)

    def test_review_scope_requires_explicit_perspectives(self):
        from support.default_responder import DefaultResponder
        from do_math.review_policy import build_review_policy
        from support.entry import entry
        profiles = build_profiles(DEFAULT_CONFIG, host=entry().ports.host)
        profile = next(p for p in profiles['execution_profiles'].values() if p['role'] == 'identity_review')
        policy = build_review_policy(reviewer_count=2, max_rounds=2)
        context = {'action': {'role': 'identity_review', 'stage': 'scope'}, 'execution_profile': profile,
                   'role_review': {'proposal_digest': 'b' * 64, 'review_policy': policy}}
        output = DefaultResponder().respond('identity_review', context, None)
        self.assertEqual([slot['perspective'] for slot in output['scope_assessment']['initial_slots']],
                         ['Statement and proof', 'Explanation and domain'])
        policy['minimum_initial_slots'] = 3
        with self.assertRaisesRegex(AssertionError, '^The explicit fixture only defines two independent perspectives$'):
            DefaultResponder().respond('identity_review', context, None)
        policy['required_perspectives'] = ['Domain', 'Proof', 'Statement']
        output = DefaultResponder().respond('identity_review', context, None)
        self.assertEqual([slot['perspective'] for slot in output['scope_assessment']['initial_slots']],
                         policy['required_perspectives'])

    def test_completed_comparison_population_can_request_audit_from_the_supplied_usable_goal_result(self):
        context = {'action': {'role': 'research_plan'}, 'tasks': [], 'ready_task_ids': [],
                   'knowledge_catalog': [{'id': 'KN-goal', 'title': 'Natural zero identity', 'usable_as_k': True}]}
        self.assertTrue(PurposeAnswers().answer('research_plan', context, None)['goal_audit'])
        context['knowledge_catalog'][0]['usable_as_k'] = False
        self.assertFalse(PurposeAnswers().answer('research_plan', context, None)['goal_audit'])
        context['action'] = {'role': 'research_preparation'}
        for usable in (False, True):
            with self.subTest(usable=usable):
                context['knowledge_catalog'][0]['usable_as_k'] = usable
                self.assertEqual(PurposeAnswers().answer('research_preparation', context, None)['candidates'], [])

    def test_plan_fixture_assesses_exactly_the_selected_task_population(self):
        action = {'role': 'research_plan'}
        output = {'dispositions': [disposition('TK-selected'), disposition('TK-deferred', kind='not_selected')]}
        context = {'tasks': [{'id': 'TK-selected', 'model_assessment': {'difficulty': 'high', 'importance': 'medium'}},
                             {'id': 'TK-deferred', 'model_assessment': {'difficulty': 'low', 'importance': 'low'}}]}
        extensions = {'model_assessments': planning_model_assessments(output, context)}
        jsonschema.validate(extensions, submission.extension_schema(action))
        identified = model_policy.validate_assessments(action, output, extensions,
                                                       {task['id']: task for task in context['tasks']})
        self.assertEqual(set(identified), {'TK-selected'})
        self.assertEqual((identified['TK-selected']['difficulty'], identified['TK-selected']['importance']),
                         ('high', 'medium'))

    def test_plan_fixture_does_not_invent_a_missing_selected_task_assessment(self):
        output = {'dispositions': [{'task_id': 'TK-missing', 'kind': 'selected'}]}
        with self.assertRaisesRegex(AssertionError, '^The planning fixture cannot assess a selected task without its '
                                                    'supplied model assessment$'):
            planning_model_assessments(output, {'tasks': [{'id': 'TK-missing'}]})


if __name__ == '__main__':
    unittest.main()
