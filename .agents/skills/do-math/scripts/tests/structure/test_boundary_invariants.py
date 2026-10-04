"""Static invariants at the product's outside boundary (의무 9-A; 조사 코드-구조 2.2).

Each table below declares every place the product crosses one kind of boundary,
with the reason it may. A new crossing that is not declared fails, so it is
reviewed once instead of being found in operation:

- ``PROCESS_STARTS``: direct ``subprocess`` calls. Long-lived children run in a
  Job through the Jobs port; what is left are short calls the owner waits on.
- ``INJECTED_STARTS``: calls of an injected process starter (``spawn``, ``runner``).
- ``INTERPRETER_USES``: ``sys.executable``. A command a person or a worker runs
  from a shell uses ``file_io.console_python()`` (조사 C-09, a scheduled
  engine's ``pythonw.exe`` in a worker's command); a process the owner starts
  itself with piped output keeps ``sys.executable``.

Every subprocess start uses the standard ``CREATE_NO_WINDOW`` value and the
native Job root passes that bit to ``CreateProcessW`` (조사 A-16);
no script module shadows a standard-library module (조사 A-12), and only
``file_io`` replaces files.
"""
import ast
from pathlib import Path
import sys
import unittest


SCRIPTS = Path(__file__).resolve().parents[2]
RUNNERS = {'run_tests.py', 'test_categories.py'}

PROCESS_STARTS = {
    ('do_math/codex_adapter.py', 'run'): 'the CLI surface probe (--version, --help)',
    ('setup_lean.py', 'run'): 'the Lean setup tool',
}
INJECTED_STARTS = {
    ('do_math/git_process.py', 'initialize_repository', '_run_process'): 'CLI Git init, preserving ambient environment and exit-only result',
    ('do_math/git_process.py', 'repository_exists', '_run_process'): 'CLI Git directory existence, preserving the accepted repository population',
    ('do_math/git_process.py', '_run', '_run_process'): 'the Git backend external subprocess boundary',
    ('do_math/git_process.py', '_project_read', '_run_process'): 'project identity Git reads, preserving ambient configuration',
    ('do_math/cli_worker.py', 'run_cli', 'spawn'): 'the provider CLI inside the worker Job',
    ('do_math/formal.py', '_worker', 'spawn'): 'Lean inside the Lean worker Job',
    ('do_math/powershell_scheduler.py', 'run', 'runner'): 'the task scheduler script',
}
# These callers moved process execution behind the shared Job/worker boundary.
# Keep the caller population as well as the worker's actual spawn in the inventory.
JOB_RUN_STARTS = {
    ('do_math/formal.py', '_project_identity'),
    ('do_math/formal.py', 'inspect_toolchain'),
    ('do_math/formal.py', 'verify_lean'),
    ('do_math/scheduled_operator.py', 'run_engine'),
    ('do_math/scheduled_operator.py', 'recovery'),
    ('setup_lean.py', 'verify_environment'),
}
INTERPRETER_USES = {
    ('do_math/file_io.py', 'console_python'): 'the rule itself',
    ('do_math/codex_adapter.py', 'start'): 'the worker Job root the owner starts with piped output',
    ('do_math/control_server.py', 'mcp_server_config'): 'the control server the CLI starts over stdio pipes',
    ('do_math/formal.py', '_job_run'): 'the Lean worker Job root',
    ('do_math/formal.py', '_project_identity'): 'the Lake search-path probe the owner runs',
    ('do_math/scheduled_operator.py', 'schedule'): 'the scheduled tasks run pythonw.exe on purpose',
    ('do_math/scheduled_operator.py', 'run_engine'): 'the scheduled engine child, piped',
    ('do_math/scheduled_operator.py', 'recovery'): 'the installation probe, piped',
}
# Every executable identity uses the same PATH/cwd/symlink rule (의무 9-A).
EXECUTABLE_IDENTITY = {('do_math/file_io.py', 'executable_identity')}


def _product_files():
    files = sorted(SCRIPTS.joinpath('do_math').rglob('*.py'))
    return files + sorted(path for path in SCRIPTS.glob('*.py') if path.name not in RUNNERS)


def _process_start_sites():
    """``(relative, function, kind, node)`` for every direct and injected process start."""
    for relative, function, node in _sites():
        if not isinstance(node, ast.Call):
            continue
        if _is(node.func, 'subprocess', {'run', 'Popen', 'call', 'check_call', 'check_output'}):
            yield relative, function, 'subprocess', node
        elif isinstance(node.func, ast.Name) and node.func.id in {'spawn', 'runner'}:
            yield relative, function, node.func.id, node
        elif _is(node.func, 'self', {'runner', '_run_process'}):
            yield relative, function, node.func.attr, node


def _sites():
    """Yield ``(relative path, enclosing function, node)`` for every node of the product."""
    for path in _product_files():
        tree = ast.parse(path.read_text(encoding='utf-8'))
        relative = path.relative_to(SCRIPTS).as_posix()

        def walk(node, function):
            for child in ast.iter_child_nodes(node):
                inner = child.name if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) else function
                yield relative, inner, child
                yield from walk(child, inner)
        yield from walk(tree, '<module>')


