"""Observe, compile, record and re-record on the actual setup/formal path."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import tempfile
import unittest

import setup_lean
from do_math import trust_inventory as records
from do_math.local_host import LocalHost
from do_math.trust_validation import check_environment
from support.trust_inputs import trust_environment
from support.fakes.clock import FakeClock
from support.knowledge_verifier_jobs import worker_jobs
from support.lean import LeanDouble


class EnvironmentFoundationWiringTests(unittest.TestCase):
    def test_foundation_identity_record_rerecord_and_check_use_ports_and_real_evidence(self):
        from support.entry import entry
        _entry = entry()
        clock = FakeClock(wall=datetime(2090, 1, 1, tzinfo=timezone.utc))
        lean = LeanDouble()
        # setup_lean compiles the raw representative source, without verifier framing.
        source, _ = records.validation_program({"project": None})
        lean.inputs[source.encode("utf-8")] = {}  # Explicit success for these exact bytes only.
        spawn = lean.spawn
        def elapsed(command, **options):
            process = spawn(command, **options)
            answer = process.wait
            def wait(timeout=None):
                if command[-1] != '--version':
                    clock.advance(1)
                return answer(timeout)
            process.wait = wait
            return process
        jobs = worker_jobs(elapsed)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            executable = root / 'toolchain/bin/lean.exe'
            executable.parent.mkdir(parents=True)
            executable.write_bytes(b'external Lean double')
            olean = root / 'toolchain/lib/lean/Init/Prelude.olean'
            olean.parent.mkdir(parents=True)
            olean.write_bytes(b'prelude')
            command = [str(executable)]
            options = {'jobs': jobs, 'clock': clock, 'environment': _entry.environment, 'git_backend': _entry.ports.git_backend}
            result = setup_lean.record_installation(command, root / 'records', root / 'evidence', **options)
            self.assertEqual((result['status'], result['created'], result['representative_check_seconds']),
                             ('recorded', True, 1))
            record = records.read_record(result['record_path'])
            self.assertEqual(record['identity']['version'], lean.version)
            baseline = record['baselines'][0]
            self.assertEqual(baseline['recorded_at'], clock.now())
            validation = baseline['validation']
            source = Path(validation['source'])
            self.assertEqual(source.read_bytes(), validation['source_text'].encode('utf-8'))
            self.assertEqual(json.loads((source.parent / 'validation.json').read_text(encoding='utf-8')), validation)
            self.assertEqual(lean.commands, [[*command, '--version'], [*command, str(source)]])
            again = setup_lean.record_installation(command, root / 'records', root / 'evidence', **options)
            self.assertFalse(again['created'])
            self.assertEqual(len(lean.checks), 1)
            request = records.registration_request(record, result['record_path'], result['binding'])
            environment, bound = trust_environment(request)
            host = LocalHost(**options)
            info = olean.stat()
            os.utime(olean, ns=(info.st_atime_ns, info.st_mtime_ns + 10**9))
            self.assertEqual(check_environment(environment, bound, host=host, clock=clock)['status'], 'invalid')
            rerecorded = setup_lean.rerecord(command, root / 'records', root / 'evidence', None, **options)
            checked = check_environment(environment, bound, host=host, clock=clock)
            self.assertEqual(checked['status'], 'verified')
            self.assertEqual(checked['rebind']['previous'], bound)
            self.assertEqual(checked['rebind']['current'], rerecorded['binding'])
            result = setup_lean.check_contents(root / 'records', None, command, **options)
            self.assertEqual(result['status'], 'passed')
            self.assertEqual(result['check']['checked_at'], clock.now())
            self.assertEqual(len(lean.checks), 2)
            self.assertEqual(len(jobs.launched), 6)

    def test_foundation_settling_uses_passed_window_and_clock_on_real_files(self):
        from do_math.file_io import RACY_NS
        from support.knowledge_verifier_jobs import approved_toolchain
        with tempfile.TemporaryDirectory() as directory:
            _, identity = approved_toolchain(Path(directory))
            clock = FakeClock(wall=datetime.now(timezone.utc))
            before = clock.monotonic()
            observed = setup_lean._settled_fingerprint(identity, clock=clock, racy_ns=RACY_NS)
            self.assertEqual(observed, records.observe_fingerprint(identity))
            self.assertEqual(clock.monotonic() - before, RACY_NS / 1e9)
