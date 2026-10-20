"""Small executable proofs for asynchronous dispatch and isolated integration."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ENGINE = Path(__file__).resolve().parents[1]

FAKE = r'''
import json,sys,time
from pathlib import Path
prompt=sys.stdin.read()
s=json.loads(prompt.splitlines()[0].removeprefix('SESSION_JSON='))
assert '최소' in prompt
records=Path(s['records']); repo=Path(s['source_repo'])
qpath=records/'queue.json'; q=json.loads(qpath.read_text())
def publish(path,value):
    pending=path.with_suffix('.tmp');pending.write_text(json.dumps(value),encoding='utf-8');pending.replace(path)
def task(i,deps=(),kind='work'):
    d=records/'tasks'/i;d.mkdir(parents=True,exist_ok=True)
    (d/'objective.md').write_text('Produce '+i,encoding='utf-8')
    return dict(id=i,kind=kind,depends_on=list(deps),writes=[] if kind=='review' else ['src/'+i+'.txt'],inputs=[])
if s['role']=='manager':
    inbox=json.loads(Path(s['inbox']).read_text())
    for event in inbox['completed']:
        i=event['id']
        assert event['returncode']==0
        subprocess=__import__('subprocess')
        subprocess.run([sys.executable,str(Path(s['engine'])/'workspaces.py'),'integrate',str(repo),str(records),i],check=True)
        if i not in q['accepted']:q['accepted'].append(i)
    if not q['tasks']:
        settings=json.loads((records/'settings.json').read_text());settings['max_workers']=2
        publish(records/'settings.json',settings)
        q['tasks']=[task('a'),task('b')]
    if 'b' in q['accepted'] and not any(t['id']=='c' for t in q['tasks']):q['tasks'].append(task('c',['b']))
    if {'a','b','c'}<=set(q['accepted']) and not any(t['id']=='review' for t in q['tasks']):q['tasks'].append(task('review',['a','b','c'],'review'))
    if 'review' in q['accepted']:q['status']='complete';q['reason']='All outputs and review accepted.'
    publish(qpath,q)
else:
    i=s['task'];w=Path(s['workspace']);d=records/'tasks'/i
    if i=='a':
        deadline=time.monotonic()+10
        while not (records/'c-started').exists():
            if time.monotonic()>deadline:raise RuntimeError('C was held behind slow A')
            time.sleep(.02)
        assert (w/'src/b.txt').read_text()=='old-b', 'A read B live edit'
    if i=='c':
        assert (w/'src/b.txt').read_text()=='new-b', 'C did not receive accepted B'
        (records/'c-started').write_text('yes')
    if i=='review':
        assert all((w/('src/'+x+'.txt')).read_text()=='new-'+x for x in ['a','b','c'])
    else:(w/('src/'+i+'.txt')).write_text('new-'+i)
    publish(d/'report.json',dict(status='complete',summary=i,changes=[] if i=='review' else ['src/'+i+'.txt'],verification='Checked assigned output.',findings=[]))
'''


class AsyncFlowTests(unittest.TestCase):
    def test_fast_dependency_starts_before_slow_peer_finishes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);repo=root/'repo';records=root/'records'
            (repo/'src').mkdir(parents=True);records.mkdir()
            for i in 'abc':(repo/'src'/f'{i}.txt').write_text('old-'+i)
            for n in ('context','plan','seams'):(records/f'{n}.md').write_text(n)
            fake=root/'fake.py';fake.write_text(FAKE,encoding='utf-8')
            (records/'settings.json').write_text(json.dumps(dict(max_workers=1,snapshot_paths=['src'],command=[sys.executable,str(fake)])))
            (records/'queue.json').write_text(json.dumps(dict(status='active',tasks=[],accepted=[])))
            result=subprocess.run([sys.executable,str(ENGINE/'run.py'),str(repo),str(records)],capture_output=True,text=True,timeout=30)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            queue=json.loads((records/'queue.json').read_text())
            self.assertEqual(queue['status'],'complete')
            self.assertEqual(set(queue['accepted']),{'a','b','c','review'})
            for i in queue['accepted']:
                home=records/'tasks'/i
                self.assertFalse((home/'base').exists())
                self.assertFalse((home/'workspace').exists())
                self.assertTrue((home/'archive.json').exists())
                self.assertEqual(json.loads((home/'cleanup.json').read_text())['status'],'complete')
            for i in 'abc':self.assertEqual((repo/'src'/f'{i}.txt').read_text(),'new-'+i)
            check=subprocess.run([sys.executable,str(ENGINE/'check.py'),'queue',str(records)],capture_output=True,text=True)
            self.assertEqual(check.returncode,0,check.stdout+check.stderr)

    def test_conflicting_user_edit_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);repo=root/'repo';records=root/'records'
            (repo/'src').mkdir(parents=True);records.mkdir()
            (repo/'src/a.txt').write_text('original')
            for n in ('context','plan','seams'):(records/f'{n}.md').write_text(n)
            spec=importlib.util.spec_from_file_location('workspace_test',ENGINE/'workspaces.py')
            module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
            task=dict(id='a',kind='work',depends_on=[],writes=['src/a.txt'],inputs=[])
            workspace=module.prepare(repo,records,task,dict(snapshot_paths=['src']))
            (workspace/'src/a.txt').write_text('worker')
            (repo/'src/a.txt').write_text('user')
            with self.assertRaisesRegex(ValueError,'conflict'):
                module.integrate(repo,records,'a')
            self.assertEqual((repo/'src/a.txt').read_text(),'user')


if __name__=='__main__':unittest.main()
