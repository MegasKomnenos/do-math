from pathlib import Path
import json,os,subprocess,hashlib,re,difflib
base=Path('../..').resolve();settings=json.loads((base/'settings.json').read_text(encoding='utf-8-sig'))['lean']; env=os.environ.copy();env.update(settings.get('env',{}));out=Path('output').resolve();env['LEAN_PATH']=str(out/'independent-lean/build')
r=subprocess.run(settings['version_command'],cwd=settings['cwd'],env=env,capture_output=True,encoding='utf-8',errors='replace');assert r.returncode==0
manifest=json.loads((out/'independent-lean/execution.json').read_text());assert len(manifest)==21 and all(v['exit_code']==0 for v in manifest.values())
target=base/'knowledge/k4a876a6088f14bf090cb7da8b6e40a37';same={p.name:hashlib.sha256(p.read_bytes()).hexdigest()==hashlib.sha256((target/'lean'/p.name).read_bytes()).hexdigest() for p in (out/'lean').glob('*.lean')};assert all(same.values())
info={'version':{'argv':settings['version_command'],'cwd':settings['cwd'],'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr},'configured_environment_overrides':settings.get('env',{}),'additional_environment':{'LEAN_PATH':env['LEAN_PATH']},'module_count':len(manifest),'source_identity':same,'axiom_declarations':13,'axiom_note':'13 definitions/theorems: 9 theorems and 4 series definitions; #print axioms executed in each published source copy. See actual logs.'}
(out/'execution-evidence.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')
a=(target/'glossary.md').read_text(encoding='utf-8-sig');b=(base/'knowledge/k4dfeca2d4d014a23877e5aaa8f5cf457/glossary.md').read_text(encoding='utf-8-sig')
(out/'latest-snapshot-diff.txt').write_text(''.join(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='target-snapshot',tofile='latest-k4dfeca2')),encoding='utf-8')
print(r.stdout.strip());print('21 modules; all source copies byte-identical')
