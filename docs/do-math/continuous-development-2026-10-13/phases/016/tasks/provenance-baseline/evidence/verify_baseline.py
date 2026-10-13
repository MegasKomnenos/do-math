"""Verify saved input bytes/API declarations only. Does not import/execute any project file."""
import ast
import hashlib
import importlib.metadata
import io
import json
from pathlib import Path
import platform
import sys
from investigate import REPO, RUN, OUT, PREFIX, sha, write, git
from extract_baseline_helpers import no_reparse


manifest=json.loads((OUT/'baseline-manifest.json').read_text(encoding='utf-8'))
root=Path(manifest['extracted_scripts'])
assert root.resolve().is_relative_to(OUT.resolve()) and root.resolve() != (REPO/PREFIX).resolve()
no_reparse(root)
rows=manifest['files']
assert {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()} == {r['path'] for r in rows}
tree=git('verify-tree','ls-tree','-r','-z',manifest['baseline_commit'],'--',PREFIX+'/')
expected={}
for raw in tree.split(b'\0'):
    if raw:
        meta,path=raw.split(b'\t',1)
        mode,kind,blob=meta.decode().split()
        assert kind=='blob' and mode in ('100644','100755')
        expected[path.decode('utf-8')]=(mode,blob)
assert expected=={r['repository_path']:(r['mode'],r['git_blob']) for r in rows}
# Independent readback against fresh Git objects, not against hashes alone.
object_ids=list(dict.fromkeys(r['git_blob'] for r in rows))
argv=['git','cat-file','--batch']
import subprocess
from datetime import datetime, timezone
request=('\n'.join(object_ids)+'\n').encode()
started=datetime.now(timezone.utc).isoformat()
p=subprocess.run(argv,cwd=REPO,input=request,capture_output=True)
(OUT/'verify-objects.stdin').write_bytes(request)
(OUT/'verify-objects.stderr').write_bytes(p.stderr)
write('verify-objects.command.json',dict(argv=argv,cwd=str(REPO),started=started,
    ended=datetime.now(timezone.utc).isoformat(),exit_code=p.returncode,
    stdin='verify-objects.stdin',stdout_bytes=len(p.stdout),stdout_sha256=sha(p.stdout),
    stdout_equal_extraction=p.stdout==(OUT/'extraction-objects.stdout.bin').read_bytes(),
    stdout_original='extraction-objects.stdout.bin',stderr='verify-objects.stderr'))
assert p.returncode==0 and p.stdout==(OUT/'extraction-objects.stdout.bin').read_bytes()
stream=io.BytesIO(p.stdout)
objects={}
for blob in object_ids:
    actual,kind,size=stream.readline().decode().strip().split()
    assert actual==blob and kind=='blob'
    data=stream.read(int(size))
    assert stream.read(1)==b'\n'
    objects[blob]=data
assert not stream.read()
for row in rows:
    path=root/row['path']
    no_reparse(path)
    data=path.read_bytes()
    assert data==objects[row['git_blob']]
    assert sha(data)==row['sha256'] and len(data)==row['bytes']
    assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['git_blob']


def parse(path):
    return ast.parse(path.read_bytes(),filename=str(path))


def declarations(tree):
    result={}
    def visit(nodes,prefix=''):
        for node in nodes:
            if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
                result[prefix+node.name]=dict(positional=[a.arg for a in node.args.posonlyargs+node.args.args],
                    keyword_only=[a.arg for a in node.args.kwonlyargs],line=node.lineno)
            elif isinstance(node,ast.ClassDef):
                visit(node.body,prefix+node.name+'.')
    visit(tree.body)
    return result


bg=declarations(parse(root/'tests/support/branch_gate.py'))
runner=declarations(parse(root/'run_tests.py'))
store=declarations(parse(root/'tests/support/t3_store.py'))
required_bg=['Measurement.__init__','Measurement.start','Measurement.begin','Measurement.save',
             'Measurement.entered','Measurement.merge','shared_state','used_state','unmeasured','write_index']
