"""실제 해석 생산자의 원문·질문·봉인 계약을 한 필드씩 검증한다."""
from copy import deepcopy
import re
import unittest

from do_math import governance as gov
from support.governance_cases import question_sim, question_bundle

class GovernanceImportCoordinateTests(unittest.TestCase):
    def test_units_empty(self):
        sim = question_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = deepcopy(question_bundle(sim))
        source = bundle['source']
        output = bundle['output']
        output['import_units'] = []
        before = deepcopy((i, r, output, source))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('import units required') + "$"):
            gov.validate_import_units(i, r, source, output, clock=sim.clock)
        self.assertEqual((i, r, output, source), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_details_object(self):
        sim = question_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = deepcopy(question_bundle(sim))
        source = bundle['source']
        output = bundle['output']
        output['question_details'] = {}
        before = deepcopy((i, r, output, source))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('question details required') + "$"):
            gov.validate_import_units(i, r, source, output, clock=sim.clock)
        self.assertEqual((i, r, output, source), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_question_identity(self):
        sim = question_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = deepcopy(question_bundle(sim))
        source = bundle['source']
        output = bundle['output']
        output['question_details'][0]['id'] = ''
        before = deepcopy((i, r, output, source))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('duplicate question identity') + "$"):
            gov.validate_import_units(i, r, source, output, clock=sim.clock)
        self.assertEqual((i, r, output, source), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_unit_object(self):
        sim = question_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = deepcopy(question_bundle(sim))
        source = bundle['source']
        output = bundle['output']
        output['import_units'][0] = 'bad'
        before = deepcopy((i, r, output, source))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('import unit must be an object') + "$"):
            gov.validate_import_units(i, r, source, output, clock=sim.clock)
        self.assertEqual((i, r, output, source), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_unit_duplicate(self):
        sim = question_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = deepcopy(question_bundle(sim))
        source = bundle['source']
        output = bundle['output']
        output['import_units'].append(deepcopy(output['import_units'][0]))
        before = deepcopy((i, r, output, source))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('duplicate meaning unit') + "$"):
            gov.validate_import_units(i, r, source, output, clock=sim.clock)
        self.assertEqual((i, r, output, source), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_range_start(self):
        sim = question_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = deepcopy(question_bundle(sim))
        source = bundle['source']
        output = bundle['output']
        output['import_units'][0]['source_range']['start'] = 1
        before = deepcopy((i, r, output, source))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('source coverage gap, overlap, or invalid coordinate') + "$"):
            gov.validate_import_units(i, r, source, output, clock=sim.clock)
        self.assertEqual((i, r, output, source), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_range_bool(self):
        sim = question_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = deepcopy(question_bundle(sim))
        source = bundle['source']
        output = bundle['output']
        output['import_units'][0]['source_range']['start'] = False
        before = deepcopy((i, r, output, source))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('source coverage gap, overlap, or invalid coordinate') + "$"):
            gov.validate_import_units(i, r, source, output, clock=sim.clock)
        self.assertEqual((i, r, output, source), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_range_end(self):
        sim = question_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = deepcopy(question_bundle(sim))
        source = bundle['source']
        output = bundle['output']
        output['import_units'][0]['source_range']['end'] = len(source['text']) + 1
        before = deepcopy((i, r, output, source))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('source coverage gap, overlap, or invalid coordinate') + "$"):
            gov.validate_import_units(i, r, source, output, clock=sim.clock)
        self.assertEqual((i, r, output, source), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_unknown_owner(self):
        sim = question_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = deepcopy(question_bundle(sim))
        source = bundle['source']
        output = bundle['output']
        output['import_units'][0]['owner_kind'] = 'missing'
        before = deepcopy((i, r, output, source))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('owner has no registered domain handler') + "$"):
            gov.validate_import_units(i, r, source, output, clock=sim.clock)
        self.assertEqual((i, r, output, source), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_payload_object(self):
        sim = question_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = deepcopy(question_bundle(sim))
        source = bundle['source']
        output = bundle['output']
        output['import_units'][0]['payload'] = []
        before = deepcopy((i, r, output, source))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('unit payload must be an object') + "$"):
            gov.validate_import_units(i, r, source, output, clock=sim.clock)
        self.assertEqual((i, r, output, source), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_decision_reference(self):
        sim = question_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = deepcopy(question_bundle(sim))
        source = bundle['source']
        output = bundle['output']
        output['import_units'][0]['decision_refs'] = ['missing']
        before = deepcopy((i, r, output, source))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('existing decision does not resolve') + "$"):
            gov.validate_import_units(i, r, source, output, clock=sim.clock)
        self.assertEqual((i, r, output, source), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_question_reference(self):
        sim = question_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = deepcopy(question_bundle(sim))
        source = bundle['source']
        output = bundle['output']
        output['import_units'][0]['question_refs'] = ['missing']
        before = deepcopy((i, r, output, source))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('unit question does not resolve') + "$"):
            gov.validate_import_units(i, r, source, output, clock=sim.clock)
        self.assertEqual((i, r, output, source), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_incomplete_coverage(self):
        sim = question_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = deepcopy(question_bundle(sim))
        source = bundle['source']
        output = bundle['output']
        output['import_units'][0]['source_range']['end'] -= 1
        before = deepcopy((i, r, output, source))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('incomplete source coverage') + "$"):
            gov.validate_import_units(i, r, source, output, clock=sim.clock)
        self.assertEqual((i, r, output, source), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_unowned_question(self):
        sim = question_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = deepcopy(question_bundle(sim))
        source = bundle['source']
        output = bundle['output']
        output['import_units'][0]['question_refs'] = []
        before = deepcopy((i, r, output, source))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('question lacks a source meaning unit') + "$"):
            gov.validate_import_units(i, r, source, output, clock=sim.clock)
        self.assertEqual((i, r, output, source), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_question_index(self):
        sim = question_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = deepcopy(question_bundle(sim))
        source = bundle['source']
        output = bundle['output']
        output['question_details'][0]['question_index'] = 1
        before = deepcopy((i, r, output, source))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('invalid question coordinate') + "$"):
            gov.validate_import_units(i, r, source, output, clock=sim.clock)
        self.assertEqual((i, r, output, source), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_question_index_bool(self):
        sim = question_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = deepcopy(question_bundle(sim))
        source = bundle['source']
        output = bundle['output']
        output['question_details'][0]['question_index'] = False
        before = deepcopy((i, r, output, source))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('invalid question coordinate') + "$"):
            gov.validate_import_units(i, r, source, output, clock=sim.clock)
        self.assertEqual((i, r, output, source), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_question_blocks(self):
        sim = question_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = deepcopy(question_bundle(sim))
        source = bundle['source']
        output = bundle['output']
        output['question_details'][0]['blocks'] = 'true'
        before = deepcopy((i, r, output, source))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('question must state whether the decision blocks work') + "$"):
            gov.validate_import_units(i, r, source, output, clock=sim.clock)
        self.assertEqual((i, r, output, source), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_question_target(self):
        sim = question_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = deepcopy(question_bundle(sim))
        source = bundle['source']
        output = bundle['output']
        output['question_details'][0]['target_ids'] = ['missing']
        before = deepcopy((i, r, output, source))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('question affects an unknown target') + "$"):
            gov.validate_import_units(i, r, source, output, clock=sim.clock)
        self.assertEqual((i, r, output, source), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_question_source_unit(self):
        sim = question_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = deepcopy(question_bundle(sim))
        source = bundle['source']
        output = bundle['output']
        output['question_details'][0]['source_unit_ids'] = ['missing']
        before = deepcopy((i, r, output, source))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('question source unit missing') + "$"):
            gov.validate_import_units(i, r, source, output, clock=sim.clock)
        self.assertEqual((i, r, output, source), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_question_options(self):
        sim = question_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = deepcopy(question_bundle(sim))
        source = bundle['source']
        output = bundle['output']
        output['question_details'][0]['options'] = {}
        before = deepcopy((i, r, output, source))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('question options and effects must be explicit') + "$"):
            gov.validate_import_units(i, r, source, output, clock=sim.clock)
        self.assertEqual((i, r, output, source), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_unrouted_text(self):
        sim = question_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = deepcopy(question_bundle(sim))
        source = bundle['source']
        output = bundle['output']
        output['questions'].append('소유자가 없는 질문')
        before = deepcopy((i, r, output, source))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('all questions require source and impact details') + "$"):
            gov.validate_import_units(i, r, source, output, clock=sim.clock)
        self.assertEqual((i, r, output, source), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)
