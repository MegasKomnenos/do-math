from work import *
import importlib.util
path=REPO/'.claude/skills/writing-skills/scripts/build_skill_mirrors.py'
spec=importlib.util.spec_from_file_location('mirror',path); mirror=importlib.util.module_from_spec(spec); spec.loader.exec_module(mirror)
phase=json.loads((RUN/'phases/024/phase.json').read_text(encoding='utf-8-sig'))
allowed=phase['tasks'][0]['writes']
rules=mirror.load_rules(REPO/'.agents/diff')
base=mirror.iter_files(REPO/mirror.BASE_REL)
outputs={rel:mirror.transform(rel,p.read_bytes(),rules) for rel,p in base.items()}
outputs.update({rel:p.read_bytes() for rel,p in mirror.iter_files(REPO/'.agents/diff').items() if rel not in mirror.RESERVED})
existing=mirror.iter_files(REPO/'.agents/skills')
changed=sorted('.agents/skills/'+rel for rel in set(outputs)|set(existing)
               if rel not in outputs or rel not in existing or existing[rel].read_bytes()!=outputs[rel])
assert all(p in allowed for p in changed),changed
manifest=json.loads((REPO/'.agents/diff/_manifest.json').read_text(encoding='utf-8-sig'))
assert all(mirror.sha1(base[rel].read_bytes())==sha for rel,sha in manifest['overlays'].items())
save('mirror-plan.json',{'expected_changes':changed,'all_within_writes':True,'overlays_current':True,'output_count':len(outputs)})
print('Authorized mirror changes',len(changed),'outputs',len(outputs))
