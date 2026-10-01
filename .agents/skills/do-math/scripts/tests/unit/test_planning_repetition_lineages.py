"""Repetition lineages: how repeated generations and receiver failures are counted, held and released, and when a
preparation must name its regeneration time (``revisions``, ``governance.apply_decision``, ``submission``; layer 2),
moved from ``test_repetition`` (``RepetitionLineageTests``).

The tests call the product's pure functions on plain records; nothing of the
product is replaced. The legacy continuation test took its instance and runtime
from an in-memory engine (``engine_fixtures.routing_engine``) whose methods it
never called; here the same records are built directly.
"""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from do_math import contracts, governance, integration, revisions, submission, task_contracts
from do_math.configuration import DEFAULT_CONFIG
from support.state_builders import governance_start


def routing_state():
    """The instance and runtime ``engine_fixtures.routing_engine`` holds: a governed instance ``RI-test``, nothing run."""
    instance = governance_start({'id': 'RI-test', 'knowledge': {}, 'relations': [], 'goal_status': 'unresolved',
                                 'config': {'goal_auditors': 2, 'max_artifact_bytes': DEFAULT_CONFIG['max_artifact_bytes']}})
    runtime = {'tasks': {}, 'activities': {}, 'executions': {}, 'queue': [], 'questions': [], 'question_links': [],
               'history': [], 'inputs': [], 'interpretations': {}, 'status': 'ready'}
    return instance, runtime


