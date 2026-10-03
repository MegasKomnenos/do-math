"""The Lean verifier on the installed Lean and on real Windows Jobs (``formal``).

The Lean tests run the portable compiler (``DO_MATH_KNOWLEDGE_TEST_LEAN`` when
set, else ``portable_bin(toolchain_root())/'lean.exe'``) through the product's
real Job transport, with no expected identity unless a test gives one, so
``inspect_toolchain`` observes the compiler with its own ``--version`` Job. A
worktree reaches the toolchain through a junction to the main tree's
``.skill-workspace/do-math-toolchains``. The Job tests run small Python programs
in real Jobs, where the process tree, the termination and the native exit code
are the operating system's.
"""
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

from do_math import formal
from do_math.formal import inspect_toolchain, toolchain_root, verify_lean
from do_math.lean_evidence import compare_formal_results, portable_bin, toolchain_errors
from support.provider_inputs import actual_command
from support.provider_probes import ObservedCalls
from test_categories import test_group as category


class InstalledLeanTests(unittest.TestCase):
    @category('lean')
    def test_actual_shared_closure_traversal_matches_each_declaration_checked_alone(self):
        from support.entry import entry
        _entry = entry()
        from do_math.wiring import real_ports
        _entry.ports = real_ports(environment=_entry.environment)
        source = ('def base : Nat := 1\ndef mid : Nat := base\ntheorem leaf : mid = mid := rfl\n'
                  "theorem em' (p : Prop) : p ∨ ¬p := Classical.em p\ntheorem t : True := True.intro\n")
        names = ['leaf', "em'", 't']
        with tempfile.TemporaryDirectory() as d:
            together = verify_lean(source=source, declarations=names, workspace=Path(d), lean_command=actual_command(), clock=_entry.ports.clock, environment=_entry.environment, jobs=_entry.ports.jobs, git_backend=_entry.ports.git_backend)
            alone = {name: verify_lean(source=source, declarations=[name], workspace=Path(d), lean_command=actual_command(), clock=_entry.ports.clock, environment=_entry.environment, jobs=_entry.ports.jobs, git_backend=_entry.ports.git_backend)
                     for name in names}
        self.assertEqual(together['status'], 'verified', together)
        self.assertEqual(set(together['axioms']["em'"]), {'Classical.choice', 'Quot.sound', 'propext'})
        for name, result in alone.items():
            self.assertEqual(result['status'], 'verified', result)
            for field in ('axioms', 'dependency_closure', 'declaration_evidence', 'declaration_signatures'):
                self.assertEqual(together[field][name], result[field][name], (field, name))
            self.assertEqual({dependency: together['dependency_evidence'][dependency]
                              for dependency in result['dependency_closure'][name]}, result['dependency_evidence'])

    @category('lean')
    def test_actual_exact_unicode_names_and_expressions_are_not_normalized(self):
        from support.entry import entry
        _entry = entry()
        from do_math.wiring import real_ports
        _entry.ports = real_ports(environment=_entry.environment)
        names = ['\u212a', 'K']
        source = 'theorem \u212a (\u2126 : True) : True := \u2126\r\ntheorem K : True := True.intro\n-- e\u0301\n'
        with tempfile.TemporaryDirectory() as d:
            result = verify_lean(source=source, declarations=names, workspace=Path(d), lean_command=actual_command(), clock=_entry.ports.clock, environment=_entry.environment, jobs=_entry.ports.jobs, git_backend=_entry.ports.git_backend)
        self.assertEqual(result['status'], 'verified', {k: result.get(k) for k in ('status', 'reason', 'stderr')})
        self.assertEqual(result['source_sha256'], hashlib.sha256(source.encode()).hexdigest())
        self.assertEqual(result['declarations'], names)
        self.assertEqual(set(result['declaration_evidence']), set(names))
        self.assertEqual(set(result['declaration_signatures']), set(names))
        self.assertIn('\u2126', result['declaration_signatures'][names[0]])

    @category('lean')
    def test_actual_prime_declarations_have_signatures_and_axioms(self):
        from support.entry import entry
        _entry = entry()
        from do_math.wiring import real_ports
        _entry.ports = real_ports(environment=_entry.environment)
        with tempfile.TemporaryDirectory() as d:
            names = ["sumTo_succ'", "N.foo''", "α'"]
            source = ("theorem sumTo_succ' (n : Nat) : n = n := rfl\nnamespace N\ntheorem foo'' : True := by trivial\n"
                      "end N\ntheorem α' : True := by trivial")
            result = verify_lean(source=source, declarations=names, workspace=Path(d), lean_command=actual_command(), clock=_entry.ports.clock, environment=_entry.environment, jobs=_entry.ports.jobs, git_backend=_entry.ports.git_backend)
            self.assertEqual(result['status'], 'verified', result)
            self.assertEqual(set(result['declaration_signatures']), set(names))
            self.assertEqual(set(result['axioms']), set(names))
            self.assertEqual(set(result['declaration_evidence']), set(names))
            self.assertEqual(set(result['dependency_evidence']),
                             {d for name in names for d in result['dependency_closure'][name]})

    @category('lean')
    def test_actual_signatures_preserve_binders_and_unicode(self):
        from support.entry import entry
        _entry = entry()
        from do_math.wiring import real_ports
        _entry.ports = real_ports(environment=_entry.environment)
        with tempfile.TemporaryDirectory() as d:
            r = verify_lean(source='theorem good (n : Nat) : n = n := rfl\n'
                                   'def unicodeGood : ∀ α : Type, α → α := fun _ x => x',
                            declarations=['good', 'unicodeGood'], workspace=Path(d), lean_command=actual_command(), clock=_entry.ports.clock, environment=_entry.environment, jobs=_entry.ports.jobs, git_backend=_entry.ports.git_backend)
            self.assertEqual(r['status'], 'verified')
            self.assertIn('(n : Nat)', r['declaration_signatures']['good'])
            self.assertIn('α', r['declaration_signatures']['unicodeGood'])

    @category('lean')
    def test_actual_changed_transitive_body_requires_identity_reassessment(self):
        """About 50 s as the class's first Lean run on a cold file cache (Lean's start loads its prelude), 8 s otherwise."""
        from support.entry import entry
        _entry = entry()
        from do_math.wiring import real_ports
        _entry.ports = real_ports(environment=_entry.environment)
        results = []
        with tempfile.TemporaryDirectory() as d:
            for value in (1, 2):
                result = verify_lean(source=f'def base : Nat := {value}\ndef mid : Nat := base\ntheorem leaf : mid = mid := rfl',
                                     declarations=['leaf'], workspace=Path(d), lean_command=actual_command(), clock=_entry.ports.clock, environment=_entry.environment, jobs=_entry.ports.jobs, git_backend=_entry.ports.git_backend)
                self.assertEqual(result['status'], 'verified', result)
                self.assertIn('base', result['dependency_closure']['leaf'])
                results.append(result)
        comparison = compare_formal_results(*results)
        self.assertTrue(comparison['requires_identity_review'])
        self.assertIn('dependency_evidence', comparison['changed'])
        self.assertFalse(compare_formal_results(results[0], results[0])['requires_identity_review'])

    @category('lean')
    def test_installed_lean_extracts_transitive_constants(self):
        from support.entry import entry
        _entry = entry()
        from do_math.wiring import real_ports
        _entry.ports = real_ports(environment=_entry.environment)
        command = [os.environ.get('DO_MATH_KNOWLEDGE_TEST_LEAN', str(portable_bin(toolchain_root()) / 'lean.exe'))]
        if not Path(command[0]).is_file():
            self.skipTest('installed Lean is unavailable')
        # Use the installed compiler through its actual local Job transport.
        with tempfile.TemporaryDirectory() as directory:
            result = verify_lean(source='def base : Nat := 1\ndef mid : Nat := base\ntheorem leaf : mid = base := rfl',
                                 declarations=['leaf'], workspace=Path(directory), lean_command=command, clock=_entry.ports.clock, environment=_entry.environment, jobs=_entry.ports.jobs, git_backend=_entry.ports.git_backend)
        self.assertEqual(result['status'], 'verified', result)
        self.assertIn('dependency_closure', result)
        self.assertIn('base', result['dependency_closure']['leaf'])
        self.assertIn('mid', result['dependency_closure']['leaf'])
        self.assertIn('leaf', result['declaration_evidence'])

    @category('lean')
    def test_path_lookup_spelling_matches_the_inspected_executable(self):
        """The command names the installed Lean in another letter case; the identity keeps the file's own spelling."""
        from support.entry import entry
        _entry = entry()
        from do_math.wiring import real_ports
        _entry.ports = real_ports(environment=_entry.environment)
        if os.name != 'nt':
            self.skipTest('Windows PATHEXT lookup keeps the spelling of its argument')
        lean = Path(actual_command()[0])
        command = [str(lean).upper()]
        self.assertNotEqual(command[0], str(lean.resolve()))
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve()
            observed = inspect_toolchain(command, root, clock=_entry.ports.clock, environment=_entry.environment, jobs=_entry.ports.jobs, git_backend=_entry.ports.git_backend)
            self.assertEqual(observed['executable'], str(lean.resolve()))
            result = verify_lean(source='theorem x : True := True.intro', declarations=['x'], workspace=root,
                                 lean_command=command, expected_toolchain=observed, clock=_entry.ports.clock, environment=_entry.environment, jobs=_entry.ports.jobs, git_backend=_entry.ports.git_backend)
        # Not rejected as a changed identity: the compile ran and checked the source.
        self.assertEqual((result['status'], result['reason']), ('verified', None), result)
        self.assertEqual(result['toolchain'], observed)


