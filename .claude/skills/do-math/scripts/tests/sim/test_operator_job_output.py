"""The shared Job worker preserves the operator's cwd and strict UTF-8 contract."""
from pathlib import Path
import tempfile
import unittest

from do_math.formal import _job_run
from support.fakes.clock import FakeClock
from support.knowledge_verifier_jobs import OutputCompiler, worker_jobs


class CapturedCompiler(OutputCompiler):
    def __call__(self, command, **arguments):
        self.directory = Path(arguments['cwd'])
        return super().__call__(command, **arguments)


class BytesCompiler:
    def __call__(self, command, **arguments):
        self.out = arguments['stdout']
        return self

    def __enter__(self):
        return self

    def __exit__(self, *exception):
        return False

    def wait(self, timeout=None):
        self.out.write(b'bad: \xff\r\n')
        return 0


class OperatorJobOutputTests(unittest.TestCase):
    def test_operator_os_error_transport_preserves_fields_and_lean_failure_contract(self):
        from support.entry import entry
        _entry = entry()
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        rename = OSError(13, 'permission denied', str(root / 'source'))
        rename.filename2 = str(root / 'destination')
        for original in (OSError(13, 'permission denied', str(root / 'program')), OSError('start refused'), rename):
            for preserve in (False, True):
                with self.subTest(error=str(original), preserve=preserve):
                    def refused(command, **arguments):
                        raise original
                    jobs = worker_jobs(refused)
                    if preserve:
                        with self.assertRaises(OSError) as caught:
                            _job_run(['fixture'], root, jobs=jobs, clock=FakeClock(), preserve_os_error=True, environment=_entry.environment)
                        self.assertIs(type(caught.exception), type(original))
                        self.assertEqual(str(caught.exception), str(original))
                        self.assertEqual(caught.exception.args, original.args)
                        self.assertEqual(caught.exception.filename, original.filename)
                        self.assertEqual(getattr(caught.exception, "winerror", None), getattr(original, "winerror", None))
                        self.assertEqual(caught.exception.filename2, original.filename2)
                    else:
                        with self.assertRaisesRegex(RuntimeError, 'formal worker failed:') as caught:
                            _job_run(['fixture'], root, jobs=jobs, clock=FakeClock(), environment=_entry.environment)
                        self.assertIn(str(original), str(caught.exception))
                    self.assertTrue(jobs.launched[0].closed)

    def test_evidence_spool_does_not_change_external_command_cwd(self):
        from support.entry import entry
        _entry = entry()
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        cwd, spool = root / 'command', root / 'spool'
        cwd.mkdir()
        spool.mkdir()
        compiler = CapturedCompiler('normal\r\noutput')
        jobs = worker_jobs(compiler)
        result = _job_run(['fixture'], cwd, jobs=jobs, clock=FakeClock(),
                          evidence_dir=spool, decode_errors='strict', environment=_entry.environment)
        self.assertEqual(result, (0, 'normal\noutput', '', False))
        self.assertEqual(compiler.directory, cwd)
        self.assertEqual(list(cwd.iterdir()), [])
        self.assertEqual(jobs.launched[0].cwd.parent, spool)
        self.assertEqual(compiler.commands, [['fixture']])

    def test_operator_strict_decoding_refuses_bytes_the_lean_default_replaces(self):
        from support.entry import entry
        _entry = entry()
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        for strict in (False, True):
            with self.subTest(strict=strict):
                jobs = worker_jobs(BytesCompiler())
                options = {'decode_errors': 'strict'} if strict else {}
                if strict:
                    with self.assertRaisesRegex(UnicodeDecodeError, 'invalid start byte'):
                        _job_run(['fixture'], root, jobs=jobs, clock=FakeClock(), **options, environment=_entry.environment)
                else:
                    self.assertEqual(_job_run(['fixture'], root, jobs=jobs, clock=FakeClock(), **options, environment=_entry.environment),
                                     (0, 'bad: \ufffd\n', '', False))
                self.assertTrue(jobs.launched[0].closed)