class RepetitionLineageTests(unittest.TestCase):
    def test_continue_after_successful_empty_preparation_creates_its_missing_request(self):
        from support.entry import entry
        _entry = entry()
        instance, runtime = routing_state()
        instance['config']['exhaustion_empty_limit'] = 1
        instance['governance_sources'] = {'UI-source': governance.preserve_source(
            'UI-source', 'Continue the held empty preparation.', origin='user')}
        original = {'id': 'AC-original', 'role': 'research_preparation'}
        revisions.bind_repetition_bases(instance, runtime, original)
        runtime['executions']['EX-empty'] = {'id': 'EX-empty', 'role': 'research_preparation',
            'status': 'ended', 'outcome': 'output_accepted', 'action': original}
        revisions.record_execution_outcome(instance, runtime, original,
            {'summary': 'No candidate'}, 'EX-empty', accepted=True, clock=_entry.ports.clock)
        key = original['repetition_bases']['exhaustion_empty']
        allowed = {'id': 'AC-next', 'role': 'research_preparation', 'revision_targets': {},
                   'repetition_bases': {'exhaustion_empty': key}}
        change = {'kind': 'repetition_continue', 'decision_id': 'DC-continue', 'lineage': 'exhaustion_empty',
                  'lineage_id': key, 'hold_event_ref': 'EX-empty', 'allowed_action': allowed}
        instance, runtime, _ = governance.apply_decision(instance, runtime, change, source_ref='UI-source', clock=_entry.ports.clock)
        self.assertEqual([a['id'] for a in runtime['queue']], ['AC-next'])
        self.assertFalse(revisions.action_repetition_waits(instance, runtime, runtime['queue'][0]))
        self.assertEqual(revisions.action_scope(runtime['queue'][0]), allowed)

    def test_supplement_does_not_increment_or_reset_empty_generation(self):
        from support.entry import entry
        _entry = entry()
        instance = {'id': 'RI', 'config': {}}
        runtime = {'tasks': {}, 'queue': [], 'history': [], 'executions': {}}
        revisions.record_repetition(instance, runtime, lineage='exhaustion_empty', lineage_id='basis',
            event_ref='EX-empty', outcome='empty', owner='ai', reason='No candidates', clock=_entry.ports.clock)
        before = deepcopy(runtime['history'])
        for field in ('assessment_targets', 'observation_rule_targets'):
            action = {'role': 'research_preparation', field: {'TK': {}}}
            runtime['executions']['EX-supplement'] = {'role': action['role']}
            revisions.record_execution_outcome(instance, runtime, action, {'summary': 'Supplement applied'},
                                               'EX-supplement', accepted=True, clock=_entry.ports.clock)
        self.assertEqual(runtime['history'], before)
        runtime['history'].append({'kind': 'repetition_hold', 'lineage': 'exhaustion_empty',
            'lineage_id': 'basis', 'event_ref': 'EX-empty', 'owner': 'user'})
        action.update(repetition_bases={'exhaustion_empty': 'basis'}, observation_rule_targets={})
        self.assertFalse(revisions.action_repetition_waits(instance, runtime, action))
        runtime['tasks']['TK'] = {'id': 'TK'}
        runtime['history'].append({'kind': 'repetition_hold', 'lineage': 'contract_revision',
            'lineage_id': 'TK', 'event_ref': 'EX-revision', 'owner': 'user'})
        action['observation_rule_targets'] = {'TK': {}}
        self.assertEqual([row['lineage'] for row in revisions.action_repetition_waits(instance, runtime, action)], ['contract_revision'])

    def test_receiver_failure_categories_count_once_and_success_ends_streak(self):
        from support.entry import entry
        _entry = entry()
        instance = {'id': 'RI', 'config': {}}
        runtime = {'queue': [], 'executions': {}, 'history': []}
        action = {'role': 'research_plan', 'repetition_bases': {'selection_failure': 'basis'}}
        for index, rule in enumerate(('schema.required', 'submission.parse', 'integration.application')):
            eid = 'EX-' + str(index)
            runtime['executions'][eid] = {'role': action['role'], 'error_kind': integration.failure_kind([
                integration.issue(rule, 'output', 'message deliberately contains no classification hints')])}
            for _ in range(2):
                revisions.record_execution_outcome(instance, runtime, action, {}, eid, accepted=False, clock=_entry.ports.clock)
        self.assertEqual(task_contracts.repetition_lineages(runtime)['selection_failure']['count'], 3)
        for kind in ('currentness_changed', 'publication_failure', 'input_failure'):
            runtime['executions'][kind] = {'role': action['role'], 'error_kind': kind}
            revisions.record_execution_outcome(instance, runtime, action, {}, kind, accepted=False, clock=_entry.ports.clock)
        self.assertEqual(task_contracts.repetition_lineages(runtime)['selection_failure']['count'], 3)
        runtime['executions']['EX-good'] = {'role': action['role']}
        revisions.record_execution_outcome(instance, runtime, action, {}, 'EX-good', accepted=True, clock=_entry.ports.clock)
        self.assertEqual(task_contracts.repetition_lineages(runtime)['selection_failure']['count'], 0)

    def test_generation_time_uses_fixed_machine_observation_and_excludes_supplement(self):
        from support.entry import entry
        _entry = entry()
        action = {'role': 'research_preparation'}
        schema = contracts.action_schema(action)
        self.assertIn('regenerate_after', schema['required'])
        supplemental = contracts.action_schema({**action, 'assessment_targets': {}})
        self.assertNotIn('regenerate_after', supplemental['properties'])
        context = {'action': action, 'observed_at': '2026-09-23T00:00:00Z',
                   'tasks': [], 'kind_definitions': {}, 'knowledge_catalog': [], 'available_input_refs': []}
        output = {'summary': 'No candidates', 'used_sources': [], 'questions': [], 'candidates': []}
        with tempfile.TemporaryDirectory() as directory:
            for time, invalid in (('2026-09-23T01:00:00Z', False), ('2026-09-22T23:00:00Z', True),
                                  ('2026-09-23T01:00:00', True)):
                issues = submission._payload_issues({**output, 'regenerate_after': time}, schema, context, {}, Path(directory), clock=_entry.ports.clock)
                self.assertEqual(any(i.get('rule_id') == 'submission.regeneration_time' for i in issues), invalid, issues)

    def test_generation_time_is_checked_only_when_no_candidate_is_proposed(self):
        from support.entry import entry
        _entry = entry()
        from support.role_answers import candidate
        action = {'role': 'research_preparation'}
        schema = contracts.action_schema(action)
        context = {'action': action, 'observed_at': '2026-09-23T00:00:00Z',
                   'tasks': [], 'kind_definitions': {}, 'knowledge_catalog': [], 'available_input_refs': []}
        proposed = {'summary': 'One candidate', 'used_sources': [], 'questions': [], 'candidates': [candidate('one')]}
        empty = {**proposed, 'summary': 'No candidates', 'candidates': []}
        with tempfile.TemporaryDirectory() as directory:
            for output, time, invalid in ((proposed, None, False), (proposed, '2026-09-22T23:00:00Z', False),
                                          (empty, None, True)):
                issues = submission._payload_issues({**output, 'regenerate_after': time}, schema, context, {}, Path(directory), clock=_entry.ports.clock)
                self.assertEqual(any(i['path'] == 'output/regenerate_after' for i in issues), invalid, issues)


if __name__ == '__main__':
    unittest.main()
