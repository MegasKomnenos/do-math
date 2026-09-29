"""Background commands must not allocate consoles when launched by pythonw."""
from pathlib import Path
import ast
import json
import os
import subprocess
import sys
import tempfile
import unittest
import importlib.util

SCRIPTS = Path(__file__).resolve().parents[1]


class BackgroundProcessTests(unittest.TestCase):
    @unittest.skipUnless(os.name == 'nt' and importlib.util.find_spec('psutil'),
                         'Windows process-tree observation requires psutil')
    def test_real_git_descendants_are_observed_without_visible_windows(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            script = root / 'actual_git_probe.py'
            script.write_text(r'''import ctypes,json,subprocess,sys,time,psutil
from pathlib import Path
sys.path.insert(0,sys.argv[1])
from do_math.git_store import GitStateStore
root=Path(sys.argv[2]); repo=root/'repo'; repo.mkdir()
subprocess.run(['git','init','-q',str(repo)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
store=GitStateStore(repo,'RI-00000000000000000000000000')
real_run=subprocess.run; captured={}
def capture(command,**kwargs):
    captured.update(command=command,kwargs=kwargs)
    return real_run(command,**kwargs)
subprocess.run=capture
store._backend._run(store.repository,'cat-file','--batch',input=b'')
subprocess.run=real_run
command=captured['command']; options=captured['kwargs']; options.pop('input'); options.pop('check')
kernel=ctypes.WinDLL('kernel32',use_last_error=True); user=ctypes.WinDLL('user32',use_last_error=True)
kernel.GetConsoleWindow.restype=ctypes.c_void_p
user.IsWindowVisible.argtypes=[ctypes.c_void_p]
user.GetWindowThreadProcessId.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_ulong)]
callback_type=ctypes.WINFUNCTYPE(ctypes.c_bool,ctypes.c_void_p,ctypes.c_void_p)
results=[]
for positive in (True,False):
    launch=dict(options)
    if positive:
        launch['creationflags']=subprocess.CREATE_NEW_CONSOLE
        startup=subprocess.STARTUPINFO(); startup.dwFlags=subprocess.STARTF_USESHOWWINDOW; startup.wShowWindow=0
        launch['startupinfo']=startup
    p=subprocess.Popen(command,stdin=subprocess.PIPE,**launch)
    try:
        p.stdin.write(b'0000000000000000000000000000000000000000\n'); p.stdin.flush()
        assert b'missing' in p.stdout.readline(), 'actual Git must answer the batch request'
        family=[psutil.Process(p.pid),*psutil.Process(p.pid).children(recursive=True)]
        pids={x.pid for x in family}; consoles=[]; visible=[]
        def visit(hwnd,unused):
            owner=ctypes.c_ulong(); user.GetWindowThreadProcessId(hwnd,ctypes.byref(owner))
            if owner.value in pids and user.IsWindowVisible(hwnd): visible.append(owner.value)
            return True
        user.EnumWindows(callback_type(visit),None)
        for child in family:
            if kernel.AttachConsole(child.pid):
                handle=kernel.GetConsoleWindow(); consoles.append(int(handle or 0)); kernel.FreeConsole()
            else:
                error=ctypes.get_last_error()
                assert error in (6,87), (child.pid,error)
                consoles.append(0)
        results.append({'positive':positive,'names':[x.name() for x in family],
                        'consoles':consoles,'visible':visible})
    finally:
        p.communicate(timeout=10)
raw=bytes(range(256))+b'\r\n'
snap=store.publish(None,{'research/instance.json':b'{}','runtime/state.json':b'{}',
    'runtime/artifacts/actual/binary':raw})
assert store.read_bytes(snap.head,'runtime/artifacts/actual/binary')==raw
(root/'actual.json').write_text(json.dumps(results))
''', encoding='utf-8')
            process = subprocess.run([str(Path(sys.executable).with_name('pythonw.exe')), str(script), str(SCRIPTS), str(root)],
                           capture_output=True, text=True, timeout=60, creationflags=subprocess.CREATE_NO_WINDOW)
            self.assertEqual(process.returncode, 0, process.stderr)
            positive, observed = json.loads((root / 'actual.json').read_text())
            self.assertTrue(any(positive['consoles']), positive)
            self.assertTrue(any('git' in name.lower() for name in observed['names']), observed)
            self.assertTrue(observed['consoles'])
            self.assertFalse(any(observed['consoles']), observed)
            self.assertEqual(observed['visible'], [])

    def test_all_managed_subprocess_calls_explicitly_prevent_console_creation(self):
        calls = []
        for path in (SCRIPTS / 'do_math').glob('*.py'):
            for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
                if not isinstance(node, ast.Call):
                    continue
                function = node.func
                direct = (isinstance(function, ast.Attribute)
                          and isinstance(function.value, ast.Name)
                          and function.value.id == 'subprocess'
                          and function.attr in {'run', 'Popen'})
                # The scheduler port's real adapter calls the injected ``self.runner``.
                injected = (path.name == 'powershell_scheduler.py'
                            and ((isinstance(function, ast.Name) and function.id == 'runner')
                                 or (isinstance(function, ast.Attribute) and function.attr == 'runner'
                                     and isinstance(function.value, ast.Name) and function.value.id == 'self')))
                # The workers start their external program through the injected ``spawn`` (Popen's shape).
                spawned = (path.name in {'cli_worker.py', 'formal.py'}
                           and isinstance(function, ast.Name) and function.id == 'spawn')
                if direct or injected or spawned:
                    calls.append((path.name, node.lineno))
                    self.assertIn('creationflags', {k.arg for k in node.keywords}, calls[-1])
        # The scan must reach every launching module. Both providers share one
        # capability probe (codex_adapter) and one worker launch (cli_worker.run_cli,
        # through ``spawn``), so the product has ten call sites: cli 2, codex_adapter 1,
        # cli_worker 1, formal 2 (one through ``spawn``), git_process 1, scheduled_operator 2,
        # powershell_scheduler 1.
        self.assertGreaterEqual(len(calls), 10)

    @unittest.skipUnless(os.name == 'nt', 'Windows console semantics')
    def test_pythonw_git_calls_have_no_console_and_preserve_binary_state(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            script = root / 'probe.py'
            script.write_text('''import ctypes,json,subprocess,sys
from pathlib import Path
sys.path.insert(0,sys.argv[1])
from do_math.git_store import GitStateStore
root=Path(sys.argv[2]); repository=root/'repo'; repository.mkdir()
real_run=subprocess.run
real_run(['git','init','-q',str(repository)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
consoles=[]
def observed(command,**kwargs):
    if not consoles:
        result=real_run([str(Path(sys.executable).with_name('python.exe')),'-c',
            'import ctypes; print(ctypes.windll.kernel32.GetConsoleWindow())'],
            capture_output=True,text=True,creationflags=kwargs.get('creationflags',0),check=True)
        consoles.append(int(result.stdout))
    return real_run(command,**kwargs)
subprocess.run=observed
store=GitStateStore(repository,'RI-00000000000000000000000000')
raw=bytes(range(256))
first=store.publish(None,{'research/instance.json':b'{}','runtime/state.json':b'{}',
    'runtime/artifacts/one/binary':raw})
second=store.publish(first.head,{'runtime/state.json':b'{"next":true}'})
result={'parent_console':int(ctypes.windll.kernel32.GetConsoleWindow()),
    'child_consoles':consoles,'binary_unchanged':store.read_bytes(second.head,'runtime/artifacts/one/binary')==raw,
    'parent_preserved':store._backend._run(store.repository,'rev-parse',second.head+'^').stdout.decode().strip()==first.head}
(root/'result.json').write_text(json.dumps(result))
''', encoding='utf-8')
            subprocess.run([str(Path(sys.executable).with_name('pythonw.exe')), str(script),
                            str(SCRIPTS), str(root)], check=True, timeout=60,
                           creationflags=subprocess.CREATE_NO_WINDOW)
            result = json.loads((root / 'result.json').read_text())
            self.assertEqual(result['parent_console'], 0)
            self.assertEqual(result['child_consoles'], [0])
            self.assertTrue(result['binary_unchanged'])
            self.assertTrue(result['parent_preserved'])


if __name__ == '__main__':
    unittest.main()
