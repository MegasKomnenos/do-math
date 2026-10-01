"""A rejected candidate is kept on a verified head without publishing it (``lifecycle_engine``, layer 2),
and the lifecycle rules refuse a malformed clock high-water mark (``record_schemas``, layer 2).

The repository is the real ``ResearchRepository`` on the in-process Git fake,
so every publication passes the storage contract.
"""
import json
from pathlib import Path
import tempfile
import unittest

from do_math.initialization import initialize_state
from do_math.lifecycle_engine import preserve_rejected_candidate
from do_math.record_schemas import validate_lifecycle
from do_math.repository import ResearchRepository
from support.fakes.clock import FakeClock
from support.fakes.git_backend import make_fake, make_repository


class PersistedCandidateTests(unittest.TestCase):
    def setUp(self):
        from support.entry import entry
        _entry = entry()
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        self.clock = FakeClock()
        identifier = self.clock.new_id('RI')
        self.store = ResearchRepository(make_repository(root / 'repository'), identifier, backend=make_fake(),
                                        clock=self.clock)
        self.instance, self.runtime = initialize_state(instance_id=identifier, goal='G', workspace=root / 'work',
                                                       config={}, source_input='Original request', clock=self.clock, host=_entry.ports.host)
        self.head = self.store.initialize(self.instance, self.runtime)

    def test_good_head_preserves_rejected_raw_not_candidate_state(self):
        """About 0.2-0.35 s, over the 0.2 s unit budget: two publications through the storage contract on the in-process Git fake."""
        _, before_i, before_r = self.store.load(self.head)
        result = preserve_rejected_candidate(self.store, self.head, raw=b'{broken candidate', reason='schema rejection',
                                             clock=self.clock)
        self.assertNotEqual(result['snapshot'], self.head)
        self.assertEqual(self.store.read(result['raw_ref'], result['snapshot']), b'{broken candidate')
        audit = json.loads(self.store.read(result['audit_ref'], result['snapshot']))
        self.assertEqual({key: audit[key] for key in ('candidate_ref', 'base_snapshot', 'reason', 'disposition')},
                         {'candidate_ref': result['raw_ref'], 'base_snapshot': self.head, 'reason': 'schema rejection',
                          'disposition': 'rejected_not_applied'})
        _, after_i, after_r = self.store.load(result['snapshot'])
        self.assertEqual((after_i, after_r), (before_i, before_r))

    def test_damaged_head_is_not_rewritten_even_to_preserve_candidate(self):
        """About 0.2-0.35 s, over the 0.2 s unit budget: two publications through the storage contract on the in-process Git fake."""
        path = next(row['path'] for row in self.store.load_records(self.head)[3] if row['family'] == 'lifecycle')
        damaged = self.store._store.publish(self.head, {path: b'{}\n'}).head
        # Loading validates a head; a head that does not load is damaged.
        with self.assertRaisesRegex(ValueError, 'invalid record envelope fields'):
            self.store.load(damaged)
        with self.assertRaisesRegex(ValueError, 'damaged current state cannot be rewritten: invalid record envelope fields'):
            preserve_rejected_candidate(self.store, damaged, raw=b'raw', reason='candidate rejected', clock=self.clock)
        self.assertEqual(self.store._store.read_snapshot().head, damaged)

    def test_candidate_bytes_are_required(self):
        with self.assertRaisesRegex(TypeError, 'candidate raw bytes required'):
            preserve_rejected_candidate(self.store, self.head, raw='text', reason='not bytes', clock=self.clock)
        self.assertEqual(self.store._store.read_snapshot().head, self.head)

    def test_malformed_or_naive_high_water_is_rejected(self):
        for value in ('not-a-time', '2026-09-20T00:00:00', '2026-09-20T09:00:00+09:00'):
            with self.subTest(value=value):
                self.runtime['last_observed_utc'] = value
                with self.assertRaisesRegex(ValueError, 'high-water'):
                    validate_lifecycle(self.instance, self.runtime)


if __name__ == '__main__':
    unittest.main()
