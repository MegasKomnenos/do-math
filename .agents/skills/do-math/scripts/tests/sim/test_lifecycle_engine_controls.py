"""Lifecycle controls, authority, clock, readiness and events on the real engine (``lifecycle_engine``, ``core_engine``).

Each test starts from a Sim: the restored public activation, or a publicly
initialized instance where the case is before activation. Controls are applied
the way the owner applies a queued request (``engine_lifecycle.extended``), so a
rejection raises with its reason; the engine's judgments are called on the
Sim's engine where a case needs one exact step. Nothing replaces an engine
method or the store, and time moves only on the Sim's clock.
"""
from copy import deepcopy
from datetime import timedelta
from pathlib import Path
import hashlib
import tempfile
import unittest

from jsonschema import Draft202012Validator

from do_math import activities, questions
from do_math.execution_profiles import profile_ref
from do_math.governance import validate_grant_source
from do_math.record_schemas import RECORDS
from support.state_builders import policy_change
from do_math.engine import ResearchEngine
from support.engine_lifecycle import (ObservedCalls, approve, artifact_reader_code, clear_work, code_of, extended, grant,
                                      next_environment, queue_work, research_grant, task, transition)
from support.sim import Sim, warm_template

setUpModule = warm_template


def initialized(test):
    """A Sim of a publicly initialized, not yet active instance; removed with ``test``."""
    directory = tempfile.TemporaryDirectory()
    test.addCleanup(directory.cleanup)
    return Sim(directory.name)


class AuthorityTests(unittest.TestCase):
    def test_controls_reach_active_and_separate_initial_authority(self):
        sim = Sim.activated()
        e = sim.engine
        self.assertEqual(e.instance['lifecycle']['state'], 'active')
        self.assertEqual(set(e.instance['grants']), {'GR-initial-sim', 'GR-research-sim'})
        with self.assertRaisesRegex(ValueError, 'initialization authority cannot authorize research'):
            e._action_lifecycle_gate({'role': 'intent_interpretation', 'grant_id': 'GR-initial-sim'})
        chosen = e.instance['lifecycle']['adoption']['initial_profile_ref']
        actual = e._execution_profile({'role': 'intent_interpretation', 'profile_ref': chosen})
        self.assertEqual(profile_ref(actual), chosen)

    def test_adoption_preserves_approved_grants_and_disjoint_initial_scope(self):
        sim = Sim.activated()
        e = sim.engine
        for row in e.instance['grants'].values():
            approved = e.instance['decisions'][row['decision_id']]['change']['grant']
            self.assertEqual(row.get('initialization_only'), approved.get('initialization_only'))
            validate_grant_source(e.instance, row)
        with self.assertRaisesRegex(ValueError, 'initialization authority cannot authorize research'):
            e._action_lifecycle_gate({'role': 'intent_interpretation', 'grant_id': 'GR-initial-sim'})
        initial = initialized(self).engine
        grant(initial, 'GR-narrow', initial=True)
        before = deepcopy(initial.instance['grants'])
        with self.assertRaisesRegex(ValueError, 'initial and research authority must use distinct grants'):
            extended(initial, 'decision', {'change': {'kind': 'initialization', 'operation': 'adopt',
                                                      'initial_grant_ids': ['GR-narrow'], 'research_grant_ids': ['GR-narrow']}})
        self.assertEqual(initial.instance['grants'], before)

    def test_ambiguous_adopted_grants_are_not_selected_by_order(self):
        e = Sim.activated().engine
        research = research_grant(e)
        grant(e, 'GR-other')
        e.instance['lifecycle']['adoption']['research_grant_ids'] = ['GR-other', research]
        action = {'id': 'AC-ambiguous', 'role': 'research_preparation'}
        with self.assertRaisesRegex(ValueError, 'research authority: ambiguous current grants'):
            e._action_lifecycle_gate(action)
        self.assertNotIn('grant_id', action)
        selected = {**action, 'grant_id': research}
        e._action_lifecycle_gate(selected)
        self.assertEqual(selected['grant_id'], research)

    def test_unique_eligible_grant_within_adoption_and_explicit_denial(self):
        e = Sim.activated().engine
        research = research_grant(e)
        grant(e, 'GR-other')
        e.instance['grants']['GR-other']['included_targets'] = ['different']
        e.instance['lifecycle']['adoption']['research_grant_ids'] = ['GR-other', research]
        action = {'id': 'AC-unique', 'role': 'research_preparation'}
        e._action_lifecycle_gate(action)
        self.assertEqual(action['grant_id'], research)
        with self.assertRaisesRegex(ValueError, 'research authority: no current grant permits this action'):
            e._action_lifecycle_gate({**action, 'grant_id': 'GR-other'})

    def test_formal_requires_preapproved_environment(self):
        e = Sim.activated().engine
        self.assertEqual(e._formal_environment()['id'], e.instance['active_trust_environment'])
        e.instance['active_trust_environment'] = None
        with self.assertRaisesRegex(ValueError, 'approved fixed trust environment required: trust environment absent'):
            e._formal_environment()

    def test_initial_intent_receipt_cannot_replace_import_evidence(self):
        e = Sim.activated().engine
        original = deepcopy(e.runtime['intent_imports'])
        self.assertEqual(len(original), 1)
        for field, reason in (('check', 'initial input requires a sealed, fully checked applied import'),
                              ('application', 'sealed import application receipt changed'),
                              ('source', 'immutable source bytes or revision changed')):
            with self.subTest(field=field):
                e.runtime['intent_imports'] = deepcopy(original)
                bundle = next(iter(e.runtime['intent_imports'].values()))
                if field == 'check':
                    bundle['check']['bundle_sha256'] = '0' * 64
                elif field == 'application':
                    bundle['application']['status'] = 'awaiting_decision'
                else:
                    bundle['source']['text'] = 'different original'
                with self.assertRaisesRegex(ValueError, reason):
                    e._complete_initial_intent(e.instance['lifecycle']['input_id'])

    def test_capability_evidence_rejects_changed_host_or_forged_record(self):
        sim = Sim.activated()
        e = sim.engine
        ref = e.instance['role_profile_refs']['intent_interpretation'][0]
        self.assertTrue(e._capability_requirements(ref)['satisfied'])
        observed = sim.ports.host.identity
        sim.ports.host.identity = {'host': 'different'}  # the host port now reports another CLI installation
        self.assertFalse(e._capability_requirements(ref)['satisfied'])
        sim.ports.host.identity = observed
        self.assertTrue(e._capability_requirements(ref)['satisfied'])
        for row in e.instance['capability_evidence'].values():
            row['identity'] = {'forged': True}
        self.assertFalse(e._capability_requirements(ref)['satisfied'])

    def test_session_capacity_reads_git_reservations_not_sqlite(self):
        sim = Sim.activated()
        resources = sim.engine._session_resources()
        self.assertTrue(resources)
        for row in resources.values():
            self.assertEqual(set(row), {'limit', 'used', 'execution_ids', 'available'})
        for root in (sim.root, Path(sim.instance['workspace'])):
            self.assertFalse((root / 'session-slots').exists())


