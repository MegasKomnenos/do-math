"""Input overflow recovery through public controls and model calls on the Sim (``core_engine``, ``call_engine``).

The two ways out of an input overflow: the user's public retry after raising
the limit, and the planner's choice of an offered larger profile. Every step is
a public control or an owner pass on the Sim; model calls run through the
worker and the model double (``support.scheduling_model`` records every call and
lets a test act inside one). The legacy tests drove the CLI on the synthetic
active state and replaced the model runner with ``DefaultResponder`` or a local
runner in real Windows Jobs; the CLI's ``configure``, ``request --retry-action``
and ``close`` send exactly the controls used here, and
``boundary/test_engine_cli.py`` runs that command surface.
"""
from copy import deepcopy
import json
import re
import unittest

from do_math import execution_profiles, planning
from support.default_responder import DefaultResponder
from support.engine_lifecycle import applied, approve, clear_work, research_grant, task
from support.engine_overflow import apply_limit, gate_closes_before_admission, held, overflowed_sim, retry
from support.scheduling_model import scenario_model
from support.sim import Sim

CLOSED = 'closed/completed instance cannot accept new research activities'


def setUpModule():
    overflowed_sim()  # build the held request's template before the first test, so no test pays for it


def question(sim, identifier):
    return next(q for q in sim.runtime['question_links'] if q['id'] == identifier)


def maintenance_calls(model):
    return [call for call in model.calls if call['role'] == 'maintenance']


class InputRecoveryPublicTests(unittest.TestCase):
    def test_public_retry_replays_refails_resolves_and_rejects_after_close(self):
        """About 4 s: a restored held request, three owner passes and one maintenance call through the worker."""
        sim = overflowed_sim()
        model = scenario_model(sim, DefaultResponder())
        # The copied state is the first overflow: a public configure (limit 1),
        # a public maintenance request and one owner pass.
        self.assertEqual(len(sim.runtime.get('input_overflows', [])), 1, sim.waiting())
        action_id, waiting = held(sim)
        first_question_id = waiting['question_id']
        first_question = question(sim, first_question_id)
        self.assertEqual(first_question['origin_field'], 'resolution_question/question')
        self.assertIsNotNone(first_question['origin_execution_id'])
        status = sim.engine.status()  # the CLI's status --json is this report
        public_question = next(q for q in status['question_links'] if q['id'] == first_question_id)
        self.assertEqual(public_question['text'], waiting['detail']['resolution_question']['question'])
        self.assertNotIn('source_status', public_question)

        first_retry = retry(sim, action_id, 'UC-retry-same-limit')
        replay = retry(sim, action_id, 'UC-retry-same-limit')
        self.assertTrue(first_retry['accepted'])
        self.assertTrue(replay['replayed'])
        sim.step()
        runtime = sim.runtime
        self.assertEqual(len(runtime['input_overflows']), 2)
        self.assertEqual(sum(row.get('kind') == 'input_overflow_retry_started'
                             and row.get('request_id') == 'UC-retry-same-limit' for row in runtime['history']), 1)
        self.assertTrue(any(row.get('kind') == 'input_overflow_retry_failed' for row in runtime['history']))
        self.assertEqual(question(sim, first_question_id)['status'], 'resolved')
        second_question_id = runtime['waiting_actions'][action_id]['question_id']
        self.assertNotEqual(second_question_id, first_question_id)
        self.assertEqual(question(sim, second_question_id)['status'], 'open')
        self.assertEqual(maintenance_calls(model), [], 'an overflowing request never reaches the model')

        apply_limit(sim, 3_000_000, 'UC-limit-large')
        current_profiles = deepcopy(sim.instance['role_profile_refs']['maintenance'])
        self.assertTrue(retry(sim, action_id, 'UC-retry-large')['accepted'])
        sim.step()
        runtime = sim.runtime
        self.assertNotIn(action_id, runtime['waiting_actions'])
        self.assertEqual(question(sim, second_question_id)['status'], 'resolved')
        resolved = next(row for row in runtime['history'] if row.get('kind') == 'input_overflow_retry_resolved')
        self.assertIn(resolved['profile_ref'], current_profiles)
        self.assertLessEqual(resolved['prompt_bytes'], resolved['limit_bytes'])
        self.assertEqual(len(runtime['input_overflows']), 2, 'successful admission must preserve both historical failures')
        self.assertEqual([call['action']['id'] for call in maintenance_calls(model)], [action_id])

        applied(sim, 'close', text='Boundary test complete')
        with self.assertRaisesRegex(ValueError, '^' + re.escape(CLOSED) + '$'):
            retry(sim, action_id, 'UC-retry-closed')
        sim.restart()
        self.assertEqual(sim.runtime['status'], 'closed')
        self.assertEqual(sim.runtime['queue'], [])

    def test_resolved_retry_marker_survives_provider_deferral_and_repreparation(self):
        """About 4 s: a restored held request, a deferred pass and one maintenance call through the worker."""
        sim = overflowed_sim()
        model = scenario_model(sim, DefaultResponder())
        action_id, waiting = held(sim)
        question_id = waiting['question_id']
        apply_limit(sim, 3_000_000, 'UC-marker-limit-large')
        retry(sim, action_id, 'UC-marker-retry')
        # While the retried request's input is prepared, the provider refuses new calls for a while:
        # a usage limit an earlier Codex call reported closes its gate before the admission.
        with gate_closes_before_admission(sim, 'codex') as gate:
            sim.step()
        self.assertIsInstance(gate['retry_at'], int)
        first = question(sim, question_id)
        first_history = deepcopy(first['resolution_history'])
        first_resolution_ref = first['resolution_ref']
        deferred = next(row for row in sim.runtime['queue'] if row['id'] == action_id)
        self.assertEqual(deferred['input_overflow_retry']['state'], 'resolved')
        self.assertEqual(maintenance_calls(model), [], 'the deferred request did not start')

        sim.advance(gate['retry_at'] - sim.clock.wall_ns() / 1_000_000_000 + 1)  # the gate's retry time passes
        sim.step()
        after = question(sim, question_id)
        self.assertEqual(after['resolution_ref'], first_resolution_ref)
        self.assertEqual(after['resolution_history'], first_history)
        self.assertEqual(sum(row.get('kind') == 'input_overflow_retry_resolved'
                             and row.get('request_id') == 'UC-marker-retry' for row in sim.runtime['history']), 1)
        executions = [row for row in sim.runtime['executions'].values() if row.get('action', {}).get('id') == action_id]
        self.assertTrue(any(row.get('outcome') == 'start_failed'
                            and row.get('result_disposition', {}).get('kind') == 'provider_limit'
                            and any(step.get('reason') == 'provider admission deferred'
                                    for step in row.get('transitions', []))
                            for row in executions), executions)
        self.assertTrue(any(row.get('outcome') == 'output_accepted' for row in executions))
        self.assertEqual([call['action']['id'] for call in maintenance_calls(model)], [action_id])