class ToolchainContractTests(unittest.TestCase):
    @category('lean')
    def test_inspection_matches_actual_formal_verifier(self):
        from support.entry import entry
        _entry = entry()
        from do_math.wiring import real_ports
        _entry.ports = real_ports(environment=_entry.environment)
        command = [str(portable_bin(toolchain_root()) / 'lean.exe')]
        if not Path(command[0]).is_file():
            self.skipTest('portable Lean is not installed')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            observed = inspect_toolchain(command, root, clock=_entry.ports.clock, environment=_entry.environment, jobs=_entry.ports.jobs, git_backend=_entry.ports.git_backend)
            self.assertEqual(toolchain_errors(observed), [])
            result = verify_lean(source='theorem repair_probe : True := True.intro', declarations=['repair_probe'],
                                 workspace=root, lean_command=command, expected_toolchain=observed, clock=_entry.ports.clock, environment=_entry.environment, jobs=_entry.ports.jobs, git_backend=_entry.ports.git_backend)
            self.assertEqual(result['status'], 'verified', result)
            self.assertEqual(result['toolchain'], observed)


# The manifest the installed Lake writes for this project when it has none; with it in place Lake leaves the
# project's inputs as they are, so an observation does not itself change what the next one is keyed by.
MANIFEST = ('{"version": "1.2.0",\n "packagesDir": ".lake/packages",\n "packages": [],\n "name": "fixture",\n'
            ' "lakeDir": ".lake",\n "fixedToolchain": false}\n')