class ClockTests(unittest.TestCase):
    def test_clock_regression_precedes_authority(self):
        sim = Sim.activated()
        e = sim.engine
        sim.clock.set_wall(sim.clock.wall() - timedelta(seconds=1))  # below the published high-water mark
        before = deepcopy(e.instance['grants'])
        with self.assertRaisesRegex(ValueError, 'clock prevents new authority: persisted_utc_regression'):
            grant(e, 'GR-bad')
        self.assertEqual(e.instance['grants'], before)
        with self.assertRaisesRegex(ValueError, 'clock prevents new authority: persisted_utc_regression'):
            e._action_lifecycle_gate({'role': 'external_action'})

    def test_event_uses_the_clock_sample_that_passed_the_guard(self):
        sim = initialized(self)
        e = sim.engine
        approved = sim.clock.wall() + timedelta(seconds=2)
        samples = iter([approved, approved - timedelta(seconds=1)])
        sim.clock.wall = lambda: next(samples)  # the wall clock reads a later, earlier sample on the next read
        event = e._lifecycle_event('test_clock_observation', schedule=False)
        self.assertEqual(event['at'], approved.isoformat())
        self.assertEqual(e.runtime['last_observed_utc'], approved.isoformat())


class ReadinessTests(unittest.TestCase):
    """An active instance whose queue and pending events a test starts empty."""

    def setUp(self):
        self.sim = Sim.activated()
        self.e = self.sim.engine
        clear_work(self.sim)

    def test_review_currentness_and_no_persisted_readiness(self):
        e = self.e
        t = task(e, approved=False)
        e._refresh_readiness()
        e._refresh_readiness()
        self.assertEqual(len([a for a in e.runtime['queue'] if a['role'] == 'task_contract_review']), 1)
        approve(e, e.runtime['tasks'][t['id']])
        e.runtime['queue'].clear()
        e._refresh_readiness()
        self.assertEqual(e._task_readiness[t['id']]['state'], 'ready')
        readiness_event = next(row for row in e.runtime['events'] if row['kind'] == 'task_became_ready')
        Draft202012Validator(RECORDS['events']).validate(readiness_event)
        self.assertEqual(readiness_event['basis']['records'], e._task_readiness[t['id']]['basis'])
        self.assertEqual(e.runtime['tasks'][t['id']]['status'], 'planned')
        self.assertNotIn('task_readiness', e.runtime)
        extended(e, 'decision', {'change': policy_change(e, 'New evidence requirement')})
        e._refresh_readiness()
        self.assertEqual(e._task_readiness[t['id']]['state'], 'not_ready')
        for event in e.runtime['events']:
            Draft202012Validator(RECORDS['events']).validate(event)
        e._save()
        self.assertNotIn('task_readiness', e.store.load()[2])

    def test_rejected_current_review_not_repeated(self):
        e = self.e
        t = task(e, approved=False)
        approve(e, t, 'rejected')
        e._refresh_readiness()
        self.assertFalse(any(a['role'] == 'task_contract_review' for a in e.runtime['queue']))

    def test_missing_input_and_bad_condition_distinct(self):
        e = self.e
        a = task(e, inputs=['absent'])
        b = task(e, 'TK-two', condition={'op': 'unsupported'})
        e._refresh_readiness()
        self.assertEqual(e._task_readiness[a['id']]['state'], 'not_ready')
        self.assertEqual(e._task_readiness[b['id']]['state'], 'evaluation_error')

    def test_completed_removes_readiness_projection(self):
        e = self.e
        t = task(e)
        e._refresh_readiness()
        self.assertIn(t['id'], e._task_readiness)
        e.runtime['tasks'][t['id']]['status'] = 'completed'
        e._refresh_readiness()
        self.assertNotIn(t['id'], e._task_readiness)

    def test_published_event_is_not_mutated_when_assigned(self):
        e = self.e
        event = e._lifecycle_event('user_input_available')
        event['event_seq'] = 1
        original = deepcopy(event)
        e._refresh_readiness()
        self.assertEqual(next(row for row in e.runtime['events'] if row['id'] == event['id']), original)
        self.assertIn(event['id'], e.runtime['pending_events'])
        self.assertTrue(any(event['id'] in a.get('event_refs', []) for a in e.runtime['queue']))
        other = e._lifecycle_event('user_input_available')
        e._consume_action_events({'event_refs': [event['id']]}, 'EX-accepted-plan')
        self.assertNotIn(event['id'], e.runtime['pending_events'])
        self.assertIn(other['id'], e.runtime['pending_events'])
        self.assertEqual(next(row for row in e.runtime['events'] if row['id'] == event['id']), original)

    def test_one_input_request_is_one_event_and_its_consumption_keeps_a_later_request(self):
        e = self.e
        tid = task(e)['id']

        def current():
            return e.runtime['tasks'][tid]
        current()['newinput'] = 'RQ-one'
        e._refresh_readiness()
        self.sim.advance(5)
        e._refresh_readiness()
        inputs = [row for row in e.runtime['events'] if row['kind'] == 'task_new_input']
        self.assertEqual([row['request_id'] for row in inputs], ['RQ-one'])
        self.assertEqual(e.runtime['pending_events'].count(inputs[0]['id']), 1)
        current()['newinput'] = 'RQ-two'
        e._consume_action_events({'event_refs': [inputs[0]['id']]}, 'EX-accepted-plan')
        self.assertEqual(current()['newinput'], 'RQ-two')
        e._refresh_readiness()
        later = next(row for row in e.runtime['events'] if row.get('request_id') == 'RQ-two')
        e._consume_action_events({'event_refs': [later['id']]}, 'EX-accepted-plan')
        self.assertNotIn('newinput', current())

    def test_empty_queue_prepares_from_goal_exhaustion_regardless_of_cycle_count(self):
        e = self.e
        e.runtime['cycles'] = 1000
        e._refresh_readiness()
        preparation = next((a for a in e.runtime['queue'] if a['role'] == 'research_preparation'), None)
        self.assertIsNotNone(preparation)
        self.assertIn('exhaustion_basis', preparation)
        self.assertTrue(preparation['exhaustion_basis']['exhausted'])

    def test_assigned_events_survive_and_live_input_is_not_changed(self):
        e = self.e
        first = e._lifecycle_event('user_input_available')
        e._refresh_readiness()
        a = next(a for a in e.runtime['queue'] if a['role'] == 'research_plan')
        e._register_execution(a, {'id': 'EX-live', 'role': 'research_plan', 'status': 'running'})
        self.assertEqual(e.runtime['executions']['EX-live']['status'], 'running')
        original = deepcopy(a)
        second = e._lifecycle_event('user_input_available')
        e._refresh_readiness()
        self.assertEqual(next(a for a in e.runtime['queue'] if a.get('id') == original['id']), original)
        self.assertTrue({first['id'], second['id']} <= set(e.runtime['pending_events']))

    def test_dispatch_uses_current_task_predicate(self):
        e = self.e
        t = task(e)
        a = queue_work(e, t['id'])
        self.assertTrue(e._dispatchable(a))
        e.runtime['tasks'][t['id']]['inputs'].append('absent')
        self.assertFalse(e._dispatchable(a))
        e.runtime['tasks'][t['id']]['inputs'] = []
        e.runtime['tasks'][t['id']]['status'] = 'ready'
        e.runtime['task_readiness'] = {t['id']: {'state': 'ready'}}
        self.assertFalse(e._dispatchable(a))
        self.assertEqual(a['dispatch_wait']['kind'], 'task_readiness')

    def test_task_artifact_context_reaches_refresh_and_dispatch(self):
        e = self.e
        # Two artifacts sealed at one snapshot, then a later head: a read at the head instead of the
        # condition's snapshot is a different call. Each judgment gets an artifact no judgment has matched
        # yet, since a matched digest's verdict is remembered and its bytes are then not read again.
        artifacts = {name: ('runtime/artifacts/EX-evidence/' + name + '.json', ('{"valid":true,"n":"%s"}' % name).encode())
                     for name in ('refresh', 'dispatch', 'refused')}
        e._save({path: raw for path, raw in artifacts.values()})
        snapshot = e.head
        e.instance['title'] = 'A later published change'
        e._save()
        self.assertNotEqual(e.head, snapshot)

        def condition(name, content=None):
            path, raw = artifacts[name]
            return {'op': 'artifact_valid', 'artifact_ref': {'snapshot': snapshot, 'path': path,
                                                             'sha256': hashlib.sha256(content or raw).hexdigest()}}

        def reads(seen):
            """``(path, snapshot)`` of every evidence read and every repository read the judgments made."""
            return ([(call['path'], call['commit']) for call in seen.calls['reader']],
                    [(call['path'], call['snapshot']) for call in seen.calls['store']])
        codes = dict(reader=artifact_reader_code(), store=code_of(e.store.read),
                     selected=code_of(ResearchEngine._selected_action_current))

        t = task(e, condition=condition('refresh'))
        with ObservedCalls(**codes) as seen:
            e._refresh_readiness()
        self.assertEqual(e._task_readiness[t['id']]['state'], 'ready')
        expected = [(artifacts['refresh'][0], snapshot)]
        self.assertEqual(reads(seen), (expected, expected))

        dispatched = task(e, 'TK-dispatch', condition=condition('dispatch'))
        a = queue_work(e, dispatched['id'])
        with ObservedCalls(**codes) as seen:
            self.assertTrue(e._dispatchable(a))
        path, raw = artifacts['dispatch']
        self.assertEqual(reads(seen), ([(path, snapshot)], [(path, snapshot)]))
        # The evaluation context _dispatchable actually handed to _selected_action_current reads the named bytes.
        handed, = [call['evaluation_context'] for call in seen.calls['selected']]
        self.assertTrue(callable(handed['validate_artifact']))
        self.assertEqual(handed['read_artifact'](path, snapshot), raw)

        # Another digest for sealed bytes: readiness reads them and refuses the condition, and so does
        # the dispatch judgment's readiness check, which then stops before _selected_action_current.
        refused = task(e, 'TK-refused', condition=condition('refused', b'{"valid":false}'))
        with ObservedCalls(**codes) as seen:
            e._refresh_readiness()
        verdict = e._task_readiness[refused['id']]
        self.assertEqual(verdict['state'], 'evaluation_error')
        self.assertTrue(any('artifact bytes differ from sealed hash' in error for error in verdict['errors']), verdict)
        self.assertEqual(reads(seen)[0], [(artifacts['refused'][0], snapshot)])
        b = queue_work(e, refused['id'])
        with ObservedCalls(**codes) as seen:
            self.assertFalse(e._dispatchable(b))
        self.assertEqual(reads(seen)[0], [(artifacts['refused'][0], snapshot)])
        self.assertEqual(seen.calls['selected'], [])


