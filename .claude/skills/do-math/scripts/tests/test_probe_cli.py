"""probe_cli argument checks which never call a model."""
from pathlib import Path
import sys
import unittest


class ProbeTests(unittest.TestCase):
    def test_claude_model_names_reach_the_runner_with_one_provider_prefix(self):
        import tempfile
        from unittest.mock import patch
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        import probe_cli
        for model, routed in (('opus', 'claude:opus'), ('claude:opus', 'claude:opus'),
                              ('claude-opus-5', 'claude-opus-5')):
            with self.subTest(model=model), tempfile.TemporaryDirectory() as directory, \
                    patch.object(probe_cli, 'ModelRunner') as runner:
                runner.return_value.run.return_value = {'status': 'failed', 'output': None}
                probe_cli.run_case(Path(directory), 'structured', provider='claude', model=model,
                                   effort='low', timeout=1, only_assigned=False)
                self.assertEqual(runner.return_value.run.call_args.kwargs['model'], routed)

    def test_live_report_hashes_every_implementation_module(self):
        import json
        import tempfile
        from unittest.mock import patch
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        import probe_cli
        with tempfile.TemporaryDirectory() as directory, \
                patch.object(probe_cli, 'run_case', return_value={'case': 'structured', 'passed': True}), \
                patch('builtins.print'):
            probe_cli.main(['--provider', 'codex', '--model', 'fixture-model', '--cases', 'structured',
                            '--output-dir', str(Path(directory) / 'evidence')])
            report = json.loads((Path(directory) / 'evidence' / 'report.json').read_text(encoding='utf-8'))
        package = Path(probe_cli.__file__).parent / 'do_math'
        self.assertEqual(set(report['sources']),
                         {str(path.relative_to(package.parent)) for path in package.rglob('*.py')})


if __name__ == "__main__":
    unittest.main()
