"""Model metadata stays off the authored wire: the receivers of preparation and planning assessments
(``planning_engine._apply_model_metadata``, ``_ensure_model_assessments``; layer 2), the coverage rule
(``model_policy.validate_assessments``), task contracts (``contracts.task_candidate_record``) and role
selection (``model_policy.selection``), moved from ``test_model_metadata_boundary``.

Assessments are recorded in the execution's ``model_decisions`` and in the
receiving task contract, never in the dispositions or candidates the model
authored. The engine tests run the real engine over a small state on the Git
fake (``support.provider_state``) instead of the legacy ``routing_engine``, an
engine object over a refusing store with three methods replaced by autospec
doubles (조사 S-04); those three are not on these paths. As in the legacy
tests, the model's extension and the tasks are put into the engine's runtime
and the method is called directly, as the receiver is.
"""
from copy import deepcopy
import json
from pathlib import Path
import re
import tempfile
import unittest

from do_math import model_policy
from do_math.configuration import DEFAULT_CONFIG
from do_math.contracts import task_candidate_record
from do_math.execution_profiles import build_profiles, profile_ref
from do_math.model_policy import LIMITS, assessment_basis
from support.record_builders import approved_task
from support.role_answers import candidate, disposition
from support.observation_inputs import prepared_rule_conditions
from support.default_responder import rating
from support.provider_state import engine_over

PLAN = {'role': 'research_plan'}


def coverage(missing=(), unexpected=()):
    """The exact coverage error of ``validate_assessments``, as an anchored pattern."""
    return '^' + re.escape('model assessment coverage: ' + json.dumps(
        {'missing': list(missing), 'unexpected': list(unexpected)})) + '$'


class EngineCase(unittest.TestCase):
    def engine(self):
        # The runtime families the legacy routing_engine held, stored empty (its ``interpretations``
        # is not a stored family and these receivers do not read it).
        engine, _ = engine_over(Path(self.enterContext(tempfile.TemporaryDirectory())), runtime={
            'tasks': {}, 'activities': {}, 'questions': [], 'question_links': [], 'history': []})
        self.assertEqual(engine.instance['config'], DEFAULT_CONFIG)
        return engine