class LifecycleControlTests(unittest.TestCase):
    def test_pause_returns_to_original_phase_and_preserves_events(self):
        e = Sim.activated().engine
        ev = e._lifecycle_event('user_input_available')
        extended(e, 'pause', {})
        e._refresh_readiness()
        self.assertIn(ev['id'], e.runtime['pending_events'])
        extended(e, 'pause', {}, 'UI-again')
        extended(e, 'resume', {})
        self.assertEqual(e.instance['lifecycle']['state'], 'active')

    def test_conversation_requires_new_live_generation(self):
        sim = Sim.activated()
        e = sim.engine
        extended(e, 'conversation', {'operation': 'attach', 'id': 'chat', 'generation': 1, 'lease_seconds': 10,
                                     'disconnect_policy': 'pause'})
        sim.advance(11)
        e._check_conversations()
        with self.assertRaisesRegex(ValueError, 'conversation pause requires a live new connection generation'):
            extended(e, 'resume', {})
        with self.assertRaisesRegex(ValueError, 'signal does not identify the current connected conversation generation'):
            extended(e, 'conversation', {'operation': 'heartbeat', 'id': 'chat', 'generation': 1})
        extended(e, 'conversation', {'operation': 'attach', 'id': 'chat', 'generation': 2, 'lease_seconds': 10})
        extended(e, 'resume', {})
        self.assertEqual(e.instance['lifecycle']['state'], 'active')

    def test_continue_alias_is_rejected_without_changing_conversation(self):
        e = Sim.activated().engine
        before = deepcopy((e.instance, e.runtime))
        with self.assertRaisesRegex(ValueError, 'conversation loss policy'):
            extended(e, 'conversation', {'operation': 'attach', 'id': 'chat', 'generation': 1, 'lease_seconds': 60,
                                         'disconnect_policy': 'continue'})
        self.assertEqual((e.instance, e.runtime), before)

    def test_continue_policy_does_not_pause(self):
        sim = Sim.activated()
        e = sim.engine
        extended(e, 'conversation', {'operation': 'attach', 'id': 'chat', 'generation': 1, 'lease_seconds': 1,
                                     'disconnect_policy': 'continue_authorized'})
        sim.advance(2)
        e._check_conversations()
        self.assertEqual(e.runtime['conversations']['chat']['status'], 'lost')
        self.assertEqual(e.instance['lifecycle']['state'], 'active')

    def test_control_replay_and_atomic_rejection(self):
        e = Sim.activated().engine
        q = {'operation': 'attach', 'id': 'chat', 'generation': 1, 'lease_seconds': 60,
             'disconnect_policy': 'continue_authorized'}
        extended(e, 'conversation', q, 'UI-fixed')
        before = deepcopy((e.instance, e.runtime))
        extended(e, 'conversation', q, 'UI-fixed')
        self.assertEqual((e.instance, e.runtime), before)
        with self.assertRaisesRegex(ValueError, 'user control ID reused with changed content'):
            extended(e, 'conversation', {**q, 'generation': 2}, 'UI-fixed')
        self.assertEqual((e.instance, e.runtime), before)

    def test_initial_grant_does_not_queue_research_before_activation(self):
        e = initialized(self).engine
        grant(e, 'GR-initial', initial=True)
        self.assertIn('GR-initial', e.instance['grants'])
        self.assertEqual(e.runtime['queue'], [])

    def test_closed_pause_cannot_reopen(self):
        e = initialized(self).engine
        e.runtime['status'] = 'closed'
        before = deepcopy((e.instance, e.runtime))
        with self.assertRaisesRegex(ValueError, 'closed/completed instance cannot pause or reopen'):
            e._pause_lifecycle('user_pause')
        self.assertEqual((e.instance, e.runtime), before)
        with self.assertRaisesRegex(ValueError, 'closed/completed instance cannot resume'):
            e._resume_lifecycle({'origin': 'user'})

    def test_close_control_seals_terminal_marker(self):
        e = initialized(self).engine
        self.assertTrue(extended(e, 'close', {}))
        self.assertTrue(e.instance['lifecycle']['permanently_closed'])
        self.assertEqual(e.runtime['status'], 'closed')
        self.assertEqual(e.runtime['queue'], [])
        for action in ('pause', 'resume'):
            with self.subTest(action=action), self.assertRaisesRegex(
                    ValueError, 'closed/completed instance cannot apply lifecycle controls'):
                extended(e, action, {})


