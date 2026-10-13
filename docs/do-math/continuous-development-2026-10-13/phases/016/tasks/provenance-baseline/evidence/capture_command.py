"""Preserve actual command output and process receipt for task-owned checks."""
import json
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

out=Path(__file__).resolve().parent
name=sys.argv[1]
argv=sys.argv[2:]
started=datetime.now(timezone.utc).isoformat()
child=subprocess.Popen(argv,cwd='C:/math',stdout=subprocess.PIPE,stderr=subprocess.PIPE)
stdout,stderr=child.communicate()
(out/(name+'.stdout')).write_bytes(stdout)
(out/(name+'.stderr')).write_bytes(stderr)
(out/(name+'.command.json')).write_text(json.dumps(dict(argv=argv,cwd='C:/math',pid=child.pid,
    started=started,ended=datetime.now(timezone.utc).isoformat(),exit_code=child.returncode,
    stdout=name+'.stdout',stderr=name+'.stderr'),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(stdout.decode('utf-8',errors='replace'))
if stderr:
    print(stderr.decode('utf-8',errors='replace'),file=sys.stderr)
sys.exit(child.returncode)
