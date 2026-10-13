"""Compute the official generator outputs without writing product files."""
import importlib.util
import json
import os
import sys
from run_command import ROOT, EVIDENCE, write_json

path = ROOT / '.claude/skills/writing-skills/scripts/build_skill_mirrors.py'
spec = importlib.util.spec_from_file_location('official_mirror_builder', path)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
rules = builder.load_rules(ROOT / '.agents/diff')
base = builder.iter_files(ROOT / builder.BASE_REL)
overlays = {rel: p for rel, p in builder.iter_files(ROOT / '.agents/diff').items()
            if rel not in builder.RESERVED}
outputs = {rel: builder.transform(rel, p.read_bytes(), rules) for rel, p in base.items()}
outputs.update({rel: p.read_bytes() for rel, p in overlays.items()})
existing = builder.iter_files(ROOT / '.agents/skills')
created = sorted(set(outputs) - set(existing))
deleted = sorted(set(existing) - set(outputs))
updated = sorted(rel for rel in outputs.keys() & existing.keys()
                 if existing[rel].read_bytes() != outputs[rel])
manifest = json.loads((ROOT / '.agents/diff/_manifest.json').read_text(encoding='utf-8-sig'))
expected_manifest = {'overlays': {rel: builder.sha1(base[rel].read_bytes())
                                for rel in sorted(overlays) if rel in base}}
assert expected_manifest == manifest, 'Overlay drift: do not build'
manifest_text = json.dumps(expected_manifest, ensure_ascii=False, indent=2, sort_keys=True) + '\n'
# build_target uses Path.write_text with newline=None, which writes CRLF on Windows.
manifest_bytes = manifest_text.replace('\n', os.linesep).encode('utf-8')
assert (ROOT / '.agents/diff/_manifest.json').read_bytes() == manifest_bytes
changes = ['.agents/skills/' + rel for rel in updated]
allowed = {'.agents/skills/do-math/references/CLI-실행-계약.md',
           '.agents/skills/do-math/scripts/tests/.timings.json'}
result = {'outputs': len(outputs), 'created': created, 'deleted': deleted,
          'changed': changes, 'manifest_unchanged': True}
write_json(EVIDENCE / (sys.argv[1] + '.json'), result)
assert not created and not deleted and set(changes) <= allowed, result
print(json.dumps(result, ensure_ascii=False))
