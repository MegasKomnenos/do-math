"""Repetition lineages, their holds, research exhaustion and the classification of preparation receipts
(``revisions``, ``task_contracts``, ``planning``; layer 2), moved from ``test_task_contracts``
(``RepetitionLineageTests``, ``PreparationReceiptClassificationTests``).

The tests call the product's pure functions on plain records; nothing of the product is replaced.
"""
from copy import deepcopy
import unittest

import jsonschema

from do_math import planning, revisions, task_contracts
from do_math.configuration import DEFAULT_CONFIG
from do_math.state_contract import default_state_contract
from support.record_builders import approve_task, approved_task


class RepetitionLineageTests(unittest.TestCase):
    def test_real_receipts_produce_all_five_lineages_and_initial_versions(self):
        from support.entry import entry
        _entry = entry()
        t, i, r = approved_task()
        t['producer_execution'] = 'EX-prep'
        i['knowledge'] = {'KN-first': {'id': 'KN-first', 'producer_execution': 'EX-work'},
                          'KN-next': {'id': 'KN-next', 'producer_execution': 'EX-revise', 'supersedes': 'KN-first'}}
        for identifier, action, output, accepted in [
                ('EX-prep', {'role': 'research_preparation'}, {'summary': 'preserved one contract'}, True),
                ('EX-plan', {'role': 'research_plan'}, {'summary': 'semantic rejection'}, False),
                ('EX-import', {'role': 'intent_interpretation', 'stage': 'interpret', 'previous_import_id': 'IM-1',
                               'target': 'UI-original'}, {'summary': 'reauthor interpretation'}, True),
                ('EX-work', {'role': 'research_work'}, {'summary': 'first proposal'}, True),
                ('EX-revise', {'role': 'research_work'}, {'summary': 'replacement proposal'}, True)]:
            r['executions'][identifier] = {'id': identifier, 'role': action['role'], 'status': 'ended'}
            revisions.bind_repetition_bases(i, r, action)
            revisions.record_import_rework(i, r, action, identifier, clock=_entry.ports.clock)
            revisions.record_execution_outcome(i, r, action, output, identifier, accepted=accepted, clock=_entry.ports.clock)
        counts = task_contracts.repetition_lineages(r)
        self.assertTrue(all(row['events'] for row in counts.values()))
        self.assertEqual(counts['proposal_version']['by_lineage'], {'KN-first': 2})
        self.assertEqual(counts['contract_revision']['count'], 1)
        self.assertEqual(counts['exhaustion_empty']['count'], 0)

    def test_a_technical_retry_does_not_reset_the_configured_user_limit(self):
        from support.entry import entry
        _entry = entry()
        i = {'config': {'selection_failure_limit': 1}}
        r = {'history': [], 'queue': [], 'executions': {}}
        revisions.record_repetition(i, r, lineage='selection_failure', lineage_id='population', event_ref='EX-bad',
                                    outcome='rejected', owner='ai', reason='missing dispositions', clock=_entry.ports.clock)
        action = {'id': 'AC-retry', 'role': 'research_plan', 'continuation_of': 'EX-bad',
                  'repetition_bases': {'selection_failure': 'population'}}
        r['executions']['EX-bad'] = {'id': 'EX-bad', 'role': 'research_plan', 'action': {'id': 'AC-retry'}, 'status': 'ended'}
        self.assertTrue(revisions.action_repetition_waits(i, r, action))
        r['executions']['EX-op'] = {'id': 'EX-op', 'role': 'operational_review', 'status': 'ended', 'outcome': 'output_accepted'}
        r['operational_dispositions'] = {'OD-1': {'id': 'OD-1', 'execution_id': 'EX-op', 'target_execution_id': 'EX-bad',
                                                  'status': 'applied',
                                                  'disposition': {'kind': 'retry', 'basis_refs': ['EX-bad'],
                                                                  'next_owner': 'research_plan', 'reason': 'fixed input manifest',
                                                                  'scope': 'repeat only the held plan',
                                                                  'replay_safety': 'no external effects'}}}
        self.assertTrue(revisions.action_repetition_waits(i, r, action))
        self.assertEqual(task_contracts.repetition_lineages(r)['selection_failure']['count'], 1)
        self.assertEqual(revisions.repetition_hold(r, 'selection_failure', 'population')['owner'], 'user')

    def test_new_request_ids_do_not_reset_semantic_lineage(self):
        t, i, r = approved_task()
        a = {'id': 'AC-1', 'role': 'research_plan'}
        b = {'id': 'AC-2', 'role': 'research_plan'}
        revisions.bind_repetition_bases(i, r, a)
        revisions.bind_repetition_bases(i, r, b)
        self.assertEqual(a['repetition_bases'], b['repetition_bases'])
        i['sources'][0]['sha256'] = 'b' * 64
        c = {'id': 'AC-3', 'role': 'research_plan'}
        revisions.bind_repetition_bases(i, r, c)
        self.assertNotEqual(a['repetition_bases'], c['repetition_bases'])

    def test_one_case_grant_is_available_before_reservation_but_not_after_other_use(self):
        from support.entry import entry
        _entry = entry()
        t, i, r = approved_task()
        i['grants']['GR-1']['reuse'] = 'once'
        approve_task(t, i, r)
        self.assertEqual(planning.task_ready(t, i, r, evaluation_context={'now': _entry.ports.clock.now(), 'host_id': _entry.host_id})['state'], 'ready')
        r['executions']['EX-used'] = {'id': 'EX-used', 'grant_id': 'GR-1', 'role': 'research_work', 'status': 'ended',
                                      'action': {'id': 'AC-other'}}
        self.assertEqual(planning.task_ready(t, i, r, evaluation_context={'now': _entry.ports.clock.now(), 'host_id': _entry.host_id})['state'], 'not_ready')

    def test_one_regeneration_diagnosis_waits_for_a_new_basis_after_its_attempt(self):
        from support.entry import entry
        _entry = entry()
        for outcome in ('output_accepted', 'execution_incomplete'):
            with self.subTest(outcome=outcome):
                instance = {'id': 'IN-one', 'goal_status': 'unresolved', 'sources': []}
                runtime = {'status': 'active', 'tasks': {}, 'queue': [], 'executions': {}, 'events': [], 'pending_events': [],
                           'history': [{'kind': 'task_repetition', 'lineage': 'exhaustion_empty', 'lineage_id': 'basis-one',
                                        'outcome': 'empty', 'event_ref': 'EX-prepare', 'reason': 'No candidate available'}]}
                planning.schedule_reconsideration(instance, runtime, now='2026-09-20T00:00:00Z', clock=_entry.ports.clock)
                action = deepcopy(runtime['queue'].pop())
                self.assertEqual(action['role'], 'research_plan')
                runtime['executions']['EX-plan'] = {'id': 'EX-plan', 'role': 'research_plan', 'status': 'ended',
                                                    'outcome': outcome, 'action': action}
                planning.schedule_reconsideration(instance, runtime, now='2026-09-20T00:00:01Z', clock=_entry.ports.clock)
                self.assertEqual(runtime['queue'], [])
                instance['sources'].append({'id': 'SO-new', 'sha256': 'a' * 64})
                planning.schedule_reconsideration(instance, runtime, now='2026-09-20T00:00:02Z', clock=_entry.ports.clock)
                self.assertEqual(len(runtime['queue']), 1)
                self.assertNotEqual(runtime['queue'][0]['exhaustion_event_ref'], action['exhaustion_event_ref'])

    def test_empty_regeneration_cannot_immediately_repeat_and_periodic_is_independent(self):
        from support.entry import entry
        _entry = entry()
        i = {'id': 'IN-1', 'goal_status': 'unresolved', 'config': deepcopy(DEFAULT_CONFIG)}
        r = {'status': 'active', 'tasks': {}, 'queue': [], 'executions': {}, 'events': [], 'pending_events': [], 'history': []}
        planning.schedule_reconsideration(i, r, now='2026-09-20T00:00:00Z', clock=_entry.ports.clock)
        exhausted = next(e for e in r['events'] if e['kind'] == 'research_exhausted')
        self.assertEqual(exhausted['observed_at'], '2026-09-20T00:00:00Z')
        self.assertIsNone(exhausted['regenerate_after'])
        jsonschema.validate(exhausted, default_state_contract().family('runtime', 'events').schema)
        r['queue'] = []
        revisions.record_repetition(i, r, lineage='exhaustion_empty', lineage_id='basis-1', event_ref='EX-empty',
                                    outcome='empty', owner='ai', reason='no candidate', clock=_entry.ports.clock)
        planning.schedule_reconsideration(i, r, now='2026-09-20T00:00:01Z', clock=_entry.ports.clock)
        self.assertFalse(any(a['role'] == 'research_preparation' for a in r['queue']))
        r['next_research_reconsider_at'] = '2026-09-20T00:00:02Z'
        planning.record_due_events(i, r, '2026-09-20T00:00:03Z')
        planning.schedule_reconsideration(i, r, now='2026-09-20T00:00:03Z', clock=_entry.ports.clock)
        self.assertTrue(any(a['role'] == 'research_preparation' for a in r['queue']))

    def test_repetition_threshold_counts_validation_failures_once_per_execution(self):
        from support.entry import entry
        _entry = entry()
        instance = {'id': 'IN-1', 'config': {'selection_failure_limit': 2}}
        runtime = {'history': [], 'queue': [], 'executions': {}}
        action = {'role': 'research_plan', 'repetition_bases': {'selection_failure': 'population-1'}}
        for number, failure in enumerate(('output_validation', 'output_schema')):
            identifier = 'EX-' + str(number)
            runtime['executions'][identifier] = {'role': 'research_plan', 'error_kind': failure}
            for _ in range(2):
                revisions.record_execution_outcome(instance, runtime, action, {}, identifier, accepted=False, clock=_entry.ports.clock)
            count = task_contracts.repetition_lineages(runtime)['selection_failure']['count']
            self.assertEqual(count, number + 1)
        self.assertTrue(revisions.repetition_hold(runtime, 'selection_failure', 'population-1'))
        self.assertFalse(revisions.repetition_hold(runtime, 'selection_failure', 'population-2'))

    def test_technical_plan_failures_do_not_count_and_acceptance_ends_the_sequence(self):
        from support.entry import entry
        _entry = entry()
        instance = {'id': 'IN-1'}
        runtime = {'history': [], 'queue': [], 'executions': {}}
        action = {'role': 'research_plan', 'repetition_bases': {'selection_failure': 'population-1'}}
        for number, failure in enumerate(('currentness_changed', 'publication_failure', 'input_failure')):
            identifier = 'EX-technical-' + str(number)
            runtime['executions'][identifier] = {'role': 'research_plan', 'error_kind': failure}
            revisions.record_execution_outcome(instance, runtime, action, {}, identifier, accepted=False, clock=_entry.ports.clock)
        self.assertEqual(task_contracts.repetition_lineages(runtime)['selection_failure']['count'], 0)
        runtime['executions']['EX-invalid'] = {'role': 'research_plan', 'error_kind': 'output_validation'}
        revisions.record_execution_outcome(instance, runtime, action, {}, 'EX-invalid', accepted=False, clock=_entry.ports.clock)
        self.assertEqual(task_contracts.repetition_lineages(runtime)['selection_failure']['count'], 1)
        runtime['executions']['EX-accepted'] = {'role': 'research_plan'}
        revisions.record_execution_outcome(instance, runtime, action, {}, 'EX-accepted', accepted=True, clock=_entry.ports.clock)
        self.assertEqual(task_contracts.repetition_lineages(runtime)['selection_failure']['count'], 0)

    def test_repetition_receipt_produces_followup_once(self):
        from support.entry import entry
        _entry = entry()
        runtime = {'history': [], 'queue': [], 'question_links': []}
        for _ in range(2):
            revisions.record_repetition({}, runtime, lineage='selection_failure', lineage_id='IN-1', event_ref='EX-failed',
                                        outcome='rejected', owner='ai', reason='schema repair', clock=_entry.ports.clock)
        self.assertEqual(len(runtime['history']), 1)
        self.assertEqual(len(runtime['queue']), 1)
        self.assertEqual(runtime['queue'][0]['role'], 'operational_review')
        self.assertFalse(runtime['question_links'])