def _is(node, owner, names):
    return (isinstance(node, ast.Attribute) and node.attr in names
            and isinstance(node.value, ast.Name) and node.value.id == owner)


def _executable_identities():
    """Sites of ``Path(shutil.which(x) or x)``: an executable resolved to compare or record its identity."""
    for relative, function, node in _sites():
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'Path' and node.args
                and isinstance(node.args[0], ast.BoolOp) and isinstance(node.args[0].values[0], ast.Call)
                and _is(node.args[0].values[0].func, 'shutil', {'which'})):
            yield relative, function, node.lineno


class BoundaryInvariantTests(unittest.TestCase):
    def test_process_starts_are_declared_and_open_no_console_window(self):
        starts, injected = set(), set()
        for relative, function, kind, node in _process_start_sites():
            if kind == 'subprocess':
                starts.add((relative, function))
            else:
                injected.add((relative, function, kind))
            with self.subTest(site=(relative, function, node.lineno)):
                flags = [keyword.value for keyword in node.keywords if keyword.arg == 'creationflags']
                self.assertEqual(len(flags), 1, 'process start requires its console suppression flag')
                self.assertEqual(ast.unparse(flags[0]), "getattr(subprocess, 'CREATE_NO_WINDOW', 0)",
                                 'creationflags must use the Windows suppression value, not merely exist')
        self.assertEqual(starts, set(PROCESS_STARTS), 'direct process starts differ from the declared ones')
        self.assertEqual(injected, set(INJECTED_STARTS), 'injected process starts differ from the declared ones')
        job_starts = set()
        for relative, function, node in _sites():
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == '_job_run':
                job_starts.add((relative, function))
                with self.subTest(job_start=(relative, function, node.lineno)):
                    self.assertTrue({'jobs', 'clock', 'environment'} <= {kw.arg for kw in node.keywords})
        self.assertEqual(job_starts, JOB_RUN_STARTS, 'shared Job callers differ from the declared ones')


    def test_native_job_creation_passes_suspended_and_no_window_bits(self):
        calls = [(relative, function, node) for relative, function, node in _sites()
                 if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                 and node.func.attr in {'CreateProcessW', 'CreateProcessA'}]
        self.assertEqual([(relative, function) for relative, function, _ in calls],
                         [('do_math/windows_job.py', '_create_suspended_root')])
        self.assertEqual(ast.unparse(calls[0][2].args[5]), 'flags', 'native creation must receive the checked mask')
        tree = ast.parse((SCRIPTS / 'do_math/windows_job.py').read_text(encoding='utf-8'))
        constants = {node.target.id: ast.literal_eval(node.value) for node in ast.walk(tree)
                     if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
                     and node.target.id in {'_CREATE_NO_WINDOW', '_CREATE_SUSPENDED'}}
        self.assertEqual(constants, {'_CREATE_NO_WINDOW': 0x08000000, '_CREATE_SUSPENDED': 0x00000004})
        owner = next(node for node in ast.walk(tree)
                     if isinstance(node, ast.FunctionDef) and node.name == '_create_suspended_root')
        masks = [node.value for node in ast.walk(owner) if isinstance(node, ast.Assign)
                 and any(isinstance(target, ast.Name) and target.id == 'flags' for target in node.targets)]
        self.assertEqual(len(masks), 1, 'native creation has one reviewed flags assignment')

        def terms(node):
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
                return terms(node.left) | terms(node.right)
            return {ast.unparse(node)}

        self.assertTrue({'_CREATE_NO_WINDOW', '_CREATE_SUSPENDED'} <= terms(masks[0]),
                        'both bits must be ORed into the mask without being cleared')

    def test_interpreter_uses_are_declared(self):
        uses = {(relative, function) for relative, function, node in _sites() if _is(node, 'sys', {'executable'})}
        self.assertEqual(uses, set(INTERPRETER_USES), 'uses of sys.executable differ from the declared ones')

    def test_no_script_module_shadows_a_standard_library_module(self):
        # A worker runs from do_math/ and a tool from scripts/, so their files import by bare name;
        # modules of subpackages (do_math/ports/) are always imported by their package name.
        top = list(SCRIPTS.joinpath('do_math').glob('*.py')) + [path for path in SCRIPTS.glob('*.py') if path.name not in RUNNERS]
        names = {path.stem for path in top if path.stem != '__init__'}
        self.assertEqual(sorted(names & set(sys.stdlib_module_names)), [])

    def test_only_file_io_replaces_files(self):
        sites = {(relative, function) for relative, function, node in _sites()
                 if isinstance(node, ast.Call) and (_is(node.func, 'os', {'replace'}) or _is(node.func, 'shutil', {'move'}))}
        self.assertEqual({relative for relative, _ in sites}, {'do_math/file_io.py'})

    def test_executable_identity_has_one_normalization(self):
        sites = sorted(_executable_identities())
        self.assertEqual(sorted({(relative, function) for relative, function, _ in sites}), sorted(EXECUTABLE_IDENTITY),
                         'executable identities resolved outside the one normalization: ' + repr(sites))


if __name__ == '__main__':
    unittest.main()
