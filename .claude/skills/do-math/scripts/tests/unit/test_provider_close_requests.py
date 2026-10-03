"""작업자 요청의 중앙 모집단, 반환값 및 고유 반려 사유를 확인한다."""
from copy import deepcopy
from pathlib import Path
import re
import tempfile
import unittest

from do_math import worker_request as rules
from do_math.claude_adapter import ADAPTERS, provider_adapter
from support.fakes.clock import FakeClock
from support.provider_runs import ProviderJobs
from support.provider_close_inputs import request_seed, claude_rejections


class RequestContractTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.clock, self.jobs = FakeClock(), ProviderJobs()

    def seed(self, provider):
        return request_seed(provider, self.root, jobs=self.jobs, clock=self.clock)

    def test_all_provider_efforts_return_the_exact_request(self):
        for provider in ADAPTERS:
            check = getattr(rules, 'check_' + provider + '_request')
            for effort in sorted(getattr(rules, provider.upper() + '_EFFORTS')):
                seed = {**self.seed(provider), 'effort': effort}
                with self.subTest(provider=provider, effort=effort):
                    self.assertEqual(check(deepcopy(seed)), seed)
        self.assertEqual(self.jobs.launched, [])

    def test_common_required_fields_and_unknown_fields_have_exact_reasons(self):
        for provider in ADAPTERS:
            check = getattr(rules, 'check_' + provider + '_request')
            seed = self.seed(provider)
            required = rules.COMMON_REQUIRED | getattr(rules, provider.upper() + '_REQUIRED')
            for key in sorted(required):
                bad = deepcopy(seed)
                del bad[key]
                with self.subTest(provider=provider, key=key):
                    with self.assertRaisesRegex(ValueError, '^' + re.escape('worker request misses ' + key) + '$'):
                        check(bad)
            with self.assertRaisesRegex(ValueError, '^unknown worker request fields: alien$'):
                check({**seed, 'alien': 1})

    def test_common_string_and_runtime_rejections_preserve_other_fields(self):
        for provider in ADAPTERS:
            check = getattr(rules, 'check_' + provider + '_request')
            seed = self.seed(provider)
            keys = (rules.COMMON_REQUIRED | getattr(rules, provider.upper() + '_REQUIRED') | {'output_schema_path'}) - {'max_runtime_seconds'}
            for key in sorted(keys):
                for value in ('', ' ', '\0', None, 0, [], {}):
                    with self.subTest(provider=provider, key=key, value=value):
                        with self.assertRaisesRegex(ValueError, '^' + key + ' must be a nonempty NUL-free string$'):
                            check({**seed, key: value})
            for value in (True, 0, -1, '1', float('inf'), float('nan')):
                with self.subTest(provider=provider, timeout=value):
                    with self.assertRaisesRegex(ValueError, '^max_runtime_seconds must be positive and finite or null$'):
                        check({**seed, 'max_runtime_seconds': value})

    def test_claude_specific_rejections_and_lock_positive_controls(self):
        seed = self.seed('claude')
        for label, request, reason in claude_rejections(seed):
            with self.subTest(label=label):
                with self.assertRaisesRegex(ValueError, '^' + re.escape(reason) + '$'):
                    rules.check_claude_request(request)
        for model, lock in (('haiku', False), ('claude-sonnet-5', True)):
            request = {**seed, 'model': model, 'claude_only_assigned_model': lock}
            self.assertEqual(rules.check_claude_request(deepcopy(request)), request)

    def test_codex_sandbox_population_and_negative_controls(self):
        seed = self.seed('codex')
        for sandbox in rules.CODEX_SANDBOXES:
            for windows in rules.CODEX_WINDOWS_SANDBOXES:
                request = {**seed, 'sandbox': sandbox, 'windows_sandbox': windows}
                self.assertEqual(rules.check_codex_request(deepcopy(request)), request)
        for field, value, reason in (
            ('effort', 'outside', 'unsupported effort or approval policy'),
            ('approval_policy', 'always', 'unsupported effort or approval policy'),
            ('sandbox', 'outside', 'a supported sandbox is required'),
            ('windows_sandbox', 'none', 'windows_sandbox must be elevated or unelevated when present')):
            with self.subTest(field=field):
                with self.assertRaisesRegex(ValueError, '^' + re.escape(reason) + '$'):
                    rules.check_codex_request({**seed, field: value})

    def test_nonobject_and_unknown_provider_are_rejected(self):
        for provider in ADAPTERS:
            for value in (None, 0, [], 'x', True):
                with self.subTest(provider=provider, value=value):
                    with self.assertRaisesRegex(ValueError, '^worker request must be an object$'):
                        getattr(rules, 'check_' + provider + '_request')(value)
        with self.assertRaisesRegex(ValueError, '^unsupported profile provider$'):
            provider_adapter('outside', jobs=self.jobs, clock=self.clock)