class PreparationReceiptClassificationTests(unittest.TestCase):
    def test_rejected_preparation_does_not_count_as_an_empty_research_result(self):
        from support.entry import entry
        _entry = entry()
        for failure in ('output_validation', 'currentness_changed', 'output_contract'):
            with self.subTest(failure=failure):
                instance = {'id': 'I', 'config': {'exhaustion_empty_limit': 1}}
                action = {'role': 'research_preparation', 'repetition_bases': {'exhaustion_empty': 'same-input'}}
                runtime = {'tasks': {}, 'queue': [], 'history': [], 'executions': {
                    'EX-failed': {'id': 'EX-failed', 'role': 'research_preparation',
                                  'error_kind': failure, 'observed_at': '2026-09-20T00:00:00Z'}}}
                revisions.record_execution_outcome(instance, runtime, action,
                                                   {'regenerate_after': '2026-09-21T00:00:00Z'}, 'EX-failed', accepted=False, clock=_entry.ports.clock)
                self.assertEqual(runtime['history'], [])
                self.assertEqual(runtime['queue'], [])
                self.assertFalse(revisions.action_repetition_waits(instance, runtime, action))
                runtime['executions']['EX-empty'] = {'id': 'EX-empty', 'role': 'research_preparation'}
                revisions.record_execution_outcome(instance, runtime, action, {}, 'EX-empty', accepted=True, clock=_entry.ports.clock)
                self.assertEqual(task_contracts.repetition_lineages(runtime)['exhaustion_empty']['count'], 1)
                self.assertTrue(revisions.repetition_hold(runtime, 'exhaustion_empty', 'same-input'))

    def test_partially_accepted_contract_still_records_its_real_production(self):
        from support.entry import entry
        _entry = entry()
        value, instance, runtime = approved_task()
        value['producer_execution'] = 'EX-partial'
        runtime['executions']['EX-partial'] = {'id': 'EX-partial', 'role': 'research_preparation'}
        action = {'role': 'research_preparation', 'repetition_bases': {'exhaustion_empty': 'same-input'}}
        revisions.record_execution_outcome(instance, runtime, action, {}, 'EX-partial', accepted=False, clock=_entry.ports.clock)
        receipts = [r for r in runtime['history'] if r.get('lineage') == 'exhaustion_empty']
        self.assertEqual([r['outcome'] for r in receipts], ['contracts_preserved'])
        self.assertEqual(task_contracts.repetition_lineages(runtime)['contract_revision']['count'], 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
