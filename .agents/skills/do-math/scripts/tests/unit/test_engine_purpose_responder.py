"""The purpose scenario's answers against the product's contracts (``support.engine_purpose.PurposeResponder``).

The purpose flows (``flows/test_engine_purpose.py``) answer every role with the
legacy ``support.purpose_answers.PurposeAnswers`` answers and the extensions the model
double's responder writes beside them. These tests feed those answers to the
product's pure schema, profile, role-input and assessment functions (layers 1
and 2), so the scenario cannot satisfy a contract falsely.
"""
from copy import deepcopy
from pathlib import Path
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


class PurposeAnswerContractTests(unittest.TestCase):
    def test_candidate_fixture_chooses_declared_current_profile_editions(self):
        from support.entry import entry
        _entry = entry()
        prior = build_profiles(DEFAULT_CONFIG, host=_entry.ports.host)
        current = build_profiles({**DEFAULT_CONFIG, 'tool_review_window_seconds': 60,
                                  'self_check_response_window_seconds': 5}, host=_entry.ports.host)
        context = {'execution_profiles': list({**prior['execution_profiles'], **current['execution_profiles']}.values()),
                   'role_profile_refs': current['role_profile_refs'], 'grants': []}
        output = {'candidates': [candidate('one exact edition per model')]}
        bind_candidates(output, context)
        self.assertEqual(output['candidates'][0]['profile_refs'], list(current['role_profile_refs']['research_work']))
        self.assertNotEqual(prior['role_profile_refs']['research_work'], current['role_profile_refs']['research_work'])

    def test_fixture_reads_returned_report_from_the_actual_supplied_task_source(self):
        from support.entry import entry
        _entry = entry()
        instance, runtime = surface_state()
        runtime['tasks'] = {'TK-returned': {'id': 'TK-returned', 'status': 'waiting',
            'results': [{'execution_id': 'EX-work', 'report': 'The supplied report states the argument.'}]}}
        profile = next(p for p in instance['execution_profiles'].values() if p['role'] == 'research_plan')
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            fitted = prepare_role_input({'action': {'role': 'research_plan'}, 'resources': {}, 'ready_task_ids': [],
                                         'knowledge_catalog': [], 'tasks': deepcopy(list(runtime['tasks'].values()))},
                                        instance=instance, runtime=runtime, role='research_plan', profile=profile,
                                        snapshot='a' * 40, workspace=workspace, activity_id='AC-1', clock=_entry.ports.clock)
            self.assertNotIn('results', fitted['context']['tasks'][0])
            observed = parse_context(fitted['prompt'], workspace)
            self.assertEqual(observed['tasks'][0]['results'], runtime['tasks']['TK-returned']['results'])

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