class LakeEnvironmentTests(unittest.TestCase):
    @category('lean')
    def test_lake_search_paths_are_observed_once_per_unchanged_project_input(self):
        """The installed Lake reports the search paths from a real Job; the product observes them once per input."""
        from support.entry import entry
        _entry = entry()
        from do_math.wiring import real_ports
        _entry.ports = real_ports(environment=_entry.environment)
        lake = portable_bin(toolchain_root()) / 'lake.exe'
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve()
            project = root / 'project'
            project.mkdir()
            (project / 'lakefile.toml').write_text('name = "fixture"\n', encoding='utf-8')
            manifest = project / 'lake-manifest.json'
            manifest.write_text(MANIFEST, encoding='utf-8')
            command = [str(lake), '--dir', str(project), 'env', 'lean']
            with ObservedCalls(job_run=formal._job_run) as calls:
                first = formal._project_identity(command, workspace=root, clock=_entry.ports.clock, environment=_entry.environment, jobs=_entry.ports.jobs, git_backend=_entry.ports.git_backend)
                self.assertEqual(formal._project_identity(command, workspace=root, clock=_entry.ports.clock, environment=_entry.environment, jobs=_entry.ports.jobs, git_backend=_entry.ports.git_backend), first)
                self.assertEqual(calls.count('job_run'), 1, 'unchanged inputs reuse the observed search paths')
                manifest.write_text(json.dumps(json.loads(MANIFEST)), encoding='utf-8')
                formal._project_identity(command, workspace=root, clock=_entry.ports.clock, environment=_entry.environment, jobs=_entry.ports.jobs, git_backend=_entry.ports.git_backend)
                self.assertEqual(calls.count('job_run'), 2, 'a changed project input is observed again')
            self.assertIn(str(project / '.lake' / 'build' / 'lib' / 'lean'), first['search_paths'])