class InitialQueueTests(unittest.TestCase):
    """The initial interpretation queue of an active instance returned to ``initializing`` without its intent check.

    A control replaces ``engine.instance``, so the lifecycle is read again after one.
    """

    def setUp(self):
        self.e = Sim.activated().engine
        self.initial = self.e.instance['lifecycle']['adoption']['initial_grant_ids'][0]

    def initializing(self):
        lifecycle = self.e.instance['lifecycle']
        lifecycle.update(state='initializing')
        lifecycle.pop('intent_check', None)
        self.e.runtime['queue'].clear()
        return lifecycle

    def test_initial_queue_does_not_manufacture_explicit_grant_choice(self):
        e = self.e
        grant(e, 'GR-init-other', initial=True)
        lifecycle = self.initializing()
        lifecycle['adoption']['initial_grant_ids'] = ['GR-init-other', self.initial]
        e._queue_initial_intent()
        action = next(a for a in e.runtime['queue'] if a['role'] == 'intent_interpretation')
        self.assertNotIn('grant_id', action)
        with self.assertRaisesRegex(ValueError, 'initial operating authority: ambiguous current grants'):
            e._action_lifecycle_gate(action)
        lifecycle['adoption']['initial_grant_ids'] = [self.initial]
        e._action_lifecycle_gate(action)
        self.assertEqual(action['grant_id'], self.initial)

    def test_initial_queue_treats_held_input_overflow_as_the_same_request(self):
        e = self.e
        lifecycle = self.initializing()
        held = {'id': 'AC-held-overflow', 'role': 'intent_interpretation', 'target': lifecycle['input_id'],
                'stage': 'interpret', 'initialization': True}
        e.runtime['waiting_actions'] = {held['id']: {'action': held, 'kind': 'input_overflow',
                                                    'reason': 'input_overflow', 'next_owner': 'user'}}
        e._queue_initial_intent()
        self.assertEqual(e.runtime['queue'], [], 'a held initial request must not be regenerated under a new action ID')