class OverflowGitConnection(unittest.TestCase):
    def test_plan_choice_repackages_original_work_and_reaches_runner(self):
        """A 720 KB input, profile recovery, real work and an independent incomplete assessment."""
        from support.cross_contracts import assert_call_records
        from support.model import Answer
        sim = Sim.activated()
        clear_work(sim)
        engine = sim.engine
        base = execution_profiles.resolve_profile(engine.instance['execution_profiles'],
                                                  engine.instance['role_profile_refs']['research_work'][-1])
        large = deepcopy(base)
        large['input']['max_input_bytes'] = 2000000
        large['observation']['settings'].update(tool_review_window_seconds=60, self_check_response_window_seconds=5)
        large = execution_profiles.seal_profile(large)
        small = deepcopy(large)
        small['input']['max_input_bytes'] = 500000
        small = execution_profiles.seal_profile(small)
        reference = execution_profiles.profile_ref(large)
        for profile in (small, large):
            engine.instance['execution_profiles'][profile['id']] = profile
            # The capability evidence the probe records, from the fake host's observation of this profile's CLI.
            evidence = execution_profiles.capability_evidence(profile, sim.ports.host.cli_describe(profile),
                                                              observed_at=engine.runtime['last_observed_utc'])
            engine.instance.setdefault('capability_evidence', {})[evidence['id']] = evidence
        row = task(engine, 'TK-1', approved=False)
        row.update(title='Fixed input recovery', status='active', work_class='nonformal', basis_refs=[],
                   profile_refs=[execution_profiles.profile_ref(small), reference],
                   model_assessment={'difficulty': 'high', 'importance': 'high', 'reason': 'Preserve the assigned requirement'},
                   question='Inspect the following fixed evidence: ' + 'required evidence ' * 40000, results=[])
        approve(engine, row)
        action = {'id': 'AC-overflow-work', 'role': 'research_work', 'target': row['id'],
                  'profile_ref': execution_profiles.profile_ref(small), 'grant_id': research_grant(engine),
                  'selected_contract_sha256': planning.contract_hash(row), 'model_assessment': deepcopy(row['model_assessment'])}
        engine.runtime['queue'] = [action]
        engine._save()
        model = scenario_model(sim, DefaultResponder())

        def choose(context, workspace):
            if not context['input_overflow_requests']:
                return
            request = context['input_overflow_requests'][0]
            extension = {'input_overflow_resolutions': [{'action_id': request['action_id'],
                'profile_ref': request['allowed_profile_refs'][0], 'reason': 'The complete input fits this allowed profile'}]}
            (workspace / 'activity-extensions.json').write_text(json.dumps(extension), encoding='utf-8')
        model.during('research_plan', choose)

        sim.step()
        self.assertEqual(model.calls, [])
        waiting = sim.runtime['waiting_actions'][action['id']]
        self.assertEqual(waiting['next_owner'], 'research_plan', waiting)
        owner, question_id = waiting['action']['owner_activity_id'], waiting['question_id']
        request, = [a for a in sim.runtime['queue'] if a.get('overflow_activity_id') == owner]
        self.assertEqual(request['input_overflow'], waiting['detail'])
        self.assertEqual(assert_call_records(self, sim)['research_plan'], 0)
        sim.step()
        self.assertEqual([call['role'] for call in model.calls], ['research_plan'])
        first_plan, = [e for e in sim.runtime['executions'].values() if e['action']['id'] == request['id']]
        self.assertEqual(first_plan['outcome'], 'output_accepted', first_plan.get('error'))
        self.assertEqual(assert_call_records(self, sim)['research_plan'], 1)
        retried = next(a for a in sim.runtime['queue'] if a['id'] == action['id'])
        self.assertEqual(retried['profile_ref'], reference)
        self.assertEqual(retried['owner_activity_id'], owner)
        self.assertEqual(question(sim, question_id)['status'], 'open')
        sim.step()
        self.assertEqual([call['role'] for call in model.calls], ['research_plan', 'research_work'])
        self.assertEqual(model.calls[-1]['action']['profile_ref'], reference)
        self.assertEqual(model.calls[-1]['action']['owner_activity_id'], owner)
        self.assertEqual(question(sim, question_id)['status'], 'resolved')
        attempts = [e for e in sim.runtime['executions'].values() if e.get('action', {}).get('id') == action['id']]
        self.assertEqual(len(attempts), 2)
        self.assertEqual(len({e['id'] for e in attempts}), 2)
        self.assertTrue(any(e.get('outcome') == 'output_accepted' for e in attempts))

        accepted, = [e for e in attempts if e.get('outcome') == 'output_accepted']
        assessment_request, = [a for a in sim.runtime['queue']
                               if accepted['id'] in a.get('receipt_refs', [])]
        self.assertIn('Assess accepted research report and knowledge', assessment_request['reason'])
        imported = [kid for kid, record in sim.instance['knowledge'].items()
                    if record.get('producer_execution') == accepted['id']]
        self.assertTrue(imported)
        self.assertCountEqual(assessment_request['evidence_refs'], imported)
        def inspect_remaining(out, context):
            out['goal_audit'] = False
            for result in out['task_assessments']:
                current = next(t for t in context['tasks'] if t['id'] == result['task_id'])
                from support.role_answers import assessment_awaiting_required_evidence
                result.update(assessment_awaiting_required_evidence(current))
            return out
        model.on('research_plan', id=assessment_request['id']).reply(Answer(inspect_remaining))
        sim.run_until(lambda current: any(c['action']['id'] == assessment_request['id']
                                         for c in current.model.calls), max_steps=8)
        assessment_plan, = [e for e in sim.runtime['executions'].values()
                            if e['action']['id'] == assessment_request['id']]
        self.assertEqual(assessment_plan['outcome'], 'output_accepted',
                         {'error': assessment_plan.get('error'), 'receipts': model.receipts})
        self.assertEqual(sim.runtime['tasks'][row['id']]['assessment']['execution_id'], assessment_plan['id'])
        self.assertEqual(sim.runtime['tasks'][row['id']]['assessment']['decision'], 'incomplete')
        self.assertEqual(assert_call_records(self, sim)['research_plan'], 2)
        for _ in range(2):
            sim.step()
            assert_call_records(self, sim)
            for requested in (request, assessment_request):
                self.assertEqual(sum(c['action']['id'] == requested['id'] for c in model.calls), 1)


