import importlib.util
import json
from pathlib import Path
from run_command import REPO, EVIDENCE, write

script = REPO / '.claude/skills/writing-skills/scripts/build_skill_mirrors.py'
spec = importlib.util.spec_from_file_location('skill_mirror_builder', script)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
rules = builder.load_rules(REPO / '.agents/diff')
base = builder.iter_files(REPO / '.claude/skills')
existing = builder.iter_files(REPO / '.agents/skills')
outputs = {name: builder.transform(name, path.read_bytes(), rules) for name, path in base.items()}
for name, path in builder.iter_files(REPO / '.agents/diff').items():
    if name not in builder.RESERVED:
        outputs[name] = path.read_bytes()
changed = ['.agents/skills/' + name for name in sorted(outputs.keys() | existing.keys())
           if name not in outputs or name not in existing or existing[name].read_bytes() != outputs[name]]
phase = json.loads((EVIDENCE.parents[2] / 'phase.json').read_text(encoding='utf-8'))
writes = phase['tasks'][0]['writes']
outside = [path for path in changed if not any(path == allowed or allowed.endswith('/') and path.startswith(allowed)
                                            for allowed in writes)]
raw_changes = [name for name, path in base.items() if name.startswith('do-math/scripts/tests/corpus/')
               and path.read_bytes() != outputs[name]]
report = {'changed': changed, 'outside_writes': outside, 'corpus_byte_transformations': raw_changes}
write(EVIDENCE / 'mirror-plan.json', report)
print(json.dumps(report, ensure_ascii=False))
assert not outside, outside
