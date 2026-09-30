"""The Lake project's source identity (``formal.project_source_identity``, layer 3) run directly on real Git.

The identity reads the project with short ``git`` processes the product starts
itself (``formal._git``; no port stands for them), so these tests make real
repositories. It also reaches the role input of intent interpretation, where
it must stay small.
"""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from do_math import execution_profiles
from do_math.context_store import prepare_role_input
from do_math.formal import project_source_identity
from record_fixtures import surface_state
from research_fixtures import git_init
from support.provider_probes import ObservedCalls


class ProjectSourceIdentityTests(unittest.TestCase):
    def test_project_preparation_honors_stop_before_starting_git(self):
        with tempfile.TemporaryDirectory() as d, ObservedCalls(popen=subprocess.Popen.__init__) as calls:
            with self.assertRaisesRegex(RuntimeError, 'stopped'):
                project_source_identity(Path(d), should_stop=lambda: True)
        self.assertEqual(calls.count('popen'), 0, 'no process started before the stop')

    def test_project_source_identity_excludes_unrelated_and_tracks_project_changes(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            project = root / 'project'
            project.mkdir()
            (project / 'Main.lean').write_text('def x := 1', encoding='utf8')
            (root / 'unrelated').mkdir()
            (root / 'unrelated' / 'x').write_text('a', encoding='utf8')
            subprocess.run(['git', '-C', str(root), 'init', '-q'], check=True)
            subprocess.run(['git', '-C', str(root), 'add', '.'], check=True)
            subprocess.run(['git', '-C', str(root), '-c', 'user.name=t', '-c', 'user.email=t@x', 'commit', '-qm', 'base'],
                           check=True)
            before = project_source_identity(project)
            (project / '.lake' / 'packages' / 'dep').mkdir(parents=True)
            (project / '.lake' / 'packages' / 'dep' / 'Dep.lean').write_text('def y := 1', encoding='utf8')
            self.assertEqual(before, project_source_identity(project))
            (root / 'unrelated' / 'x').write_text('b', encoding='utf8')
            subprocess.run(['git', '-C', str(root), 'add', 'unrelated/x'], check=True)
            subprocess.run(['git', '-C', str(root), '-c', 'user.name=t', '-c', 'user.email=t@x', 'commit', '-qm',
                            'unrelated'], check=True)
            self.assertEqual(before, project_source_identity(project))
            (project / 'Main.lean').write_text('def x := 2', encoding='utf8')
            self.assertNotEqual(before, project_source_identity(project))

    def test_untracked_project_does_not_report_unresolved_git_expression_as_hash(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            project = root / 'untracked'
            project.mkdir()
            (root / 'tracked.txt').write_text('fixture', encoding='utf8')
            (project / 'lakefile.toml').write_text('name = "fixture"', encoding='utf8')
            subprocess.run(['git', '-C', str(root), 'init', '-q'], check=True)
            subprocess.run(['git', '-C', str(root), 'add', 'tracked.txt'], check=True)
            subprocess.run(['git', '-C', str(root), '-c', 'user.name=t', '-c', 'user.email=t@x', 'commit', '-qm',
                            'fixture'], check=True)
            identity = project_source_identity(project)
            self.assertIsNone(identity['git_tree'])
            self.assertEqual(identity['untracked_file_count'], 1)
            self.assertRegex(identity['untracked_sha256'], r'^[0-9a-f]{64}$')


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
