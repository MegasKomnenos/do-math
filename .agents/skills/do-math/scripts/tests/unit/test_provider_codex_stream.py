"""Codex ``exec --json`` streams as the collector parses them (``codex_stream.parse_jsonl``, layer 1).

A stream establishes completion only with its own well-formed terminal event:
a parse stops at the first row it cannot read exactly, and what it read
before stays reported.
"""
import unittest

from do_math.codex_stream import parse_jsonl, stderr_diagnostics


class CodexStreamTests(unittest.TestCase):
    def test_stderr_diagnostics_index_exact_log_lines_without_decoding_other_bytes(self):
        line = (b'2026-10-20T15:55:28.118316Z ERROR codex_models_manager::manager: '
                b'failed to refresh available models: request timed out')
        prefix = b'\xff\xfe\r\n'
        raw = prefix + line + b'\r\n' + line
        diagnostics = stderr_diagnostics(raw)
        self.assertEqual([row['source'] for row in diagnostics], [
            {'artifact': 'stderr', 'offset': len(prefix), 'bytes': len(line) + 2},
            {'artifact': 'stderr', 'offset': len(prefix) + len(line) + 2, 'bytes': len(line)}])
        self.assertEqual([raw[row['source']['offset']:row['source']['offset'] + row['source']['bytes']]
                          for row in diagnostics], [line + b'\r\n', line])
        self.assertEqual(stderr_diagnostics(line.replace(b'ERROR', b'WARN'))[0]['reported_level'], 'WARN')
        for other in (None, b'', b'request timed out\n', b'quoted: ' + line,
                      line.replace(b'codex_models_manager::manager', b'other_component'),
                      line.replace(b'request timed out', b'connection failed')):
            with self.subTest(raw=other):
                self.assertEqual(stderr_diagnostics(other), [])

    def test_native_error_is_a_complete_failure_only_with_its_failed_terminal(self):
        prefix = (b'{"type":"thread.started","thread_id":"failed-request"}\n'
                  b'{"type":"turn.started"}\n'
                  b'{"type":"error","message":"request rejected"}\n')
        failed = parse_jsonl(prefix + b'{"type":"turn.failed","error":{"message":"request rejected"}}\n')
        self.assertTrue(failed['parse_complete'])
        self.assertTrue(failed['turn_failed'])
        self.assertFalse(failed['turn_completed'])
        self.assertEqual(failed['unknown_events'], [])
        self.assertNotIn('final_text', failed)
        for suffix in (b'', b'{"type":"turn.completed"}\n'):
            with self.subTest(suffix=suffix):
                self.assertFalse(parse_jsonl(prefix + suffix)['parse_complete'])

    def test_jsonl_tail_and_missing_terminal_are_not_success(self):
        parsed = parse_jsonl(b'{"type":"thread.started","thread_id":"t"}\nnot-json')
        self.assertEqual(parsed["thread_id"], "t")
        self.assertFalse(parsed["turn_completed"])
        self.assertFalse(parsed["parse_complete"])
        self.assertEqual(parsed["unparsed_tail_bytes"], len(b"not-json"))

    def test_ambiguous_or_nonfinite_native_events_cannot_establish_completion(self):
        prefix = (b'{"type":"thread.started","thread_id":"t"}\n'
                  b'{"type":"turn.started"}\n')
        invalid = [b'{"type":"turn.failed","type":"turn.completed"}\n',
                   b'{"type":"turn.completed","usage":{"tokens":1,"tokens":2}}\n',
                   b'{"type":"turn.completed","usage":{"cost":NaN}}\n',
                   b'{"type":"turn.completed","usage":{"cost":Infinity}}\n',
                   b'{"type":"turn.completed","usage":{"cost":-Infinity}}\n',
                   b'{"type":"turn.completed","usage":{"cost":1e999}}\n']
        for terminal in invalid:
            with self.subTest(terminal=terminal):
                parsed = parse_jsonl(prefix + terminal)
                self.assertFalse(parsed["parse_complete"])
                self.assertFalse(parsed["turn_completed"])
                self.assertEqual(parsed["parsed_bytes"], len(prefix))
                self.assertEqual(parsed["unparsed_tail_bytes"], len(terminal))
                self.assertEqual(parsed["unknown_events"][0]["kind"], "invalid_jsonl")
        valid = parse_jsonl(prefix + b'{"type":"turn.completed","usage":{"cost":0.25}}\n')
        self.assertTrue(valid["parse_complete"])
        self.assertTrue(valid["turn_completed"])
        self.assertEqual(valid["usage"], [{"cost": 0.25}])


if __name__ == "__main__":
    unittest.main()