class InputOverflowRetryTests(unittest.TestCase):
    def test_retry_reuses_the_exact_held_action_and_current_authority(self):
        from support.entry import entry
        _entry = entry()
        e = Sim.activated().engine
        action = {'id': 'AC-held-overflow', 'role': 'research_preparation'}
        e._action_lifecycle_gate(action)
        activity = e._activity_for_action(action)
        condition = {'kind': 'input_overflow', 'action_ids': [action['id']]}
        activities.wait_for(e.runtime, activity['id'], reason='input_overflow', condition=condition,
                            next_owner='user', at=e._lifecycle_now().isoformat())
        question = questions.link(e.runtime, execution_id='EX-overflow', field='resolution_question/question',
                                  owner='user', targets=[action['id']], blocks=True, clock=_entry.ports.clock)
        e.runtime['queue'].clear()
        e.runtime.setdefault('waiting_actions', {})[action['id']] = {'action': deepcopy(action), 'kind': 'input_overflow',
                                                      'reason': 'input_overflow', 'question_id': question['id'],
                                                      'next_owner': 'user'}
        prior_profile = deepcopy(action['profile_ref'])
        retried = e._retry_input_overflow_action({'id': 'UC-retry', 'config': {'retry_action': action['id']}})
        self.assertEqual(retried['id'], action['id'])
        self.assertEqual(retried['owner_activity_id'], activity['id'])
        self.assertEqual(retried['profile_ref'], prior_profile)
        self.assertEqual(e.runtime['activities'][activity['id']]['status'], 'ready')
        self.assertNotIn(action['id'], e.runtime['waiting_actions'])
        self.assertEqual(question['status'], 'open', 'a request does not prove that packing now fits')
        e.runtime['status'] = 'closed'
        with self.assertRaisesRegex(ValueError, 'closed/completed'):
            e._retry_input_overflow_action({'id': 'UC-closed', 'config': {'retry_action': action['id']}})


