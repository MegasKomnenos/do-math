"""The CLI's file query and file read name the snapshot they read (``cli.execute``), over the real Git process.

``cli.execute`` opens the repository with the product's default ports and takes
no Ports, so its reads run the real Git process; that places this test with
the boundary tests, as ``test_setup_lean_compile`` is placed for its real Job.
The repository is laid out without a git process (``make_repository``) and
written through the real backend.
"""
import hashlib
from pathlib import Path
import tempfile
import unittest

from do_math.cli import build_parser, execute
from do_math.repository import ResearchRepository
from research_fixtures import current_state
from support.fakes.clock import FakeClock
from support.fakes.git_backend import make_repository


class CliFileReadTests(unittest.TestCase):
    def test_file_query_and_read_include_resolved_snapshot_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            root = make_repository(Path(directory))
            identifier = FakeClock().new_id('RI')
            store = ResearchRepository(root, identifier)
            head = store.initialize(*current_state(
                {'id': identifier, 'sources': [], 'knowledge': {}, 'trust_environments': {}},
                {'tasks': {}, 'executions': {}, 'queue': [], 'status': 'ready', 'question_links': []}))
            parser = build_parser()
            query, code = execute(parser.parse_args(['query', '--repository', str(root), '--instance', identifier,
                                                     '--files', '--prefix', 'research/', '--limit', '1']))
            self.assertEqual(code, 0)
            self.assertEqual(query['provenance']['snapshot'], head)
            self.assertEqual(query['provenance']['filters']['prefix'], 'research/')
            path = store.list_files('research/', head)[0]
            read, code = execute(parser.parse_args(['read', '--repository', str(root), '--instance', identifier,
                                                    '--path', path]))
            self.assertEqual(code, 0)
            self.assertEqual(read['snapshot'], head)
            self.assertEqual(len(read['sha256']), 64)
            self.assertEqual(read['sha256'], hashlib.sha256(store.read(path, head)).hexdigest())


if __name__ == '__main__':
    unittest.main()
