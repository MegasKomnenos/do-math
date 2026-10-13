import ctypes
import json
from pathlib import Path
import sys
from task_tools import HERE, REPO, write
sys.path.insert(0, str(REPO / '.claude/skills/do-math/scripts'))
from do_math.windows_job import WindowsJob

root = HERE / 'repaired-os-final'
root.mkdir()
source = HERE / 'fixture-audit/repaired-os/probe.py'
probe = root / 'probe.py'
probe.write_bytes(source.read_bytes())
argv = [str(Path(sys.executable).with_name('pythonw.exe')), '-B', str(probe),
        str(REPO / '.claude/skills/do-math/scripts'), str(root)]
kernel = ctypes.WinDLL('kernel32', use_last_error=True)
kernel.GetExitCodeProcess.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong)]
kernel.GetExitCodeProcess.restype = ctypes.c_int
with WindowsJob(argv, cwd=root) as child:
    pid = child.pid
    child.resume()
    assert child.wait()
    inspection = child.inspect()
    code = ctypes.c_ulong()
    if not kernel.GetExitCodeProcess(child.process_handle, ctypes.byref(code)):
        raise ctypes.WinError(ctypes.get_last_error())
    assert code.value == 0
    assert inspection.root_signaled and inspection.active_processes == 0 and not inspection.process_ids
positive, negative = json.loads((root / 'actual.json').read_bytes())
assert any(positive['consoles']) and not any(negative['consoles'])
assert negative['visible'] == [] and all(x['stdin_unchanged'] for x in (positive, negative))
write('repaired-os-observation.json', {'argv':argv,'pid':pid,'exit_code':code.value,
      'job_root_signaled':inspection.root_signaled, 'active_processes':inspection.active_processes,
      'process_ids':list(inspection.process_ids), 'positive':positive, 'negative':negative,
      'binary_readback':True,'scope':'actual pythonw in WindowsJob; real Git and descendants; separate observer'})
print(json.dumps({'exit_code':code.value,'positive':positive,'negative':negative}))
