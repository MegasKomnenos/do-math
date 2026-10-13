import importlib.util
import json
import os
from pathlib import Path
import sys
from task_tools import REPO, RUN, HERE, write

spec = importlib.util.spec_from_file_location('official_mirror', REPO / '.claude/skills/writing-skills/scripts/build_skill_mirrors.py')
mirror = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mirror)
base = mirror.iter_files(REPO / '.claude/skills')
diff = REPO / '.agents/diff'
rules = mirror.load_rules(diff)
overlays = {r:p for r,p in mirror.iter_files(diff).items() if r not in mirror.RESERVED}
outputs = {r:mirror.transform(r, p.read_bytes(), rules) for r,p in base.items()}
outputs.update({r:p.read_bytes() for r,p in overlays.items()})
existing = mirror.iter_files(REPO / '.agents/skills')
changes = ['.agents/skills/' + r for r in sorted(set(outputs) | set(existing))
           if r not in existing or r not in outputs or existing[r].read_bytes() != outputs[r]]
phase = json.loads((RUN / 'phases/016/phase.json').read_bytes())
allowed = next(t['writes'] for t in phase['tasks'] if t['id'] == 't4-fixture-repair')
outside = [p for p in changes if p not in allowed]
manifest = json.loads((diff / '_manifest.json').read_bytes())
new_manifest = {'overlays': {r:mirror.sha1(base[r].read_bytes()) for r in sorted(overlays) if r in base}}
manifest_bytes = (json.dumps(new_manifest,ensure_ascii=False,indent=2,sort_keys=True) + '\n').replace('\n',os.linesep).encode('utf-8')
result = {'changes':changes,'outside_writes':outside,
          'manifest_unchanged':(diff / '_manifest.json').read_bytes() == manifest_bytes,
          'manifest_values_unchanged':manifest == new_manifest,'output_count':len(outputs)}
label = sys.argv[1] if len(sys.argv)>1 else 'mirror-plan'
write(label + '.json', result)
print(json.dumps(result,ensure_ascii=False))
assert not outside, outside
assert result['manifest_unchanged']
