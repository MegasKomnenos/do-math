"""The native final's revalidation against its published start and input (``native_final.verified_native_final``, layer 2).

Native bytes reach central capture only through this check; the provider
evidence is an explicit fixture (``support.submission_receiver.native_result``:
a finished Codex call's collection record whose launch ticket comes from the
Jobs and clock port fakes). Each rejection is pinned by the product's message,
so a mutation fails for the evidence it breaks and not for an earlier one.
"""
from copy import deepcopy
import hashlib
from pathlib import Path
from types import SimpleNamespace
import unittest

from do_math.codex_adapter import _artifact
from do_math.native_final import verified_native_final
from do_math.payloads import json_safe
from support.fakes.clock import FakeClock
from support.fakes.jobs import FakeJobs
from support.submission_probes import CallSites
from support.submission_receiver import native_result

IDENTITY_DIFFERS = 'native collected/start identity differs from its published process'


class NativeFinalProtocolTests(unittest.TestCase):
    def setUp(self):
        self.execution = {'id': 'EX-native', 'grant_id': 'GR-native',
                          'execution_profile_ref': {'id': 'EP-native', 'sha256': 'a' * 64}}
        self.context = {'execution_id': 'EX-native', 'action': {'grant_id': 'GR-native'}}
        # A combining accent, a precomposed letter, Hangul and an emoji, written as escapes.
        self.raw = '{"text":"e\u0301 \u00b7 \u00e9 \u00b7 \ud55c\uae00 \u00b7 \U0001f600"}'.encode()
        ports = SimpleNamespace(ports=SimpleNamespace(jobs=FakeJobs([])), clock=FakeClock())
        self.result = native_result(ports, self.execution, self.context, self.raw, Path('C:/workspace'))

    def test_verified_native_stream_retains_exact_bytes_and_serialized_evidence(self):
        for value in [self.result, json_safe(self.result)]:
            self.assertEqual(verified_native_final(value, self.execution, self.context), self.raw)

    def test_collected_digests_are_compared_as_records_without_rehashing(self):
        serialized = json_safe(self.result)
        # The legacy test made hashlib.sha256 raise; this records every call of it from any code instead.
        with CallSites(hashlib.sha256) as calls:
            for value in [self.result, serialized]:
                self.assertEqual(verified_native_final(value, self.execution, self.context), self.raw)
        self.assertEqual(calls.files(), [], 'collection already hashed these bytes')
        # The serialized copy and the collected record must still name the same digest.
        serialized['execution']['collect']['stdout']['raw']['sha256'] = 'c' * 64
        with self.assertRaisesRegex(ValueError, 'serialized native artifact differs'):
            verified_native_final(serialized, self.execution, self.context)

    def test_changed_creation_identity_or_pid_and_float_identity_are_rejected(self):
        mutations = [
            (lambda r: r['execution']['started'].update(creation_filetime=134345064658094592), IDENTITY_DIFFERS),
            (lambda r: r['execution']['collect']['process_identity'].update(creation_filetime=134345064658094592),
             IDENTITY_DIFFERS),
            (lambda r: r['execution']['collect']['process_identity'].update(pid=124), IDENTITY_DIFFERS),
            # The same value as a float is not an exact integer.
            (lambda r: r['execution']['started'].update(creation_filetime=float(134345064658094591)),
             'native process identity requires an exact positive integer')]
        for index, (mutate, message) in enumerate(mutations):
            with self.subTest(mutation=index):
                result = deepcopy(self.result)
                mutate(result)
                with self.assertRaisesRegex(ValueError, '^' + message + '$'):
                    verified_native_final(result, self.execution, self.context)

    def test_status_alone_bad_stream_changed_request_and_unconfirmed_barrier_rejected(self):
        stream_mismatch = 'native stream does not establish this exact completed final'
        variants = [
            (lambda r: r.pop('execution'), 'native completion evidence is missing or malformed'),
            (lambda r: r.update(status='stopped'), 'native execution did not complete normally'),
            (lambda r: r['execution']['collect']['termination_barrier'].update(active_processes=1),
             'native collection or local termination is incomplete'),
            (lambda r: r['execution']['collect'].update(stdout=_artifact(r['execution']['collect']['stdout']['raw'] + b'{')),
             stream_mismatch),
            (lambda r: r['execution']['collect'].update(final=_artifact(b'{"text":"different"}')), stream_mismatch),
            (lambda r: r['execution']['collect']['worker_status'].update(request_sha256='b' * 64),
             'native request, input, or worker completion differs from the published execution')]
        for index, (mutate, message) in enumerate(variants):
            with self.subTest(mutation=index):
                result = deepcopy(self.result)
                mutate(result)
                with self.assertRaisesRegex(ValueError, '^' + message + '$'):
                    verified_native_final(result, self.execution, self.context)


if __name__ == '__main__':
    unittest.main()
