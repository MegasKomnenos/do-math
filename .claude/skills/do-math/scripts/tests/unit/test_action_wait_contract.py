"""Registered wait construction: evidence isolation and atomic kind changes."""
from copy import deepcopy
import unittest

from do_math import governance
from do_math.wait_rules import WAITING_ACTION_RULES, waiting_action, update_waiting_action
from support.sim import Sim, warm_template

setUpModule = warm_template


class ActionWaitRecordTests(unittest.TestCase):
    def record(self):
        sim = Sim.activated()
        sim.engine._enqueue('maintenance', reason='Normal producer action for the wait record contract')
        action = deepcopy(next(row for row in sim.runtime['queue'] if row['role'] == 'maintenance'))
        authority = governance.authorize(sim.instance, action, runtime=sim.runtime, at=sim.ports.clock.now())
        return {'action': action, 'kind': 'action_authority', 'reason': 'Preserve the actual authority evidence',
                'detail': {'authority': authority, 'profile_refs': deepcopy(sim.instance['role_profile_refs']['maintenance'])}}

    def test_every_registered_kind_constructs_isolated_whole_evidence(self):
        source = self.record()
        for kind, rule in WAITING_ACTION_RULES.items():
            with self.subTest(kind=kind):
                producer = {**source, 'kind': kind}
                before = deepcopy(producer)
                record = waiting_action(producer)
                self.assertEqual(record, {**before, 'next_owner': rule['next_owner']})
                record['action']['reason'] = 'changed consumer action'
                record['detail']['profile_refs'].clear()
                self.assertEqual(producer, before)

    def test_kind_updates_preserve_evidence_and_invalid_updates_change_nothing(self):
        source = self.record()
        record = waiting_action(source)
        for kind, rule in WAITING_ACTION_RULES.items():
            with self.subTest(kind=kind):
                update_waiting_action(record, kind=kind)
                self.assertEqual(record, {**source, 'kind': kind, 'next_owner': rule['next_owner']})
        for kind in ('unknown_wait', [], None, True):
            with self.subTest(rejected=kind):
                before = deepcopy(record)
                with self.assertRaisesRegex(ValueError, '^unregistered action wait:'):
                    update_waiting_action(record, kind=kind)
                self.assertEqual(record, before)
        for changes, reason in (
                ({'action': None}, '^action wait requires its actual action and reason$'),
                ({'next_owner': None}, '^action wait requires its actual next owner$')):
            before = deepcopy(record)
            with self.assertRaisesRegex(ValueError, reason):
                update_waiting_action(record, **changes)
            self.assertEqual(record, before)
