"""운영자 로컬 증거와 예약 인자의 계약. 제품 저장기와 예약 포트를 그대로 지난다."""
import base64
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from do_math import scheduled_operator as operator
from support.entry import entry


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.values = entry()

    def test_path_and_bytes_evidence_roundtrip_preserves_exact_bytes(self):
        raw = b'\x00\xffoperator'
        target = self.root / 'operator/result.json'
        operator._json(target, {'path': self.root, 'raw': raw, 'text': '운영자'})
        self.assertEqual(operator._load_json(target), {'path': str(self.root), 'text': '운영자',
            'raw': {'sha256': hashlib.sha256(raw).hexdigest(), 'text': raw.decode('utf-8', 'replace'),
                    'base64': base64.b64encode(raw).decode('ascii')}})
        self.assertTrue(target.read_bytes().endswith(b'\n'))
        self.assertEqual(list(target.parent.iterdir()), [target])

    def test_unsupported_evidence_keeps_previous_atomic_file(self):
        target = self.root / 'result.json'
        operator._json(target, {'value': 'previous'})
        before = target.read_bytes()
        with self.assertRaisesRegex(TypeError, '^unsupported supervisor evidence: set$'):
            operator._json(target, {'value': {'unsupported'}})
        self.assertEqual(target.read_bytes(), before)
        self.assertEqual(list(self.root.iterdir()), [target])

    def test_nonfinite_evidence_keeps_previous_atomic_file(self):
        target = self.root / 'result.json'
        operator._json(target, {'value': 1})
        before = target.read_bytes()
        with self.assertRaisesRegex(ValueError, 'Out of range float values'):
            operator._json(target, {'value': float('nan')})
        self.assertEqual(target.read_bytes(), before)

    def test_absent_and_nonobject_markers_are_not_loaded_as_hold_records(self):
        target = self.root / 'HOLD.json'
        self.assertIsNone(operator._load_json(target))
        for value in ([], 'operator', 3, None):
            with self.subTest(value=value):
                target.write_text(json.dumps(value), encoding='utf-8')
                self.assertIsNone(operator._load_json(target))
                self.assertEqual(json.loads(target.read_bytes()), value)

    def test_release_without_hold_has_no_effect_or_timestamp(self):
        self.assertEqual(operator.release(self.root, clock=self.values.ports.clock), {'released': None})
        self.assertFalse((self.root / 'operator').exists())

    def test_release_records_later_time_and_removes_only_hold(self):
        clock = self.values.ports.clock
        held = operator.hold(self.root, reason='사용자 점검', clock=clock)
        self.assertTrue(operator._held(self.root))
        self.assertEqual(operator._operator_dir(self.root), self.root / 'operator')
        clock.advance(7)
        released = operator.release(self.root, clock=clock)
        self.assertEqual(released, {'released': held, 'released_at': clock.now()})
        self.assertNotEqual(held['started_at'], released['released_at'])
        self.assertFalse(operator._held(self.root))
        self.assertEqual(operator._load_json(self.root / 'operator/release.json'), released)
        self.assertEqual(operator.release(self.root, clock=clock), {'released': None})
        self.assertEqual(operator._load_json(self.root / 'operator/release.json'), released)

    def test_install_requires_both_configuration_values_before_scheduler(self):
        for interval, timeout in ((None, 1), (1, None), (None, None)):
            with self.subTest(interval=interval, timeout=timeout):
                with self.assertRaisesRegex(ValueError, '^install requires the configured operator interval and timeout$'):
                    operator.schedule('install', repository=self.root, instance='RI-input', workspace=self.root,
                        interval_seconds=interval, operator_timeout_seconds=timeout, scheduler=self.values.ports.scheduler)
        self.assertEqual(self.values.ports.scheduler.calls, [])
        self.assertEqual(self.values.ports.scheduler.tasks, {})

    def test_wake_requires_aware_time_and_nonempty_generation_before_scheduler(self):
        for at, key in (('bad-time', 'codex:1'), ('2026-01-01T00:00:00', 'codex:1'),
                        ('2026-01-01T00:00:00+00:00', ''), (None, 'codex:1')):
            with self.subTest(at=at, key=key):
                with self.assertRaisesRegex(ValueError, '^wake requires a timezone-aware retry time and generation key$'):
                    operator.schedule('schedule-wake', repository=self.root, instance='RI-input', workspace=self.root,
                        wake_at=at, wake_key=key, scheduler=self.values.ports.scheduler)
        self.assertEqual(self.values.ports.scheduler.calls, [])
        self.assertEqual(self.values.ports.scheduler.tasks, {})

    def test_cancel_removes_registration_but_preserves_other_evidence(self):
        scheduler = self.values.ports.scheduler
        marker = self.root / 'operator/wake-registration.json'
        operator._json(marker, {'key': 'codex:1', 'retry_at': '2026-01-02T00:00:00+00:00'})
        held = operator.hold(self.root, reason='보존할 HOLD', clock=self.values.ports.clock)
        result = operator.cancel_wake(self.root, 'RI-input', self.root, scheduler=scheduler)
        self.assertEqual(result, {'operator': None, 'engine': None, 'wake': None})
        self.assertEqual([action for action, _ in scheduler.calls], ['cancel-wake'])
        self.assertFalse(marker.exists())
        self.assertEqual(operator._load_json(self.root / 'operator/HOLD.json'), held)
