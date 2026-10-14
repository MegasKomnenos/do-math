import importlib.util
import json
import sys
from work import REPO, HERE, save

path = REPO / '.claude/skills/writing-skills/scripts/build_skill_mirrors.py'
spec = importlib.util.spec_from_file_location('mirror_generator', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
diff = REPO / '.agents/diff'
base = module.iter_files(REPO / module.BASE_REL)
rules = module.load_rules(diff)
outputs = {rel: module.transform(rel, path.read_bytes(), rules) for rel, path in base.items()}
overlays = {rel: path for rel, path in module.iter_files(diff).items() if rel not in module.RESERVED}
outputs.update({rel: path.read_bytes() for rel, path in overlays.items()})
existing = module.iter_files(REPO / '.agents/skills')
changes = ['.agents/skills/' + rel for rel in sorted(outputs.keys() | existing.keys())
           if rel not in existing or rel not in outputs or existing[rel].read_bytes() != outputs[rel]]
writes = json.loads((REPO / 'docs/do-math/continuous-development-2026-10-13/phases/027/phase.json').read_text(encoding='utf-8-sig'))['tasks'][0]['writes']
manifest = json.loads((diff / '_manifest.json').read_text(encoding='utf-8-sig'))
stale = [rel for rel in overlays if rel in base and manifest['overlays'].get(rel) != module.sha1(base[rel].read_bytes())]
result = {'files': len(outputs), 'changes': changes, 'outside_writes': [p for p in changes if p not in writes], 'stale': stale}
save(sys.argv[1] if len(sys.argv) > 1 else 'mirror-plan.json', result)
print(json.dumps(result, ensure_ascii=False))
assert not result['outside_writes'] and not stale