class ModelMetadataBoundaryTests(EngineCase):
    def test_plan_receiver_records_model_decisions_without_changing_the_authored_dispositions(self):
        engine = self.engine()
        rating = {'difficulty': 'low', 'importance': 'medium', 'reason': 'The supplied bounded contract'}
        output = {'dispositions': [disposition('TK-selected'),
                                   disposition('TK-waiting', kind='not_selected')]}
        original = deepcopy(output)
        self.assertNotIn('TK-selected', engine.runtime['tasks'])
        engine.runtime['executions']['EX-plan'] = {'extensions': {
            'model_assessments': [{'task_id': 'TK-selected', **rating}]}}
        engine._apply_model_metadata(PLAN, output, 'EX-plan')
        self.assertEqual(engine.runtime['executions']['EX-plan']['model_decisions'], {'TK-selected': rating})
        self.assertEqual(output, original)
        # A selected task without a stored assessment must be rated; an unselected one must not be.
        engine.runtime['executions']['EX-plan']['extensions']['model_assessments'] = []
        with self.assertRaisesRegex(ValueError, coverage(missing=['TK-selected'])):
            engine._apply_model_metadata(PLAN, output, 'EX-plan')
        engine.runtime['executions']['EX-plan']['extensions']['model_assessments'] = [
            {'task_id': 'TK-selected', **rating}, {'task_id': 'TK-waiting', **rating}]
        with self.assertRaisesRegex(ValueError, coverage(unexpected=['TK-waiting'])):
            engine._apply_model_metadata(PLAN, output, 'EX-plan')

    def test_plan_rates_a_selected_task_only_to_change_or_supply_its_stored_assessment(self):
        engine = self.engine()
        stored = {'difficulty': 'low', 'importance': 'medium', 'reason': 'Reviewed with the contract'}
        changed = {'difficulty': 'high', 'importance': 'high', 'reason': 'A failed attempt showed the gap is central'}
        engine.runtime['tasks'] = {'TK-kept': {'id': 'TK-kept', 'model_assessment': stored},
                                   'TK-unrated': {'id': 'TK-unrated'}}
        output = {'dispositions': [disposition('TK-kept'), disposition('TK-unrated'),
                                   disposition('TK-waiting', kind='not_selected')]}

        def apply(rows):
            engine.runtime['executions']['EX-plan'] = {'extensions': {'model_assessments': rows}}
            engine._apply_model_metadata(PLAN, output, 'EX-plan')
            return engine.runtime['executions']['EX-plan']['model_decisions']
        self.assertEqual(apply([{'task_id': 'TK-unrated', **stored}]), {'TK-unrated': stored})
        self.assertEqual(apply([{'task_id': 'TK-kept', **changed}, {'task_id': 'TK-unrated', **stored}]),
                         {'TK-kept': changed, 'TK-unrated': stored})
        with self.assertRaisesRegex(ValueError, coverage(missing=['TK-unrated'])):
            apply([{'task_id': 'TK-kept', **changed}])
        with self.assertRaisesRegex(ValueError, coverage(unexpected=['TK-waiting'])):
            apply([{'task_id': 'TK-unrated', **stored}, {'task_id': 'TK-waiting', **stored}])
        with self.assertRaisesRegex(ValueError, '^duplicate model assessment: TK-unrated$'):
            apply([{'task_id': 'TK-unrated', **stored}, {'task_id': 'TK-unrated', **changed}])

    def test_formal_contract_binds_the_supplied_environment_without_changing_wire(self):
        item = candidate('formal work', formal=True)
        original = deepcopy(item)
        contract = task_candidate_record(item, task_id='TK-one', trust_environment_id='TE-author')
        self.assertEqual(contract['trust_environment_id'], 'TE-author')
        self.assertEqual(item, original)
        item['work_class'] = 'nonformal'
        self.assertNotIn('trust_environment_id', task_candidate_record(item,
            task_id='TK-other', trust_environment_id='TE-author'))

    def test_task_work_allowlist_does_not_block_the_independent_contract_reviewer(self):
        from support.entry import entry
        _entry = entry()
        config = deepcopy(DEFAULT_CONFIG)
        instance = build_profiles(config, host=_entry.ports.host)
        profiles = instance['execution_profiles']
        work = next(p for p in profiles.values() if p['role'] == 'research_work'
                    and p['ai']['tier'] == 'low')
        tasks = {'TK-one': {'profile_refs': [profile_ref(work)], 'model_assessment': {
            'difficulty': 'low', 'importance': 'low', 'reason': 'Bounded work'}}}
        selected = model_policy.selection(config,
            {'role': 'task_contract_review', 'target': 'TK-one'}, tasks, {}, instance=instance)
        reviewer = profiles[selected['profile_ref']['id']]
        self.assertEqual(reviewer['role'], 'task_contract_review')
        # The task's low rating is below the reviewer role's tier floor, which wins.
        self.assertEqual(reviewer['ai']['tier'], config['role_tiers']['task_contract_review'])
        selected_work = model_policy.selection(config,
            {'role': 'research_work', 'target': 'TK-one'}, tasks, {}, instance=instance)
        self.assertEqual(selected_work['profile_ref'], profile_ref(work))
        tasks['TK-one']['profile_refs'] = []
        with self.assertRaisesRegex(ValueError, 'permitted role/model edition'):
            model_policy.selection(config, {'role': 'research_work', 'target': 'TK-one'},
                tasks, {}, instance=instance)

    def test_assessment_is_preserved_without_changing_the_candidate_wire_shape(self):
        from support.entry import entry
        _entry = entry()
        engine = self.engine()
        item = candidate('bounded observation')
        profile = next(p for p in build_profiles(DEFAULT_CONFIG, host=_entry.ports.host)['execution_profiles'].values()
                       if p['role'] == 'research_work')
        item['profile_refs'] = [profile_ref(profile)]
        output = {'candidates': [item]}
        original = deepcopy(output)
        rating = {'difficulty': 'low', 'importance': 'low', 'reason': 'A bounded test task'}
        engine.runtime['executions']['EX-prepare'] = {'extensions': {
            'model_assessments': [{'task_title': item['title'], **rating}]}}
        engine._apply_model_metadata({'role': 'research_preparation'}, output, 'EX-prepare')
        contract = task_candidate_record(output['candidates'][0], task_id='TK-test')
        self.assertEqual(output, original)
        self.assertEqual(engine.runtime['executions']['EX-prepare']['model_decisions'],
                         {item['title']: rating})
        self.assertEqual(contract['title'], item['title'])