class LimitedRecoveryTests(unittest.TestCase):
    def test_limited_recovery_refuses_unbound_requests_and_surfaces_check_defects(self):
        from support.provider_probes import ObservedCalls
        from support.engine_lifecycle import applied
        sim = Sim.activated()
        e = sim.engine
        with ObservedCalls(check=e._check_limited_recovery) as calls:
            self.assertFalse(e._limited_recovery_allowed({'id': 'AC-plain', 'role': 'maintenance'}))
        self.assertEqual(calls.count('check'), 0)
        applied(sim, 'pause', text='repair paused research')
        applied(sim, 'decision', config={'change': {'kind': 'grant', 'grant': {
            'id': 'GR-repair', 'kind': 'local', 'roles': ['maintenance'], 'included_targets': ['RI-test'],
            'purposes': ['restore sealed input'], 'reuse': 'once'}}})
        e._enqueue('maintenance', 'RI-test', purpose='restore sealed input')
        action = next(a for a in e.runtime['queue'] if a['role'] == 'maintenance' and a.get('target') == 'RI-test')
        e._save()
        applied(sim, 'decision', config={'change': {'kind': 'limited_recovery', 'action_id': action['id'],
            'grant_id': 'GR-repair', 'profile_ref': e._select_model(action)['profile_ref'],
            'purpose': 'restore sealed input', 'procedure': 'Restore the sealed input and verify its digest',
            'expires_at': (sim.clock.wall() + timedelta(minutes=5)).isoformat()}})
        action = next(a for a in e.runtime['queue'] if a['id'] == action['id'])
        self.assertTrue(e._limited_recovery_allowed(action))
        malformed = deepcopy(action)
        malformed['repair']['limited_recovery']['source_ref'] = 'UC-one'
        with ObservedCalls(check=e._check_limited_recovery) as calls:
            with self.assertRaises(KeyError) as caught:
                e._limited_recovery_allowed(malformed)
            self.assertEqual(caught.exception.args, ('UC-one',))
        self.assertEqual(calls.count('check'), 1)
        stale = deepcopy(action)
        stale['repair']['limited_recovery']['pause_basis'] = 'stale'
        self.assertFalse(e._limited_recovery_allowed(stale))
        self.assertTrue(e._limited_recovery_allowed(action))

    def test_paused_recovery_is_exact_authorized_and_revocable(self):
        sim = Sim.activated()
        e = sim.engine
        e._pause_lifecycle('user_pause')
        grant(e, 'GR-repair', spec={'kind': 'local', 'roles': ['maintenance'], 'included_targets': ['RI-test'],
                                    'purposes': ['restore sealed input'], 'reuse': 'once'})
        action = {'id': 'AC-repair', 'role': 'maintenance', 'target': 'RI-test', 'purpose': 'restore sealed input'}
        e.runtime['queue'].append(action)
        ref = e._select_model(action)['profile_ref']
        extended(e, 'decision', {'change': {'kind': 'limited_recovery', 'action_id': 'AC-repair', 'grant_id': 'GR-repair',
            'profile_ref': ref, 'purpose': 'restore sealed input',
            'procedure': 'Restore the specified sealed input and verify its digest',
            'expires_at': (sim.clock.wall() + timedelta(minutes=5)).isoformat()}})
        action = next(a for a in e.runtime['queue'] if a['id'] == 'AC-repair')
        e._check_limited_recovery(action)
        e._action_lifecycle_gate(action)
        self.assertTrue(e._limited_recovery_allowed(action))
        self.assertFalse(e._execution_stop_requested(action))
        self.assertEqual(e.runtime['status'], 'paused')
        prior_stop = e.runtime['stop_requested']
        e.runtime['stop_requested'] = 'new_emergency_stop'
        self.assertFalse(e._limited_recovery_allowed(action))
        e.runtime['stop_requested'] = prior_stop
        for other in ({**action, 'target': 'RI-other'}, {'role': 'research_preparation'}):
            with self.subTest(other=other), self.assertRaisesRegex(ValueError, 'lifecycle or conversation prevents dispatch'):
                e._action_lifecycle_gate(other)
        e._pause_lifecycle('new_pause')
        self.assertFalse(e._limited_recovery_allowed(action))
        self.assertTrue(e._execution_stop_requested(action))