@category('resource')
class RealJobTests(unittest.TestCase):
    """``formal._job_run`` with no Jobs port: a real Windows Job runs the worker and its program."""

    def test_nested_stop_preserves_flushed_child_output(self):
        from support.entry import entry
        _entry = entry()
        from do_math.wiring import real_ports
        _entry.ports = real_ports(environment=_entry.environment)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            ready = root / 'ready'
            child = ("import time; from pathlib import Path; print('child started',flush=True); Path("
                     + repr(str(ready)) + ").touch(); time.sleep(10)")
            parent = 'import subprocess,sys,time; subprocess.Popen([sys.executable,"-c",' + repr(child) + ']); time.sleep(10)'
            result = formal._job_run([sys.executable, '-c', parent], root, should_stop=ready.exists, clock=_entry.ports.clock, environment=_entry.environment, jobs=_entry.ports.jobs)
        self.assertTrue(result[3])
        self.assertIn('child started', result[1])

    def test_actual_job_stop_without_completion_is_still_stopped(self):
        from support.entry import entry
        _entry = entry()
        from do_math.wiring import real_ports
        _entry.ports = real_ports(environment=_entry.environment)
        with tempfile.TemporaryDirectory() as d:
            result = formal._job_run([sys.executable, '-c', 'import time; time.sleep(10)'], Path(d),
                                     should_stop=lambda: True, clock=_entry.ports.clock, environment=_entry.environment, jobs=_entry.ports.jobs)
        self.assertTrue(result[3])

    def test_native_compiler_crash_code_reaches_the_verifier(self):
        """A compiler process ending with an NTSTATUS code: the real worker and Job carry it to the verdict."""
        from support.entry import entry
        _entry = entry()
        from do_math.wiring import real_ports
        _entry.ports = real_ports(environment=_entry.environment)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            fake = root / 'compiler.py'
            fake.write_text("import sys,ctypes\nif '--version' in sys.argv: print('synthetic compiler')\n"
                            "else: ctypes.windll.kernel32.ExitProcess(0xC0000005)\n", encoding='utf8')
            result = verify_lean(source='theorem good : True := True.intro', declarations=['good'],
                                 workspace=root, lean_command=[sys.executable, str(fake)], clock=_entry.ports.clock, environment=_entry.environment, jobs=_entry.ports.jobs, git_backend=_entry.ports.git_backend)
        self.assertEqual(result['status'], 'failed')
        self.assertEqual(result.get('exit_code'), 0xC0000005)
        self.assertEqual(result['reason'], 'compiler crashed')


if __name__ == '__main__':
    unittest.main()
