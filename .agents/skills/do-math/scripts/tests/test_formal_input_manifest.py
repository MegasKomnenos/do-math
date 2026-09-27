from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import execution_profiles
from do_math.context_store import prepare_role_input
from do_math.formal import project_source_identity
from record_fixtures import surface_state
from research_fixtures import git_init


class FormalInputManifestTests(unittest.TestCase):
    def test_project_identity_bounds_role_input_and_detects_file_changes(self):
        instance, runtime = surface_state()
        instance['config']['max_input_bytes'] = 500000
        instance.update(execution_profiles.build_profiles(instance['config']))
        profile = next(p for p in instance['execution_profiles'].values()
                       if p['role'] == 'intent_interpretation')
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            project = base / 'project'
            project.mkdir()
            git_init(project)
            (project / 'lakefile.toml').write_text('name = "test"\n', encoding='utf-8')
            for index in range(40):
                (project / f'Module{index}.lean').write_text(f'-- source {index}\n', encoding='utf-8')
            identity = project_source_identity(project)
            self.assertLess(len(json.dumps(identity).encode('utf-8')), 1024)
            self.assertEqual(identity['untracked_file_count'], 41)
            path = project / 'Module0.lean'
            path.write_text('-- changed source\n', encoding='utf-8')
            changed = project_source_identity(project)
            self.assertNotEqual(changed, identity)
            path.rename(project / 'Renamed.lean')
            renamed = project_source_identity(project)
            self.assertNotEqual(renamed, changed)
            (project / 'Renamed.lean').unlink()
            removed = project_source_identity(project)
            self.assertNotEqual(removed, renamed)
            self.assertEqual(removed['untracked_file_count'], 40)
            self.assertEqual(removed, project_source_identity(project))
            toolchain = {'version': 'Lean test edition', 'executable': 'test-lean', 'sha256': 'b' * 64,
                         'project': {'source_identity': removed}}
            verifier = {'command': ['test-lean'], 'observed_toolchain': toolchain,
                        'expected_toolchain': deepcopy(toolchain), 'allowed_axioms': [],
                        'environment_id': 'TE-fixed', 'environment_status': 'active'}
            context = {'instance_id': instance['id'], 'action': {'id': 'AC-interpret', 'role': 'intent_interpretation'},
                       'user_request': {'text': 'For every n : Nat, n + 0 = n'},
                       'interpretation_to_check': None, 'formal_verifier': verifier}
            workspace = base / 'workspace'
            workspace.mkdir()
            fitted = prepare_role_input(context, instance=instance, runtime=runtime,
                role='intent_interpretation', profile=profile, snapshot='a' * 40,
                workspace=workspace, activity_id='AC-1', install_submission_tools=True,
                artifact_prefix='runtime/artifacts/BA-input')
            self.assertIsNone(fitted['overflow'], 'Machine-only inventory should not prevent intent interpretation')
            self.assertLess(fitted['actual_bytes'], profile['input']['max_input_bytes'])
            machine_context = json.loads((workspace / 'input/submission/context.json').read_bytes())
            self.assertEqual(machine_context['formal_verifier']['expected_toolchain'], toolchain)
            self.assertEqual(fitted['validation_context']['formal_verifier']['expected_toolchain'], toolchain)
            visible = fitted['context']['formal_verifier']
            self.assertEqual(visible['observed_toolchain']['version'], toolchain['version'])
            self.assertEqual(visible['expected_toolchain'], toolchain)
            self.assertEqual(context['formal_verifier'], verifier)


if __name__ == '__main__':
    unittest.main()
