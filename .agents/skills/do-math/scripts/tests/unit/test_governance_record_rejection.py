"""정상 생산 상태의 한 필드 변조와 거부의 원자성. 실행 결과는 별도 측정한다."""
from copy import deepcopy
import re
import unittest

from do_math import governance as gov
from support.governance_cases import records_sim, proposed_record

class GovernanceRecordRejectionTests(unittest.TestCase):
    def test_record_kind(self):
        sim = records_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        record = proposed_record(i, 'PO-close')
        record['kind'] = 'other'
        before = deepcopy((i, r, record))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('unsupported governance record kind') + "$"):
            gov.validate_governance_record(record)
        self.assertEqual((i, r, record), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_record_revision(self):
        sim = records_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        record = proposed_record(i, 'PO-close')
        record['revision'] = 0
        before = deepcopy((i, r, record))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('governance revision must be positive') + "$"):
            gov.validate_governance_record(record)
        self.assertEqual((i, r, record), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_self_supersession(self):
        sim = records_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        record = proposed_record(i, 'PO-close')
        record['supersedes'] = [record['id']]
        before = deepcopy((i, r, record))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('self supersession') + "$"):
            gov.validate_governance_record(record)
        self.assertEqual((i, r, record), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_content_object(self):
        sim = records_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        record = proposed_record(i, 'PO-close')
        record['content'] = []
        before = deepcopy((i, r, record))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('governance content required') + "$"):
            gov.validate_governance_record(record)
        self.assertEqual((i, r, record), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_context_empty(self):
        sim = records_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        record = proposed_record(i, 'CX-close')
        record['content']['terms'] = []
        before = deepcopy((i, r, record))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('context terms required') + "$"):
            gov.validate_governance_record(record)
        self.assertEqual((i, r, record), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_context_term_object(self):
        sim = records_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        record = proposed_record(i, 'CX-close')
        record['content']['terms'][0] = 'P'
        before = deepcopy((i, r, record))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('context term must be an object') + "$"):
            gov.validate_governance_record(record)
        self.assertEqual((i, r, record), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_context_duplicate(self):
        sim = records_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        record = proposed_record(i, 'CX-close')
        record['content']['terms'].append(deepcopy(record['content']['terms'][0]))
        before = deepcopy((i, r, record))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('duplicate context term') + "$"):
            gov.validate_governance_record(record)
        self.assertEqual((i, r, record), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_audit_mapping_empty(self):
        sim = records_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        record = proposed_record(i, 'AU-close')
        record['content']['verdict_mapping'] = {}
        before = deepcopy((i, r, record))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('audit needs explicit universal verdict mapping') + "$"):
            gov.validate_governance_record(record)
        self.assertEqual((i, r, record), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_audit_mapping_verdict(self):
        sim = records_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        record = proposed_record(i, 'AU-close')
        record['content']['verdict_mapping']['pass'] = 'solved'
        before = deepcopy((i, r, record))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('audit needs explicit universal verdict mapping') + "$"):
            gov.validate_governance_record(record)
        self.assertEqual((i, r, record), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_document_object(self):
        sim = records_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        record = proposed_record(i, 'PO-close')
        record['document'] = []
        before = deepcopy((i, r, record))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('document reference required') + "$"):
            gov.validate_governance_record(record)
        self.assertEqual((i, r, record), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_document_hash(self):
        sim = records_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        record = proposed_record(i, 'PO-close')
        record['document'] = {'ref': 'documents/policy.md', 'sha256': 'broken'}
        before = deepcopy((i, r, record))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('document bytes hash required') + "$"):
            gov.validate_governance_record(record)
        self.assertEqual((i, r, record), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_goal_assurance(self):
        sim = records_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        i['goal_status'] = 'done'
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('unsupported final goal assurance') + "$"):
            gov.validate_governance_state(i)
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_approval_missing(self):
        sim = records_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        i['governance']['PO-close']['approval_ref'] = 'missing'
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('governance approval missing') + "$"):
            gov.validate_governance_state(i)
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_approval_actor(self):
        sim = records_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        i['decisions'][i['governance']['PO-close']['approval_ref']]['actor'] = 'ai'
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('record lacks actual source-bound user approval') + "$"):
            gov.validate_governance_state(i)
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_approval_source_hash(self):
        sim = records_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        i['decisions'][i['governance']['PO-close']['approval_ref']]['source_sha256'] = '0' * 64
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('record lacks actual source-bound user approval') + "$"):
            gov.validate_governance_state(i)
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_content_hash(self):
        sim = records_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        i['governance']['PO-close']['content_sha256'] = '0' * 64
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('governance content differs from approved proposal') + "$"):
            gov.validate_governance_state(i)
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_lifecycle(self):
        sim = records_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        i['governance']['PO-close']['status'] = 'unknown'
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('invalid governance lifecycle') + "$"):
            gov.validate_governance_state(i)
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_supersession_link(self):
        sim = records_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        i['governance']['PO-close']['status'] = 'superseded'
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('broken governance supersession') + "$"):
            gov.validate_governance_state(i)
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_duplicate_record(self):
        sim = records_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        record = proposed_record(i, 'PO-close')
        before = deepcopy((i, r, record))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('governance ID is immutable') + "$"):
            gov._install_record(i, record, 'unused', 'GS-close')
        self.assertEqual((i, r, record), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_absent_superseded(self):
        sim = records_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        record = proposed_record(i, 'PO-close')
        record['id'] = 'PO-next'
        record['supersedes'] = ['missing']
        before = deepcopy((i, r, record))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('supersession must name an active same-kind record') + "$"):
            gov._install_record(i, record, 'unused', 'GS-close')
        self.assertEqual((i, r, record), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_same_rule(self):
        sim = records_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        record = proposed_record(i, 'PO-close')
        record['id'] = 'PO-next'
        before = deepcopy((i, r, record))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('same rule requires explicit supersession') + "$"):
            gov._install_record(i, record, 'unused', 'GS-close')
        self.assertEqual((i, r, record), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_audit_absent(self):
        sim = records_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        hashes = gov.additional_audit_input(i, r)[0]['input_hashes']
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('audit is not current') + "$"):
            gov.evaluate_additional_audit(i, 'missing', 'pass', assessor='goal_audit', input_hashes=hashes, runtime=r)
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_audit_assessor(self):
        sim = records_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        hashes = gov.additional_audit_input(i, r)[0]['input_hashes']
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('audit assessor or verdict differs from approval') + "$"):
            gov.evaluate_additional_audit(i, 'AU-close', 'pass', assessor='maintenance', input_hashes=hashes, runtime=r)
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_audit_stale_input(self):
        sim = records_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        hashes = gov.additional_audit_input(i, r)[0]['input_hashes']
        hashes[next(iter(hashes))] = '0' * 64
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('audit required input is absent or stale') + "$"):
            gov.evaluate_additional_audit(i, 'AU-close', 'pass', assessor='goal_audit', input_hashes=hashes, runtime=r)
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)
