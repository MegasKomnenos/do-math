"""Real filesystem identity and role-input wiring over declared Git worktrees."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from do_math import execution_profiles
from do_math.context_store import prepare_role_input
from do_math.formal import project_source_identity, verify_lean
from do_math.file_io import cached_sha256
from support.knowledge_verifier_jobs import approved_toolchain
from support.record_builders import surface_state
from support.fakes.git_backend import make_repository, InProcessGit, ProjectWorktree
from support.provider_probes import ObservedCalls


class ProjectSourceIdentityTests(unittest.TestCase):
    def setUp(self):
        self.git_backend = InProcessGit()

    def test_project_root_memo_accepts_unhashable_equal_backend_worlds(self):
        """포트 계약에 없는 hash/동등성 조건으로 서로 다른 Git 세계를 합치지 않는다."""
        class EqualGitWorld(InProcessGit):
            __hash__ = None

            def __eq__(self, other):
                return isinstance(other, EqualGitWorld)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / 'Main.lean').write_bytes(b'def x := 1\n')
            first, second = EqualGitWorld(), EqualGitWorld()
            self.assertEqual(first, second)
            self.assertIsNot(first, second)
            second.worktrees[root] = ProjectWorktree(
                trees={'.': 'd' * 40}, tracked_paths=frozenset({'Main.lean'}))
            outside = project_source_identity(root, git_backend=first)
            tracked = project_source_identity(root, git_backend=second)
            self.assertIsNone(outside['git_tree'])
            self.assertEqual(outside['untracked_file_count'], 1)
            self.assertEqual(tracked['git_tree'], 'd' * 40)
            self.assertEqual(tracked['untracked_file_count'], 0)
            self.assertEqual(project_source_identity(root, git_backend=first), outside)
            self.assertEqual(project_source_identity(root, git_backend=second), tracked)

    def test_project_preparation_honors_stop_before_starting_git(self):
        with tempfile.TemporaryDirectory() as d, ObservedCalls(popen=subprocess.Popen.__init__) as calls:
            with self.assertRaisesRegex(RuntimeError, 'stopped'):
                project_source_identity(Path(d), git_backend=self.git_backend, should_stop=lambda: True)
        self.assertEqual(calls.count('popen'), 0, 'no process started before the stop')

    def test_project_source_identity_excludes_unrelated_and_tracks_project_changes(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            project = root / 'project'
            project.mkdir()
            (project / 'Main.lean').write_text('def x := 1', encoding='utf8')
            (root / 'unrelated').mkdir()
            (root / 'unrelated' / 'x').write_text('a', encoding='utf8')
            state = ProjectWorktree(trees={'project': 'a' * 40},
                                    tracked_paths=frozenset({'project/Main.lean', 'unrelated/x'}))
            self.git_backend.worktrees[root.resolve()] = state
            before = project_source_identity(project, git_backend=self.git_backend)
            (project / '.lake' / 'packages' / 'dep').mkdir(parents=True)
            (project / '.lake' / 'packages' / 'dep' / 'Dep.lean').write_text('def y := 1', encoding='utf8')
            self.assertEqual(before, project_source_identity(project, git_backend=self.git_backend))
            (root / 'unrelated' / 'x').write_text('b', encoding='utf8')
            # The unrelated commit changes only the repository root tree.
            state.trees['.'] = 'b' * 40
            self.assertEqual(before, project_source_identity(project, git_backend=self.git_backend))
            (project / 'Main.lean').write_text('def x := 2', encoding='utf8')
            state.diffs['project'] = b'-def x := 1\n+def x := 2\n'
            self.assertNotEqual(before, project_source_identity(project, git_backend=self.git_backend))

    def test_untracked_project_does_not_report_unresolved_git_expression_as_hash(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            project = root / 'untracked'
            project.mkdir()
            (root / 'tracked.txt').write_text('fixture', encoding='utf8')
            (project / 'lakefile.toml').write_text('name = "fixture"', encoding='utf8')
            self.git_backend.worktrees[root.resolve()] = ProjectWorktree(
                trees={'.': 'c' * 40}, tracked_paths=frozenset({'tracked.txt'}))
            identity = project_source_identity(project, git_backend=self.git_backend)
            self.assertIsNone(identity['git_tree'])
            self.assertEqual(identity['untracked_file_count'], 1)
            self.assertRegex(identity['untracked_sha256'], r'^[0-9a-f]{64}$')

    def test_project_root_memo_is_separate_for_backend_worlds_and_moved_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            project = root / 'project'
            project.mkdir()
            (project / 'Main.lean').write_bytes(b'def x := 1\n')
            first = project_source_identity(project, git_backend=self.git_backend)
            other = InProcessGit()
            state = ProjectWorktree(trees={'.': 'a' * 40}, tracked_paths=frozenset({'Main.lean'}))
            other.worktrees[project] = state
            second = project_source_identity(project, git_backend=other)
            self.assertEqual(first['untracked_file_count'], 1)
            self.assertIsNone(first['git_tree'])
            self.assertEqual(second['untracked_file_count'], 0)
            self.assertEqual(second['git_tree'], 'a' * 40)
            # Same-world memo of no repository deliberately remains until owner reset.
            self.git_backend.worktrees[project] = state
            self.assertEqual(project_source_identity(project, git_backend=self.git_backend), first)
            moved = root / 'moved'
            project.rename(moved)
            other.worktrees[moved] = other.worktrees.pop(project)
            current = project_source_identity(moved, git_backend=other)
            self.assertEqual(current, {**second, 'root': str(moved)})

    def test_project_has_no_implicit_backend_or_invalid_root_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            for invalid in (False, None):
                with self.subTest(root=invalid), self.assertRaises(AttributeError) as rejected:
                    project_source_identity(invalid, git_backend=self.git_backend)
                self.assertEqual(rejected.exception.name, 'resolve')
                self.assertIs(rejected.exception.obj, invalid)
                with self.subTest(backend=invalid), self.assertRaises(AttributeError) as rejected:
                    project_source_identity(Path(directory), git_backend=invalid)
                self.assertEqual(rejected.exception.name, 'project_repository_root')
                self.assertIs(rejected.exception.obj, invalid)
            with self.assertRaisesRegex(TypeError, "missing 1 required keyword-only argument: 'git_backend'"):
                project_source_identity(Path(directory))

    def test_filesystem_only_project_keeps_all_input_bytes_and_excludes_lake(self):
        from do_math.lean_evidence import LAKE_PROJECT_FILES
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in LAKE_PROJECT_FILES:
                (root / name).write_bytes(b'first\x00\xff')
            (root / 'Main.lean').write_bytes(b'first\x00\xff')
            (root / '.lake').mkdir()
            (root / '.lake/Ignored.lean').write_bytes(b'dependency')
            initial = project_source_identity(root, git_backend=self.git_backend)
            self.assertEqual(initial['untracked_file_count'], len(LAKE_PROJECT_FILES) + 1)
            for name in (*LAKE_PROJECT_FILES, 'Main.lean'):
                path = root / name
                path.write_bytes(b'changed\x00\xfe')
                self.assertNotEqual(project_source_identity(root, git_backend=self.git_backend), initial)
                path.write_bytes(b'first\x00\xff')
            (root / '.lake/Ignored.lean').write_bytes(b'different')
            self.assertEqual(project_source_identity(root, git_backend=self.git_backend), initial)


class FormalInputManifestTests(unittest.TestCase):
    def setUp(self):
        self.git_backend = InProcessGit()

    def test_project_identity_bounds_role_input_and_detects_file_changes(self):
        from support.entry import entry
        _entry = entry()
        self.git_backend = _entry.ports.git_backend
        instance, runtime = surface_state()
        instance['config']['max_input_bytes'] = 500000
        instance.update(execution_profiles.build_profiles(instance['config'], host=_entry.ports.host))
        profile = next(p for p in instance['execution_profiles'].values()
                       if p['role'] == 'intent_interpretation')
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            project = base / 'project'
            project.mkdir()
            make_repository(project)
            self.git_backend.worktrees[project.resolve()] = ProjectWorktree()
            (project / 'lakefile.toml').write_text('name = "test"\n', encoding='utf-8')
            for index in range(40):
                (project / f'Module{index}.lean').write_text(f'-- source {index}\n', encoding='utf-8')
            identity = project_source_identity(project, git_backend=self.git_backend)
            self.assertLess(len(json.dumps(identity).encode('utf-8')), 1024)
            self.assertEqual(identity['untracked_file_count'], 41)
            path = project / 'Module0.lean'
            path.write_text('-- changed source\n', encoding='utf-8')
            changed = project_source_identity(project, git_backend=self.git_backend)
            self.assertNotEqual(changed, identity)
            path.rename(project / 'Renamed.lean')
            renamed = project_source_identity(project, git_backend=self.git_backend)
            self.assertNotEqual(renamed, changed)
            (project / 'Renamed.lean').unlink()
            removed = project_source_identity(project, git_backend=self.git_backend)
            self.assertNotEqual(removed, renamed)
            self.assertEqual(removed['untracked_file_count'], 40)
            self.assertEqual(removed, project_source_identity(project, git_backend=self.git_backend))
            command, toolchain = approved_toolchain(base)
            lake = Path(command[0]).with_name('lake.exe')
            command = [str(lake), '--dir', str(project), 'env', command[0]]
            toolchain.update(configured_command=command, executable=str(lake), sha256=cached_sha256(lake),
                             project={'source_identity': removed,
                                      'manifest_hashes': {'lakefile.toml': cached_sha256(project / 'lakefile.toml')},
                                      'search_paths': []})
            verifier = {'command': command, 'observed_toolchain': toolchain,
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
                                        artifact_prefix='runtime/artifacts/BA-input', clock=_entry.ports.clock)
            self.assertIsNone(fitted['overflow'], 'Machine-only inventory should not prevent intent interpretation')
            self.assertLess(fitted['actual_bytes'], profile['input']['max_input_bytes'])
            machine_context = json.loads((workspace / 'input/submission/context.json').read_bytes())
            self.assertEqual(machine_context['formal_verifier']['expected_toolchain'], toolchain)
            self.assertEqual(fitted['validation_context']['formal_verifier']['expected_toolchain'], toolchain)
            visible = fitted['context']['formal_verifier']
            self.assertEqual(visible['observed_toolchain']['version'], toolchain['version'])
            self.assertEqual(visible['expected_toolchain'], toolchain)
            self.assertEqual(context['formal_verifier'], verifier)
            # The installed manifest is the verifier's actual input. A later file
            # change must reach currentness through Git + real filesystem reads.
            (project / 'Late.lean').write_bytes(b'theorem late : True := True.intro\n')
            supplied = machine_context['formal_verifier']
            result = verify_lean(source='theorem x : True := True.intro', declarations=['x'],
                workspace=workspace, lean_command=supplied['command'],
                expected_toolchain=supplied['expected_toolchain'],
                jobs=_entry.ports.jobs, clock=_entry.ports.clock, environment=_entry.environment,
                git_backend=self.git_backend)
            self.assertEqual(result['status'], 'rejected')
            self.assertEqual(result['reason'], 'approved project inputs changed before execution')
            self.assertIn('approved project inputs changed', result['identity_errors'])
            self.assertEqual(_entry.ports.jobs.launched, [])


if __name__ == '__main__':
    unittest.main()
