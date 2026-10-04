"""활동의 선언·대기·종결 경계에서 거부 사유와 원상 보존을 확인한다."""
from copy import deepcopy
import unittest

from do_math import activities
from do_math.execution_lifecycle import create_execution


AT = '2090-01-01T00:00:00+00:00'
LATER = '2090-01-01T00:00:01+00:00'


def opened(**changes):
    runtime = {'queue': [], 'executions': {}}
    declaration = dict(activity_id='AY-one', activity_kind='research', owner_ref='RI-one',
                       input_refs=['SO-one'], opened_at=AT, stage='work', execution_limit=1)
    declaration.update(changes)
    record = activities.open_activity(runtime, **declaration)
    return runtime, record, declaration


def attempt(identifier='EX-one', owner='AY-one'):
    return create_execution(execution_id=identifier, owner_activity_id=owner, actor_kind='ai',
        input_manifest={}, profile_ref={'id': 'PF-one', 'revision': 1, 'sha256': 'a' * 64}, created_at=AT)


class ActivityGuardTests(unittest.TestCase):
    def test_every_declared_wait_kind_preserves_condition_and_resumes_only_for_that_condition(self):
        from do_math.wait_rules import ACTIVITY_WAIT_RULES
        from do_math.record_schemas import RECORDS
        from jsonschema import Draft202012Validator
        checker = Draft202012Validator(RECORDS['activities'])
        for kind in ACTIVITY_WAIT_RULES:
            with self.subTest(kind=kind):
                runtime, record, _ = opened()
                condition = {'source': ['SO-new']}
                activities.wait_for(runtime, record['id'], kind=kind, reason='The exact input is unavailable',
                    condition=condition, next_owner='user', at=AT)
                checker.validate(record)
                self.assertEqual(record['waiting']['kind'], kind)
                condition['source'].append('SO-other')
                before = deepcopy(runtime)
                with self.assertRaisesRegex(ValueError, '^the resolved condition differs from the recorded wait$'):
                    activities.resume_activity(runtime, record['id'], condition=condition, at=LATER)
                self.assertEqual(runtime, before)
                activities.resume_activity(runtime, record['id'], condition={'source': ['SO-new']}, at=LATER)
                self.assertEqual(record['status'], 'ready')
                self.assertNotIn('waiting', record)

    def test_unknown_kind_and_untyped_conditional_continuation_leave_the_state_unchanged(self):
        runtime, record, _ = opened()
        for kind in (None, True, [], {}, 'new-unregistered-kind'):
            before = deepcopy(runtime)
            with self.subTest(kind=kind), self.assertRaisesRegex(ValueError, '^unregistered activity wait:'):
                activities.wait_for(runtime, record['id'], kind=kind, reason='Waiting for input',
                    condition='SO-new', next_owner='user', at=AT)
            self.assertEqual(runtime, before)
        from do_math.execution_lifecycle import transition_execution
        execution = attempt()
        execution['action'] = {'id': 'AC-pause', 'role': 'maintenance'}
        activities.assign_execution(runtime, record['id'], execution)
        transition_execution(execution, 'starting', at=AT)
        transition_execution(execution, 'stopping', at=AT)
        transition_execution(execution, 'ended', at=AT, outcome='cancelled')
        before = deepcopy(runtime)
        with self.assertRaisesRegex(ValueError, '^unregistered activity wait: None$'):
            activities.continue_activity(runtime, execution['id'], at=LATER,
                reason='Pause until the public decision', condition={'kind': 'user_resume'}, next_owner='user')
        self.assertEqual(runtime, before)

    def test_invalid_declarations_do_not_create_activities(self):
        for field, value, reason in [('owner_ref', None, 'owner_ref is required'),
                ('input_refs', {}, 'input_refs must be a list'),
                *[('execution_limit', v, 'execution_limit must be a positive integer or null')
                  for v in (True, 0, -1, '1')]]:
            with self.subTest(field=field, value=value):
                runtime = {}
                declaration = dict(activity_id='AY-one', activity_kind='research',
                                   owner_ref='RI-one', input_refs=[], opened_at=AT)
                declaration[field] = value
                with self.assertRaisesRegex(ValueError, '^' + reason + '$'):
                    activities.open_activity(runtime, **declaration)
                self.assertEqual(runtime, {})

    def test_exact_redeclaration_is_idempotent_but_changed_facts_are_rejected(self):
        runtime, record, declaration = opened()
        self.assertIs(activities.open_activity(runtime, **declaration), record)
        before = deepcopy(runtime)
        with self.assertRaisesRegex(ValueError, '^activity AY-one was already opened with different facts$'):
            activities.open_activity(runtime, **{**declaration, 'owner_ref': 'RI-other'})
        self.assertEqual(runtime, before)

    def test_assignment_rejects_missing_owner_stage_wait_and_limit(self):
        for case in ('missing', 'owner', 'stage', 'waiting', 'finished', 'limit'):
            with self.subTest(case=case):
                runtime, record, _ = opened()
                execution = attempt()
                stage = 'work'
                identifier = 'AY-one'
                if case == 'missing':
                    identifier, reason = 'AY-missing', 'unknown activity AY-missing'
                elif case == 'owner':
                    execution = attempt(owner='AY-other')
                    reason = 'execution owner_activity_id differs from activity'
                elif case == 'stage':
                    stage, reason = 'review', 'execution stage differs from activity stage'
                elif case == 'waiting':
                    activities.wait_for(runtime, identifier, kind='required_input', reason='근거 대기', condition='SO-two', next_owner='user', at=AT)
                    reason = 'resolve the recorded activity wait before assigning an execution'
                elif case == 'finished':
                    activities.finish_activity(runtime, identifier, result_refs=[], unresolved=[], followups=[], at=AT)
                    reason = 'a finished activity cannot receive another execution'
                else:
                    activities.assign_execution(runtime, identifier, attempt('EX-old'), stage=stage)
                    reason = 'activity execution limit is exhausted'
                before = deepcopy(runtime)
                with self.assertRaisesRegex(ValueError, '^' + reason + '$'):
                    activities.assign_execution(runtime, identifier, execution, stage=stage)
                self.assertEqual(runtime, before)

    def test_binding_rejects_duplicate_requests_and_foreign_owner_without_partial_update(self):
        for rows, reason in [([{'id': 'AC-one'}, {'id': 'AC-one'}], 'action has duplicate queued requests'),
                ([{'id': 'AC-one', 'owner_activity_id': 'AY-other'}], 'action is already bound to another activity')]:
            with self.subTest(reason=reason):
                runtime, _, _ = opened()
                runtime['queue'] = rows
                action = {'id': 'AC-one'}
                before = deepcopy(runtime)
                with self.assertRaisesRegex(ValueError, '^' + reason + '$'):
                    activities.bind_action(runtime, action, 'AY-one')
                self.assertEqual((runtime, action), (before, {'id': 'AC-one'}))

    def test_wait_resume_and_finished_replay_preserve_exact_facts(self):
        runtime, record, _ = opened()
        condition = {'source': ['SO-new']}
        activities.wait_for(runtime, 'AY-one', kind='required_input', reason='원문 대기', condition=condition, next_owner='user', at=AT)
        condition['source'].append('SO-mutated')
        self.assertEqual(record['waiting']['condition'], {'source': ['SO-new']})
        before = deepcopy(runtime)
        with self.assertRaisesRegex(ValueError, '^the resolved condition differs from the recorded wait$'):
            activities.resume_activity(runtime, 'AY-one', condition=condition, at=LATER)
        self.assertEqual(runtime, before)
        activities.resume_activity(runtime, 'AY-one', condition={'source': ['SO-new']}, at=LATER)
        self.assertEqual((record['status'], record['resumed_at']), ('ready', LATER))
        self.assertNotIn('waiting', record)
        facts = dict(result_refs=['KN-one'], unresolved=['OB-two'], followups=['AC-next'], at=LATER)
        self.assertIs(activities.finish_activity(runtime, 'AY-one', **facts), record)
        self.assertIs(activities.finish_activity(runtime, 'AY-one', **facts), record)
        before = deepcopy(runtime)
        with self.assertRaisesRegex(ValueError, '^a finished activity is immutable$'):
            activities.finish_activity(runtime, 'AY-one', **{**facts, 'result_refs': []})
        self.assertEqual(runtime, before)

    def test_live_execution_prevents_wait_finish_and_continuation(self):
        runtime, _, _ = opened()
        execution = attempt()
        execution['action'] = {'id': 'AC-one', 'role': 'research_work'}
        activities.assign_execution(runtime, 'AY-one', execution)
        before = deepcopy(runtime)
        with self.assertRaisesRegex(ValueError, '^an activity may wait only after its assigned executions ended$'):
            activities.wait_for(runtime, 'AY-one', kind='required_input', reason='대기', condition='source', next_owner='user', at=LATER)
        with self.assertRaisesRegex(ValueError, '^an activity with a live execution cannot finish$'):
            activities.finish_activity(runtime, 'AY-one', result_refs=[], unresolved=[], followups=[], at=LATER)
        with self.assertRaisesRegex(ValueError, '^only an ended execution can request continuation$'):
            activities.continue_activity(runtime, 'EX-one', at=LATER, reason='이어가기')
        self.assertEqual(runtime, before)

    def test_invalid_container_and_orphan_diagnostics_are_exact(self):
        self.assertEqual(activities.validate_activities({'activities': []}), ['activities and executions must be dictionaries'])
        self.assertEqual(activities.validate_activities({'activities': {'AY-one': []}, 'executions': {'EX-one': None}}),
            ['AY-one: invalid activity record', 'EX-one: execution has no matching activity'])
        for field, reason in [('activities', 'runtime.activities must be a dictionary'),
                              ('executions', 'runtime.executions must be a dictionary')]:
            with self.subTest(field=field):
                runtime, _, declaration = opened()
                runtime[field] = []
                with self.assertRaisesRegex(ValueError, '^' + reason + '$'):
                    if field == 'activities':
                        activities.open_activity(runtime, **declaration)
                    else:
                        activities.continue_activity(runtime, 'EX-one', at=LATER, reason='이어가기')


