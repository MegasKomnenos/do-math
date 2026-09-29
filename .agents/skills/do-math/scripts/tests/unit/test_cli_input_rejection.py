"""An unknown ``init`` option is refused by the command-line contract (``cli_contract``, layer 2) before any effect.

The argv parser and the JSON request translator run in process. The legacy
test replaced ``cli._require_git`` to see that the Git check was not reached;
here the audit hook sees every process started while the parser or translator
runs (``subprocess.Popen``), which covers the Git check and any other process,
and the folder that would hold the repository and the workspace stays empty.
"""
from pathlib import Path
import tempfile
import unittest

from do_math.cli_contract import CliInputError, _json_arguments, build_parser
from support.storage_files import audit_events


class UnknownInitOptionTests(unittest.TestCase):
    def test_unknown_init_option_has_no_repository_or_workspace_effect(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with audit_events('subprocess.Popen') as started:
                with self.assertRaisesRegex(CliInputError, '^unrecognized arguments: --invented-option value$'):
                    build_parser().parse_args(['init', '--repository', str(root / 'repo'),
                                               '--workspace', str(root / 'work'), '--goal', 'Compare methods',
                                               '--invented-option', 'value'])
            self.assertEqual(started, [])
            self.assertEqual(list(root.iterdir()), [])
            request = {'schema_version': 5, 'command': 'init', 'payload': {
                'repository': str(root / 'repo'), 'workspace': str(root / 'work'), 'goal': 'Compare methods',
                'invented_option': 'value'}}
            with audit_events('subprocess.Popen') as started:
                with self.assertRaisesRegex(CliInputError, r"^invalid command payload: Additional properties are not "
                                                           r"allowed \('invented_option' was unexpected\)$"):
                    _json_arguments(build_parser(), request)
            self.assertEqual(started, [])
            self.assertEqual(list(root.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
