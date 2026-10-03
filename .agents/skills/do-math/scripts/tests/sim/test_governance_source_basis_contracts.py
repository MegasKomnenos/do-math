"""공개 원자료 생산자의 추가·교체·삭제가 봉인한 판정 근거에 미치는 영향."""
from copy import deepcopy
import unittest

from do_math import input_basis
from do_math.control_contracts import normalized_source
from support.engine_lifecycle import applied
from support.sim import Sim, warm_template

setUpModule = warm_template


class GovernanceSourceBasisTests(unittest.TestCase):
    def source(self, sim, name, raw):
        applied(sim, 'source', config=normalized_source(name, raw))
        row = next(row for row in sim.instance['sources'] if row['name'] == name)
        self.assertEqual(sim.engine.store.read(row['path'], sim.engine.head), raw)
        return row

    def test_unreferenced_public_source_addition_preserves_captured_basis(self):
        sim = Sim.activated()
        source = self.source(sim, '원문.txt', '정확한 원문'.encode())
        expected = [{'name': source['name'], 'path': source['path'], 'sha256': source['sha256']}]
        for ref in sorted(input_basis.aliases(source)):
            with self.subTest(ref=ref):
                self.assertEqual(input_basis.capture_sources(sim.instance, [ref]), expected)
        basis = input_basis.capture_decision_basis(sim.instance, sim.runtime, [source['id']])
        self.source(sim, '무관.txt', b'')
        before = deepcopy((sim.instance, sim.runtime, basis))
        self.assertEqual(input_basis.decision_basis_changes(basis, sim.instance, sim.runtime), [])
        self.assertTrue(input_basis.sources_current(expected, sim.instance))
        self.assertEqual((sim.instance, sim.runtime, basis), before)

    def test_public_source_replacement_invalidates_only_the_original_source_basis(self):
        sim = Sim.activated()
        original = deepcopy(self.source(sim, '원문.txt', b'first'))
        basis = input_basis.capture_decision_basis(sim.instance, sim.runtime, [original['id']])
        other = self.source(sim, '별도.txt', b'other')
        unrelated = input_basis.capture_decision_basis(sim.instance, sim.runtime, [other['id']])
        replacement = self.source(sim, '원문.txt', b'second')
        self.assertEqual(replacement['id'], original['id'])
        self.assertEqual(replacement['revision'], original['revision'] + 1)
        self.assertEqual(replacement['history'], [original])
        before = deepcopy((sim.instance, sim.runtime))
        self.assertEqual(input_basis.decision_basis_changes(basis, sim.instance, sim.runtime), [
            {'id': None, 'field': 'sources', 'before': basis['sources'], 'after': 'changed',
             'next': 'refresh_decision'}])
        self.assertEqual(input_basis.decision_basis_changes(unrelated, sim.instance, sim.runtime), [])
        self.assertEqual((sim.instance, sim.runtime), before)

    def test_missing_captured_source_is_reported_without_changing_the_snapshot(self):
        sim = Sim.activated()
        source = self.source(sim, '원문.txt', b'exact')
        basis = input_basis.capture_decision_basis(sim.instance, sim.runtime, [source['id']])
        instance = deepcopy(sim.instance)
        instance['sources'].remove(source)
        before = deepcopy((instance, sim.runtime, basis))
        self.assertFalse(input_basis.sources_current(basis['sources'], instance))
        self.assertEqual(input_basis.decision_basis_changes(basis, instance, sim.runtime), [
            {'id': None, 'field': 'sources', 'before': basis['sources'], 'after': 'changed',
             'next': 'refresh_decision'}])
        self.assertEqual((instance, sim.runtime, basis), before)
