import importlib.util
import json
import os
import sys
from task_tools import ROOT, HERE, dump

path = ROOT / '.claude/skills/writing-skills/scripts/build_skill_mirrors.py'
spec = importlib.util.spec_from_file_location('mirror_builder', path)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
base = builder.iter_files(ROOT / builder.BASE_REL)
rules = builder.load_rules(ROOT / '.agents/diff')
outputs = {rel: builder.transform(rel, p.read_bytes(), rules) for rel,p in base.items()}
overlays = {rel:p for rel,p in builder.iter_files(ROOT / '.agents/diff').items() if rel not in builder.RESERVED}
outputs.update({rel:p.read_bytes() for rel,p in overlays.items()})
existing = builder.iter_files(ROOT / '.agents/skills')
changes = ['.agents/skills/' + rel for rel in sorted(set(existing)|set(outputs))
           if rel not in existing or rel not in outputs or existing[rel].read_bytes() != outputs[rel]]
phase = json.loads((HERE.parents[2] / 'phase.json').read_text(encoding='utf-8-sig'))
allowed = phase['tasks'][0]['writes']
outside = [p for p in changes if p not in allowed]
manifest = {'overlays': {rel:builder.sha1(base[rel].read_bytes()) for rel in sorted(overlays) if rel in base}}
manifest_matches = (ROOT/'.agents/diff/_manifest.json').read_bytes() == (
    json.dumps(manifest,ensure_ascii=False,indent=2,sort_keys=True)+'\n').replace('\n', os.linesep).encode('utf-8')
record = {'changes':changes,'outside_writes':outside,'manifest_bytes_unchanged':manifest_matches,'outputs':len(outputs)}
dump(HERE / (sys.argv[1]+'.json'),record)
print(json.dumps(record,ensure_ascii=False))
assert not outside and manifest_matches