class ProcessedRejectionTests(EngineCase):
    def test_original_academic_contract_request_has_a_recipient_without_erasing_ai_preparation(self):
        from do_math import planning
        host = self.engine()
        task, _, _ = approved_task()
        task['initial_observation_rules'] = prepared_rule_conditions([task['id']])[0]['observation_rules']
        task.update(academic_requirement_id='R', model_assessment=rating(),
            revision_requested={'revision': task['revision'], 'contract_sha256': planning.contract_hash(task),
                'source_refs': ['EX-review'], 'user_decision_refs': [], 'reason': 'The review requests an original contract correction'})
        task['reviews'] = [{**assessment_basis(task), 'decision': 'revision_required', 'execution_id': 'EX-review',
            'item_reviews': [{'decision': 'revision_required', 'revision_fields': ['contract']}]}]
        host.runtime['tasks'], host.runtime['queue'] = {task['id']: task}, []
        before = deepcopy((task['model_assessment'], task['initial_observation_rules']))
        host._ensure_model_assessments()
        host._ensure_model_assessments()
        requests = [a for a in host.runtime['queue'] if a['role'] == 'research_preparation']
        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0]['revision_targets'][task['id']]['source_refs'], ['EX-review'])
        self.assertEqual((task['model_assessment'], task['initial_observation_rules']), before)
        self.assertEqual(task['waiting']['next_owner'], 'research_preparation')

    def test_processed_rejection_cannot_erase_a_fresh_equal_or_changed_assessment(self):
        host = self.engine()
        host.instance['config'] = {'session_limits': deepcopy(LIMITS)}
        runtime = host.runtime
        for unchanged in (False, True):
            with self.subTest(unchanged=unchanged):
                task, _, _ = approved_task()
                rules = prepared_rule_conditions([task['id']])[0]['observation_rules']
                task['initial_observation_rules'] = deepcopy(rules)
                task.update(academic_requirement_id='R', revision_requested={'revision': task['revision'], 'source': 'REJECT',
                    'reason': 'task contract review returned revision_required'},
                    model_assessment=rating())
                task['reviews'] = [{**assessment_basis(task), 'decision': 'revision_required', 'execution_id': 'REJECT',
                    'item_reviews': [{'decision': 'revision_required', 'revision_fields': ['model_assessment', 'initial_observation_rules']}]}]
                # Each case starts as the legacy state did: this one task and an empty queue.
                runtime['tasks'], runtime['queue'] = {task['id']: task}, []
                self.assertEqual(runtime.get('waiting_actions', {}), {})
                host._ensure_model_assessments()
                revised = rating() if unchanged else {**rating(), 'importance': 'high'}
                task['model_assessment'] = deepcopy(revised)
                task['initial_observation_rules'] = deepcopy(rules)
                runtime['queue'] = [{'id': 'NEW-REVIEW', 'role': 'task_contract_review', 'target': task['id']}]
                for _ in range(3):
                    host._ensure_model_assessments()
                self.assertEqual(task['model_assessment'], revised)
                self.assertEqual(len(task['model_assessment_history']), 1)
                self.assertEqual([a['id'] for a in runtime['queue']], ['NEW-REVIEW'])
                task['reviews'].append({**assessment_basis(task), 'decision': 'unresolved', 'execution_id': 'REJECT-NEW'})
                host._ensure_model_assessments()
                self.assertEqual(task['model_assessment'], revised)
                self.assertEqual(task['initial_observation_rules'], rules)
                self.assertEqual(len(task['model_assessment_history']), 1)
                self.assertIs(host.runtime, runtime)


if __name__ == '__main__':
    unittest.main()
