"""Codex ``exec --json`` streams as the collector parses them (``codex_stream.parse_jsonl``, layer 1).

A stream establishes completion only with its own well-formed terminal event:
a parse stops at the first row it cannot read exactly, and what it read
before stays reported.
"""
import unittest

from do_math.codex_stream import parse_jsonl


class CodexStreamTests(unittest.TestCase):
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