if __name__ == '__main__':
    unittest.main()


class PublicCliOverflowEvidenceTests(unittest.TestCase):
    def test_public_retry_preserves_failure_and_dispatches_one_original_action(self):
        from pathlib import Path
        import tempfile
        from do_math.configuration import DEFAULT_CONFIG
        from support.engine_cli_journey import Journey
        sim = overflowed_sim()
        action_id, waiting = held(sim)
        with tempfile.TemporaryDirectory() as directory:
            journey = Journey(sim, Path(directory))
            failures = deepcopy(journey.state()[2]['input_overflows'])
            config, _ = journey.document('config', {'max_input_bytes': DEFAULT_CONFIG['max_input_bytes']})
            self.assertEqual(journey.call('configure', '--config-file', config)['effect'], 'applied')
            config_hash = journey.call('status', '--json')['config_sha256']
            journey.decision('probe', {'kind': 'initialization', 'operation': 'probe', 'config_sha256': config_hash})
            first = journey.call('request', '--retry-action', action_id, '--request-id', 'UC-engine-retry')
            replay = journey.call('request', '--retry-action', action_id, '--request-id', 'UC-engine-retry')
            self.assertEqual((first['effect'], replay['effect']), ('applied', 'applied'))
            self.assertEqual(first['request_id'], replay['request_id'])
            journey.call('run', '--max-steps', '1')
            _, _, runtime = journey.state()
            self.assertNotIn(action_id, runtime['waiting_actions'])
            self.assertEqual([r['action']['id'] for r in sim.model.calls if r['role'] == 'maintenance'], [action_id])
            self.assertEqual(sum(r.get('kind') == 'input_overflow_retry_started' and
                r.get('request_id') == first['request_id'] for r in runtime['history']), 1)
            self.assertEqual(next(q for q in runtime['question_links'] if q['id'] == waiting['question_id'])['status'], 'resolved')
            self.assertEqual(runtime['input_overflows'], failures)
