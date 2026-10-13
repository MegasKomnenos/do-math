from pathlib import Path
import sys
sys.path.insert(0, 'C:/math/.claude/skills/do-math/scripts')
from do_math.windows_job import WindowsJob
here = Path(__file__).resolve().parent
with WindowsJob([sys.executable, '-B', str(here / 'os_handle_probe.py'), 'job'], cwd=here) as child:
    child.resume()
    child.wait()
    print('Job diagnostic exit:', child.poll())
