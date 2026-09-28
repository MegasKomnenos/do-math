"""probe_cli argument checks which never call a model."""
from pathlib import Path
import sys
import unittest


class ProbeTests(unittest.TestCase):
    def test_claude_only_cases_and_options_are_rejected_before_live_setup(self):
        import io
        from contextlib import redirect_stderr
        from unittest.mock import patch
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        import probe_cli
        for options in (['--cases', 'background'], ['--only-assigned-model']):
            with self.subTest(options=options), patch.object(Path, 'mkdir') as mkdir, \
                    patch.object(probe_cli, 'run_case') as run, redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as result:
                    probe_cli.main(['--provider', 'codex', '--model', 'must-not-run',
                                    '--output-dir', 'unused-evidence', *options])
                self.assertEqual(result.exception.code, 2)
                mkdir.assert_not_called()
                run.assert_not_called()

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


if __name__ == "__main__":
    unittest.main()
