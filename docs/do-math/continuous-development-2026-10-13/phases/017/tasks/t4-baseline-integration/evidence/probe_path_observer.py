"""Observe actual subprocess cwd before the unchanged installed-probe TestCase cleans it up."""
import hashlib
import importlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import traceback
import unittest

E=Path(__file__).resolve().parent
sys.path[:0]=['C:/math/.claude/skills/do-math/scripts','C:/math/.claude/skills/do-math/scripts/tests']
m=importlib.import_module('boundary.test_operator_installation_probe')
mode=sys.argv[1]
original_worker=E/'canonical-t4-full-final/boundary-isolated-021/scratch'
target_length=len(str(original_worker)) if mode=='long' else len(str(E/'c4/boundary-isolated-021/scratch'))
prefix=E/'probe-owned'
prefix.mkdir(exist_ok=True)
root=prefix/('p'*(target_length-len(str(prefix))-1))
root.mkdir(exist_ok=False)
os.environ['TEMP']=os.environ['TMP']=os.environ['TMPDIR']=str(root)
tempfile.tempdir=None
calls=[]
real_run=subprocess.run
def observe(*args,**kwargs):
    argv=args[0] if args else kwargs['args']
    cwd=Path(kwargs.get('cwd',Path.cwd()))
    row={'argv':list(map(str,argv)),'cwd':str(cwd),'cwd_characters':len(str(cwd)),'cwd_is_directory':cwd.is_dir()}
    if '-c' in argv and 'probe_cli.main' in str(argv):
        dest=E/('probe-'+mode+'-raw')/('snapshot-'+str(len(calls)))
        dest.parent.mkdir(exist_ok=True)
        shutil.copytree(cwd.parent,dest)
        row['preserved_snapshot']=str(dest)
        row['manifest_sha256']=hashlib.sha256((cwd.parent/'bootstrap-manifest.json').read_bytes()).hexdigest() if (cwd.parent/'bootstrap-manifest.json').exists() else None
    try:
        p=real_run(*args,**kwargs)
        row.update(exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr)
        return p
    except Exception as exc:
        row.update(exception=type(exc).__name__,winerror=getattr(exc,'winerror',None),traceback=traceback.format_exc())
        raise
    finally:
        calls.append(row)
subprocess.run=observe
case=m.OperatorInstallationProbeTests('test_empty_installed_document_reports_incomplete_with_nonzero_exit')
result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([case]))
subprocess.run=real_run
data={'mode':mode,'owned_temp':str(root),'temp_characters':len(str(root)),'matched_worker_temp_characters':target_length,
      'source_sha256':hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest(),'calls':calls,
      'successful':result.wasSuccessful(),'errors':[(t.id(),detail) for t,detail in result.errors],
      'failures':[(t.id(),detail) for t,detail in result.failures],'tests_run':result.testsRun}
(E/('probe-'+mode+'-observation.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'mode':mode,'successful':result.wasSuccessful(),'temp_characters':len(str(root)),
                  'native_cwd':[(r['cwd_characters'],r.get('winerror'),r.get('exit_code')) for r in calls]},ensure_ascii=False))
sys.exit(0 if result.wasSuccessful() else 1)
