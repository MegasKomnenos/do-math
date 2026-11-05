import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from retention import conversation


class RetentionTests(unittest.TestCase):
    def test_native_messages_and_tool_output_are_not_truncated_or_duplicated(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            middle = 'begin\n' + ('a' * 4000) + 'THE DECISIVE MIDDLE' + ('z' * 4000) + '\nend'
            rows = [
                {'type': 'event_msg', 'payload': {'type': 'agent_message', 'message': 'Duplicated transport event'}},
                {'type': 'response_item', 'payload': {'type': 'message', 'role': 'assistant', 'content': [{'type': 'output_text', 'text': 'The mathematical account.'}]}},
                {'type': 'response_item', 'payload': {'type': 'custom_tool_call', 'name': 'exec', 'input': 'print(1 + 1)'}},
                {'type': 'response_item', 'payload': {'type': 'custom_tool_call_output', 'output': middle}},
                {'type': 'response_item', 'payload': {'type': 'reasoning', 'summary': [], 'encrypted_content': 'OPAQUE_TRANSPORT'}},
            ]
            source = root / 'native.jsonl'
            source.write_text('\n'.join(json.dumps(r) for r in rows), encoding='utf-8')
            target = root / 'conversation.md'
            self.assertEqual(conversation(source, target, True), 3)
            result = target.read_text(encoding='utf-8')
            self.assertIn(middle, result)
            self.assertIn('print(1 + 1)', result)
            self.assertNotIn('Duplicated transport event', result)
            self.assertNotIn('OPAQUE_TRANSPORT', result)


if __name__ == '__main__':
    unittest.main()
