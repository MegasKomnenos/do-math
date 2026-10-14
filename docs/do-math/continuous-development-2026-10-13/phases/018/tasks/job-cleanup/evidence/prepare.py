import importlib.util
import json
from pathlib import Path

E = Path(__file__).resolve().parent
# Reuse the previous task's evidence orchestration, not its observed results.
OLD = E.parents[3] / '017/tasks/t4-baseline-integration/evidence'
driver = (OLD / 'task_driver.py').read_text(encoding='utf-8')
driver = driver.replace('dm017-', 'dm018-').replace("phases/016/manager-evidence/source-inspected.json", "phases/017/manager-evidence/source-inspected.json")
driver = driver.replace('different_from_016', 'different_from_017')
driver = driver.replace("elif mode == 'finish':", "elif mode == 'observe':\n        sys.exit(execute('observe-'+sys.argv[2], [PY,'-u','-B',E/'observe_job.py',sys.argv[2]], external_temp=True))\n    elif mode == 'related':\n        tree = sys.argv[2]\n        scripts = REPO / ('.claude' if tree == 'canonical' else '.agents') / 'skills/do-math/scripts'\n        label = tree + '-related'\n        output = E / ('cr' if tree == 'canonical' else 'mr')\n        sys.exit(execute(label, [PY,'-u','-B',scripts/'run_tests.py','boundary.test_port_jobs','contracts.test_port_jobs','--jobs','1','--output',output], output=output, external_temp=True))\n    elif mode == 'exact-job':\n        output = E/'cj'\n        scripts = REPO/'.claude/skills/do-math/scripts'\n        sys.exit(execute('canonical-exact-job',[PY,'-u','-B',scripts/'run_tests.py','boundary.test_port_jobs.WindowsJobsContract.test_a_job_resumes_only_once','--jobs','1','--output',output],output=output,external_temp=True))\n    elif mode == 'finish':")
(E / 'task_driver.py').write_text(driver, encoding='utf-8')
verifier = (OLD / 'verify_task.py').read_text(encoding='utf-8')
verifier = verifier.replace("phases/017/phase.json", "phases/018/phase.json")
(E / 'verify_task.py').write_text(verifier, encoding='utf-8')
spec = importlib.util.spec_from_file_location('driver', E/'task_driver.py')
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)
audit = []
for ref in d.read(d.RUN/'phases/018/phase.json')['tasks'][0]['inputs']:
    root, rel = ref.split(':',1)
    p = (d.RUN if root == 'run' else d.REPO)/rel
    raw = p.read_bytes()
    value = json.loads(raw.decode('utf-8-sig')) if p.suffix == '.json' else raw.decode('utf-8-sig')
    row = {'reference':ref, 'sha256':d.sha(p), 'bytes':len(raw), 'type':type(value).__name__}
    if isinstance(value, dict): row['keys'] = list(value)
    audit.append(row)
d.write(E/'input-audit.json', audit)
print('Read assigned inputs:', len(audit))