class ActivityTransitionBoundaryTests(unittest.TestCase):
    def produced_attempt(self):
        from do_math.configuration import DEFAULT_CONFIG
        from do_math.execution_profiles import build_profiles
        from support.entry import entry
        profiles = build_profiles(deepcopy(DEFAULT_CONFIG), host=entry().ports.host)
        reference = profiles['role_profile_refs']['research_work'][0]
        return create_execution(execution_id='EX-one', owner_activity_id='AY-one', actor_kind='ai',
            input_manifest={}, profile_ref=reference, created_at=AT)

    def test_reassigning_the_same_attempt_does_not_spend_another_execution(self):
        runtime, activity, _ = opened()
        execution = self.produced_attempt()
        activities.assign_execution(runtime, activity['id'], execution, stage='work')
        before = deepcopy(runtime)
        self.assertIs(activities.assign_execution(runtime, activity['id'], execution, stage='work'), activity)
        self.assertEqual(runtime, before)
        self.assertEqual(activity['assigned_execution_ids'], [execution['id']])
        self.assertEqual(activities.validate_activities(runtime), [])

    def test_continuation_requires_every_current_attempt_to_end(self):
        from do_math.execution_lifecycle import transition_execution
        runtime, activity, _ = opened(execution_limit=None)
        first = self.produced_attempt()
        first['action'] = {'id': 'AC-one', 'role': 'research_work'}
        activities.assign_execution(runtime, activity['id'], first)
        transition_execution(first, 'ended', at=LATER, outcome='cancelled')
        second = create_execution(execution_id='EX-current', owner_activity_id=activity['id'],
            actor_kind=first['actor_kind'], input_manifest=first['input_manifest'],
            profile_ref=first['execution_profile_ref'], created_at=LATER)
        activities.assign_execution(runtime, activity['id'], second)
        before = deepcopy(runtime)
        with self.assertRaisesRegex(ValueError, "^continuation requires the activity's current attempts to end$"):
            activities.continue_activity(runtime, first['id'], at=LATER, reason='retry earlier attempt')
        self.assertEqual(runtime, before)
        self.assertEqual(activities.validate_activities(runtime), [])

    def test_continuation_preserves_current_queued_inputs_and_replaces_its_own_obligation(self):
        from do_math.execution_lifecycle import transition_execution
        runtime, activity, _ = opened(execution_limit=None)
        execution = self.produced_attempt()
        execution['action'] = {'id': 'AC-one', 'role': 'research_work',
                               'target': 'TK-old', 'grant_id': 'GR-old'}
        activities.assign_execution(runtime, activity['id'], execution)
        transition_execution(execution, 'ended', at=LATER, outcome='cancelled')
        runtime['queue'] = [{'id': 'AC-one', 'role': 'research_work',
                             'target': 'TK-current', 'grant_id': 'GR-current'}]
        original_execution = deepcopy(execution)
        for reason in ('first continuation', 'updated continuation'):
            with self.subTest(reason=reason):
                action = activities.continue_activity(runtime, execution['id'], at=LATER, reason=reason)
                self.assertIs(action, runtime['queue'][0])
                self.assertEqual(runtime['queue'], [{'id': 'AC-one', 'role': 'research_work',
                    'target': 'TK-current', 'grant_id': 'GR-current', 'owner_activity_id': activity['id'],
                    'continuation_of': execution['id'], 'context_origin': []}])
                obligation = {'action_id': 'AC-one', 'execution_id': execution['id'], 'reason': reason}
                self.assertEqual(activity['unresolved'], [obligation])
                self.assertEqual(activity['followups'], [{**obligation, 'next_owner': 'engine'}])
                self.assertEqual(activity['status'], 'ready')
                self.assertEqual(execution, original_execution)
                self.assertEqual(activities.validate_activities(runtime), [])

    def test_successor_state_follows_transitive_attempts_and_excludes_another_owner(self):
        from do_math.execution_lifecycle import transition_execution
        runtime, activity, _ = opened(execution_limit=None)
        first = self.produced_attempt()
        activities.assign_execution(runtime, activity['id'], first)
        transition_execution(first, 'ended', at=LATER, outcome='cancelled')
        previous = first
        for identifier in ('EX-child', 'EX-grandchild'):
            successor = create_execution(execution_id=identifier, owner_activity_id=activity['id'],
                actor_kind=first['actor_kind'], input_manifest=first['input_manifest'],
                profile_ref=first['execution_profile_ref'], created_at=LATER,
                continuation_of=previous['id'])
            activities.assign_execution(runtime, activity['id'], successor)
            if identifier == 'EX-child':
                transition_execution(successor, 'ended', at=LATER, outcome='cancelled')
            previous = successor
        activities.open_activity(runtime, activity_id='AY-other', activity_kind='research',
            owner_ref='RI-other', input_refs=[], opened_at=AT)
        foreign = create_execution(execution_id='EX-other', owner_activity_id='AY-other', actor_kind='ai',
            input_manifest={}, profile_ref=first['execution_profile_ref'], created_at=LATER,
            continuation_of=first['id'])
        activities.assign_execution(runtime, 'AY-other', foreign)
        # The foreign relation is an intentionally damaged continuation input;
        # observing successors must not treat it as this activity's recovery.
        before = deepcopy(runtime)
        self.assertEqual(activities.successor_state(runtime, first['id']), {
            'state': 'in_progress', 'execution_ids': ['EX-child', 'EX-grandchild'],
            'live_execution_ids': ['EX-grandchild'], 'action_ids': []})
        self.assertEqual(runtime, before)
        transition_execution(previous, 'ended', at=LATER, outcome='cancelled')
        self.assertEqual(activities.successor_state(runtime, first['id']), {
            'state': 'continued', 'execution_ids': ['EX-child', 'EX-grandchild'],
            'live_execution_ids': [], 'action_ids': []})

    def test_unknown_finished_and_missing_condition_rejections_preserve_activity_facts(self):
        runtime, activity, _ = opened()
        calls = [
            ('action requires an existing unfinished activity', lambda: activities.bind_action(runtime, {'id': 'AC-unbound'}, 'AY-absent')),
            ('unknown activity AY-absent', lambda: activities.wait_for(runtime, 'AY-absent', kind='required_input',
                reason='wait', condition='source', next_owner='user', at=LATER)),
            ('unknown activity AY-absent', lambda: activities.resume_activity(runtime, 'AY-absent',
                condition='source', at=LATER)),
            ('unknown activity AY-absent', lambda: activities.finish_activity(runtime, 'AY-absent',
                result_refs=[], unresolved=[], followups=[], at=LATER)),
            ('only a waiting activity can resume', lambda: activities.resume_activity(runtime, activity['id'],
                condition='source', at=LATER)),
            ('condition and next_owner are required', lambda: activities.wait_for(runtime, activity['id'], kind='required_input',
                reason='wait', condition=None, next_owner='user', at=LATER)),
            ('condition and next_owner are required', lambda: activities.wait_for(runtime, activity['id'], kind='required_input',
                reason='wait', condition='source', next_owner=None, at=LATER)),
        ]
        for reason, call in calls:
            with self.subTest(reason=reason):
                before = deepcopy(runtime)
                with self.assertRaises(ValueError) as caught:
                    call()
                self.assertEqual(str(caught.exception), reason)
                self.assertEqual(runtime, before)
        activities.finish_activity(runtime, activity['id'], result_refs=[], unresolved=[], followups=[], at=LATER)
        before = deepcopy(runtime)
        with self.assertRaisesRegex(ValueError, '^a finished activity cannot wait$'):
            activities.wait_for(runtime, activity['id'], kind='required_input', reason='wait', condition='source', next_owner='user', at=LATER)
        self.assertEqual(runtime, before)
        self.assertEqual(activities.validate_activities(runtime), [])

    def test_damaged_activity_links_report_exact_errors_without_repairing_the_input(self):
        from do_math.execution_lifecycle import transition_execution
        runtime, activity, _ = opened(execution_limit=None)
        predecessor = self.produced_attempt()
        activities.assign_execution(runtime, activity['id'], predecessor)
        transition_execution(predecessor, 'ended', at=LATER, outcome='cancelled')
        successor = create_execution(execution_id='EX-successor', owner_activity_id=activity['id'],
            actor_kind=predecessor['actor_kind'], input_manifest=predecessor['input_manifest'],
            profile_ref=predecessor['execution_profile_ref'], created_at=LATER,
            continuation_of=predecessor['id'])
        activities.assign_execution(runtime, activity['id'], successor)
        self.assertEqual(activities.validate_activities(runtime), [])
        damaged = deepcopy(runtime)
        damaged['activities'][activity['id']]['assigned_execution_ids'].append(successor['id'])
        before = deepcopy(damaged)
        self.assertEqual(activities.validate_activities(damaged), ['EX-successor: assigned to multiple activities'])
        self.assertEqual(damaged, before)
        damaged = deepcopy(runtime)
        damaged['executions'][successor['id']]['owner_activity_id'] = 'AY-absent'
        before = deepcopy(damaged)
        self.assertEqual(activities.validate_activities(damaged), [
            'AY-one: execution binding is invalid for EX-successor',
            'EX-successor: execution has no matching activity'])
        self.assertEqual(damaged, before)
        damaged = deepcopy(runtime)
        # An intentionally invalid continuation edge, not a normal stored execution.
        damaged['executions'][successor['id']]['continuation_of'] = 'EX-absent'
        before = deepcopy(damaged)
        self.assertEqual(activities.validate_activities(damaged),
                         ['EX-successor: continuation is not an ended execution in the same activity'])
        self.assertEqual(damaged, before)
        for field, operation, expected in [
            ('waiting', lambda r: activities.wait_for(r, 'AY-one', kind='required_input', reason='wait',
                condition='source', next_owner='user', at=LATER), 'AY-one: waiting state lacks its condition'),
            ('finished_at', lambda r: activities.finish_activity(r, 'AY-one',
                result_refs=[], unresolved=[], followups=[], at=LATER), 'AY-one: finished state lacks finished_at'),
        ]:
            with self.subTest(field=field):
                candidate, _, _ = opened()
                operation(candidate)
                del candidate['activities']['AY-one'][field]
                before = deepcopy(candidate)
                self.assertEqual(activities.validate_activities(candidate), [expected])
                self.assertEqual(candidate, before)
