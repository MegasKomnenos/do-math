"""The command-line surface: arguments and JSON requests are validated before any effect, and reads name their snapshot."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import cli
from do_math.repository import ResearchRepository, new_id
from research_fixtures import current_state, git_init


class CliSurfaceTests(unittest.TestCase):
    def test_file_query_and_read_include_resolved_snapshot_provenance(self):
        # CLI imports ENGINE, so keep this boundary test independent of any
        # concurrent engine/observation implementation work.
        from do_math.cli import build_parser, execute
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            git_init(root)
            identifier = new_id("RI")
            store = ResearchRepository(root, identifier)
            head = store.initialize(*current_state({"id": identifier, "sources": [], "knowledge": {}, "trust_environments": {}},
                                    {"tasks": {}, "executions": {}, "queue": [], "status": "ready", "question_links": []}))
            parser = build_parser()
            query, code = execute(parser.parse_args(["query", "--repository", str(root), "--instance", identifier,
                                                      "--files", "--prefix", "research/", "--limit", "1"]))
            self.assertEqual(code, 0)
            self.assertEqual(query["provenance"]["snapshot"], head)
            self.assertEqual(query["provenance"]["filters"]["prefix"], "research/")
            path = store.list_files("research/", head)[0]
            read, code = execute(parser.parse_args(["read", "--repository", str(root), "--instance", identifier,
                                                     "--path", path]))
            self.assertEqual(code, 0)
            self.assertEqual(read["snapshot"], head)
            self.assertEqual(len(read["sha256"]), 64)

    def test_unknown_init_option_has_no_repository_or_workspace_effect(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.object(cli, '_require_git') as git:
                with self.assertRaisesRegex(ValueError, 'unrecognized'):
                    cli.build_parser().parse_args(['init', '--repository', str(root/'repo'),
                        '--workspace', str(root/'work'), '--goal', 'Compare methods', '--invented-option', 'value'])
                git.assert_not_called()
            self.assertEqual(list(root.iterdir()), [])
            request = {'schema_version':5, 'command':'init', 'payload':{'repository':str(root/'repo'),
                'workspace':str(root/'work'), 'goal':'Compare methods', 'invented_option':'value'}}
            with patch.object(cli, '_require_git') as git:
                with self.assertRaisesRegex(ValueError, 'unknown|unrecognized|unexpected'):
                    cli._json_arguments(cli.build_parser(), request)
                git.assert_not_called()


if __name__ == "__main__":
    unittest.main()
