"""The CLI's ``decision --file`` sends the file's exact text and parsed change (``cli.execute``), over the real Git process.

``cli.execute`` opens the repository with the product's default ports and takes
no Ports (이음매 장부 6), so the decision runs the real Git process and the real
clock; that places this test with the boundary tests. The instance is a new
Git repository with the public ``initialize`` only (``research_fixtures.new_instance``).
The decision is the user's governance adoption; how the engine applies an
import approval sent the same way is ``sim.test_governance_approval``'s.
"""
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest

from do_math import cli
from do_math.engine import ResearchEngine, control
from research_fixtures import charter, new_instance


class CliDecisionFileTests(unittest.TestCase):
    def test_decision_file_crlf_text_is_the_preserved_decision_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            iid = new_instance(root, goal='User approves P', workspace=root / 'work', config={'scholarly_enabled': False})
            spec = {'kind': 'initialization', 'operation': 'governance', 'records': [charter()]}
            text = json.dumps(spec, ensure_ascii=False, indent=2).replace('\n', '\r\n') + '\r\n'
            path = root / 'exact-decision.json'
            path.write_bytes(text.encode('utf-8'))
            response = io.StringIO()
            with redirect_stdout(response):
                code = cli.main(['decision', '--repository', str(root), '--instance', iid,
                                 '--file', str(path), '--request-id', 'adopt-charter'])
            self.assertEqual(code, 0, response.getvalue())
            result = json.loads(response.getvalue())['result']
            self.assertEqual(result['effect'], 'applied')
            restarted = ResearchEngine(root, iid)
            self.assertEqual([row['text'] for row in restarted.instance['governance_sources'].values()
                              if row['text'] == text], [text])
            self.assertEqual(restarted.instance['governance']['CH1']['content'], charter()['content'])
            replay = control(root, iid, 'decision', text=text, config={'change': spec}, request_id='adopt-charter')
            self.assertEqual(replay['snapshot'], result['snapshot'])


if __name__ == '__main__':
    unittest.main()