class PausedDispatchTests(unittest.TestCase):
    """The owner's pass while paused: only the action a limited recovery decision names is dispatched."""

    def test_limited_recovery_admission_and_stop_gate_agree_for_each_binding_axis(self):
        """3-C/B-36: public approval with one premise changed at a time, no model replay."""
        from support.scheduling_recovery import limited_recovery_sim
        sim = limited_recovery_sim()
        engine = sim.engine
        before_instance, before_runtime = deepcopy(sim.instance), deepcopy(sim.runtime)
        original = deepcopy(next(a for a in sim.runtime['queue'] if a['id'] == 'AC-limited'))
        cases = ('valid', 'missing_binding', 'pause_id', 'pause_basis', 'action_hash', 'target',
                 'purpose', 'profile', 'source_approval', 'grant_revoked', 'permanently_closed', 'new_stop')
        for damage in cases:
            engine.instance, engine.runtime = deepcopy(before_instance), deepcopy(before_runtime)
            action = deepcopy(original)
            binding = action['repair']['limited_recovery']
            if damage == 'missing_binding': action['repair'].pop('limited_recovery')
            elif damage in ('pause_id', 'pause_basis'): binding[damage] = 'changed-' + damage
            elif damage == 'action_hash': binding['action_sha256'] = '0' * 64
            elif damage == 'target': action['target'] = 'RI-other'
            elif damage == 'purpose': action['purpose'] += ' outside approval'
            elif damage == 'profile': action['profile_ref'] = {**action['profile_ref'], 'revision': action['profile_ref']['revision'] + 1}
            elif damage == 'source_approval':
                engine.runtime['extended_controls'][binding['source_ref']]['request']['config']['change']['procedure'] += ' changed'
            elif damage == 'grant_revoked': engine.instance['grants'][action['grant_id']]['status'] = 'revoked'
            elif damage == 'permanently_closed': engine.instance['lifecycle']['permanently_closed'] = True
            elif damage == 'new_stop': engine.runtime['stop_requested'] = 'new emergency stop'
            with self.subTest(damage=damage):
                allowed = damage == 'valid'
                self.assertIs(engine._limited_recovery_allowed(action), allowed)
                self.assertIs(engine._execution_stop_requested(action), not allowed)
                if allowed:
                    engine._action_lifecycle_gate(action)
                else:
                    reason = ('closed/completed instance cannot dispatch' if damage == 'permanently_closed' else
                              'profile reference is absent or stale' if damage == 'profile' else
                              'lifecycle or conversation prevents dispatch')
                    import re
                    with self.assertRaisesRegex(ValueError, '^' + re.escape(reason) + '$'):
                        engine._action_lifecycle_gate(action)
        engine.instance, engine.runtime = before_instance, before_runtime
        self.assertIs(engine._limited_recovery_allowed(original), True)
        sim.advance(301)  # the publicly adopted limited approval lasts five minutes
        self.assertIs(engine._limited_recovery_allowed(original), False)
        self.assertIs(engine._execution_stop_requested(original), True)
        with self.assertRaisesRegex(ValueError, '^lifecycle or conversation prevents dispatch$'):
            engine._action_lifecycle_gate(deepcopy(original))

    def recovery(self, e, action, grant_id, purpose, procedure, profile):
        extended(e, 'decision', {'change': {'kind': 'limited_recovery', 'action_id': action['id'], 'grant_id': grant_id,
            'profile_ref': profile, 'purpose': purpose, 'procedure': procedure,
            'expires_at': (e.ports.clock.wall() + timedelta(minutes=5)).isoformat()}})

    def test_scheduler_scopes_maintenance_dispatch_with_executor_double(self):
        """About 2.5 s in a full run, over the 2 s Sim budget: the owner pass runs the maintenance call through the worker."""
        sim = Sim.activated()
        e = sim.engine
        e._pause_lifecycle('user_pause')
        grant(e, 'GR-repair', spec={'kind': 'local', 'roles': ['maintenance'], 'reuse': 'once',
                                    'included_targets': ['RI-test']})
        # The queue holds the repair and then general research, as the product queues them.
        e.runtime['queue'].clear()
        e._enqueue('maintenance', 'RI-test', reason='Inspect the exact recovery target')
        e._enqueue('research_preparation', reason='General research waits for the resume')
        action, general = e.runtime['queue']
        self.recovery(e, action, 'GR-repair', 'inspect the exact recovery target',
                      'Inspect this target only; do not resume research', e._select_model(action)['profile_ref'])
        before = set(e.runtime['executions'])
        e._save()
        sim.step()  # one owner pass: the real executor starts what the scheduler dispatches
        dispatched = [row['role'] for eid, row in sim.runtime['executions'].items() if eid not in before]
        self.assertEqual(dispatched, ['maintenance'])
        self.assertEqual([call['role'] for call in sim.model.calls], ['maintenance'])
        self.assertEqual(sim.runtime['status'], 'paused')
        self.assertEqual(sim.runtime['queue'][0]['id'], general['id'])

    def test_scheduler_runs_only_approved_machine_recovery_and_stays_paused(self):
        sim = Sim.activated()
        environment = next_environment(sim, 'repair')
        e = sim.engine
        transition(sim, environment)
        e._pause_lifecycle('user_pause')
        grant(e, 'GR-repair', spec={'kind': 'local', 'roles': ['trust_activate'], 'reuse': 'once',
                                    'purposes': ['activate empty verified environment']})
        action = next(a for a in e.runtime['queue'] if a['role'] == 'trust_activate')
        self.recovery(e, action, 'GR-repair', 'activate empty verified environment',
                      'Activate this empty target transition only', profile_ref(e._execution_profile(action)))
        e.runtime['queue'].insert(0, {'id': 'AC-general', 'role': 'research_preparation'})
        e._save()
        sim.step()
        self.assertEqual(sim.instance['active_trust_environment'], environment)
        self.assertEqual(sim.runtime['status'], 'paused')
        self.assertEqual(sim.instance['lifecycle']['state'], 'paused')
        self.assertTrue(any(a['id'] == 'AC-general' for a in sim.runtime['queue']))
        repair = [x for x in sim.runtime['executions'].values() if x['role'] == 'trust_activate'][-1]
        self.assertEqual(repair['status'], 'ended')
        self.assertEqual(repair['submission_receipt']['state'], 'accepted')
        self.assertEqual(sim.model.calls, [])


if __name__ == '__main__':
    unittest.main()
