import ast
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
REPO = Path('C:/math')
SCRIPTS = REPO / '.claude/skills/do-math/scripts'
tree = ast.parse((SCRIPTS / 'tests/boundary/test_scheduling_background_processes.py').read_text(encoding='utf-8'))
original = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == 'DESCENDANTS_PROBE' for t in n.targets))
instrument = '''
kernel.GetStdHandle.argtypes=[ctypes.c_ulong]; kernel.GetStdHandle.restype=ctypes.c_void_p
kernel.GetHandleInformation.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_ulong)]
handles=[]
def handle_state(label):
    rows=[]
    for key in (-10,-11,-12):
        h=kernel.GetStdHandle(key & 0xffffffff); flags=ctypes.c_ulong()
        valid=bool(kernel.GetHandleInformation(h,ctypes.byref(flags)))
        rows.append({'std':key,'handle':h,'valid':valid,'error':ctypes.get_last_error() if not valid else 0})
    handles.append({'label':label,'handles':rows})
    (root/'handles.json').write_text(json.dumps(handles))
handle_state('before_observation')
'''
block = '''        for child in family:
            if kernel.AttachConsole(child.pid):
                handle=kernel.GetConsoleWindow(); consoles.append(int(handle or 0)); kernel.FreeConsole()
            else:
                error=ctypes.get_last_error()
                assert error in (6,87), (child.pid,error)
                consoles.append(0)
'''
assert block in original
for mode in ('control', 'original'):
    root = HERE / ('os-' + (sys.argv[1] + '-' if len(sys.argv) > 1 else '') + mode)
    root.mkdir()
    source = original.replace('results=[]', instrument + '\nresults=[]')
    if mode == 'control':
        source = source.replace(block, '        consoles=[0 for child in family]\n')
    source = source.replace("        results.append", "        handle_state('after_observation_' + str(positive))\n        results.append")
    (root / 'probe.py').write_text(source, encoding='utf-8')
    argv = [str(Path(sys.executable).with_name('pythonw.exe')), '-B', str(root / 'probe.py'), str(SCRIPTS), str(root)]
    with (root / 'stdout').open('wb') as out, (root / 'stderr').open('wb') as err:
        child = subprocess.Popen(argv, stdout=out, stderr=err, creationflags=subprocess.CREATE_NO_WINDOW)
        code = child.wait()
    (root / 'receipt.json').write_text(json.dumps({'argv':argv,'pid':child.pid,'exit_code':code}), encoding='utf-8')
    print(json.dumps({'mode': mode, 'exit_code': code,
                     'handles': json.loads((root / 'handles.json').read_bytes()),
                     'stderr': (root / 'stderr').read_text(encoding='utf-8', errors='replace')}), flush=True)