assert all(name in bg for name in required_bg)
assert all(name in runner for name in ('flatten','_run_suite','TimedResult.preserve','_ModuleSuites.run'))
assert runner['_run_suite']['positional']==['tests','directory']
assert 'measurement' in runner['_run_suite']['keyword_only']
assert bg['Measurement.__init__']['positional']==['self','root','data_file']
assert bg['Measurement.begin']['positional']==['self','order']
assert bg['Measurement.save']['positional']==['self','directory']
assert bg['Measurement.merge']['positional']==['self','directories']
assert 'Measurement.input_dependencies' not in bg
assert 'credited_functions' not in bg and 'shared_labels' not in bg
assert bg['Measurement.absorb']['positional']==['self','entered','opens']
assert not bg['build_index']['keyword_only']
assert not store['records']['keyword_only']
consumer=REPO/PREFIX/'tests/boundary/test_shared_input_provenance.py'
consumer_data=consumer.read_bytes()
consumer_tree=ast.parse(consumer_data)
constants={n.targets[0].id:ast.literal_eval(n.value) for n in consumer_tree.body
           if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name)
           and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str)}
snippets={name:ast.parse(constants[name],filename='<'+name+'>') for name in ('PROBE','SNAPSHOT')}
snapshot_node=next(n for n in consumer_tree.body if isinstance(n,ast.Assign)
                   and isinstance(n.targets[0],ast.Name) and n.targets[0].id=='WORKER')
worker=constants['SNAPSHOT']+ast.literal_eval(snapshot_node.value.right)
ast.parse(worker,filename='<WORKER>')
# New-only API calls are inside the explicitly measured mode, not baseline mode.
assert "if mode == 'measured':" in worker
new_block=worker.split("if mode == 'measured':",1)[1]
assert 'measurement.input_dependencies()' in new_block and 'measurement.shared_inputs' in new_block
assert 'input_dependencies' not in worker.split("if mode == 'measured':",1)[0]
identifiers=[n.name for n in ast.walk(consumer_tree) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_exact_baseline_')]
assert len(identifiers)==2
declaration_evidence=dict(baseline_branch_gate={n:bg[n] for n in required_bg+['Measurement.absorb','build_index']},
                         baseline_runner={n:runner[n] for n in ('flatten','_run_suite','TimedResult.preserve','_ModuleSuites.run')},
                         baseline_store={n:store[n] for n in ('module_records','records','stored_entries')},
                         missing_new_api=['Measurement.input_dependencies','Measurement.shared_inputs','credited_functions','shared_labels'],
                         exact_ids=['boundary.test_shared_input_provenance.SharedInputProvenanceTests.'+n for n in identifiers],
                         static_only=True,common_worker_api_available=True,baseline_mode_avoids_new_api=True)
write('api-static-verification.json',declaration_evidence)
stable=json.loads((OUT/'stable-source-comparison.json').read_text(encoding='utf-8'))
for row in stable:
    assert sha((REPO/row['path']).read_bytes())==row['current_sha256']
introduced=git('introduced-consumer','show',manifest['introduction_commit']+':'+PREFIX+'/tests/boundary/test_shared_input_provenance.py')
assert introduced.decode('utf-8').splitlines()==consumer_data.decode('utf-8').splitlines()
git('history-parents','rev-list','--parents','-n','1',manifest['introduction_commit'])
git('history-is-ancestor','merge-base','--is-ancestor',manifest['baseline_commit'],manifest['introduction_commit'])
git('object-format','rev-parse','--show-object-format')
git('baseline-selection-record','show',manifest['introduction_commit']+':기억/layer1/M-0472.md')
write('tool-edition.json',dict(python=sys.version,executable=sys.executable,
    executable_sha256=sha(Path(sys.executable).read_bytes()),platform=platform.platform(),
    coverage_distribution=importlib.metadata.version('coverage'),git=(OUT/'git-version.stdout').read_text().strip(),
    product_imports_performed=False,official_tests_performed=False))
write('baseline-verification.json',dict(verified=True,files=len(rows),bytes=sum(r['bytes'] for r in rows),
    unique_blobs=len(objects),tree_population_equal=True,fresh_git_bytes_equal=True,
    manifest_sha256=sha((OUT/'baseline-manifest.json').read_bytes()),required_files=manifest['required_files'],
    baseline=str(root.resolve()),current_root_different=True,paths_contained=True,reparse_points=0,
    stable_sources_unchanged=True,consumer_matches_introduction_ignoring_newlines=True,
    api_inspection_only=True,product_imports_performed=False,official_tests_performed=False,
    ordinary_or_measured_comparison_performed=False))
print(json.dumps(json.loads((OUT/'baseline-verification.json').read_text()),ensure_ascii=False))
