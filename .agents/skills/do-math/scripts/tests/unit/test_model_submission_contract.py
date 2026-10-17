"""The provider double must not silently weaken a test's submission contract."""
import io
import json
from pathlib import Path
import tempfile
import unittest

from support.fakes.clock import FakeClock
from support.model import Answer, FakeCLI, ModelDouble, default, raw


class SubmissionContractTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.model = ModelDouble(FakeClock())
        self.stream = io.BytesIO()
        self.final = self.root / 'final.txt'
        self.cli = FakeCLI(self.model, ['codex', '--output-last-message', str(self.final)],
                           self.stream, io.BytesIO(), self.root)

    def test_normal_response_requires_binding_before_writing_a_draft_or_final(self):
        with self.assertRaisesRegex(AssertionError, 'normal bound response requires control binding'):
            self.cli.communicate(input=(
                'You are the do-math role: maintenance.\n--- CANONICAL INPUT CONTEXT ---\n'
                '{"action": {"role": "maintenance"}}\n--- OUTPUT JSON SCHEMA ---\n{}').encode())
        self.assertFalse((self.root / 'output.json').exists())
        self.assertFalse(self.final.exists())
        self.assertEqual(self.stream.getvalue(), b'')

    def test_unexpected_terminal_receipt_never_satisfies_normal_acceptance(self):
        for state in ('rejected', 'closed', 'previewed', 'unknown', None):
            with self.subTest(state=state):
                receipt = {'request_id': 'RQ-contract', 'state': state}
                with self.assertRaisesRegex(AssertionError, 'expected receipt accepted'):
                    self.cli.check_receipt(receipt, 'accepted')
        self.cli.check_receipt({'state': 'accepted'}, 'accepted')

    def test_explicit_rejection_checks_the_exact_receipt(self):
        answer = raw({}, expected_receipt='rejected')
        self.cli.check_receipt({'state': 'rejected'}, answer.expected_receipt)
        with self.assertRaisesRegex(AssertionError, 'expected receipt rejected'):
            self.cli.check_receipt({'state': 'accepted'}, answer.expected_receipt)

    def test_actual_closed_transport_does_not_satisfy_normal_acceptance(self):
        from do_math.control_transport import ControlTransport
        transport = ControlTransport(self.root / 'transport', clock=self.model.clock)
        binding = transport.issue('EX-closed', 'GR-closed', workspace=self.root)
        context = self.root / 'input/submission/context.json'
        context.parent.mkdir(parents=True)
        context.write_text(json.dumps({'execution_id': 'EX-closed', 'control_binding': binding}), encoding='utf-8')
        transport.close(binding, reason='explicit owner closure')
        with self.assertRaisesRegex(AssertionError, 'expected receipt accepted'):
            self.cli.communicate(input=(
                'You are the do-math role: maintenance.\n--- CANONICAL INPUT CONTEXT ---\n'
                '{"action": {"role": "maintenance"}}\n--- OUTPUT JSON SCHEMA ---\n{}').encode())
        self.assertEqual(self.model.receipts[-1]['state'], 'closed')
        self.assertFalse(self.final.exists())
        # A declared provider failure cannot turn an unexpected receipt into a successful test.
        with self.assertRaisesRegex(AssertionError, 'expected receipt accepted'):
            self.cli.finish({'summary': 'failed provider'}, raw({}, expected_receipt='accepted', returncode=1))
        self.assertIsNone(self.cli.returncode)
        self.assertEqual(self.stream.getvalue(), b'')
        self.cli.finish({'summary': 'late output'}, default(expected_receipt='closed'))
        self.assertEqual(json.loads(self.final.read_bytes())['receipt'], 'closed')

    def test_interleaved_outputs_keep_each_calls_answer_and_exit_contract(self):
        from do_math.control_transport import ControlTransport
        standalone = raw({'summary': 'first call'}, mode='standalone', expected_receipt=None)
        closed = raw({'summary': 'second call'}, expected_receipt='closed', returncode=1)
        self.model.on('maintenance').reply(standalone).reply(closed)
        first, first_answer = self.model.output('maintenance', {'action': {'role': 'maintenance'}}, self.root)
        second, second_answer = self.model.output('maintenance', {'action': {'role': 'maintenance'}}, self.root)
        self.assertIs(first_answer, standalone)
        self.assertIs(second_answer, closed)
        transport = ControlTransport(self.root / 'transport', clock=self.model.clock)
        binding = transport.issue('EX-second', 'GR-second', workspace=self.root)
        path = self.root / 'input/submission/context.json'
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({'execution_id': 'EX-second', 'control_binding': binding}), encoding='utf-8')
        transport.close(binding, reason='explicit owner closure')
        other_stream = io.BytesIO()
        other_final = self.root / 'second-final.txt'
        other = FakeCLI(self.model, ['codex', '--output-last-message', str(other_final)],
                        other_stream, io.BytesIO(), self.root)
        other.finish(second, second_answer)
        self.assertEqual(other.returncode, 1)
        self.assertEqual(self.model.receipts[-1]['state'], 'closed')
        self.assertEqual(other_stream.getvalue(), b'')
        self.assertFalse(other_final.exists())
        self.cli.finish(first, first_answer)
        self.assertEqual(self.cli.returncode, 0)
        self.assertEqual(json.loads(self.final.read_bytes()), {'summary': 'first call'})
        self.assertEqual(len(self.model.receipts), 1)

    def test_standalone_output_is_explicit_and_has_no_receipt(self):
        answer = raw({'summary': 'standalone'}, mode='standalone', expected_receipt=None)
        self.cli.finish(answer.make({}, {}), answer)
        self.assertEqual(json.loads(self.final.read_bytes()), {'summary': 'standalone'})
        self.assertEqual(self.cli.returncode, 0)
        self.assertFalse((self.root / 'output.json').exists())
        self.assertEqual(self.model.receipts, [])
        with self.assertRaisesRegex(ValueError, '^bound answers require an exact terminal receipt; standalone answers require None$'):
            Answer(lambda out, ctx: out, mode='standalone')
        with self.assertRaisesRegex(ValueError, '^bound answers require an exact terminal receipt; standalone answers require None$'):
            Answer(lambda out, ctx: out, expected_receipt=None)
        with self.assertRaisesRegex(ValueError, '^bound answers require an exact terminal receipt; standalone answers require None$'):
            Answer(lambda out, ctx: out, expected_receipt='unknown')
