"""Six academic storage families: real publication, content and full reverse fields."""
from copy import deepcopy
from functools import cache
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from contracts.pairs import assert_pair
from do_math.state_contract import StateContract, default_state_contract
from support.storage_academic_pairs import (ACTOR, REJECTION, RESPONSE, EVIDENCE_REF, FAMILIES,
    family_pair, goal_samples, assessment_samples, resolution_samples)


def digest(value):
    return hashlib.sha256((json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2,
                                      allow_nan=False) + '\n').encode()).hexdigest()


class AcademicStoragePairs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.directory.cleanup)
        cls.root = Path(cls.directory.name)
        cls.addClassCleanup(cls._prepared.cache_clear)

    @classmethod
    @cache
    def _prepared(cls):
        # These producers exercise the product: run them from the test body,
        # so their failures are test results, rather than broken class fixtures.
        return (goal_samples(cls.root / 'goal'),
                assessment_samples(cls.root / 'assessment'),
                resolution_samples(cls.root / 'resolution'))

    @property
    def goals(self):
        return self._prepared()[0]

    @property
    def assessments(self):
        return self._prepared()[1]

    @property
    def resolutions(self):
        return self._prepared()[2]

    @property
    def samples(self):
        return self.goals + self.assessments + self.resolutions

    def test_all_six_families_receive_real_stored_values_and_produce_every_field(self):
        for root, family in FAMILIES:
            with self.subTest(family=root + '.' + family):
                assert_pair(self, family_pair(default_state_contract(), root, family, self.samples), self.samples)

    def test_goal_slots_basis_and_invalidation_preserve_exact_semantics(self):
        initial = self.goals[0][1][0]
        self.assertEqual((initial['goal_status'], initial['goal_judgments']), ('unsolved', []))
        solved, runtime = self.goals[-2][1]
        group = solved['goal_judgments']
        self.assertEqual(solved['goal_status'], 'mathematically_solved')
        self.assertEqual({j['basis'] for j in group}, {solved['goal_assessment_basis']})
        self.assertEqual({j['slot'] for j in group}, set(range(len(group))))
        self.assertEqual({j['required'] for j in group}, {len(group)})
        self.assertEqual(len({j['execution_id'] for j in group}), len(group))
        for row in group:
            self.assertTrue(row['current'])
            self.assertTrue(row['scope_complete'])
            self.assertTrue(row['formal_result_refs'])
            self.assertTrue(row['assessment_refs'])
            self.assertTrue(row['dependencies'])
            for ref in row['record_basis']:
                self.assertEqual(ref['status'], 'active')
            audit, = row['additional_audits']
            self.assertEqual((audit['audit_ref'], audit['verdict'], audit['decision']), ('AU', 'pass', 'satisfied'))
            self.assertEqual(audit['audit_sha256'], digest(solved['governance']['AU']))
            execution = runtime['executions'][row['execution_id']]
            self.assertEqual(audit['input_hashes'], execution['additional_audit_input'][0]['input_hashes'])
        invalid, _ = self.goals[-1][1]
        self.assertEqual(invalid['goal_status'], 'unsolved')
        self.assertEqual(invalid['goal_assessment_basis'], solved['goal_assessment_basis'])
        self.assertTrue(all(j['current'] is False for j in invalid['goal_judgments']))
        for row in invalid['goal_judgments']:
            self.assertIn('no longer usable', row['invalidated_reason'])
            self.assertEqual(row['use_history'][-1]['reason'], 'Withdraw the exact mathematical premise')

    def test_task_assessments_preserve_all_three_decisions_and_exact_criteria(self):
        for decision, (instance, runtime) in self.assessments:
            with self.subTest(decision=decision):
                row, = runtime['academic_assessments']
                task = runtime['tasks'][row['task_id']]
                self.assertEqual(row['decision'], decision)
                self.assertEqual(row['solution_basis'], task['solution_basis'])
                self.assertEqual(row['requirements_sha256'], task['requirements_sha256'])
                self.assertEqual(row['task_assessment_sha256'], digest(task['assessment']))
                self.assertEqual(row['execution_id'], task['assessment']['execution_id'])
                self.assertEqual(runtime['executions'][row['execution_id']]['input_solution_basis'], task['solution_basis'])
                self.assertEqual(row['assessor'], 'research_plan')
                self.assertEqual(row['external_effect_receipts'], [])
                self.assertEqual([e['criterion'] for e in row['evidence']],
                                 ['Explain the proof', 'Discuss the limitations'])
                self.assertEqual([e['satisfied'] for e in row['evidence']],
                                 [False, True] if decision == 'unresolved' else [True, True])
                work = next(r['execution_id'] for r in task['results'])
                self.assertEqual([e['evidence'] for e in row['evidence']],
                                 ['', work] if decision == 'unresolved' else [work, work])

    def test_resolution_seals_exact_rejection_bytes_and_planner_input(self):
        initial = self.resolutions[0][1][1]
        original, = initial['external_rejections']
        self.assertEqual((original['actor'].encode(), original['text'].encode()), (ACTOR.encode(), REJECTION.encode()))
        self.assertTrue(original['created_at'])
        self.assertTrue(original['source_ref'])
        for decision, (instance, runtime) in self.resolutions[1:]:
            with self.subTest(decision=decision):
                self.assertEqual(runtime['external_rejections'], [original])
                row = runtime['academic_resolution_records'][-1]
                self.assertEqual(row['rejection_id'], original['id'])
                self.assertEqual(row['rejection_sha256'], digest(original))
                self.assertEqual(row['solution_basis'], original['solution_basis'])
                self.assertEqual(row['decision'], decision)
                self.assertEqual(row['evidence_refs'], [EVIDENCE_REF])
                self.assertEqual(row['evidence_hashes'], {EVIDENCE_REF: hashlib.sha256(RESPONSE).hexdigest()})
                actor = runtime['executions'][row['execution_id']]
                self.assertEqual((actor['role'], actor['input_solution_basis']), ('research_plan', row['solution_basis']))
                payload = {k: v for k, v in row.items() if k not in {'id', 'sha256'}}
                self.assertEqual(row['id'], 'AR-' + digest(payload)[:24])
                self.assertEqual(row['sha256'], digest({k: v for k, v in row.items() if k != 'sha256'}))

    def test_unproduced_optional_is_detected_for_records_and_nested_singleton(self):
        for root, family in FAMILIES:
            if family in {'goal_status', 'goal_assessment_basis'}:
                self.assertEqual(family_pair(default_state_contract(), root, family, self.samples).fields,
                                 frozenset({'/value'}))
                continue
            original = default_state_contract().family(root, family)
            schema = deepcopy(original.schema)
            target = schema['items']['properties']['evidence']['items'] if family == 'academic_assessments' else schema
            target['properties']['unproduced_optional'] = {'type': 'string'}
            contract = StateContract()
            contract.register_family(root, family, schema=schema, shape=original.shape, identity=original.identity)
            with self.subTest(family=family), self.assertRaisesRegex(AssertionError, 'unproduced_optional'):
                assert_pair(self, family_pair(contract, root, family, self.samples), self.samples)

    def test_removed_goal_fields_and_unknown_nested_assessment_content_cannot_publish(self):
        from support.academic_assessment_cases import assessed_case
        sim, tid, assessment, eid = assessed_case()
        engine = sim.engine
        engine._record_academic_assessment(engine.runtime['tasks'][tid], assessment, eid)
        engine._save()
        published = deepcopy(engine.store.load())
        head, instance, runtime = published
        for field in ('created_at', 'findings', 'input_basis'):
            broken = deepcopy(instance)
            broken['goal_judgments'][0][field] = []
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "Additional properties are not allowed.*" + field):
                engine.store.save_with_state(head, broken, runtime)
            self.assertEqual(engine.store.load(), published)
        for field in ('solution_basis', 'evidence'):
            broken = deepcopy(runtime)
            row = broken['academic_assessments'][0][field]
            (row[0] if isinstance(row, list) else row)['unexpected'] = 'not produced'
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'Additional properties are not allowed.*unexpected'):
                engine.store.save_with_state(head, instance, broken)
            self.assertEqual(engine.store.load(), published)
