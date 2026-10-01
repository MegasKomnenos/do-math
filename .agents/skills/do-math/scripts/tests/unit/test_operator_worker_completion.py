"""The worker transports checked OS facts without accepting arbitrary exception records."""
import unittest

from do_math.lean_evidence import check_completion_status


class CompletionTests(unittest.TestCase):
    def test_os_error_fields_and_failure_phase_are_checked(self):
        record = {'errno': 2, 'strerror': 'missing', 'filename': 'program', 'winerror': 2,
                  'filename2': None, 'message': 'missing program'}
        self.assertIsNone(check_completion_status({'state': 'worker_error', 'exit': None, 'os_error': record}))
        wrong = [{**record, 'errno': True}, {**record, 'filename': []}, {**record, 'message': None},
                 {k: v for k, v in record.items() if k != 'winerror'}, {**record, 'exception_type': 'custom'}]
        for value in wrong:
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, '^invalid completion OS error$'):
                check_completion_status({'state': 'worker_error', 'exit': None, 'os_error': value})
        with self.assertRaisesRegex(ValueError, '^invalid completion OS error$'):
            check_completion_status({'state': 'exited', 'exit': 0, 'os_error': record})
