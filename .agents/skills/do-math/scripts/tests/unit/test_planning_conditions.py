"""Task conditions, readiness and plan inputs (``planning``, ``task_scope``; layer 2), moved from ``test_planning``.

Every test calls the product's pure functions on plain records
(``record_fixtures``, ``knowledge_fixtures``); nothing of the product is
replaced. Two legacy tests patched the product: the index scan count is now
observed on the unchanged ``planning.record_index`` (``ObservedCalls``), and the
historical goal judgment now stands on knowledge whose identity links are real
(``knowledge_fixtures.verified_knowledge``) instead of a patched
``knowledge_records.usable_links``. The artifact reader and validator of an
evaluation context are the caller's callables, so the tests still pass
counting doubles there. The two document tests read the skill's
``references/과제-착수조건.md``.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import unittest
from unittest.mock import Mock
import uuid

from do_math import planning, task_scope
from do_math.state_contract import ARTIFACT_ROOT
from support.record_builders import approve_task, approved_task
from support.provider_probes import ObservedCalls

READINESS_DOCUMENT = Path(__file__).resolve().parents[3] / 'references' / '과제-착수조건.md'


class ActivityConditionTests(unittest.TestCase):
    def test_activity_kind_uses_the_stored_activity_contract(self):
        from do_math.activities import open_activity
        runtime = {'activities': {}, 'executions': {}}
        open_activity(runtime, activity_id='AT-kind', activity_kind='research_work',
                      owner_ref='TK-kind', input_refs=[], opened_at='2026-09-25T00:00:00Z')
        condition = {'op': 'record_field_equals', 'space': 'runtime', 'family': 'activity',
                     'record_id': 'AT-kind', 'pointer': '/activity_kind', 'value': 'research_work'}
        planning.validate_condition(condition)
        self.assertEqual(planning.evaluate_condition(condition, {}, runtime)['state'], 'ready')
        self.assertEqual(planning.evaluate_condition(
            {**condition, 'value': 'maintenance'}, {}, runtime)['state'], 'not_ready')
        self.assertEqual(planning.evaluate_condition(
            {**condition, 'record_id': 'AT-missing'}, {}, runtime)['state'], 'not_ready')
        with self.assertRaisesRegex(ValueError, 'exposed machine field'):
            planning.validate_condition({**condition, 'pointer': '/role'})


class PlanningTests(unittest.TestCase):
    def setUp(self):
        self.task, self.instance, self.runtime = approved_task()
        self.instance['knowledge'] = {'K': {'id': 'K', 'lifecycle': 'active', 'kind': 'lemma'}}

    def condition(self, op='record_exists', **changes):
        return dict(op=op, space='research', family='knowledge', record_id='K', **changes)

    def test_conditions_and_errors_preserve_basis(self):
        condition = {'op': 'all', 'args': [self.condition(), self.condition('record_field_equals', pointer='/kind', value='lemma')]}
        before = deepcopy(self.instance)
        result = planning.evaluate_condition(condition, self.instance, self.runtime)
        self.assertEqual(result['state'], 'ready')
        self.assertEqual(len(result['basis']), 2)
        self.assertEqual(before, self.instance)
        self.instance['knowledge']['K']['kind'] = 'theorem'
        self.assertEqual(planning.evaluate_condition(condition, self.instance, self.runtime)['state'], 'not_ready')
        changed = planning.evaluate_condition(self.condition(), self.instance, self.runtime)
        self.assertNotEqual(changed['basis'][0]['sha256'], result['basis'][0]['sha256'])
        for invalid in [{'op': 'unknown'}, self.condition('record_field_equals', pointer='/question', value=1),
                        {'op': 'any', 'args': [{'op': 'always'}, {'op': 'unknown'}]}]:
            self.assertEqual(planning.evaluate_condition(invalid, self.instance, self.runtime)['state'], 'evaluation_error')
        self.instance['knowledge'].clear()
        result = planning.evaluate_condition(self.condition(), self.instance, self.runtime)
        self.assertEqual(result['state'], 'not_ready')
        self.assertIn('absencequery', result['basis'][0])

    def test_instance_conditions_and_bases_read_one_projection_of_either_instance_form(self):
        from support.entry import entry
        _entry = entry()
        from do_math.initialization import governance_working_view
        editions = planning.governance_revisions(self.instance)
        self.task['occurrence_condition'] = {'op': 'record_field_equals', 'space': 'research', 'family': 'instance',
                                             'record_id': self.instance['id'], 'pointer': '/goal_revision',
                                             'value': editions['goal_revision']}
        approve_task(self.task, self.instance, self.runtime)
        view = governance_working_view(self.instance)
        self.assertEqual(planning.task_ready(self.task, self.instance, self.runtime, evaluation_context={'now': _entry.ports.clock.now(), 'host_id': _entry.host_id})['state'], 'ready')
        self.assertEqual(planning.task_ready(self.task, view, self.runtime, evaluation_context={'now': _entry.ports.clock.now(), 'host_id': _entry.host_id}),
                         planning.task_ready(self.task, self.instance, self.runtime, evaluation_context={'now': _entry.ports.clock.now(), 'host_id': _entry.host_id}))
        basis = planning.capture_task_basis(self.task, self.instance, self.runtime)
        self.assertEqual(planning.capture_task_basis(self.task, view, self.runtime), basis)
        # The instance record is its projection, not the whole research state.
        self.instance['knowledge']['K']['kind'] = 'theorem'
        self.assertEqual(planning.capture_task_basis(self.task, self.instance, self.runtime), basis)

    def test_artifact_condition_grammar_is_the_reader_prefix_and_state_segments(self):
        ref = {'snapshot': 'SN-1', 'sha256': hashlib.sha256(b'x').hexdigest()}
        planning.validate_condition({'op': 'artifact_valid', 'artifact_ref': {**ref, 'path': ARTIFACT_ROOT + 'BA-1/proof.txt'}})
        # Outside the root the reader prefix rejects the path; below it each segment follows the state path rule.
        for path, reason in (('out/proof.txt', '^artifact path must name an archived artifact under runtime/artifacts/$'),
                             (ARTIFACT_ROOT + 'BA-1/../proof.txt', '^path contains an invalid segment$'),
                             (ARTIFACT_ROOT + 'BA-1/con.txt', '^path contains a reserved Windows device name$'),
                             (ARTIFACT_ROOT + 'BA-1/a:b.txt', '^path contains a Windows-invalid segment$'),
                             (ARTIFACT_ROOT, '^path contains an invalid segment$')):
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, reason):
                planning.validate_condition({'op': 'artifact_valid', 'artifact_ref': {**ref, 'path': path}})

    def test_task_ready_rechecks_reviews_inputs_and_conditions(self):
        from support.entry import entry
        _entry = entry()
        self.assertEqual(planning.task_ready(self.task, self.instance, self.runtime, evaluation_context={'now': _entry.ports.clock.now(), 'host_id': _entry.host_id})['state'], 'ready')
        self.task['reviews'][0]['revision'] = 2
        self.assertEqual(planning.task_ready(self.task, self.instance, self.runtime, evaluation_context={'now': _entry.ports.clock.now(), 'host_id': _entry.host_id})['state'], 'not_ready')
        self.task['occurrence_condition'] = self.condition('record_lifecycle_is', value='withdrawn')
        approve_task(self.task, self.instance, self.runtime)
        self.assertEqual(planning.task_ready(self.task, self.instance, self.runtime, evaluation_context={'now': _entry.ports.clock.now(), 'host_id': _entry.host_id})['state'], 'not_ready')

    def test_contract_hash_only_changes_for_contract_fields(self):
        baseline = planning.contract_hash(self.task)
        self.task.update(status='waiting', waiting={'kind': 'external_event'}, history=['bookkeeping'])
        self.assertEqual(planning.contract_hash(self.task), baseline)
        self.task['question'] = 'changed'
        self.assertNotEqual(planning.contract_hash(self.task), baseline)

    def test_a_revision_request_of_an_earlier_revision_is_already_answered(self):
        task = {'revision': 2, 'reviews': [], 'revision_requested': {'revision': 1, 'source': 'EX-review'}}
        self.assertFalse(planning.revision_requested(task))
        self.assertFalse(planning.revision_required(task))
        task['revision_requested']['revision'] = 2
        self.assertTrue(planning.revision_requested(task))
        self.assertTrue(planning.revision_required(task))

    def test_periodic_exploration_is_not_consumed_by_preparation_only(self):
        from support.entry import entry
        _entry = entry()
        from do_math.model_policy import preparation_only
        for field in ('assessment_targets', 'observation_rule_targets'):
            with self.subTest(field=field):
                runtime = deepcopy(self.runtime)
                supplement = {'id': 'AC-supplement', 'role': 'research_preparation',
                              field: {self.task['id']: {'revision': self.task['revision'],
                                                        'contract_sha256': planning.contract_hash(self.task)}}}
                runtime.update(status='active', queue=[supplement], executions={},
                               waiting_actions={}, events=[], pending_events=[],
                               next_research_reconsider_at='2026-09-24T00:00:00Z')
                original = deepcopy(supplement)
                planning.record_due_events(self.instance, runtime, '2026-09-25T00:00:00Z')
                planning.schedule_reconsideration(self.instance, runtime, now='2026-09-25T00:00:00Z', clock=_entry.ports.clock)
                self.assertEqual(supplement, original)
                general = [a for a in runtime['queue']
                           if a['role'] == 'research_preparation' and not preparation_only(a)]
                self.assertEqual(len(general), 1)
                due = [e['id'] for e in runtime['events'] if e['kind'] == 'research_reconsider_due']
                self.assertEqual(general[0]['event_refs'], due)
                self.assertTrue(general[0]['periodic_reconsideration'])
                # Assignment lives in the request's event_refs; published events carry no mark.
                self.assertFalse(any('assigned_to' in event for event in runtime['events']))
                planning.record_due_events(self.instance, runtime, '2026-09-25T00:00:01Z')
                planning.schedule_reconsideration(self.instance, runtime, now='2026-09-25T00:00:01Z', clock=_entry.ports.clock)
                self.assertEqual(len(runtime['queue']), 2)

    def test_due_events_are_unique_and_paused_preserves_pending(self):
        self.runtime['next_research_reconsider_at'] = '2026-01-01T00:00:00Z'
        self.task.update(newinput='RQ-source')
        events = planning.collect_due_events(self.instance, self.runtime, '2026-01-02T00:00:00Z')
        self.assertEqual(sorted(e['kind'] for e in events), ['research_reconsider_due', 'task_new_input'])
        self.assertEqual(len(events), len({e['id'] for e in events}))
        self.runtime['status'] = 'paused'
        recorded = planning.record_due_events(self.instance, self.runtime, '2026-01-02T00:00:00Z')
        self.assertEqual(self.runtime['pending_events'], [e['id'] for e in recorded])
        self.assertEqual(planning.record_due_events(self.instance, self.runtime, '2026-01-02T00:00:00Z'), [])

    def test_one_input_request_is_one_event_across_observations_and_scheduling(self):
        from support.entry import entry
        _entry = entry()
        self.task.update(newinput='RQ-source')
        first = planning.record_due_events(self.instance, self.runtime, '2026-01-02T00:00:00Z')
        self.assertEqual([(e['kind'], e['request_id']) for e in first], [('task_new_input', 'RQ-source')])
        self.assertEqual(planning.record_due_events(self.instance, self.runtime, '2026-01-02T00:00:05Z'), [])
        planning.schedule_reconsideration(self.instance, self.runtime, now='2026-01-02T00:00:05Z', clock=_entry.ports.clock)
        inputs = [e for e in self.runtime['events'] if e['kind'] == 'task_new_input']
        self.assertEqual([e['id'] for e in inputs], [first[0]['id']])
        self.assertEqual(self.runtime['pending_events'].count(first[0]['id']), 1)
        self.task.update(newinput='RQ-later')
        later = planning.record_due_events(self.instance, self.runtime, '2026-01-02T00:00:09Z')
        self.assertEqual([e['request_id'] for e in later], ['RQ-later'])

    def test_source_arrival_and_trust_transition_are_machine_conditions(self):
        condition = {'op': 'all', 'args': [
            {'op': 'record_exists', 'space': 'research', 'family': 'source', 'record_id': 'SO-new'},
            {'op': 'record_lifecycle_is', 'space': 'research', 'family': 'trust-environment', 'record_id': 'TE-1',
             'value': 'active'}]}
        self.assertEqual(planning.evaluate_condition(condition, self.instance, self.runtime)['state'], 'not_ready')
        self.instance['sources'].append({'id': 'SO-new', 'sha256': 'a' * 64})
        self.instance['trust_environments'] = {'TE-1': {'id': 'TE-1', 'status': 'active'}}
        self.assertEqual(planning.evaluate_condition(condition, self.instance, self.runtime)['state'], 'ready')
        self.instance['trust_environments']['TE-1']['status'] = 'invalid'
        self.assertEqual(planning.evaluate_condition(condition, self.instance, self.runtime)['state'], 'not_ready')

    def test_relation_condition_rechecks_its_proof_after_import(self):
        from support.entry import entry
        _entry = entry()
        from support.knowledge_builders import verified_knowledge
        from do_math import knowledge_records as kr
        i, r, kid, aid = verified_knowledge()
        fid = i['knowledge'][kid]['formal_result_id']
        xid = i['knowledge'][kid]['exposition_id']
        claim = {'kind': 'formally_implies', 'source': kid, 'target': kid, 'confirmed_scope': 'True implies True'}
        i['expositions'][xid]['relation_claim'] = claim
        i, aid = kr.record_identity_assessment(i, kid, {'decision': 'match', 'basis': kr.identity_basis(i, kid),
                                                        'cycle_id': 'RC-relation'}, 'policy:1', runtime=r, clock=_entry.ports.clock)
        relation = {'id': 'RL-1', 'kind': 'formally_implies', 'source': kid, 'target': kid,
                    'confirmed_scope': 'True implies True', 'evidence': 'reflexivity',
                    'formal_result_refs': [fid], 'assessment_refs': [aid]}
        i['relations'] = [relation]
        condition = {'op': 'relation_exists', 'subkind': 'formally_implies', 'from_id': kid, 'to_id': kid}
        actual = planning.evaluate_condition(condition, i, r)
        self.assertEqual(actual['state'], 'ready', actual)
        i['formal_results'][fid]['formal_use'] = 'suspended'
        self.assertNotEqual(planning.evaluate_condition(condition, i, r)['state'], 'ready')


class ConditionIndexTests(unittest.TestCase):
    def test_compound_condition_scans_one_population_and_rechecks_the_next_evaluation(self):
        instance = {'knowledge': {'K' + str(i): {'id': 'K' + str(i)} for i in range(200)}}
        condition = {'op': 'all', 'args': [
            {'op': 'record_exists', 'space': 'research', 'family': 'knowledge', 'record_id': 'K' + str(i)}
            for i in range(50)]}
        # Every start of the unchanged record_index is counted, from any caller.
        with ObservedCalls(record_index=planning.record_index) as scans:
            result = planning.evaluate_condition(condition, instance, {})
        self.assertEqual(scans.count('record_index'), 1)
        self.assertEqual(result['state'], 'ready')
        self.assertEqual(len(result['basis']), 50)
        del instance['knowledge']['K0']
        self.assertEqual(planning.evaluate_condition(condition, instance, {})['state'], 'not_ready')
        duplicate = {'tasks': {'K1': {'id': 'K1'}}}
        result = planning.evaluate_condition(condition, instance, duplicate)
        self.assertEqual(result['state'], 'evaluation_error')
        self.assertIn('duplicate', result['errors'][0])
        wrong_family = {'op': 'record_exists', 'space': 'runtime', 'family': 'task', 'record_id': 'K1'}
        result = planning.evaluate_condition(wrong_family, instance, {})
        self.assertEqual(result['state'], 'evaluation_error')
        self.assertIn('another family', result['errors'][0])


class ArtifactConditionTests(unittest.TestCase):
    def test_artifact_condition_reads_and_validates_a_sealed_artifact_once(self):
        raw = b'{"result": true}'
        ref = {'snapshot': 'a' * 40, 'path': 'runtime/artifacts/BA-cond/result.json',
               'sha256': hashlib.sha256(raw).hexdigest()}
        read, validate = Mock(return_value=raw), Mock(return_value=True)
        # A fresh git_dir: the verdict cache is keyed by repository, so no earlier test's entry answers.
        context = {'snapshot': 'b' * 40, 'read_artifact': read, 'validate_artifact': validate,
                   'git_dir': 'git-' + uuid.uuid4().hex, 'now': '2026-09-26T00:00:00+00:00'}
        condition = {'op': 'artifact_valid', 'artifact_ref': ref}
        for _ in range(3):
            self.assertEqual(planning.evaluate_condition(condition, {}, {}, evaluation_context=context)['state'], 'ready')
        self.assertEqual((read.call_count, validate.call_count), (1, 1))

    def test_artifact_verdict_belongs_to_its_validator_and_needs_no_repository(self):
        raw = b'{"result": true}'
        ref = {'snapshot': 'a' * 40, 'path': 'runtime/artifacts/BA-verdict/result.json',
               'sha256': hashlib.sha256(raw).hexdigest()}
        read, accept, reject = Mock(return_value=raw), Mock(return_value=True), Mock(return_value=False)
        condition = {'op': 'artifact_valid', 'artifact_ref': ref}
        for validate, state in ((accept, 'ready'), (reject, 'evaluation_error'), (accept, 'ready'), (reject, 'evaluation_error')):
            context = {'snapshot': 'b' * 40, 'read_artifact': read, 'validate_artifact': validate,
                       'git_dir': None, 'now': '2026-09-26T00:00:00+00:00'}
            self.assertEqual(planning.evaluate_condition(condition, {}, {}, evaluation_context=context)['state'], state)
        # Without a repository the bytes are matched every time; each verdict is computed once.
        self.assertEqual((read.call_count, accept.call_count, reject.call_count), (4, 1, 1))


class ReadinessCopyTests(unittest.TestCase):
    def test_historical_judgment_cannot_override_changed_governance_or_sources(self):
        from support.knowledge_builders import verified_knowledge
        from do_math.knowledge_records import usable_links
        from support.record_builders import domain_governance
        # The judged knowledge is a verified theorem with a current identity link, so the
        # judgment's dependency is usable by the product's own rule (the legacy test patched it).
        instance = domain_governance()
        state, _, kid, _ = verified_knowledge()
        instance.update(state)
        instance['sources'] = [{'name': 'source', 'path': 'source.txt', 'sha256': 'a' * 64}]
        instance['knowledge'][kid]['task_id'] = 'TK-one'
        judgment = {'id': 'GJ-one', 'decision': 'satisfied', 'scope_complete': True, 'current': True,
                    'dependencies': [kid], 'record_basis': [], **planning.governance_revisions(instance),
                    'source_basis': deepcopy(instance['sources'])}
        instance['goal_judgments'] = [judgment]

        def judge():
            self.assertTrue(usable_links(instance, kid))  # only the source or the edition changes below
            return task_scope.designated_judgment({'id': 'TK-one'}, {'judges': ['goal_audit']},
                                                  {'evidence_refs': ['GJ-one']}, instance, {})
        self.assertEqual(judge(), 'GJ-one')
        instance['sources'][0]['sha256'] = 'b' * 64
        self.assertIsNone(judge())
        instance['sources'][0]['sha256'] = 'a' * 64
        judgment['goal_revision'] = 'old-edition'
        self.assertIsNone(judge())

    def test_borrowed_inputs_and_copied_results_match_prior_evaluation(self):
        from support.entry import entry
        _entry = entry()
        task, instance, runtime = approved_task()
        for scenario in ('ready', 'waiting', 'missing', 'invalid'):
            with self.subTest(scenario=scenario):
                value, state, working = deepcopy((task, instance, runtime))
                working['tasks'][value['id']] = value
                if scenario == 'waiting':
                    value['waiting'] = {'kind': 'external_event', 'next_owner': 'user', 'reason': 'wait'}
                elif scenario == 'missing':
                    value['inputs'].append('SO-missing')
                elif scenario == 'invalid':
                    value['occurrence_condition'] = {'op': 'unknown'}
                before = deepcopy((value, state, working))
                old = planning.task_ready(deepcopy(value), deepcopy(state), deepcopy(working), evaluation_context={'now': _entry.ports.clock.now(), 'host_id': _entry.host_id})
                result = deepcopy(planning.task_ready(value, state, working, evaluation_context={'now': _entry.ports.clock.now(), 'host_id': _entry.host_id}))
                self.assertEqual(result, old)
                self.assertEqual((value, state, working), before)
                if scenario == 'waiting':
                    self.assertIn(value['waiting'], result['waits'])
                    result['waits'][0]['reason'] = 'changed by result consumer'
                    self.assertEqual(value['waiting']['reason'], 'wait')


class ReadinessConditionTests(unittest.TestCase):
    def test_required_certification_condition_tracks_current_identity_effect(self):
        from support.knowledge_builders import verified_knowledge
        instance, runtime, kid, _ = verified_knowledge()
        condition = {'op': 'record_field_equals', 'space': 'research', 'family': 'knowledge',
                     'record_id': kid, 'pointer': '/usable_as_k', 'value': True}
        self.assertEqual(planning.evaluate_condition(condition, instance, runtime)['state'], 'ready')
        for use in instance['assessment_uses'].values():
            use['status'] = 'suspended'
        self.assertEqual(planning.evaluate_condition(condition, instance, runtime)['state'], 'not_ready')
        with self.assertRaisesRegex(ValueError, '^usable_as_k comparison requires a boolean$'):
            planning.validate_condition({**condition, 'value': 1})

    def test_documented_readiness_examples_match_the_live_grammar(self):
        blocks = re.findall(r'```json\s+(.*?)```', READINESS_DOCUMENT.read_text(encoding='utf-8'), re.S)
        self.assertGreaterEqual(len(blocks), 2)
        for block in blocks:
            value = json.loads(block)
            conditions = [value] if 'op' in value else [row['occurrence_condition'] for row in value['task_conditions']]
            for condition in conditions:
                planning.validate_condition(condition)

    def test_readiness_document_tables_match_the_condition_grammar(self):
        """Operations, record families with their space, and pointers agree with planning."""
        text = READINESS_DOCUMENT.read_text(encoding='utf-8')
        tables, current = {}, None
        for line in text.splitlines():
            if not line.startswith('|'):
                current = None
                continue
            cells = [cell.strip() for cell in line.strip().strip('|').split('|')]
            if current is None:
                current = tables.setdefault(cells[0], [])
            elif not set(cells[0]) <= set('-: '):
                current.append(cells)
        operations = {}
        for cells in tables['`op`']:
            for op in re.findall(r'`([^`]+)`', cells[0]):
                operations[op] = set(re.findall(r'`([^`]+)`', cells[1]))
        self.assertEqual(set(operations), set(planning.CONDITION_FIELDS))
        for op, fields in planning.CONDITION_FIELDS.items():
            self.assertLessEqual(fields, operations[op], op)
        listed = text.split('현재 기록 가족은', 1)[1].split('이다.', 1)[0]
        families = set(re.findall(r'`([^`]+)`', listed))
        self.assertEqual(families, set(planning.RECORD_FAMILIES))
        runtime_list = re.search(r'((?:`[^`]+`,\s*)*`[^`]+`)의 space는 `runtime`', text).group(1)
        runtime = set(re.findall(r'`([^`]+)`', runtime_list))
        self.assertEqual(runtime, {family for family, (space, _) in planning.RECORD_FAMILIES.items() if space == 'runtime'})
        self.assertEqual(families - runtime,
                         {family for family, (space, _) in planning.RECORD_FAMILIES.items() if space == 'research'})
        pointers = {re.findall(r'`([^`]+)`', cells[0])[0]: set(re.findall(r'`([^`]+)`', cells[1]))
                    for cells in tables['기록 가족']}
        self.assertEqual(pointers, {family: set(fields) for family, fields in planning.EXPOSED_FIELDS.items()})

    def test_nonformal_research_reuse_is_ready_but_not_certified(self):
        from support.entry import entry
        _entry = entry()
        from do_math.knowledge import assess_use
        from do_math.knowledge_records import create_candidate
        task, instance, runtime = approved_task()
        instance.setdefault('kind_definitions', {})['KD-observation'] = {'id': 'KD-observation', 'status': 'active'}
        instance, kid = create_candidate(instance, {'id': 'KN-computation', 'kind': 'observation',
                                                    'kind_definition_id': 'KD-observation',
                                                    'statement': 'Computed n=1 through 20',
                                                    'explanation': 'Bounded exact computation',
                                                    'summary': 'Finite evidence', 'dependencies': []},
                                         source_ref='SO-1', actor_ref='EX-compute', clock=_entry.ports.clock)
        task['reuse'] = [kid]
        approve_task(task, instance, runtime)
        self.assertFalse(assess_use(instance['knowledge'][kid], instance)['valid'])
        self.assertEqual(planning.task_ready(task, instance, runtime, evaluation_context={'now': _entry.ports.clock.now(), 'host_id': _entry.host_id})['state'], 'ready')
        for field, value in [('lifecycle', 'withdrawn'), ('use_suspended', True), ('kind_use_suspended', True)]:
            changed = deepcopy(instance)
            changed['knowledge'][kid][field] = value
            approve_task(task, changed, runtime)
            self.assertEqual(planning.task_ready(task, changed, runtime, evaluation_context={'now': _entry.ports.clock.now(), 'host_id': _entry.host_id})['state'], 'not_ready', field)


if __name__ == '__main__':
    unittest.main(verbosity=2)
